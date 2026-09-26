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
