"""Portable article projection and explicit, recoverable export."""

import re
import sqlite3
import unicodedata
from contextlib import nullcontext
from pathlib import Path

from pydantic import ValidationError

from refs import files, projects, sources
from refs.catalog import changed, connect
from refs.models import SourceCreate
from refs.results import RefError

PROFILE = "portable-bibtex-v1"
PROFILE_FINGERPRINT = files.digest(PROFILE.encode())
TEX_ESCAPES = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def tex(value: str) -> str:
    if any(ord(char) < 32 and char not in "\n\t" for char in value):
        raise RefError("invalid_export_value", "Control characters cannot be exported")
    return "".join(TEX_ESCAPES.get(char, char) for char in value)


def title(value: str, protection: dict) -> str:
    value = unicodedata.normalize("NFC", value)
    if protection.get("preserve_case"):
        return "{" + tex(value) + "}"
    terms = sorted({unicodedata.normalize("NFC", term) for term in protection.get("protected_terms", [])}, key=lambda term: (-len(term), term))
    if not terms:
        return tex(value)
    pattern = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(term) for term in terms) + r")(?!\w)")
    parts, end = [], 0
    for match in pattern.finditer(value):
        parts.extend([tex(value[end:match.start()]), "{" + tex(match.group()) + "}"])
        end = match.end()
    return "".join(parts) + tex(value[end:])


def warning(key: str, code: str, message: str, **details) -> dict:
    return dict(code=code, message=message, path=None, details={"citation_key": key, **details}, retryable=False)


def serialize(records: list[dict]) -> tuple[bytes, list[dict]]:
    entries, warnings, errors = [], [], []
    seen = set()
    for record in sorted(records, key=lambda row: row["citation_key"]):
        key = record["citation_key"]
        if key.casefold() in seen:
            errors.append(dict(citation_key=key, code="case_colliding_key"))
        seen.add(key.casefold())
        # Revalidate stored values: unknown facts never disappear during export.
        create = {name: record[name] for name in SourceCreate.model_fields if name in record}
        try:
            value = SourceCreate.model_validate(create).canonical()
            metadata = value["metadata"]
            protection = value["title_protection"]
            fields = []
            if metadata.get("author"):
                names = ["{" + tex(name["literal"]) + "}" if "literal" in name
                         else tex(name["family"]) + (", " + tex(name["given"]) if "given" in name else "")
                         for name in metadata["author"]]
                fields.append(("author", " and ".join(names)))
            else:
                warnings.append(warning(key, "missing_author", "No author was supplied"))
            fields.append(("title", title(metadata["title"], protection.get("title", {}))))
            if "container-title" in metadata:
                fields.append(("journal", title(metadata["container-title"], protection.get("container-title", {}))))
            else:
                warnings.append(warning(key, "missing_journal", "No journal was supplied"))
            if "issued" in metadata:
                fields.append(("year", str(metadata["issued"]["date-parts"][0][0])))
            else:
                warnings.append(warning(key, "missing_issued", "No issued year was supplied"))
            for source, target in (("volume", "volume"), ("issue", "number"), ("page", "pages")):
                if source in metadata:
                    text = metadata[source]
                    if source == "page":
                        text = re.sub(r"(?<=\d)[-–](?=\d)", "--", text)
                    fields.append((target, tex(text)))
            # These URI fields retain literal bytes, without generic TeX decoding.
            for source, target in (("DOI", "doi"), ("URL", "url")):
                if source in metadata:
                    text = metadata[source]
                    if re.search(r"[{}\\\s\x00-\x1f\x7f]", text):
                        raise RefError("invalid_export_value", "URI contains unsafe characters")
                    fields.append((target, text))
            entries.append("@article{" + key + ",\n" + "".join(f"  {name} = {{{text}}},\n" for name, text in fields) + "}\n")
        except (ValidationError, RefError) as exc:
            errors.append(dict(citation_key=key, code="unsupported_record", message=str(exc)))
    if errors:
        raise RefError("export_blocked", "All unsupported entries must be corrected before export", details={"entries": errors})
    return "\n".join(entries).encode("utf-8"), warnings


def target_state(connection, target: Path, project_id: str) -> tuple[str | None, bool, bool]:
    row = connection.execute("SELECT * FROM export_targets WHERE destination=?", (str(target),)).fetchone()
    current = files.current_digest(target)
    if row is None:
        if current is not None:
            raise RefError("unadopted_target", "Existing bibliography has not been adopted", path=str(target))
        return None, False, False
    if row["project_id"] != project_id or row["profile_fingerprint"] != PROFILE_FINGERPRINT:
        raise RefError("target_binding_conflict", "Destination belongs to another project or profile", path=str(target))
    if current is not None and current == row["baseline_digest"]:
        return current, False, True
    if current is not None and current == row["pending_digest"]:
        return current, True, True
    if current is None and row["baseline_digest"] is None:
        return None, False, True
    raise RefError("outside_edit", "Destination differs from recorded export bytes", path=str(target))


def finish_export(catalog: Path, target: Path, digest: str) -> None:
    with connect(catalog, write=True) as connection:
        count = connection.execute(
            "UPDATE export_targets SET baseline_digest=?, pending_digest=NULL WHERE destination=? AND pending_digest=?",
            (digest, str(target), digest)).rowcount
        if count != 1:
            raise RefError("export_intent_conflict", "Recorded export intent changed", 5)
        changed(connection)


def export(catalog: Path, project_ref: str, output: Path, *, profile: str = PROFILE, dry_run: bool = False) -> dict:
    if profile != PROFILE:
        raise RefError("unsupported_profile", "This milestone supports portable-bibtex-v1", 2)
    target = files.destination(output)
    with connect(catalog) as connection:
        project = projects.resolve(connection, project_ref)
        selected = [sources.record(connection, row[0]) for row in connection.execute(
            "SELECT s.id FROM sources s JOIN project_sources ps ON s.id=ps.source_id WHERE ps.project_id=? AND ps.cited=1 AND s.state='active' ORDER BY s.citation_key",
            (project["id"],))]
        revision = connection.execute("SELECT revision FROM catalog_meta").fetchone()[0]
    data, warnings = serialize(selected)
    candidate_digest = files.digest(data)
    result = dict(output=str(target), profile=profile, count=len(selected),
                  keys=[record["citation_key"] for record in selected], sha256=candidate_digest,
                  catalog_revision=revision, warnings=warnings)
    # Preview never acquires the file lock, stages bytes or reconciles intent.
    with nullcontext() if dry_run else files.file_lock(catalog):
        with connect(catalog) as connection:
            current, recoverable, known = target_state(connection, target, project["id"])
        if dry_run:
            return result | dict(dry_run=True, recoverable=recoverable)
        if recoverable:
            assert current is not None
            finish_export(catalog, target, current)
        if current == candidate_digest:
            return result | dict(unchanged=True, recovered=recoverable)
        with files.staged(target, data) as temporary:
            with connect(catalog, write=True) as connection:
                checked, _, _ = target_state(connection, target, project["id"])
                if checked != current:
                    raise RefError("outside_edit", "Destination changed while preparing export")
                if not known:
                    connection.execute("INSERT INTO export_targets VALUES (?, ?, ?, NULL, ?)", (str(target), project["id"], PROFILE_FINGERPRINT, candidate_digest))
                else:
                    connection.execute("UPDATE export_targets SET pending_digest=? WHERE destination=?", (candidate_digest, str(target)))
                changed(connection)
            files.publish(temporary, target, current)
            try:
                if files.current_digest(target) != candidate_digest:
                    raise RefError("integrity_error", "Published output changed", 5)
                finish_export(catalog, target, candidate_digest)
            except (OSError, sqlite3.Error, RefError) as exc:
                raise RefError("export_published_unrecorded", "Output was published; retry export to reconcile recorded intent", 4,
                               path=str(target), details={"published": True, "cause": str(exc)}) from exc
        return result | dict(unchanged=False, recovered=recoverable)
