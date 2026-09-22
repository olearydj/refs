"""Installed CLI tests always select isolated configuration and data paths."""

import json
import os
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def cli(tmp_path):
    env = dict(os.environ, REFS_CONFIG=str(tmp_path / "config.toml"),
               REFS_CATALOG=str(tmp_path / "cat"))

    def run(*args, expected=0):
        result = subprocess.run(
            ["refs", "--json", *map(str, args)], env=env,
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == expected, (result.stdout, result.stderr)
        value = json.loads(result.stdout)
        assert value["schema_version"] == "1.0"
        return value

    return run


@pytest.fixture
def initialized(cli, tmp_path):
    cli("init", "--library-root", tmp_path / "lib")
    return cli


@pytest.fixture
def reference_path():
    return Path(__file__).parent / "fixtures" / "reference.json"


@pytest.fixture
def zotero_fixture(tmp_path):
    import runpy
    build = runpy.run_path(str(Path(__file__).parent/'fixtures/zotero/fixture.py'))['build']
    return build(tmp_path/'zotero')
