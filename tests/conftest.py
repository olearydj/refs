"""Installed CLI tests always select isolated configuration and data paths."""

import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

SCHEMA_VERSION = 6
TABLE_COUNT = 16
REFS_COMMAND = [sys.executable, "-m", "refs", "--no-project-config"]


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
        result = subprocess.run([*REFS_COMMAND, *map(str, args)], env=cli_env, cwd=cli_cwd, capture_output=True, text=True, check=False)
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
def initialized(cli, tmp_path, initialized_template):
    clone_initialized_template(initialized_template, tmp_path)
    return cli


@pytest.fixture(scope="session")
def initialized_template(tmp_path_factory):
    base = tmp_path_factory.getbasetemp()
    shared = base.parent if os.environ.get("PYTEST_XDIST_WORKER") else base
    template = shared / "refs-initialized-template"
    with (shared / "refs-initialized-template.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not (template / ".complete").exists():
            if template.exists():
                shutil.rmtree(template)
            template.mkdir()
            env = isolated_env(template)
            result = subprocess.run(
                [*REFS_COMMAND, "--json", "init", "--library-root", str(template / "lib")],
                env=env, cwd=template, capture_output=True, text=True, check=False,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            (template / "cat" / "staging").mkdir(mode=0o700)
            (template / ".complete").touch()
        fcntl.flock(lock, fcntl.LOCK_UN)
    return template


def clone_initialized_template(template, destination):
    from refs.config import toml_text

    shutil.copytree(template / "cat", destination / "cat", copy_function=shutil.copy2)
    (destination / "lib").mkdir()
    values = tomllib.loads((template / "config.toml").read_text())
    values["catalog"]["path"] = str(destination / "cat")
    values["resources"]["library_root"] = str(destination / "lib")
    values["resources"]["roots"]["library"] = str(destination / "lib")
    (destination / "config.toml").write_text(toml_text(values))


@pytest.fixture
def reference_path():
    return Path(__file__).parent / "fixtures" / "reference.json"


@pytest.fixture
def zotero_fixture(tmp_path):
    import runpy
    build = runpy.run_path(str(Path(__file__).parent/'fixtures/zotero/fixture.py'))['build']
    return build(tmp_path/'zotero')
