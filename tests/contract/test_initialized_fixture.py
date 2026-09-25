"""Each initialized test home is a private copy of the session template."""

import sqlite3
from contextlib import closing

from conftest import clone_initialized_template


def test_initialized_catalog_copies_are_independent(initialized_template, tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    clone_initialized_template(initialized_template, first)
    clone_initialized_template(initialized_template, second)
    for home in (first, second):
        assert (home / "cat" / "files.lock").is_file()
        assert (home / "cat" / "ready").is_file()
        assert (home / "cat" / "staging").is_dir()
    with closing(sqlite3.connect(first / "cat" / "catalog.sqlite")) as connection, connection:
        connection.execute("UPDATE catalog_meta SET revision=revision+1 WHERE singleton=1")
    with closing(sqlite3.connect(first / "cat" / "catalog.sqlite")) as connection:
        assert connection.execute("SELECT revision FROM catalog_meta").fetchone()[0] == 1
    with closing(sqlite3.connect(second / "cat" / "catalog.sqlite")) as connection:
        assert connection.execute("SELECT revision FROM catalog_meta").fetchone()[0] == 0
