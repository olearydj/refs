"""Capture services preserve original evidence and never merge a candidate."""

import hashlib
import json
import sqlite3
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from refs import kinds, languages, naming
from refs import logging as action_log
from refs.adapters.search_sqlite import refresh
from refs.catalog import changed, connect
from refs.models import REGISTRY, SourceCreate, editable, parse, revalidate
from refs.results import RefError, notice


def core_record(connection, source_id: str) -> dict:
    row = connection.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()
    if row is None:
        raise RefError("source_missing", "Source was not found")
    value = dict(row)
    result = json.loads(value.pop("details_json")) | value
    if result.get("loc") is None:
        result.pop("loc", None)
    result["metadata"] = json.loads(result.pop("metadata_json"))
    result["corrected_fields"] = json.loads(result.pop("corrected_fields_json"))
    result["key_provenance"] = json.loads(result.pop("key_provenance_json"))
    result['kind'] = kinds.identify(result)
    return result


def record(connection, source_id: str) -> dict:
    result = core_record(connection, source_id)
    result["originals"] = [dict(r) for r in connection.execute(
        "SELECT id, sha256, byte_length, format, origin, locator FROM originals WHERE source_id=? ORDER BY id",
        (source_id,))]
    result['limitations'] = languages.limitations(result['metadata'])
    for original in connection.execute("SELECT definitions_json FROM originals WHERE source_id=? AND (origin LIKE 'import-%' OR (origin='add' AND format='csljson'))", (source_id,)):
        for limitation in json.loads(original[0]).get('limitations', []):
            paths = [row['canonical_path'] for row in REGISTRY['rows'] if row['input_format']=='bib' and row['source_field']==limitation['field']]
            if paths and any(path in result['corrected_fields'] for path in paths):
                continue
            if limitation not in result['limitations']:
                result['limitations'].append(limitation)
    from refs.adapters.bibtex import original_facts
    raw_entries = connection.execute("SELECT DISTINCT raw_bytes FROM originals WHERE source_id=? AND format='bib'", (source_id,))
    preserved = {'howpublished' for raw, in raw_entries for entry in original_facts(raw) if entry['howpublished']}
    for field in sorted(preserved):
        if not any(item['field'] == field for item in result['limitations']):
            result['limitations'].append(dict(field=field, reason=f'Preserved from import: {field}'))
    from refs.resources import inventory
    result["resources"] = inventory(connection, source_id)
    result["projects"] = [dict(row) for row in connection.execute("SELECT p.id, p.name FROM projects p JOIN project_sources ps ON ps.project_id=p.id WHERE ps.source_id=? AND ps.cited=1 ORDER BY p.name", (source_id,))]
    result['links'] = linked_sources(connection, source_id)
    return result


def linked_sources(connection, source_id: str) -> list[dict]:
    rows = connection.execute(
        "SELECT DISTINCT s.id, s.citation_key, s.metadata_json, s.state "
        "FROM sources s JOIN source_relations r ON (r.source_id=? AND r.target_id=s.id) "
        "OR (r.target_id=? AND r.source_id=s.id) ORDER BY s.citation_key", (source_id, source_id))
    links = []
    for row in rows:
        link = dict(row)
        link['title'] = json.loads(link.pop('metadata_json')).get('title')
        links.append(link)
    return links


def change_link(catalog: Path, reference: str, other: str, revision: int | None = None, *, unlink: bool = False, dry_run: bool = False) -> dict:
    with connect(catalog, write=not dry_run) as connection:
        current = checked_record(connection, reference, revision)
        target = record(connection, resolve(connection, other))
        if current['id'] == target['id']:
            raise RefError('invalid_link', 'Link two different sources', 2)
        exists = any(link['id'] == target['id'] for link in current['links'])
        if exists != unlink:
            return current | {'unchanged': True}
        links = [link for link in current['links'] if link['id'] != target['id']]
        if not unlink:
            links.append(dict(id=target['id'], citation_key=target['citation_key'], title=target['metadata'].get('title'), state=target['state']))
        if dry_run:
            return current | {'links': sorted(links, key=lambda link: link['citation_key']), 'dry_run': True}
        revisions = {source['id']: source['revision'] for source in (current, target)}
        action_log.log_mutation('source.unlink' if unlink else 'source.link',
                                {'id': current['id'], 'citation_key': current['citation_key'], 'other_id': target['id']},
                                {'revisions': revisions}, {'revisions': {key: value + 1 for key, value in revisions.items()}},
                                changes={'linked': {'old': exists, 'new': not unlink}})
        if unlink:
            connection.execute('DELETE FROM source_relations WHERE (source_id=? AND target_id=?) OR (source_id=? AND target_id=?)',
                               (current['id'], target['id'], target['id'], current['id']))
        else:
            connection.execute('INSERT INTO source_relations VALUES (?,?,?,?)', (current['id'], 'urn:uuid:' + target['id'], target['id'], 'refs'))
        for source_id, old_revision in revisions.items():
            updated = connection.execute('UPDATE sources SET revision=revision+1, updated_at=? WHERE id=? AND revision=?',
                                         (datetime.now(UTC).isoformat(), source_id, old_revision))
            if updated.rowcount != 1:
                raise RefError('stale_revision', 'Reload the source and use its current revision', details={'expected': old_revision})
        changed(connection)
        return record(connection, current['id'])


def resolve(connection, reference: str) -> str:
    matches = connection.execute("SELECT id FROM sources WHERE id=? OR citation_key=?", (reference, reference)).fetchall()
    if len(matches) != 1:
        raise RefError("source_ambiguous" if matches else "source_missing",
                       "Use one exact source ID or citation key", details={"reference": reference})
    return matches[0]["id"]


def show(catalog: Path, reference: str) -> dict:
    with connect(catalog) as connection:
        return record(connection, resolve(connection, reference))


def bindings(source: SourceCreate) -> list[tuple[str, str, str]]:
    return list(dict.fromkeys(
        (identity.namespace, identity.library_uri, identity.item_key)
        for entry in source.provenance
        if (identity := entry.source_identity) is not None
        and identity.namespace is not None and identity.library_uri is not None and identity.item_key is not None
    ))


def allocate_key(connection, source: SourceCreate, policy: dict | None = None, *, warnings: list[dict] | None = None) -> dict:
    if source.citation_key is not None:
        return dict(origin='supplied', policy=None, table_version=None, unicode_version=None)
    base, index = naming.key(source.canonical(), policy, warnings=warnings), 0
    while connection.execute('SELECT 1 FROM sources WHERE citation_key=?', (base + naming.suffix(index),)).fetchone():
        index += 1
    source.citation_key = SourceCreate.valid_key(base + naming.suffix(index))
    return naming.provenance(policy)


def add(catalog: Path, raw: bytes, locator: str, **options) -> dict:
    result = _add(catalog,raw,locator,**options)
    if result['outcome'] == 'needs_attention':
        raise RefError('identity_conflict', 'Inspect differing incoming values and use update or import reconcile', data=result, details=result['binding'] | {'source_ids':[result['id']]})
    return result


def _add(catalog: Path, raw: bytes, locator: str, *, format: str = "refs", dry_run: bool = False, policy: dict | None = None, loc: str | None = None, kind: str | None = None) -> dict:
    from refs.adapters import csl
    source, limitations = csl.parse(raw, with_limitations=True) if format == "csljson" else (parse(raw), [])
    canonical = source.canonical()
    if kind is not None:
        payload = json.loads(raw)
        if isinstance(payload, list):
            payload = payload[0]
        supplied = payload.get('metadata', {}) if format == 'refs' else payload
        if 'type' not in supplied:
            canonical['metadata'].pop('type')
        canonical = kinds.assign(canonical, kind)
    normalized, warnings = naming.normalize(canonical,policy)
    source = SourceCreate.model_validate(normalized)
    with connect(catalog, write=not dry_run) as connection:
        try:
            from refs.importing import bind_and_fill, preserve, save_add_conflict
            existing, binding = bind_and_fill(connection, source, raw, dry_run=dry_run, origin="add")
        except RefError as exc:
            if exc.issue['code'] == 'log_unwritable':
                raise
            exc.data = dict(outcome="needs_attention", id=None, citation_key=source.citation_key)
            raise
        if existing:
            if not dry_run and not connection.execute('SELECT 1 FROM originals WHERE source_id=? AND sha256=?', (existing,hashlib.sha256(raw).hexdigest())).fetchone():
                preserve(connection,raw,locator,hashlib.sha256(raw).hexdigest(),source_id=existing,format=format,origin='import-capture',definitions={'incoming_key':source.citation_key,'limitations':limitations})
            current = record(connection,existing)
            warnings.extend(kinds.warnings(current))
            if binding['conflicts']:
                if not dry_run:
                    original = preserve(connection,raw,locator,hashlib.sha256(raw).hexdigest(),source_id=existing,format=format,origin='import-capture',definitions={'incoming_key':source.citation_key,'limitations':limitations})
                    save_add_conflict(connection,raw,locator,dict(status='conflict',source_id=existing,citation_key=current['citation_key'],binding=binding,conflicts=[item['path'] for item in binding['conflicts']],incoming=source.canonical(),original_ref=original))
                return current | dict(outcome='needs_attention', binding=binding, warnings=warnings, dry_run=dry_run)
            current = set_loc(connection, current, loc, dry_run=dry_run)
            return current | dict(unchanged=not binding['filled'], dry_run=dry_run, outcome='already_present', warnings=warnings, binding=binding)
        likely = [dict(row) for row in connection.execute(
            "SELECT id, citation_key FROM sources WHERE lower(json_extract(metadata_json, '$.title'))=lower(?)",
            (source.metadata.title,))]
        if likely:
            warnings.append(notice('likely_match', 'Similar title found; created separately because title alone is not identity', details={'candidates': likely}))
        warnings.extend(kinds.warnings(normalized))
        key_provenance = allocate_key(connection, source, policy, warnings=warnings)
        if dry_run:
            if loc is not None and source.loc is None:
                source.loc = loc
            return dict(dry_run=True, outcome="created", id=None, citation_key=source.citation_key,
                        record=source.canonical() | {'kind': kinds.identify(source.canonical())}, kind=kinds.identify(source.canonical()), key_provenance=key_provenance, warnings=warnings, limitations=limitations)
        if loc is not None and source.loc is None:
            source.loc = loc
        return insert_source(connection, source, raw, locator, format=format, warnings=warnings, key_provenance=key_provenance, limitations=limitations)


def set_loc(connection, current: dict, loc: str | None, *, dry_run: bool = False) -> dict:
    if loc is None or current.get('loc'):
        return current
    if dry_run:
        return current | {'loc': loc}
    canonical = editable(current) | {'loc': loc}
    return store_record(connection, current, revalidate(canonical), current['corrected_fields'])


def insert_source(connection, source: SourceCreate, raw: bytes, locator: str, *, format: str, warnings: list, key_provenance: dict, limitations: list | None = None) -> dict:
    fingerprint = hashlib.sha256(raw).hexdigest()
    source_id = str(uuid4())
    now = datetime.now(UTC).isoformat()
    details = source.canonical()
    metadata = details.pop("metadata")
    details.pop("citation_key")
    loc = details.pop("loc", None)
    action_log.log_mutation('source.create', {'id':source_id,'citation_key':source.citation_key}, None,
                            {'revision':1}, changes={'record':{'old':None,'new':source.canonical()}},
                            original={'sha256':fingerprint,'byte_length':len(raw),'format':format,'locator':locator})
    try:
        connection.execute(
            "INSERT INTO sources (id, citation_key, created_at, updated_at, metadata_json, details_json, key_provenance_json, loc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (source_id, source.citation_key, now, now, json.dumps(metadata), json.dumps(details),
             json.dumps(key_provenance), loc))
    except sqlite3.IntegrityError as exc:
        if 'sources.citation_key' in str(exc):
            raise RefError('key_conflict','Citation key is already reserved') from exc
        raise
    connection.execute(
        "INSERT INTO originals (id, source_id, raw_bytes, sha256, byte_length, format, origin, file_digest, locator, definitions_json) VALUES (?, ?, ?, ?, ?, ?, 'add', ?, ?, ?)",
        (str(uuid4()), source_id, raw, fingerprint, len(raw), format, fingerprint, locator, json.dumps({'limitations':limitations or []})))
    for binding in bindings(source):
        connection.execute("INSERT INTO origin_identities VALUES (?, ?, ?, ?, ?)", (*binding, source_id, fingerprint))
    refresh(connection, record(connection, source_id))
    changed(connection)
    return record(connection, source_id) | {"outcome": "created", "warnings": warnings}

def checked_record(connection, reference: str, revision: int | None) -> dict:
    current = record(connection, resolve(connection, reference))
    if revision is not None and revision != current['revision']:
        raise RefError('stale_revision', 'Reload the source and use its current revision',
                       details={'expected': revision, 'actual': current['revision']})
    return current


def store_record(connection, current: dict, canonical: dict, corrections: list[str]) -> dict:
    details = dict(canonical)
    metadata = details.pop('metadata')
    details.pop('citation_key', None)
    loc = details.pop('loc', None)
    action_log.log_mutation('source.update', {'id':current['id'],'citation_key':current['citation_key']},
                            {'revision':current['revision']}, {'revision':current['revision']+1}, changes=action_log.changes(editable(current),canonical))
    updated = connection.execute('UPDATE sources SET metadata_json=?, details_json=?, loc=?, corrected_fields_json=?, updated_at=?, revision=revision+1 WHERE id=? AND revision=?',
                                 (json.dumps(metadata), json.dumps(details), loc, json.dumps(corrections), datetime.now(UTC).isoformat(), current['id'], current['revision']))
    if updated.rowcount != 1:
        raise RefError('stale_revision','Reload the source and use its current revision',details={'expected':current['revision']})
    refresh(connection, record(connection, current['id']))
    changed(connection)
    return record(connection, current['id'])


def patch_path(value: dict, path: str, replacement, *, clear: bool) -> None:
    from typing import get_args

    from refs.models import Date, Metadata
    parts = path.split('.')
    dates = {field.alias or name for name,field in Metadata.model_fields.items() if Date in get_args(field.annotation)}
    date_members = {field.alias or name for name,field in Date.model_fields.items()}
    date_member = len(parts)==3 and parts[1] in dates and parts[2] in date_members
    if parts[0] in ('context', 'provenance', 'legacy_tags') and len(parts) != 1:
        raise RefError('invalid_patch', 'Replace arrays as a whole', 2)
    if parts[0] == 'metadata' and len(parts) > 2 and not date_member:
        raise RefError('invalid_patch', 'Unknown metadata path', 2)
    if parts[0] == 'metadata' and len(parts) == 2:
        probe = deepcopy(value)
        probe.setdefault('metadata', {})[parts[1]] = '__validate_path__'
        try:
            SourceCreate.model_validate(probe)
        except ValidationError as exc:
            if any(item['type'] == 'extra_forbidden' for item in exc.errors()):
                raise RefError('invalid_patch', 'Unknown metadata path', 2) from exc
    node = value
    for part in parts[:-1]:
        if part not in node:
            node[part] = {}
        if not isinstance(node[part], dict):
            raise RefError('invalid_patch', 'Patch path crosses a scalar or array', 2)
        node = node[part]
    if clear:
        if parts[-1] not in node:
            # Validate absent clear paths rather than accepting arbitrary names.
            probe = deepcopy(value)
            patch_path(probe, path, '__validate_path__', clear=False)
            try:
                SourceCreate.model_validate(probe)
            except ValidationError as exc:
                if any(item['type'] == 'extra_forbidden' for item in exc.errors()):
                    raise RefError('invalid_patch', 'Unknown clear path', 2) from exc
        node.pop(parts[-1], None)
    else:
        node[parts[-1]] = replacement


def update(catalog: Path, reference: str, patch: dict, revision: int | None = None, *, dry_run: bool = False, policy: dict | None = None, kind: str | None = None) -> dict:
    from refs.models import SourcePatch
    try:
        patch_model = SourcePatch.model_validate(patch)
    except ValidationError as exc:
        raise RefError('invalid_patch', 'Patch does not match the supported record profile', 2, details={'issues':exc.errors(include_url=False,include_context=False,include_input=False)}) from exc
    with connect(catalog, write=not dry_run) as connection:
        current = checked_record(connection, reference, revision)
        canonical = editable(current)
        original = deepcopy(canonical)
        for path, value in patch_model.set.items():
            patch_path(canonical, path, value, clear=False)
        for path in patch_model.clear:
            patch_path(canonical, path, None, clear=True)
        if kind is not None:
            canonical = kinds.assign(canonical, kind)
        if patch_model.provenance:
            canonical.setdefault('provenance', []).extend(item.model_dump(exclude_none=True) for item in patch_model.provenance)
        try:
            canonical = revalidate(canonical)
            title_fields={field for field in canonical['metadata'] if 'metadata' in patch_model.set or 'metadata.'+field in patch_model.set}
            dropped_terms = []
            for field in list(canonical['title_protection']):
                supplied = any(path == 'title_protection' or path == 'title_protection.'+field or path.startswith('title_protection.'+field+'.') for path in patch_model.set)
                if supplied:
                    title_fields.add(field)
                elif original['metadata'].get(field) != canonical['metadata'].get(field):
                    protection = canonical['title_protection'][field]
                    dropped_terms.extend((field, term) for term in protection['protected_terms'] if not naming.protected_spans(canonical['metadata'].get(field, ''), [term]))
                    protection['protected_terms'] = [term for term in protection['protected_terms'] if naming.protected_spans(canonical['metadata'].get(field, ''), [term])]
            canonical, warnings = naming.normalize(canonical,policy,title_fields)
            if dropped_terms:
                names = ', '.join(f'{field}: {term}' for field, term in dropped_terms)
                warnings.append(notice('protected_terms_dropped', f'Protected terms no longer in the edited title were dropped: {names}', path='title_protection', details={'terms':[{'field':field,'term':term} for field,term in dropped_terms]}))
            canonical = revalidate(canonical)
        except ValidationError as exc:
            raise RefError('invalid_patch', 'Patch does not match the supported record profile', 2, details={'issues':exc.errors(include_url=False,include_context=False,include_input=False)}) from exc
        if canonical == original:
            return current | {'unchanged': True, 'warnings': warnings}
        kind_paths = set(kinds.row(kind)['fields']) | {'metadata.type'} if kind else set()
        corrections = sorted(set(current['corrected_fields']) | (set(patch_model.set) | set(patch_model.clear) | kind_paths) - {'loc'})
        if dry_run:
            preview = {field: value for field, value in current.items() if field not in SourceCreate.model_fields}
            return preview | canonical | dict(kind=kinds.identify(canonical), dry_run=True, corrected_fields=corrections, warnings=warnings)
        return store_record(connection, current, canonical, corrections) | {'warnings': warnings}


def _change_identity(connection, current: dict, field: str, value: str, event: str, warnings: list[dict], execute: bool) -> dict:
    if current[field] == value:
        return current | dict(unchanged=True, warnings=warnings)
    if not execute:
        return current | {field: value, 'dry_run': True, 'warnings': warnings}
    action_log.log_mutation(event, {'id':current['id'],'citation_key':current['citation_key']},
                            {'revision':current['revision']}, {'revision':current['revision']+1},
                            changes={field:{'old':current[field],'new':value}})
    # Column names are internal constants, never user paths.
    try:
        updated = connection.execute(f'UPDATE sources SET {field}=?, revision=revision+1, updated_at=? WHERE id=? AND revision=?',
                                     (value, datetime.now(UTC).isoformat(), current['id'],current['revision']))
    except sqlite3.IntegrityError as exc:
        if field == 'citation_key' and 'sources.citation_key' in str(exc):
            raise RefError('key_conflict','Citation key is already reserved') from exc
        raise
    if updated.rowcount != 1:
        raise RefError('stale_revision','Reload the source and use its current revision',details={'expected':current['revision']})
    if field == 'citation_key':
        connection.execute('UPDATE sources SET key_provenance_json=? WHERE id=?', (json.dumps({'origin': 'explicit_rekey'}), current['id']))
    refresh(connection, record(connection, current['id']))
    changed(connection)
    return record(connection, current['id']) | {'warnings': warnings} | ({'previous_key': current['previous_key']} if field == 'citation_key' else {})


def rekey(catalog: Path, reference: str, revision: int, new_key: str, *, execute: bool = False) -> dict:
    with connect(catalog, write=execute) as connection:
        current = checked_record(connection, reference, revision)
        current['previous_key'] = current['citation_key']
        try:
            SourceCreate.valid_key(new_key)
        except ValueError as exc:
            raise RefError('invalid_key', str(exc), 2) from exc
        if not new_key.strip():
            raise RefError('invalid_key', 'Citation key cannot be blank', 2)
        occupied = connection.execute('SELECT id FROM sources WHERE citation_key=? AND id<>?', (new_key, current['id'])).fetchone()
        if occupied:
            raise RefError('key_conflict', 'Citation key is already reserved')
        warnings = [notice('external_citations_unchanged', 'External citations are not rewritten')]
        return _change_identity(connection, current, 'citation_key', new_key, 'source.key_set', warnings, execute)


def set_state(catalog: Path, reference: str, revision: int | None, state: str, *, execute: bool = False) -> dict:
    with connect(catalog, write=execute) as connection:
        if revision is None and state != 'active':
            raise RefError('revision_required', 'Supply the current revision', 2)
        current = record(connection, resolve(connection, reference)) if revision is None else checked_record(connection, reference, revision)
        event = 'source.remove' if state == 'removed' else 'source.reactivate'
        return _change_identity(connection, current, 'state', state, event, [], execute)
