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


@pytest.fixture
def multiple_targets(initialized, cli_env, cli_cwd, tmp_path):
    record = tmp_path / 'source.json'
    record.write_text(json.dumps({'schema_version': '1.0', 'citation_key': 'one',
                                 'metadata': {'type': 'book', 'title': 'Recorded Work'}}))
    initialized('add', '--format', 'refs', '--input', record)
    initialized('project', 'create', 'demo')
    initialized('project', 'cite', 'demo', 'one')
    (cli_cwd / '.git').mkdir()
    config = cli_cwd / '.refs.toml'
    config.write_text('project = "demo"\n[[export.targets]]\noutput = "references.json"\nprofile = "csl-json-v1"\n[[export.targets]]\noutput = "paper.bib"\nprofile = "portable-bibtex-v1"\n')

    def run(*args, expected=0, human=False):
        result = subprocess.run([sys.executable, '-m', 'refs', *([] if human else ['--json']), 'export', *map(str, args)],
                                env=cli_env, cwd=cli_cwd, capture_output=True, text=True)
        assert result.returncode == expected, result.stdout + result.stderr
        return result if human else json.loads(result.stdout)

    return run, config


def bindings(tmp_path):
    import sqlite3
    with sqlite3.connect(tmp_path / 'cat/catalog.sqlite') as db:
        return db.execute('SELECT destination, project_id, profile_fingerprint, baseline_digest, pending_digest FROM export_targets ORDER BY destination').fetchall()


def test_two_profiles_bind_and_repeat_as_current(multiple_targets, cli_cwd, tmp_path):
    import hashlib

    run, _ = multiple_targets
    first = run()
    assert first['status'] == 'ok'
    targets = first['data']['targets']
    assert [(t['profile'], t['outcome']) for t in targets] == [('csl-json-v1', 'written'), ('portable-bibtex-v1', 'written')]
    assert json.loads((cli_cwd / 'references.json').read_text()) == [{'id': 'one', 'title': 'Recorded Work', 'type': 'book'}]
    assert (cli_cwd / 'paper.bib').read_text().startswith('@book{one,')
    bound = bindings(tmp_path)
    assert len(bound) == 2 and bound[0][1] == bound[1][1]
    for t in targets:
        row = next(r for r in bound if r[0] == t['output'])
        assert row[2] == hashlib.sha256(t['profile'].encode()).hexdigest()
        assert row[3] == hashlib.sha256((cli_cwd / t['output']).read_bytes()).hexdigest()
        assert row[4] is None
    second = run()['data']['targets']
    assert [t['outcome'] for t in second] == ['current', 'current']
    assert bindings(tmp_path) == bound
    human = run(human=True)
    assert 'current' in human.stdout and 'references.json' in human.stdout and 'paper.bib' in human.stdout


def test_outside_edit_refuses_only_that_target_and_continues(multiple_targets, initialized, cli_cwd, tmp_path):
    run, _ = multiple_targets
    run()
    before = bindings(tmp_path)
    edited = cli_cwd / 'references.json'
    edited.write_text('outside edit\n')
    patch = tmp_path / 'patch.json'
    patch.write_text('{"schema_version":"1.0","set":{"metadata.publisher":"New Publisher"}}')
    initialized('update', 'one', '--patch', patch)
    result = run(expected=4)
    assert result['status'] == 'partial' and result['errors'][0]['code'] == 'export_partial'
    a, b = result['data']['targets']
    assert a['outcome'] == 'refused' and a['error']['code'] == 'outside_edit'
    assert b['outcome'] == 'written' and 'New Publisher' in (cli_cwd / 'paper.bib').read_text()
    assert edited.read_text() == 'outside edit\n'
    assert next(r for r in bindings(tmp_path) if r[0] == str(edited)) == next(r for r in before if r[0] == str(edited))
    human = run(expected=4, human=True)
    assert 'refused' in human.stdout and 'current' in human.stdout


def test_mixed_export_configuration_refuses_before_writes(multiple_targets, cli_cwd, tmp_path):
    run, config = multiple_targets
    config.write_text(config.read_text().replace('[[export.targets]]', '[export]\noutput = "single.bib"\n[[export.targets]]', 1))
    before = (tmp_path / 'cat/catalog.sqlite').read_bytes()
    result = run(expected=2)
    assert result['errors'][0]['code'] == 'invalid_config'
    assert 'not both' in result['errors'][0]['message']
    assert result['errors'][0]['path'] == str(config)
    assert (tmp_path / 'cat/catalog.sqlite').read_bytes() == before
    assert not (cli_cwd / 'references.json').exists() and not (cli_cwd / 'paper.bib').exists()


def test_explicit_profile_or_output_selects_one_target(multiple_targets, cli_cwd, tmp_path):
    run, _ = multiple_targets
    result = run('--profile', 'csl-json-v1')['data']
    assert 'targets' not in result and result['profile'] == 'csl-json-v1'
    assert not (cli_cwd / 'paper.bib').exists()
    result = run('--output', cli_cwd / 'references.json')['data']
    assert result['unchanged'] and result['profile'] == 'csl-json-v1'
    result = run('--output', tmp_path / 'chosen.json', '--profile', 'csl-json-v1')['data']
    assert result['output'] == str(tmp_path / 'chosen.json')
    assert not (cli_cwd / 'paper.bib').exists()


def test_list_preview_does_not_bind_or_write(multiple_targets, cli_cwd, tmp_path):
    run, _ = multiple_targets
    before = (tmp_path / 'cat/catalog.sqlite').read_bytes()
    assert [t['outcome'] for t in run('--dry-run')['data']['targets']] == ['preview', 'preview']
    assert (tmp_path / 'cat/catalog.sqlite').read_bytes() == before
    assert not bindings(tmp_path)
    assert not (cli_cwd / 'references.json').exists() and not (cli_cwd / 'paper.bib').exists()


@pytest.mark.parametrize('invalid', ['duplicate-output', 'empty-list', 'missing-profile', 'unsupported-profile'])
def test_invalid_target_list_fails_before_export(multiple_targets, cli_cwd, tmp_path, invalid):
    run, config = multiple_targets
    text = config.read_text()
    if invalid == 'duplicate-output':
        text = text.replace('paper.bib', './references.json')
    elif invalid == 'empty-list':
        text = 'project = "demo"\n[export]\ntargets = []\n'
    elif invalid == 'missing-profile':
        text = text.replace('profile = "csl-json-v1"\n', '')
    else:
        text = text.replace('csl-json-v1', 'unknown-v1')
    config.write_text(text)
    before = (tmp_path / 'cat/catalog.sqlite').read_bytes()
    assert run(expected=2)['errors'][0]['code'] == 'invalid_config'
    assert (tmp_path / 'cat/catalog.sqlite').read_bytes() == before
    assert not (cli_cwd / 'references.json').exists()


def test_profile_selector_refuses_ambiguous_list(multiple_targets, tmp_path):
    run, config = multiple_targets
    config.write_text(config.read_text().replace('portable-bibtex-v1', 'csl-json-v1'))
    result = run('--profile', 'csl-json-v1', expected=2)
    assert result['errors'][0]['code'] == 'invalid_invocation'
    assert 'exactly one' in result['errors'][0]['message']
    assert not bindings(tmp_path)


def test_project_list_replaces_user_single_target(multiple_targets, tmp_path, cli_cwd):
    run, _ = multiple_targets
    user = tmp_path / 'config.toml'
    user.write_text(user.read_text() + '\n[export]\noutput = "user.bib"\nprofile = "portable-bibtex-v1"\n')
    assert len(run()['data']['targets']) == 2
    assert not (tmp_path / 'user.bib').exists()
    assert (cli_cwd / 'references.json').exists()


def test_unavailable_target_directory_reports_failure_and_continues(multiple_targets, cli_cwd, tmp_path):
    run, config = multiple_targets
    config.write_text(config.read_text().replace('output = "references.json"', 'output = "absent/references.json"'))
    a, b = run(expected=4)['data']['targets']
    assert a['outcome'] == 'refused' and a['error']['code'] == 'storage_error' and a['exit_code'] == 5
    assert b['outcome'] == 'written'
    assert not (cli_cwd / 'absent').exists()
    assert len(bindings(tmp_path)) == 1
    assert (cli_cwd / 'paper.bib').read_text().startswith('@book{one,')
