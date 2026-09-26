"""Owner-admitted types preserve their canonical identity through the portable profile."""

from typing import get_args

import pytest

from refs import bibliography, models, render
from refs.adapters import bibtex, csl, zotero

ADMITTED = ['periodical','entry-encyclopedia','map','graphic','motion_picture','song','broadcast','dataset','post']


@pytest.mark.parametrize('kind', ADMITTED)
def test_new_type_and_genre_survive_portable_round_trip(kind):
    source = models.SourceCreate.model_validate({'schema_version':'1.0','citation_key':'example',
        'metadata':{'type':kind,'title':'Recorded Work','genre':'Supplied genre','author':[{'family':'Example'}], 'issued':{'date-parts':[[2020]]}}})
    output, _ = bibliography.serialize([source.canonical()])
    assert output.startswith(b'@misc{example,')
    assert b'type = {Supplied genre}' in output
    assert b'cslgenre' not in output
    assert b'note =' not in output
    restored = bibtex.parse(bibtex.partition(output)[0]['raw'])['source']
    assert restored.metadata.type == kind
    assert restored.metadata.genre == 'Supplied genre'


def test_model_type_literal_has_exactly_the_registry_admissions():
    assert set(get_args(models.Metadata.model_fields['type'].annotation)) == set(models.REGISTRY['core_fields']['type']['schema']['enum'])


@pytest.mark.parametrize(('label','canonical'), [('proceedings','book'),('collection','book'),('booklet','document'),
    ('generic','document'),('presentation','speech'),('talk','speech'),('softwareversion','software'),('periodical','periodical'),
    ('inreference','entry-encyclopedia'),('map','map'),('image','graphic'),('movie','motion_picture'),('audio','song'),('broadcast','broadcast'),('dataset','dataset'),('post','post')])
def test_admitted_bib_spellings(label, canonical):
    source = bibtex.parse(f'@{label}{{example,title={{Recorded Work}},author={{Example, Ada}},year={{2020}}}}'.encode())['source']
    assert source.metadata.type == canonical
    assert source.native_type.value == label


@pytest.mark.parametrize(('label','canonical'), [('encyclopediaArticle','entry-encyclopedia'),('map','map'),('artwork','graphic'),
    ('film','motion_picture'),('videoRecording','motion_picture'),('audioRecording','song'),('podcast','song'),('radioBroadcast','broadcast'),('tvBroadcast','broadcast'),('dataset','dataset'),('forumPost','post')])
def test_admitted_zotero_spellings(label, canonical):
    item={'key':'EXAMPLE1','data':{'itemType':label,'title':'Recorded Work','date':'2020'}}
    source=zotero.parse(item, {'library_uri':'users/fixture'})['source']
    assert source.metadata.type == canonical
    assert source.metadata.title == 'Recorded Work'


def test_csl_pamphlet_maps_to_document():
    assert csl.parse(b'{"type":"pamphlet","title":"Recorded Work"}').metadata.type == 'document'


@pytest.mark.parametrize(('label','canonical'), [('proceedings','book'),('manual','document'),('phdthesis','thesis')])
def test_portable_native_label_refines_entry_type(label, canonical):
    source=bibtex.parse(f'@{label}{{example,title={{Recorded Work}},author={{Example, Ada}},year={{2020}}}}'.encode())['source']
    output,_=bibliography.serialize([source.canonical()])
    assert output.startswith(f'@{label}{{'.encode())
    restored=bibtex.parse(bibtex.partition(output)[0]['raw'])['source']
    assert restored.metadata.type == canonical
    assert render.type_label(source.canonical()) == f'{canonical} ({label})'


@pytest.mark.parametrize(('label','canonical'), [('constitution','legislation'),('jurisdiction','legal_case'),('bill','bill'),
    ('regulation','regulation'),('treaty','treaty'),('hearing','hearing'),('letter','personal_communication'),
    ('review','review-book'),('score','musical_score'),('performance','performance')])
def test_deferred_bib_types_refuse_by_csl_name(label, canonical):
    from refs.results import RefError
    with pytest.raises(RefError) as caught:
        bibtex.parse(f'@{label}{{example,title={{Recorded Work}}}}'.encode())
    assert caught.value.exit_code == 2
    assert caught.value.issue['code'] == 'invalid_bib_entry'
    assert caught.value.issue['details']['csl_type'] == canonical
    assert caught.value.issue['details']['recommendation'] == f'Admit CSL type {canonical} by adding a registry type row.'
    assert caught.value.issue['message'].endswith(caught.value.issue['details']['recommendation'])


@pytest.mark.parametrize('canonical', ['legislation','legal_case','bill','regulation','treaty','hearing',
    'personal_communication','review-book','musical_score','performance'])
def test_deferred_csl_types_refuse_by_name(canonical):
    import json

    from refs.results import RefError
    with pytest.raises(RefError) as caught:
        csl.parse(json.dumps({'type':canonical,'title':'Recorded Work'}).encode())
    assert caught.value.exit_code == 2
    assert caught.value.issue['code'] == 'invalid_record'
    assert caught.value.issue['details']['csl_type'] == canonical
    assert caught.value.issue['message'].endswith(f'Admit CSL type {canonical} by adding a registry type row.')


@pytest.mark.parametrize(('label','canonical'), [('statute','legislation'),('case','legal_case'),('bill','bill'),
    ('hearing','hearing'),('letter','personal_communication'),('email','personal_communication'),('instantMessage','personal_communication')])
def test_deferred_zotero_types_refuse_by_csl_name(label, canonical):
    from refs.results import RefError
    with pytest.raises(RefError) as caught:
        zotero.parse({'key':'EXAMPLE1','data':{'itemType':label,'title':'Recorded Work'}}, {'library_uri':'users/fixture'})
    assert caught.value.exit_code == 2
    assert caught.value.issue['code'] == 'unknown_zotero_type'
    assert caught.value.issue['details']['csl_type'] == canonical
    assert caught.value.issue['message'].endswith(f'Admit CSL type {canonical} by adding a registry type row.')


@pytest.mark.parametrize('label', ['nameonly','hardware'])
def test_unrepresented_bib_types_have_no_admission_recommendation(label):
    from refs.results import RefError
    with pytest.raises(RefError) as caught:
        bibtex.parse(f'@{label}{{example,title={{Recorded Work}}}}'.encode())
    assert caught.value.exit_code == 2
    assert caught.value.issue['code'] == 'invalid_bib_entry'
    assert caught.value.issue['message'] == 'Unsupported entry type'
    assert 'recommendation' not in caught.value.issue['details']


def test_misc_type_is_genre_with_or_without_canonical_type_marker():
    raw = b'@misc{example,title={Recorded Work},type={Audio podcast}}'
    unmarked = bibtex.parse(raw)
    assert unmarked['source'].metadata.type == 'document'
    assert unmarked['source'].metadata.genre == 'Audio podcast'
    assert unmarked['limitations'] == []
    marked = bibtex.parse(raw[:-1] + b',csltype={song}}')
    assert marked['source'].metadata.type == 'song'
    assert marked['source'].metadata.genre == 'Audio podcast'


def test_new_type_marker_follows_registry_portable_projection(monkeypatch):
    rows = [row | {'portable':'techreport'} if row['canonical']=='song' else row for row in models.REGISTRY['type_mappings']]
    monkeypatch.setitem(models.REGISTRY, 'type_mappings', rows)
    source = models.SourceCreate.model_validate({'schema_version':'1.0', 'citation_key':'example',
        'metadata':{'type':'song', 'title':'Recorded Work', 'genre':'Audio podcast'}})
    output, _ = bibliography.serialize([source.canonical()])
    assert output.startswith(b'@techreport{example,')
    assert b'type = {Audio podcast}' in output
    assert b'csltype' not in output
    assert b'cslgenre' not in output
