"""Small filesystem primitives for guarded bibliography publication."""

import fcntl
import hashlib
import os
import stat
import tempfile
import time
from contextlib import contextmanager
from contextvars import ContextVar
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


_held_locks: ContextVar[frozenset] = ContextVar("held_file_locks", default=frozenset())


@contextmanager
def file_lock(catalog: Path):
    key = catalog.resolve()
    if key in _held_locks.get():
        yield
        return
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
        token = _held_locks.set(_held_locks.get() | {key})
        try:
            yield
        finally:
            _held_locks.reset(token)
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


def hash_file(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def file_identity(path: Path):
    value = path.stat()
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


@contextmanager
def verified_copy(catalog: Path, source: Path, target: Path):
    """Publish verified bytes and remove only this invocation's staging name."""
    import shutil

    staging = catalog/'staging'
    if staging.is_symlink():
        raise RefError('unsafe_path','Remove the unsafe staging symlink before copying')
    staging.mkdir(mode=0o700,exist_ok=True)
    if staging.stat().st_dev != target.parent.stat().st_dev:
        raise RefError('staging_volume_mismatch','Keep catalog staging and the library on the same volume')
    before = file_identity(source)
    with tempfile.NamedTemporaryFile(prefix='copy-',dir=staging,delete=False) as stream:
        temporary = Path(stream.name)
        identity = os.fstat(stream.fileno())
        try:
            with source.open('rb') as incoming:
                if (os.fstat(incoming.fileno()).st_dev,os.fstat(incoming.fileno()).st_ino) != before[:2]:
                    raise RefError('source_changed','Source changed before reading; retry after the download completes')
                shutil.copyfileobj(incoming,stream)
            stream.flush()
            source_digest = hash_file(source)
            copy_digest = hash_file(temporary)
            if before != file_identity(source) or source_digest != copy_digest:
                raise RefError('source_changed','Source changed during copying; retry after the download completes')
            publish(temporary,target,None)
            yield copy_digest
        finally:
            try:
                current = temporary.lstat()
            except FileNotFoundError:
                pass
            else:
                if (current.st_dev,current.st_ino) == (identity.st_dev,identity.st_ino):
                    temporary.unlink()
