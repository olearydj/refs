"""Exp 5: a plausible year of artifact retention (12 monthly Zotero snapshots of the observed 74,035,200-byte size
as BLOBs) and what backup (backup API / VACUUM INTO), integrity_check and a concurrent writer look like on it.
Also shows the failure mode at SQLITE_LIMIT_LENGTH. Deletes its large files at the end.
"""
import hashlib, multiprocessing as mp, os, shutil, sqlite3, sys, time
from pathlib import Path

BASE = Path(__file__).parent / "exp5"
SNAP = 74_035_200 + 655_360   # zotero.sqlite + better-bibtex.sqlite sizes observed via ls -l
MONTHS = 12


def connect(db):
    c = sqlite3.connect(db, isolation_level=None, timeout=5.0)
    c.execute("pragma busy_timeout=5000"); c.execute("pragma synchronous=FULL")
    return c


def prober(db, stop, q):
    c = connect(db); worst = 0.0; fails = 0; n = 0
    while not stop.is_set():
        t0 = time.perf_counter()
        try:
            c.execute("begin immediate"); c.execute("insert into ops(v) values('x')"); c.execute("commit"); n += 1
        except sqlite3.OperationalError:
            fails += 1
            try: c.execute("rollback")
            except sqlite3.Error: pass
        worst = max(worst, time.perf_counter() - t0); time.sleep(0.02)
    q.put((n, fails, round(worst, 3)))


def run(journal):
    d = BASE / journal; d.mkdir(parents=True)
    db = str(d / "catalog.sqlite")
    c = connect(db); c.execute(f"pragma journal_mode={journal}")
    c.execute("create table artifacts(sha256 text primary key, bytes blob, n integer)"); c.execute("create table ops(id integer primary key, v text)")
    t0 = time.perf_counter()
    for m in range(MONTHS):
        b = os.urandom(SNAP)
        c.execute("begin immediate"); c.execute("insert into artifacts values(?,?,?)", (hashlib.sha256(b).hexdigest(), b, len(b))); c.execute("commit")
    del b
    print(f"[{journal}] inserted {MONTHS} x {SNAP / 1e6:.1f} MB in {time.perf_counter() - t0:.1f}s; catalog size = {os.path.getsize(db) / 1e6:.0f} MB")
    ctx = mp.get_context("spawn"); q = ctx.Queue(); stop = ctx.Event()
    p = ctx.Process(target=prober, args=(db, stop, q)); p.start(); time.sleep(0.5)
    t0 = time.perf_counter(); dst = sqlite3.connect(str(d / "backup.sqlite")); c.backup(dst, pages=-1); dst.close()
    t_backup = time.perf_counter() - t0
    t0 = time.perf_counter(); c.execute("vacuum into ?", (str(d / "vacuum.sqlite"),)); t_vac = time.perf_counter() - t0
    t0 = time.perf_counter(); ok = c.execute("pragma integrity_check").fetchone()[0]; t_ic = time.perf_counter() - t0
    stop.set(); p.join(); n, fails, worst = q.get()
    print(f"[{journal}] backup API {t_backup:.2f}s | VACUUM INTO {t_vac:.2f}s | integrity_check={ok} {t_ic:.2f}s | "
          f"concurrent writer: {n} commits, {fails} 'database is locked', worst latency {worst}s")
    c.close()


if __name__ == "__main__":
    shutil.rmtree(BASE, ignore_errors=True)
    for j in ("DELETE", "WAL"):
        run(j)
    # failure mode at the BLOB length limit (limit lowered so the test stays small)
    c = sqlite3.connect(":memory:"); print("default SQLITE_LIMIT_LENGTH:", c.getlimit(sqlite3.SQLITE_LIMIT_LENGTH))
    c.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 1_000_000); c.execute("create table a(b blob)")
    try:
        c.execute("insert into a values(?)", (b"x" * 1_000_001,))
    except Exception as e:
        print("blob over limit ->", type(e).__name__, e)
    shutil.rmtree(BASE, ignore_errors=True)
