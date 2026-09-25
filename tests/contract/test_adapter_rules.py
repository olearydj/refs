import json

from conftest import extracted

from refs.adapters import bibtex, zotero
from refs.models import portable_url


def test_alias_conflicts_share_one_code_across_import_routes(initialized, tmp_path, zotero_fixture):
    bib = tmp_path / 'alias.bib'
    bib.write_text('@article{alias,title={A Study},journal={First Journal},journaltitle={Second Journal}}')
    bib_result = initialized('import', '--input', bib, expected=4)
    assert bib_result['data']['entries'][0]['code'] == 'alias_conflict'
    assert bib_result['data']['entries'][0]['status'] == 'conflict'

    folder = tmp_path / 'extracted'
    extracted(zotero_fixture, folder)
    item = folder / 'items/ITEM0001.json'
    value = json.loads(item.read_text())
    value['data']['extra'] += '\nDOI: 10.5555/different'
    item.write_text(json.dumps(value))
    zotero_result = initialized('import', '--format', 'zotero', '--input', folder, expected=4)
    assert any(entry.get('code') == 'alias_conflict' and entry['status'] == 'conflict' for entry in zotero_result['data']['entries'])

    csl_input = tmp_path / 'alias.json'
    csl_input.write_text(json.dumps({'type': 'book', 'title': 'A Study', 'shortTitle': 'One', 'title-short': 'Two'}))
    csl_result = initialized('add', '--format', 'csljson', '--input', csl_input, expected=3)
    assert csl_result['errors'][0]['code'] == 'alias_conflict'


def test_csl_dropped_fields_remain_visible_as_limitations(initialized, tmp_path):
    path = tmp_path / 'source.json'
    path.write_text(json.dumps({'type': 'book', 'title': 'A Study', 'unmappedField': 'evidence', 'URL': 'file:///local'}))
    created = initialized('add', '--format', 'csljson', '--input', path)['data']
    shown = initialized('show', created['id'])['data']
    assert {'unmappedField', 'URL'} <= {item['field'] for item in created['limitations']}
    assert shown['limitations'] == created['limitations']
    assert 'URL' not in shown['metadata']
    assert portable_url('https://example.org/paper') and not portable_url('file:///local')
    assert any(item['field'] == 'url' for item in bibtex.parse(b'@book{x,title={A Study},url={file:///local}}')['limitations'])
    assert any(item['field'] == 'url' for item in zotero.parse({'key': 'ITEM0001', 'data': {'itemType': 'book', 'title': 'A Study', 'url': 'file:///local'}}, {'library_uri': 'users/123'})['limitations'])
