import json
import runpy
from pathlib import Path

import pytest

from refs import importing, sources
from refs.results import RefError


def conflicting(catalog, *, title='Imported Title', origin='library'):
    return importing.run(catalog, f'@book{{book,title={{{title}}},publisher={{New Publisher}},year={{2020}}}}'.encode(), 'library.bib', origin=origin)


def test_keep_current_persists_without_changing_source_and_is_scoped(initialized, tmp_path):
    catalog=tmp_path/'cat'
    importing.run(catalog,b'@book{book,title={Current Title},publisher={Current Publisher},year={2020}}','first.bib')
    batch=conflicting(catalog)['import_id']
    before=sources.show(catalog,'book')
    snapshot=(catalog/'catalog.sqlite').read_bytes()
    preview=initialized('import','reconcile',batch,'--keep-current','book')['data']
    assert (catalog/'catalog.sqlite').read_bytes()==snapshot
    assert all(d['action']=='keep_current' for d in preview['entries'][0]['decisions'])
    assert preview['entries'][0]['remaining_conflicts']==[]
    from refs.render import render_text
    assert 'Keep current metadata.title: "Current Title"' in render_text('import reconcile',preview,[])
    result=initialized('import','reconcile',batch,'--keep-current','book','--execute','--if-batch-revision',preview['batch_revision'])['data']
    assert result['batch_revision']!=preview['batch_revision']
    current=sources.show(catalog,'book')
    assert current['metadata']==before['metadata'] and current['revision']==before['revision']
    review=importing.show(catalog,batch)
    assert review['entries'][0]['binding']['conflicts']==[]
    assert review['counts']['conflict']==0
    assert conflicting(catalog)['counts']['unchanged']==1
    assert conflicting(catalog,origin='other')['counts']['conflict']==1
    changed=conflicting(catalog,title='Later Incoming Title')
    assert changed['entries'][0]['conflicts']==['metadata.title']
    sources.update(catalog,'book',{'schema_version':'1.0','set':{'metadata.title':'Later Current Title'}},current['revision'])
    assert conflicting(catalog)['entries'][0]['conflicts']==['metadata.title']


def test_keep_current_partial_mixed_and_stale(initialized,tmp_path):
    catalog=tmp_path/'cat'
    importing.run(catalog,b'@book{book,title={Current Title},publisher={Current Publisher},year={2020}}','first.bib')
    batch=conflicting(catalog)['import_id']
    preview=importing.reconcile(catalog,batch,[],keep_current=['book.metadata.title'])
    assert [x['path'] for x in preview['entries'][0]['remaining_conflicts']]==['metadata.publisher']
    with pytest.raises(RefError,match='Preview'):
        importing.reconcile(catalog,batch,[],keep_current=['book'],execute=True)
    with pytest.raises(RefError,match='one decision'):
        importing.reconcile(catalog,batch,['book.metadata.title'],keep_current=['book.metadata.title'])
    current=sources.show(catalog,'book')
    sources.update(catalog,'book',{'schema_version':'1.0','set':{'metadata.volume':'2'}},current['revision'])
    with pytest.raises(RefError,match='changed'):
        importing.reconcile(catalog,batch,[],keep_current=['book'],execute=True,revision=preview['batch_revision'])
    preview=importing.reconcile(catalog,batch,['book.metadata.publisher'],keep_current=['book.metadata.title'])
    importing.reconcile(catalog,batch,['book.metadata.publisher'],keep_current=['book.metadata.title'],execute=True,revision=preview['batch_revision'])
    current=sources.show(catalog,'book')
    assert current['metadata']['title']=='Current Title'
    assert current['metadata']['publisher']=='New Publisher'
    assert 'metadata.title' not in current['corrected_fields']
    assert conflicting(catalog)['counts']['unchanged']==1


def test_zotero_keep_current_applies_on_later_import(initialized,tmp_path,zotero_fixture):
    extract=runpy.run_path(str(Path(__file__).parents[2]/'tools/zotero_extract/extract.py'))['extract']
    directory=tmp_path/'input'
    extract(zotero_fixture,directory,zotero_fixture.parent,base_path=zotero_fixture.parent/'base',legacy=zotero_fixture.parent/'better-bibtex.sqlite')
    importing.run_zotero(tmp_path/'cat',directory,origin='zotero')
    path=directory/'items/ITEM0002.json'
    value=json.loads(path.read_text())
    value['data']['title']='Later Book Title'
    path.write_text(json.dumps(value))
    batch=importing.run_zotero(tmp_path/'cat',directory,origin='zotero')['import_id']
    entry=next(e for e in importing.show(tmp_path/'cat',batch)['entries'] if e['item_key']=='ITEM0002')
    key=entry['citation_key']
    preview=importing.reconcile(tmp_path/'cat',batch,[],keep_current=[key])
    importing.reconcile(tmp_path/'cat',batch,[],keep_current=[key],execute=True,revision=preview['batch_revision'])
    assert importing.run_zotero(tmp_path/'cat',directory,origin='zotero')['counts']=={'applied':0,'unchanged':6,'conflict':0,'invalid':0}
