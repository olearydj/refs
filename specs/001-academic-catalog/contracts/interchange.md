# Import, Bibliography, and Recovery Formats v1

The [bibliographic profile](bibliography.md) owns type/field coverage, projection semantics, inherited-field rules, supporting records, and fixture obligations. Its explicit rules supersede the earlier broad table below where native subtypes need finer distinctions.

## Common Preservation Rules

Every imported artifact is retained byte-for-byte with SHA-256, format, origin namespace, adapter version, and locator metadata. Parsing produces one accountable entry per record or failed raw block. Comments, strings, preambles, unknown fields, and unresolved relationships remain recoverable. Canonical normalized data never replaces original evidence. Unsupported input is visible; no library-wide lossless conversion is claimed.

`--origin` is a stable user-chosen namespace for the same upstream dataset. The same origin plus artifact digests replays its batch. A changed artifact uses recorded item identities where available, then consistent identifiers; byte identity of a different dataset does not authorize identity merging. Identical retries and per-entry revisions follow [records](records.md).

## BibTeX/BibLaTeX

Freeze the parser pipeline rather than inheriting changing defaults: parse raw blocks without middleware; identify parse failures, duplicate keys, and case-colliding field names first; then resolve supported string references and remove only the outer lexical enclosure on a separate working representation. Preserve nested protected groups before LaTeX decoding. Use pylatexenc's parser for supported text/accents and group boundaries, retaining unrecognized macros/math as original syntax with warnings. Do not lower-case fields before detecting `author`/`Author` ambiguity, and do not globally strip braces.

| Imported representation | Normalized handling / output |
| --- | --- |
| `article` | Journal article; author/editor roles, title, journal, volume/number, pages/eid, issued date, DOI, URL. |
| `book`, `inbook`, `incollection` | Book or chapter with title/container distinction, publisher/place, edition, series, pages, ordered contributor roles. Traditional BibTeX inbook is dialect-specific: its title is the book title; apply B15 rather than the BibLaTeX chapter mapping. |
| `inproceedings`, `conference` | Conference paper with booktitle, event/publication details, editors/organization and pages. |
| `online`, `software`, `misc` | Explicit webpage/software/document representation; retain native type. An ambiguous miscellaneous entry requires type review before a claim of citation fidelity. |
| `thesis`, `phdthesis`, `mastersthesis` | Thesis with subtype/genre and institution retained. |
| `patent`, `report`, `techreport`, `unpublished` | Type-specific jurisdiction/number/institution/status retained; preprint classification requires explicit evidence. |
| `author`, `editor`, additional contributor fields | Parse order and personal/literal distinctions; fully grouped corporate names remain literals. Unsupported forms retained and flagged. |
| `shorttitle`, `edition`, version/custom fields | Preserve original text; normalize only unambiguous meanings. Never treat `1.4` as fourteenth edition or split `P1E` automatically. |
| `file`, keywords, annotation/note fields | File expressions become attachment metadata/resource links only where parsed safely; keywords become legacy tags. Bibliographic note/annotation fields stay distinct from authored child notes and PDF annotations. Supporting records retain identities and parents under the bibliography contract. No moves, fetching, taxonomy promotion, or note overwrite. |
| Unknown type/field or TeX construct | Retain original and explicit limitation; do not silently manufacture a supported value. |

Supported inheritance is limited to the parent/child pairs and exact field transfers enumerated in the [bibliographic contract](bibliography.md#inheritance-macros-and-better-bibtex-extra). Child values win and inheritance retains field provenance. Other crossref/xref/xdata/custom semantics remain unresolved. Required unresolved facts block export until explicit reconciliation or verified flattening; preserving raw syntax is not usable inheritance support. A selected child does not automatically select its parent.

Output uses stable binary citation-key order and stable field order, UTF-8, and no run timestamps. BibLaTeX is the default; BibTeX output supports only representable mapped data and reports limitations. Preserve corporate grouping and technical title protection. Do not double-encode already retained TeX. Expand supported string references or emit the required deterministic definitions; undefined macros required for usable output fail visibly. Retained noncitation fields remain in the catalog even when omitted from a project bibliography, with an omission report. Export never silently omits a selected source.

## Zotero Snapshot Input

Input is a directory with `manifest.json` and preserved databases. Snapshot acquisition is separate from import and must happen with Zotero closed or an equivalently verified consistent snapshot procedure. This feature's importer does not connect to or modify a running Zotero catalog.

```json
{
  "format": "refs-zotero-snapshot",
  "version": 1,
  "captured_at": "2026-09-20T12:00:00Z",
  "quiescent": true,
  "library_identity": "local-personal-library",
  "members": [
    {"role": "zotero", "path": "zotero.sqlite", "sha256": "actual-member-sha256"},
    {"role": "better_bibtex", "path": "better-bibtex.sqlite", "sha256": "actual-member-sha256"}
  ],
  "original_locations": {"data_directory": "/original/zotero", "linked_base": "/original/documents"}
}
```

The shown digests are explanatory strings; actual inputs require 64 lowercase hexadecimal digits matching the members. Member paths must be relative, nonescaping, and regular files. Opening databases is read-only, validates integrity, and records schema/version/capability fingerprints. Admission requires the adapter's supported schema fixture matrix; unknown schemas are rejected before source application. Item identity is library identity plus Zotero item key. Better BibTeX keys are joined through verified source IDs/keys, never assumed from row ordering.

Preserve collections and ordered creator roles. Absolute paths remain absolute; `storage:` paths resolve beneath the original data directory's storage, and base-relative links beneath the original linked base. Do not point links at the snapshot's copied directory. Missing paths remain reported links. Notes, annotations and all attachment metadata are imported as structured supporting items with origin/parent identities, including URL-only or missing-file attachments. Asserted related-item links retain resolved or unresolved endpoint identities. Their inspection and full export are required; editing/rendering remain outside scope. The certified schema matrix and at least 30 representative records are release fixtures; this planning artifact does not certify a live library.

## Backup Bundle v1

```text
backup-directory/
  manifest.json
  catalog.sqlite
  config.toml
  resources.jsonl
```

Manifest fields: `format="refs-backup"`, `version=1`, `state="complete"`, catalog ID, catalog schema version, application version, created time, configuration digest, each member's relative path/hash/byte length, resource count, and `external_contents_included=false`. Original artifacts and provenance are inside the snapshot. List excluded external resources with locator, mode, and last observed availability; a link inventory is not content backup.

Unknown versions, extra undocumented executable members, path traversal, symlinks, missing hashes, and inconsistent catalog identities are rejected. Restore uses the schema migration compatibility policy. Bundle checksums verify consistency, not authenticity against a malicious author; bundles are local user-controlled inputs and no content is executed.

## Full Library Export v1

```text
library-directory/
  manifest.json
  sources.jsonl
  collections.jsonl
  resources.jsonl
  supporting-items.jsonl
  source-relations.jsonl
  bibliography-profile.json
  projects.jsonl
  memberships.jsonl
  origins.jsonl
  provenance.jsonl
  imports.jsonl
  operations.jsonl
  export-targets.jsonl
  config.toml
  originals/<sha256>
```

Manifest uses `format="refs-library"`, `version=1`, completion state, catalog identity, counts, member hashes/lengths, and external-content exclusion. Each line is one documented entity object using the field names and relationships in [data model](../data-model.md); UUIDs and order indices are retained. `memberships.jsonl` distinguishes collection/project relationships and citation selection. `imports.jsonl` includes batches/entries and unresolved outcomes. `operations.jsonl` includes durable semantic/recovery state, not transient lock files. Each source record includes state (active or removed tombstone), creators/identifiers, metadata, overrides, and policy provenance; manifests distinguish active counts from retained tombstone counts. `supporting-items.jsonl` retains notes/attachment/annotation content, formats and parent references; `source-relations.jsonl` retains asserted relationships including unresolved endpoints. `bibliography-profile.json` identifies the canonical profile and upstream pins. Every recognized native field remains in the structured source record as well as its original evidence. Original artifacts are opaque unchanged bytes with digest names, never executable scripts.

The runtime `library-export` schema describes each entity type and manifest; consumers can read the UTF-8 records and originals without refs or SQLite. Full export does not itself adopt or overwrite project bibliographies. Externally linked files and managed document-library contents remain excluded and listed. Completion is published only after counts and all references are checked.
