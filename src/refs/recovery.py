"""SQLite snapshots and validation for the documented manual restore procedure."""

import json
import os
import sqlite3
import tempfile
from importlib.resources import files as package_files
from pathlib import Path

from refs import files, resources
from refs.catalog import connect
from refs.config import Settings
from refs.results import RefError

MEMBERS = {'catalog.sqlite','config.toml','resources.jsonl'}


def validate_database(path: Path) -> dict:
    with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as connection:
        if connection.execute('PRAGMA integrity_check').fetchall()!=[('ok',)] or connection.execute('PRAGMA foreign_key_check').fetchall():
            raise RefError('snapshot_invalid','Database integrity failed; retain the snapshot and choose another backup',5)
        with sqlite3.connect(':memory:') as expected:
            expected.executescript(package_files('refs').joinpath('migrations/001_initial.sql').read_text())
            for name, in expected.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                columns=expected.execute(f'PRAGMA table_info("{name}")').fetchall()
                if connection.execute(f'PRAGMA table_info("{name}")').fetchall()!=columns:
                    raise RefError('unsupported_schema','Catalog tables do not match the supported schema; retain this snapshot for inspection',5)
        connection.row_factory=sqlite3.Row
        meta=connection.execute('SELECT * FROM catalog_meta WHERE singleton=1').fetchone()
        if meta is None or meta['schema_version']!=1:
            raise RefError('unsupported_schema','Use a supported catalog schema',5)
        return dict(meta)


def validate_snapshot(path: Path) -> dict:
    try:
        if path.is_symlink() or not path.is_dir():
            raise ValueError('Snapshot must be a real directory')
        manifest_path=path/'manifest.json'
        if manifest_path.is_symlink():
            raise ValueError('Manifest cannot be a symlink')
        manifest=json.loads(manifest_path.read_text())
        if manifest['schema_version']!=1 or manifest['external_contents_included'] is not False or set(manifest['members'])!=MEMBERS:
            raise ValueError('Unsupported manifest or member set')
        if set(item.name for item in path.iterdir()) != MEMBERS|{'manifest.json'}:
            raise ValueError('Unexpected snapshot members')
        for name, expected in manifest['members'].items():
            member=path/name
            if member.is_symlink() or not member.is_file() or member.stat().st_size!=expected['size'] or files.hash_file(member)!=expected['sha256']:
                raise ValueError(f'Member failed verification: {name}')
        meta=validate_database(path/'catalog.sqlite')
        if meta['catalog_id']!=manifest['catalog_id'] or meta['schema_version']!=manifest['catalog_schema_version']:
            raise ValueError('Catalog identity disagrees with manifest')
        with sqlite3.connect((path/'catalog.sqlite').as_uri()+'?mode=ro',uri=True) as connection:
            connection.row_factory=sqlite3.Row
            actual=resources.inventory(connection)
        inventory=[json.loads(line) for line in (path/'resources.jsonl').read_text().splitlines()]
        if inventory!=actual:
            raise ValueError('Resource inventory disagrees with saved database')
        return manifest
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error) as exc:
        raise RefError('snapshot_invalid','Snapshot validation failed; inspect it before restoring',5,path=str(path),details={'cause':str(exc)}) from exc


def snapshot_database(catalog: Path, target: Path):
    target.touch(mode=0o600,exist_ok=False)
    with connect(catalog) as source,sqlite3.connect(target) as destination:
        source.backup(destination)


def backup(settings: Settings, output: Path, *, dry_run=False) -> dict:
    target=output.expanduser().absolute()
    if target.exists() or target.is_symlink():
        raise RefError('backup_exists','Choose a new, unused snapshot directory',path=str(target))
    with connect(settings.catalog_path()):
        pass
    if dry_run:
        return dict(output=str(target),dry_run=True,external_contents_included=False)
    with files.file_lock(settings.catalog_path()):
        configuration=settings.config.read_bytes()
        staging=Path(tempfile.mkdtemp(prefix=target.name+'-',suffix='.partial',dir=target.parent))
        (staging/'config.toml').write_bytes(configuration)
        (staging/'config.toml').chmod(0o600)
        snapshot_database(settings.catalog_path(),staging/'catalog.sqlite')
        if settings.config.read_bytes()!=configuration:
            raise RefError('configuration_changed','Configuration changed during backup; inspect the partial snapshot and retry',5,path=str(staging))
        meta=validate_database(staging/'catalog.sqlite')
        with sqlite3.connect((staging/'catalog.sqlite').as_uri()+'?mode=ro',uri=True) as saved:
            saved.row_factory=sqlite3.Row
            inventory=resources.inventory(saved)
        (staging/'resources.jsonl').write_text(''.join(json.dumps(item,ensure_ascii=False)+'\n' for item in inventory))
        manifest=dict(schema_version=1,configuration_path=str(settings.config),catalog_schema_version=meta['schema_version'],catalog_id=meta['catalog_id'],catalog_revision=meta['revision'],external_contents_included=False,
                      members={name:dict(size=(staging/name).stat().st_size,sha256=files.hash_file(staging/name)) for name in sorted(MEMBERS)})
        (staging/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        for member in staging.iterdir():
            member.chmod(0o600)
        validate_snapshot(staging)
        # Exclusive directory creation reserves the destination. Manifest goes last;
        # an interrupted publication never masquerades as a validated snapshot.
        target.mkdir(mode=0o700)
        try:
            for name in [*sorted(MEMBERS),'manifest.json']:
                os.link(staging/name,target/name)
            validate_snapshot(target)
        except (OSError,RefError) as exc:
            raise RefError('backup_incomplete','Snapshot publication was interrupted; retain the partial directories and retry at a new path',4,path=str(target),details={'staging':str(staging)}) from exc
        for member in staging.iterdir():
            member.unlink()
        staging.rmdir()
    return dict(output=str(target),catalog_id=meta['catalog_id'],external_contents_included=False,members=manifest['members'])
