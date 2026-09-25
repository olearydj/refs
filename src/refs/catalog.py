"""SQLite lifecycle and short application transactions.

SQLite connection contexts commit or roll back; closing/finally owns their lifetime.
"""

import os
import sqlite3
import tomllib
from contextlib import closing, contextmanager
from datetime import date
from importlib.resources import files
from pathlib import Path
from uuid import uuid4

from refs import logging as action_log
from refs.config import Settings, absolute, toml_text
from refs.results import RefError, upgrade_notices

MIGRATIONS = ('001_initial.sql', '002_zotero_ingest.sql', '003_source_loc.sql',
              '004_file_operations.sql', '005_lowercase_unfiled.sql')
SCHEMA_VERSION = len(MIGRATIONS)


@contextmanager
def connect(catalog: Path, *, write: bool = False):
    action_log.bind(action_log.command(), catalog)
    db = catalog / "catalog.sqlite"
    if not db.is_file():
        raise RefError("catalog_missing", "Selected catalog is missing", path=str(catalog))
    if not (catalog / "ready").is_file():
        raise RefError("recovery_required", "Catalog initialization is incomplete", 5, path=str(catalog))
    if write and (not os.access(catalog,os.W_OK) or not os.access(db,os.W_OK)):
        raise RefError('home_not_writable','Allow write access to the selected catalog and its staging directory, then retry',5,path=str(catalog))
    if write:
        action_log.setup(catalog, mutation=True)
    connection = sqlite3.connect(db.as_uri() + ("?mode=rw" if write else "?mode=ro"), uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=5000")
        try:
            ensure_schema(catalog, connection)
            meta = connection.execute("SELECT * FROM catalog_meta WHERE singleton=1").fetchone()
        except sqlite3.OperationalError as exc:
            if not write and "readonly" in str(exc):
                raise RefError("recovery_required", "SQLite needs writable rollback recovery", 5) from exc
            raise
        if not meta or meta["schema_version"] != SCHEMA_VERSION:
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
    action_log.setup(catalog, mutation=True)
    config.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if library:
        library.mkdir(mode=0o700, parents=True, exist_ok=True)
    db = catalog / "catalog.sqlite"
    db.touch(mode=0o600, exist_ok=False)
    action_log.log_mutation('catalog.init', str(catalog), None, {'schema_version': SCHEMA_VERSION, 'library': str(library) if library else None})
    catalog_id = str(uuid4())
    with closing(sqlite3.connect(db)) as connection, connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
        connection.executescript(files("refs").joinpath("migrations/" + MIGRATIONS[0]).read_text())
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
    if version is None or version[0] not in range(1, SCHEMA_VERSION + 1):
        raise RefError('unsupported_schema', f'Expected catalog schema 1 through {SCHEMA_VERSION}', 5)
    for filename in MIGRATIONS[version[0]:]:
        legacy = connection.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='catalog_meta'").fetchone()[0]
        normalize = ("ALTER TABLE catalog_meta RENAME TO catalog_meta_legacy;\n"
                     "CREATE TABLE catalog_meta (singleton INTEGER PRIMARY KEY CHECK (singleton=1), catalog_id TEXT NOT NULL UNIQUE, schema_version INTEGER NOT NULL CHECK (schema_version>=1), revision INTEGER NOT NULL DEFAULT 0 CHECK (revision>=0));\n"
                     "INSERT INTO catalog_meta SELECT * FROM catalog_meta_legacy;\nDROP TABLE catalog_meta_legacy;\n") if 'CHECK (schema_version =' in legacy else ''
        try:
            connection.executescript('BEGIN IMMEDIATE;\n' + normalize + files('refs').joinpath('migrations/' + filename).read_text() + '\nCOMMIT;')
        except BaseException:
            connection.rollback()
            raise


def migrate(catalog: Path) -> None:
    """Explicit offline upgrade; caller must stop writers and retain a snapshot."""
    if not (catalog/'ready').is_file():
        raise RefError('recovery_required', 'Inspect the incomplete catalog before migrating', 5)
    with closing(sqlite3.connect((catalog/'catalog.sqlite').resolve().as_uri()+'?mode=rw', uri=True)) as connection, connection:
        connection.execute('PRAGMA foreign_keys=ON')
        before = connection.execute('SELECT schema_version FROM catalog_meta').fetchone()[0]
        if before != SCHEMA_VERSION:
            action_log.setup(catalog, mutation=True)
            action_log.log_mutation('schema.upgrade', str(catalog), {'schema_version':before}, {'schema_version':SCHEMA_VERSION})
        upgrade_connection(connection)


def ensure_schema(catalog: Path, connection: sqlite3.Connection) -> None:
    """Upgrade an existing catalog only after saving a consistent safety copy."""
    from refs.files import file_lock
    db = catalog / 'catalog.sqlite'
    def version():
        return connection.execute('SELECT schema_version FROM catalog_meta').fetchone()[0]
    current = version()
    if current == SCHEMA_VERSION:
        return
    if current not in range(1, SCHEMA_VERSION):
        raise RefError('unsupported_schema', 'Catalog schema is newer or unsupported; use a compatible refs version', 5)
    with file_lock(catalog):
        current = version()
        if current == SCHEMA_VERSION:
            return
        if current not in range(1, SCHEMA_VERSION):
            raise RefError('unsupported_schema', 'Catalog schema is newer or unsupported; use a compatible refs version', 5)
        safety = catalog / f'before-schema-{SCHEMA_VERSION}-{date.today().isoformat()}.sqlite'
        with closing(sqlite3.connect(db.as_uri()+'?mode=rw', uri=True)) as c, c:
            c.execute('BEGIN IMMEDIATE')
            try:
                action_log.setup(catalog, mutation=True)
                action_log.log_mutation('schema.upgrade', str(catalog), {'schema_version': current}, {'schema_version': SCHEMA_VERSION}, safety_copy=str(safety))
                with safety.open('xb'):
                    safety.chmod(0o600)
                with closing(sqlite3.connect(db.as_uri()+'?mode=ro', uri=True)) as source, source, closing(sqlite3.connect(safety)) as target, target:
                    source.backup(target)
                with safety.open('rb') as stream:
                    os.fsync(stream.fileno())
            except (OSError, sqlite3.Error) as exc:
                raise RefError('unsupported_schema', f'Cannot write schema safety copy {safety}: {exc}; resolve this before retrying', 5) from exc
            finally:
                c.rollback()
            c.execute('PRAGMA foreign_keys=ON')
            upgrade_connection(c)
        upgrade_notices.set([*upgrade_notices.get(), dict(code='schema_upgraded', message=f'Upgraded catalog schema {current} to {SCHEMA_VERSION}; safety copy: {safety}', path=str(safety), details={}, retryable=False)])
