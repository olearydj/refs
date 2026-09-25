"""Gate Better BibTeX JSON fixtures through refs in disposable rehearsal homes."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from move_rehearsal import clone_owner_copy, phase6_cli, phase6_paths, phase6_restore, sandboxed

NATIVE_CHILDREN = {'attachment', 'note', 'annotation'}
HERE = Path(__file__).resolve().parent


def fixture_key(path: Path, token: str) -> str:
    return hashlib.sha256(f'{path}:{token}'.encode()).hexdigest()[:8].upper()


def materialize_zotero(path: Path, directory: Path) -> int:
    """Wrap a BBT export's native item values in refs' extracted API directory shape."""
    source = json.loads(path.read_bytes())
    if not isinstance(source, dict) or not isinstance(source.get('items'), list):
        raise ValueError('Not a native Zotero fixture bundle')
    directory.mkdir()
    (directory/'items').mkdir()
    collection_source = source.get('collections') or {}
    if not isinstance(collection_source, dict):
        raise ValueError('Collection map is not an object')
    collection_keys = {key: fixture_key(path, 'collection:'+key) for key in collection_source}
    collections = []
    for key, value in collection_source.items():
        parent = value.get('parent')
        if parent and parent not in collection_keys:
            raise ValueError(f'Unknown collection parent: {parent}')
        collections.append(dict(key=collection_keys[key], data=dict(key=collection_keys[key], name=value.get('name') or key,
                    parentCollection=collection_keys[parent] if parent else False)))
    (directory/'collections.json').write_text(json.dumps(collections, ensure_ascii=False))
    used = set()

    def save(index: str, data: dict, parent: str | None = None) -> str:
        data = dict(data)
        suggested = data.get('key')
        key = suggested if isinstance(suggested, str) and len(suggested) == 8 and suggested.isascii() and suggested.isalnum() and suggested == suggested.upper() else fixture_key(path, index)
        if key in used:
            key = fixture_key(path, index+':duplicate')
        if key in used:
            raise ValueError(f'Duplicate synthetic item key at {index}')
        used.add(key)
        data['key'] = key
        if isinstance(data.get('extra'), list):
            if not all(isinstance(line, str) for line in data['extra']):
                raise ValueError(f'Extra lines are not text at {index}')
            data['extra'] = '\n'.join(data['extra'])
        if parent:
            data['parentItem'] = parent
        if isinstance(data.get('relations'), list):
            if data['relations']:
                raise ValueError(f'Unsupported fixture relation list at {index}')
            data['relations'] = {}
        attachments = data.pop('attachments', [])
        notes = data.pop('notes', [])
        if data.get('itemType') == 'attachment' and isinstance(data.get('path'), str) and Path(data['path']).is_absolute():
            data['path'] = str(directory/'unavailable-attachments'/key)
        (directory/'items'/f'{key}.json').write_text(json.dumps(dict(key=key, data=data), ensure_ascii=False))
        for child_index, attachment in enumerate(attachments):
            if not isinstance(attachment, dict):
                raise ValueError(f'Attachment is not an object at {index}:{child_index}')
            save(f'{index}:attachment:{child_index}', {'itemType':'attachment', **attachment}, key)
        for child_index, note in enumerate(notes):
            if not isinstance(note, str):
                raise ValueError(f'Note is not text at {index}:{child_index}')
            save(f'{index}:note:{child_index}', dict(itemType='note', note=note), key)
        return key

    primary = 0
    for index, item in enumerate(source['items']):
        if not isinstance(item, dict) or not isinstance(item.get('itemType'), str):
            raise ValueError(f'Native item is missing itemType at {index}')
        primary += item['itemType'] not in NATIVE_CHILDREN
        save(str(index), item)
    version = source.get('version') or {}
    manifest = dict(format='refs-zotero-input', version=1, api_version=3,
                    library_uri='users/local/'+fixture_key(path, 'library'), zotero_version=str(version.get('zotero') or 'BBT-fixture'),
                    userdata_version=1, global_version=1, extractor_version='bbt-fixture-wrap-1',
                    data_directory=str(directory), base_path=str(directory), skipped={})
    (directory/'manifest.json').write_text(json.dumps(manifest))
    return primary


def classify(entry: dict) -> dict:
    path = Path(entry['path']).resolve()
    if not path.is_file() or path.is_symlink() or path.suffix.lower() != '.json':
        raise ValueError(f'JSON corpus input is not a regular .json file: {path}')
    value = json.loads(path.read_bytes())
    route = entry['route']
    if route == 'zotero' and isinstance(value, dict) and isinstance(value.get('items'), list):
        kind, count = 'native_zotero', sum(isinstance(item, dict) and item.get('itemType') not in NATIVE_CHILDREN for item in value['items'])
    elif route == 'csl' and isinstance(value, list):
        kind, count = 'csl_array', len(value)
    elif route == 'inapplicable' and isinstance(value, dict) and set(value) == {'id', 'result'}:
        kind, count = 'inapplicable_result', 0
    else:
        raise ValueError(f'Fixture shape does not match declared route: {path}')
    return dict(source=entry['source'], path=str(path), bytes=path.stat().st_size, route=route, kind=kind, entries=count)


def render_export(settings, home: Path, index: int, project: str, remaining) -> dict:
    target = home/f'export-{index}.bib'
    code, envelope = phase6_cli(settings, 'export', '--project', project, '--output', str(target), timeout=remaining())
    export_codes = sorted({error['code'] for error in envelope.get('errors', [])})
    blocking = [item for error in envelope.get('errors', []) for item in error.get('details', {}).get('entries', []) if item.get('class') in ('blocking', 'structural', 'unknown')]
    findings = Counter(item.get('code') or 'unspecified' for item in blocking)
    examples = {item['code']:dict(key=item.get('citation_key'), reason=item.get('message')) for item in blocking if item.get('code')}
    if code == 0 and target.is_file() and (envelope.get('data') or {}).get('count', 0) == 0:
        render = dict(skipped='empty selection')
    elif code == 0 and target.is_file() and shutil.which('pandoc'):
        rendered = subprocess.run(sandboxed(['pandoc', '--citeproc', '--bibliography', str(target), '-t', 'plain']),
                                  input='---\nnocite: "@*"\n---\n', text=True, capture_output=True, timeout=remaining())
        render = dict(exit=rendered.returncode, bytes=len(rendered.stdout.encode()), warnings=len(rendered.stderr.splitlines()))
    elif code == 0:
        render = dict(skipped='pandoc unavailable')
    else:
        render = dict(skipped='export blocked', codes=export_codes)
    return dict(export_exit=code, export_entries=(envelope.get('data') or {}).get('count'), export_codes=export_codes,
                export_findings=dict(findings), export_examples=examples, render=render)


def run(sample: Path, work: Path, manifest_path: Path) -> dict:
    phase6_paths(sample, work)
    manifest = json.loads(manifest_path.read_text())
    limits = manifest['ceilings']
    if len(manifest['files']) > limits['files'] or len({entry['path'] for entry in manifest['files']}) != len(manifest['files']):
        raise ValueError('JSON corpus file count or uniqueness exceeds its manifest ceiling')
    if shutil.disk_usage(work).free < limits['temporary_bytes'] * 2:
        raise ValueError('Insufficient free space for JSON corpus ceiling')
    classification = [classify(entry) for entry in manifest['files']]
    total_entries = sum(row['entries'] for row in classification)
    if total_entries > limits['entries']:
        raise ValueError('JSON corpus entry count exceeds manifest ceiling')
    started = time.monotonic()
    baseline_free = shutil.disk_usage(work).free
    home = work/'corpus'
    settings = clone_owner_copy(sample, home)
    peak_disk, results = 0, []

    def remaining():
        seconds = limits['seconds']-(time.monotonic()-started)
        if seconds <= 0:
            raise ValueError('JSON corpus time ceiling exceeded')
        return seconds

    try:
        for index, row in enumerate(classification):
            peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
            if peak_disk > limits['temporary_bytes']:
                raise ValueError('JSON corpus disk ceiling exceeded')
            if row['kind'] == 'inapplicable_result':
                results.append(row | dict(inapplicable='BBT result object, not a Zotero or CSL source'))
                continue
            project = f'phase6-json-{index}'
            if row['kind'] == 'native_zotero':
                directory = home/f'zotero-{index}'
                try:
                    expected = materialize_zotero(Path(row['path']), directory)
                except ValueError as exc:
                    results.append(row | dict(conversion_refusal=str(exc)))
                    continue
                if expected != row['entries']:
                    raise AssertionError(f'Zotero entry count changed during wrapping: {row["path"]}')
                origin = project
                code, imported = phase6_cli(settings, 'import', '--format', 'zotero', '--input', str(directory), '--origin', origin, timeout=remaining())
                if code == 2 and imported.get('errors', [{}])[0].get('code') == 'invalid_zotero_input':
                    results.append(row | dict(import_exit=code, whole_refusal='invalid_zotero_input', reason=imported['errors'][0]['message']))
                    continue
                if code not in (0, 4):
                    raise AssertionError(f'Unexpected Zotero import exit {code}: {row["path"]}: {imported.get("errors")}')
                data = imported.get('data') or {}
                if sum(data.get('counts', {}).values()) != row['entries']:
                    raise AssertionError(f'Unaccounted Zotero items: {row["path"]}: {data.get("counts")}')
                again_code, again = phase6_cli(settings, 'import', '--format', 'zotero', '--input', str(directory), '--origin', origin, timeout=remaining())
                again_counts = (again.get('data') or {}).get('counts', {})
                if again_code not in (0, 4) or again_counts.get('applied') != 0:
                    raise AssertionError(f'Zotero re-import applied records: {row["path"]}: {again_counts}')
                entry_codes = Counter(item.get('code') or 'none' for item in data.get('entries', []) if item['status'] in ('invalid','conflict'))
                conflict_paths = Counter(path for item in data.get('entries', []) if item['status'] == 'conflict' for path in item.get('conflicts', []))
                examples = {issue:next((dict(key=item.get('citation_key'), reason=item.get('message') or ', '.join(item.get('conflicts', [])),
                                              paths=item.get('conflicts', [])) for item in data.get('entries', []) if item.get('code') == issue), None) for issue in entry_codes}
                result = row | dict(import_exit=code, outcomes=data['counts'], entry_codes=dict(entry_codes), examples=examples, reimport=again_counts,
                                    conflict_paths=dict(conflict_paths), preservation=data.get('preservation', {}))
                phase6_cli(settings, 'project', 'create', project, timeout=remaining())
                cite_code, cited = phase6_cli(settings, 'project', 'cite', project, '--from-import', origin, timeout=remaining())
                if cite_code:
                    results.append(result | dict(project_cite_code=cited['errors'][0]['code'], export=dict(skipped='project citation refused')))
                    continue
            else:
                worker = sandboxed([sys.executable, str(HERE/'corpus_csl_worker.py'), str(settings.config), str(settings.catalog_path()), row['path'], project])
                completed = subprocess.run(worker, capture_output=True, text=True, timeout=remaining(), cwd=work)
                if completed.returncode or completed.stderr:
                    raise AssertionError(f'CSL worker failed for {row["path"]}: {completed.returncode}: {completed.stderr[:1000]}')
                data = json.loads(completed.stdout)
                if sum(data['outcomes'].values()) != row['entries'] or sum(data['reimport'].values()) != row['entries']:
                    raise AssertionError(f'Unaccounted CSL elements: {row["path"]}')
                result = row | data | dict(import_exit=0, project_cite_code=None)
            results.append(result | render_export(settings, home, index, project, remaining))
            peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
            if peak_disk > limits['temporary_bytes']:
                raise ValueError('JSON corpus disk ceiling exceeded')
        check_code, check = phase6_cli(settings, 'resource', 'check', '--verify', timeout=remaining())
        if check_code or check['status'] != 'ok':
            raise AssertionError('Post-JSON-corpus resource check failed')
        statuses = Counter((item.get('kind') or 'recorded',item['status']) for item in check['data']['items'])
        backup_code, backup = phase6_cli(settings, 'backup', '--output', str(home/'snapshot'), timeout=remaining())
        if backup_code or backup['status'] != 'ok':
            raise AssertionError(f'Post-JSON-corpus backup failed: {backup.get("errors")}')
        restored = phase6_restore(settings, home/'snapshot', home/'restored', timeout=remaining())
        elapsed = time.monotonic()-started
        peak_disk = max(peak_disk, baseline_free-shutil.disk_usage(work).free)
        if elapsed > limits['seconds'] or peak_disk > limits['temporary_bytes']:
            raise ValueError('JSON corpus time or disk ceiling exceeded during backup or restore')
        return dict(classification=classification, results=results, total_entries=total_entries,
                    outcomes=dict(sum((Counter(result.get('outcomes', {})) for result in results),Counter())),
                    post_resource_check={f'{kind}:{status}':count for (kind,status),count in statuses.items()},
                    restore=restored, wall_seconds=round(elapsed,2), peak_temporary_bytes=max(peak_disk,0), ceilings=limits)
    finally:
        shutil.rmtree(home)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.sample.resolve(), args.work.resolve(), args.manifest.resolve()), indent=2, ensure_ascii=False))
