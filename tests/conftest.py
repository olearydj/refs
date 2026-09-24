"""Installed CLI tests always select isolated configuration and data paths."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

SCHEMA_VERSION = 5
TABLE_COUNT = 15


def pytest_addoption(parser):
    parser.addoption("--require-tools", action="store_true", help="fail when an external rendering tool is unavailable")


def pytest_configure(config):
    config._refs_require_tools = config.getoption("--require-tools") or os.environ.get("REFS_REQUIRE_TOOLS") == "1"


def pytest_terminal_summary(terminalreporter):
    missing = set()
    for report in terminalreporter.stats.get("skipped", []):
        reason = str(report.longrepr)
        match = re.search(r"Rendering consumer unavailable: ([\w.-]+)", reason)
        if match:
            missing.add(match.group(1))
    if missing:
        terminalreporter.write_line("Missing rendering tools: " + ", ".join(sorted(missing)))


def isolated_env(tmp_path):
    return dict(os.environ, REFS_CONFIG=str(tmp_path / "config.toml"), REFS_CATALOG=str(tmp_path / "cat"))


@pytest.fixture
def cli_env(tmp_path):
    return isolated_env(tmp_path)


@pytest.fixture
def cli_cwd(tmp_path):
    path = tmp_path / "work"
    path.mkdir()
    return path


@pytest.fixture
def human(initialized, cli_env, cli_cwd):
    def run(*args, expected=0):
        result = subprocess.run([sys.executable, "-m", "refs", "--no-project-config", *map(str, args)], env=cli_env, cwd=cli_cwd, capture_output=True, text=True, check=False)
        assert result.returncode == expected, result.stdout + result.stderr
        return result.stdout + result.stderr
    return run


def extracted(database, output):
    import runpy

    from refs.adapters import zotero

    runpy.run_path("tools/zotero_extract/extract.py")["extract"](database, output, database.parent, database.parent / "base", database.parent / "better-bibtex.sqlite")
    return zotero.read(output)


@pytest.fixture
def cli(cli_env, cli_cwd):

    def run(*args, expected=0):
        result = subprocess.run(
            [sys.executable, "-m", "refs", "--json", "--no-project-config", *map(str, args)], env=cli_env,
            cwd=cli_cwd, capture_output=True, text=True, check=False,
        )
        assert result.returncode == expected, (result.stdout, result.stderr)
        assert result.stderr == "", result.stderr
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
