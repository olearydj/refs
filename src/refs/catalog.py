"""SQLite lifecycle and short application transactions."""

import os
import sqlite3
import tomllib
from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
from uuid import uuid4

from refs.config import Settings, absolute, toml_text
from refs.results import RefError


@contextmanager
def connect(catalog: Path, *, write: bool = False):
    db = catalog / "catalog.sqlite"
    if not db.is_file():
        raise RefError("catalog_missing", "Selected catalog is missing", path=str(catalog))
    if not (catalog / "ready").is_file():
        raise RefError("recovery_required", "Catalog initialization is incomplete", 5, path=str(catalog))
    if write and (not os.access(catalog,os.W_OK) or not os.access(db,os.W_OK)):
        raise RefError('home_not_writable','Allow write access to the selected catalog and its staging directory, then retry',5,path=str(catalog))
    connection = sqlite3.connect(db.as_uri() + ("?mode=rw" if write else "?mode=ro"), uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        try:
            meta = connection.execute("SELECT * FROM catalog_meta WHERE singleton=1").fetchone()
        except sqlite3.OperationalError as exc:
            if not write and "readonly" in str(exc):
                raise RefError("recovery_required", "SQLite needs writable rollback recovery", 5) from exc
            raise
        if not meta or meta["schema_version"] != 2:
            raise RefError("unsupported_schema", "Catalog schema is not supported", 5)
        if write:
            connection.execute("PRAGMA synchronous=FULL")
            if connection.execute("PRAGMA journal_mode").fetchone()[0] != "delete":
                raise RefError("unsupported_schema", "Catalog must use rollback journaling", 5)
            connection.execute("BEGIN IMMEDIATE")
        else:
            connection.execute("BEGIN")
        yield connection
        if write:
            connection.commit()
    finally:
        connection.close()


def changed(connection: sqlite3.Connection) -> None:
    connection.execute("UPDATE catalog_meta SET revision=revision+1 WHERE singleton=1")


def init(settings: Settings, library: Path | None, dry_run: bool = False, *, reuse_config=False) -> dict:
    catalog = settings.catalog_path()
    config = settings.config
    if reuse_config:
        if not config.is_file():
            raise RefError('init_conflict','--reuse-config requires an existing configuration')
        configured = tomllib.loads(config.read_text()).get('catalog', {}).get('path')
        if not configured or absolute(configured, config.parent) != catalog or library != settings.library:
            raise RefError('init_conflict','Use the configured catalog and library with --reuse-config')
        if (catalog/'ready').exists():
            raise RefError('init_conflict','--reuse-config refuses an existing ready catalog')
    if config.exists() and settings.library != library:
        raise RefError("init_conflict", "Existing configuration has a different library", path=str(config))
    if (catalog / "ready").is_file():
        if not config.is_file():
            raise RefError("init_conflict", "Ready catalog has no selected configuration")
        with connect(catalog) as connection:
            meta = dict(connection.execute("SELECT * FROM catalog_meta").fetchone())
        return dict(catalog_id=meta["catalog_id"], unchanged=True)
    if catalog.exists() and (not catalog.is_dir() or any(catalog.iterdir())):
        raise RefError("init_conflict", "Catalog destination is not empty; inspect existing files", path=str(catalog))
    for path in [catalog, config.parent, library]:
        if path is None:
            continue
        if str(path).startswith("/Volumes/") and len(path.parts) > 2 and not Path(*path.parts[:3]).is_mount():
            raise RefError("init_conflict", "Selected volume is not mounted", path=str(path))
        if path.exists() and not path.is_dir():
            raise RefError("init_conflict", "Destination is not a directory", path=str(path))
    if config.exists() and not reuse_config:
        raise RefError("init_conflict", "Existing configuration without a ready catalog requires inspection", path=str(config))
    if dry_run:
        return dict(dry_run=True, paths=settings.describe(), library=str(library) if library else None)
    catalog.mkdir(mode=0o700, parents=True, exist_ok=True)
    catalog.chmod(0o700)
    config.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if library:
        library.mkdir(mode=0o700, parents=True, exist_ok=True)
    db = catalog / "catalog.sqlite"
    db.touch(mode=0o600, exist_ok=False)
    catalog_id = str(uuid4())
    with sqlite3.connect(db) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
        connection.executescript(files("refs").joinpath("migrations/001_initial.sql").read_text())
        connection.execute("INSERT INTO catalog_meta VALUES (1, ?, 1, 0)", (catalog_id,))
        connection.commit()
        upgrade_connection(connection)
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RefError("recovery_required", "New catalog failed integrity check", 5)
    values: dict = dict(schema_version=1, catalog=dict(path=str(catalog)))
    if library:
        values['resources'] = dict(library_root=str(library), roots=dict(library=str(library)))
    if not reuse_config:
        with config.open("x") as stream:
            config.chmod(0o600)
            stream.write(toml_text(values))
    (catalog / "files.lock").touch(mode=0o600, exist_ok=False)
    (catalog / "ready").touch(mode=0o600, exist_ok=False)
    return dict(catalog_id=catalog_id, unchanged=False, paths=settings.describe(), library=str(library) if library else None)


def upgrade_connection(connection: sqlite3.Connection) -> None:
    version = connection.execute('SELECT schema_version FROM catalog_meta').fetchone()
    if version is None or version[0] not in (1, 2):
        raise RefError('unsupported_schema', 'Expected catalog schema 1 or 2', 5)
    if version[0] == 1:
        try:
            connection.executescript('BEGIN IMMEDIATE;\n' + files('refs').joinpath('migrations/002_zotero_ingest.sql').read_text() + '\nCOMMIT;')
        except BaseException:
            connection.rollback()
            raise


def migrate(catalog: Path) -> None:
    """Explicit offline upgrade; caller must stop writers and retain a snapshot."""
    if not (catalog/'ready').is_file():
        raise RefError('recovery_required', 'Inspect the incomplete catalog before migrating', 5)
    with sqlite3.connect((catalog/'catalog.sqlite').resolve().as_uri()+'?mode=rw', uri=True) as connection:
        connection.execute('PRAGMA foreign_keys=ON')
        upgrade_connection(connection)
