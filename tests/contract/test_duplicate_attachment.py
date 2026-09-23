import json

from refs import sources


def test_copy_warns_without_writes_for_linked_duplicate(initialized,tmp_path):
    source=sources.add(tmp_path/'cat',json.dumps({'schema_version':'1.0','citation_key':'attention','metadata':{'type':'article','title':'Attention Is All You Need'}}).encode(),'synthetic.json')
    box=tmp_path/'box-linked.pdf'
    incoming=tmp_path/'download.pdf'
    box.write_bytes(b'%PDF-1.4 synthetic Attention fixture')
    incoming.write_bytes(box.read_bytes())
    linked=initialized('resource','add',source['id'],'--path',box)['data']
    before=(tmp_path/'cat/catalog.sqlite').read_bytes()
    for flags in [('--dry-run',),()]:
        result=initialized('resource','add',source['id'],'--path',incoming,'--copy',*flags)
        assert result['data']['copied'] is False
        assert result['data']['duplicate_resource_id']==linked['id']
        assert result['warnings'][0]['code']=='duplicate_attachment'
        assert result['warnings'][0]['details']['resource_id']==linked['id']
        assert linked['id'] in result['warnings'][0]['message']
        assert (tmp_path/'cat/catalog.sqlite').read_bytes()==before
        assert len(sources.show(tmp_path/'cat',source['id'])['resources'])==1
        assert not list((tmp_path/'lib').rglob('*.pdf'))
        assert incoming.read_bytes()==box.read_bytes()
    # Same name is not evidence of identical contents. Hash current file bytes,
    # rather than trusting a stale saved digest or the name.
    incoming.write_bytes(b'%PDF-1.4 different content')
    result=initialized('resource','add',source['id'],'--path',incoming,'--copy')
    assert result['data']['copied'] is True
