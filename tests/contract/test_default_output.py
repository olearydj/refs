"""Installed commands use plain text unless the envelope is requested."""

import subprocess

import pytest
from conftest import REFS_COMMAND, isolated_env


def test_command_confirmations(initialized, tmp_path, reference_path):
    key = 'smith-2024-learningPython'
    env = isolated_env(tmp_path)

    def check(args, first):
        result = subprocess.run([*REFS_COMMAND, *map(str, args)], env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines()[0] == first
        assert '\x1b' not in result.stdout

    check(['init', '--library-root', tmp_path/'lib'], f"Unchanged: Initialized catalog at {tmp_path/'cat'} (library: {tmp_path/'lib'})")
    check(['add', '--format', 'refs', '--input', reference_path], f'Created {key}')
    check(['add', '--format', 'refs', '--input', reference_path], f'Already present: {key} (revision 1)')
    check(['project', 'create', 'paper'], 'Created project paper')
    check(['project', 'cite', 'paper', key], f'Cited {key} in paper')
    check(['project', 'show', 'paper'], 'Project: paper')
    check(['export', '--project', 'paper', '--output', tmp_path/'out.bib'], f"Wrote {tmp_path/'out.bib'} (1 entries, 0 warnings)")
    check(['update', key, '--if-revision', '1', '--set', 'metadata.volume="2"'], f'Updated {key} (revision 2)')
    check(['project', 'uncite', 'paper', key], f'Uncited {key} from paper')
    check(['key', 'set', key, '--key', 'smith-example', '--if-revision', '2', '--execute'], f'Renamed {key} to smith-example')
    check(['remove', 'smith-example', '--if-revision', '3', '--execute'], 'Removed smith-example')
    check(['reactivate', 'smith-example', '--if-revision', '4', '--execute'], 'Reactivated smith-example')
    result = subprocess.run([*REFS_COMMAND, 'show', 'missing'], env=env, capture_output=True, text=True)
    assert result.returncode == 3
    assert not result.stdout
    assert 'Use one exact source ID or citation key' in result.stderr


@pytest.mark.parametrize(('args', 'first'), [
    (['init'], 'Initialized catalog at '),
    (['paths'], 'Configuration\t'),
    (['schema', 'source-create'], '{'),
    (['add', '--format', 'refs'], 'Already present: '),
    (['show', 'smith-2024-learningPython'], 'Key\tsmith-2024-learningPython'),
    (['search', 'Python'], 'smith-2024-learningPython\t2024\tSmith\t'),
    (['list'], 'smith-2024-learningPython\t2024\tSmith\t'),
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
    result = subprocess.run([*REFS_COMMAND, *args], env=isolated_env(tmp_path), capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[0].startswith(first)


@pytest.mark.parametrize('command', ['import','resource add','resource unlink','resource check','open'])
def test_file_commands_first_line(initialized,tmp_path,reference_path,command):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    paths=[tmp_path/'one.pdf',tmp_path/'two.pdf']
    for path in paths:
        path.write_bytes(b'synthetic')
    first=initialized('resource','add',source['id'],'--path',paths[0])['data']
    bib=tmp_path/'input.bib'
    bib.write_text('@book{new,title={New Book}}')
    cases={
        'import':(['import','--input',str(bib)],f'Imported 1, unchanged 0, conflicts 0, invalid 0 from {bib}'),
        'resource add':(['resource','add',source['id'],'--path',str(paths[1])],f"Linked {paths[1]} to {source['citation_key']}"),
        'resource unlink':(['resource','unlink',first['id'],'--execute'],f"Unlinked {paths[0]} from {source['citation_key']}"),
        'resource check':(['resource','check'],f'linked with no loc (untouched)\t{paths[0]}\t'),
        'open':(['open',source['id']],'Choose a resource with --resource:'),
    }
    if command=='open':
        initialized('resource','add',source['id'],'--path',paths[1])
    args,expected=cases[command]
    result=subprocess.run([*REFS_COMMAND,*args],env=isolated_env(tmp_path),capture_output=True,text=True)
    assert result.returncode == 0,result.stderr
    assert result.stdout.splitlines()[0]==expected



def test_paths_has_three_readable_lines_before_init(tmp_path):
    result = subprocess.run([*REFS_COMMAND, 'paths'], env=isolated_env(tmp_path), capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.splitlines() == [f"Configuration\t{tmp_path/'config.toml'}", f"Catalog\t{tmp_path/'cat'}", 'Library\t(not configured)']
    assert not (tmp_path/'cat').exists()



def test_open_help_explains_effects(tmp_path):
    result=subprocess.run([*REFS_COMMAND,'open','--help'],env=isolated_env(tmp_path),capture_output=True,text=True)
    assert result.returncode==0
    text=' '.join(result.stdout.split())
    assert 'default application' in text and 'Never modifies the file' in text
    assert not (tmp_path/'cat').exists()
