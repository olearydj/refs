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

## Slice 3 brief: organize files

Owner direction, 2026-09-22: after the ingest, "clean it up / reorg the refs folder, and migrate other adhoc papers / bib consumers to the new method." Earlier (2026-09-21) the PDFs were to move to a visible folder on Casa, renamed and cleaned up, and synced to other devices with Syncthing. This is the destructive slice: the move-with-delete protocol gets full specification, an experiment on a copy of the real tree, and an independent review before it touches the library. Everything else in the slice is decided by use.

### Outcome

Every file the catalog knows sits under `/Volumes/Casa/refs/lib`, recorded by root and relative path, in a folder tree that is its filing. The old Box tree and the Zotero storage folder hold nothing refs owns. New intake from Downloads moves the file rather than copying it. A file can be refiled by an explicit, previewed move. An interrupted move can be re-run to completion with nothing lost and nothing duplicated. Syncthing shares lib with the owner's other devices; that is a Syncthing setting made after the move, not a refs feature.

### Observed inputs, read-only, 2026-09-23

551 catalog resources, all absolute links, none under a named root: 511 under `~/Box Sync/zotero` (4.2 GB, all PDF) and 40 under `~/Zotero/storage` (37 HTML snapshots, 2 JPG, 1 PDF). Every linked path resolves. The Box tree has 517 real files: the 511 plus six PDFs no source links (two copies of Boost Your Git DX, ZeroToSoldMobile, Thomas 2025, ExploringMITCurricwithLLM, Bailenson). Zotero storage has three more unlinked PDFs. The Box tree is already a collection layout: 497 of 511 files sit in a folder whose relative path is one of their source's collection paths, and the other 14 sit in that collection's parent folder (`papers`, `web`). Names are Zotero's "Author - Year - Title" form with spaces and truncation; on disk they are NFD Unicode, in the catalog NFC, and macOS resolves both. lib holds nothing today. The cutover archive holds the database and JSON, not the PDFs, and no Time Machine backup exists. One vault note references the Box tree by path, seven times. Syncthing runs under launchd and already shares the vault with two devices.

### Decisions needed from the owner

D1 Layout. A: keep the collection tree as it stands, moved intact so `lib/dissertation/mixed-reality/...` stays what it is, and a folder path under lib is the file's filing collection with no separate filing table (Recommended: it is the layout you built and 497 of 511 files already agree with it; derive-from-location is the accepted A2 rule). B: flat, one folder per citation key initial or per year. C: something else you describe.

D2 Names. A: the move preserves names, as A2 already says for reorganize; renaming stays a separate later pass under the same protocol, if use shows the names hurt (Recommended: one destructive change at a time, and the current names already carry author, year and title). B: rename by the accepted convention during the move, so the one big move is also the one big rename.

D3 Unlinked files. The six Box PDFs and three storage PDFs that no source links. A: leave them where they are and list them in the move report; you add the ones you want with `add --file` before or after (Recommended). B: move them into `lib/Unfiled` as orphans for later capture. Owner, 2026-09-23, on the copied originals left in the Box tree: "I don't mind the extras in the Box folder. it is essentially an archive / backup of zotero db for now." Taken as A: the tree is an archive, unlinked files stay and are listed.

D4 Intake default. A: `add --file` and `resource add` move from Downloads by default, with `--copy` to keep the original (Recommended: the ledger item "move default", and Downloads cruft is the incident). B: keep copy as the default and add `--move`.

### What is built, proposal

1. One move protocol, used by every route: copy to `cat/staging` with an exclusive name, fsync, atomic publish into lib without overwrite, verify the destination digest against the source digest, then in one transaction re-record the resource as root plus relative path and mark the original as pending removal, then delete the original and mark the operation complete. Filenames are written NFC. A `file_operations` table (one row per file: resource, source path, destination, digest, state, timestamps) is the journal; re-running the same command resumes from the recorded state. No request-ID replay, no operations list/show, no native metadata adapter; `resource check` reports incomplete operations and the report of a completed move lists every old path beside its new one, which is what the vault link fix needs.
2. `reorganize`: previewed bulk move of linked files under a path prefix into lib, preserving relative paths (D1) and names (D2), or of one resource to a named collection folder. This is the 551-file cutover and the future refile in one command.
3. Intake by move per D4, through the same protocol.
4. The sync setup is a Syncthing folder added by the owner after the move; refs records nothing about it. `resource check` already recognizes sync-conflict filenames.

Budget: about three invocations, one table, no new dependency, roughly 600 source lines. Score should hold at 6. Journals, recover commands, request-ID replay, forced directory syncing beyond the fsyncs above, and the native metadata adapter stay deferred until an interruption in real use shows what re-running does not cover.

### What must never break

No delete before a verified copy: the destination digest is checked before the original goes, and the owner makes a plain copy of the Box tree and the storage folder under `/Volumes/Casa/archive/refs/` before the bulk move, because no other copy of the PDFs exists. No overwrite in lib. Existing names unless D2 chooses otherwise. Citation keys and every catalog row other than the resource locator. The Zotero database and the vault, read-only throughout. The never-cut list in `AGENTS.md`.

### Acceptance gate

Rehearse in a temporary home on a copy of the catalog and a sample of the real tree: a clean run, a run killed between publish and delete, a run killed between re-record and delete, each re-run to completion with 551 resources recorded under lib, every digest matching, no file present twice and no file missing. Then the real move under owner authorization, followed by `resource check` clean, `open` on a sample, and the vault paths updated from the report.

### Process

Full specification for the protocol and the journal (a short section in [files-and-recovery](contracts/files-and-recovery.md) and the data model), an independent review of that section only, tasks, build against synthetic fixtures, the rehearsal above, then the real move. Governing text stays net-flat or smaller.

## Deferred work

This is a boundary ledger, not a later-slice specification.

| Destination | Deferred surface |
| --- | --- |
| Slice 3: organize files | Relocating the library tree; filing from folders without movement; move default and explicit reorganize; operations/file-operations journals, operations list/show, recover, request-ID replay; native metadata adapter, attribute verification, forced flushes and directory syncing; renaming by convention; sync setup. |
| Later recovery/exit | Full restore command, file-inclusive backup/bundle validation and logical library export. |
| Backlog | export_projections, export_waivers/export waive, field_provenance table, normalize, index rebuild, background project membership, primary-resource administration, 10,000-source gate and four-process matrix. |
| When a second implementation is evaluated | Search entry point, selectable providers and replacement proof (including the QMD investigation). |
| Existing product backlog | Public CSL/Zotero JSON output, richer declared-consumer profiles, RIS, built-in lookup, PDF/semantic search and enrichment. |
| Fix batch from post-cutover use, 2026-09-22 (delivered 2026-09-23: 7f1ceab, 7e7858e, d30e03a; +51 lines, no schema or binding change) | (a) A bound `add` that finds differing values persists them: one `imports` row with origin `add` and the submitted record's digest, one entry holding the binding and conflicts, so `show` displays them and `import reconcile` can settle them; no row when nothing needs a later decision. Incident: Attention's three differences existed only in a saved result envelope. (b) `import list`: one line per run (batch ID, origin, date, counts), newest first; today a batch ID is findable only from the creating envelope or by reading SQLite, which the constitution forbids agents. (c) `resource add --copy` warns and skips the copy when the source already has an attachment with the same content, naming the existing resource. Incident: a redundant copy of Attention's PDF left `open` unable to choose. |
| Reference cleanup (owner-named backlog, 2026-09-22) | `refs verify KEY` or `--all`: fetch the authoritative record by DOI or ISBN (Crossref, DataCite), diff against the catalog, propose fills and corrections accepted per field. The deferred DOI lookup pointed at existing records. Needs a network adapter and a review flow; its own small slice after the library import shows how spotty the records are. |
| Next fix batch (2026-09-23) | (a) The resource label, when given at copy intake, becomes the last segment of the convention filename: short title, optional edition or version, year, then the slugged label, as in `ZeroToSold-v1.2.4-2020-mobile.pdf` and `BoostYourGitDX-2023-r2023-06-03.pdf`. One rule for alternative formats and releases of one source; a source keeps one file per resource, distinguished by label. Incident: three releases of Boost Your Git DX and a mobile build of Zero to Sold cannot be filed under their sources today because the convention name collides. Owner: "I don't want to delete the versions." (b) and (c): the two polish items in the conveniences row below. (d) Configured lists add to the built-in ones instead of replacing them: `keys.stopwords`, `titles.minor_words`, `titles.protected_terms`, `sorting.ignore_leading_articles`; `config show` keeps reporting the effective list with its origins. Owner, 2026-09-23: an internal list that a setting silently overrules "is a bad design"; refs never writes the config file, so additive is the visible fix. Removing a built-in entry waits for an incident. (e) Capitals rule: a word of two or more letters in all capitals inside a mixed-case title is an acronym, kept without warning; a title whose every letter-word is capitals is shouted and gets the review warning. The protected list then serves mixed-case words such as LaTeX and nbgrader. Incident: MIT and EECS warned on a correct title while a fully shouted title would pass with only its minor words lowered. (f) A record that fails validation reports the failing path and reason in the error details and the human line, instead of only "Input does not match the supported record profile". Incident: a hand-written book record with `context` as a string instead of a list took a schema read to diagnose. |
| Conveniences from first use (2026-09-22), slice 2 or 3 | Key preview candidates: `add --dry-run` shows the chosen title fragment plus the next two candidate word pairs so an explicit `--key` can be picked in one step. Owner's use-list continues to accumulate here. Polish noted 2026-09-23: the `import list` text layout drops the batch revision token and shows time to the second (JSON keeps both; only `import reconcile` consumes the token); the reconcile date-parts fix in 7e7858e should extend the existing patch helper rather than set nested paths inline. |

No deferred command needs a placeholder CLI or empty table. Current originals, optional native type, identities and correction markers retain the information required for later decisions. Without saved projection history, slice 1 reports lossy re-import differences without overwriting richer values; without stored waivers, known blocking losses remain blocked.
