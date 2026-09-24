import json

from refs import bibliography, sources


def test_language_edit_and_unknown_limitations(initialized,tmp_path):
    source=sources.add(tmp_path/'cat',json.dumps({'schema_version':'1.0','metadata':{'type':'book','title':'A Synthetic Book','language':'English'}}).encode(),'synthetic')
    assert source['metadata']['language']=='en'
    for literal in ('eng','en-US','Uncatalogued Language'):
        source=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'metadata.language':literal}},source['revision'])
        assert source['metadata']['language']==('en' if literal=='eng' else literal)
    assert source['limitations']==[{'field':'language','reason':'Unrecognized language retained literally: Uncatalogued Language; supply a language tag if known'}]
    output,warnings=bibliography.serialize([source])
    assert b'langid' not in output
    assert any(w['code']=='language_unrecognized' for w in warnings)
    source=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'metadata.language':'French'}},source['revision'])
    assert source['metadata']['language']=='fr' and not source['limitations']
