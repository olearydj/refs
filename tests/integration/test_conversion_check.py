"""Consumer gates compare independent baselines and preserve real inputs."""

import hashlib
import json
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).parents[1] / 'fixtures/real-trial/conversion_check.py'
harness = runpy.run_path(str(HARNESS))


def digests(path):
    return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


@pytest.fixture
def trial(initialized, tmp_path):
    project = tmp_path / 'project'
    shutil.copytree(Path(__file__).parents[1] / 'fixtures/conversion-project', project)
    (project / '.git').mkdir()
    (project / '.git/private').write_text('not copied')
    (project / 'rendered.json').write_text('stale artifact must not be copied')
    (project / 'references.json').write_text('original export stays untouched')
    for key, title in [('same', 'Same Title'), ('changed', 'New Title')]:
        source = tmp_path / (key + '.json')
        source.write_text(json.dumps({'schema_version': '1.0', 'citation_key': key,
                                     'metadata': {'type': 'book', 'title': title}}))
        initialized('add', '--format', 'refs', '--input', source)
    initialized('project', 'create', 'synthetic')
    for key in ('same', 'changed'):
        initialized('project', 'cite', 'synthetic', key)
    register = tmp_path / 'converted/register.json'
    register.parent.mkdir()
    register.write_text(json.dumps({'schema_version': 1, 'projects': [{
        'name': 'synthetic', 'path': str(project), 'refs_project': 'synthetic',
        'targets': [{'path': 'references.json', 'profile': 'csl-json-v1'}],
        'consumers': [{'name': 'stub', 'command': [sys.executable, 'consumer.py'],
                       'artifact': 'rendered.json',
                       'extract': {'kind': 'json', 'path': ['sources'], 'key': 'id'},
                       'tools': {'python': {'command': [sys.executable, '--version'], 'recorded': 'test baseline'}}}],
    }]}))
    fixture = register.parent / 'synthetic/stub.txt'
    fixture.parent.mkdir()
    fixture.write_text(json.dumps({
        'same': '{"id": "same", "title": "Same Title"}',
        'changed': '{"id": "changed", "title": "Old Title"}',
        'gone': '{"id": "gone", "title": "Missing reference"}',
    }))
    return register, project, fixture


def invoke(tmp_path, register, *args):
    work = tmp_path / ('run-' + str(len(list(tmp_path.glob('run-*')))))
    result = subprocess.run([sys.executable, str(HARNESS), '--register', str(register),
                             '--catalog', str(tmp_path / 'cat'), '--work', str(work),
                             '--all', *args], text=True, capture_output=True)
    return result, work


def test_gate_classifies_entries_and_leaves_catalog_project_and_fixture_unchanged(trial, tmp_path):
    register, project, fixture = trial
    before = digests(tmp_path / 'cat'), digests(project), fixture.read_bytes()
    result, work = invoke(tmp_path, register)
    assert result.returncode == 1, result.stderr
    gate = json.loads(result.stdout)
    consumer = gate['projects'][0]['consumers'][0]
    assert consumer['entries'] == [
        {'entry': 'same', 'outcome': 'identical', 'before': '{"id": "same", "title": "Same Title"}', 'after': '{"id": "same", "title": "Same Title"}'},
        {'entry': 'changed', 'outcome': 'changed', 'before': '{"id": "changed", "title": "Old Title"}', 'after': '{"id": "changed", "title": "New Title"}'},
        {'entry': 'gone', 'outcome': 'missing', 'before': '{"id": "gone", "title": "Missing reference"}', 'after': None},
    ]
    assert before == (digests(tmp_path / 'cat'), digests(project), fixture.read_bytes())
    assert not (work / 'synthetic/project/.git').exists()
    assert '| gone | missing |' in (work / 'gate.md').read_text()
    assert (work / 'synthetic/catalog/refs.log').is_file()


def test_missing_fixture_exits_three_then_explicit_record_writes_current_extraction(trial, tmp_path):
    register, project, fixture = trial
    fixture.unlink()
    before = digests(tmp_path / 'cat'), digests(project), register.read_bytes()
    result, _ = invoke(tmp_path, register)
    assert result.returncode == 3, result.stderr
    assert json.loads(result.stdout)['exit_code'] == 3
    assert json.loads(result.stdout)['projects'][0]['consumers'][0]['fixture_missing']
    assert before == (digests(tmp_path / 'cat'), digests(project), register.read_bytes())
    assert not fixture.exists()
    recorded, _ = invoke(tmp_path, register, '--record')
    assert recorded.returncode == 3  # reports the absent accepted baseline even while recording
    assert json.loads(recorded.stdout)['exit_code'] == 3
    assert json.loads(recorded.stdout)['recorded']
    assert json.loads(fixture.read_text()) == {
        'changed': '{"id": "changed", "title": "New Title"}',
        'same': '{"id": "same", "title": "Same Title"}',
    }
    repeated, _ = invoke(tmp_path, register)
    assert repeated.returncode == 0, repeated.stderr
    assert {e['outcome'] for e in json.loads(repeated.stdout)['projects'][0]['consumers'][0]['entries']} == {'identical'}


@pytest.mark.parametrize('mutation', ['escape', 'command', 'extract', 'versions', 'duplicate'])
def test_register_refuses_malformed_entry(trial, mutation):
    register, _, _ = trial
    data = json.loads(register.read_text())
    project = data['projects'][0]
    if mutation == 'escape':
        project['targets'][0]['path'] = '../outside.json'
    elif mutation == 'command':
        project['consumers'][0]['command'] = 'python consumer.py'
    elif mutation == 'extract':
        project['consumers'][0]['extract']['kind'] = 'unknown'
    elif mutation == 'versions':
        del project['consumers'][0]['tools']
    else:
        data['projects'].append(project)
    register.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        harness['load_register'](register)


def test_pdf_entries_keep_changed_facts_and_join_continuations_across_pages():
    extraction = {'heading': 'Sources', 'entry_pattern': r'^\[(?P<entry>\d+)\]\s'}
    text = 'Sources ........ 12\nBody\nSources\n[1] A title.\n    Volume 2.\n\n 12\n\f    Pages 3–4.\n[2] Another title.\n 13\n'
    assert harness['pdf_entries'](text, extraction) == {'1': '[1] A title. Volume 2. Pages 3–4.', '2': '[2] Another title.'}
    with pytest.raises(ValueError, match='heading not found'):
        harness['pdf_entries']('No references', extraction)


@pytest.mark.slow
def test_real_jose_gate_matches_accepted_fixture(tmp_path, request):
    for tool in ('quarto', 'pdftotext', 'lualatex'):
        if not shutil.which(tool):
            if request.config._refs_require_tools:
                pytest.fail(f'Rendering consumer unavailable: {tool}')
            pytest.skip(f'Rendering consumer unavailable: {tool}')
    catalog = Path('/Volumes/Casa/refs/cat')
    publication = Path('/Volumes/Casa/pub/2026-jose-danvas')
    if not catalog.exists() or not publication.exists():
        pytest.skip('Owner real catalog/publication unavailable')
    # Other parallel CLI tests may append diagnostics to refs.log. The isolated
    # synthetic test above checks every file; here pin the real database bytes.
    before = (catalog / 'catalog.sqlite').read_bytes()
    result = subprocess.run([sys.executable, str(HARNESS), '--project', 'jose-danvas',
                             '--work', str(tmp_path / 'real')], text=True, capture_output=True)
    report = json.loads(result.stdout)['projects'][0]
    assert 'error' not in report, result.stdout + result.stderr
    consumers = report['consumers']
    assert result.returncode == (3 if any(c['fixture_missing'] for c in consumers) else 0)
    for consumer in consumers:
        assert len(consumer['entries']) == 11
        assert consumer['fixture_missing'] == (not Path(consumer['fixture']).exists())
        if not consumer['fixture_missing']:
            assert {e['outcome'] for e in consumer['entries']} == {'identical'}
    assert (catalog / 'catalog.sqlite').read_bytes() == before


def test_changed_entry_fails_without_recording(trial, tmp_path):
    register, _, fixture = trial
    baseline = json.loads(fixture.read_text())
    del baseline['gone']
    fixture.write_text(json.dumps(baseline))
    before = fixture.read_bytes()
    result, _ = invoke(tmp_path, register)
    assert result.returncode == 1, result.stderr
    assert json.loads(result.stdout)['exit_code'] == 1
    entries = json.loads(result.stdout)['projects'][0]['consumers'][0]['entries']
    assert [e['outcome'] for e in entries] == ['identical', 'changed']
    assert fixture.read_bytes() == before


def test_failed_consumer_cannot_reuse_stale_artifact_or_record(trial, tmp_path):
    register, _, fixture = trial
    data = json.loads(register.read_text())
    data['projects'][0]['consumers'][0]['command'] = [sys.executable, '-c', 'pass']
    register.write_text(json.dumps(data))
    before = fixture.read_bytes()
    result, work = invoke(tmp_path, register, '--record')
    assert result.returncode == 1
    assert 'rendered.json' in json.loads(result.stdout)['projects'][0]['error']
    assert not (work / 'synthetic/project/rendered.json').exists()
    assert fixture.read_bytes() == before


def test_explicit_input_copies_only_named_file_from_excluded_worktree(trial, tmp_path):
    register, project, _ = trial
    nested = project / 'worktrees/venue'
    nested.mkdir(parents=True)
    (nested / 'paper.md').write_text('A manuscript')
    (nested / '.git').write_text('private Git pointer')
    (nested / 'other.txt').write_text('unselected')
    data = json.loads(register.read_text())
    data['projects'][0]['inputs'] = ['worktrees/venue/paper.md']
    register.write_text(json.dumps(data))
    before = digests(project)
    result, work = invoke(tmp_path, register)
    assert result.returncode == 1  # existing synthetic missing reference
    assert 'error' not in json.loads(result.stdout)['projects'][0]
    copied = work / 'synthetic/project/worktrees/venue'
    assert [p.name for p in copied.iterdir()] == ['paper.md']
    assert (copied / 'paper.md').read_text() == 'A manuscript'
    assert digests(project) == before


@pytest.mark.parametrize('item', ['../outside.md', '/tmp/outside.md', 'worktrees/venue/.git', 'references.json'])
def test_register_refuses_unsafe_explicit_input(trial, item):
    register, _, _ = trial
    data = json.loads(register.read_text())
    data['projects'][0]['inputs'] = [item]
    register.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        harness['load_register'](register)


@pytest.mark.parametrize('mode', ['file-symlink', 'directory-symlink', 'missing'])
def test_explicit_input_refuses_symlinks_and_missing_files_without_changing_source(trial, tmp_path, mode):
    register, project, _ = trial
    nested = project / 'worktrees'
    nested.mkdir()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'paper.md').write_text('Do not copy')
    if mode == 'directory-symlink':
        (nested / 'venue').symlink_to(outside, target_is_directory=True)
    else:
        (nested / 'venue').mkdir()
        if mode == 'file-symlink':
            (nested / 'venue/paper.md').symlink_to(outside / 'paper.md')
    data = json.loads(register.read_text())
    data['projects'][0]['inputs'] = ['worktrees/venue/paper.md']
    register.write_text(json.dumps(data))
    before = digests(project), digests(outside)
    result, work = invoke(tmp_path, register)
    assert result.returncode == 1
    error = json.loads(result.stdout)['projects'][0]['error']
    assert ('existing file' if mode == 'missing' else 'symlink') in error
    assert not (work / 'synthetic/project').exists()
    assert (digests(project), digests(outside)) == before


@pytest.mark.parametrize('finding', ['identical', 'changed', 'missing', 'failed-consumer'])
def test_absent_fixture_does_not_hide_other_consumer_findings(trial, tmp_path, finding):
    register, project, fixture = trial
    data = json.loads(register.read_text())
    consumer = json.loads(json.dumps(data['projects'][0]['consumers'][0]))
    consumer['name'] = 'unaccepted'
    data['projects'][0]['consumers'].insert(0, consumer)
    baseline = {
        'same': '{"id": "same", "title": "Same Title"}',
        'changed': '{"id": "changed", "title": "New Title"}',
    }
    if finding == 'changed':
        baseline['changed'] = '{"id": "changed", "title": "Old Title"}'
    elif finding == 'missing':
        baseline['gone'] = '{"id": "gone", "title": "Missing reference"}'
    elif finding == 'failed-consumer':
        data['projects'][0]['consumers'][1]['command'] = [sys.executable, '-c', 'raise SystemExit(7)']
    register.write_text(json.dumps(data))
    fixture.write_text(json.dumps(baseline))
    before = digests(tmp_path / 'cat'), digests(project), digests(register.parent)
    result, work = invoke(tmp_path, register)
    expected = 3 if finding == 'identical' else 1
    assert result.returncode == expected, result.stderr
    gate = json.loads(result.stdout)
    assert gate['exit_code'] == expected
    assert json.loads((work / 'gate.json').read_text()) == gate
    checked = gate['projects'][0]
    if finding == 'failed-consumer':
        assert 'Command failed (7)' in checked['error']
    else:
        assert checked['consumers'][0]['fixture_missing']
        assert not checked['consumers'][1]['fixture_missing']
        assert finding in {e['outcome'] for e in checked['consumers'][1]['entries']}
    assert before == (digests(tmp_path / 'cat'), digests(project), digests(register.parent))
