import shutil
import sqlite3
from importlib.resources import files

import pytest

from refs.catalog import connect, migrate
from refs.results import RefError


def old_catalog(path):
    path.mkdir()
    (path / "ready").touch()
    with sqlite3.connect(path / "catalog.sqlite") as c:
        c.executescript(files("refs").joinpath("migrations/001_initial.sql").read_text())
        c.execute("INSERT INTO catalog_meta VALUES (1,'stable',1,7)")


def test_explicit_migration_preserves_identity(tmp_path):
    path = tmp_path / "old"
    old_catalog(path)
    with pytest.raises(RefError):
        with connect(path):
            pass
    migrate(path)
    migrate(path)
    with connect(path) as c:
        assert tuple(c.execute("SELECT * FROM catalog_meta").fetchone()) == (1, "stable", 4, 7)
        assert c.execute("PRAGMA foreign_key_check").fetchall() == []
        assert (
            c.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'search_projection_%'"
            ).fetchone()[0]
            == 15
        )


def test_migration_rolls_back_failed_statement(tmp_path):
    path = tmp_path / "old"
    old_catalog(path)
    with sqlite3.connect(path / "catalog.sqlite") as c:
        c.execute("CREATE TABLE collections (collision TEXT)")
    with pytest.raises(sqlite3.OperationalError):
        migrate(path)
    with sqlite3.connect(path / "catalog.sqlite") as c:
        assert c.execute("SELECT schema_version FROM catalog_meta").fetchone()[0] == 1
        assert not c.execute("SELECT 1 FROM sqlite_master WHERE name='import_entries'").fetchone()


def test_reuse_config(cli, tmp_path):
    cli("init", "--library-root", tmp_path / "lib")
    config = tmp_path / "config.toml"
    before = config.read_bytes()
    cli("init", "--reuse-config", expected=3)
    shutil.rmtree(tmp_path / "cat")
    cli("init", expected=3)
    cli("init", "--reuse-config", "--dry-run")
    assert not (tmp_path / "cat").exists()
    cli("init", "--reuse-config")
    assert config.read_bytes() == before
    assert (tmp_path / "lib").is_dir()
    with connect(tmp_path / "cat") as c:
        assert c.execute("SELECT schema_version FROM catalog_meta").fetchone()[0] == 4
    cli("--catalog", tmp_path / "other", "init", "--reuse-config", expected=3)


def test_move_operations_schema_and_constraints(cli, tmp_path):
    cli('init', '--library-root', tmp_path/'lib')
    with connect(tmp_path/'cat', write=True) as c:
        assert c.execute('SELECT schema_version FROM catalog_meta').fetchone()[0] == 4
        assert c.execute("SELECT name FROM sqlite_master WHERE name='file_operations'").fetchone()
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO file_operations (id,resource_id,old_path,new_path,old_name,new_name,staging_path,state,created_at,updated_at) VALUES ('op','missing','old','new','old','new','stage','other','now','now')")


def test_failed_move_migration_rolls_back(tmp_path):
    path = tmp_path/'old'
    old_catalog(path)
    with sqlite3.connect(path/'catalog.sqlite') as c:
        c.executescript(files('refs').joinpath('migrations/002_zotero_ingest.sql').read_text())
        c.executescript(files('refs').joinpath('migrations/003_source_loc.sql').read_text())
        c.execute('CREATE TABLE file_operations (collision TEXT)')
    with pytest.raises(sqlite3.OperationalError):
        migrate(path)
    with sqlite3.connect(path/'catalog.sqlite') as c:
        assert c.execute('SELECT schema_version FROM catalog_meta').fetchone()[0] == 3
