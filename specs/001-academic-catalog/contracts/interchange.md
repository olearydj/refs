# Input, Migration and Recovery Formats v1

## Bibliographic input in slice 1

`add --format refs|csljson|bib --input PATH` accepts a single entry; stdin is supported. CSL input is passed through the same bounded canonical validator as refs metadata; external id is origin evidence, not a catalog UUID. `import --format bib --input PATH --origin TEXT` accepts a file and records per-entry outcomes. Input accepts legacy BibTeX plus the supported BibLaTeX aliases per entry, not an assumption that a file extension proves dialect. The parser adapter remains bibtexparser==2.0.1 with a fixed raw-block pipeline; do not use its writer or default decoding middleware as semantic authority.

Retain each entry's exact bytes, its containing-file digest/locator, relevant definitions/comments and failed-block evidence. For a malformed block whose parser raw text is truncated, use independently retained original input bytes, not that truncated text. Duplicate/case-colliding fields, missing-equals absorption and embedded-entry-marker cases require adapter guards or an explicit unresolved result; never silently accept corrupted fields. No refs-owned general parser is introduced merely to bypass these defects.

Decode only supported non-verbatim text through exact-pinned pylatexenc==2.11 on a working representation. Preserve original syntax, case-protection groups and unknown commands. Never decode DOI/URL/file fields with a generic LaTeX-to-text transform. Export generates canonical values and protection; it does not round-trip old raw TeX. Unsupported commands/math retain original evidence and an unassessed-output limitation.

Only month macros are resolved natively. Arbitrary strings, concatenation, crossref/xdata and custom inheritance are preserved unresolved. An explicit external Biber/Pandoc flattening pre-step may produce a second input with tool/version and original provenance; do not implement a false subset of inheritance rules. An inbook with booktitle has a part title; without it but with chapter/pages, preserve traditional container-plus-part identification and flag interpretation in preview.

`--origin` identifies an upstream dataset. Same origin plus input digest replays outcomes. Changed input uses prior origin identities or explicitly reconciled consistent identifiers. Conflicts remain unapplied; conflict-free entries commit individually. Re-importing a refs fallback uses export projection evidence as specified in records.md, not key-only matching. Source corrections and deliberate clears always prevail until explicit reconciliation.

## One-time Zotero extraction, slice 3

The installed runtime does not depend on Zotero's SQLite layout or Better BibTeX database. A separately versioned one-time read-only extractor produces UTF-8 JSON Lines under the published `refs-zotero-input-v1` contract. Each line contains a bibliographic item with original published API-shaped item JSON, library URI, item key, raw dates plus meta.parsedDate when present, ordered creators, tags, collection keys, attachment locators, child-note originals and related endpoints. Lines identify kinds and parents; attachment/relationship-only lines may retain unresolved parent keys without fabricating a source.

Snapshot/extraction acquisition is explicit. Archive a dated full Zotero data directory outside the catalog while Zotero is closed or through a verified consistent snapshot procedure. Record archive path, hashes, application/schema/BBT versions and extractor version; do not embed the databases in refs. The observed source is Zotero 6.0.37 (userdata 121/global schema 28) with BBT 7.0.0; certify that concrete route against fixtures. Unknown layouts require another tested extractor, not silent runtime compatibility. BBT 8+ cannot be assumed to have better-bibtex.sqlite.

Resolve assigned keys from verified native/Extra/legacy BBT evidence, with disagreements reported rather than precedence hiding a conflict. All 562 observed Extra keys matched BBT in the audit, but that is a historical observation, not a universal invariant. Library/item identities remain provenance and grant no permission to update Zotero objects.

Child notes become imported searchable context after preview; store original markup and derived inert searchable text with their origin. Do not import attachment outline notes or annotation rows. Preserve simple related pairs and unresolved endpoints. URL-only attachments remain URL metadata; standalone attachments remain extractor records requiring explicit source association or reported preserved-only status. Do not create supporting_items or invent bibliographic parents. Trash and replacement/merge predicates are explicitly reported by the extractor and never silently resurrect removed items.

Imported files stay where they are. Preserve storage/base/absolute path semantics against the original data directory, not the archive copy. The 511 external files can use one named old-tree root. The user may later authorize moving the whole tree beneath lib and changing that mapping, followed by resolve checks and catalog-only filing assignment. This document authorizes no live movement.

The stale June library-wide .bib may be a slice 1 seed after explicit regeneration outside refs; it is not a verified Zotero migration. Later exact types, collections and identities require reconciliation, with keys as candidates rather than automatic merge authority.

## Snapshot v1, slice 1

A snapshot directory contains catalog.sqlite, config.toml, resources.jsonl and manifest.json. The manifest states format=refs-snapshot, version=1, catalog/schema/profile identity, each member's hash/size, configuration origin, root inventory, unresolved operation IDs, and external_contents_included=false. It is published from a verified .partial directory. Raw originals and export projection/waiver evidence are in the database. Recovery procedure and separate-home proof are required in quickstart.md.

## Later full export, slice 4

A versioned logical bundle contains documented JSONL sources, resources, collections, projects, memberships, origin identities, field provenance, originals, imports/outcomes, related pairs, operations and export targets/projections/waivers, plus config and manifest hashes/counts. Include removed-source state and retained keys. No supporting-items file exists. Every field can be read without refs or executing SQLite. File-byte inclusion is explicit; inventories alone are not file backup. Restore and logical export are different operations. Unknown versions, invalid references and escaping paths must fail visibly.
