"""Exp 1: same-volume move: link+unlink / renamex_np(RENAME_EXCL) vs copy-based staging.

Compares inode, birthtime, mtime, xattrs (quarantine, Finder tags, where-froms, resource fork),
ACL, BSD flags across four strategies. Everything stays under the scratch directory.
"""
import ctypes, errno, os, shutil, subprocess, sys, time
from pathlib import Path

BASE = Path(__file__).parent / "exp1"
shutil.rmtree(BASE, ignore_errors=True)
(BASE / "downloads").mkdir(parents=True)
(BASE / "library").mkdir()


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True)


def make_source(name):
    p = BASE / "downloads" / name
    p.write_bytes(os.urandom(256 * 1024))
    # Backdate mtime and birthtime (SetFile -d sets creation date).
    sh("SetFile", "-d", "01/02/2020 03:04:05", str(p))
    sh("xattr", "-w", "com.apple.quarantine", "0083;66aa0000;Safari;ABCD-1234", str(p))
    sh("xattr", "-w", "com.apple.metadata:kMDItemWhereFroms", "https://example.org/paper.pdf", str(p))
    # Finder tag (binary plist normally; a text value is enough to test preservation)
    sh("xattr", "-w", "com.apple.metadata:_kMDItemUserTags", "Red\n6", str(p))
    sh("xattr", "-w", "user.refs.test", "hello", str(p))
    # Resource fork
    with open(str(p) + "/..namedfork/rsrc", "wb") as f:
        f.write(b"RSRCFORKDATA" * 10)
    # ACL
    sh("chmod", "+a", "everyone deny delete_child", str(p))  # harmless on a file
    sh("chmod", "+a", "staff allow read", str(p))
    os.utime(p, (1600000000, 1600000000))  # last: mtime 2020-09-13, birth 2020-01-02
    return p


def describe(p):
    st = os.stat(p)
    xs = sh("xattr", str(p)).stdout.split()
    acl = [l.strip() for l in sh("ls", "-le", str(p)).stdout.splitlines()[1:]]
    return {
        "ino": st.st_ino,
        "birth": int(st.st_birthtime),
        "mtime": int(st.st_mtime),
        "nlink": st.st_nlink,
        "xattrs": sorted(xs),
        "acl": acl,
        "flags": st.st_flags,
    }


def show(label, before, after):
    print(f"--- {label}")
    for k in before:
        b, a = before[k], after[k]
        mark = "SAME" if a == b else "DIFF"
        print(f"  {k:7} {mark}  before={b}  after={a}")


# Strategy A: os.link + os.unlink
src = make_source("a.pdf")
dst = BASE / "library" / "a.pdf"
before = describe(src)
t0 = time.perf_counter()
os.link(src, dst)
mid = describe(dst)
os.unlink(src)
t1 = time.perf_counter()
show(f"A os.link+os.unlink ({(t1 - t0) * 1e3:.2f} ms)", before, describe(dst))
print("  nlink while both names exist:", mid["nlink"])
# collision behaviour
src2 = make_source("a.pdf")
try:
    os.link(src2, dst)
    print("  collision: NOT detected (bad)")
except FileExistsError as e:
    print("  collision: FileExistsError errno", e.errno, "- source and destination untouched")

# Strategy B: renamex_np RENAME_EXCL via ctypes
libc = ctypes.CDLL(None, use_errno=True)
RENAME_EXCL = 0x4
src = make_source("b.pdf")
dst = BASE / "library" / "b.pdf"
before = describe(src)
r = libc.renamex_np(os.fsencode(src), os.fsencode(dst), ctypes.c_uint(RENAME_EXCL))
print("renamex_np rc", r, "errno", ctypes.get_errno())
show("B renamex_np(RENAME_EXCL)", before, describe(dst))
src2 = make_source("b.pdf")
r = libc.renamex_np(os.fsencode(src2), os.fsencode(dst), ctypes.c_uint(RENAME_EXCL))
print("  collision rc", r, "errno", errno.errorcode.get(ctypes.get_errno()), "source still exists:", src2.exists())

# Strategy C: design protocol with plain byte copy to sibling staging, then hardlink_to, unlink stage, unlink source
src = make_source("c.pdf")
dst = BASE / "library" / "c.pdf"
stage = BASE / "library" / ".c.pdf.refs-staging"
before = describe(src)
t0 = time.perf_counter()
fd = os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with open(src, "rb") as f, os.fdopen(fd, "wb") as g:
    shutil.copyfileobj(f, g)
    g.flush()
    os.fsync(g.fileno())
dst.hardlink_to(stage)
stage.unlink()
src.unlink()
t1 = time.perf_counter()
show(f"C staging byte copy + hardlink_to ({(t1 - t0) * 1e3:.2f} ms)", before, describe(dst))

# Strategy D: same, but shutil.copy2 (the best stdlib metadata copier)
src = make_source("d.pdf")
dst = BASE / "library" / "d.pdf"
stage = BASE / "library" / ".d.pdf.refs-staging"
before = describe(src)
shutil.copy2(src, stage)
dst.hardlink_to(stage)
stage.unlink()
src.unlink()
show("D staging shutil.copy2 + hardlink_to", before, describe(dst))

# Strategy E: /bin/cp -p (copyfile(3) COPYFILE_ALL semantics) for reference
src = make_source("e.pdf")
dst = BASE / "library" / "e.pdf"
before = describe(src)
sh("cp", "-p", str(src), str(dst))
show("E /bin/cp -p (copyfile(3))", before, describe(dst))

# GetFileInfo creation date for A and C
for n in ("a.pdf", "c.pdf", "d.pdf", "e.pdf"):
    print(n, "GetFileInfo -d:", sh("GetFileInfo", "-d", str(BASE / "library" / n)).stdout.strip())

print("stdlib xattr API on this platform:", {n: hasattr(os, n) for n in ("listxattr", "getxattr", "setxattr")})
print("shutil._copyxattr usable:", hasattr(os, "listxattr"))

# Timing on a 64 MiB file: link+unlink vs copy+fsync+sha256 verify both sides
import hashlib
big = BASE / "downloads" / "big.bin"
big.write_bytes(os.urandom(64 * 1024 * 1024))
t0 = time.perf_counter(); os.link(big, BASE / "library" / "big.bin"); os.unlink(big); t1 = time.perf_counter()
print(f"64MiB link+unlink: {(t1-t0)*1e3:.2f} ms")
big = BASE / "library" / "big.bin"
t0 = time.perf_counter()
h1 = hashlib.file_digest(open(big, "rb"), "sha256").hexdigest()
st = BASE / "library" / ".big2.staging"
with open(big, "rb") as f, open(st, "xb") as g:
    shutil.copyfileobj(f, g, 1024 * 1024); g.flush(); os.fsync(g.fileno())
h2 = hashlib.file_digest(open(st, "rb"), "sha256").hexdigest()
(BASE / "library" / "big2.bin").hardlink_to(st); st.unlink()
h3 = hashlib.file_digest(open(big, "rb"), "sha256").hexdigest()  # fresh source recheck
t1 = time.perf_counter()
print(f"64MiB copy+fsync+3xsha256 protocol: {(t1-t0)*1e3:.2f} ms  ok={h1==h2==h3}")
