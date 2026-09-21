# Implementation Plan: Academic Catalog Workflow

**Date:** 2026-09-21. **Feature:** [spec.md](spec.md). **Status:** revised design independently reviewed; only explicit Principle II amendment approval remains before task generation. No implementation or live migration has run. Task generation is for slice 1 only, followed by read-only analyze.

## Summary and selected model

Deliver capture → correction/search → project citation selection → explicit portable bibliography, with linked resources, verified copy-only intake and demonstrated snapshot restore. The user chose demand-driven metadata, imported notes as context, four-class export decisions, root-derived ownership, internal Title Case with per-title terms, portable output, no transliteration dependency and separate Casa catalog/library folders. Audit sections 11–12 preserve their exact replies and the auditor's interpretations.

Use one bounded CSL-shaped metadata object and four justified extensions, type-scoped mappings and immutable per-entry originals. See [semantic review](reviews/semantic-row-review-2026-09-21.md), [examples](reviews/model-examples-2026-09-21/README.md), [records](contracts/records.md) and [registry](contracts/bibliographic-coverage.json). The remaining Pandoc differences are evidence about its reader, not validation of refs' future importer. Extensions still need their named release fixtures.

## Technical context

Python 3.14 (`>=3.14,<3.15`) is a chosen initial support policy, not a technical necessity. Typer `>=0.27.2,<0.28`, Pydantic `>=2.13,<3`, bibtexparser `==2.0.1` as a guarded raw-block adapter, pylatexenc `==2.11` for supported one-way non-verbatim decoding. No Unidecode/AnyAscii runtime dependency. SQLite/TOML/pathlib/hashlib/unicodedata/fcntl provide the local core. No runtime network/model service. Use uv_build `>=0.12.1,<0.13`, a committed uv.lock, `[tool.uv] exclude-newer = "3 days"`, and uv sync --locked. Choose and exactly pin the current evaluated ty version when the environment is created; do not float its diagnostics in CI. pytest/pytest-cov and Ruff are development tools.

Storage is local SQLite rollback journal, validated canonical JSON, relational identity/relationships/operations and derived FTS5. Keep config in ~/.config/refs/config.toml, database/lock/staging in /Volumes/Casa/refs/cat and library in /Volumes/Casa/refs/lib. Runtime setup must check foreign keys, JSON/FTS5 and supported filesystem primitives. Live catalog/staging are never synced. External storage and arbitrary concurrent writers are not covered by a catalog lock.

Target macOS first, with Linux support only after the same contract suite passes. Cross-volume Downloads intake uses verified native-metadata-aware copy, same-volume no-overwrite publication from cat staging, catalog commit and (slice 2 only) identity-safe source cleanup. pathlib is preferred; low-level calls have specific durability/identity responsibilities. Creation-date preservation across volumes is not promised. Process-crash safety is required; power-loss protection is best effort with disclosed limits.

Engineering target: at 10,000 sources and 30,000 links, warmed search/list p95 ≤1 second across 100 fixed queries on a recorded reference machine; measure installed startup separately. Target up to four concurrent CLI processes with a five-second bounded lock wait. These are proposed measurable engineering gates, not achieved results.

## Delivery slices and requirement allocation

The specification describes the complete academic feature. Tasks generated now MUST cover only slice 1 and its applicable acceptance cases. Later clauses listed here are intentionally deferred, not silently omitted or claimed complete.

| Slice | Included behavior | Requirements and acceptance boundary |
| --- | --- | --- |
| 1: core + copy | Agent refs/CSL/Bib capture; Bib file import needed for adoption; correction, keys/titles/search; projects; portable export and projection-aware re-import; linking/opening; copy into Unfiled; snapshot plus manual verified restore; configuration and diagnostics | FR-001–015; FR-016 except collection filters; FR-017; FR-018–024 for bibliography inputs only, excluding Zotero/collection/note migration; FR-025–027; FR-030 Unfiled only; FR-031 copy/link only; FR-033–035 for non-destructive effects and catalog removal; FR-036–041 with snapshot/manual restore subset; FR-043–048. SC-001/004/005/006/009 plus applicable copy/recovery/mapping portions of SC-002/003/007/008/010. |
| 2: organization and move | Collection hierarchy/filtering, filing from folders without movement, explicit selected reorganize, move default and cross-volume cleanup | Complete collection portions of FR-016/028–035 and SC-007. Same-volume source-link optimization only after copy path proof. |
| 3: Zotero migration | One-time extractor/published JSON input, previewed child-note context, related pairs, original archive, origin/library identity and full reconciliation | Complete FR-018–024/049 and corresponding SC-002/003/010. Preserve original library; viewer check of malformed annotation before cutover. |
| 4: portable exit/recovery tools | Full restore CLI/bundle validation, optional file-inclusive backup and logical library export | Complete FR-040–042 and SC-008. No full cutover without these recovery/exit obligations. |

No task in slice 1 implements annotations, a supporting_items subsystem, arbitrary BibLaTeX inheritance, richer bibliography profiles, general plugin management, PDF search or full Zotero migration. Collection schema reserves Unfiled only. The first usable increment is all of slice 1, not US1 alone: export, safe copy and demonstrated restoration are part of the user's choice.

## Structure

```text
src/refs/
  cli.py                 # Typer/envelopes and command registration
  models.py              # strict input/output and profile validation
  config.py              # separate config/catalog/root resolution
  catalog.py             # schema, transactions, identities and revisions
  normalization.py       # titles, terms, Latin key tokens and filenames
  search.py              # internal lexical boundary and folded projection
  operations.py          # retry outcomes and effect reservations
  files.py               # link/copy/check/open; later move/reorganize
  platform_files.py      # native metadata, sync and exclusive primitives
  bibliography.py        # assessment, portable generation, publication
  recovery.py            # snapshot and verification
  adapters/bibtex.py     # guarded syntax adapter and scoped mapping
  adapters/csl.py        # agent structured input
  adapters/search_sqlite.py # default selectable search
  adapters/search_protocol.py # read-only versioned provider interface
  migrations/            # explicit schema definitions; no implicit upgrade
  data/                  # packaged registry/schema pins and policy tables
tests/
  unit/
  contract/
  integration/
  fixtures/search_plugin/ # independent literal-search implementation
tools/restore_snapshot.py # verified slice 1 restore procedure helper
```

Later one-time migration tooling belongs under tools/zotero_extract/, outside the installed runtime. Small ordinary modules suffice; no generic repository hierarchy. Search has a small read-only boundary selected through refs.search.v1 entry points and an independently installed literal-search proof, required in slice 1 by constitution IV/V. No general plugin framework or automatic installation is introduced.

## Constitution review

Principles I, III and V are implemented through stable IDs/keys, one fact authority, explicit effects, strict structured operations, retained evidence and representative runtime/restore gates. Principles IV/V require selectable search and an independently installed alternative demonstration in slice 1; the initial deferral proposal was corrected by independent review. Principle II's old adopt-without-move sentence conflicts with the accepted root-based A2 decision: an exact replacement has been presented for explicit authorization. Until recorded as a separate amendment, this is an unresolved constitutional conflict, not a PASS or waiver. Filename preservation, explicit previewed moves, no membership-driven movement and verification before deletion remain binding.

## Validation and review gates

Independent review must re-evaluate both existing checklists without rewriting original item text/IDs. It must check mapping scope, clearing and fallback re-import, title terms, normalized names and Latin overrides, output class/waiver boundaries, parser counterexamples, locations, copy/collision/crash evidence and restore procedure. Historical audit counts stay historical; a new assessment records current findings.

Implementation tests are explicitly required: installed CLI envelopes; stale updates and concurrent key allocation; malformed parser inputs; all promoted field/type/role fixtures including negative aliases and clearing; corporate names and particles; date precision; title protection; native labels; preserved originals; unknown/waiver expiry; golden rendered fields through declared consumers; blocked-output byte preservation; external edits; copy metadata and every interruption boundary; retry after config repair; unresolved-operation snapshots; verified restore to a second directory. Repeat only to resolve a concrete failure or required gate.

Synthetic/public material is the default. The user must select an actual paper and authorize its live replacement/migration separately. No reviewed design artifact proves live fidelity. The audit's 239/240 annotation match is evidence of embedded presence, not reader rendering. Preserve the one-file viewer check in migration readiness.

## Complexity and deferred work

Durable file intent is necessary because filesystem publication and SQLite commits are separate. Projection records are necessary for idempotent re-import of known lossy output. Store per-entry originals; keep large Zotero databases outside the catalog. No supporting-item subsystem, mode flag, editable duplicate namespaces, general plugin manager or dependency-backed romanization. Full backup bundle tooling and rich output return only with the later slice's need and fixtures.

## Payload and corpus boundaries

The one-second search/list target uses 10,000 records with at most 4 KiB indexed metadata/context text each and summary output at the default 50-result limit; resource links carry paths/labels, not file bytes. Report the actual fixture distribution. Show/full original retrieval and oversized entry parsing are outside that timing target and have separate byte counts and memory measurements. Inputs are processed per entry with bounded batch iteration; original bytes are retrieved through explicit inspection, not embedded in every search result. No arbitrary semantic truncation is permitted. Synthetic tests include a 1 MiB note/original and a 1,000-entry file to expose accidental quadratic/full-batch copying; this is a bounded test, not a new ingestion ceiling.

The real migration sample is at least 30 records and expands to cover every type/construct actually used by the selected paper, including unpromoted constructs. Keep that live-paper gate separate from synthetic mapping fixtures. Unassessed required constructs need explicit resolution before manuscript adoption/cutover.
