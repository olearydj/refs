"""Snapshots use SQLite and contain inventories, never resource contents."""

import json
import sqlite3

import pytest

from refs import recovery
from refs.config import select
from refs.results import RefError


def test_snapshot_members_and_incomplete_import(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    missing=tmp_path/'missing.pdf'
    initialized('resource','add',source['id'],'--path',missing)
    with sqlite3.connect(tmp_path/'cat'/'catalog.sqlite') as connection:
        connection.execute("INSERT INTO imports (id,origin,file_digest,started_at) VALUES ('unfinished','synthetic','abc','today')")
    selected=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'))
    target=tmp_path/'snapshot'
    recovery.backup(selected,target)
    manifest=recovery.validate_snapshot(target)
    assert manifest['external_contents_included'] is False
    assert set(p.name for p in target.iterdir())=={'catalog.sqlite','config.toml','resources.jsonl','manifest.json'}
    inventory=[json.loads(line) for line in (target/'resources.jsonl').read_text().splitlines()]
    assert inventory[0]['path']==str(missing)
    with sqlite3.connect(target/'catalog.sqlite') as connection:
        assert connection.execute("SELECT finished_at FROM imports WHERE id='unfinished'").fetchone()[0] is None
    with pytest.raises(RefError):
        recovery.backup(selected,target)


def test_configuration_change_refuses_publication(initialized,tmp_path,monkeypatch):
    selected=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'))
    original=recovery.snapshot_database
    def changed(*args):
        original(*args)
        selected.config.write_text(selected.config.read_text()+'\n# changed\n')
    monkeypatch.setattr(recovery,'snapshot_database',changed)
    with pytest.raises(RefError):
        recovery.backup(selected,tmp_path/'snapshot')
    assert not (tmp_path/'snapshot').exists()


def test_snapshot_interruption_and_preview(initialized,tmp_path,monkeypatch):
    selected=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'))
    target=tmp_path/'snapshot'
    assert recovery.backup(selected,target,dry_run=True)['dry_run']
    assert not target.exists()
    monkeypatch.setattr(recovery,'snapshot_database',lambda *args: (_ for _ in ()).throw(OSError('synthetic failure')))
    with pytest.raises(OSError):
        recovery.backup(selected,target)
    assert not target.exists()
    assert list(tmp_path.glob('*.partial'))


def test_missing_table_is_not_a_supported_snapshot(initialized,tmp_path):
    with sqlite3.connect(tmp_path/'cat'/'catalog.sqlite') as connection:
        connection.execute('DROP TABLE project_sources')
    with pytest.raises(RefError) as error:
        recovery.backup(select(str(tmp_path/'config.toml'),str(tmp_path/'cat')),tmp_path/'snapshot')
    assert error.value.issue['code']=='unsupported_schema'


def test_backup_human_confirmation(initialized,tmp_path):
    import os
    import subprocess
    target=tmp_path/'snapshot'
    result=subprocess.run(['refs','backup','--output',str(target)],env=dict(os.environ,REFS_CONFIG=str(tmp_path/'config.toml'),REFS_CATALOG=str(tmp_path/'cat')),text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    assert result.stdout.splitlines()[0]==f'Wrote snapshot {target} (external file bytes excluded)'



@pytest.mark.parametrize('marker', [None, 'another-format'])
def test_snapshot_format_is_required(initialized,tmp_path,marker):
    target=tmp_path/'snapshot'
    recovery.backup(select(str(tmp_path/'config.toml'),str(tmp_path/'cat')),target)
    assert recovery.validate_snapshot(target)['format']=='refs-backup'
    path=target/'manifest.json'
    manifest=json.loads(path.read_text())
    if marker is None:
        del manifest['format']
    else:
        manifest['format']=marker
    path.write_text(json.dumps(manifest))
    with pytest.raises(RefError):
        recovery.validate_snapshot(target)
