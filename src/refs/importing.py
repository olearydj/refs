"""Per-entry import transactions, immutable evidence and lightweight run counts."""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from refs import kinds, naming, sources
from refs.adapters import bibtex, csl, zotero
from refs.catalog import changed, connect
from refs.models import SourceCreate, editable, normalize_doi, revalidate
from refs.results import RefError, notice


def preserve(connection, raw: bytes, locator: str, file_digest: str, *, source_id=None, format='bib', origin='import', definitions=None):
    fingerprint = hashlib.sha256(raw).hexdigest()
    existing = connection.execute('SELECT id FROM originals WHERE sha256=? AND origin=? AND locator=?',(fingerprint,origin,locator)).fetchone()
    if existing:
        return existing[0]
    original_id = str(uuid4())
    from refs import logging as action_log
    action_log.log_mutation('source.original', {'id':original_id,'source_id':source_id}, None,
                            {'sha256':fingerprint,'byte_length':len(raw),'format':format,'origin':origin,'locator':locator})
    connection.execute('INSERT OR IGNORE INTO originals (id,source_id,raw_bytes,sha256,byte_length,format,origin,file_digest,locator,definitions_json) VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (original_id, source_id, raw, fingerprint, len(raw), format, origin, file_digest, locator, json.dumps(definitions or {})))
    return original_id


def differences(incoming: dict, current: dict, prefix='') -> list[str]:
    result = []
    for key, value in incoming.items():
        path = f'{prefix}.{key}' if prefix else key
        if key in ('schema_version', 'citation_key', 'provenance') or value in ({}, []):
            continue
        existing = current.get(key)
        if isinstance(value, dict):
            result.extend(differences(value, existing if isinstance(existing, dict) else {}, path))
        elif key == 'DOI' and isinstance(existing, str) and normalize_doi(value) == normalize_doi(existing):
            continue
        elif value != existing:
            result.append(path)
    return result


def value_at(record: dict, path: str):
    value = record
    for part in path.split('.'):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def isbn_plan(connection, incoming: list[SourceCreate]) -> dict:
    from collections import Counter

    from refs.search import identifier
    counts = Counter(identifier('ISBN',source.metadata.ISBN) for source in incoming if source.metadata.type=='book' and source.metadata.ISBN)
    existing = {}
    for row in connection.execute('SELECT id,metadata_json FROM sources'):
        metadata = json.loads(row['metadata_json'])
        if metadata['type']=='book' and metadata.get('ISBN'):
            existing.setdefault(identifier('ISBN',metadata['ISBN']),[]).append(row['id'])
    return dict(incoming=counts, existing=existing)


def doi_plan(connection) -> dict[str, set[str]]:
    existing: dict[str, set[str]] = {}
    for row in connection.execute('SELECT id,metadata_json FROM sources'):
        doi = json.loads(row['metadata_json']).get('DOI')
        if doi:
            existing.setdefault(normalize_doi(doi), set()).add(row['id'])
    return existing


def title_plan(connection) -> dict[str, list[dict]]:
    """Lowered title to the sources carrying it, built once per batch so the likely-match warning never scans per entry."""
    existing: dict[str, list[dict]] = {}
    for row in connection.execute('SELECT id,citation_key,metadata_json FROM sources'):
        title = json.loads(row['metadata_json']).get('title')
        if isinstance(title, str) and title:
            existing.setdefault(title.lower(), []).append(dict(id=row['id'], citation_key=row['citation_key']))
    return existing


def decisions_plan(connection, origin: str) -> dict[str, list[dict]]:
    kept: dict[str, list[dict]] = {}
    for row in connection.execute("SELECT e.source_id,e.decisions_json FROM import_entries e JOIN imports i ON i.id=e.import_id WHERE i.origin=? AND e.source_id IS NOT NULL AND e.decisions_json!='[]'",(origin,)):
        kept.setdefault(row['source_id'],[]).extend(decision for decision in json.loads(row['decisions_json']) if decision['action']=='keep_current')
    return kept


def match(connection, source: SourceCreate, fingerprint: str, *, isbn_groups=None, doi_groups=None) -> tuple[str | None, list[str]]:
    ids = {row[0] for row in connection.execute('SELECT id FROM sources WHERE citation_key=?', (source.citation_key,))}
    ids.update(row[0] for row in connection.execute('SELECT source_id FROM originals WHERE sha256=? AND source_id IS NOT NULL', (fingerprint,)))
    if source.metadata.DOI:
        doi = normalize_doi(source.metadata.DOI)
        if doi_groups is not None:
            ids.update(doi_groups.get(doi, ()))
        else:
            for row in connection.execute('SELECT id,metadata_json FROM sources'):
                metadata = json.loads(row['metadata_json'])
                if metadata.get('DOI') and doi==normalize_doi(metadata['DOI']):
                    ids.add(row['id'])
    for binding in sources.bindings(source):
        row = connection.execute('SELECT source_id FROM origin_identities WHERE namespace=? AND library_uri=? AND item_key=?', binding).fetchone()
        if row:
            ids.add(row[0])
    if not ids and source.metadata.type=='book' and source.metadata.ISBN:
        from refs.search import identifier
        groups = isbn_groups if isbn_groups is not None else isbn_plan(connection,[source])
        isbn = identifier('ISBN',source.metadata.ISBN)
        candidates = groups['existing'].get(isbn,[])
        if candidates:
            if len(candidates)!=1 or groups['incoming'].get(isbn,0)!=1:
                raise RefError('identity_conflict','ISBN group is not one-to-one; inspect the books without binding them',details={'source_ids':candidates,'isbn':isbn,'incoming_count':groups['incoming'].get(isbn,0)})
            ids.update(candidates)
    if len(ids) > 1:
        raise RefError('identity_conflict', 'Identity signals disagree; inspect the sources', details={'source_ids': sorted(ids)})
    if not ids:
        return None, []
    source_id = next(iter(ids))
    current = sources.core_record(connection, source_id)
    if current['state'] != 'active':
        raise RefError('source_removed', 'Matched source is removed; inspect it before reactivating', details={'source_id': source_id})
    return source_id, differences(source.canonical(), current)


def bind_and_fill(connection, source: SourceCreate, raw: bytes, *, dry_run=False, isbn_groups=None, doi_groups=None, kept_by_source=None, origin=None) -> tuple[str | None, dict]:
    source_id, paths = match(connection, source, hashlib.sha256(raw).hexdigest(),isbn_groups=isbn_groups,doi_groups=doi_groups)
    if not source_id:
        return None, {}
    from refs.search import identifier
    current = sources.core_record(connection, source_id)
    incoming = source.canonical()
    compatible = True
    for field in ('type','edition','DOI','ISBN'):
        before, after = current['metadata'].get(field), incoming['metadata'].get(field)
        if before is None or after is None:
            continue
        if field in ('DOI','ISBN'):
            before, after = identifier(field,str(before)), identifier(field,str(after))
        if before != after:
            compatible = False
    canonical = editable(current)
    fills, conflicts = [], []
    kept = kept_by_source.get(source_id,[]) if kept_by_source is not None else []
    if kept_by_source is None and origin is not None:
        for row in connection.execute('SELECT e.decisions_json FROM import_entries e JOIN imports i ON i.id=e.import_id WHERE e.source_id=? AND i.origin=?', (source_id,origin)):
            kept.extend(decision for decision in json.loads(row[0]) if decision['action']=='keep_current')
    for path in paths:
        if path.startswith('native_type.') and current.get('native_type') and incoming['metadata']['type'] == current['metadata']['type']:
            continue
        before, after = value_at(current,path), value_at(incoming,path)
        if path in ('metadata.DOI','metadata.ISBN') and before and identifier(path.split('.')[1],str(before)) == identifier(path.split('.')[1],str(after)):
            continue
        if any(decision['path']==path and decision['current']==before and decision['incoming']==after for decision in kept):
            continue
        corrected = any(path == marker or path.startswith(marker+'.') or marker.startswith(path+'.') for marker in current['corrected_fields'])
        if compatible and before in (None,[],{}) and not corrected:
            sources.patch_path(canonical,path,after,clear=False)
            fills.append(path)
        else:
            conflicts.append(dict(path=path,current=before,incoming=after))
    if compatible:
        for entry in incoming.get('provenance',[]):
            imported = entry | {'origin':'import'}
            if entry not in canonical['provenance'] and imported not in canonical['provenance']:
                canonical['provenance'].append(imported)
        if fills and not any(p.get('origin')=='import' for p in canonical['provenance']):
            canonical['provenance'].append(dict(origin='import',access='unknown'))
        if not dry_run:
            # Validate the combined record before binding the incoming identity.
            canonical = revalidate(canonical)
            if canonical != editable(current):
                sources.store_record(connection,current,canonical,current['corrected_fields'])
            for binding in sources.bindings(source):
                connection.execute('INSERT OR IGNORE INTO origin_identities VALUES (?,?,?,?,?)', (*binding,source_id,hashlib.sha256(raw).hexdigest()))
    return source_id, dict(bound=compatible, incoming_key=source.citation_key, catalog_key=current['citation_key'], filled=fills, conflicts=conflicts)


def apply_entry(connection, block: dict, locator: str, file_digest: str, *, dry_run=False, settings=None, import_id=None, isbn_groups=None, doi_groups=None, kept_by_source=None, origin=None, loc=None, title_groups=None, kind=None) -> dict:
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
        canonical = source.canonical()
        if kind is not None:
            canonical = kinds.assign(canonical, kind)
        canonical, warnings = naming.normalize(canonical,settings.values if settings else None)
        warnings.extend(kinds.warnings(canonical))
        canonical.pop('citation_key', None)
        canonical['provenance'][0]['source_identity'] = dict(namespace='bibtex', library_uri=locator, item_key=key)
        source = SourceCreate.model_validate(canonical)
        source.citation_key = key
        incoming = source.canonical()
        source_id, binding = bind_and_fill(connection, source, raw, dry_run=dry_run,isbn_groups=isbn_groups,doi_groups=doi_groups,kept_by_source=kept_by_source,origin=origin or locator)
        conflicts = [item['path'] for item in binding.get('conflicts', [])]
        if conflicts:
            outcome = dict(outcome='conflict', code='value_conflict', source_id=source_id, citation_key=key, conflicts=conflicts)
        elif source_id:
            if loc is not None and not binding.get('conflicts'):
                sources.set_loc(connection, sources.core_record(connection, source_id), loc, dry_run=dry_run)
            outcome = dict(outcome='applied' if binding.get('filled') else 'unchanged', source_id=source_id, citation_key=key)
        else:
            title = source.metadata.title
            if title_groups is not None:
                likely = list(title_groups.get(title.lower(), [])) if isinstance(title, str) else []
            else:
                likely = [dict(row) for row in connection.execute("SELECT id, citation_key FROM sources WHERE lower(json_extract(metadata_json,'$.title'))=lower(?)", (title,)).fetchall()]
            if likely:
                warnings.append(notice('likely_match', 'Similar title found; imported separately because title alone is not identity', details={'candidates': likely}))
            if not dry_run:
                if loc is not None and source.loc is None:
                    source.loc = loc
                created = sources.insert_source(connection, source, raw, evidence_locator, format='bib', warnings=warnings, key_provenance={'origin':'supplied', 'policy':None, 'table_version':None, 'unicode_version':None})
                source_id = created['id']
            outcome = dict(outcome='applied', source_id=source_id, citation_key=key)
        outcome.update(binding=binding, warnings=warnings, limitations=parsed['limitations'], resource_proposals=parsed['resource_proposals'])
        if settings is not None and source_id and outcome['outcome'] in ('applied','unchanged'):
            from refs.resources import import_links
            outcome['resources'], resource_warnings = import_links(connection,settings,source_id,parsed['resource_proposals'],locator,dry_run=dry_run)
            outcome['warnings'].extend(resource_warnings)
            outcome['resource_proposals'] = []
    except (RefError, ValidationError) as exc:
        if isinstance(exc,RefError) and exc.issue['code'] == 'log_unwritable':
            raise
        if isinstance(exc, ValidationError):
            message = f'Entry at byte {block["start"]}: citation key is empty' if re.match(rb'@\w+\s*[{(]\s*,', raw) else 'Entry cannot satisfy the record profile; inspect its preserved original'
            exc = RefError('invalid_bib_entry', message, 2)
        conflict = exc.issue['code'] in ('identity_conflict', 'source_removed', 'alias_conflict', 'value_conflict')
        outcome = dict(outcome='conflict' if conflict else 'invalid', code=exc.issue['code'], message=str(exc), details=exc.issue['details'], limitations=exc.issue['details'].get('limitations', []))
    outcome['kind'] = kinds.identify(incoming) if incoming else None
    outcome['incoming'] = incoming
    outcome['citation_key'] = key
    outcome['status'] = outcome['outcome']
    outcome.update(start=block['start'], end=block['end'], preserved=True, editable=outcome['outcome'] in ('applied','unchanged'), searchable=outcome['outcome'] in ('applied','unchanged'), exportable='requires export assessment')
    if not dry_run:
        outcome['original_ref'] = preserve(connection, raw, evidence_locator, file_digest, source_id=source_id if outcome['outcome'] in ('applied','unchanged') else None,
                 origin='import-'+outcome['outcome'], definitions=dict(start=block['start'], end=block['end'], limitations=outcome.get('limitations', []), import_id=import_id, incoming_key=key))
    return outcome


def start_batch(connection, batch: str, origin: str, fingerprint: str) -> None:
    from refs import logging as action_log
    action_log.log_mutation('import.batch_open', {'batch_id':batch}, None,
                            {'origin':origin,'file_digest':fingerprint,'counts':{'applied':0,'unchanged':0,'conflict':0,'invalid':0}})
    connection.execute('INSERT INTO imports (id,origin,file_digest,started_at) VALUES (?,?,?,?)', (batch, origin, fingerprint, datetime.now(UTC).isoformat()))


def save_add_conflict(connection, raw: bytes, locator: str, result: dict) -> None:
    if not result.get('binding', {}).get('conflicts'):
        return
    batch = str(uuid4())
    start_batch(connection, batch, 'add', hashlib.sha256(raw).hexdigest())
    save_entry(connection, batch, locator, result)
    connection.execute('UPDATE imports SET conflict=1, revision=revision+1, finished_at=? WHERE id=?', (datetime.now(UTC).isoformat(), batch))
    changed(connection)


def run(catalog: Path, raw: bytes, locator: str, *, dry_run=False, origin: str | None = None, settings=None) -> dict:
    fingerprint = hashlib.sha256(raw).hexdigest()
    run_id = str(uuid4())
    counts = dict(applied=0, unchanged=0, conflict=0, invalid=0)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            start_batch(connection, run_id, origin or locator, fingerprint)
            preserve(connection, raw, locator, fingerprint, format='bib-file', origin='import-file')
            changed(connection)
    blocks = bibtex.partition(raw)
    incoming = []
    for block in blocks:
        if block['kind']=='entry':
            try:
                incoming.append(bibtex.parse(block['raw'])['source'])
            except RefError:
                pass
    with connect(catalog) as connection:
        isbn_groups = isbn_plan(connection,incoming)
        doi_groups = doi_plan(connection) if any(source.metadata.DOI for source in incoming) else None
        kept_by_source = decisions_plan(connection,origin or locator)
        title_groups = title_plan(connection)
    entries = []
    for block in blocks:
        if block['kind'] != 'entry':
            continue
        with connect(catalog, write=not dry_run) as connection:
            result = apply_entry(connection, block, locator, fingerprint, dry_run=dry_run, settings=settings, import_id=run_id,isbn_groups=isbn_groups,doi_groups=doi_groups,kept_by_source=kept_by_source,origin=origin or locator,title_groups=title_groups)
            outcome = result['outcome']
            if outcome == 'applied' and result.get('source_id') and result.get('incoming'):
                created_title = result['incoming']['metadata'].get('title')
                if isinstance(created_title, str) and created_title:
                    title_groups.setdefault(created_title.lower(), []).append(dict(id=result['source_id'], citation_key=result.get('citation_key')))
            if doi_groups is not None and (outcome in ('applied','unchanged') or result.get('binding',{}).get('bound')) and result.get('source_id') and result.get('incoming'):
                doi = result['incoming']['metadata'].get('DOI')
                if doi:
                    doi_groups.setdefault(normalize_doi(doi),set()).add(result['source_id'])
            counts[outcome] += 1
            if not dry_run:
                save_entry(connection, run_id, f"{locator}#bytes={block['start']}:{block['end']}", result)
                connection.execute(f'UPDATE imports SET {outcome}={outcome}+1, revision=revision+1 WHERE id=?', (run_id,))
                changed(connection)
            entries.append(result)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            from refs import logging as action_log
            action_log.log_mutation('import.batch_close', {'batch_id':run_id},
                                    {'finished':False}, {'finished':True,'counts':counts})
            connection.execute('UPDATE imports SET finished_at=? WHERE id=?', (datetime.now(UTC).isoformat(), run_id))
    return dict(import_id=None if dry_run else run_id, input=locator, file_digest=fingerprint, counts=counts, entries=entries, dry_run=dry_run, warnings=[])


def csl_blocks(raw: bytes) -> list[dict]:
    """Split a CSL object or array without rewriting any element's evidence bytes."""
    try:
        text = raw.decode('utf-8')
        decoder = json.JSONDecoder()
        position = 0
        byte_position = 0
        blocks = []

        def byte_at(index: int) -> int:
            nonlocal position, byte_position
            byte_position += len(text[position:index].encode('utf-8'))
            position = index
            return byte_position

        def space(index: int) -> int:
            while index < len(text) and text[index] in ' \t\r\n':
                index += 1
            return index

        index = space(0)
        array = index < len(text) and text[index] == '['
        if array:
            index += 1
        while True:
            index = space(index)
            if array and index < len(text) and text[index] == ']':
                index += 1
                break
            start = index
            value, end = decoder.raw_decode(text, index)
            if not array and not isinstance(value, dict):
                raise ValueError('Expected one CSL object or an array of CSL objects')
            first, last = byte_at(start), byte_at(end)
            blocks.append(dict(raw=raw[first:last], start=first, end=last))
            index = space(end)
            if not array:
                break
            if index >= len(text) or text[index] not in ',]':
                raise ValueError('Expected a comma or closing bracket in CSL array')
            if text[index] == ']':
                index += 1
                break
            index += 1
            if space(index) < len(text) and text[space(index)] == ']':
                raise ValueError('Trailing comma in CSL array')
        if space(index) != len(text):
            raise ValueError('Expected one CSL object or an array of CSL objects')
        return blocks
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise RefError('invalid_record', 'Input is not a CSL JSON object or array', 2) from exc


def apply_csl_entry(connection, block: dict, locator: str, file_digest: str, *, dry_run=False, settings=None, import_id=None, isbn_groups=None, doi_groups=None, kept_by_source=None, origin=None) -> dict:
    raw = block['raw']
    evidence_locator = f"{locator}#bytes={block['start']}:{block['end']}"
    source_id, incoming = None, None
    result: dict = {}
    try:
        source, limitations = csl.parse(raw, with_limitations=True)
        identity = source.provenance[0].source_identity
        row = connection.execute('SELECT id FROM sources WHERE citation_key=?', (identity.item_key,)).fetchone() if identity else None
        current = sources.core_record(connection, row[0]) if row else None
        canonical = source.canonical()
        if current:
            # Exported CSL ids are catalog keys; unrelated external ids still use normal key allocation.
            canonical['citation_key'] = current['citation_key']
        if current and canonical['metadata'] == current['metadata']:
            # Keep the exact casing policy when imported metadata is already identical.
            canonical['title_protection'] = current['title_protection']
            warnings = []
        else:
            canonical, warnings = naming.normalize(canonical, settings.values if settings else None)
        warnings.extend(kinds.warnings(canonical))
        source = SourceCreate.model_validate(canonical)
        incoming = source.canonical()
        source_id, binding = bind_and_fill(connection, source, raw, dry_run=dry_run, isbn_groups=isbn_groups, doi_groups=doi_groups, kept_by_source=kept_by_source, origin=origin or locator)
        conflicts = [item['path'] for item in binding.get('conflicts', [])]
        if conflicts:
            result = dict(status='conflict', code='value_conflict', source_id=source_id, conflicts=conflicts)
        elif source_id:
            result = dict(status='applied' if binding.get('filled') else 'unchanged', source_id=source_id)
        else:
            provenance = sources.allocate_key(connection, source, settings.values if settings else None, warnings=warnings)
            if not dry_run:
                source_id = sources.insert_source(connection, source, raw, evidence_locator, format='csljson', warnings=warnings, key_provenance=provenance, limitations=limitations)['id']
            result = dict(status='applied', source_id=source_id)
        result.update(binding=binding, citation_key=binding.get('catalog_key') or source.citation_key, warnings=warnings, limitations=limitations)
    except (RefError, ValidationError) as exc:
        if isinstance(exc, RefError) and exc.issue['code'] == 'log_unwritable':
            raise
        if isinstance(exc, ValidationError):
            exc = RefError('invalid_record', 'Input does not match the supported record profile', 2)
        result = dict(status='conflict' if exc.issue['code'] in ('identity_conflict', 'source_removed', 'alias_conflict', 'value_conflict') else 'invalid', code=exc.issue['code'], message=str(exc), details=exc.issue['details'], limitations=exc.issue['details'].get('limitations', []))
    result.update(kind=kinds.identify(incoming) if incoming else None, outcome=result['status'], incoming=incoming, start=block['start'], end=block['end'], preserved=True, editable=result['status'] in ('applied', 'unchanged'), searchable=result['status'] in ('applied', 'unchanged'), exportable='requires export assessment')
    if not dry_run:
        result['original_ref'] = preserve(connection, raw, evidence_locator, file_digest, source_id=source_id if result['status'] in ('applied', 'unchanged') else None, format='csljson', origin='import-'+result['status'], definitions=dict(start=block['start'], end=block['end'], limitations=result.get('limitations', []), import_id=import_id))
    return result


def run_csl(catalog: Path, raw: bytes, locator: str, *, dry_run=False, origin: str | None = None, settings=None) -> dict:
    blocks = csl_blocks(raw)
    fingerprint, run_id = hashlib.sha256(raw).hexdigest(), str(uuid4())
    counts = dict(applied=0, unchanged=0, conflict=0, invalid=0)
    incoming = []
    for block in blocks:
        try:
            incoming.append(csl.parse(block['raw']))
        except RefError:
            pass
    with connect(catalog) as connection:
        isbn_groups = isbn_plan(connection, incoming)
        doi_groups = doi_plan(connection) if any(source.metadata.DOI for source in incoming) else None
        kept_by_source = decisions_plan(connection, origin or locator)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            start_batch(connection, run_id, origin or locator, fingerprint)
            preserve(connection, raw, locator, fingerprint, format='csljson-file', origin='import-file')
            changed(connection)
    entries = []
    for block in blocks:
        with connect(catalog, write=not dry_run) as connection:
            result = apply_csl_entry(connection, block, locator, fingerprint, dry_run=dry_run, settings=settings, import_id=run_id, isbn_groups=isbn_groups, doi_groups=doi_groups, kept_by_source=kept_by_source, origin=origin or locator)
            status = result['status']
            if doi_groups is not None and result.get('source_id') and result.get('incoming') and status in ('applied', 'unchanged'):
                doi = result['incoming']['metadata'].get('DOI')
                if doi:
                    doi_groups.setdefault(normalize_doi(doi), set()).add(result['source_id'])
            counts[status] += 1
            if not dry_run:
                save_entry(connection, run_id, f"{locator}#bytes={block['start']}:{block['end']}", result)
                connection.execute(f'UPDATE imports SET {status}={status}+1, revision=revision+1 WHERE id=?', (run_id,))
                changed(connection)
            entries.append(result)
    if not dry_run:
        with connect(catalog, write=True) as connection:
            from refs import logging as action_log
            action_log.log_mutation('import.batch_close', {'batch_id':run_id}, {'finished':False}, {'finished':True,'counts':counts})
            connection.execute('UPDATE imports SET finished_at=? WHERE id=?', (datetime.now(UTC).isoformat(), run_id))
    return dict(import_id=None if dry_run else run_id, input=locator, file_digest=fingerprint, counts=counts, entries=entries, dry_run=dry_run, warnings=[])


def add(catalog: Path, raw: bytes, locator: str, *, dry_run=False, settings=None, loc=None, kind=None) -> dict:
    blocks = [block for block in bibtex.partition(raw) if block['kind'] == 'entry']
    if len(blocks) != 1:
        raise RefError('invalid_bib_input', 'Use add for one entry, or import for a bibliography', 2)
    with connect(catalog, write=not dry_run) as connection:
        entry = apply_entry(connection, blocks[0], locator, hashlib.sha256(raw).hexdigest(), dry_run=dry_run, settings=settings, origin='add', loc=loc, kind=kind)
        if not dry_run:
            save_add_conflict(connection, raw, locator, entry)
    if entry['outcome'] in ('conflict', 'invalid'):
        raise RefError(entry['code'], entry.get('message', 'Inspect conflicting fields and use update'), 2 if entry['outcome'] == 'invalid' else 3, details=entry['details'] if entry.get('details', {}).get('kind') else entry,
                       data={'outcome':'needs_attention', 'citation_key':entry.get('citation_key')})
    record = sources.show(catalog, entry['source_id']) if entry['source_id'] else entry['incoming']
    if dry_run and loc is not None and not record.get('loc'):
        record['loc'] = loc
    return record | dict(kind=kinds.identify(record), outcome='created' if entry['outcome'] == 'applied' else 'already_present', warnings=entry.get('warnings', []), dry_run=dry_run, limitations=entry['limitations'])


def save_entry(connection, batch: str, locator: str, result: dict) -> None:
    source_id = result.get('source_id')
    revision = connection.execute('SELECT revision FROM sources WHERE id=?',(source_id,)).fetchone()[0] if source_id else None
    if result['status'] == 'applied':
        from refs import logging as action_log
        action_log.log_mutation('import.entry', {'batch_id':batch,'source_id':source_id,'citation_key':result.get('citation_key')},
                                {'revision':revision-1} if revision and revision > 1 else None,
                                {'revision':revision,'status':'applied','locator':locator})
    candidates = result.get('details', {}).get('source_ids', [source_id] if source_id else [])
    connection.execute('INSERT INTO import_entries (id,import_id,locator,status,candidates_json,conflicts_json,source_id,source_revision,payload_json) VALUES (?,?,?,?,?,?,?,?,?)',
                       (str(uuid4()), batch, locator, result['status'], json.dumps(candidates), json.dumps(result.get('conflicts', [])), source_id, revision, json.dumps(result)))


def apply_zotero(connection, entry: dict, manifest: dict, fingerprint: str, *, dry_run=False, settings=None, batch=None, isbn_groups=None, origin=None) -> dict:
    incoming, source_id = None, None
    result: dict = {}
    try:
        parsed = zotero.parse(entry['item'], manifest)
        canonical = parsed['source'].canonical()
        key = canonical.pop('citation_key', None)
        incoming, warnings = naming.normalize(canonical, settings.values if settings else None)
        warnings.extend(kinds.warnings(incoming))
        incoming['context'] = entry.get('context', [])
        source = SourceCreate.model_validate(incoming)
        source.citation_key = key
        incoming = source.canonical()
        source_id, binding = bind_and_fill(connection, source, entry['raw'], dry_run=dry_run,isbn_groups=isbn_groups,origin=origin)
        conflicts = [item['path'] for item in binding.get('conflicts', [])]
        if source_id:
            result = dict(status='conflict' if conflicts else 'applied' if binding.get('filled') else 'unchanged', source_id=source_id, conflicts=conflicts)
            if conflicts:
                result['code'] = 'value_conflict'
        else:
            provenance = sources.allocate_key(connection, source, settings.values if settings else None, warnings=warnings)
            if not dry_run:
                source_id = sources.insert_source(connection, source, entry['raw'], entry['locator'], format='zotero-json', warnings=warnings, key_provenance=provenance)['id']
            result = dict(status='applied', source_id=source_id)
        result.update(binding=binding, citation_key=source.citation_key, warnings=warnings, limitations=parsed['limitations'])
    except (RefError,ValueError,TypeError,KeyError,AttributeError) as exc:
        if isinstance(exc,RefError) and exc.issue['code'] == 'log_unwritable':
            raise
        if not isinstance(exc,RefError):
            exc = RefError('invalid_zotero_item','Malformed item fields; inspect the preserved original JSON',2)
        result = dict(status='conflict' if exc.issue['code'] in ('identity_conflict', 'source_removed', 'alias_conflict', 'value_conflict') else 'invalid', code=exc.issue['code'], message=str(exc), details=exc.issue['details'])
    result.update(kind=kinds.identify(incoming) if incoming else None, outcome=result['status'], incoming=incoming, item_key=entry['key'], preserved=True)
    if not dry_run:
        result['original_ref'] = preserve(connection, entry['raw'], entry['locator'], fingerprint, source_id=source_id if result['status'] in ('applied','unchanged') else None,
                 format='zotero-json', origin='import-'+result['status'], definitions=dict(limitations=result.get('limitations', []), import_id=batch, incoming_key=result.get('citation_key')))
    return result


def zotero_isbn_groups(catalog: Path, bundle: dict) -> dict:
    incoming = []
    for entry in bundle['items']:
        if entry['data']['itemType']=='book' and isinstance(entry['data'].get('ISBN'),str):
            incoming.append(SourceCreate.model_validate({'schema_version':'1.0','metadata':{'type':'book','title':'ISBN group candidate','ISBN':entry['data']['ISBN']}}))
    with connect(catalog) as connection:
        return isbn_plan(connection,incoming)


def start_zotero_batch(catalog: Path, directory: Path, bundle: dict, evidence: list[bytes], fingerprint: str, batch: str, origin: str | None) -> dict:
    with connect(catalog, write=True) as connection:
        start_batch(connection, batch, origin or str(directory), fingerprint)
        for name, raw in zip(('manifest.json','collections.json'), evidence, strict=True):
            preserve(connection, raw, str(directory/name), fingerprint, format='zotero-evidence', origin='import-file')
        for entry in bundle['items']:
            if entry['data']['itemType'] in zotero.CHILDREN:
                preserve(connection, entry['raw'], entry['locator'], fingerprint, format='zotero-json', origin='import-child')
        changed(connection)
    with connect(catalog, write=True) as connection:
        return import_collections(connection, bundle)


def zotero_entries(catalog: Path, directory: Path, bundle: dict, fingerprint: str, batch: str, collections: dict, isbn_groups: dict, settings, dry_run: bool, origin: str | None) -> tuple[list[dict], dict]:
    entries = []
    counts = dict(applied=0, unchanged=0, conflict=0, invalid=0)
    for entry in bundle['items']:
        if entry['data']['itemType'] in zotero.CHILDREN:
            continue
        entry['context'] = child_context(bundle, entry['key'])
        with connect(catalog, write=not dry_run) as connection:
            result = apply_zotero(connection, entry, bundle['manifest'], fingerprint, dry_run=dry_run, settings=settings, batch=batch,isbn_groups=isbn_groups,origin=origin or str(directory))
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
    return entries, counts


def finish_zotero_batch(catalog: Path, batch: str, counts: dict) -> None:
    with connect(catalog, write=True) as connection:
        from refs import logging as action_log
        action_log.log_mutation('import.batch_close', {'batch_id':batch},
                                {'finished':False}, {'finished':True,'counts':counts})
        connection.execute('UPDATE imports SET finished_at=? WHERE id=?', (datetime.now(UTC).isoformat(), batch))
        for relation in connection.execute('SELECT source_id,target_uri FROM source_relations WHERE target_id IS NULL').fetchall():
            uri, _, key = relation['target_uri'].rpartition('/items/')
            bound = connection.execute("SELECT source_id FROM origin_identities WHERE namespace='zotero' AND library_uri=? AND item_key=?", (uri,key)).fetchone()
            if bound:
                connection.execute('UPDATE source_relations SET target_id=? WHERE source_id=? AND target_uri=?', (bound[0],relation['source_id'],relation['target_uri']))


def run_zotero(catalog: Path, directory: Path, *, dry_run=False, origin=None, settings=None) -> dict:
    bundle = zotero.read(directory)
    manifest = bundle['manifest']
    evidence = [(directory/name).read_bytes() for name in ('manifest.json','collections.json')]
    fingerprint = hashlib.sha256(b''.join(evidence + [entry['raw'] for entry in bundle['items']])).hexdigest()
    batch = str(uuid4())
    isbn_groups = zotero_isbn_groups(catalog, bundle)
    collections = start_zotero_batch(catalog, directory, bundle, evidence, fingerprint, batch, origin) if not dry_run else {}
    entries, counts = zotero_entries(catalog, directory, bundle, fingerprint, batch, collections, isbn_groups, settings, dry_run, origin)
    if not dry_run:
        finish_zotero_batch(catalog, batch, counts)
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
    result = []
    for entry in bundle['items']:
        data = entry['data']
        if data.get('parentItem') != parent:
            continue
        text = zotero.context(entry['item'])
        if text:
            result.append(dict(text=text, origin='import', original_ref=bundle['manifest']['library_uri']+'/items/'+entry['key']))
    return result


def associate(connection, bundle: dict, entry: dict, source_id: str, collections: dict, *, settings=None, dry_run=False) -> tuple[list, list]:
    from refs.resources import zotero_attachment
    warnings, resources = [], []
    if not dry_run:
        for key in entry['data'].get('collections', []):
            connection.execute('INSERT OR IGNORE INTO source_collections VALUES (?,?)', (source_id,collections[key]['id']))
        for endpoint in zotero.relations(entry['item']):
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
                warnings.append(notice('attachment_missing', 'Original attachment file is missing; restore it at the recorded path', path=child['locator'], details=resource))
        except RefError as exc:
            if exc.issue['code'] == 'log_unwritable':
                raise
            warnings.append(exc.issue)
    return resources, warnings


def inspect_batch(connection, batch: str, status=None) -> dict:
    run = connection.execute('SELECT * FROM imports WHERE id=?', (batch,)).fetchone()
    if run is None:
        raise RefError('import_missing', 'Use the import_id returned by import')
    if status is not None and status not in ('applied','unchanged','conflict','invalid'):
        raise RefError('invalid_status', 'Choose applied, unchanged, conflict or invalid', 2)
    entries, revisions = [], []
    for row in connection.execute('SELECT * FROM import_entries WHERE import_id=? ORDER BY rowid', (batch,)):
        entry = json.loads(row['payload_json'])
        found = connection.execute('SELECT revision FROM sources WHERE id=?', (row['source_id'],)).fetchone() if row['source_id'] else None
        revision = found[0] if found else None
        revisions.append((row['id'], row['source_id'], revision))
        entry.update(entry_id=row['id'], status=row['status'], source_revision=revision,
                     candidates=json.loads(row['candidates_json']), decisions=json.loads(row['decisions_json']))
        if 'binding' in entry:
            conflicts = json.loads(row['conflicts_json'])
            original = {item['path']:item for item in entry['binding'].get('conflicts',[])}
            entry['binding']['conflicts'] = [original[item] if isinstance(item,str) else item for item in conflicts]
            entry['conflicts'] = [item['path'] for item in entry['binding']['conflicts']]
        if status is None or status == row['status']:
            entries.append(entry)
    # A read-only review token binds the persisted batch version and observed sources.
    token = int.from_bytes(hashlib.sha256(json.dumps([run['revision'],revisions]).encode()).digest()[:8], 'big')
    return dict(import_id=batch, origin=run['origin'], batch_revision=token, entries=entries,
                counts={name:run[name] for name in ('applied','unchanged','conflict','invalid')})


def list_batches(catalog: Path) -> dict:
    with connect(catalog) as connection:
        items = []
        for run in connection.execute('SELECT id,origin,started_at,revision,applied,unchanged,conflict,invalid FROM imports ORDER BY started_at DESC,rowid DESC'):
            # The review token binds the batch revision and every observed source revision, read in one indexed query per batch.
            revisions = [(row['id'], row['source_id'], row['revision']) for row in connection.execute(
                'SELECT e.id, e.source_id, s.revision FROM import_entries e LEFT JOIN sources s ON s.id=e.source_id WHERE e.import_id=? ORDER BY e.rowid', (run['id'],))]
            token = int.from_bytes(hashlib.sha256(json.dumps([run['revision'],revisions]).encode()).digest()[:8], 'big')
            items.append(dict(import_id=run['id'], origin=run['origin'], counts={name:run[name] for name in ('applied','unchanged','conflict','invalid')},
                              batch_revision=token, created=run['started_at']))
        return dict(items=items)


def show(catalog: Path, batch: str, status=None) -> dict:
    with connect(catalog) as connection:
        return inspect_batch(connection,batch,status)


def select_reconciliation(connection, review: dict, selectors: list[str], keep_current: list[str] | None, dismiss: list[str] | None = None) -> dict:
    selected: dict[str, dict[str,str]] = {}
    choices = [(selector,'take_incoming') for selector in selectors] + [(selector,'keep_current') for selector in keep_current or []] + [(selector, 'dismissed') for selector in dismiss or []]
    for selector, action in choices:
        exact = [entry for entry in review['entries'] if entry.get('citation_key') == selector]
        candidates = exact or [entry for entry in review['entries'] if entry.get('citation_key') and selector.startswith(entry['citation_key']+'.')]
        if len(candidates) != 1:
            raise RefError('ambiguous_selection', 'Use one unambiguous batch citation key and canonical field path', details={'selector':selector})
        entry = candidates[0]
        if action == 'dismissed':
            if not exact or entry['status'] != 'conflict' or entry.get('binding', {}).get('bound') or entry.get('decisions'):
                raise RefError('invalid_selection', 'Dismiss requires an undecided, unbound conflict selected by exact key', 2, details={'selector': selector})
            selected[entry['entry_id']] = {'': 'dismissed'}
            continue
        if not entry.get('source_id') or not entry.get('incoming') or not entry.get('binding',{}).get('bound'):
            raise RefError('identity_conflict', 'Inspect identity or invalid-entry conflicts before accepting metadata', details={'selector':selector})
        current = sources.record(connection,entry['source_id'])
        if current['state'] != 'active':
            raise RefError('source_removed', 'Reactivate the source before reconciling')
        available = [item['path'] for item in entry.get('binding',{}).get('conflicts',[])]
        requested = available if exact else [selector[len(entry['citation_key'])+1:]]
        if any(path not in available for path in requested):
            raise RefError('invalid_selection', 'Select a conflicting canonical path from import show', 2)
        target = selected.setdefault(entry['entry_id'],{})
        for path in requested:
            if path in target and target[path] != action:
                raise RefError('invalid_selection', 'Choose one decision per field', 2)
            target[path] = action
    return selected


def apply_reconciliation(connection, batch: str, review: dict, selected: dict, execute: bool) -> list[dict]:
    proposals = []
    for entry in review['entries']:
        if entry['entry_id'] not in selected:
            continue
        if selected[entry['entry_id']] == {'': 'dismissed'}:
            decision = {'action': 'dismissed'}
            proposals.append(dict(citation_key=entry['citation_key'], source_id=entry.get('source_id'),
                                  decisions=[decision], remaining_conflicts=[]))
            if execute:
                from refs import logging as action_log
                action_log.log_mutation('import.reconcile', {'batch_id': batch, 'entry_id': entry['entry_id']},
                                        {'decisions': []}, {'decisions': [decision]})
                connection.execute('UPDATE import_entries SET decisions_json=? WHERE id=?',
                                   (json.dumps([decision]), entry['entry_id']))
                connection.execute('UPDATE imports SET revision=revision+1 WHERE id=?', (batch,))
                changed(connection)
            continue
        current = sources.record(connection,entry['source_id'])
        canonical = editable(current)
        decisions = []
        for path in sorted(selected[entry['entry_id']]):
            incoming, previous = value_at(entry['incoming'],path), value_at(current,path)
            if incoming != previous:
                action = selected[entry['entry_id']][path]
                if action == 'take_incoming':
                    sources.patch_path(canonical,path,incoming,clear=False)
                decisions.append(dict(path=path,current=previous,incoming=incoming,action=action))
        try:
            canonical = revalidate(canonical)
        except ValidationError as exc:
            raise RefError('invalid_selection', 'Selected values do not form a valid source; inspect dependent fields', 2) from exc
        remaining = [item for item in entry.get('binding',{}).get('conflicts',[]) if item['path'] not in selected[entry['entry_id']] and value_at(canonical,item['path']) != item['incoming']]
        proposals.append(dict(citation_key=entry['citation_key'],source_id=current['id'],source_revision=current['revision'],decisions=decisions,remaining_conflicts=remaining))
        if execute and (decisions or entry['status']=='conflict' and not remaining):
            from refs import logging as action_log
            action_log.log_mutation('import.reconcile', {'batch_id':batch,'entry_id':entry['entry_id'],'source_id':current['id'],'citation_key':current['citation_key']},
                                    {'revision':current['revision'],'status':entry['status']},
                                    {'revision':current['revision']+bool(any(item['action']=='take_incoming' for item in decisions)),'status':'conflict' if remaining else 'applied'},
                                    changes={item['path']:{'old':item['current'],'new':item['incoming'] if item['action']=='take_incoming' else item['current']} for item in decisions})
            taken = [item['path'] for item in decisions if item['action']=='take_incoming']
            if taken:
                sources.store_record(connection,current,canonical,list(dict.fromkeys(current['corrected_fields']+taken)))
            if entry.get('original_ref'):
                original = connection.execute('SELECT * FROM originals WHERE id=?',(entry['original_ref'],)).fetchone()
                preserve(connection,original['raw_bytes'],original['locator'],original['file_digest'],source_id=current['id'],format=original['format'],origin='import-reconciled',definitions=json.loads(original['definitions_json']))
            status = 'conflict' if remaining else 'applied'
            saved = json.loads(connection.execute('SELECT decisions_json FROM import_entries WHERE id=?',(entry['entry_id'],)).fetchone()[0])
            connection.execute('UPDATE import_entries SET status=?,conflicts_json=?,source_revision=?,decisions_json=? WHERE id=?',
                               (status,json.dumps(remaining),sources.record(connection,current['id'])['revision'],json.dumps(saved+decisions),entry['entry_id']))
            connection.execute(f'UPDATE imports SET {entry["status"]}={entry["status"]}-1, {status}={status}+1, revision=revision+1 WHERE id=?' if status != entry['status'] else 'UPDATE imports SET revision=revision+1 WHERE id=?', (batch,))
            changed(connection)
    return proposals


def reconcile(catalog: Path, batch: str, selectors: list[str], *, keep_current=None, dismiss=None, execute=False, revision=None) -> dict:
    if not selectors and not keep_current and not dismiss:
        raise RefError('invalid_selection', 'Supply --take-incoming/--keep-current KEY[.field] or --dismiss KEY', 2)
    if execute and revision is None:
        raise RefError('revision_required', 'Preview the batch and supply --if-batch-revision', 2)
    with connect(catalog,write=execute) as connection:
        review = inspect_batch(connection,batch)
        if execute and review['batch_revision'] != revision:
            raise RefError('stale_revision', 'Preview the batch again; its entries or source revisions changed', details={'expected':revision,'actual':review['batch_revision']})
        selected = select_reconciliation(connection, review, selectors, keep_current, dismiss)
        proposals = apply_reconciliation(connection, batch, review, selected, execute)
        return dict(import_id=batch,batch_revision=inspect_batch(connection,batch)['batch_revision'],dry_run=not execute,entries=proposals)
