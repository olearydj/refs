"""Refs JSON recommends admission only for known deferred CSL types."""

import json

import pytest


@pytest.mark.parametrize('kind', ['personal_communication', 'invented-type'])
def test_refs_type_refusal_recommends_only_known_deferred_types(initialized, tmp_path, kind):
    path = tmp_path / 'record.json'
    path.write_text(json.dumps({
        'schema_version': '1.0',
        'citation_key': 'family-recollection',
        'metadata': {'type': kind, 'title': 'Family recollection'},
    }))
    database = tmp_path / 'cat/catalog.sqlite'
    before = database.read_bytes()
    result = initialized('add', '--format', 'refs', '--input', path, expected=2)
    assert result['command'] == 'add'
    error = result['errors'][0]
    assert error['code'] == 'invalid_record'
    assert any(issue['msg'] == 'Value error, Unsupported source type' for issue in error['details']['issues'])
    if kind == 'personal_communication':
        assert error['details']['csl_type'] == 'personal_communication'
        recommendation = 'Admit CSL type personal_communication by adding a registry type row.'
        assert error['details']['recommendation'] == recommendation
        assert error['message'].endswith(recommendation)
    else:
        assert 'csl_type' not in error['details']
        assert 'recommendation' not in error['details']
        assert error['message'] == 'Input does not match the supported record profile'
    assert database.read_bytes() == before
