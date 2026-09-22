import json

import pytest

from refs import bibliography, languages, naming, sources
from refs.adapters import bibtex, csl, zotero
from refs.models import SourceCreate


@pytest.mark.parametrize(('incoming','expected'), [('English','en'),('eng','en'),('en','en'),('en-US','en-US'),('Uncatalogued Language','Uncatalogued Language'),('ger','de'),('deu','de'),('fre','fr'),('fra','fr'),('spa','es'),('chi','zh'),('zho','zh'),('jpn','ja')])
def test_language_normalization_all_routes(incoming,expected):
    metadata={'type':'book','title':'A Synthetic Book','language':incoming}
    proposals=[
        SourceCreate.model_validate({'schema_version':'1.0','metadata':metadata}),
        csl.parse(json.dumps(metadata).encode()),
        bibtex.parse(f'@book{{x,title={{A Synthetic Book}},language={{{incoming}}}}}'.encode())['source'],
        zotero.parse({'key':'ITEM0001','data':{'itemType':'book','title':'A Synthetic Book','language':incoming}},{'library_uri':'users/123'})['source'],
    ]
    assert all(p.metadata.language==expected for p in proposals)


def test_language_edit_and_unknown_limitations(initialized,tmp_path):
    source=sources.add(tmp_path/'cat',json.dumps({'schema_version':'1.0','metadata':{'type':'book','title':'A Synthetic Book','language':'English'}}).encode(),'synthetic')
    assert source['metadata']['language']=='en'
    for literal in ('eng','en-US','Uncatalogued Language'):
        source=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'metadata.language':literal}},source['revision'])
        assert source['metadata']['language']==('en' if literal=='eng' else literal)
    assert source['limitations']==languages.limitations(source['metadata'])
    assert source['limitations'][0]['field']=='language'
    output,warnings=bibliography.serialize([source])
    assert b'langid' not in output
    assert any(w['code']=='language_unrecognized' for w in warnings)
    source=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'metadata.language':'French'}},source['revision'])
    assert source['metadata']['language']=='fr' and not source['limitations']


def test_unknown_language_uses_missing_language_title_rule():
    value={'schema_version':'1.0','citation_key':'title','metadata':{'type':'book','title':'Éléments of Mathematics','language':'Uncatalogued Language'}}
    _,warnings=naming.normalize(value)
    assert any(w['code']=='title_language_unknown_or_nonenglish' for w in warnings)
    _,warnings=bibliography.serialize([value])
    assert any(w['code']=='language_unspecified' for w in warnings)
    value['metadata']['title']='Elements of Mathematics'
    _,warnings=naming.normalize(value)
    assert not any(w['code']=='title_language_unknown_or_nonenglish' for w in warnings)


def test_valid_wrong_language_is_preserved_and_warns():
    value={'schema_version':'1.0','citation_key':'mislabel','metadata':{'type':'book','title':'Statistics with Python','language':'bn'}}
    source=SourceCreate.model_validate(value)
    assert source.metadata.language=='bn'
    output,warnings=bibliography.serialize([source.canonical()])
    assert b'langid = {bangla}' in output
    assert any(w['code']=='title_language_review' for w in warnings)
    assert not languages.limitations(source.canonical()['metadata'])


def test_bibliographic_and_terminologic_aliases_share_tags():
    for left,right,expected in [('alb','sqi','sq'),('arm','hye','hy'),('cze','ces','cs'),('dut','nld','nl'),('wel','cym','cy')]:
        assert languages.normalize(left)==languages.normalize(right)==expected
    for value in ('en-US','zh-Hant-TW','de-CH','bn'):
        assert languages.normalize(value)==languages.tag(value)==value
