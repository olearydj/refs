"""Exp 2: cost of fsync vs F_FULLFSYNC on this APFS volume, and SQLite commit cost with fullfsync off/on."""
import fcntl, os, shutil, sqlite3, statistics, time
from pathlib import Path

BASE = Path(__file__).parent / "exp2"
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir()


def bench(label, sync, n=100):
    p = BASE / f"{label}.bin"
    fd = os.open(p, os.O_WRONLY | os.O_CREAT, 0o600)
    ts = []
    for _ in range(n):
        os.write(fd, os.urandom(4096))
        t0 = time.perf_counter()
        sync(fd)
        ts.append((time.perf_counter() - t0) * 1e3)
    os.close(fd)
    print(f"{label:12} n={n} median={statistics.median(ts):.3f} ms p95={sorted(ts)[int(n * .95)]:.3f} ms total={sum(ts):.1f} ms")


bench("fsync", os.fsync)
bench("F_FULLFSYNC", lambda fd: fcntl.fcntl(fd, fcntl.F_FULLFSYNC))

# directory fsync / F_FULLFSYNC: does it work at all?
dfd = os.open(BASE, os.O_RDONLY)
try:
    os.fsync(dfd); print("dir fsync: ok")
except OSError as e:
    print("dir fsync:", e)
try:
    fcntl.fcntl(dfd, fcntl.F_FULLFSYNC); print("dir F_FULLFSYNC: ok")
except OSError as e:
    print("dir F_FULLFSYNC:", e)
os.close(dfd)

for journal in ("DELETE", "WAL"):
    for full in (0, 1):
        db = BASE / f"c_{journal}_{full}.sqlite"
        c = sqlite3.connect(db, isolation_level=None)
        c.execute(f"pragma journal_mode={journal}")
        c.execute("pragma synchronous=FULL")
        c.execute(f"pragma fullfsync={full}")
        c.execute(f"pragma checkpoint_fullfsync={full}")
        c.execute("create table t(id integer primary key, v text)")
        t0 = time.perf_counter()
        for i in range(200):
            c.execute("begin immediate"); c.execute("insert into t(v) values(?)", ("x" * 200,)); c.execute("commit")
        dt = time.perf_counter() - t0
        print(f"sqlite journal={journal:6} synchronous=FULL fullfsync={full}: 200 commits {dt * 1e3:.0f} ms ({dt / 200 * 1e3:.2f} ms/commit)")
        c.close()
