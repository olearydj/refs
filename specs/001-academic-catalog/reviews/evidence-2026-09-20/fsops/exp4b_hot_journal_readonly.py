"""Exp 4b: after a writer is killed mid-transaction (hot rollback journal), can a strictly read-only open
(the contract's dry-run/preview: "opens existing data read-only") still read? Same question for WAL."""
import multiprocessing as mp, os, shutil, sqlite3
from pathlib import Path

BASE = Path(__file__).parent / "exp4b"


def crasher(db):
    c = sqlite3.connect(db, isolation_level=None)
    c.execute("pragma cache_size=5"); c.execute("pragma synchronous=FULL")
    c.execute("begin immediate")
    c.execute("update t set v = v || 'y'")     # touches every page; tiny cache forces spill into the main db file
    os._exit(9)                                 # SIGKILL-equivalent: no rollback, journal left behind


if __name__ == "__main__":
    shutil.rmtree(BASE, ignore_errors=True)
    for journal in ("DELETE", "WAL"):
        d = BASE / journal; d.mkdir(parents=True); db = str(d / "catalog.sqlite")
        c = sqlite3.connect(db, isolation_level=None); c.execute(f"pragma journal_mode={journal}")
        c.execute("create table t(id integer primary key, v text)")
        c.execute("begin"); c.executemany("insert into t(v) values(?)", [("x" * 500,) for _ in range(5000)]); c.execute("commit"); c.close()
        p = mp.get_context("spawn").Process(target=crasher, args=(db,)); p.start(); p.join()
        print(journal, "after kill:", sorted(x.name for x in d.iterdir()))
        for label, uri in (("mode=ro", f"file:{db}?mode=ro"), ("read-write", f"file:{db}")):
            try:
                r = sqlite3.connect(uri, uri=True).execute("select count(*), sum(length(v)) from t").fetchone()
                print(f"  {label:10} -> ok {r}")
            except sqlite3.Error as e:
                print(f"  {label:10} -> {type(e).__name__}: {e}")
