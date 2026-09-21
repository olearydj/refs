"""Capture services preserve original evidence and never merge a candidate."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from refs.catalog import changed, connect
from refs.models import SourceCreate, parse
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
    result["resources"] = []
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


def add(catalog: Path, raw: bytes, locator: str, *, dry_run: bool = False) -> dict:
    source = parse(raw)
    fingerprint = hashlib.sha256(raw).hexdigest()
    with connect(catalog, write=not dry_run) as connection:
        existing = candidate(connection, source, fingerprint)
        if existing:
            return record(connection, existing) | {"unchanged": True, "dry_run": dry_run}
        likely = [dict(row) for row in connection.execute(
            "SELECT id, citation_key FROM sources WHERE lower(json_extract(metadata_json, '$.title'))=lower(?)",
            (source.metadata.title,))]
        if likely:
            raise RefError("likely_match", "A source has this title; inspect the candidates", details={"candidates": likely})
        if dry_run:
            return dict(dry_run=True, citation_key=source.citation_key, record=source.canonical())
        source_id = str(uuid4())
        now = datetime.now(UTC).isoformat()
        details = source.canonical()
        metadata = details.pop("metadata")
        details.pop("citation_key")
        connection.execute(
            "INSERT INTO sources (id, citation_key, created_at, updated_at, metadata_json, details_json, key_provenance_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (source_id, source.citation_key, now, now, json.dumps(metadata), json.dumps(details),
             json.dumps({"origin": "supplied", "policy": None, "table_version": None, "unicode_version": None})))
        connection.execute(
            "INSERT INTO originals (id, source_id, raw_bytes, sha256, byte_length, format, origin, file_digest, locator) VALUES (?, ?, ?, ?, ?, 'refs', 'add', ?, ?)",
            (str(uuid4()), source_id, raw, fingerprint, len(raw), fingerprint, locator))
        for binding in bindings(source):
            connection.execute("INSERT INTO origin_identities VALUES (?, ?, ?, ?, ?)", (*binding, source_id, fingerprint))
        changed(connection)
        return record(connection, source_id)
