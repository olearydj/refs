"""Rehearse moves on a disposable sample, never on original attachment trees."""
import argparse
import json
import runpy
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import tomllib
from collections import Counter
from contextlib import closing
from pathlib import Path

from refs import catalog, files, moves, resources, sources
from refs.adapters import bibtex
from refs.config import select, toml_text
from refs.results import RefError

REPO=Path(__file__).resolve().parents[3]


def contained(root, relative):
    path=root/relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(root):
        raise ValueError('Sample paths must remain inside the disposable sample')
    return path


def prepare(sample, work):
    manifest=json.loads((sample/'manifest.json').read_text())
    if any(path.is_symlink() for path in sample.rglob('*')):
        raise ValueError('Disposable samples cannot contain symlinks')
    shutil.copytree(sample,work)
    library=work/'lib'
    library.mkdir(exist_ok=True)
    # Simulate the owner's one-time rename only inside this fresh disposable home.
    old_folder,new_folder=library/'Unfiled',library/'unfiled'
    if old_folder.exists():
        if new_folder.exists() and not old_folder.samefile(new_folder):
            raise ValueError('Both intake folders exist; inspect the disposable sample')
        old_folder.rename(new_folder)
    config=work/'config.toml'
    config.write_text(toml_text(dict(schema_version=1,catalog=dict(path=str(work/'cat')),resources=dict(library_root=str(library),roots=dict(library=str(library))))))
    with catalog.connect(work/'cat'):
        pass
    def remap(old):
        path=Path(old)
        for prefix,relative in sorted(manifest['roots'].items(),key=lambda pair:len(pair[0]),reverse=True):
            if path.is_relative_to(prefix):
                return contained(work,str(Path(relative)/path.relative_to(prefix)))
        raise ValueError('Unmapped attachment locator; refusing to read it')
    with closing(sqlite3.connect(work/'cat/catalog.sqlite')) as c, c:
        if c.execute('SELECT count(*) FROM file_operations').fetchone()[0]:
            raise ValueError('Supply a pre-move sample without operation history')
        for resource_id,path,root,relative in c.execute('SELECT id,path,root,relative FROM resources').fetchall():
            if path is not None:
                target=remap(path)
                locator=dict(path=str(target),root=None,relative=None)
            elif root=='library':
                target=contained(library,relative)
                locator=dict(path=None,root='library',relative=relative)
            else:
                raise ValueError('Unmapped named root in sample')
            if not target.is_file():
                raise ValueError('Sample attachment is missing')
            c.execute('UPDATE resources SET path=?,root=?,relative=?,locator=? WHERE id=?',(locator['path'],locator['root'],locator['relative'],json.dumps(locator,sort_keys=True),resource_id))
    settings=select(str(config),str(work/'cat'),no_project_config=True)
    assignment=runpy.run_path(str(REPO/'tools/assign_initial_loc.py'))
    proposals=assignment['preview'](settings,contained(work,manifest['box_root']))
    (work/'assignment-preview.json').write_text(json.dumps(proposals,ensure_ascii=False,indent=2))
    assignments=assignment['apply'](settings,proposals)
    (work/'assignments.json').write_text(json.dumps(assignments,ensure_ascii=False,indent=2))
    return settings


def command(settings):
    return [sys.executable,'-m','refs','--json','--no-project-config','--config',str(settings.config),'--catalog',str(settings.catalog_path()),'reorg','--execute']


def run_scenario(sample, scenario, *, keep=False):
    work=Path(tempfile.mkdtemp(prefix='refs-move-rehearsal-')).resolve()/'home'
    try:
        return _run_scenario(sample, scenario, work)
    finally:
        if not keep:
            shutil.rmtree(work.parent)


def _run_scenario(sample, scenario, work):
    settings=prepare(sample,work)
    with catalog.connect(settings.catalog_path()) as c:
        before=resources.inventory(c)
        with_files=len({item['source_id'] for item in before})
        assigned=c.execute('SELECT count(*) FROM sources WHERE loc IS NOT NULL AND id IN (SELECT source_id FROM resources)').fetchone()[0]
        fileless=c.execute('SELECT count(*) FROM sources WHERE id NOT IN (SELECT source_id FROM resources)').fetchone()[0]
        assert assigned==with_files, 'A source with files lacks loc'
        assert c.execute('SELECT count(*) FROM sources WHERE loc IS NOT NULL AND id NOT IN (SELECT source_id FROM resources)').fetchone()[0]==0, 'A file-less source received loc'
    expected={item['id']:files.hash_file(resources.resolve_path(settings,item)) for item in before}
    planned=moves.reorg(settings)
    extras={path:files.hash_file(Path(path)) for path in planned['unlinked_paths']}
    if scenario!='clean':
        worker="""import os,signal,sys
from refs import moves
from refs.config import select
def interrupt(point,row):
    if point==sys.argv[3]:
        os.kill(os.getpid(),signal.SIGKILL)
moves.checkpoint=interrupt
moves.reorg(select(sys.argv[1],sys.argv[2],no_project_config=True),execute=True)
"""
        killed=subprocess.run([sys.executable,'-c',worker,str(settings.config),str(settings.catalog_path()),scenario],capture_output=True,text=True)
        if killed.returncode!=-signal.SIGKILL:
            raise AssertionError(f'Kill boundary not reached: {killed.returncode}: {killed.stderr}')
    completed=subprocess.run(command(settings),capture_output=True,text=True)
    if completed.returncode:
        raise AssertionError(completed.stdout+completed.stderr)
    report=json.loads(completed.stdout)['data']
    (work/'move-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    with catalog.connect(settings.catalog_path()) as c:
        after=resources.inventory(c)
        operations=[dict(row) for row in c.execute('SELECT * FROM file_operations')]
    assert {item['id'] for item in after}==set(expected), 'Resource IDs or count changed'
    for item in after:
        path=resources.resolve_path(settings,item)
        assert path.is_relative_to(work), 'Locator escaped the disposable home'
        assert files.hash_file(path)==expected[item['id']], 'Attachment bytes changed'
    assert len(operations)==len(planned['moves']) and all(row['state']=='removed' for row in operations)
    assert {row['new_path'] for row in operations}=={row['new_path'] for row in planned['moves']}, 'Collision names changed on resume'
    assert all(not Path(row['old_path']).exists() for row in operations)
    assert all(files.hash_file(Path(path))==digest for path,digest in extras.items()), 'An unlinked extra changed'
    assert moves.reorg(settings,execute=True)['moves']==[], 'Completed rerun was not a no-op'
    return dict(scenario=scenario,resources=len(after),sources_with_files=with_files,sources_assigned=assigned,fileless_sources=fileless,moves=len(report['moves']),already_placed=len(after)-len(report['moves']),unlinked_files=len(extras),findings=0,home=str(work))


def run(sample, *, keep=False):
    sample=Path(sample).expanduser().resolve()
    allowed=[Path(tempfile.gettempdir()).resolve(),Path('/private/tmp'),Path('/Volumes/Casa/tmp'),REPO/'tests/fixtures/real-trial']
    if not any(sample.is_relative_to(root) for root in allowed):
        raise ValueError('Put the disposable sample under the trial fixtures or a temporary directory')
    baseline={str(path.relative_to(sample)):files.hash_file(path) for path in sample.rglob('*') if not path.is_symlink() and path.is_file()}
    results=[run_scenario(sample,scenario,keep=keep) for scenario in ('clean','published_uncommitted','recorded')]
    assert baseline=={str(path.relative_to(sample)):files.hash_file(path) for path in sample.rglob('*') if not path.is_symlink() and path.is_file()}, 'Input sample changed'
    return results


PHASE6_POINTS = ('staged', 'published_uncommitted', 'published', 'recorded', 'unlinked', 'removed', 'inside_copy', 'inside_record_transaction', 'after_row_creation', 'after_unlink')


def phase6_paths(sample, work):
    temporary = Path('/Volumes/Casa/tmp')
    if sample.is_symlink() or work.is_symlink() or not sample.is_dir() or not work.is_dir():
        raise ValueError('Supply real source and work directories')
    if not sample.is_relative_to(temporary) or not work.is_relative_to(temporary) or sample == work or sample.is_relative_to(work) or work.is_relative_to(sample):
        raise ValueError('Work must be separate from the supplied copy under /Volumes/Casa/tmp')


def clone_owner_copy(sample, home):
    """APFS clone the supplied copy. No path in the clone points back at its source."""
    if home.exists():
        raise ValueError('Working home already exists')
    if any(path.is_symlink() for path in sample.rglob('*')):
        raise ValueError('Source copy contains a symbolic link')
    subprocess.run(['cp', '-cR', str(sample), str(home)], check=True)
    config = home/'config.toml'
    config.write_text(toml_text(dict(schema_version=1, catalog=dict(path=str(home/'cat')), resources=dict(library_root=str(home/'lib'), roots=dict(library=str(home/'lib'))))))
    return select(str(config), str(home/'cat'), no_project_config=True)


def phase6_candidate(settings):
    with catalog.connect(settings.catalog_path()) as c:
        items = resources.inventory(c)
        candidates = [(resources.resolve_path(settings, item).stat().st_size, item) for item in items if item['root'] == 'library' and resources.resolve_path(settings, item).is_file()]
    if not candidates:
        raise ValueError('No managed resource in owner copy')
    return min(candidates, key=lambda pair: pair[0])[1]


def phase6_link_for_move(settings, item):
    """Put one cloned attachment outside its loc; the other 555 remain placed."""
    original = resources.resolve_path(settings, item)
    external = settings.catalog_path().parent/'external'/original.name
    external.parent.mkdir()
    original.rename(external)
    locator = dict(path=str(external), root=None, relative=None)
    with closing(sqlite3.connect(settings.catalog_path()/'catalog.sqlite')) as c, c:
        c.execute('DELETE FROM file_operations WHERE resource_id=?', (item['id'],))
        c.execute('UPDATE resources SET locator=?,path=?,root=NULL,relative=NULL WHERE id=?', (json.dumps(locator, sort_keys=True), str(external), item['id']))
    return original, external, files.hash_file(external)


PHASE6_WORKER = '''import os, signal, sys
from refs import moves
from refs.cli import main
point = sys.argv[1]
args = sys.argv[2:]
def die():
    os.kill(os.getpid(), signal.SIGKILL)
if point in ('staged','published_uncommitted','published','recorded','unlinked','removed'):
    def checkpoint(name, row):
        if name == point: die()
    moves.checkpoint = checkpoint
elif point == 'inside_copy':
    def copyfileobj(source, target, length=0):
        target.write(source.read(8192))
        target.flush()
        die()
    moves.shutil.copyfileobj = copyfileobj
elif point == 'inside_record_transaction':
    original = moves.resources.touch_source
    def touch(connection, source_id):
        original(connection, source_id)
        die()
    moves.resources.touch_source = touch
elif point == 'after_row_creation':
    original = moves.create
    def create(*a, **kw):
        row = original(*a, **kw)
        die()
    moves.create = create
elif point == 'after_unlink':
    original = moves.save
    def save(settings, row, **values):
        if values.get('state') == 'removed' and not os.path.exists(row['old_path']): die()
        return original(settings, row, **values)
    moves.save = save
sys.argv = ['refs', *args]
main()
'''


def phase6_moves(sample, work, *, ceiling_seconds=900, ceiling_bytes=2_000_000_000):
    """Kill the refs CLI process at ten protocol points, then resume each cloned home."""
    phase6_paths(sample, work)
    started = time.monotonic()
    baseline_free = shutil.disk_usage(work).free
    if baseline_free < ceiling_bytes * 2:
        raise ValueError('Free space is below twice the temporary-disk ceiling')
    rows = []
    peak_disk = 0
    for point in PHASE6_POINTS:
        home = work/('move-'+point)
        settings = clone_owner_copy(sample, home)
        peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
        try:
            item = phase6_candidate(settings)
            destination, external, digest = phase6_link_for_move(settings, item)
            with catalog.connect(settings.catalog_path()) as c:
                key = c.execute('SELECT citation_key FROM sources WHERE id=?', (item['source_id'],)).fetchone()[0]
            args = ['--json', '--no-project-config', '--config', str(settings.config), '--catalog', str(settings.catalog_path()), 'reorg', '--source', key, '--execute']
            killed = subprocess.run([sys.executable, '-c', PHASE6_WORKER, point, *args], capture_output=True, text=True, cwd=work)
            if killed.returncode != -signal.SIGKILL:
                raise AssertionError(f'{point}: refs CLI was not killed at the chosen point: {killed.returncode} {killed.stdout} {killed.stderr}')
            with closing(sqlite3.connect(settings.catalog_path()/'catalog.sqlite')) as c:
                c.row_factory = sqlite3.Row
                before = dict(c.execute('SELECT * FROM file_operations WHERE resource_id=? ORDER BY created_at DESC LIMIT 1', (item['id'],)).fetchone())
            resumed = subprocess.run([sys.executable, '-m', 'refs', *args], capture_output=True, text=True, cwd=work)
            if resumed.returncode:
                raise AssertionError(f'{point}: resume failed: {resumed.returncode} {resumed.stdout} {resumed.stderr}')
            with catalog.connect(settings.catalog_path()) as c:
                after = dict(c.execute('SELECT * FROM file_operations WHERE resource_id=? ORDER BY created_at DESC LIMIT 1', (item['id'],)).fetchone())
                stored = next(resource for resource in resources.inventory(c) if resource['id'] == item['id'])
            final = resources.resolve_path(settings, stored)
            if after['state'] != 'removed' or final != destination or external.exists() or files.hash_file(final) != digest:
                raise AssertionError(f'{point}: final state, locator, deletion or digest differs')
            rows.append(dict(point=point, killed_process='refs CLI', signal='SIGKILL', state_at_kill=before['state'], state_after_resume=after['state'], digest=digest, source_deleted=not external.exists(), destination_verified=True, resource_id=item['id']))
            peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
        finally:
            shutil.rmtree(home)
        if time.monotonic()-started > ceiling_seconds or baseline_free-shutil.disk_usage(work).free > ceiling_bytes:
            raise ValueError('Rehearsal ceiling exceeded')
    return dict(results=rows, wall_seconds=round(time.monotonic()-started, 2), peak_temporary_bytes=max(peak_disk,0), ceiling_seconds=ceiling_seconds, ceiling_bytes=ceiling_bytes)


def sandboxed(command):
    if shutil.which('sandbox-exec'):
        protected = ['/Volumes/Casa/refs', str(Path.home()/'.config/refs'), str(Path.home()/'Box Sync'), str(Path.home()/'Zotero')]
        profile = '(version 1) (allow default) (deny file-read* file-write* ' + ' '.join('(subpath '+json.dumps(path)+')' for path in protected) + ')'
        return ['sandbox-exec', '-p', profile, *command]
    return command


def phase6_cli(settings, *args, timeout=None):
    command = sandboxed([sys.executable, '-m', 'refs', '--json', '--no-project-config', '--config', str(settings.config), '--catalog', str(settings.catalog_path()), *args])
    result = subprocess.run(command, capture_output=True, text=True, cwd=settings.catalog_path().parent, timeout=timeout)
    try:
        envelope = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f'No JSON from {command}: {result.returncode} {result.stdout} {result.stderr}') from exc
    if result.stderr:
        raise AssertionError(f'Unexpected stderr: {result.stderr}')
    return result.returncode, envelope


def phase6_daily(sample, work):
    phase6_paths(sample, work)
    started = time.monotonic()
    baseline_free = shutil.disk_usage(work).free
    home = work/'daily'
    settings = clone_owner_copy(sample, home)
    try:
        with catalog.connect(settings.catalog_path()) as c:
            candidates = []
            for item in resources.inventory(c):
                path = resources.resolve_path(settings, item)
                if item['root'] == 'library' and path.is_file():
                    memberships = c.execute('SELECT p.name FROM projects p JOIN project_sources ps ON ps.project_id=p.id WHERE ps.source_id=? AND ps.cited=1', (item['source_id'],)).fetchall()
                    if memberships:
                        candidates.append((path.stat().st_size, item, memberships[0][0]))
        _, item, project = min(candidates, key=lambda candidate: candidate[0])
        source = sources.show(settings.catalog_path(), item['source_id'])
        key = source['citation_key']
        path = resources.resolve_path(settings, item)
        file_digest = files.hash_file(path)
        target = home/'daily.bib'
        code, exported = phase6_cli(settings, 'export', '--project', project, '--output', str(target))
        if code or exported['status'] != 'ok':
            raise AssertionError(f'Baseline export failed: {code} {exported["status"]} {exported["errors"][:2]}')
        bibliography_digest = files.hash_file(target)
        code, removed = phase6_cli(settings, 'remove', key, '--if-revision', str(source['revision']), '--execute')
        if code or removed['status'] != 'ok':
            raise AssertionError(f'Remove failed: {code} {removed["status"]} {removed["errors"][:2]}')
        inactive = sources.show(settings.catalog_path(), key)
        if inactive['state'] != 'removed' or files.hash_file(path) != file_digest or files.hash_file(target) != bibliography_digest:
            raise AssertionError('Remove changed a file or the existing bibliography')
        code, reactivated = phase6_cli(settings, 'reactivate', key, '--execute')
        if code or reactivated['status'] != 'ok':
            raise AssertionError(f'Reactivation failed: {code} {reactivated["status"]} {reactivated["errors"][:2]}')
        if sources.show(settings.catalog_path(), key)['state'] != 'active':
            raise AssertionError('Source did not reactivate')
        checks = {}
        for label, command in {'paths': ('paths',), 'show': ('show', key), 'search': ('search', key), 'list': ('list', '--project', project), 'project': ('project', 'show', project), 'collections': ('collection', 'list'), 'imports': ('import', 'list'), 'resources': ('resource', 'check', '--verify')}.items():
            outcome, response = phase6_cli(settings, *command)
            checks[label] = dict(exit=outcome, status=response['status'])
            if outcome or response['status'] != 'ok':
                raise AssertionError(f'{label} failed: {outcome} {response["status"]} {response["errors"][:2]}')
            if label == 'resources':
                checks[label]['statuses'] = dict(Counter(item['status'] for item in response['data']['items']))
                checks[label]['unrecorded_names'] = sorted(Path(item['resolved_path']).name for item in response['data']['items'] if item.get('kind') == 'unrecorded')
        code, backup = phase6_cli(settings, 'backup', '--output', str(home/'snapshot'))
        if code or backup['status'] != 'ok':
            raise AssertionError(f'Backup failed: {code} {backup["status"]} {backup["errors"][:2]}')
        from refs.recovery import validate_snapshot
        validate_snapshot(home/'snapshot')
        return dict(key=key, project=project, removed_state=inactive['state'], reactivated_state='active', resource_digest_before=file_digest, resource_digest_after=files.hash_file(path), bibliography_digest_before=bibliography_digest, bibliography_digest_after_remove=files.hash_file(target), checks=checks, backup_valid=True, wall_seconds=round(time.monotonic()-started,2), peak_temporary_bytes=max(baseline_free-shutil.disk_usage(work).free,0))
    finally:
        shutil.rmtree(home)


def phase6_restore(settings, snapshot, restored, *, timeout=None):
    """Use the documented second-home shape and verify catalog rows, not only manifest bytes."""
    from refs.recovery import validate_snapshot
    manifest = validate_snapshot(snapshot)
    restored.mkdir()
    restored_catalog = restored/'cat'
    restored_catalog.mkdir()
    shutil.copyfile(snapshot/'catalog.sqlite', restored_catalog/'catalog.sqlite')
    for marker in ('files.lock', 'ready'):
        (restored_catalog/marker).touch()
    values = tomllib.loads((snapshot/'config.toml').read_text())
    values['catalog']['path'] = str(restored_catalog)
    values['resources']['library_root'] = str(settings.library)
    values['resources']['roots']['library'] = str(settings.library)
    (restored/'config.toml').write_text(toml_text(values))
    second = select(str(restored/'config.toml'), str(restored_catalog), no_project_config=True)
    with catalog.connect(settings.catalog_path()) as before, catalog.connect(second.catalog_path()) as after:
        tables = [row[0] for row in before.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            if before.execute(f'SELECT * FROM "{table}"').fetchall() != after.execute(f'SELECT * FROM "{table}"').fetchall():
                raise AssertionError(f'Restored {table} rows differ')
    code, response = phase6_cli(second, 'resource', 'check', '--verify', timeout=timeout)
    if code or response['status'] != 'ok':
        raise AssertionError('Restored catalog failed resource check')
    return dict(catalog_id=manifest['catalog_id'], tables_compared=len(tables), rows_match=True, resource_check_items=len(response['data']['items']))


def phase6_corpus(sample, work, manifest_path):
    phase6_paths(sample, work)
    manifest = json.loads(manifest_path.read_text())
    limits = manifest['ceilings']
    paths = [Path(entry['path']).resolve() for entry in manifest['files']]
    if len(paths) > limits['files'] or len(set(paths)) != len(paths):
        raise ValueError('Corpus file count or uniqueness exceeds its manifest ceiling')
    if shutil.disk_usage(work).free < limits['temporary_bytes'] * 2:
        raise ValueError('Insufficient free space for corpus ceiling')
    classification, total_entries = [], 0
    for entry, path in zip(manifest['files'], paths, strict=True):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() != '.bib':
            raise ValueError(f'Corpus input is not a regular .bib file: {path}')
        raw = path.read_bytes()
        try:
            blocks = bibtex.partition(raw)
            count = sum(block['kind'] == 'entry' for block in blocks)
            total_entries += count
            classification.append(dict(source=entry['source'], path=str(path), bytes=len(raw), kind='partitioned', entries=count))
        except RefError as exc:
            classification.append(dict(source=entry['source'], path=str(path), bytes=len(raw), kind='refused_whole', code=exc.issue['code'], entries=0))
    if total_entries > limits['entries']:
        raise ValueError('Corpus entry count exceeds manifest ceiling')
    started = time.monotonic()
    baseline_free = shutil.disk_usage(work).free
    peak_disk = 0
    home = work/'corpus'
    settings = clone_owner_copy(sample, home)
    def remaining():
        seconds = limits['seconds']-(time.monotonic()-started)
        if seconds <= 0:
            raise ValueError('Corpus time ceiling exceeded')
        return seconds
    def bounded_cli(*args):
        return phase6_cli(settings,*args,timeout=remaining())
    results = []
    try:
        linked_before = 0
        file_started = [time.monotonic()]
        def finish(result):
            result['seconds'] = round(time.monotonic()-file_started[0], 2)
            results.append(result)
        for index, row in enumerate(classification):
            file_started[0] = time.monotonic()
            peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
            if time.monotonic()-started > limits['seconds'] or peak_disk > limits['temporary_bytes']:
                raise ValueError('Corpus time or disk ceiling exceeded')
            if row['kind'] == 'refused_whole':
                finish(row)
                continue
            origin = f'phase6-{index}'
            code, imported = bounded_cli('import', '--format', 'bib', '--input', row['path'], '--origin', origin)
            data = imported.get('data') or {}
            outcomes = Counter(item['status'] for item in data.get('entries', []))
            entry_codes = Counter(item.get('code') or 'none' for item in data.get('entries', []) if item['status'] in ('invalid', 'conflict'))
            examples = {code: next((dict(key=item.get('citation_key'), reason=item.get('message')) for item in data.get('entries', []) if (item.get('code') or 'none') == code and item['status'] in ('invalid', 'conflict')), None) for code in entry_codes}
            def reason(item):
                lines = (item.get('message') or '').splitlines()
                if not lines:
                    return item.get('code') or 'unspecified'
                return lines[2].strip() if lines[0].endswith('validation error for SourceCreate') and len(lines) > 2 else lines[0]
            invalid_reasons = Counter(reason(item) for item in data.get('entries', []) if item['status'] == 'invalid')
            conflict_paths = Counter(path for item in data.get('entries', []) if item['status'] == 'conflict' for path in item.get('conflicts', []))
            with catalog.connect(settings.catalog_path()) as c:
                linked_after = c.execute('SELECT count(*) FROM resources WHERE root IS NULL AND path IS NOT NULL').fetchone()[0]
            linked_added = linked_after-linked_before
            linked_before = linked_after
            if sum(outcomes.values()) != row['entries']:
                raise AssertionError(f'Unaccounted entries in {row["path"]}: {outcomes}')
            if code not in (0, 4):
                raise AssertionError(f'Unexpected import exit {code}: {imported["errors"][:2]}')
            again_code, again = bounded_cli('import', '--format', 'bib', '--input', row['path'], '--origin', origin)
            again_counts = (again.get('data') or {}).get('counts', {})
            if again_code not in (0, 4) or again_counts.get('applied') != 0:
                raise AssertionError(f'Re-import applied records for {row["path"]}: {again_counts}')
            project = origin
            bounded_cli('project', 'create', project)
            cited_code, cited = bounded_cli('project', 'cite', project, '--from-import', origin)
            if cited_code:
                finish(row | dict(import_exit=code, outcomes=dict(outcomes), entry_codes=dict(entry_codes), invalid_reasons=dict(invalid_reasons), conflict_paths=dict(conflict_paths), examples=examples, linked_resources_added=linked_added, reimport=again_counts, project_cite_code=cited['errors'][0]['code'], export=dict(skipped='project citation refused')))
                continue
            target = home/f'export-{index}.bib'
            export_code, export = bounded_cli('export', '--project', project, '--output', str(target))
            export_codes = sorted({error['code'] for error in export.get('errors', [])})
            blocking = [item for error in export.get('errors', []) for item in error.get('details', {}).get('entries', []) if item.get('class') in ('blocking', 'structural', 'unknown')]
            export_findings = Counter(item.get('code') or 'unspecified' for item in blocking)
            export_examples = {item['code']: dict(key=item.get('citation_key'), reason=item.get('message')) for item in blocking if item.get('code')}
            if export_code == 0 and target.is_file() and (export.get('data') or {}).get('count', 0) == 0:
                render = dict(skipped='empty selection')
            elif export_code == 0 and target.is_file() and shutil.which('pandoc'):
                rendered = subprocess.run(sandboxed(['pandoc', '--citeproc', '--bibliography', str(target), '-t', 'plain']), input='---\nnocite: "@*"\n---\n', text=True, capture_output=True, timeout=remaining())
                render = dict(exit=rendered.returncode, bytes=len(rendered.stdout.encode()), warnings=len(rendered.stderr.splitlines()))
            elif export_code == 0:
                render = dict(skipped='pandoc unavailable')
            else:
                render = dict(skipped='export blocked', codes=export_codes)
            finish(row | dict(import_exit=code, outcomes=dict(outcomes), entry_codes=dict(entry_codes), invalid_reasons=dict(invalid_reasons), conflict_paths=dict(conflict_paths), examples=examples, linked_resources_added=linked_added, reimport=again_counts, project_cite_code=None, export_exit=export_code, export_entries=(export.get('data') or {}).get('count'), export_codes=export_codes, export_findings=dict(export_findings), export_examples=export_examples, render=render))
            peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
            if time.monotonic()-started > limits['seconds'] or peak_disk > limits['temporary_bytes']:
                raise ValueError('Corpus time or disk ceiling exceeded')
        check_code, check = bounded_cli('resource', 'check', '--verify')
        if check_code or check['status'] != 'ok':
            raise AssertionError('Post-corpus resource check failed')
        statuses = Counter((item.get('kind') or 'recorded', item['status']) for item in check['data']['items'])
        backup_code, backup = bounded_cli('backup', '--output', str(home/'snapshot'))
        if backup_code or backup['status'] != 'ok':
            raise AssertionError(f'Post-corpus backup failed: {backup["errors"][:2]}')
        restored = phase6_restore(settings, home/'snapshot', home/'restored', timeout=remaining())
        elapsed = time.monotonic()-started
        peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
        if elapsed > limits['seconds'] or peak_disk > limits['temporary_bytes']:
            raise ValueError('Corpus time or disk ceiling exceeded during backup or restore')
        return dict(classification=classification, results=results, total_entries=total_entries, outcomes=dict(sum((Counter(result.get('outcomes', {})) for result in results), Counter())), post_resource_check={f'{kind}:{status}': count for (kind,status),count in statuses.items()}, restore=restored, wall_seconds=round(elapsed, 2), peak_temporary_bytes=max(peak_disk,0), ceilings=limits)
    finally:
        shutil.rmtree(home)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample',required=True)
    parser.add_argument('--keep',action='store_true',help='retain disposable rehearsal homes for inspection')
    parser.add_argument('--phase6-work',type=Path,help='run the ten command-kill cases in this external temporary directory')
    parser.add_argument('--daily',action='store_true',help='exercise daily commands on a clone of the supplied copy')
    parser.add_argument('--corpus-manifest',type=Path,help='classify and import the bounded corpus into a clone')
    args=parser.parse_args()
    if args.corpus_manifest:
        if not args.phase6_work:
            parser.error('--corpus-manifest needs --phase6-work')
        print(json.dumps(phase6_corpus(Path(args.sample).resolve(),args.phase6_work.resolve(),args.corpus_manifest.resolve()),indent=2))
    elif args.daily:
        if not args.phase6_work:
            parser.error('--daily needs --phase6-work')
        print(json.dumps(phase6_daily(Path(args.sample).resolve(),args.phase6_work.resolve()),indent=2))
    elif args.phase6_work:
        print(json.dumps(phase6_moves(Path(args.sample).resolve(),args.phase6_work.resolve()),indent=2))
    else:
        print(json.dumps(run(args.sample,keep=args.keep),indent=2))
