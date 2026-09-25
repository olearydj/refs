import shutil
import sqlite3
from contextlib import closing
from importlib.resources import files

import pytest
from conftest import REFS_COMMAND, SCHEMA_VERSION, TABLE_COUNT

from refs.catalog import connect, migrate
from refs.results import RefError


def old_catalog(path):
    path.mkdir()
    (path / "ready").touch()
    (path / "files.lock").touch()
    with closing(sqlite3.connect(path / "catalog.sqlite")) as c, c:
        c.executescript(files("refs").joinpath("migrations/001_initial.sql").read_text())
        c.execute("INSERT INTO catalog_meta VALUES (1,'stable',1,7)")


def test_automatic_migration_preserves_identity(tmp_path):
    path = tmp_path / "old"
    old_catalog(path)
    with connect(path):
        pass
    assert len(list(path.glob(f"before-schema-{SCHEMA_VERSION}-*.sqlite"))) == 1
    migrate(path)
    migrate(path)
    with connect(path) as c:
        assert tuple(c.execute("SELECT * FROM catalog_meta").fetchone()) == (1, "stable", SCHEMA_VERSION, 7)
        assert c.execute("PRAGMA foreign_key_check").fetchall() == []
        assert (
            c.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'search_projection_%'"
            ).fetchone()[0]
            == TABLE_COUNT
        )


def test_migration_rolls_back_failed_statement(tmp_path):
    path = tmp_path / "old"
    old_catalog(path)
    with closing(sqlite3.connect(path / "catalog.sqlite")) as c, c:
        c.execute("CREATE TABLE collections (collision TEXT)")
    with pytest.raises(sqlite3.OperationalError):
        migrate(path)
    with closing(sqlite3.connect(path / "catalog.sqlite")) as c, c:
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
        assert c.execute("SELECT schema_version FROM catalog_meta").fetchone()[0] == SCHEMA_VERSION
    cli("--catalog", tmp_path / "other", "init", "--reuse-config", expected=3)


def test_move_operations_schema_and_constraints(cli, tmp_path):
    cli('init', '--library-root', tmp_path/'lib')
    with connect(tmp_path/'cat', write=True) as c:
        assert c.execute('SELECT schema_version FROM catalog_meta').fetchone()[0] == SCHEMA_VERSION
        assert c.execute("SELECT name FROM sqlite_master WHERE name='file_operations'").fetchone()
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO file_operations (id,resource_id,old_path,new_path,old_name,new_name,staging_path,state,created_at,updated_at) VALUES ('op','missing','old','new','old','new','stage','other','now','now')")


def test_failed_move_migration_rolls_back(tmp_path):
    path = tmp_path/'old'
    old_catalog(path)
    with closing(sqlite3.connect(path/'catalog.sqlite')) as c, c:
        c.executescript(files('refs').joinpath('migrations/002_zotero_ingest.sql').read_text())
        c.executescript(files('refs').joinpath('migrations/003_source_loc.sql').read_text())
        c.execute('CREATE TABLE file_operations (collision TEXT)')
    with pytest.raises(sqlite3.OperationalError):
        migrate(path)
    with closing(sqlite3.connect(path/'catalog.sqlite')) as c, c:
        assert c.execute('SELECT schema_version FROM catalog_meta').fetchone()[0] == 3


def test_lowercase_migration_preserves_locator_identity_and_disk(tmp_path):
    import json
    path=tmp_path/'old'
    old_catalog(path)
    old_folder=tmp_path/'lib/Unfiled'
    old_folder.mkdir(parents=True)
    (old_folder/'Café.pdf').write_bytes(b'untouched')
    relative='Unfiled/Café/Unfiled/file.pdf'
    locator=dict(path=None,root='library',relative=relative)
    with closing(sqlite3.connect(path/'catalog.sqlite')) as c, c:
        for name in ['002_zotero_ingest.sql','003_source_loc.sql','004_file_operations.sql']:
            c.executescript(files('refs').joinpath('migrations/'+name).read_text())
        c.execute("INSERT INTO sources (id,citation_key,created_at,updated_at,metadata_json,details_json,key_provenance_json,loc) VALUES ('s','key','now','now','{}','{}','{}','Unfiled')")
        c.execute("INSERT INTO resources (id,source_id,locator,root,relative) VALUES ('r','s',?,'library',?)",(json.dumps(locator,sort_keys=True),relative))
    migrate(path)
    migrate(path)
    with connect(path) as c:
        row=c.execute('SELECT id,relative,locator FROM resources').fetchone()
        assert row['id']=='r' and row['relative']=='unfiled/Café/Unfiled/file.pdf'
        assert row['locator']==json.dumps(locator | {'relative':row['relative']},sort_keys=True)
        assert c.execute('SELECT loc FROM sources').fetchone()[0]=='unfiled'
        assert c.execute('SELECT schema_version FROM catalog_meta').fetchone()[0]==SCHEMA_VERSION
    assert [p.name for p in (tmp_path/'lib').iterdir()]==['Unfiled']
    assert (old_folder/'Café.pdf').read_bytes()==b'untouched'


@pytest.mark.parametrize('json_output', [False, True])
def test_read_upgrades_with_notice_and_copy(tmp_path, json_output):
    import json
    import subprocess
    path = tmp_path/'cat'
    old_catalog(path)
    original = (path/'catalog.sqlite').read_bytes()
    command = [*REFS_COMMAND, '--config', str(tmp_path/'config.toml'), '--catalog', str(path)]
    result = subprocess.run(command + (['--json'] if json_output else []) + ['list'], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    safety, = path.glob(f'before-schema-{SCHEMA_VERSION}-*.sqlite')
    with closing(sqlite3.connect(safety)) as c, c:
        assert c.execute('SELECT schema_version FROM catalog_meta').fetchone()[0] == 1
    assert safety.stat().st_size == len(original)
    if json_output:
        assert json.loads(result.stdout)['warnings'][0]['code'] == 'schema_upgraded'
    else:
        assert result.stderr.count('Upgraded catalog schema 1 to 5; safety copy:') == 1
    again = subprocess.run(command + ['list'], capture_output=True, text=True)
    assert again.returncode == 0 and 'Upgraded' not in again.stdout
    assert [json.loads(line)['event'] for line in (path/'refs.log').read_text().splitlines()].count('schema.upgrade') == 1


def test_safety_copy_failure_refuses_before_migration(tmp_path, monkeypatch):
    from pathlib import Path
    path = tmp_path/'cat'
    old_catalog(path)
    original = (path/'catalog.sqlite').read_bytes()
    real_open = Path.open
    def denied(self, *args, **kwargs):
        if self.name.startswith('before-schema-'):
            raise PermissionError('synthetic permission denial')
        return real_open(self, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', denied)
    with pytest.raises(RefError, match='Cannot write schema safety copy') as error:
        with connect(path):
            pass
    assert error.value.issue['code'] == 'unsupported_schema'
    assert (path/'catalog.sqlite').read_bytes() == original


def test_newer_schema_still_refuses(tmp_path):
    path = tmp_path/'cat'
    old_catalog(path)
    with closing(sqlite3.connect(path/'catalog.sqlite')) as c, c:
        c.execute('PRAGMA ignore_check_constraints=ON')
        c.execute('UPDATE catalog_meta SET schema_version=99')
    with pytest.raises(RefError) as error:
        with connect(path):
            pass
    assert error.value.issue['code'] == 'unsupported_schema'
    assert not list(path.glob('before-schema-*'))



def test_upgrade_inside_existing_file_lock(tmp_path):
    from refs.files import file_lock
    path = tmp_path/'cat'
    old_catalog(path)
    with file_lock(path), connect(path) as c:
        assert c.execute('SELECT schema_version FROM catalog_meta').fetchone()[0] == SCHEMA_VERSION


def test_dry_run_upgrades(cli, tmp_path):
    from refs.config import toml_text
    path = tmp_path/'cat'
    old_catalog(path)
    (tmp_path/'config.toml').write_text(toml_text(dict(schema_version=1,catalog=dict(path=str(path)))))
    value = cli('project', 'create', 'preview', '--dry-run')
    assert value['warnings'][0]['code'] == 'schema_upgraded'
    with connect(path) as c:
        assert c.execute('SELECT count(*) FROM projects').fetchone()[0] == 0
