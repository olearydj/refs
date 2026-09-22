# Implementation Plan: Slice 1

**2026-09-22 — slice 1 delivered.** Constitution 2.0.0 applies. All 37 tasks are complete; the code-complete checkpoint and the owner's real-paper trial are recorded in [slice 1 acceptance](reviews/slice-1-acceptance.md). Two polish batches driven by real-input trials followed (commits through `132d806`). This plan remains the record of the design as built and of deferred work; it is not updated for slice 2 until the owner's use-list exists. No Zotero migration has run.

## Delivery boundary

Deliver all six [slice 1 stories](spec.md#user-stories-and-acceptance): capture/correction/search, cited-only projects and portable export, .bib import, linking/copy into Unfiled, snapshot plus demonstrated manual restore, and configuration. All active FR/SC clauses in the trimmed spec apply; its deferred-ID ledger is excluded from task coverage. No partial US1-only release substitutes for capture-to-export and restore. The first development milestone is a walking skeleton: init, add, show and export for one supplied-key reference, with project create/cite to select it. The tasks split US1 and US2 into an early pass and a completion pass so this demonstration precedes the full importer and file intake. It is not the slice 1 acceptance gate.

The owner approved the keep/fold/defer list in [audit §14](reviews/2026-09-20-independent-design-audit.md#14-addendum-2026-09-21-first-right-sizing-checkpoint-and-the-slice-1-trim). That specific list supersedes the rough command budget; measure its actual size at the checkpoint rather than disguising subcommands as one operation. Architecture stays: application-owned boundaries, stable identities, revisions, schema versioning, per-entry originals and a lightweight correction marker.

## Technical choices

These are **implementation proposals**, not additional owner quotations. Python >=3.14,<3.15; Typer >=0.27.2,<0.28; Pydantic >=2.13,<3; bibtexparser==2.0.1 as a guarded block adapter; pylatexenc==2.11 for supported one-way text decoding. Four runtime dependencies, no network/model service or transliteration dependency. Use stdlib SQLite, TOML, pathlib, hashlib, unicodedata and narrowly justified descriptor/platform calls. No ORM or generic repository hierarchy.

Use uv_build >=0.12.1,<0.13, committed uv.lock, exclude-newer="3 days", and uv sync --locked. pytest/pytest-cov and Ruff are development tools; pin the evaluated ty version when creating the environment. These selections retain the prior research; no new dependency evaluation is implied by the trim.

SQLite rollback journal, foreign keys, synchronous FULL and short BEGIN IMMEDIATE writes protect revisions and key allocation. A five-second busy timeout produces an actionable retry result. Ten logical tables including one FTS projection; SQLite's internal FTS shadow tables are not additional domain tables. Config stays separate from cat/lib. macOS is first; Linux support requires the same affected contract checks.

## Structure and capability boundary

Keep ordinary modules for CLI, validated records, catalog/configuration, naming, bibliography, files and snapshot recovery, with Bib/CSL adapters. Domain functions use refs-owned values/errors, independent of Typer and SQLite row types. File adapters own only the platform primitives needed for verified copy and publication. A plain migration runner owns schema changes; ordinary open never upgrades implicitly.

The internal read-only search boundary takes literal query/filter/limit/offset and returns source IDs, revisions, matching fields and ranked snippets/availability. The application resolves authoritative records and enforces catalog policy. SQLite FTS5 is its only implementation. Rebuild the derived projection from authoritative values as needed internally; there is no index rebuild command. No entry-point selector, provider schema or proof package ships. Constitution IV/V require selection and replacement proof when a second implementation is evaluated, not now.

## Contracts

| Contract | Responsibility |
| --- | --- |
| [CLI and configuration](contracts/cli.md) | Exact approved command surface, four schemas, envelope, locations and policy defaults. |
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

**Owner decision, 2026-09-22.** Slice 1 works on one paper but cannot replace Zotero until the library is in it; daily use, not more specification, will show what refs needs. Slice 2 is therefore the Zotero ingest and whole-library use. Organizing files (relocating the tree, filing, move-by-default, reorganize) moves to slice 3, because it is the destructive part and gets the full protocol treatment. This brief is the slice's specification; the requirements it delivers already exist in [spec.md](spec.md) as deferred clauses and are un-deferred in place, not rewritten.

### Outcome

Every source in the owner's Zotero library is in refs with its original type, ordered creators and roles, citation key, tags and collection memberships; every file attachment is linked where it sits today; short child notes are folded into each source's context; related-item pairs are kept. The owner can find, cite and export anything from the library without opening Zotero, and a whole-library portable `.bib` renders the same as Better BibTeX's export. Zotero then becomes an archive. Nothing moves on disk.

Observed inputs (read-only inspection, 2026-09-20 to 22): Zotero 6.0.37, userdata schema 121, global schema 28, Better BibTeX 7.0.0. 562 regular items across 16 types; 1,343 distinct creators in 7 roles; 58 collections up to three deep with 574 memberships (9 items in more than one); 362 tags; 792 attachments (511 linked files under `~/Box Sync/zotero`, all resolving; 43 stored files; 238 URL-only); 238 short child notes on 157 sources (median 113 characters); 246 attachment notes (ZotFile outlines, median 14,600 characters); 240 annotations, all embedded in 9 PDFs and verified present; 6 related-item links; 562 `Citation Key:` lines in Extra matching the legacy Better BibTeX table exactly; 206 other `label: value` Extra lines (Google Books IDs, arXiv IDs, publishers); 12 names in BibLaTeX extended form; one empty group library; zero items in trash.

### Delivered requirements

FR-018 (the Zotero route), FR-022 (collections as memberships, tags as legacy tags, links in place), FR-023 (preservation reported separately from usability), FR-024 (per-entry accounting with `import show`), FR-028 (collection hierarchy and membership, read from the import; creation and editing wait for slice 3), FR-049 (notes to context, related pairs, origin identities). Each clause is marked "slice 2" in `spec.md` when un-deferred. Design already recorded and binding: the input contract is Zotero API v3 item and collection JSON with a manifest carrying the derived library identity (audit F-I06); key precedence is native `citationKey`, then Extra `Citation Key:`, then the legacy table; the Zotero item key and library URI are provenance, never write authority; whole databases are never stored as BLOBs; notes fold into context (audit section 11, item 2); annotations are not imported.

### What is built

1. A one-time extractor, `tools/zotero_extract/`, outside the installed package: reads `zotero.sqlite` (preferably the `.bak` Zotero maintains) read-only, locked to userdata 121, and writes per-item and per-collection JSON in the published API v3 shape plus `manifest.json`. It is a migration script, not a maintained adapter, and says so.
2. `import --format zotero --input DIR` over that directory: same identity, conflict and originals rules as `.bib` import; one original JSON document per item; collections created as a hierarchy with memberships; tags as legacy tags; linked-file and stored-file attachments as resources linked in place (stored files resolve under the original Zotero `storage/<itemKey>/`); URL-only attachments retained as context, not resources; child notes as context entries with origin `import`; attachment notes handled per decision D2 below; related links as source relations; every Extra line parsed into key, identifiers, or residual context.
3. `import show BATCH`, with per-entry status persisted for this and later batches (the slice 1 `imports` row grows an entries table), so a 562-record import's conflicts can be listed and settled with ordinary `update` or an explicit `import reconcile` decision.
4. `collection list` (read-only hierarchy with counts) and a `--collection` filter on `list` and `search`, so memberships are usable. No filing, no folder mapping, no moves.
5. The acceptance harness, written before the importer: compares the refs catalog with the Zotero database and the Better BibTeX export item by item (keys, creators, types, tags, memberships, file links) and diffs a whole-library portable export against the BBT `.bib` through Pandoc. The importer is done when the harness reports zero unexplained differences.

Not built in slice 2: any file move, rename, filing or reorganize; annotation import; a Zotero writer; `reconcile` beyond per-entry accept-incoming or keep-current; a general relationship editor. The 4.2 GB tree stays where it is; new downloads keep copying into `lib/Unfiled` until slice 3 unifies the roots.

### Decisions needed from the owner

- D1. Collection names and hierarchy: import verbatim as refs collections (recommended), or flatten or rename during import.
- D2. The 246 attachment-note outlines: skip them (recommended; they are regenerable from the PDFs and would add 4.4 MB of list markup to context), or keep them as context on the file's resource.
- D3. Title-similarity matches between the library and sources already captured (the Pipyer and Attention records): report and keep both (recommended, per FR-020; the owner merges by `remove` or re-key), or auto-bind when the DOI also agrees.
- D4. The 206 non-key Extra lines: parse the recognized identifiers (arXiv, Google Books, OCLC) into `identifiers` and keep the rest as context (recommended), or keep every line as context.

### What must never break

Existing citation keys, byte for byte. The sources, corrections and adopted export already in the owner's catalog from the Pipyer trial. The Zotero database, the Box tree and every manuscript bibliography, which are read-only throughout. No file moves, renames or deletions. The never-cut list in `AGENTS.md`.

### Acceptance gate

Run against the owner's real library only after the harness passes on synthetic fixtures and the owner authorizes the extraction. Gate: all 562 items imported with per-entry accounting and zero unexplained differences from the harness; all 562 keys preserved; all 554 file-backed attachments resolving; 58 collections and 574 memberships matching; a whole-library portable export rendering through Pandoc identically to the BBT export except for reported, explained differences; a re-run of the import reporting all items unchanged; the Pipyer project and its adopted export untouched. Then the owner migrates remaining papers one at a time by the slice 1 walkthrough and keeps the use-list that decides slice 3's content beyond the file work already promised.

### Process

Light loop, per [right-sizing](../../docs/right-sizing.md): this brief; `$speckit-clarify` to record D1 to D4 as literal replies in `spec.md`; un-defer the listed clauses and the interchange contract's Zotero section in place, keeping governing text net-flat; write the harness; `$speckit-tasks` appending slice 2 phases; `$speckit-analyze`; build; the real import under authorization. Right-sizing budget for the slice: about 6 new invocations, 2 tables (`import_entries`, `collections` with `source_collections`), no new runtime dependency, roughly 800 source lines. Exceeding any figure prompts the usual question.

## Deferred work

This is a boundary ledger, not a later-slice specification.

| Destination | Deferred surface |
| --- | --- |
| Slice 2: bring the library across (brief above) | One-time Zotero extraction and import; collections and memberships (read-only hierarchy, `--collection` filter); child-note context and related pairs; source_relations; per-entry import status and `import show`; minimal `import reconcile`. |
| Slice 3: organize files | Relocating the library tree; filing from folders without movement; move default and explicit reorganize; operations/file-operations journals, operations list/show, recover, request-ID replay; native metadata adapter, attribute verification, forced flushes and directory syncing; renaming by convention; sync setup. |
| Later recovery/exit | Full restore command, file-inclusive backup/bundle validation and logical library export. |
| Backlog | export_projections, export_waivers/export waive, field_provenance table, normalize, index rebuild, background project membership, primary-resource administration, 10,000-source gate and four-process matrix. |
| When a second implementation is evaluated | Search entry point, selectable providers and replacement proof (including the QMD investigation). |
| Existing product backlog | Public CSL/Zotero JSON output, richer declared-consumer profiles, RIS, built-in lookup, PDF/semantic search and enrichment. |
| Conveniences from first use (2026-09-22), slice 2 or 3 | Key preview candidates: `add --dry-run` shows the chosen title fragment plus the next two candidate word pairs so an explicit `--key` can be picked in one step. Owner's use-list continues to accumulate here. |

No deferred command needs a placeholder CLI or empty table. Current originals, optional native type, identities and correction markers retain the information required for later decisions. Without saved projection history, slice 1 reports lossy re-import differences without overwriting richer values; without stored waivers, known blocking losses remain blocked.
