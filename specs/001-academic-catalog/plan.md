# Implementation Plan: Slice 1

**2026-09-21 — trimmed design.** Constitution 2.0.0 is applied. The owner passed the second right-sizing checkpoint and requested the intake corrections and checklist archival before tasks. Those updates are committed. The owner has authorized slice 1 task generation; tasks.md now groups the work by runnable user stories. Analysis follows before implementation. No implementation or live migration has run.

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

## Deferred work

This is a boundary ledger, not a later-slice specification.

| Destination | Deferred surface |
| --- | --- |
| Slice 2, after real-paper use | Collections and filing; move default and explicit reorganize; operations/file-operations journals, operations list/show, recover, request-ID replay. Moving an original also requires the deferred native metadata adapter, verification of ACLs, extended attributes and resource forks, forced full flushes and directory syncing. Unfiled needs no table now. |
| Slice 3 | One-time Zotero extraction/migration, child-note context/related pairs, source_relations; per-entry import status and import show/resume/reconcile. |
| Later recovery/exit | Full restore command, file-inclusive backup/bundle validation and logical library export. |
| Backlog | export_projections, export_waivers/export waive, field_provenance table, normalize, index rebuild, background project membership, primary-resource administration, 10,000-source gate and four-process matrix. |
| When a second implementation is evaluated | Search entry point, selectable providers and replacement proof (including the QMD investigation). |
| Existing product backlog | Public CSL/Zotero JSON output, richer declared-consumer profiles, RIS, built-in lookup, PDF/semantic search and enrichment. |
| Slice 2 conveniences from first use (2026-09-22) | Key preview candidates: `add --dry-run` shows the chosen title fragment plus the next two candidate word pairs so an explicit `--key` can be picked in one step. Owner's use-list continues to accumulate here. |

No deferred command needs a placeholder CLI or empty table. Current originals, optional native type, identities and correction markers retain the information required for later decisions. Without saved projection history, slice 1 reports lossy re-import differences without overwriting richer values; without stored waivers, known blocking losses remain blocked.
