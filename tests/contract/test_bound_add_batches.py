import json

import pytest

from refs import importing, sources
from refs.catalog import connect
from refs.results import RefError


@pytest.mark.parametrize('format', ['refs', 'csljson', 'bib'])
@pytest.mark.parametrize('identifier', ['DOI', 'ISBN'])
def test_bound_add_conflicts_persist_and_reconcile(initialized, tmp_path, format, identifier):
    catalog = tmp_path/'cat'
    identity = {identifier: '10.5555/attention' if identifier == 'DOI' else '9781234567890'}
    item = {'key':'ATTN0001','data':{'itemType':'book','title':'Attention Is All You Need','date':'2017-12-05','citationKey':'assigned',**identity}}
    raw = json.dumps(item).encode()
    with connect(catalog, write=True) as connection:
        result = importing.apply_zotero(connection, {'key':'ATTN0001','item':item,'raw':raw,'locator':'synthetic.json'}, {'library_uri':'users/123'}, 'fixture')
    assert result['status']=='applied'
    metadata = {'type':'book','title':'Attention Is All You Need','issued':{'date-parts':[[2017]]},'publisher':'Synthetic Press',**identity}
    incoming = json.dumps(metadata if format=='csljson' else {'schema_version':'1.0','metadata':metadata}).encode()
    if format=='bib':
        incoming = f'@book{{assigned,title={{Attention Is All You Need}},year={{2017}},publisher={{Synthetic Press}},{identifier.lower()}={{{identity[identifier]}}}}}'.encode()
    def add(dry_run=False):
        return importing.add(catalog,incoming,'incoming.bib',dry_run=dry_run) if format=='bib' else sources.add(catalog,incoming,'incoming.json',format=format,dry_run=dry_run)
    with pytest.raises(RefError):
        add(True)
    with connect(catalog) as connection:
        assert connection.execute('SELECT count(*) FROM imports').fetchone()[0]==0
    with pytest.raises(RefError):
        add()
    with connect(catalog) as connection:
        batch = connection.execute('SELECT * FROM imports').fetchone()
        assert batch['origin']=='add' and batch['conflict']==1
        assert connection.execute('SELECT count(*) FROM import_entries').fetchone()[0]==1
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0]==1
    review=importing.show(catalog,batch['id'])
    entry=review['entries'][0]
    assert entry['binding']['filled']==['metadata.publisher']
    assert entry['binding']['conflicts'][0]['path']=='metadata.issued.date-parts'
    assert sources.show(catalog,'assigned')['metadata']['issued']['date-parts']==[[2017,12,5]]
    importing.reconcile(catalog,batch['id'],[],keep_current=['assigned'],execute=True,revision=review['batch_revision'])
    assert importing.show(catalog,batch['id'])['counts']['conflict']==0
    add()
    with connect(catalog) as connection:
        assert connection.execute('SELECT count(*) FROM imports').fetchone()[0]==1


@pytest.mark.parametrize('format', ['refs','bib'])
def test_unbound_and_identical_add_do_not_create_batches(initialized,tmp_path,format):
    raw=b'@book{sample,title={Synthetic Work},year={2020}}' if format=='bib' else json.dumps({'schema_version':'1.0','citation_key':'sample','metadata':{'type':'book','title':'Synthetic Work'}}).encode()
    for _ in range(2):
        if format=='bib':
            importing.add(tmp_path/'cat',raw,'input.bib')
        else:
            sources.add(tmp_path/'cat',raw,'input.json')
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM imports').fetchone()[0]==0
