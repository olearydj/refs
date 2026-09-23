import json
import runpy

import pytest

from refs import resources, sources
from refs.catalog import connect
from refs.config import select
from refs.results import RefError

tool=runpy.run_path('tools/assign_initial_loc.py')


def test_assignment_rules_preview_and_apply(initialized,tmp_path):
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    box=tmp_path/'Box'
    ids={}
    for key,paths in {
        'both':['Box/Papers/Café/book.pdf','storage/KEY/snapshot.html'],
        'single':['storage/OTHER/file.pdf'],
        'none':['elsewhere/file.pdf'],
        'managed':['lib/unfiled/copy.pdf'],
        'fileless':[],
        'ambiguous':['Box/A/one.pdf','Box/B/two.pdf'],
    }.items():
        record=tmp_path/(key+'.json')
        record.write_text(json.dumps({'schema_version':'1.0','citation_key':key,'metadata':{'title':key}}))
        source=initialized('add','--format','refs','--input',record)['data']
        ids[key]=source['id']
        for name in paths:
            path=tmp_path/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(name.encode())
            resources.link(settings,source['id'],path=path)
    with connect(settings.catalog_path(),write=True) as c:
        c.execute("INSERT INTO collections (id,library_uri,item_key,name,path) VALUES ('c','test','c','Collection','History/Collection')")
        for key in ['single','fileless']:
            c.execute('INSERT INTO source_collections VALUES (?,?)',(ids[key],'c'))
    before=(tmp_path/'cat/catalog.sqlite').read_bytes()
    preview=tool['preview'](settings,box)
    by_key={entry['citation_key']:entry for entry in preview}
    assert by_key['both']['loc']=='Papers/Café'
    assert by_key['single']['loc']=='unfiled'
    assert by_key['none']['loc']=='unfiled'
    assert by_key['managed']['loc']=='unfiled'
    assert all(by_key[key]['loc'] is None for key in ['fileless','ambiguous'])
    assert (tmp_path/'cat/catalog.sqlite').read_bytes()==before
    applied=tool['apply'](settings,preview)
    assert sum(entry['state']=='applied' for entry in applied)==4
    for key in ['both','single']:
        shown=sources.show(settings.catalog_path(),ids[key])
        assert shown['loc']==by_key[key]['loc'] and 'loc' not in shown['corrected_fields']
    assert (box/'Papers/Café/book.pdf').exists() and (tmp_path/'storage/KEY/snapshot.html').exists()
    assert all(entry['state']=='unchanged' for entry in tool['preview'](settings,box))


def test_assignment_revision_guard(initialized,tmp_path,reference_path):
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    source=initialized('add','--format','refs','--input',reference_path)['data']
    path=tmp_path/'Box/Topic/file.pdf'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'synthetic')
    resources.link(settings,source['id'],path=path)
    proposal=tool['preview'](settings,tmp_path/'Box')
    current=sources.show(settings.catalog_path(),source['id'])
    sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'loc':'Owner Choice'}},current['revision'])
    with pytest.raises(RefError) as caught:
        tool['apply'](settings,proposal)
    assert caught.value.issue['code']=='stale_revision'
    assert sources.show(settings.catalog_path(),source['id'])['loc']=='Owner Choice' and path.exists()
