"""Human updates use the current revision; supplied agent guards still refuse stale writes."""

import json


def test_update_without_guard_uses_current_revision_and_reports_new_one(initialized,tmp_path,reference_path):
    created=initialized('add','--format','refs','--input',reference_path)['data']
    changed=initialized('update',created['id'],'--set','metadata.genre="First value"')['data']
    assert changed['revision']==2
    assert changed['metadata']['genre']=='First value'
    patch=tmp_path/'patch.json'
    patch.write_text(json.dumps({'schema_version':'1.0','set':{'metadata.genre':'Second value'}}))
    second=initialized('update',created['id'],'--patch',patch)['data']
    assert second['revision']==3
    assert second['metadata']['genre']=='Second value'
    same=initialized('update',created['id'],'--patch',patch)['data']
    assert same['revision']==3 and same['unchanged'] is True
    assert initialized('show',created['id'])['data']['metadata']['genre']=='Second value'


def test_update_supplied_guard_preserves_stale_refusal_and_state(initialized,tmp_path,reference_path):
    created=initialized('add','--format','refs','--input',reference_path)['data']
    changed=initialized('update',created['id'],'--if-revision',1,'--set','metadata.genre="First value"')['data']
    assert changed['revision']==2
    before=(tmp_path/'cat/catalog.sqlite').read_bytes()
    refused=initialized('update',created['id'],'--if-revision',1,'--set','metadata.genre="Stale value"',expected=3)
    assert refused['errors'][0]['code']=='stale_revision'
    assert refused['errors'][0]['details']=={'expected':1,'actual':2}
    assert (tmp_path/'cat/catalog.sqlite').read_bytes()==before
    assert initialized('show',created['id'])['data']['metadata']['genre']=='First value'
    current=initialized('update',created['id'],'--if-revision',2,'--set','metadata.genre="Current value"')['data']
    assert current['revision']==3
    assert current['metadata']['genre']=='Current value'
