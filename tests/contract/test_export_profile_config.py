"""Both documented export profiles work through user and project defaults."""

import json
import subprocess
import sys

import pytest


@pytest.mark.parametrize('profile', ['portable-bibtex-v1', 'csl-json-v1'])
@pytest.mark.parametrize('layer', ['user', 'project'])
def test_export_profile_defaults_and_invocation_override(initialized, cli_env, cli_cwd, tmp_path, profile, layer):
    record = tmp_path / 'source.json'
    record.write_text(json.dumps({'schema_version': '1.0', 'citation_key': 'one',
                                 'metadata': {'type': 'book', 'title': 'Recorded Work'}}))
    initialized('add', '--format', 'refs', '--input', record)
    initialized('project', 'create', 'demo')
    initialized('project', 'cite', 'demo', 'one')
    export_settings = f'[export]\nprofile = "{profile}"\noutput = "references"\n'
    settings = 'project = "demo"\n' + export_settings
    if layer == 'user':
        path = tmp_path / 'config.toml'
        path.write_text('project = "demo"\n' + path.read_text() + '\n' + export_settings)
    else:
        (cli_cwd / '.git').mkdir()
        path = cli_cwd / '.refs.toml'
        path.write_text(settings)

    def configured(*args):
        result = subprocess.run([sys.executable, '-m', 'refs', '--json', *map(str, args)],
                                env=cli_env, cwd=cli_cwd, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stderr == ''
        return json.loads(result.stdout)

    result = configured('export')['data']
    assert result['profile'] == profile and result['count'] == 1
    output = path.parent / 'references'
    assert result['output'] == str(output)
    if profile == 'csl-json-v1':
        assert json.loads(output.read_bytes()) == [{'id': 'one', 'title': 'Recorded Work', 'type': 'book'}]
    else:
        assert output.read_bytes().startswith(b'@book{one,')
    selected = configured('config', 'show')['data']
    assert selected['values']['export.profile'] == profile
    assert selected['origins']['export.profile'] == str(path)
    other = 'csl-json-v1' if profile == 'portable-bibtex-v1' else 'portable-bibtex-v1'
    override = configured('export', '--profile', other, '--output', tmp_path / 'override')['data']
    assert override['profile'] == other and override['count'] == 1
    assert output.read_bytes().startswith(b'[' if profile == 'csl-json-v1' else b'@book{')
