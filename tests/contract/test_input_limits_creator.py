"""Unsupported creator spellings use the existing title template and retain the supplied names."""

import json
import sqlite3

import pytest
from conftest import extracted

from refs import importing, naming, sources
from refs.adapters import zotero
from refs.results import RefError


@pytest.mark.parametrize(('key_author','expected'), [(None,'recordedWork-2024'), ('wang','wang-2024-recordedWork')])
def test_chinese_creator_through_zotero_uses_title_or_key_author(initialized,tmp_path,zotero_fixture,monkeypatch,key_author,expected):
    directory = tmp_path/'input'
    extracted(zotero_fixture,directory)
    for path in (directory/'items').glob('*.json'):
        path.unlink()
    item = {'key':'EXAMPLE1','data':{'itemType':'book','title':'Recorded Work','date':'2024',
            'creators':[{'creatorType':'author','lastName':'王','firstName':'小明'}]}}
    (directory/'items/EXAMPLE1.json').write_text(json.dumps(item,ensure_ascii=False))
    if key_author:
        parse = zotero.parse
        def supplied_override(*args):
            proposal = parse(*args)
            proposal['source'].key_author = key_author
            return proposal
        monkeypatch.setattr(zotero,'parse',supplied_override)
    result = importing.run_zotero(tmp_path/'cat',directory)
    assert result['counts'] == {'applied':1,'unchanged':0,'conflict':0,'invalid':0}
    entry = result['entries'][0]
    assert entry['citation_key'] == expected
    notices = [warning for warning in entry['warnings'] if warning['code']=='creator_token_fallback']
    assert bool(notices) == (key_author is None)
    if notices:
        assert 'Creator gave no usable token' in notices[0]['message']
        assert 'key_author can be supplied' in notices[0]['message']
        assert notices[0]['details']['creator']=='王'
    stored = sources.show(tmp_path/'cat',expected)
    assert stored['metadata']['author'] == [{'family':'王','given':'小明'}]
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        payload = json.loads(connection.execute('SELECT payload_json FROM import_entries').fetchone()[0])
    assert [warning for warning in payload['warnings'] if warning['code']=='creator_token_fallback'] == notices


def test_no_usable_creator_or_title_keeps_citation_key_required(initialized,tmp_path):
    path = tmp_path/'input.json'
    path.write_text(json.dumps({'schema_version':'1.0','metadata':{'type':'book','title':'and of','author':[{'family':'王'}]}}))
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    result = initialized('add','--format','refs','--input',path,expected=2)
    assert result['errors'][0]['code']=='citation_key_required'
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before


def test_supplied_bib_key_does_not_need_a_creator_token(initialized,tmp_path):
    path = tmp_path/'input.bib'
    path.write_text('@book{assigned,title={Recorded Work},author={王, 小明},year={2024}}')
    first = initialized('add','--format','bib','--input',path)
    assert first['data']['citation_key']=='assigned'
    assert not any(warning['code']=='creator_token_fallback' for warning in first['warnings'])
    again = initialized('add','--format','bib','--input',path)
    assert again['data']['id']==first['data']['id']
    assert again['data']['outcome']=='already_present'
    assert again['data']['revision']==first['data']['revision']
    assert not any(warning['code']=='creator_token_fallback' for warning in again['warnings'])


@pytest.mark.parametrize('family',['王','***','Smith☃'])
def test_unusable_creator_uses_configured_without_creator_template(family):
    warnings = []
    record = {'metadata':{'title':'Recorded Work','author':[{'family':family}],'issued':{'date-parts':[[2024]]}}}
    assert naming.key(record,{'keys':{'without_creator':'{year}:{title}'}},warnings=warnings)=='2024:recordedWork'
    assert [warning['code'] for warning in warnings]==['creator_token_fallback']
    with pytest.raises(RefError) as caught:
        naming.key(record | {'key_author':family})
    assert caught.value.issue['code']=='key_author_required'
