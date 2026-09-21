"""Exp 3: rollback journal vs WAL with 4 writer processes (+ readers), busy_timeout=5000, synchronous=FULL.

S1: 4 writers x 200 BEGIN IMMEDIATE txns + 2 short-query readers.
S2: S1 plus one long reader holding a read snapshot for HOLD seconds (export/library-export/backup-like).
S3: citation-key suffix allocation race (-a, -b, ...) under BEGIN IMMEDIATE vs deferred BEGIN.
"""
import multiprocessing as mp, os, shutil, sqlite3, sys, time
from pathlib import Path

BASE = Path(__file__).parent / "exp3"
HOLD = 8.0
N_TX = 200


def connect(db):
    c = sqlite3.connect(db, isolation_level=None, timeout=5.0)
    c.execute("pragma busy_timeout=5000")
    c.execute("pragma synchronous=FULL")
    c.execute("pragma foreign_keys=ON")
    return c


def writer(db, wid, start, q):
    c = connect(db)
    start.wait()
    locked = 0; ok = 0; worst = 0.0
    for i in range(N_TX):
        t0 = time.perf_counter()
        try:
            c.execute("begin immediate")
            c.execute("insert into sources(citation_key, metadata_json) values(?,?)", (f"w{wid}-{i}", "{}" * 100))
            c.execute("update catalog_meta set revision=revision+1")
            c.execute("commit")
            ok += 1
        except sqlite3.OperationalError as e:
            locked += 1
            try: c.execute("rollback")
            except sqlite3.Error: pass
        worst = max(worst, time.perf_counter() - t0)
    q.put(("writer", wid, ok, locked, round(worst, 3)))


def reader(db, rid, start, stop, q):
    c = connect(db)
    start.wait()
    n = 0; locked = 0; worst = 0.0
    while not stop.is_set():
        t0 = time.perf_counter()
        try:
            c.execute("select count(*), max(id) from sources").fetchone()
            c.execute("select * from sources order by citation_key limit 50").fetchall()
            n += 1
        except sqlite3.OperationalError:
            locked += 1
        worst = max(worst, time.perf_counter() - t0)
        time.sleep(0.005)
    q.put(("reader", rid, n, locked, round(worst, 3)))


def long_reader(db, start, q):
    c = connect(db)
    start.wait()
    time.sleep(0.2)
    c.execute("begin")
    c.execute("select count(*) from sources").fetchone()  # snapshot / SHARED lock acquired
    time.sleep(HOLD)
    n = c.execute("select count(*) from sources").fetchone()[0]
    c.execute("commit")
    q.put(("long_reader", 0, n, 0, HOLD))


def scenario(journal, with_long):
    d = BASE / f"{journal}_{'long' if with_long else 'short'}"
    d.mkdir(parents=True)
    db = str(d / "catalog.sqlite")
    c = connect(db)
    c.execute(f"pragma journal_mode={journal}")
    c.execute("create table sources(id integer primary key, citation_key text unique not null, metadata_json text)")
    c.execute("create table catalog_meta(revision integer)"); c.execute("insert into catalog_meta values(0)")
    c.close()
    ctx = mp.get_context("spawn")
    q = ctx.Queue(); start = ctx.Event(); stop = ctx.Event()
    ws = [ctx.Process(target=writer, args=(db, i, start, q)) for i in range(4)]
    rs = [ctx.Process(target=reader, args=(db, i, start, stop, q)) for i in range(2)]
    ls = [ctx.Process(target=long_reader, args=(db, start, q))] if with_long else []
    for p in ws + rs + ls: p.start()
    time.sleep(0.5)
    t0 = time.perf_counter(); start.set()
    for p in ws: p.join()
    wall = time.perf_counter() - t0
    stop.set()
    for p in rs + ls: p.join()
    res = [q.get() for _ in ws + rs + ls]
    rows = sqlite3.connect(db).execute("select count(*) from sources").fetchone()[0]
    w = [r for r in res if r[0] == "writer"]; r_ = [r for r in res if r[0] == "reader"]
    print(f"[{journal:6} long_reader={with_long}] writers wall={wall:.2f}s ok={sum(x[2] for x in w)} "
          f"locked_failures={sum(x[3] for x in w)} worst_tx={max(x[4] for x in w)}s | "
          f"readers queries={sum(x[2] for x in r_)} locked={sum(x[3] for x in r_)} worst={max(x[4] for x in r_)}s | rows={rows}")


def key_worker(db, wid, mode, start, q):
    c = connect(db)
    start.wait()
    ok = 0; errs = {}
    for i in range(50):
        base = f"smith-2024-turingTrap"
        try:
            c.execute("begin immediate" if mode == "immediate" else "begin")
            taken = {r[0] for r in c.execute("select citation_key from sources where citation_key = ? or citation_key like ?", (base, base + "-%"))}
            key = base
            n = 0
            while key in taken:
                # a, b, ... z, aa, ab ...
                s = ""; k = n
                while True:
                    s = chr(ord("a") + k % 26) + s; k = k // 26 - 1
                    if k < 0: break
                key = f"{base}-{s}"; n += 1
            c.execute("insert into sources(citation_key, metadata_json) values(?, '{}')", (key,))
            c.execute("commit"); ok += 1
        except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
            errs[type(e).__name__ + ":" + str(e)] = errs.get(type(e).__name__ + ":" + str(e), 0) + 1
            try: c.execute("rollback")
            except sqlite3.Error: pass
    q.put((wid, ok, errs))


def key_race(journal, mode):
    d = BASE / f"keys_{journal}_{mode}"; d.mkdir(parents=True)
    db = str(d / "catalog.sqlite")
    c = connect(db); c.execute(f"pragma journal_mode={journal}")
    c.execute("create table sources(id integer primary key, citation_key text unique not null, metadata_json text)"); c.close()
    ctx = mp.get_context("spawn"); q = ctx.Queue(); start = ctx.Event()
    ps = [ctx.Process(target=key_worker, args=(db, i, mode, start, q)) for i in range(4)]
    for p in ps: p.start()
    time.sleep(0.5); t0 = time.perf_counter(); start.set()
    for p in ps: p.join()
    res = [q.get() for _ in ps]
    c = sqlite3.connect(db)
    total, distinct = c.execute("select count(*), count(distinct citation_key) from sources").fetchone()
    errs = {}
    for _, _, e in res:
        for k, v in e.items(): errs[k] = errs.get(k, 0) + v
    print(f"[keys {journal:6} {mode:9}] wall={time.perf_counter() - t0:.2f}s committed={sum(r[1] for r in res)}/200 rows={total} distinct={distinct} errors={errs}")


if __name__ == "__main__":
    shutil.rmtree(BASE, ignore_errors=True)
    print("python", sys.version.split()[0], "sqlite", sqlite3.sqlite_version)
    for journal in ("DELETE", "WAL"):
        scenario(journal, False)
    for journal in ("DELETE", "WAL"):
        scenario(journal, True)
    for journal in ("DELETE", "WAL"):
        for mode in ("immediate", "deferred"):
            key_race(journal, mode)
