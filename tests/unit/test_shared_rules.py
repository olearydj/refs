import json

from refs import bibliography, importing, sources
from refs.adapters import bibtex, zotero
from refs.catalog import connect
from refs.models import MONTHS, SourceCreate, person_name
from refs.results import notice


def test_month_names_and_person_join_are_shared():
    assert MONTHS[0] == ('jan', 'january')
    assert bibtex.month_number('January') == 1
    assert zotero.date_range('1–2 January 2024') == {'date-parts': [[2024, 1, 1], [2024, 1, 2]]}
    person = {'given': 'Alex', 'non-dropping-particle': 'van', 'family': 'Example'}
    assert person_name(person) == 'Alex van Example'
    record = {'schema_version': '1.0', 'citation_key': 'example2024', 'metadata': {'type': 'book', 'title': 'A Book', 'author': [person], 'issued': {'date-parts': [[2024, 1]]}}}
    output, _ = bibliography.serialize([record])
    assert b'month = jan' in output and b'van Example, Alex' in output


def test_generated_key_allocation_validates_and_suffixes_across_routes(initialized, tmp_path):
    catalog = tmp_path / 'cat'
    raw = json.dumps({'schema_version': '1.0', 'metadata': {'type': 'book', 'title': 'A Shared Book'}}).encode()
    first = sources.add(catalog, raw, 'first.json')
    item = {'key': 'ITEM0001', 'data': {'itemType': 'book', 'title': 'A Shared Book'}}
    entry = {'item': item, 'raw': json.dumps(item).encode(), 'locator': 'item.json', 'key': item['key']}
    with connect(catalog, write=True) as connection:
        imported = importing.apply_zotero(connection, entry, {'library_uri': 'users/123'}, 'fingerprint')
    second = sources.show(catalog, imported['source_id'])
    assert first['citation_key'] != second['citation_key']
    assert second['citation_key'].startswith(first['citation_key'])
    assert SourceCreate.valid_key(second['citation_key']) == second['citation_key']
    assert notice('example', 'Inspect this', path='item.json') == {'code': 'example', 'message': 'Inspect this', 'path': 'item.json', 'details': {}, 'retryable': False}
