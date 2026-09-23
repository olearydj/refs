# Implementation Plan: Slices 1 and 2

**2026-09-22, slices 1 and 2 delivered.** [Slice 1 acceptance](reviews/slice-1-acceptance.md) and [slice 2 acceptance](reviews/slice-2-acceptance.md) record the checkpoints, the Pipyer trial and the owner-executed Zotero cutover. Slice 2 landed at about 4,130 application lines (+1,000 over slice 1 against an 800 estimate, the difference being six rule-level fixes from the real-import rehearsal), 14 tables, no new dependency, 500 tests. This plan remains the record of the design as built and of deferred work; slice 3 gets a brief when the owner's use-list calls for it.

## Delivery boundary

Slice 1 delivered all six [stories](spec.md#user-stories-and-acceptance). Its tasks cover the slice 1 clauses; the marked slice 2 additions and deferred identifiers are outside that completed work. The walking skeleton demonstrated init, add, show and export before completing import, file intake and restore.

The owner approved the keep/fold/defer list in [audit §14](reviews/2026-09-20-independent-design-audit.md#14-addendum-2026-09-21-first-right-sizing-checkpoint-and-the-slice-1-trim). That specific list supersedes the rough command budget; measure its actual size at the checkpoint rather than disguising subcommands as one operation. Architecture stays: application-owned boundaries, stable identities, revisions, schema versioning, per-entry originals and a lightweight correction marker.

## Technical choices

These are **implementation proposals**, not additional owner quotations. Python >=3.14,<3.15; Typer >=0.27.2,<0.28; Pydantic >=2.13,<3; bibtexparser==2.0.1 as a guarded block adapter; pylatexenc==2.11 for supported one-way text decoding. Four runtime dependencies, no network/model service or transliteration dependency. Use stdlib SQLite, TOML, pathlib, hashlib, unicodedata and narrowly justified descriptor/platform calls. No ORM or generic repository hierarchy.

Use uv_build >=0.12.1,<0.13, committed uv.lock, exclude-newer="3 days", and uv sync --locked. pytest/pytest-cov and Ruff are development tools; pin the evaluated ty version when creating the environment. These selections retain the prior research; no new dependency evaluation is implied by the trim.

SQLite rollback journal, foreign keys, synchronous FULL and short BEGIN IMMEDIATE writes protect revisions and key allocation. A five-second busy timeout produces an actionable retry result. Slice 1 has ten logical tables including one FTS projection; SQLite's internal FTS shadow tables are not additional domain tables. Config stays separate from cat/lib. macOS is first; Linux support requires the same affected contract checks.

## Structure and capability boundary

Keep ordinary modules for CLI, validated records, catalog/configuration, naming, bibliography, files and snapshot recovery, with Bib/CSL adapters. Domain functions use refs-owned values/errors, independent of Typer and SQLite row types. File adapters own only the platform primitives needed for verified copy and publication. A plain migration runner owns schema changes; ordinary open never upgrades implicitly.

The internal read-only search boundary takes literal query/filter/limit/offset and returns source IDs, revisions, matching fields and ranked snippets/availability. The application resolves authoritative records and enforces catalog policy. SQLite FTS5 is its only implementation. Rebuild the derived projection from authoritative values as needed internally; there is no index rebuild command. No entry-point selector, provider schema or proof package ships. Constitution IV/V require selection and replacement proof when a second implementation is evaluated, not now.

## Contracts

| Contract | Responsibility |
| --- | --- |
| [CLI and configuration](contracts/cli.md) | Exact approved command surface, four schemas, envelope, locations and policy defaults. |
| [Zotero input](contracts/interchange.md) | Slice 2 extraction directory, admission, identity and attachment resolution. |
| [Records and input](contracts/records.md) | Canonical ownership, names/dates/titles, mutation, import and originals. |
| [Bibliography](contracts/bibliography.md) | Type-scoped mappings, portable projection, losses and consumer fidelity. |
| [Files and recovery](contracts/files-and-recovery.md) | Copy, export publication/adoption, backup and manual restore. |

[Data model](data-model.md) owns persistence; the [registry](contracts/bibliographic-coverage.json) retains semantic mappings. Zotero rows support the prior semantic review and future promotion; they do not add a Zotero importer to slice 1. [Research](research.md) links evidence and its limits.

## Constitution review

Principles I/III: stable keys/IDs, verbatim originals, current correction markers, strict schemas and revision guards. Principle II: root-derived ownership, untouched links except explicitly invoked intake, copy retention and no automatic export. The owner's later “Rename by default” is the separately requested intake naming policy; it does not authorize renaming linked files or later reorganize. Principles IV/V: internal boundaries now, replacement machinery at the second implementation, representative fidelity and restore evidence. No pending Principle II amendment remains.

## Verification and acceptance

Keep one installed end-to-end smoke test and one two-process key-allocation test. Add focused unit/contract fixtures for actual risks: parser corruption, names/dates/protected terms, mappings and clearing, stale updates, rerun identity, blocked export bytes, outside edits, safe copy/collision/interruption, and corrupt/valid snapshots. Consumer golden rendering checks meaningful citation fields, not just key resolution. These are proportionate correctness checks, not a four-process matrix or 10,000-source performance gate.

[Quickstart](quickstart.md) defines the smoke and second-home restore proof. Tests use synthetic/public inputs. Actual paper use is a later acceptance activity chosen by the owner, with permission for any external replacement; it precedes both whole-library cutover and any slice 2 specification. Earlier checklist passes apply to the older design and are not certification of this trim or future implementation.

## Slice 2 brief: bring the library across

**Owner decision, 2026-09-22.** Slice 1 works on one paper but cannot replace Zotero until the library is in it; daily use, not more specification, will show what refs needs. Slice 2 is therefore the Zotero ingest and whole-library use. Organizing files (relocating the tree, filing, move-by-default, reorganize) moves to slice 3, because it is the destructive part and gets the full protocol treatment. This brief and its linked contracts specify the slice; the corresponding [requirements](spec.md) are marked slice 2.

### Outcome

Every source in the owner's Zotero library is in refs with its original type, ordered creators and roles, citation key, tags and collection memberships; every file attachment is linked where it sits today; short child notes are folded into each source's context; related-item pairs are kept. The owner can find, cite and export anything from the library without opening Zotero, and a whole-library portable `.bib` renders the same as Better BibTeX's export. Zotero then becomes an archive. Nothing moves on disk.

Observed inputs (read-only inspection, 2026-09-20 to 22): Zotero 6.0.37, userdata schema 121, global schema 28, Better BibTeX 7.0.0. 562 regular items across 16 types; 1,343 distinct creators in 7 roles; 58 collections up to three deep with 574 memberships (9 items in more than one); 362 tags; 792 attachments (511 linked files under `~/Box Sync/zotero`, all resolving; 43 stored files; 238 URL-only); 238 short child notes on 157 sources (median 113 characters); 246 attachment notes (ZotFile outlines, median 14,600 characters); 240 annotations, all embedded in 9 PDFs and verified present; 6 related-item links; 562 `Citation Key:` lines in Extra matching the legacy Better BibTeX table exactly; 206 other `label: value` Extra lines (Google Books IDs, arXiv IDs, publishers); 12 names in BibLaTeX extended form; one empty group library; zero items in trash.

### Delivered requirements

FR-018, FR-022, FR-023, FR-024, FR-028 and FR-049 are active for slice 2. FR-020/021 gain D3 binding and gap filling for every import format. The [Clarifications table](spec.md#clarifications) records D1–D4 with literal replies separately from interpretations.

### What is built

1. The one-time extractor and published JSON directory follow [Zotero input](contracts/interchange.md).
2. Import, inspection, reconciliation and collection filtering follow [CLI](contracts/cli.md#slice-2-commands) and [records](contracts/records.md#identity-and-non-overwriting-import). The [data model](data-model.md) defines their four tables.
3. `tests/fixtures/real-trial/zotero_gate.py` and the existing `run.sh` render comparison establish acceptance before real import. The empty-catalog baseline is 562 missing items across 58 Zotero collections.

File organization is slice 3. The 4.2 GB tree stays in place; new downloads keep copying into lib/Unfiled. There is no Zotero writer, annotation importer or general relationship editor.

### Decision evidence

D1 preserves collections verbatim. D2's outline verification is recorded in FR-023. D3 authorizes resetting the trial catalog before migration and governs later binding and explicit corrections. A rehearsal of the real import in a temporary home on 2026-09-23 showed ISBN binding merging chapters into their book and books of one set into each other; the owner then chose the ISBN guard (literal reply "A: ISBN binds books only, one-to-one (Recommended)"): an ISBN binds only when both records are type book and exactly one incoming item matches exactly one existing source; any additional candidate makes the group a reported conflict with nothing bound; chapters never bind by ISBN; DOI binding is unchanged. Identifiers are normalized on every route (arXiv without prefix or class suffix, DOI lowercased) and equal values from several fields collapse to one before export assessment. D4 retains only the six named identifier schemes as modeled Extra data. Inspection found translator output, not Scite output: 206 labeled Extra lines, mainly Google Books IDs, arXiv IDs and publishers, plus six prose lines. Unmodeled lines remain original evidence. The decisions and their literal replies are owned by the spec, not repeated here.

### What must never break

Existing citation keys, byte for byte. The Zotero database, the Box tree and every manuscript bibliography, which are read-only throughout. (The trial catalog from slice 1 is deleted and re-initialized before the library import, per D3; the Pipyer paper is re-imported afterwards and its adoption re-established by the walkthrough.) No file moves, renames or deletions. The never-cut list in `AGENTS.md`.

### Acceptance gate

Run against the owner's real library only after the harness passes on synthetic fixtures and the owner authorizes the extraction. Gate: all 562 items imported with per-entry accounting and zero unexplained differences from the harness; all 562 keys preserved; all 554 file-backed attachments resolving; 58 collections and 574 memberships matching; a whole-library portable export rendering through Pandoc identically to the BBT export except for reported, explained differences; a re-run of the import reporting all items unchanged; then the Pipyer paper re-imported and re-adopted by the slice 1 walkthrough with every overlap bound by DOI per D3. Then the owner migrates remaining papers one at a time by the slice 1 walkthrough and keeps the use-list that decides slice 3's content beyond the file work already promised.

### Process

Follow the [light loop](../../docs/right-sizing.md): specify, append slice 2 tasks, analyze, build, then perform the real import under owner authorization. The extractor and synthetic gate come first; the real import is the last task. Budget: about six new invocations, four tables (import_entries, collections, source_collections, source_relations), no new runtime dependency and roughly 800 source lines. These are tests of proportion, not caps that distort the schema. Governing text stays net-flat or smaller.

## Deferred work

This is a boundary ledger, not a later-slice specification.

| Destination | Deferred surface |
| --- | --- |
| Slice 3: organize files | Relocating the library tree; filing from folders without movement; move default and explicit reorganize; operations/file-operations journals, operations list/show, recover, request-ID replay; native metadata adapter, attribute verification, forced flushes and directory syncing; renaming by convention; sync setup. |
| Later recovery/exit | Full restore command, file-inclusive backup/bundle validation and logical library export. |
| Backlog | export_projections, export_waivers/export waive, field_provenance table, normalize, index rebuild, background project membership, primary-resource administration, 10,000-source gate and four-process matrix. |
| When a second implementation is evaluated | Search entry point, selectable providers and replacement proof (including the QMD investigation). |
| Existing product backlog | Public CSL/Zotero JSON output, richer declared-consumer profiles, RIS, built-in lookup, PDF/semantic search and enrichment. |
| Reference cleanup (owner-named backlog, 2026-09-22) | `refs verify KEY` or `--all`: fetch the authoritative record by DOI or ISBN (Crossref, DataCite), diff against the catalog, propose fills and corrections accepted per field. The deferred DOI lookup pointed at existing records. Needs a network adapter and a review flow; its own small slice after the library import shows how spotty the records are. |
| Conveniences from first use (2026-09-22), slice 2 or 3 | Key preview candidates: `add --dry-run` shows the chosen title fragment plus the next two candidate word pairs so an explicit `--key` can be picked in one step. Owner's use-list continues to accumulate here. |

No deferred command needs a placeholder CLI or empty table. Current originals, optional native type, identities and correction markers retain the information required for later decisions. Without saved projection history, slice 1 reports lossy re-import differences without overwriting richer values; without stored waivers, known blocking losses remain blocked.
