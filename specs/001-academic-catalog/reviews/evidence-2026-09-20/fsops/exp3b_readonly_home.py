"""Exp 3b: can a process WITHOUT write permission to the catalog home (e.g. a sandboxed agent) read the catalog?

Simulated with chmod a-w on the home directory and files. Compares journal_mode=DELETE and WAL,
plain open vs mode=ro URI vs immutable=1, and flock on a read-only lock file.
"""
import fcntl, os, shutil, sqlite3, stat
from pathlib import Path

BASE = Path(__file__).parent / "exp3b"
if BASE.exists():
    for p in [BASE, *BASE.rglob("*")]:
        os.chmod(p, 0o755 if p.is_dir() else 0o644)
    shutil.rmtree(BASE)

for journal in ("DELETE", "WAL"):
    home = BASE / journal
    home.mkdir(parents=True)
    db = home / "catalog.sqlite"
    c = sqlite3.connect(db, isolation_level=None)
    c.execute(f"pragma journal_mode={journal}")
    c.execute("create table sources(id integer primary key, k text)")
    c.execute("insert into sources(k) values('smith-2024')")
    c.close()  # clean close: WAL checkpointed, -wal/-shm removed
    (home / "lock").write_bytes(b"")
    print(journal, "files after clean close:", sorted(p.name for p in home.iterdir()))
    for p in home.iterdir():
        os.chmod(p, 0o444)
    os.chmod(home, 0o555)

    def attempt(label, fn):
        try:
            print(f"  {label:34} ->", fn())
        except Exception as e:
            print(f"  {label:34} -> {type(e).__name__}: {e}")

    attempt("plain connect + select", lambda: sqlite3.connect(db).execute("select k from sources").fetchall())
    attempt("uri mode=ro + select", lambda: sqlite3.connect(f"file:{db}?mode=ro", uri=True).execute("select k from sources").fetchall())
    attempt("uri immutable=1 + select", lambda: sqlite3.connect(f"file:{db}?immutable=1", uri=True).execute("select k from sources").fetchall())
    attempt("begin immediate (write)", lambda: sqlite3.connect(db, isolation_level=None).execute("begin immediate").fetchall())

    def lock():
        fd = os.open(home / "lock", os.O_RDONLY)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.close(fd)
        return "flock LOCK_EX ok on O_RDONLY fd"
    attempt("flock on read-only lock file", lock)
    os.chmod(home, 0o755)
