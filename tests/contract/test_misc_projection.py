"""Classic styles print misc facts in note; BibLaTeX keeps their structured fields."""

import json
from pathlib import Path

import pytest

from refs import bibliography
from refs.adapters import bibtex
from refs.models import SourceCreate

FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures/real-trial/minimized'


@pytest.mark.parametrize('kind', [
    'document', 'webpage', 'post-weblog', 'standard', 'speech', 'patent', 'software',
    'periodical', 'entry-encyclopedia', 'map', 'graphic', 'motion_picture', 'song',
    'broadcast', 'dataset', 'post', 'thesis',
])
def test_biblatex_publisher_genre_and_container_survive_round_trip(kind):
    source = SourceCreate.model_validate({
        'schema_version': '1.0', 'citation_key': 'captured-item',
        'metadata': {'type': kind, 'title': 'Captured Item', 'publisher': 'Holding and Hosting Institute',
                     'genre': 'Captured item', 'container-title': 'Host Database'},
    }).canonical()
    output, notices = bibliography.serialize([source], profile="biblatex-v1")
    publisher_field = 'school' if kind == 'thesis' else 'publisher'
    assert (publisher_field + ' = {{Holding and Hosting Institute}}').encode() in output
    assert b'type = {Captured item}' in output
    assert b'title = {Host Database}' in output
    assert b'Website:' not in output
    assert not any(notice['code'] == 'field_omitted' and notice['details']['mapping_id'] in
                   ['metadata.publisher', 'metadata.genre', 'metadata.container-title'] for notice in notices)
    restored = bibtex.parse(bibtex.partition(output)[0]['raw'])
    metadata = restored['source'].canonical()['metadata']
    assert metadata['publisher'] == 'Holding and Hosting Institute'
    assert metadata['genre'] == 'Captured item'
    assert metadata['container-title'] == 'Host Database'
    assert restored['limitations'] == []
    assert source['metadata']['type'] == kind


def test_five_minimized_pilot_exports_before_and_after():
    records = json.loads((FIXTURES / 'jhl-misc-projection.json').read_text())
    before = (FIXTURES / 'jhl-misc-before.bib').read_bytes()
    output, _ = bibliography.serialize(records, profile="biblatex-v1")
    before_entries = {entry['source'].citation_key: entry['source'].canonical()['metadata']
                      for block in bibtex.partition(before) if block['kind'] == 'entry'
                      for entry in [bibtex.parse(block['raw'])]}
    after_entries = {entry['source'].citation_key: entry['source'].canonical()['metadata']
                     for block in bibtex.partition(output) if block['kind'] == 'entry'
                     for entry in [bibtex.parse(block['raw'])]}
    assert list(sorted(after_entries)) == ['afhi-750', 'iwm-person', 'macr-5804', 'nara-aad', 'so363']
    for record in records:
        key = record['citation_key']
        original, changed = before_entries[key], after_entries[key]
        assert original['title'] == changed['title'] == record['metadata']['title']
        for field in ['publisher', 'genre', 'container-title']:
            if field not in record['metadata']:
                continue
            assert changed[field] == record['metadata'][field]
            if key != 'macr-5804':
                assert field not in original
        if record['metadata'].get('medium'):
            assert 'Medium: scanned copy' in changed['note']
    before_report = next(block['raw'] for block in bibtex.partition(before) if block['kind'] == 'entry' and b'{macr-5804,' in block['raw'])
    after_report = next(block['raw'] for block in bibtex.partition(output) if block['kind'] == 'entry' and b'{macr-5804,' in block['raw'])
    portable, _ = bibliography.serialize(records)
    portable_report = next(block['raw'] for block in bibtex.partition(portable) if block['kind'] == 'entry' and b'{macr-5804,' in block['raw'])
    assert before_report == portable_report
    assert b'institution = {457th Bomb Group Association}' in after_report
    assert b'type = {Missing Air Crew Report}' in after_report
    assert b'Website:' in before and b'Website:' not in output


@pytest.mark.parametrize('kind', ['document', 'report'])
def test_medium_stays_in_note_and_names_documented_consumer_limit(kind):
    source = SourceCreate.model_validate({
        'schema_version': '1.0', 'citation_key': 'scan',
        'metadata': {'type': kind, 'title': 'Captured Scan', 'medium': 'scanned copy'},
    }).canonical()
    output, notices = bibliography.serialize([source], profile="biblatex-v1")
    assert b'note = {Medium: scanned copy}' in output
    assert b'medium =' not in output
    notice, = [item for item in notices if item['code'] == 'medium_consumer_limit']
    assert notice['details']['class'] == 'documented_fallback'
    assert notice['details']['mapping_id'] == 'metadata.medium'
    assert 'Pandoc' in notice['message'] and 'IEEE' in notice['message']
    assert not any(item['code'] == 'field_in_note' for item in notices)


def test_nonmisc_field_applicability_is_unchanged():
    source = SourceCreate.model_validate({
        'schema_version': '1.0', 'citation_key': 'thesis',
        'metadata': {'type': 'thesis', 'title': 'Dissertation', 'genre': 'PhD thesis',
                     'publisher': 'Example University', 'container-title': 'Host Database'},
    }).canonical()
    output, notices = bibliography.serialize([source])
    assert output.startswith(b'@phdthesis{thesis,')
    assert b'school = {Example University}' in output
    assert b'type = {PhD thesis}' in output
    assert b'journal =' not in output and b'Website:' not in output
    assert any(item['code'] == 'field_omitted' and item['details']['mapping_id'] == 'metadata.container-title' for item in notices)


@pytest.mark.parametrize('kind', ['document', 'webpage', 'software', 'thesis', 'patent'])
def test_portable_misc_plain_facts_lead_note_without_synthetic_howpublished(kind):
    source = {'schema_version': '1.0', 'citation_key': 'misc-facts',
              'metadata': {'type': kind, 'title': 'Example', 'container-title': 'Host & Outlet',
                           'publisher': 'Research and Development', 'genre': 'Captured item',
                           'medium': 'scanned copy', 'version': '1.2', 'note': 'Existing note',
                           'issued': {'date-parts': [[2025, 5, 27]]}}}
    output, _ = bibliography.serialize([source])
    assert output.startswith(b'@misc{')
    assert rb'note = {Host \& Outlet; Research and Development; Captured item; scanned copy; 1.2; Existing note; Issued: 2025-05-27}' in output
    for field in [b'journal', b'publisher', b'type', b'medium', b'version', b'howpublished']:
        assert b'  ' + field + b' =' not in output
    assert source['metadata']['container-title'] == 'Host & Outlet'
