"""Per-entry import transactions, immutable evidence and lightweight run counts."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from refs import naming, sources
from refs.adapters import bibtex
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
    likely = connection.execute("SELECT id FROM sources WHERE lower(json_extract(metadata_json,'$.title'))=lower(?)", (source.metadata.title,)).fetchall()
    if likely:
        raise RefError('likely_match', 'Title matches existing sources; inspect before adding', details={'source_ids':[row[0] for row in likely]})
    return None, []


def apply_entry(connection, block: dict, locator: str, file_digest: str, *, dry_run=False, settings=None) -> dict:
    raw = block['raw']
    parsed = None
    outcome: dict
    source_id = None
    evidence_locator = f"{locator}#bytes={block['start']}:{block['end']}"
    try:
        parsed = bibtex.parse(raw)
        source = parsed['source']
        key = source.citation_key
        canonical, warnings = naming.normalize(source.canonical())
        canonical.pop('citation_key', None)
        canonical['provenance'][0]['source_identity'] = dict(namespace='bibtex', library_uri=locator, item_key=key)
        source = SourceCreate.model_validate(canonical)
        source.citation_key = key
        source_id, conflicts = match(connection, source, hashlib.sha256(raw).hexdigest())
        if conflicts:
            outcome = dict(outcome='conflict', code='value_conflict', source_id=source_id, citation_key=key, conflicts=conflicts)
        elif source_id:
            outcome = dict(outcome='unchanged', source_id=source_id, citation_key=key)
        else:
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
    outcome['status'] = outcome['outcome']
    outcome.update(start=block['start'], end=block['end'], preserved=True, editable=outcome['outcome'] in ('applied','unchanged'), searchable=outcome['outcome'] in ('applied','unchanged'), exportable='requires export assessment')
    if not dry_run:
        preserve(connection, raw, evidence_locator, file_digest, source_id=source_id if outcome['outcome'] in ('applied','unchanged') else None,
                 origin='import-'+outcome['outcome'], definitions=dict(start=block['start'], end=block['end'], limitations=outcome.get('limitations', [])))
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
            result = apply_entry(connection, block, locator, fingerprint, dry_run=dry_run, settings=settings)
            outcome = result['outcome']
            counts[outcome] += 1
            if not dry_run:
                connection.execute(f'UPDATE imports SET {outcome}={outcome}+1 WHERE id=?', (run_id,))
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
