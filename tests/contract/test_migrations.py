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
        assert tuple(c.execute("SELECT * FROM catalog_meta").fetchone()) == (1, "stable", 3, 7)
        assert c.execute("PRAGMA foreign_key_check").fetchall() == []
        assert (
            c.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'search_projection_%'"
            ).fetchone()[0]
            == 14
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
        assert c.execute("SELECT schema_version FROM catalog_meta").fetchone()[0] == 3
    cli("--catalog", tmp_path / "other", "init", "--reuse-config", expected=3)
