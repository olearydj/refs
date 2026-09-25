import json
import subprocess

from conftest import REFS_COMMAND, isolated_env

from refs.models import Result, SourceRecord


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


def test_real_show_and_envelope_validate_against_published_models(initialized, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    envelope = initialized('show', source['id'])
    validated = SourceRecord.model_validate(envelope['data'])
    assert validated.id == source['id'] and validated.citation_key == source['citation_key']
    result = Result.model_validate(envelope)
    assert result.command == 'show' and result.status == 'ok'


def test_readable_output_and_json_others(initialized, tmp_path, reference_path):
    initialized('add', '--format', 'refs', '--input', reference_path)
    env = isolated_env(tmp_path)
    for args in [('show', 'smith-2024-learningPython'), ('search', 'Python'), ('list',)]:
        result = subprocess.run([*REFS_COMMAND, *args], env=env, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert 'smith-2024-learningPython' in result.stdout
        assert ('Alex Smith' if args[0] == 'show' else 'Smith') in result.stdout
        assert 'Alex  Smith' not in result.stdout
        if args[0] == 'show':
            for hidden in ('schema_version', 'created_at', 'updated_at', 'corrected_fields', 'key_provenance', 'originals', '{', '}'):
                assert hidden not in result.stdout
            assert 'container-title\tJournal of Synthetic Examples' in result.stdout
            assert 'Files\t(none)' in result.stdout
            assert 'Projects\t(none)' in result.stdout
        assert '2024' in result.stdout
        assert not result.stdout.startswith('{')
        assert '\x1b' not in result.stdout
    result = subprocess.run([*REFS_COMMAND, 'paths'], env=env, text=True, capture_output=True)
    assert result.stdout.splitlines()[0] == f"Configuration\t{tmp_path/'config.toml'}"
