"""Render converted projects in scratch; never export against the owner's catalog.

--record is an explicit assertion that the owner accepted the gate. Normal runs
never change fixtures. PDF entries use printed labels (numbers or author/year),
not inferred citation keys; JSON entries use the configured identity field.
"""

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REGISTER = Path(__file__).with_name('converted') / 'register.json'
IGNORED = {'.git', '.quarto', '.venv', '__pycache__', 'node_modules', 'worktrees'}


def relative(value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or '..' in Path(value).parts or value == '.':
        raise ValueError(f'Expected a relative path within the project: {value!r}')
    return value


def command(value):
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x for x in value):
        raise ValueError('Command must be a nonempty argv array')
    return value


def load_register(path):
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get('schema_version') != 1 or not isinstance(data.get('projects'), list) or not data['projects']:
        raise ValueError('Expected register schema_version 1 and projects')
    seen = set()
    for project in data['projects']:
        try:
            name = project['name']
            if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name) or name in seen:
                raise ValueError('Project names must be unique slugs')
            seen.add(name)
            if not Path(project['path']).is_absolute() or not project['refs_project']:
                raise ValueError('Expected absolute project path and refs project name')
            if not project['targets'] or not project['consumers']:
                raise ValueError('Each project needs targets and consumers')
            paths, consumers = set(), set()
            for target in project['targets']:
                dest = relative(target['path'])
                if dest in paths or target['profile'] not in ('csl-json-v1', 'portable-bibtex-v1', 'biblatex-v1'):
                    raise ValueError('Duplicate target or unsupported profile')
                paths.add(dest)
            for consumer in project['consumers']:
                name = consumer['name']
                if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', name) or name in consumers:
                    raise ValueError('Consumer names must be unique slugs')
                consumers.add(name)
                command(consumer['command'])
                relative(consumer['artifact'])
                ex = consumer['extract']
                if ex['kind'] == 'pdf':
                    if not ex['heading'] or 'entry' not in re.compile(ex['entry_pattern']).groupindex:
                        raise ValueError('PDF extraction needs heading and named entry group')
                elif ex['kind'] == 'json':
                    if not isinstance(ex['path'], list) or any(not isinstance(k, str) for k in ex['path']) or not isinstance(ex['key'], str) or not ex['key']:
                        raise ValueError('JSON extraction needs a path array and key field')
                else:
                    raise ValueError('Extraction kind must be pdf or json')
                if not consumer['tools']:
                    raise ValueError('Fixture tool versions are required')
                for tool in consumer['tools'].values():
                    command(tool['command'])
                    if not isinstance(tool['recorded'], str) or not tool['recorded']:
                        raise ValueError('Fixture tool version is required')
            inputs = project.get('inputs', [])
            if not isinstance(inputs, list) or len(set(inputs)) != len(inputs):
                raise ValueError('Inputs must be a list of distinct relative files')
            for item in inputs:
                relative(item)
                if '.git' in Path(item).parts or item in paths or item in {c['artifact'] for c in project['consumers']}:
                    raise ValueError('Inputs cannot include Git internals, export targets or artifacts')
            for exclude in project.get('exclude', []):
                relative(exclude)
        except (KeyError, TypeError, AttributeError, re.error) as exc:
            raise ValueError(f'Malformed register entry: {project!r}') from exc
    return data


def run_command(argv, cwd):
    result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=600)
    if result.returncode:
        raise ValueError(f'Command failed ({result.returncode}): {argv}\n{result.stdout}\n{result.stderr}')
    return result.stdout or result.stderr


def pdf_entries(text, extraction):
    lines = text.replace('\f', '\n').splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == extraction['heading']]
    if not starts:
        raise ValueError(f"PDF heading not found: {extraction['heading']}")
    pattern = re.compile(extraction['entry_pattern'])
    entries, entry, parts = {}, None, []
    for line in lines[starts[-1] + 1:]:
        if not line.strip() or re.fullmatch(r'\s*\d+\s*', line):
            continue  # blank lines and page-number footers, not reference content
        match = pattern.match(line)
        if match:
            if entry is not None:
                entries[entry] = ' '.join(parts)
            entry = match['entry']
            if entry in entries:
                raise ValueError(f'Duplicate PDF entry label: {entry}')
            parts = []
        if entry is None:
            raise ValueError(f'Unrecognized reference text: {line}')
        parts.append(' '.join(line.split()))
    if entry is not None:
        entries[entry] = ' '.join(parts)
    if not entries:
        raise ValueError('No PDF references extracted')
    return entries


def extract(artifact, extraction):
    if extraction['kind'] == 'pdf':
        return pdf_entries(run_command(['pdftotext', '-layout', str(artifact), '-'], artifact.parent), extraction)
    value = json.loads(artifact.read_text())
    for key in extraction['path']:
        value = value[key]
    if not isinstance(value, list):
        raise ValueError('JSON source list must be an array')
    entries = {}
    for item in value:
        key = item[extraction['key']]
        if not isinstance(key, str) or not key or key in entries:
            raise ValueError('JSON entry keys must be unique nonempty strings')
        entries[key] = json.dumps(item, ensure_ascii=False, sort_keys=True)
    if not entries:
        raise ValueError('No JSON references extracted')
    return entries


def compare(before, after):
    return [dict(entry=key, outcome='missing' if key not in after else 'identical' if key in before and before[key] == after[key] else 'changed',
                 before=before.get(key), after=after.get(key)) for key in dict.fromkeys([*before, *after])]


def snapshot(catalog, destination):
    destination.mkdir()
    # The source is opened read-only. Only the destination receives writes, logs,
    # revisions and export-target registration from the actual refs CLI.
    with closing(sqlite3.connect((catalog / 'catalog.sqlite').resolve().as_uri() + '?mode=ro', uri=True)) as source:
        with closing(sqlite3.connect(destination / 'catalog.sqlite')) as target:
            source.backup(target)
    (destination / 'ready').touch()
    (destination / 'files.lock').touch()


def copy_project(project, destination):
    source = Path(project['path'])
    excludes = set(project.get('exclude', [])) | {c['artifact'] for c in project['consumers']}

    def ignore(folder, names):
        skipped = []
        for name in names:
            path = Path(folder) / name
            rel = path.relative_to(source).as_posix()
            if name in IGNORED or rel in excludes:
                skipped.append(name)
            elif path.is_symlink():
                raise ValueError(f'Project copy refuses symlink: {path}')
        return skipped

    inputs = []
    for item in project.get('inputs', []):
        path = source / relative(item)
        if '.git' in Path(item).parts or any(p.is_symlink() for p in [path, *path.parents] if p != source and source in p.parents):
            raise ValueError(f'Explicit input refuses symlink or Git internals: {path}')
        if not path.is_file():
            raise ValueError(f'Explicit input must be an existing file: {path}')
        inputs.append((path, destination / item))
    shutil.copytree(source, destination, ignore=ignore)
    for path, target in inputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def check_project(project, catalog, work, fixtures):
    home = work / project['name']
    home.mkdir()
    copy = home / 'project'
    copy_project(project, copy)
    clone = home / 'catalog'
    snapshot(catalog, clone)
    config = home / 'config.toml'
    config.write_text('schema_version = 1\n')
    exports = []
    for target in project['targets']:
        output = copy / target['path']
        output.parent.mkdir(parents=True, exist_ok=True)
        output.unlink(missing_ok=True)  # disposable copied export; never the real target
        argv = [sys.executable, '-m', 'refs', '--json', '--config', str(config), '--catalog', str(clone), '--no-project-config',
                'export', '--project', project['refs_project'], '--profile', target['profile'], '--output', str(output)]
        exports.append(json.loads(run_command(argv, ROOT)))
    results = []
    for consumer in project['consumers']:
        versions = {name: run_command(tool['command'], copy).strip() for name, tool in consumer['tools'].items()}
        log = run_command(consumer['command'], copy)
        (home / (consumer['name'] + '.log')).write_text(log)
        current = extract(copy / consumer['artifact'], consumer['extract'])
        fixture = fixtures / project['name'] / (consumer['name'] + '.txt')
        previous = json.loads(fixture.read_text()) if fixture.exists() else None
        if previous is not None and (not isinstance(previous, dict) or not previous or any(not isinstance(k, str) or not isinstance(v, str) for k, v in previous.items())):
            raise ValueError(f'Malformed fixture: {fixture}')
        results.append(dict(consumer=consumer['name'], fixture=str(fixture), fixture_missing=previous is None,
                            versions=versions, recorded_versions={k: v['recorded'] for k, v in consumer['tools'].items()},
                            entries=compare(previous or {}, current), extraction=current))
    return dict(project=project['name'], scratch=str(home), exports=exports, consumers=results)


def markdown(report):
    def cell(value):
        return str(value if value is not None else '—').replace('|', '\\|').replace('\n', '<br>')
    lines = ['| Project | Consumer | Entry | Outcome | Before | After |', '| --- | --- | --- | --- | --- | --- |']
    for project in report['projects']:
        if 'error' in project:
            lines.append(f"| {project['project']} | — | — | error | — | {cell(project['error'])} |")
        for consumer in project.get('consumers', []):
            if consumer['fixture_missing']:
                lines.append(f"| {project['project']} | {consumer['consumer']} | — | missing fixture | — | — |")
            for entry in consumer['entries']:
                lines.append('| ' + ' | '.join(cell(v) for v in [project['project'], consumer['consumer'], entry['entry'], entry['outcome'], entry['before'], entry['after']]) + ' |')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument('--project')
    select.add_argument('--all', action='store_true')
    parser.add_argument('--register', type=Path, default=REGISTER)
    parser.add_argument('--catalog', type=Path, default=Path('/Volumes/Casa/refs/cat'))
    parser.add_argument('--work', type=Path, help='New scratch directory; retained with logs and JSON/Markdown gate tables')
    parser.add_argument('--record', action='store_true', help='Owner accepted this gate: write current extractions as fixtures and record tool versions')
    args = parser.parse_args(argv)
    try:
        data = load_register(args.register)
        selected = [p for p in data['projects'] if args.all or p['name'] == args.project]
        if not selected:
            raise ValueError(f'Project not registered: {args.project}')
        work = args.work.resolve() if args.work else Path(tempfile.mkdtemp(prefix='refs-conversion-'))
        if args.work:
            work.mkdir(parents=True, exist_ok=False)
        report = {'projects': []}
        for project in selected:
            try:
                report['projects'].append(check_project(project, args.catalog, work, args.register.parent))
            except (ValueError, OSError, KeyError, sqlite3.Error, subprocess.TimeoutExpired) as exc:
                report['projects'].append(dict(project=project['name'], error=str(exc)))
        consumers = [c for p in report['projects'] for c in p.get('consumers', [])]
        failed = any('error' in p for p in report['projects']) or any(
            not c['fixture_missing'] and any(e['outcome'] != 'identical' for e in c['entries'])
            for c in consumers)
        exit_code = 1 if failed else 3 if any(c['fixture_missing'] for c in consumers) else 0
        # Recording may create a first fixture, but never partially records a failed run.
        if args.record and not any('error' in p for p in report['projects']):
            for project, result in zip(selected, report['projects'], strict=True):
                for consumer, checked in zip(project['consumers'], result['consumers'], strict=True):
                    path = Path(checked['fixture'])
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(checked['extraction'], ensure_ascii=False, indent=2) + '\n')
                    source = Path(project['path'])
                    commit = run_command(['git', 'rev-parse', 'HEAD'], source).strip() if (source / '.git').exists() and (source / '.git/HEAD').exists() else None
                    consumer['fixture_provenance'] = {
                        'publication_commit': commit, 'source': 'owner-accepted scratch render (--record)',
                        'recorded_at': datetime.now(UTC).isoformat(),
                        'artifact_sha256': hashlib.sha256((Path(result['scratch']) / 'project' / consumer['artifact']).read_bytes()).hexdigest(),
                        'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                    for name, version in checked['versions'].items():
                        consumer['tools'][name]['recorded'] = version
            args.register.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            report['recorded'] = True
        report['exit_code'] = exit_code
        (work / 'gate.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        (work / 'gate.md').write_text(markdown(report))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        print(f'Markdown gate: {work / "gate.md"}', file=sys.stderr)
        return exit_code
    except (ValueError, OSError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
