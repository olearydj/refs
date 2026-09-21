"""Read-only documentation measurements for the 2026-09-21 checkpoint."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
FEATURE = ROOT / 'specs/001-academic-catalog'


def governing(path):
    p = Path(path)
    return (
        path in {'AGENTS.md', 'PROJECT_CONTEXT.md', '.specify/memory/constitution.md'}
        or (p.parent == Path('docs') and p.suffix == '.md')
        or (p.parent == Path('specs/001-academic-catalog') and p.suffix == '.md')
        or (p.parent == Path('specs/001-academic-catalog/contracts') and p.suffix in {'.md', '.json'})
    )


def rows(text):
    return [line.split('|')[1].strip() for line in text.splitlines()
            if line.startswith('| ') and not line.startswith('| ---')][1:]


def main():
    candidates = [ROOT / 'AGENTS.md', ROOT / 'PROJECT_CONTEXT.md', ROOT / '.specify/memory/constitution.md',
                  *sorted((ROOT / 'docs').glob('*.md')), *sorted(FEATURE.glob('*.md')),
                  *sorted((FEATURE / 'contracts').glob('*.md')), FEATURE / 'contracts/bibliographic-coverage.json']
    command_text = (FEATURE / 'contracts/cli.md').read_text().split('## Commands\n')[1].split('## Configuration')[0]
    commands = rows(command_text)
    tables = rows((FEATURE / 'data-model.md').read_text().split('## Authority')[0])
    expected_commands = ['init', 'paths', 'config show', 'schema NAME', 'add', 'show REF', 'update REF',
                         'search QUERY', 'list', 'key set REF', 'import', 'resource add REF',
                         'resource unlink RESOURCE', 'resource check', 'open REF', 'project create NAME',
                         'project show [PROJECT]', 'project cite PROJECT REF', 'project uncite PROJECT REF',
                         'export', 'remove REF', 'reactivate REF', 'backup']
    expected_tables = ['catalog_meta', 'sources', 'originals', 'origin_identities', 'resources', 'projects',
                       'project_sources', 'export_targets', 'imports', 'search projection']
    assert commands == expected_commands, commands
    assert tables == expected_tables, tables
    assert len(list((FEATURE / 'contracts').glob('*.md'))) == 4
    assert not (FEATURE / 'tasks.md').exists(), 'Task generation has not been authorized at this checkpoint'
    registry = FEATURE / 'contracts/bibliographic-coverage.json'
    json.loads(registry.read_text())
    original_registry = subprocess.check_output(['git', 'show', '8435765:specs/001-academic-catalog/contracts/bibliographic-coverage.json'], cwd=ROOT)
    assert original_registry == registry.read_bytes(), 'Semantic registry changed during surface trim'
    broken = []
    for path in [*candidates, *sorted((ROOT / 'docs/archive').glob('*.md')), *sorted((FEATURE / 'checklists').glob('*.md'))]:
        if path.suffix != '.md':
            continue
        for match in re.finditer(r'\]\(([^\s)]+)\)', path.read_text()):
            target = match[1].split('#')[0]
            if not target or '://' in target or target.startswith(('/', 'mailto:')):
                continue
            if not (path.parent / target).exists():
                broken.append((str(path.relative_to(ROOT)), target))
    assert not broken, broken
    baseline_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '8435765'], cwd=ROOT, text=True).splitlines()
    baseline_words = sum(len(subprocess.check_output(['git', 'show', f'8435765:{p}'], cwd=ROOT, text=True).split()) for p in baseline_paths if governing(p))
    output = json.dumps({
        'count_method': 'whitespace tokens; active docs/bootstrap/constitution/feature/contracts including JSON; archives, reviews, historical checklists and tooling excluded',
        'baseline_8435765_words_same_scope': baseline_words,
        'governing_words': sum(len(p.read_text().split()) for p in candidates),
        'governing_markdown_words': sum(len(p.read_text().split()) for p in candidates if p.suffix == '.md'),
        'spec_words': len((FEATURE / 'spec.md').read_text().split()),
        'top_level_commands': len({c.split()[0] for c in commands}),
        'invocations': len(commands), 'logical_tables': len(tables), 'contracts': 4,
        'registry_unchanged': True, 'local_links_pass': True, 'tasks_absent': True,
    }, indent=2)
    if len(sys.argv) == 3 and sys.argv[1] == "--output":
        Path(sys.argv[2]).write_text(output + "\n")
    else:
        print(output)


if __name__ == '__main__':
    main()
