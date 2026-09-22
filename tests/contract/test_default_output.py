"""Installed commands use plain text unless the envelope is requested."""

import os
import subprocess

import pytest


def test_command_confirmations(initialized, tmp_path, reference_path):
    key = 'smith-2024-learningPython'
    env = dict(os.environ, REFS_CONFIG=str(tmp_path/'config.toml'), REFS_CATALOG=str(tmp_path/'cat'))

    def check(args, first):
        result = subprocess.run(['refs', *map(str, args)], env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines()[0] == first
        assert '\x1b' not in result.stdout

    check(['init', '--library-root', tmp_path/'lib'], f"Unchanged: Initialized catalog at {tmp_path/'cat'} (library: {tmp_path/'lib'})")
    check(['add', '--format', 'refs', '--input', reference_path], f'Created {key}')
    check(['add', '--format', 'refs', '--input', reference_path], f'Already present: {key} (revision 1)')
    check(['project', 'create', 'paper'], 'Created project paper')
    check(['project', 'cite', 'paper', key], f'Cited {key} in paper')
    check(['project', 'show', 'paper'], 'Project: paper')
    exported = initialized('export', '--project', 'paper', '--output', tmp_path/'previous.bib')['data']
    check(['export', '--project', 'paper', '--output', tmp_path/'out.bib'], f"Wrote {tmp_path/'out.bib'} (1 entries, {len(exported['warnings'])} warnings)")
    check(['update', key, '--if-revision', '1', '--set', 'metadata.volume="2"'], f'Updated {key} (revision 2)')
    check(['project', 'uncite', 'paper', key], f'Uncited {key} from paper')
    check(['key', 'set', key, '--key', 'smith-example', '--if-revision', '2', '--execute'], f'Renamed {key} to smith-example')
    check(['remove', 'smith-example', '--if-revision', '3', '--execute'], 'Removed smith-example')
    check(['reactivate', 'smith-example', '--if-revision', '4', '--execute'], 'Reactivated smith-example')
    result = subprocess.run(['refs', 'show', 'missing'], env=env, capture_output=True, text=True)
    assert result.returncode == 3
    assert not result.stdout
    assert 'Use one exact source ID or citation key' in result.stderr


@pytest.mark.parametrize(('args', 'first'), [
    (['init'], 'Initialized catalog at '),
    (['paths'], '{'),
    (['schema', 'source-create'], '{'),
    (['add', '--format', 'refs'], 'Already present: '),
    (['show', 'smith-2024-learningPython'], 'Key: smith-2024-learningPython'),
    (['search', 'Python'], 'smith-2024-learningPython | Alex Smith | 2024 | '),
    (['list'], 'smith-2024-learningPython | Alex Smith | 2024 | '),
    (['project', 'create', 'other'], 'Created project other'),
    (['project', 'show'], 'paper'),
    (['project', 'cite', 'paper', 'smith-2024-learningPython'], 'Cited smith-2024-learningPython in paper'),
    (['project', 'uncite', 'paper', 'smith-2024-learningPython'], 'Unchanged: Uncited smith-2024-learningPython from paper'),
    (['update', 'smith-2024-learningPython', '--if-revision', '1', '--set', 'metadata.volume="3"'], 'Updated smith-2024-learningPython (revision 2)'),
    (['key', 'set', 'smith-2024-learningPython', '--key', 'new-key', '--if-revision', '1', '--execute'], 'Renamed smith-2024-learningPython to new-key'),
    (['remove', 'smith-2024-learningPython', '--if-revision', '1', '--execute'], 'Removed smith-2024-learningPython'),
    (['reactivate', 'smith-2024-learningPython', '--if-revision', '1', '--execute'], 'Unchanged: Reactivated smith-2024-learningPython'),
    (['export', '--project', 'paper'], 'Wrote '),
])
def test_each_command_first_line(initialized, tmp_path, reference_path, args, first):
    initialized('add', '--format', 'refs', '--input', reference_path)
    initialized('project', 'create', 'paper')
    args = list(args)
    if args[0] == 'init':
        args += ['--library-root', str(tmp_path/'lib')]
        first = 'Unchanged: ' + first
    if args[0] == 'add':
        args += ['--input', str(reference_path)]
    if args[0] == 'export':
        args += ['--output', str(tmp_path/'out.bib')]
    result = subprocess.run(['refs', *args], env=dict(os.environ, REFS_CONFIG=str(tmp_path/'config.toml'), REFS_CATALOG=str(tmp_path/'cat')), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith(first)
