"""Kind names assign and select record fields without another stored authority."""

import json
import sqlite3

import pytest

from refs import kinds
from refs.adapters import zotero
from refs.models import REGISTRY

DEFINITIONS = [('podcast','song','Audio podcast'), ('lecture','motion_picture','Lecture recording'),
               ('talk','speech','Conference presentation'), ('proceedings','book',None), ('dataset','dataset',None),
               ('repository','software','Source code repository')]


def payload(tmp_path, metadata, **fields):
    path = tmp_path/'entry.json'
    path.write_text(json.dumps({'schema_version':'1.0','metadata':{'title':'Recorded Work', **metadata}, **fields}))
    return path


@pytest.mark.parametrize(('name','canonical','genre'), DEFINITIONS)
def test_add_kind_sets_fields_and_derived_json(initialized, tmp_path, name, canonical, genre):
    path = payload(tmp_path, {}, citation_key='example')
    result = initialized('add','--format','refs','--input',path,'--kind',name)['data']
    assert result['kind'] == name
    assert result['metadata']['type'] == canonical
    assert result['metadata'].get('genre') == genre
    if name == 'proceedings':
        assert result['native_type']['value'] == 'proceedings'
    shown = initialized('show','example')['data']
    assert shown['kind'] == name
    assert shown['metadata'] == result['metadata']
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        stored = json.loads(connection.execute('SELECT details_json FROM sources').fetchone()[0])
    assert 'kind' not in stored


@pytest.mark.parametrize(('name','canonical','genre'), DEFINITIONS[:4])
def test_update_kind_sets_defining_fields_once(initialized, tmp_path, name, canonical, genre):
    initial = initialized('add','--format','refs','--input',payload(tmp_path, {'type':canonical},citation_key='example'))['data']
    changed = initialized('update','example','--kind',name,'--if-revision',initial['revision'])['data']
    assert changed['kind'] == name
    assert changed['metadata'].get('genre') == genre
    assert changed['revision'] == 2
    repeated = initialized('update','example','--kind',name,'--if-revision',2)['data']
    assert repeated['unchanged'] is True
    assert repeated['revision'] == 2


def test_kind_conflict_reports_both_values_and_does_not_write(initialized, tmp_path, human):
    initial = initialized('add','--format','refs','--input',payload(tmp_path, {'type':'song','genre':'Studio album'},citation_key='example'))['data']
    before=(tmp_path/'cat/catalog.sqlite').read_bytes()
    refused=initialized('update','example','--kind','podcast','--if-revision',1,expected=3)
    assert refused['errors'][0]['code'] == 'value_conflict'
    assert refused['errors'][0]['details']['conflicts'] == [{'path':'metadata.genre','current':'Studio album','incoming':'Audio podcast'}]
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before
    assert initialized('show','example')['data']['metadata'] == initial['metadata']
    text=human('update','example','--kind','podcast','--if-revision',1,expected=3)
    assert 'Studio album' in text and 'Audio podcast' in text


def test_kind_conflicting_type_refuses_add(initialized, tmp_path):
    before=(tmp_path/'cat/catalog.sqlite').read_bytes()
    refused=initialized('add','--format','refs','--input',payload(tmp_path, {'type':'book'}),'--kind','podcast',expected=3)
    assert refused['errors'][0]['code'] == 'value_conflict'
    assert refused['errors'][0]['details']['conflicts'] == [{'path':'metadata.type','current':'book','incoming':'song'}]
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before


def test_kind_list_and_search_filter_before_pagination(initialized, tmp_path):
    for key, metadata in [('album',{'type':'song','genre':'Studio album'}),('podcast',{'type':'song','genre':'Audio podcast'}),
                          ('document',{'type':'document'}),('lecture',{'type':'motion_picture','genre':'Lecture recording'})]:
        initialized('add','--format','refs','--input',payload(tmp_path,metadata,citation_key=key))
    selected=initialized('list','--kind','podcast','--limit',1)['data']
    assert selected['total'] == 1
    assert [item['citation_key'] for item in selected['items']] == ['podcast']
    assert selected['items'][0]['kind'] == 'podcast'
    searched=initialized('search','Recorded','--kind','lecture')['data']
    assert searched['total'] == 1
    assert [item['citation_key'] for item in searched['items']] == ['lecture']
    unassigned=initialized('list','--kind','unassigned')['data']
    assert unassigned['total'] == 1
    assert [item['citation_key'] for item in unassigned['items']] == ['album']
    assert unassigned['items'][0]['kind'] is None
    assert initialized('list','--kind','unassigned','--offset',1)['data']['items'] == []
    assert initialized('search','Recorded','--kind','unassigned')['data']['total'] == 1
    assert initialized('list','--kind','made-up',expected=2)['errors'][0]['code'] == 'invalid_invocation'


def test_repository_filter_leaves_plain_software_unassigned(initialized, tmp_path):
    for key, metadata in [('repository', {'type':'software','genre':'Source code repository'}),
                          ('software', {'type':'software'}), ('document', {'type':'document'})]:
        result = initialized('add','--format','refs','--input',payload(tmp_path,metadata,citation_key=key))
        if key == 'software':
            warning = next(item for item in result['warnings'] if item['code'] == 'kind_unassigned')
            assert warning['details']['kinds'] == ['repository']
            assert 'repository' in warning['message']
    selected = initialized('list','--kind','repository')['data']
    assert selected['total'] == 1
    assert [(item['citation_key'], item['kind']) for item in selected['items']] == [('repository', 'repository')]
    unassigned = initialized('list','--kind','unassigned')['data']
    assert unassigned['total'] == 1
    assert [(item['citation_key'], item['kind']) for item in unassigned['items']] == [('software', None)]
    assert 'genre' not in unassigned['items'][0]['metadata']


@pytest.mark.parametrize('route', ['bib','csljson','zotero'])
@pytest.mark.parametrize('canonical, kind, bib_type, zotero_type', [
    ('song', 'podcast', 'audio', 'audioRecording'),
    ('software', 'repository', 'software', 'computerProgram'),
])
def test_import_kind_warning_is_in_preview_and_saved_entry(initialized,tmp_path,route,zotero_fixture,canonical,kind,bib_type,zotero_type):
    if route == 'bib':
        path=tmp_path/'entry.bib'
        path.write_text('@' + bib_type + '{example,title={Recorded Work},author={Example, Ada},year={2020}}')
    elif route == 'csljson':
        path=tmp_path/'entry.csl.json'
        path.write_text(json.dumps([{'type':canonical,'title':'Recorded Work'}]))
    else:
        from conftest import extracted
        path=tmp_path/'bundle'
        extracted(zotero_fixture,path)
        for item_path in (path/'items').glob('*.json'):
            item_path.unlink()
        (path/'items/EXAMPLE1.json').write_text(json.dumps({'key':'EXAMPLE1','data':{'itemType':zotero_type,'title':'Recorded Work'}}))
    preview=initialized('import','--format',route,'--input',path,'--dry-run')['data']
    warning=preview['entries'][0]['warnings']
    assert any(item['code']=='kind_unassigned' and item['details']['kinds']==[kind] for item in warning)
    imported=initialized('import','--format',route,'--input',path)['data']
    saved=initialized('import','show',imported['import_id'])['data']['entries'][0]
    assert any(item['code']=='kind_unassigned' and item['details']['kinds']==[kind] for item in saved['warnings'])
    assert saved['kind'] is None
    assert saved['incoming']['metadata']['type'] == canonical
    assert 'genre' not in saved['incoming']['metadata']


def test_zotero_podcast_origin_assigns_kind_without_guessing_other_audio():
    item={'key':'EXAMPLE1','data':{'itemType':'podcast','title':'Recorded Work'}}
    podcast=zotero.parse(item,{'library_uri':'users/fixture'})['source'].canonical()
    assert podcast['metadata']['type']=='song'
    assert podcast['metadata']['genre']=='Audio podcast'
    assert kinds.identify(podcast)=='podcast'
    assert kinds.warnings(podcast)==[]
    item['data']['itemType']='audioRecording'
    audio=zotero.parse(item,{'library_uri':'users/fixture'})['source'].canonical()
    assert 'genre' not in audio['metadata']
    assert kinds.identify(audio) is None
    assert kinds.warnings(audio)[0]['details']['kinds']==['podcast']


def test_kind_defining_words_are_read_from_registry(monkeypatch):
    definitions=[dict(row) for row in REGISTRY['kinds']]
    definitions[0]=definitions[0] | {'fields':{'metadata.genre':'Changed podcast wording'}}
    monkeypatch.setitem(REGISTRY,'kinds',definitions)
    assigned=kinds.assign({'metadata':{'type':'song','title':'Recorded Work'}},'podcast')
    assert assigned['metadata']['genre']=='Changed podcast wording'
    assert kinds.identify(assigned)=='podcast'


def test_kinds_command_prints_definitions_without_opening_catalog(cli,human,tmp_path):
    before=(tmp_path/'cat/catalog.sqlite').read_bytes()  # human fixture initialized it
    result=cli('kinds')
    assert result['command']=='kinds'
    assert [(row['name'],row['type']) for row in result['data']['items']]==[(name,canonical) for name,canonical,_ in DEFINITIONS]
    assert 'podcast\tsong\tmetadata.genre=Audio podcast' in human('kinds')
    repository = next(row for row in result['data']['items'] if row['name'] == 'repository')
    assert repository['fields'] == {'metadata.genre': 'Source code repository'}
    assert repository.get('origins', {}) == {}
    assert 'repository\tsoftware\tmetadata.genre=Source code repository' in human('kinds')
    assert (tmp_path/'cat/catalog.sqlite').read_bytes()==before


@pytest.mark.parametrize('route', ['bib','csljson'])
def test_add_kind_works_on_the_other_capture_routes(initialized,tmp_path,route):
    path=tmp_path/'input'
    path.write_text('@audio{example,title={Recorded Work},author={Example, Ada},year={2020}}' if route=='bib' else '{"title":"Recorded Work"}')
    preview=initialized('add','--format',route,'--input',path,'--kind','podcast','--dry-run')['data']
    record=preview.get('record',preview)
    assert record['metadata']['type']=='song'
    assert record['metadata']['genre']=='Audio podcast'
    assert preview['kind']=='podcast'
    saved=initialized('add','--format',route,'--input',path,'--kind','podcast')['data']
    assert saved['kind']=='podcast'
    assert saved['metadata']['genre']=='Audio podcast'


def test_clearing_genre_removes_derived_kind(initialized,tmp_path):
    initial=initialized('add','--format','refs','--input',payload(tmp_path,{},citation_key='example'),'--kind','podcast')['data']
    patch=tmp_path/'patch.json'
    patch.write_text('{"schema_version":"1.0","clear":["metadata.genre"]}')
    changed=initialized('update','example','--patch',patch,'--if-revision',initial['revision'])['data']
    assert 'genre' not in changed['metadata']
    assert changed['kind'] is None
    assert initialized('list','--kind','unassigned')['data']['total']==1


def test_kinds_needs_no_catalog(cli_env,tmp_path):
    import subprocess
    import sys
    env=cli_env | {'REFS_CATALOG':str(tmp_path/'missing')}
    result=subprocess.run([sys.executable,'-m','refs','--json','--no-project-config','kinds'],env=env,capture_output=True,text=True,check=False)
    assert result.returncode==0, result.stdout+result.stderr
    assert json.loads(result.stdout)['data']['items'][0]['name']=='podcast'
    assert not (tmp_path/'missing').exists()
