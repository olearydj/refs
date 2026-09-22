import json
import os
import subprocess


def test_csl_input_and_four_schemas(initialized, tmp_path):
    raw = {'id': 'external-1', 'type': 'book', 'title': 'learning Python', 'language': 'en', 'author': [{'family': 'Smith'}], 'issued': {'date-parts': [[2024]]}}
    path = tmp_path / 'csl.json'
    path.write_text(json.dumps(raw))
    result = initialized('add', '--format', 'csljson', '--input', path)['data']
    assert result['id'] != 'external-1'
    assert result['metadata']['title'] == 'Learning Python'
    assert result['provenance'][0]['source_identity']['item_key'] == 'external-1'
    for name in ['source-create', 'source-patch', 'source-record', 'result']:
        schema = initialized('schema', name)['data']
        assert schema['type'] == 'object'
        assert schema['additionalProperties'] is False
    initialized('schema', 'no-such-schema', expected=2)


def test_readable_output_and_json_others(initialized, tmp_path, reference_path):
    initialized('add', '--format', 'refs', '--input', reference_path)
    env = dict(os.environ, REFS_CONFIG=str(tmp_path/'config.toml'), REFS_CATALOG=str(tmp_path/'cat'))
    for args in [('show', 'smith-2024-learningPython'), ('search', 'Python'), ('list',)]:
        result = subprocess.run(['refs', *args], env=env, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert 'smith-2024-learningPython' in result.stdout
        assert 'Alex Smith' in result.stdout
        assert 'Alex  Smith' not in result.stdout
        if args[0] == 'show':
            for hidden in ('schema_version', 'created_at', 'updated_at', 'corrected_fields', 'key_provenance', 'originals', '{', '}'):
                assert hidden not in result.stdout
            assert 'Container: Journal of Synthetic Examples' in result.stdout
            assert 'Files: (none)' in result.stdout
            assert 'Projects: (none)' in result.stdout
        assert '2024' in result.stdout
        assert not result.stdout.startswith('{')
        assert '\x1b' not in result.stdout
    result = subprocess.run(['refs', 'paths'], env=env, text=True, capture_output=True)
    assert json.loads(result.stdout)['schema_version'] == '1.0'
