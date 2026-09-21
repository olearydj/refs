"""Small filesystem primitives for guarded bibliography publication."""

import fcntl
import hashlib
import os
import stat
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

from refs.results import RefError


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def destination(path: Path) -> Path:
    if path.is_symlink():
        raise RefError("unsafe_target", "Export destination cannot be a symbolic link", path=str(path))
    return path.resolve()


def current_digest(path: Path) -> str | None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(mode):
        raise RefError("unsafe_target", "Export destination must be a regular file", path=str(path))
    return digest(path.read_bytes())


@contextmanager
def file_lock(catalog: Path):
    # Init creates this file. Never replace its inode or create it during preview.
    with (catalog / "files.lock").open("r+b") as stream:
        deadline = time.monotonic() + 5
        while True:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise RefError("lock_timeout", "Catalog file effects are busy; retry", 6, retryable=True) from None
                time.sleep(0.05)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


@contextmanager
def staged(path: Path, data: bytes):
    with tempfile.NamedTemporaryFile(prefix=".refs-", suffix=".tmp", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        identity = os.fstat(stream.fileno())
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        if current_digest(temporary) != digest(data):
            raise RefError("integrity_error", "Staged output digest differs", 5, path=str(temporary))
        yield temporary
    finally:
        # A replacement at our temporary name is not ours to remove.
        if temporary.exists() and temporary.lstat().st_ino == identity.st_ino:
            temporary.unlink()


def publish(temporary: Path, target: Path, expected: str | None) -> None:
    if current_digest(target) != expected:
        raise RefError("outside_edit", "Destination changed before publication", path=str(target))
    if expected is None:
        try:
            os.link(temporary, target)
        except FileExistsError:
            raise RefError("outside_edit", "Destination appeared before publication", path=str(target)) from None
    else:
        os.replace(temporary, target)
