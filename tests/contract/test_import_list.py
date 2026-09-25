import json
import re
import subprocess

import pytest
from conftest import REFS_COMMAND, isolated_env

from refs import importing, sources
from refs.results import RefError


def test_saved_batches_list_newest_first_with_review_tokens(initialized,tmp_path):
    cat=tmp_path/'cat'
    assert initialized('import','list')['data']['items']==[]
    first=importing.run(cat,b'@book{assigned,title={Attention Is All You Need},doi={10.5555/attention},year={2017}}','fixture.bib',origin='zotero')['import_id']
    raw=json.dumps({'type':'book','title':'Attention Is All You Need','DOI':'10.5555/attention','issued':{'date-parts':[[2018]]}}).encode()
    with pytest.raises(RefError) as error:
        sources.add(cat,raw,'incoming.json',format='csljson')
    assert error.value.issue['code'] == 'identity_conflict'
    before=(cat/'catalog.sqlite').read_bytes()
    items=initialized('import','list')['data']['items']
    assert [row['origin'] for row in items]==['add','zotero']
    assert items[1]['import_id']==first
    assert items[0]['counts']=={'applied':0,'unchanged':0,'conflict':1,'invalid':0}
    for row in items:
        assert row['created'] and row['batch_revision']==importing.show(cat,row['import_id'])['batch_revision']
    assert (cat/'catalog.sqlite').read_bytes()==before
    env=isolated_env(tmp_path)
    result=subprocess.run([*REFS_COMMAND,'import','list'],env=env,capture_output=True,text=True)
    assert result.returncode==0 and len(result.stdout.splitlines())==2
    assert result.stdout.startswith(items[0]['import_id'][:8]+'\tadd\t')
    assert 'conflict 1' in result.stdout and 'batch revision' not in result.stdout
    assert not re.search(r'\b\d{19}\b',result.stdout)
    assert not re.search(r'\d{2}:\d{2}:\d{2}\.\d',result.stdout)
    importing.reconcile(cat,items[0]['import_id'],['assigned'],execute=True,revision=items[0]['batch_revision'])
    assert importing.list_batches(cat)['items'][0]['counts']['conflict']==0
