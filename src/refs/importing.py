"""Per-entry import transactions, immutable evidence and lightweight run counts."""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from refs import naming, sources
from refs.adapters import bibtex, zotero
from refs.catalog import changed, connect
from refs.models import SourceCreate
from refs.results import RefError


def preserve(connection, raw: bytes, locator: str, file_digest: str, *, source_id=None, format='bib', origin='import', definitions=None):
    fingerprint = hashlib.sha256(raw).hexdigest()
    connection.execute('INSERT OR IGNORE INTO originals (id,source_id,raw_bytes,sha256,byte_length,format,origin,file_digest,locator,definitions_json) VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (str(uuid4()), source_id, raw, fingerprint, len(raw), format, origin, file_digest, locator, json.dumps(definitions or {})))


def differences(incoming: dict, current: dict, prefix='') -> list[str]:
    result = []
    for key, value in incoming.items():
        path = f'{prefix}.{key}' if prefix else key
        if key in ('schema_version', 'citation_key', 'provenance') or value in ({}, []):
            continue
        existing = current.get(key)
        if isinstance(value, dict):
            result.extend(differences(value, existing if isinstance(existing, dict) else {}, path))
        elif key == 'DOI' and isinstance(existing, str) and sources.doi_identity(value) == sources.doi_identity(existing):
            continue
        elif value != existing:
            result.append(path)
    return result


def match(connection, source: SourceCreate, fingerprint: str) -> tuple[str | None, list[str]]:
    ids = {row[0] for row in connection.execute('SELECT id FROM sources WHERE citation_key=?', (source.citation_key,))}
    ids.update(row[0] for row in connection.execute('SELECT source_id FROM originals WHERE sha256=? AND source_id IS NOT NULL', (fingerprint,)))
    for row in connection.execute('SELECT id,metadata_json FROM sources'):
        metadata = json.loads(row['metadata_json'])
        if source.metadata.DOI and metadata.get('DOI') and sources.doi_identity(source.metadata.DOI) == sources.doi_identity(metadata['DOI']):
            ids.add(row['id'])
    for binding in sources.bindings(source):
        row = connection.execute('SELECT source_id FROM origin_identities WHERE namespace=? AND library_uri=? AND item_key=?', binding).fetchone()
        if row:
            ids.add(row[0])
    if len(ids) > 1:
        raise RefError('identity_conflict', 'Identity signals disagree; inspect the sources', details={'source_ids': sorted(ids)})
    if ids:
        source_id = next(iter(ids))
        current = sources.record(connection, source_id)
        if current['state'] != 'active':
            raise RefError('source_removed', 'Matched source is removed; inspect it before reactivating', details={'source_id': source_id})
        return source_id, differences(source.canonical(), current)
    return None, []


def apply_entry(connection, block: dict, locator: str, file_digest: str, *, dry_run=False, settings=None, import_id=None) -> dict:
    raw = block['raw']
    parsed = None
    incoming = None
    header = re.match(rb'@\w+\s*[{(]\s*([^,]+),', raw)
    key = header[1].decode('utf-8', errors='replace').strip() if header else '(unreadable key)'
    outcome: dict
    source_id = None
    evidence_locator = f"{locator}#bytes={block['start']}:{block['end']}"
    try:
        parsed = bibtex.parse(raw)
        source = parsed['source']
        key = source.citation_key
        canonical, warnings = naming.normalize(source.canonical(),settings.values if settings else None)
        canonical.pop('citation_key', None)
        canonical['provenance'][0]['source_identity'] = dict(namespace='bibtex', library_uri=locator, item_key=key)
        source = SourceCreate.model_validate(canonical)
        source.citation_key = key
        incoming = source.canonical()
        source_id, conflicts = match(connection, source, hashlib.sha256(raw).hexdigest())
        if conflicts:
            outcome = dict(outcome='conflict', code='value_conflict', source_id=source_id, citation_key=key, conflicts=conflicts)
        elif source_id:
            outcome = dict(outcome='unchanged', source_id=source_id, citation_key=key)
        else:
            likely = connection.execute("SELECT id, citation_key FROM sources WHERE lower(json_extract(metadata_json,'$.title'))=lower(?)", (source.metadata.title,)).fetchall()
            if likely:
                warnings.append(dict(code='likely_match', message='Similar title found; imported separately because title alone is not identity', path=None, details={'candidates':[dict(row) for row in likely]}, retryable=False))
            if not dry_run:
                created = sources.insert_source(connection, source, raw, evidence_locator, format='bib', warnings=warnings, key_provenance={'origin':'supplied', 'policy':None, 'table_version':None, 'unicode_version':None})
                source_id = created['id']
            outcome = dict(outcome='applied', source_id=source_id, citation_key=key)
        outcome.update(warnings=warnings, limitations=parsed['limitations'], resource_proposals=parsed['resource_proposals'])
        if settings is not None and source_id and outcome['outcome'] in ('applied','unchanged'):
            from refs.resources import import_links
            outcome['resources'], resource_warnings = import_links(connection,settings,source_id,parsed['resource_proposals'],locator,dry_run=dry_run)
            outcome['warnings'].extend(resource_warnings)
            outcome['resource_proposals'] = []
    except (RefError, ValidationError) as exc:
        if isinstance(exc, ValidationError):
            exc = RefError('invalid_bib_entry', 'Entry cannot satisfy the record profile; inspect its preserved original', 2)
        conflict = exc.issue['code'] in ('identity_conflict', 'source_removed', 'likely_match')
        outcome = dict(outcome='conflict' if conflict else 'invalid', code=exc.issue['code'], message=str(exc), details=exc.issue['details'], limitations=exc.issue['details'].get('limitations', []))
    outcome['incoming'] = incoming
    outcome['citation_key'] = key
    outcome['status'] = outcome['outcome']
    outcome.update(start=block['start'], end=block['end'], preserved=True, editable=outcome['outcome'] in ('applied','unchanged'), searchable=outcome['outcome'] in ('applied','unchanged'), exportable='requires export assessment')
    if not dry_run:
        preserve(connection, raw, evidence_locator, file_digest, source_id=source_id if outcome['outcome'] in ('applied','unchanged') else None,
                 origin='import-'+outcome['outcome'], definitions=dict(start=block['start'], end=block['end'], limitations=outcome.get('limitations', []), import_id=import_id))
    return outcome


def run(catalog: Path, raw: bytes, locator: str, *, dry_run=False, origin: str | None = None, settings=None) -> dict:
    fingerprint = hashlib.sha256(raw).hexdigest()
    run_id = str(uuid4())
    counts = dict(applied=0, unchanged=0, conflict=0, invalid=0)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            connection.execute('INSERT INTO imports (id,origin,file_digest,started_at) VALUES (?,?,?,?)', (run_id, origin or locator, fingerprint, datetime.now(UTC).isoformat()))
            preserve(connection, raw, locator, fingerprint, format='bib-file', origin='import-file')
            changed(connection)
    blocks = bibtex.partition(raw)
    entries = []
    for block in blocks:
        if block['kind'] != 'entry':
            continue
        with connect(catalog, write=not dry_run) as connection:
            result = apply_entry(connection, block, locator, fingerprint, dry_run=dry_run, settings=settings, import_id=run_id)
            outcome = result['outcome']
            counts[outcome] += 1
            if not dry_run:
                save_entry(connection, run_id, f"{locator}#bytes={block['start']}:{block['end']}", result)
                connection.execute(f'UPDATE imports SET {outcome}={outcome}+1, revision=revision+1 WHERE id=?', (run_id,))
                changed(connection)
            entries.append(result)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            connection.execute('UPDATE imports SET finished_at=? WHERE id=?', (datetime.now(UTC).isoformat(), run_id))
    return dict(import_id=None if dry_run else run_id, input=locator, file_digest=fingerprint, counts=counts, entries=entries, dry_run=dry_run, warnings=[])


def add(catalog: Path, raw: bytes, locator: str, *, dry_run=False, settings=None) -> dict:
    blocks = [block for block in bibtex.partition(raw) if block['kind'] == 'entry']
    if len(blocks) != 1:
        raise RefError('invalid_bib_input', 'Use add for one entry, or import for a bibliography', 2)
    result = run(catalog, raw, locator, dry_run=dry_run, settings=settings)
    entry = result['entries'][0]
    if entry['outcome'] in ('conflict', 'invalid'):
        raise RefError(entry.get('code', 'import_conflict'), entry.get('message', 'Inspect conflicting fields and use update'), 2 if entry['outcome'] == 'invalid' else 3, details=entry,
                       data={'outcome':'needs_attention', 'citation_key':entry.get('citation_key')})
    record = sources.show(catalog, entry['source_id']) if entry['source_id'] else bibtex.parse(blocks[0]['raw'])['source'].canonical()
    return record | dict(outcome='created' if entry['outcome'] == 'applied' else 'already_present', warnings=entry.get('warnings', []), dry_run=dry_run, limitations=entry['limitations'])


def save_entry(connection, batch: str, locator: str, result: dict) -> None:
    source_id = result.get('source_id')
    revision = sources.record(connection, source_id)['revision'] if source_id else None
    candidates = result.get('details', {}).get('source_ids', [source_id] if source_id else [])
    connection.execute('INSERT INTO import_entries (id,import_id,locator,status,candidates_json,conflicts_json,source_id,source_revision,payload_json) VALUES (?,?,?,?,?,?,?,?,?)',
                       (str(uuid4()), batch, locator, result['status'], json.dumps(candidates), json.dumps(result.get('conflicts', [])), source_id, revision, json.dumps(result)))


def apply_zotero(connection, entry: dict, manifest: dict, fingerprint: str, *, dry_run=False, settings=None, batch=None) -> dict:
    incoming, source_id = None, None
    result: dict = {}
    try:
        parsed = zotero.parse(entry['item'], manifest)
        incoming, warnings = naming.normalize(parsed['source'].canonical(), settings.values if settings else None)
        incoming['context'] = entry.get('context', [])
        source = SourceCreate.model_validate(incoming)
        source_id, conflicts = match(connection, source, hashlib.sha256(entry['raw']).hexdigest())
        if source_id:
            result = dict(status='conflict' if conflicts else 'unchanged', source_id=source_id, conflicts=conflicts)
        else:
            provenance = dict(origin='supplied', policy=None, table_version=None, unicode_version=None)
            if source.citation_key is None:
                base, index = naming.key(incoming, settings.values if settings else None), 0
                while connection.execute('SELECT 1 FROM sources WHERE citation_key=?', (base+naming.suffix(index),)).fetchone():
                    index += 1
                source.citation_key = base+naming.suffix(index)
                provenance = naming.provenance(settings.values if settings else None)
            if not dry_run:
                source_id = sources.insert_source(connection, source, entry['raw'], entry['locator'], format='zotero-json', warnings=warnings, key_provenance=provenance)['id']
            result = dict(status='applied', source_id=source_id)
        result.update(citation_key=source.citation_key, warnings=warnings, limitations=parsed['limitations'])
    except RefError as exc:
        result = dict(status='conflict' if exc.issue['code'] in ('identity_conflict', 'source_removed', 'alias_conflict') else 'invalid', code=exc.issue['code'], message=str(exc), details=exc.issue['details'])
    result.update(outcome=result['status'], incoming=incoming, item_key=entry['key'], preserved=True)
    if not dry_run:
        preserve(connection, entry['raw'], entry['locator'], fingerprint, source_id=source_id if result['status'] in ('applied','unchanged') else None,
                 format='zotero-json', origin='import-'+result['status'], definitions=dict(limitations=result.get('limitations', []), import_id=batch))
    return result


def run_zotero(catalog: Path, directory: Path, *, dry_run=False, origin=None, settings=None) -> dict:
    bundle = zotero.read(directory)
    manifest = bundle['manifest']
    evidence = [(directory/name).read_bytes() for name in ('manifest.json','collections.json')]
    fingerprint = hashlib.sha256(b''.join(evidence + [entry['raw'] for entry in bundle['items']])).hexdigest()
    batch = str(uuid4())
    counts = dict(applied=0, unchanged=0, conflict=0, invalid=0)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            connection.execute('INSERT INTO imports (id,origin,file_digest,started_at) VALUES (?,?,?,?)', (batch, origin or str(directory), fingerprint, datetime.now(UTC).isoformat()))
            for name, raw in zip(('manifest.json','collections.json'), evidence, strict=True):
                preserve(connection, raw, str(directory/name), fingerprint, format='zotero-evidence', origin='import-file')
            for entry in bundle['items']:
                if entry['data']['itemType'] in zotero.CHILDREN:
                    preserve(connection, entry['raw'], entry['locator'], fingerprint, format='zotero-json', origin='import-child')
            changed(connection)
    collections = {}
    if not dry_run:
        with connect(catalog, write=True) as connection:
            collections = import_collections(connection, bundle)
    entries = []
    for entry in bundle['items']:
        if entry['data']['itemType'] in zotero.CHILDREN:
            continue
        entry['context'] = child_context(bundle, entry['key'])
        with connect(catalog, write=not dry_run) as connection:
            result = apply_zotero(connection, entry, manifest, fingerprint, dry_run=dry_run, settings=settings, batch=batch)
            if result.get('source_id') and result['status'] in ('applied','unchanged'):
                result['resources'], notices = associate(connection,bundle,entry,result['source_id'],collections,settings=settings,dry_run=dry_run)
                result.setdefault('warnings', []).extend(notices)
            status = result['status']
            counts[status] += 1
            if not dry_run:
                save_entry(connection, batch, entry['locator'], result)
                connection.execute(f'UPDATE imports SET {status}={status}+1, revision=revision+1 WHERE id=?', (batch,))
                changed(connection)
            entries.append(result)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            connection.execute('UPDATE imports SET finished_at=? WHERE id=?', (datetime.now(UTC).isoformat(), batch))
            for relation in connection.execute('SELECT source_id,target_uri FROM source_relations WHERE target_id IS NULL').fetchall():
                uri, _, key = relation['target_uri'].rpartition('/items/')
                bound = connection.execute("SELECT source_id FROM origin_identities WHERE namespace='zotero' AND library_uri=? AND item_key=?", (uri,key)).fetchone()
                if bound:
                    connection.execute('UPDATE source_relations SET target_id=? WHERE source_id=? AND target_uri=?', (bound[0],relation['source_id'],relation['target_uri']))
    preservation = dict(manifest.get('skipped', {}))
    preservation['attachment_outlines'] = sum(bool(item['data'].get('note')) for item in bundle['items'] if item['data']['itemType']=='attachment')
    preservation['standalone_children'] = sum(not item['data'].get('parentItem') for item in bundle['items'] if item['data']['itemType'] in zotero.CHILDREN)
    return dict(import_id=None if dry_run else batch, input=str(directory), file_digest=fingerprint, counts=counts, entries=entries, dry_run=dry_run, warnings=[], preservation=preservation)


def import_collections(connection, bundle: dict) -> dict:
    uri = bundle['manifest']['library_uri']
    pending = {entry['key']: entry['data'] for entry in bundle['collections']}
    result = {}
    while pending:
        for key, data in list(pending.items()):
            parent = data.get('parentCollection')
            if parent and parent not in result:
                continue
            path = (result[parent]['path']+'/' if parent else '')+data['name']
            previous = connection.execute('SELECT * FROM collections WHERE library_uri=? AND item_key=?', (uri,key)).fetchone()
            identity = previous['id'] if previous else str(uuid4())
            parent_id = result[parent]['id'] if parent else None
            if not previous:
                connection.execute('INSERT INTO collections (id,library_uri,item_key,parent,name,path) VALUES (?,?,?,?,?,?)', (identity,uri,key,parent_id,data['name'],path))
            elif (previous['parent'],previous['name'],previous['path']) != (parent_id,data['name'],path):
                connection.execute('UPDATE collections SET parent=?,name=?,path=?,revision=revision+1 WHERE id=?', (parent_id,data['name'],path,identity))
            result[key] = dict(id=identity,path=path)
            del pending[key]
    return result


def child_context(bundle: dict, parent: str) -> list[dict]:
    import html
    result = []
    for entry in bundle['items']:
        data = entry['data']
        if data.get('parentItem') != parent:
            continue
        text = None
        if data['itemType'] == 'note':
            text = html.unescape(re.sub(r'<[^>]*>', ' ', data.get('note','')))
            text = ' '.join(text.split())
        elif data['itemType'] == 'attachment' and data.get('linkMode') == 'linked_url':
            text = data.get('url')
        if text:
            result.append(dict(text=text, origin='import', original_ref=entry['locator']))
    return result


def associate(connection, bundle: dict, entry: dict, source_id: str, collections: dict, *, settings=None, dry_run=False) -> tuple[list, list]:
    from refs.resources import zotero_attachment
    warnings, resources = [], []
    if not dry_run:
        for key in entry['data'].get('collections', []):
            connection.execute('INSERT OR IGNORE INTO source_collections VALUES (?,?)', (source_id,collections[key]['id']))
        relations = entry['data'].get('relations', {}).get('dc:relation', [])
        for target in [relations] if isinstance(relations,str) else relations:
            endpoint = target.removeprefix('http://zotero.org/').removeprefix('https://zotero.org/')
            uri, _, key = endpoint.rpartition('/items/')
            bound = connection.execute("SELECT source_id FROM origin_identities WHERE namespace='zotero' AND library_uri=? AND item_key=?", (uri,key)).fetchone()
            connection.execute('INSERT OR IGNORE INTO source_relations VALUES (?,?,?,?)', (source_id,endpoint,bound[0] if bound else None,bundle['manifest']['library_uri']))
    for child in bundle['items']:
        data = child['data']
        if data.get('parentItem') != entry['key'] or data['itemType'] != 'attachment' or data.get('linkMode') == 'linked_url':
            continue
        try:
            resource = zotero_attachment(connection,settings,source_id,child['item'],bundle['manifest'],dry_run=dry_run)
            resources.append(resource)
            if resource['status'] == 'missing':
                warnings.append(dict(code='attachment_missing',message='Original attachment file is missing; restore it at the recorded path',path=child['locator'],details=resource,retryable=False))
        except RefError as exc:
            warnings.append(exc.issue)
    return resources, warnings
