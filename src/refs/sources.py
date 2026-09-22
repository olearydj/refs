"""Capture services preserve original evidence and never merge a candidate."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from refs import naming
from refs.adapters.search_sqlite import refresh
from refs.catalog import changed, connect
from refs.models import REGISTRY, SourceCreate, parse
from refs.results import RefError


def record(connection, source_id: str) -> dict:
    row = connection.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()
    if row is None:
        raise RefError("source_missing", "Source was not found")
    value = dict(row)
    result = json.loads(value.pop("details_json")) | value
    result["metadata"] = json.loads(result.pop("metadata_json"))
    result["corrected_fields"] = json.loads(result.pop("corrected_fields_json"))
    result["key_provenance"] = json.loads(result.pop("key_provenance_json"))
    result["originals"] = [dict(r) for r in connection.execute(
        "SELECT id, sha256, byte_length, format, origin, locator FROM originals WHERE source_id=? ORDER BY id",
        (source_id,))]
    result['limitations'] = []
    for original in connection.execute("SELECT definitions_json FROM originals WHERE source_id=? AND origin LIKE 'import-%'", (source_id,)):
        for limitation in json.loads(original[0]).get('limitations', []):
            paths = [row['canonical_path'] for row in REGISTRY['rows'] if row['input_format']=='bib' and row['source_field']==limitation['field']]
            if paths and any(path in result['corrected_fields'] for path in paths):
                continue
            if limitation not in result['limitations']:
                result['limitations'].append(limitation)
    result["resources"] = []
    result["projects"] = [dict(row) for row in connection.execute("SELECT p.id, p.name FROM projects p JOIN project_sources ps ON ps.project_id=p.id WHERE ps.source_id=? AND ps.cited=1 ORDER BY p.name", (source_id,))]
    return result


def resolve(connection, reference: str) -> str:
    matches = connection.execute("SELECT id FROM sources WHERE id=? OR citation_key=?", (reference, reference)).fetchall()
    if len(matches) != 1:
        raise RefError("source_ambiguous" if matches else "source_missing",
                       "Use one exact source ID or citation key", details={"reference": reference})
    return matches[0]["id"]


def show(catalog: Path, reference: str) -> dict:
    with connect(catalog) as connection:
        return record(connection, resolve(connection, reference))


def doi_identity(value: str) -> str:
    value = value.strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            return value[len(prefix):].strip()
    return value


def bindings(source: SourceCreate) -> list[tuple[str, str, str]]:
    return list(dict.fromkeys(
        (identity.namespace, identity.library_uri, identity.item_key)
        for entry in source.provenance
        if (identity := entry.source_identity) is not None
        and identity.namespace is not None and identity.library_uri is not None and identity.item_key is not None
    ))


def candidate(connection, source: SourceCreate, fingerprint: str) -> str | None:
    ids = {r["id"] for r in connection.execute("SELECT id FROM sources WHERE citation_key=?", (source.citation_key,))}
    ids.update(r[0] for r in connection.execute("SELECT source_id FROM originals WHERE sha256=? AND source_id IS NOT NULL", (fingerprint,)))
    for binding in bindings(source):
        row = connection.execute("SELECT source_id FROM origin_identities WHERE namespace=? AND library_uri=? AND item_key=?", binding).fetchone()
        if row:
            ids.add(row["source_id"])
    if source.metadata.DOI:
        for row in connection.execute("SELECT id, metadata_json FROM sources"):
            doi = json.loads(row["metadata_json"]).get("DOI")
            if doi and doi_identity(doi) == doi_identity(source.metadata.DOI):
                ids.add(row["id"])
    if not ids:
        return None
    if len(ids) == 1:
        source_id = next(iter(ids))
        state = connection.execute("SELECT state FROM sources WHERE id=?", (source_id,)).fetchone()[0]
        if state == "removed":
            raise RefError("source_removed", "Matched source is removed", details={"source_id": source_id})
        prior = connection.execute("SELECT 1 FROM originals WHERE source_id=? AND sha256=?", (source_id, fingerprint)).fetchone()
        if prior:
            return source_id
    raise RefError("identity_conflict", "Input matches existing identity evidence; inspect it before creating another source",
                   details={"source_ids": sorted(ids)})


def add(catalog: Path, raw: bytes, locator: str, *, format: str = "refs", dry_run: bool = False) -> dict:
    from refs.adapters import csl
    source = csl.parse(raw) if format == "csljson" else parse(raw)
    normalized, warnings = naming.normalize(source.canonical())
    source = SourceCreate.model_validate(normalized)
    fingerprint = hashlib.sha256(raw).hexdigest()
    with connect(catalog, write=not dry_run) as connection:
        try:
            existing = candidate(connection, source, fingerprint)
        except RefError as exc:
            exc.data = dict(outcome="needs_attention", id=None, citation_key=source.citation_key)
            raise
        if existing:
            return record(connection, existing) | {"unchanged": True, "dry_run": dry_run, "outcome": "already_present", "warnings": warnings}
        likely = [dict(row) for row in connection.execute(
            "SELECT id, citation_key FROM sources WHERE lower(json_extract(metadata_json, '$.title'))=lower(?)",
            (source.metadata.title,))]
        if likely:
            raise RefError("likely_match", "A source has this title; inspect the candidates", details={"candidates": likely},
                           data=dict(outcome="needs_attention", id=None, citation_key=source.citation_key))
        key_provenance = {"origin": "supplied", "policy": None, "table_version": None, "unicode_version": None}
        if source.citation_key is None:
            base = naming.key(source.canonical())
            index = 0
            while connection.execute("SELECT 1 FROM sources WHERE citation_key=?", (base + naming.suffix(index),)).fetchone():
                index += 1
            source.citation_key = SourceCreate.valid_key(base + naming.suffix(index))
            key_provenance = naming.provenance()
        if dry_run:
            return dict(dry_run=True, outcome="created", id=None, citation_key=source.citation_key,
                        record=source.canonical(), key_provenance=key_provenance, warnings=warnings)
        return insert_source(connection, source, raw, locator, format=format, warnings=warnings, key_provenance=key_provenance)


def insert_source(connection, source: SourceCreate, raw: bytes, locator: str, *, format: str, warnings: list, key_provenance: dict) -> dict:
    fingerprint = hashlib.sha256(raw).hexdigest()
    source_id = str(uuid4())
    now = datetime.now(UTC).isoformat()
    details = source.canonical()
    metadata = details.pop("metadata")
    details.pop("citation_key")
    connection.execute(
        "INSERT INTO sources (id, citation_key, created_at, updated_at, metadata_json, details_json, key_provenance_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (source_id, source.citation_key, now, now, json.dumps(metadata), json.dumps(details),
         json.dumps(key_provenance)))
    connection.execute(
        "INSERT INTO originals (id, source_id, raw_bytes, sha256, byte_length, format, origin, file_digest, locator) VALUES (?, ?, ?, ?, ?, ?, 'add', ?, ?)",
        (str(uuid4()), source_id, raw, fingerprint, len(raw), format, fingerprint, locator))
    for binding in bindings(source):
        connection.execute("INSERT INTO origin_identities VALUES (?, ?, ?, ?, ?)", (*binding, source_id, fingerprint))
    refresh(connection, record(connection, source_id))
    changed(connection)
    return record(connection, source_id) | {"outcome": "created", "warnings": warnings}

def checked_record(connection, reference: str, revision: int) -> dict:
    current = record(connection, resolve(connection, reference))
    if revision != current['revision']:
        raise RefError('stale_revision', 'Reload the source and use its current revision',
                       details={'expected': revision, 'actual': current['revision']})
    return current


def store_record(connection, current: dict, canonical: dict, corrections: list[str]) -> dict:
    details = dict(canonical)
    metadata = details.pop('metadata')
    details.pop('citation_key', None)
    connection.execute('UPDATE sources SET metadata_json=?, details_json=?, corrected_fields_json=?, updated_at=?, revision=revision+1 WHERE id=? AND revision=?',
                       (json.dumps(metadata), json.dumps(details), json.dumps(corrections), datetime.now(UTC).isoformat(), current['id'], current['revision']))
    refresh(connection, record(connection, current['id']))
    changed(connection)
    return record(connection, current['id'])


def patch_path(value: dict, path: str, replacement, *, clear: bool) -> None:
    from refs.models import REGISTRY
    parts = path.split('.')
    if parts[0] in ('context', 'provenance', 'legacy_tags') and len(parts) != 1:
        raise RefError('invalid_patch', 'Replace arrays as a whole', 2)
    if parts[0] == 'metadata' and (len(parts) > 2 or len(parts) == 2 and parts[1] not in REGISTRY['core_fields']):
        raise RefError('invalid_patch', 'Unknown metadata path', 2)
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
            probe = json.loads(json.dumps(value))
            patch_path(probe, path, '__validate_path__', clear=False)
            try:
                SourceCreate.model_validate(probe)
            except ValidationError as exc:
                if any(item['type'] == 'extra_forbidden' for item in exc.errors()):
                    raise RefError('invalid_patch', 'Unknown clear path', 2) from exc
        node.pop(parts[-1], None)
    else:
        node[parts[-1]] = replacement


def update(catalog: Path, reference: str, patch: dict, revision: int, *, dry_run: bool = False) -> dict:
    from refs.models import SourcePatch
    try:
        patch_model = SourcePatch.model_validate(patch)
    except ValidationError as exc:
        raise RefError('invalid_patch', str(exc), 2) from exc
    with connect(catalog, write=not dry_run) as connection:
        current = checked_record(connection, reference, revision)
        canonical = {name: current[name] for name in SourceCreate.model_fields if name in current}
        original = json.loads(json.dumps(canonical))
        for path, value in patch_model.set.items():
            patch_path(canonical, path, value, clear=False)
        for path in patch_model.clear:
            patch_path(canonical, path, None, clear=True)
        if patch_model.provenance:
            canonical.setdefault('provenance', []).extend(item.model_dump(exclude_none=True) for item in patch_model.provenance)
        try:
            canonical = SourceCreate.model_validate(canonical).canonical()
            canonical, warnings = naming.normalize(canonical)
            canonical = SourceCreate.model_validate(canonical).canonical()
        except ValidationError as exc:
            raise RefError('invalid_patch', str(exc), 2) from exc
        if canonical == original:
            return current | {'unchanged': True, 'warnings': warnings}
        corrections = sorted(set(current['corrected_fields']) | set(patch_model.set) | set(patch_model.clear))
        if dry_run:
            return current | canonical | dict(dry_run=True, corrected_fields=corrections, warnings=warnings)
        return store_record(connection, current, canonical, corrections) | {'warnings': warnings}


def change_identity(catalog: Path, reference: str, revision: int, *, new_key: str | None = None,
                    state: str | None = None, execute: bool = False) -> dict:
    with connect(catalog, write=execute) as connection:
        current = checked_record(connection, reference, revision)
        warnings = []
        if new_key is not None:
            try:
                SourceCreate.valid_key(new_key)
            except ValueError as exc:
                raise RefError('invalid_key', str(exc), 2) from exc
            if not new_key.strip():
                raise RefError('invalid_key', 'Citation key cannot be blank', 2)
            occupied = connection.execute('SELECT id FROM sources WHERE citation_key=? AND id<>?', (new_key, current['id'])).fetchone()
            if occupied:
                raise RefError('key_conflict', 'Citation key is already reserved')
            field, value = 'citation_key', new_key
            warnings = [{'code': 'external_citations_unchanged', 'message': 'External citations are not rewritten', 'path': None, 'details': {}, 'retryable': False}]
        else:
            field, value = 'state', state
        if current[field] == value:
            return current | dict(unchanged=True, warnings=warnings)
        if not execute:
            return current | {field: value, 'dry_run': True, 'warnings': warnings}
        # Column names are internal constants, never user paths.
        connection.execute(f'UPDATE sources SET {field}=?, revision=revision+1, updated_at=? WHERE id=?', (value, datetime.now(UTC).isoformat(), current['id']))
        if new_key is not None:
            connection.execute('UPDATE sources SET key_provenance_json=? WHERE id=?', (json.dumps({'origin': 'explicit_rekey'}), current['id']))
        refresh(connection, record(connection, current['id']))
        changed(connection)
        return record(connection, current['id']) | {'warnings': warnings}
