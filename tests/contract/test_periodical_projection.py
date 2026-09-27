"""The JHL pilot's publication type, date and place survive portable output."""

import json
from pathlib import Path

import pytest

from refs import bibliography
from refs.adapters import bibtex
from refs.models import SourceCreate

FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures'


@pytest.mark.parametrize(('kind', 'subtype'), [
    ('article-newspaper', 'newspaper'), ('article-magazine', 'magazine'),
])
def test_periodical_type_date_page_and_place_round_trip(kind, subtype):
    payload = json.loads((FIXTURES / 'rendering/newspaper.json').read_text())
    payload['metadata']['type'] = kind
    payload['metadata']['note'] += '; Independent capture fact'
    source = SourceCreate.model_validate(payload)
    output, warnings = bibliography.serialize([source.canonical()])
    assert output.startswith(b'@article{kt-1942-10-30,')
    assert f'entrysubtype = {{{subtype}}}'.encode() in output
    assert b'address = {Kingsport, Tennessee}' in output
    assert b'Published in' not in output
    assert b'{I}ndependent capture fact' in output
    assert not any(w['code'] == 'field_omitted' and w['details']['mapping_id'] == 'metadata.publisher-place' for w in warnings)
    restored = bibtex.parse(bibtex.partition(output)[0]['raw'])
    metadata = restored['source'].canonical()['metadata']
    assert metadata['type'] == kind
    assert metadata['issued'] == {'date-parts': [[1942, 10]]}
    assert metadata['page'] == '1'
    assert metadata['publisher-place'] == 'Kingsport, Tennessee'
    assert restored['source'].native_type.namespace == 'bibtex'
    assert restored['source'].native_type.value == 'article'
    assert restored['limitations'] == []


def test_minimized_pilot_newspaper_before_and_after():
    raw = (FIXTURES / 'real-trial/minimized/jhl-newspaper-before.bib').read_bytes()
    before = bibtex.parse(bibtex.partition(raw)[0]['raw'])['source']
    assert before.citation_key == 'kt-1942-10-30'
    assert before.metadata.type == 'article-journal'
    assert before.metadata.publisher_place is None
    assert 'Published in Kingsport, Tennessee.' in before.metadata.note
    source = SourceCreate.model_validate_json((FIXTURES / 'rendering/newspaper.json').read_bytes())
    output, _ = bibliography.serialize([source.canonical()])
    after = bibtex.parse(bibtex.partition(output)[0]['raw'])['source']
    assert after.citation_key == before.citation_key
    assert after.metadata.title == before.metadata.title
    assert after.metadata.issued.date_parts == [[1942, 10]]
    assert before.metadata.issued.date_parts == [[1942, 10, 30]]
    assert after.metadata.page == before.metadata.page
    assert after.metadata.type == 'article-newspaper'
    assert after.metadata.publisher_place == 'Kingsport, Tennessee'
    assert b'Published in' not in output


@pytest.mark.parametrize('place', [None, 'Elsewhere'])
def test_place_note_is_kept_unless_the_same_place_is_projected(place):
    payload = json.loads((FIXTURES / 'rendering/newspaper.json').read_text())
    if place is None:
        payload['metadata'].pop('publisher-place')
    else:
        payload['metadata']['publisher-place'] = place
    output, _ = bibliography.serialize([SourceCreate.model_validate(payload).canonical()])
    assert b'{P}ublished in Kingsport, Tennessee.' in output


@pytest.mark.parametrize(('subtype', 'canonical'), [('Newspaper', 'article-newspaper'), ('MAGAZINE', 'article-magazine')])
def test_article_entrysubtype_names_are_case_insensitive(subtype, canonical):
    raw = f'@article{{example,title={{Recorded Work}},EntrySubtype={{{subtype}}}}}'.encode()
    source = bibtex.parse(raw)['source']
    assert source.metadata.type == canonical
    assert source.native_type.value == 'article'
