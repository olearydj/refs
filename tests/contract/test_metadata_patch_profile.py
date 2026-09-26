"""Accepted metadata has the same set, clear and bind-fill vocabulary as creation."""

import json
from pathlib import Path

import pytest

from refs import bibliography
from refs.results import RefError

FIXTURE = Path(__file__).parents[1]/'fixtures/real-trial/minimized/csl-bound-source-fill.json'


def test_csl_bound_source_field_fills_existing_record(initialized):
    result = initialized('import', '--format', 'csljson', '--input', FIXTURE)
    assert result['data']['counts'] == dict(applied=2, unchanged=0, conflict=0, invalid=0)
    first, second = result['data']['entries']
    assert first['source_id'] == second['source_id']
    assert second['binding']['filled'] == ['metadata.source']
    shown = initialized('show', first['source_id'])['data']
    assert shown['metadata']['source'] == 'PubMed Central'
    assert shown['revision'] == 2


@pytest.mark.parametrize(('field', 'replacement'), [
    ('source', 'Changed value'),
    ('archive_location', 'Changed value'),
    ('chair', [{'family':'Example', 'given':'Ada'}]),
])
def test_extended_metadata_can_be_set_and_cleared(initialized, tmp_path, field, replacement):
    imported = initialized('import', '--format', 'csljson', '--input', FIXTURE)['data']
    source = initialized('show', imported['entries'][0]['source_id'])['data']
    path = 'metadata.'+field
    patch = tmp_path/'patch.json'
    patch.write_text(json.dumps({'schema_version':'1.0', 'set':{path:replacement}}))
    changed = initialized('update', source['id'], '--patch', patch, '--if-revision', source['revision'])['data']
    assert changed['metadata'][field] == replacement
    patch.write_text(json.dumps({'schema_version':'1.0', 'clear':[path]}))
    cleared = initialized('update', source['id'], '--patch', patch, '--if-revision', changed['revision'])['data']
    shown = initialized('show', source['id'])['data']
    assert field not in cleared['metadata'] and field not in shown['metadata']
    assert shown['revision'] == source['revision']+2


@pytest.mark.parametrize('operation', ['set', 'clear'])
def test_unknown_metadata_path_refuses_without_changing_record(initialized, tmp_path, operation):
    source_id = initialized('import', '--format', 'csljson', '--input', FIXTURE)['data']['entries'][0]['source_id']
    before = initialized('show', source_id)['data']
    path = 'metadata.not-a-csl-variable'
    patch = tmp_path/'unknown.json'
    patch.write_text(json.dumps({'schema_version':'1.0', operation:{path:'Value'} if operation=='set' else [path]}))
    result = initialized('update', source_id, '--patch', patch, '--if-revision', before['revision'], expected=2)
    assert result['errors'][0]['code'] == 'invalid_patch'
    assert result['errors'][0]['message'] == 'Unknown metadata path'
    assert initialized('show', source_id)['data'] == before


def test_source_export_remains_unassessed_after_fill(initialized):
    source_id = initialized('import', '--format', 'csljson', '--input', FIXTURE)['data']['entries'][0]['source_id']
    source = initialized('show', source_id)['data']
    with pytest.raises(RefError) as error:
        bibliography.serialize([source])
    assert error.value.exit_code == 3
    assert error.value.issue['code'] == 'export_blocked'
    assert any(item['code']=='unassessed_mapping' and item['path']=='metadata.source'
               for item in error.value.issue['details']['entries'])
