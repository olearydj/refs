"""Exp 4: (a) TOCTOU on source deletion; (b) crash-point walk of a minimal same-volume link protocol
whose recovery needs only one journal row plus lstat() of two names (inode identity is the proof of publication).
"""
import hashlib, os, shutil, sqlite3
from pathlib import Path

BASE = Path(__file__).parent / "exp4"
shutil.rmtree(BASE, ignore_errors=True)
(BASE / "dl").mkdir(parents=True); (BASE / "lib").mkdir()

# ---------- (a) TOCTOU: path-based unlink deletes whatever is at the path now
src = BASE / "dl" / "paper.pdf"; src.write_bytes(b"original bytes")
verified = os.stat(src)                       # "fresh source identity/content ... must match" check passes here
digest = hashlib.sha256(src.read_bytes()).hexdigest()
# a browser re-download / the user's "Replace" lands between verification and unlink:
tmp = BASE / "dl" / "paper.pdf.download"; tmp.write_bytes(b"NEWER, DIFFERENT, UNIQUE bytes"); os.replace(tmp, src)
now = os.lstat(src)
print("(a) inode at verification:", verified.st_ino, " inode at unlink time:", now.st_ino,
      " -> identity check detects replacement:", (verified.st_ino, verified.st_dev) != (now.st_ino, now.st_dev))
os.unlink(src)  # what the contract's `cleanup_pending` step does if it only re-hashes earlier or not at all
print("(a) blind path unlink destroyed the only copy of the newer file:", not src.exists())

# Race-free variant: move the name aside under a private name first, then verify WHAT WE HOLD, then unlink (or rename back).
src.write_bytes(b"original bytes"); ident = os.lstat(src)
tmp.write_bytes(b"NEWER bytes 2"); os.replace(tmp, src)          # attacker/browser wins the race again
aside = BASE / "dl" / ".paper.pdf.refs-cleanup"
os.link(src, aside); held = os.lstat(aside)                      # link, not rename: never hides the user's name
if (held.st_ino, held.st_dev) != (ident.st_ino, ident.st_dev):
    os.unlink(aside)                                             # not ours: drop only our private extra name
    print("(a) aside-link variant: identity mismatch detected, user's new file kept:", src.read_bytes())

# ---------- (b) crash-point walk: prepared -> link -> catalog commit -> unlink source -> complete
db = sqlite3.connect(BASE / "catalog.sqlite", isolation_level=None)
db.execute("create table resources(id integer primary key, path text)")
db.execute("create table file_ops(id integer primary key, res integer, src text, dst text, dev integer, ino integer, size integer, sha text, state text)")


class Crash(Exception):
    pass


def move(res, src, dst, crash_at=None):
    st = os.lstat(src)
    sha = hashlib.sha256(Path(src).read_bytes()).hexdigest()
    db.execute("begin immediate")
    cur = db.execute("insert into file_ops(res,src,dst,dev,ino,size,sha,state) values(?,?,?,?,?,?,?, 'prepared')",
                     (res, str(src), str(dst), st.st_dev, st.st_ino, st.st_size, sha))
    op = cur.lastrowid; db.execute("commit")
    if crash_at == 1: raise Crash(op)
    os.link(src, dst)                                   # atomic, EEXIST on collision, same inode
    if crash_at == 2: raise Crash(op)
    db.execute("begin immediate")
    db.execute("update resources set path=? where id=?", (str(dst), res))
    db.execute("update file_ops set state='committed' where id=?", (op,)); db.execute("commit")
    if crash_at == 3: raise Crash(op)
    finish(op)
    return op


def same(path, dev, ino):
    try:
        s = os.lstat(path)
    except FileNotFoundError:
        return None
    return (s.st_dev, s.st_ino) == (dev, ino)


def finish(op):
    _, res, src, dst, dev, ino, size, sha, state = db.execute("select * from file_ops where id=?", (op,)).fetchone()
    if same(src, dev, ino) and same(dst, dev, ino):
        os.unlink(src)       # removing one of two names of the SAME inode can never lose bytes
    db.execute("update file_ops set state='complete' where id=?", (op,))


def recover(op):
    _, res, src, dst, dev, ino, size, sha, state = db.execute("select * from file_ops where id=?", (op,)).fetchone()
    s, d = same(src, dev, ino), same(dst, dev, ino)
    if state == "prepared" and not d:
        # never published by us (dst absent, or a DIFFERENT inode = someone else's file, even if byte-identical)
        db.execute("update file_ops set state='abandoned' where id=?", (op,)); return "rolled back: nothing to undo, source untouched"
    if state == "prepared" and d:
        db.execute("begin immediate"); db.execute("update resources set path=? where id=?", (dst, res))
        db.execute("update file_ops set state='committed' where id=?", (op,)); db.execute("commit")
    finish(op); return "rolled forward"


for crash_at in (1, 2, 3):
    src = BASE / "dl" / f"f{crash_at}.pdf"; dst = BASE / "lib" / f"f{crash_at}.pdf"
    src.write_bytes(os.urandom(1000))
    db.execute("insert into resources(id, path) values(?,?)", (crash_at, str(src)))
    try:
        move(crash_at, src, dst, crash_at)
    except Crash as c:
        op = c.args[0]
        before = (src.exists(), dst.exists(), db.execute("select state from file_ops where id=?", (op,)).fetchone()[0])
        outcome = recover(op)
        path = db.execute("select path from resources where id=?", (crash_at,)).fetchone()[0]
        print(f"(b) crash after step {crash_at}: (src,dst,state)={before} -> {outcome}; src={src.exists()} dst={dst.exists()} "
              f"catalog->{Path(path).parent.name}/{Path(path).name} resolves={Path(path).exists()}")

# identical-content squatter at destination while op is 'prepared': inode differs -> not ours -> no deletion of anything
src = BASE / "dl" / "g.pdf"; dst = BASE / "lib" / "g.pdf"; src.write_bytes(b"same"); db.execute("insert into resources(id,path) values(9,?)", (str(src),))
try:
    move(9, src, dst, 1)
except Crash as c:
    dst.write_bytes(b"same")   # user dragged a copy there by hand after the crash
    print("(b) identical squatter:", recover(c.args[0]), "| src kept:", src.exists(), "dst kept:", dst.exists())
