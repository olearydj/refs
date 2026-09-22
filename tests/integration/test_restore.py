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
        value=json.loads(path.read_text());value['schema_version']=999
        path.write_text(json.dumps(value))
    with pytest.raises(RefError):
        recovery.validate_snapshot(target)
