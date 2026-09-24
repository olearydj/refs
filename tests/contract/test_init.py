import sqlite3
import stat
from contextlib import closing


def test_paths_before_init(cli, tmp_path):
    result = cli("paths")["data"]
    assert result["catalog"]["path"] == str(tmp_path / "cat")
    assert result["config"]["path"] == str(tmp_path / "config.toml")
    assert not (tmp_path / "cat").exists()
    assert not (tmp_path / "config.toml").exists()


def test_init_and_repeat(cli, tmp_path):
    first = cli("init", "--library-root", tmp_path / "lib")["data"]
    db = tmp_path / "cat" / "catalog.sqlite"
    before = db.read_bytes()
    second = cli("init", "--library-root", tmp_path / "lib")["data"]
    assert second["catalog_id"] == first["catalog_id"]
    assert second["unchanged"]
    assert db.read_bytes() == before
    assert stat.S_IMODE(db.stat().st_mode) == 0o600
    assert stat.S_IMODE(db.parent.stat().st_mode) == 0o700
    assert (db.parent / "ready").exists()
    with closing(sqlite3.connect(db)) as connection, connection:
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA journal_mode").fetchone() == ("delete",)


def test_init_preview_has_no_effect(cli, tmp_path):
    cli("init", "--library-root", tmp_path / "lib", "--dry-run")
    assert list(tmp_path.iterdir()) == [tmp_path / "work"]


def test_unknown_directory_not_overwritten(cli, tmp_path):
    (tmp_path / "cat").mkdir()
    sentinel = tmp_path / "cat" / "precious"
    sentinel.write_text("unchanged")
    result = cli("init", "--no-library", expected=3)
    assert result["errors"][0]["code"] == "init_conflict"
    assert sentinel.read_text() == "unchanged"


def test_missing_catalog_not_created(cli, tmp_path):
    import pytest

    from refs.catalog import connect
    from refs.results import RefError

    with pytest.raises(RefError, match="missing"):
        with connect(tmp_path / "cat"):
            pass
    assert not (tmp_path / "cat").exists()
