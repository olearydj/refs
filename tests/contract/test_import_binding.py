import json

import pytest

from refs import importing, sources
from refs.catalog import connect
from refs.models import SourceCreate
from refs.results import RefError


def create(catalog, key='assigned', **metadata):
    value={'schema_version':'1.0','citation_key':key,'metadata':{'type':'book','title':'A Study','DOI':'10.5555/study',**metadata}}
    return sources.add(catalog,json.dumps(value).encode(),'capture.json')


@pytest.mark.parametrize('format',['bib','refs','csljson'])
def test_bind_fill_retains_key_and_clear(initialized,tmp_path,format):
    catalog=tmp_path/'cat'
    current=create(catalog)
    if format=='bib':
        raw=b'@book{incoming,title={A Study},doi={https://doi.org/10.5555/STUDY},publisher={Press}}'
        result=importing.run(catalog,raw,'incoming.bib')['entries'][0]
    else:
        value={'type':'book','title':'A Study','DOI':'https://doi.org/10.5555/STUDY','publisher':'Press'}
        if format=='refs':
            value={'schema_version':'1.0','citation_key':'incoming','metadata':value}
        result=sources.add(catalog,json.dumps(value).encode(),'incoming.json',format=format)
    assert result.get('binding',{}).get('bound')
    current=sources.show(catalog,current['id'])
    assert current['citation_key']=='assigned' and current['metadata']['publisher']=='Press'
    assert any(p['origin']=='import' for p in current['provenance'])
    sources.update(catalog,current['id'],{'schema_version':'1.0','clear':['metadata.publisher']},current['revision'])
    incoming=SourceCreate.model_validate({'schema_version':'1.0','metadata':{'type':'book','title':'A Study','DOI':'10.5555/study','publisher':'Press'}})
    with connect(catalog,write=True) as c:
        _, result=importing.bind_and_fill(c,incoming,b'synthetic')
        assert result['conflicts']==[{'path':'metadata.publisher','current':None,'incoming':'Press'}]
    assert 'publisher' not in sources.show(catalog,current['id'])['metadata']


def test_isbn_ambiguity_type_edition_and_title(initialized,tmp_path):
    catalog=tmp_path/'cat'
    record=create(catalog,ISBN='978-1-23',edition=2)
    result=importing.run(catalog,b'@book{other,title={Different Title},isbn={978123},edition={3}}','test.bib')
    entry=result['entries'][0]
    assert entry['status']=='conflict' and not entry['binding']['bound']
    assert sources.show(catalog,record['id'])['metadata']['edition']==2
    other=create(catalog,key='separate',DOI='10.5555/other')
    sources.update(catalog,other['id'],{'schema_version':'1.0','set':{'metadata.ISBN':'978123'}},other['revision'])
    result=importing.run(catalog,b'@book{third,title={A Study},isbn={978123}}','test.bib')
    assert result['entries'][0]['code']=='identity_conflict'
    assert len(result['entries'][0]['details']['source_ids'])==2
    title_only=sources.add(catalog,json.dumps({'schema_version':'1.0','metadata':{'type':'book','title':'A Study'}}).encode(),'new.json')
    assert title_only['outcome']=='created' and title_only['warnings'][0]['code']=='likely_match'


def test_dry_run_and_removed_never_bind(initialized,tmp_path):
    catalog=tmp_path/'cat'
    record=create(catalog)
    before=(catalog/'catalog.sqlite').read_bytes()
    importing.run(catalog,b'@book{new,title={A Study},doi={10.5555/study},publisher={Press}}','incoming.bib',dry_run=True)
    assert (catalog/'catalog.sqlite').read_bytes()==before
    sources.set_state(catalog,record['id'],record['revision'],'removed',execute=True)
    with pytest.raises(RefError,match='removed'):
        create(catalog)
