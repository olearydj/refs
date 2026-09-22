"""Execute the documented procedure itself in disposable homes."""

import os
import re
import sqlite3
import subprocess
from pathlib import Path

import pytest

from refs import recovery
from refs.config import select
from refs.results import RefError


def procedure(name):
    text=Path('docs/restore.md').read_text()
    return re.search(r'```python '+name+r'\n(.*?)\n```',text,re.S).group(1)


def run_restore(snapshot,home):
    result=subprocess.run(['python','-',str(snapshot),str(home)],input=procedure('restore'),text=True,capture_output=True)
    return result


def test_documented_restore_and_all_tables(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    initialized('update',source['id'],'--if-revision',1,'--set','metadata.volume="99"')
    initialized('project','create','paper')
    initialized('project','cite','paper',source['id'])
    initialized('export','--project','paper','--output',tmp_path/'paper.bib')
    initialized('resource','add',source['id'],'--path',tmp_path/'missing.pdf')
    selected=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'))
    snapshot=tmp_path/'snapshot'
    recovery.backup(selected,snapshot)
    home=tmp_path/'restored'
    result=run_restore(snapshot,home)
    assert result.returncode==0,result.stderr
    assert (home/'config.toml').read_text()==(snapshot/'config.toml').read_text().replace(str(tmp_path/'cat'),str(home/'cat'))
    with sqlite3.connect(snapshot/'catalog.sqlite') as saved,sqlite3.connect(home/'cat'/'catalog.sqlite') as restored:
        for (name,) in saved.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            assert saved.execute(f'SELECT * FROM "{name}"').fetchall()==restored.execute(f'SELECT * FROM "{name}"').fetchall(),name
    env=dict(os.environ,REFS_CONFIG=str(home/'config.toml'),REFS_CATALOG=str(home/'cat'))
    for args in [('paths',),('list',),('show',source['id']),('project','show','paper'),('resource','check')]:
        result=subprocess.run(['refs','--json',*args],env=env,text=True,capture_output=True)
        assert result.returncode==0,result.stderr
    assert run_restore(snapshot,home).returncode!=0


@pytest.mark.parametrize('damage',['bytes','symlink','version'])
def test_corruption_is_refused(initialized,tmp_path,damage):
    import json
    selected=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'))
    target=tmp_path/'snapshot'
    recovery.backup(selected,target)
    if damage=='bytes':
        (target/'catalog.sqlite').write_bytes(b'corrupt')
    elif damage=='symlink':
        (target/'config.toml').unlink()
        (target/'config.toml').symlink_to(selected.config)
    else:
        path=target/'manifest.json'
        value=json.loads(path.read_text())
        value['schema_version']=999
        path.write_text(json.dumps(value))
    with pytest.raises(RefError):
        recovery.validate_snapshot(target)


def test_documented_hot_journal_recovery(initialized,tmp_path):
    catalog=tmp_path/'cat'
    database=catalog/'catalog.sqlite'
    with sqlite3.connect(database) as connection:
        connection.execute('CREATE TABLE synthetic_padding (value BLOB)')
        connection.executemany('INSERT INTO synthetic_padding VALUES (?)',[(b'a'*4096,)]*100)
    crash="""import os,sqlite3,sys
connection=sqlite3.connect(sys.argv[1])
connection.execute('PRAGMA cache_size=1')
connection.execute('BEGIN IMMEDIATE')
connection.execute("UPDATE synthetic_padding SET value=zeroblob(4096)")
os._exit(0)
"""
    subprocess.run(['python','-c',crash,str(database)],check=True)
    journal=Path(str(database)+'-journal')
    assert journal.exists() and journal.stat().st_size>0
    result=subprocess.run(['python','-',str(catalog)],input=procedure('hot-journal'),text=True,capture_output=True)
    assert result.returncode==0,result.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute('SELECT value FROM synthetic_padding LIMIT 1').fetchone()[0]==b'a'*4096


def test_zotero_decisions_and_fourteen_tables_restore(initialized,zotero_fixture,tmp_path):
    import json
    import runpy

    from refs import importing
    from refs.catalog import connect

    directory=tmp_path/'input'
    runpy.run_path('tools/zotero_extract/extract.py')['extract'](zotero_fixture,directory,zotero_fixture.parent,zotero_fixture.parent/'base',zotero_fixture.parent/'better-bibtex.sqlite')
    initialized('import','--format','zotero','--input',directory)
    path=directory/'items/ITEM0002.json'
    value=json.loads(path.read_bytes())
    value['data']['title']='Explicitly Revised Book'
    path.write_text(json.dumps(value))
    batch=initialized('import','--format','zotero','--input',directory,expected=4)['data']['import_id']
    preview=importing.reconcile(tmp_path/'cat',batch,['extra2.metadata.title'])
    importing.reconcile(tmp_path/'cat',batch,['extra2.metadata.title'],execute=True,revision=preview['batch_revision'])
    selected=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'))
    snapshot=tmp_path/'snapshot'
    recovery.backup(selected,snapshot)
    assert recovery.validate_snapshot(snapshot)['external_contents_included'] is False
    result=run_restore(snapshot,tmp_path/'restored')
    assert result.returncode==0,result.stderr
    with connect(tmp_path/'cat') as original, connect(tmp_path/'restored/cat') as restored:
        tables=[row[0] for row in original.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'search_projection_%'")]
        assert len(tables)==14
        for name in tables:
            assert [tuple(r) for r in original.execute(f'SELECT * FROM "{name}"')]==[tuple(r) for r in restored.execute(f'SELECT * FROM "{name}"')],name
        for name in ('import_entries','collections','source_collections','source_relations','origin_identities','originals'):
            assert restored.execute(f'SELECT count(*) FROM {name}').fetchone()[0]>0
        assert restored.execute("SELECT count(*) FROM import_entries WHERE decisions_json<>'[]'").fetchone()[0]==1
    assert importing.show(tmp_path/'restored/cat',batch)['entries'][1]['decisions']


def test_schema_two_table_damage_is_refused(initialized,tmp_path):
    database=tmp_path/'cat/catalog.sqlite'
    with sqlite3.connect(database) as c:
        c.execute('ALTER TABLE import_entries RENAME COLUMN decisions_json TO wrong')
    with pytest.raises(RefError,match='schema'):
        recovery.validate_database(database)
