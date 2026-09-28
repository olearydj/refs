"""A catalog-local diagnostic stream with durable mutation records."""

import json
import logging
import os
from collections.abc import Callable
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path

from refs.results import RefError

EVENTS = frozenset({
    "command.open", "command.close", "source.create", "source.original", "source.update", "source.key_set",
    "source.remove", "source.reactivate", "source.link", "source.unlink", "resource.link", "resource.unlink",
    "resource.copy", "resource.move", "import.entry", "import.batch_open",
    "import.batch_close", "import.reconcile", "export.write", "export.adopt", "export.forget",
    "project.create", "project.cite", "project.uncite", "backup.write",
    "schema.upgrade", "catalog.init", "diagnostic",
})

_command: ContextVar[str] = ContextVar("refs_log_command", default="library")
_catalog: ContextVar[str | None] = ContextVar("refs_log_catalog", default=None)
_logger = logging.getLogger("refs")
_logger.setLevel(logging.DEBUG)
_logger.propagate = False
_file: DurableFileHandler | None = None
_console: logging.Handler | None = None
_opening: Callable[[], None] | None = None


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.command = _command.get()
        record.catalog = _catalog.get()
        return True


class JSONLines(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        value = dict(timestamp=datetime.fromtimestamp(record.created, UTC).isoformat(),
                     level=record.levelname.lower(), event=record.__dict__["event"],
                     command=record.__dict__["command"], catalog=record.__dict__["catalog"], pid=record.process)
        value.update(record.__dict__["fields"])
        return json.dumps(value, ensure_ascii=False, default=str, separators=(",", ":"))


class DurableFileHandler(logging.Handler):
    def __init__(self, path: Path):
        super().__init__(logging.DEBUG)
        self.path = path
        created = not path.exists()
        self.stream = path.open("a", encoding="utf-8")
        if created:
            try:
                descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
            except OSError:
                self.stream.close()
                raise
        self.setFormatter(JSONLines())
        self.addFilter(ContextFilter())

    def emit(self, record: logging.LogRecord) -> None:
        try:
            if record.__dict__["mutation"] and (not os.access(self.path, os.W_OK) or self.path.stat().st_ino != os.fstat(self.stream.fileno()).st_ino):
                raise OSError("Catalog log was made unwritable or replaced")
            self.stream.write(self.format(record) + "\n")
            if record.__dict__["mutation"]:
                self.stream.flush()
                os.fsync(self.stream.fileno())
        except (OSError, ValueError) as exc:
            if record.__dict__["mutation"]:
                raise RefError("log_unwritable", "Cannot write the catalog log; change refused", 5,
                               path=str(self.path)) from exc
            # Diagnostic logging is best effort; only mutations require it.

    def close(self) -> None:
        try:
            self.stream.close()
        finally:
            super().close()


def bind(command: str, catalog: Path | None = None) -> None:
    _command.set(command)
    if catalog is not None:
        _catalog.set(str(catalog))


def command() -> str:
    return _command.get()


def defer_open(callback: Callable[[], None]) -> None:
    global _opening
    _opening = callback


def setup(catalog: Path, *, verbose: bool = False, mutation: bool = False) -> None:
    global _file, _console, _opening
    bind(_command.get(), catalog)
    path = catalog / "refs.log"
    if _file is None or _file.path != path:
        if _file is not None:
            _logger.removeHandler(_file)
            _file.close()
        _file = None
        try:
            if path.is_symlink():
                raise OSError("Catalog log cannot be a symbolic link")
            _file = DurableFileHandler(path)
            _logger.addHandler(_file)
        except OSError as exc:
            if mutation:
                raise RefError("log_unwritable", "Cannot open the catalog log; change refused", 5,
                               path=str(path)) from exc
            # A read-only command must not need write access to its log.
    if verbose and _console is None:
        from rich.console import Console
        from rich.logging import RichHandler
        _console = RichHandler(level=logging.DEBUG, console=Console(stderr=True), show_path=False)
        _console.addFilter(ContextFilter())
        _logger.addHandler(_console)
    elif not verbose and _console is not None:
        _logger.removeHandler(_console)
        _console.close()
        _console = None
    if _file is not None and _opening is not None:
        opening, _opening = _opening, None
        opening()


def event(name: str, *, mutation: bool = False, **fields) -> None:
    if name not in EVENTS:
        raise ValueError(f"Unregistered log event: {name}")
    catalog = _catalog.get()
    if mutation and (_file is None or catalog is not None and _file.path != Path(catalog) / "refs.log"):
        if catalog is None:
            raise RefError("log_unwritable", "No catalog log is selected; change refused", 5)
        setup(Path(catalog), mutation=True)
    _logger.info(name, extra={"event": name, "fields": fields, "mutation": mutation})


def log_mutation(name: str, target, before, after, **fields) -> None:
    if name in ("command.open", "command.close", "diagnostic"):
        raise ValueError(f"Not a mutation event: {name}")
    fields.setdefault("changes", changes(before or {}, after or {}))
    event(name, mutation=True, target=target, before=before, after=after, **fields)


def changes(before: dict, after: dict, prefix: str = "") -> dict:
    """Return changed canonical paths without recording preserved evidence bytes."""
    result = {}
    for key in before.keys() | after.keys():
        path = f"{prefix}.{key}" if prefix else key
        old, new = before.get(key), after.get(key)
        if isinstance(old, dict) and isinstance(new, dict):
            result.update(changes(old, new, path))
        elif old != new:
            result[path] = {"old": old, "new": new}
    return result
