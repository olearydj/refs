# Tasks: Academic Catalog, Slice 1

**Input:** [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md), the four contracts, research.md and quickstart.md. **Status:** generated 2026-09-21; nothing implemented or checked off. Tests are included because the spec and plan require them.

The first milestone is a walking skeleton: initialize a disposable catalog, add one reference, show it, and export it. Export still uses a project, so the skeleton includes project create and cite. It uses a supplied citation key and one English journal article. It is a working increment, not acceptance of the complete slice.

Tasks remain grouped by user story. US1 and US2 each have an early pass for the skeleton and a completion pass. Setup and foundation contain only what that first path needs. All six stories, consumer checks and the restore proof are required before slice 1 is ready for the owner's paper. Deferred work in plan.md is excluded.

## Format and working rules

Each task has an ID, an optional `[P]` marker and, in story phases, a story label. Paths are relative to the repository root. `[P]` means the task can run alongside the other marked task in that phase once earlier phases are complete; it does not authorize skipping dependencies. Tasks without that marker run in listed order. Shared files such as src/refs/cli.py are edited sequentially.

Keep ordinary modules and application-owned values/errors. Add tables to src/refs/migrations/001_initial.sql as their stories arrive; before release these are iterations of the initial schema, exercised in fresh disposable catalogs, not implicit upgrades of a real catalog. No milestone authorizes live migration. Write the named risk tests before the corresponding implementation, confirm they fail for the missing behavior, then make them pass. Extend one installed smoke test through the milestones rather than creating a second end-to-end suite.

## Phase 1: Setup

**Outcome:** An installable Python package and a working test command.

- [x] T001 Create pyproject.toml, uv.lock, src/refs/__init__.py, src/refs/__main__.py and tests/conftest.py. Apply plan.md's Python and four runtime dependency constraints, uv_build, the three-day cooldown and `uv sync --locked`. Configure pytest, Ruff and the exactly evaluated ty version. Provide the refs console entry point and disposable test homes; do not add runtime dependencies.

## Phase 2: Foundation for the first runnable path

**Outcome:** The real CLI can initialize a disposable catalog and report failures in the agreed format.

- [x] T002 Implement the Typer entry point in src/refs/cli.py and refs-owned results/errors in src/refs/results.py. Use schema_version, command, status, data, warnings and errors; enforce exit codes 0 and 2–6, one JSON object on stdout even on usage failures, progress on stderr, human output and noninteractive execution. Validate previews without persistent effects. Test this boundary in tests/contract/test_results.py. Covers FR-013, FR-014 and FR-017.
- [x] T003 Implement basic paths before init, reporting the resolved configuration, catalog and library locations, plus explicit configuration/catalog selection and init in src/refs/config.py, src/refs/catalog.py, src/refs/migrations/001_initial.sql and src/refs/cli.py. Start with the data-model constraint “One stable catalog UUID, schema version and monotonically increasing catalog revision. No implicit init or upgrade.” Use foreign keys, rollback journaling, synchronous FULL, short BEGIN IMMEDIATE writes and the five-second timeout. Honor explicit temporary paths, repeat-init no-op, no overwrite, no fallback when a selected volume is missing, private permissions and a ready marker after validation. Add focused failure checks in tests/contract/test_init.py. Full preference discovery follows in US6. Covers FR-017 and FR-044.

## Phase 3: US1 — Save and show the first reference (P1, early pass)

**Goal:** Persist a real source and its original input through supported commands.

**Runnable check:** Add tests/fixtures/reference.json to an empty disposable catalog, show its supplied key and compare the returned source, revision and original evidence with the input. Unsupported fields fail explicitly in this early pass.

- [x] T004 [US1] Write tests/contract/test_capture.py and tests/fixtures/reference.json for a supplied-key English journal article, original JSON preservation, duplicate/conflicting identity and add --dry-run. Assert returned identity/key and unchanged catalog bytes after preview. Covers FR-001–005 and FR-014.
- [x] T005 [US1] Implement the initial source envelope in src/refs/models.py and the sources table in src/refs/migrations/001_initial.sql. Carry the exact data-model constraints: “Stable UUID, binary-unique citation key, active/removed state, revision, UTC timestamps; validated metadata/context/native type/extensions/title protection and overrides.” “Key-generation provenance holds policy/table/Unicode versions.” “A compact corrected_fields JSON marker identifies explicit sets, clears and type-superseded paths; origins/access claims remain distinguishable on the row.” Validate the skeleton article and explicit key now; T013 broadens supported values without adding another authority. Covers FR-001–005 and FR-047.
- [x] T006 [US1] Implement add --format refs and show in src/refs/sources.py, src/refs/catalog.py and src/refs/cli.py. Add originals and origin_identities in src/refs/migrations/001_initial.sql with “Immutable exact entry bytes, SHA-256, length, format, origin, file digest/locator and needed comments/definitions; nullable source association for unresolved input.” “Deduplicate by digest plus origin/locator association so repeated import does not duplicate evidence.” “Retain exact .bib file bytes once for adoption inspection as well as addressable entries; no whole Zotero databases.” Identity constraints are “Unique namespace/library identity/item key binding to source ID, plus input fingerprint. Bindings cannot be stolen.” Save source, original and accepted identity together; return likely matches or conflicts instead of merging by title. Pass T004 through the installed command. Covers FR-001–005, FR-014 and FR-020.

## Phase 4: US2 — Export the first reference (P1, early pass)

**Goal:** Complete milestone 1 through the real CLI and a real bibliography file.

**Runnable check:** Initialize, add, show, project create, project cite and export one reference. A second export is identical. Adding or editing catalog data does not itself write a bibliography.

- [x] T007 [US2] Start the single installed smoke test in tests/integration/test_smoke.py using tests/fixtures/reference.json and a temporary config/catalog/library. Assert init → add → show → project create → project cite → export, the expected key and article fields, deterministic bytes and refusal to replace an unrelated existing file. This test begins red and becomes milestone 1 at T010. Covers FR-036–038 and the initial portion of SC-006.
- [x] T008 [US2] Implement project create and cite in src/refs/projects.py and src/refs/cli.py. Add projects and project_sources to src/refs/migrations/001_initial.sql with “Stable ID, unique nonblank name, description and revision.” and “Unique project/source pair and cited boolean. Every slice 1 row has cited=true. Cite inserts, uncite deletes; repeats are no-ops.” Cite only active sources and preserve their identities. Covers FR-036.
- [x] T009 [US2] Implement export of the supported skeleton article in src/refs/bibliography.py, src/refs/files.py and src/refs/cli.py. Add export_targets to src/refs/migrations/001_initial.sql with “Unique canonical destination, project/profile fingerprint and last successful byte digest.” and a nullable pending_digest recorded before publication. The baseline remains nullable until publication. Recognise matching pending output on retry, including first export, then advance the baseline and clear the pending digest atomically. Select the project's active citations in a consistent snapshot, emit portable BibTeX with protected spelling, stage beside the destination and publish without overwrite. For a previously adopted unchanged target, use guarded atomic replacement; unknown input or outside edits stop without changing bytes. Do not hard-code the fixture, fabricate facts, or silently omit unsupported fields. Covers FR-037–039 and SC-006.
- [x] T010 [US2] Run the installed smoke test in tests/integration/test_smoke.py and add its disposable CLI walkthrough to specs/001-academic-catalog/quickstart.md. Verify actual SQLite persistence and .bib bytes, not mocked services. Mark milestone 1 complete only when init, add, show and export work end to end; the project steps are part of the same run.

### Milestone 1 demonstration

The fixture has citation_key `smith-2024-learningPython`. Run these commands only once the implementation exists; every path stays under a disposable directory.

```sh
demo=$(mktemp -d)
export REFS_CONFIG="$demo/config.toml" REFS_CATALOG="$demo/cat"
uv run --locked refs init --library-root "$demo/lib"
uv run --locked refs add --format refs --input tests/fixtures/reference.json
uv run --locked refs show smith-2024-learningPython
uv run --locked refs project create demo
uv run --locked refs project cite demo smith-2024-learningPython
uv run --locked refs export --project demo --output "$demo/references.bib"
```

## Phase 5: US1 — Complete capture, correction and retrieval (P1)

**Goal:** Keep and find complete or incomplete references without a project. Single-entry Bib input is completed with its shared adapter in US3.

**Runnable check:** Add refs and CSL inputs, inspect the four schemas, correct a record, reject a stale correction, search each supported field, and remove/reactivate without losing its key. Run the one two-process key-allocation test.

- [x] T011 [P] [US1] Write tests/unit/test_records.py and tests/unit/test_naming.py for strict nested values, names and particles, corporate authors, date precision, extensions, type applicability, protected terms, whole-title preservation, short-title boundaries, numeric editions and versions, explicit overrides, Latin normalization, unsupported scripts and collision suffixes. Use the accepted examples and negative cases, including a patent and a presentation proving that the first author is used uniformly across types. Covers FR-002, FR-005–012, FR-047–048 and SC-004.
- [x] T012 [P] [US1] Write tests/contract/test_sources.py, tests/contract/test_search.py and tests/integration/test_key_allocation.py for revision checks, explicit clearing, tombstones, rekey preview, original retention and matching-field evidence. Keep exactly one two-process key-allocation test that exercises BEGIN IMMEDIATE and unique keys. Check empty results and sources without tags. Covers FR-003–005, FR-014–017, FR-035 and SC-004–005/009.
- [x] T013 [US1] Complete the strict record and patch models in src/refs/models.py. Package the unchanged mapping registry under src/refs/data/. Include a pinned CSL schema only if runtime models validate against it; keep Zotero and BibLaTeX reference definitions under tests/ if needed, never in the slice 1 wheel. Record provenance and hashes; narrow validation to the profile's types, fields and four extensions. Enforce all nested constraints in contracts/records.md, including real calendar validation, ordered personal/literal names, language, native label compatibility, title_parts, context origins and access claims. Unknown imported values remain original evidence. Covers FR-001–002, FR-005, FR-008–010 and FR-047–048.
- [x] T014 [US1] Implement title, short-title, sort-title, edition display, filename and key policy functions in src/refs/naming.py and the versioned Latin table in src/refs/data/creator-latin-v1.json. Follow contracts/records.md and contracts/cli.md, including numeric edition versus version, term protection, ND keys but original-name filename fallback when year is absent, override precedence and no automatic rekey. Allocate suffixes in the source transaction and persist policy/table/Unicode versions. Use the first author, then first editor, then title/year uniformly for every type, with key_author taking precedence. Connect generated keys and dry-run explanations to add in src/refs/sources.py. Covers FR-006–012 and SC-004.
- [x] T015 [US1] Implement update --set/--patch, key set, remove and reactivate in src/refs/sources.py and src/refs/cli.py. Replace arrays whole, use explicit clear rather than null, reject incompatible type changes, enforce expected revisions and increment once only on change. Record corrected paths, keep original evidence and reserved removed keys, preview destructive catalog changes, preserve associations for reactivation, and never alter external files or bibliographies. Covers FR-004–005, FR-014, FR-021 and FR-035.
- [x] T016 [US1] Implement the internal read-only search boundary in src/refs/search.py and SQLite FTS5 in src/refs/adapters/search_sqlite.py. Add its projection in src/refs/migrations/001_initial.sql with “Derived FTS5 metadata/context/legacy-tag text keyed by source ID; matching fields returned with current source revision.” Keep it rebuildable from authoritative values and update it transactionally on source changes. Wire exact key/identifier lookup, lexical search, project filtering and title/key list order in src/refs/cli.py, including pagination and matching-field origin. Do not search PDF bytes or arbitrary originals. Covers FR-015–017 and SC-005.
- [x] T017 [US1] Implement CSL-shaped input in src/refs/adapters/csl.py and offline schema discovery in src/refs/cli.py using src/refs/models.py and src/refs/results.py. Expose exactly source-create, source-patch, source-record and result. Treat incoming CSL id as origin evidence, preserve supplied input and apply the same validator and identity rules as refs JSON. Pass the US1 tests and extend tests/integration/test_smoke.py with capture, correction and retrieval. Covers FR-001, FR-013, FR-047–048 and SC-009–010.

## Phase 6: US2 — Complete portable project export (P1)

**Goal:** Export the bounded bibliography profile with honest losses and safe replacement.

**Runnable check:** Cite and uncite several supported types, show projects, export twice, render through all three consumers, and prove blocked output and outside edits preserve existing bytes. Adopting a bibliography uses the importer delivered in US3.

- [x] T018 [US2] Write tests/contract/test_export.py and consumer fixtures under tests/fixtures/rendering/ with tests/integration/test_rendering.py. Cover all four report classes, all five closed blocking-loss codes, case-only duplicate keys, missing non-English language, corporate “ and ” names, date precision, titles, cleared values, empty selection, deterministic output, failure before publication, interruption after publication followed by a clean next export, and genuine outside edits. Define expected rendered authors, dates, publication, edition and protected spelling for Pandoc, Biber and classic BibTeX/elsarticle-num. Covers FR-037–039, FR-048 and SC-006/010.
- [x] T019 [US2] Complete the type-scoped portable serializer and value-dependent loss assessment in src/refs/bibliography.py against src/refs/data/bibliographic-coverage.json. Cover every slice 1 output type and field, preserving the distinction between article issue and report number, preprint repository data, traditional inbook, standard as misc, corporate names and patent extensions. Generate from current values and explicit clears; never execute original TeX. Report every affected entry before staging, and let --allow-unknown-mappings override only unknown losses for that invocation. Covers FR-002, FR-008, FR-037, FR-039 and FR-047–048.
- [x] T020 [US2] Complete project show/list-via-show and uncite in src/refs/projects.py and src/refs/cli.py, including no-op repeats, project revisions and removed-source diagnostics. Complete snapshot selection, destination/profile binding, pending_digest recovery, baseline guards and crash-safe publication in src/refs/bibliography.py and src/refs/files.py. Test failure before publication, recovery after publication, and genuine outside edits separately. Preserve overwritten outside bytes in originals. Keep first adoption blocked until T024 supplies proof of import. Run tests/contract/test_export.py and tests/integration/test_rendering.py; record consumer/style versions and actual results in specs/001-academic-catalog/reviews/slice-1-acceptance.md. Covers FR-016, FR-035–039 and SC-006.

## Phase 7: US3 — Import an existing bibliography (P2)

**Goal:** Bring a manuscript bibliography into the catalog without overwriting current decisions, then adopt its output explicitly.

**Runnable check:** Import mixed valid, conflicting and malformed entries; show originals and reasons; rerun without duplicates; use update to settle a value; adopt the exact imported file with explicit overwrite.

- [x] T021 [US3] Write tests/contract/test_import.py and synthetic fixtures in tests/fixtures/bibliography/. Include the audit's parser corruption cases, duplicate fields, missing-equals absorption, embedded entry markers, raw-byte preservation, partial batches, interrupted runs, conflicting identities, removed sources, unsupported constructs, explicit clears and lossy fallback re-import. Add the exact-digest adoption cases to tests/contract/test_export.py. Covers FR-018–022, FR-024, FR-038 and SC-002–003.
- [x] T022 [US3] Implement the guarded bibtexparser adapter in src/refs/adapters/bibtex.py. Retain independently captured raw input and entry offsets; decode supported text through pinned pylatexenc without altering URI/file fields. Apply type-scoped aliases, protection braces, ordered names, date/year/month agreement, legacy journal/address/school fields, traditional inbook and howpublished/note composition. Resolve only month macros; preserve unsupported commands, inheritance and macros with explicit limitations. Covers FR-002, FR-008, FR-018–020 and FR-047–048.
- [x] T023 [US3] Implement import runs in src/refs/importing.py and src/refs/migrations/001_initial.sql with “One row per actual import run: ID, origin, exact file digest, start/finish timestamps and aggregate counts (applied/unchanged/conflict/invalid); incomplete finish stays visible after interruption.” Commit each accepted entry and its counts with its original and identity; preserve conflicting/invalid originals without a status table. Never overwrite current values or revive a removed source. Report every entry, allow safe re-runs and expose supported file paths as links through the resource service delivered in T027. Until that service lands, retain those paths as explicit pending resource proposals in the report and originals, not as silently dropped data. Covers FR-018–022, FR-024 and SC-002–003.
- [x] T024 [US3] Wire import and add --format bib in src/refs/cli.py through the shared adapter and validators. Implement existing-file adoption in src/refs/bibliography.py: require a finished import of the exact digest, report current conflicts, and require --adopt --overwrite for replacement. Reject incomplete or unpartitionable proof and recheck actual bytes before publication. Do not treat key-only or lossy projection matches as permission to overwrite. Pass tests/contract/test_import.py and the adoption cases in tests/contract/test_export.py. Covers FR-001, FR-019–021, FR-024 and FR-038.
- [x] T025 [US3] Add tests/contract/test_mapping_convergence.py and tests/fixtures/mappings/ to compare refs JSON, CSL input and supported Bib input through the actual adapters. For each promoted slice 1 mapping assert a distinguishing value, contradictory aliases, edits, clears and the output assessment. Cover the four extension distinctions and all observed type families; scope Zotero-only input rows to the existing design probes, not a new runtime importer. Extend tests/integration/test_smoke.py with repeat import and adoption. Covers FR-047–048 and SC-002–003/010.

## Phase 8: US4 — Keep research files (P2)

**Goal:** Link existing files and safely copy new downloads into Unfiled.

**Runnable check:** Exercise add --file (copy), add --file --link, resource add (link), resource add --copy, keep-name, inspect/check/open/unlink, collisions, source changes and interruption. Original files survive every case. Re-run a Bib import with resource paths and verify the links are registered once.

- [x] T026 [US4] Write tests/contract/test_resources.py and tests/integration/test_copy.py with disposable files. Check the differing add/resource-add defaults, naming/fallback, unavailable library, changed source, destination collision, unsafe paths, bundles, interruption before publication and after publication before registration. Assert that a finished unregistered destination survives and that unlink/removal changes no bytes. Cover explicit open selection without launching real applications in tests. Covers FR-012, FR-025–027, FR-030–035 and SC-007.
- [x] T027 [US4] Add resources in src/refs/migrations/001_initial.sql with “Stable ID, source ID, revision, label/media type, absolute or named-root relative locator, verified digest for copied files.” and “Unique source/locator association.” Implement link, show inventory, resource check, unlink and open in src/refs/resources.py and src/refs/cli.py. Resolve containment safely, preserve missing locators, normalize in-library paths to the library root and never move bytes on root edits. Wire imported file paths from src/refs/importing.py as idempotent links, with unsupported path syntax reported. Covers FR-022, FR-025–027 and FR-032/034.
- [x] T028 [US4] Implement copy intake in src/refs/files.py using cat/staging: create a temporary copy, independently compare hashes and source stability, publish without overwrite, then register under a revision check. Keep the source in every outcome and never delete a published unregistered copy. Use the coordination lock and short transactions without holding a write lock while copying. Leave native metadata preservation, full flushes, directory syncing and journals deferred. Pass tests/integration/test_copy.py. Covers FR-030–034 and SC-007.
- [x] T029 [US4] Integrate add --file with default copy and --link, and resource add with default link and --copy, in src/refs/cli.py and src/refs/resources.py. Apply naming from src/refs/naming.py, validate --keep-name, show intended destinations and keep previews side-effect free. Return partial IDs/paths when metadata saves but copying fails; enable explicit linking of an inspected finished copy. Extend tests/integration/test_smoke.py with resource handling and rerun import resource checks from T021. Covers FR-012, FR-014, FR-022, FR-025–035 and SC-007.

## Phase 9: US5 — Recover the catalog (P2)

**Goal:** Produce a consistent snapshot and demonstrate restoring it into another home.

**Runnable check:** Back up the populated synthetic catalog, restore it into a new directory, open it through the CLI and compare all authoritative data. Refuse corrupt snapshots and nonempty restore destinations.

- [x] T030 [US5] Write tests/contract/test_backup.py for SQLite-consistent snapshots, configuration changes during capture, incomplete import runs, resource inventories, member hashes, partial output and no overwrite. Define restore comparisons and corruption/nonempty-destination failures in tests/integration/test_restore.py. Cover every table, corrected fields, original bytes, reserved keys, selected projects and missing resources. Covers FR-040–041 and SC-008.
- [x] T031 [US5] Implement backup in src/refs/recovery.py and src/refs/cli.py with SQLite's backup API and the coordination lock. Publish a verified new snapshot directory containing catalog.sqlite, config.toml, resources.jsonl and manifest.json, with external_contents_included=false. Include all ten tables; never copy only the live SQLite main file or pretend the inventory includes attachment bytes. Covers FR-040 and SC-008.
- [x] T032 [US5] Write the exact manual restore and SQLite hot-journal recovery commands in docs/restore.md and exercise those same steps in tests/integration/test_restore.py. Validate schema, paths, hashes, integrity and foreign keys; restore into a second empty home, open it with refs, compare saved identities and decisions, and report missing files without changing them. Document that only one mutating home may control shared targets and restore grants no overwrite permission. Record the successful restore proof in specs/001-academic-catalog/reviews/slice-1-acceptance.md. Do not add a restore/recover CLI. Covers FR-017, FR-041 and SC-008–009.

## Phase 10: US6 — See and control effective settings (P2)

**Goal:** Complete configuration inspection and permitted paper-local defaults.

**Runnable check:** Inspect paths/settings before initialization, select two disposable projects, inspect each value's origin, disable discovery, and reject invalid location or naming overrides without writes.

- [x] T033 [US6] Write tests/contract/test_config.py for flag/environment/user precedence, nearest .refs.toml discovery including Git worktrees, explicit selection/disable, allowed project keys, invalid values and missing/unwritable locations. Assert no fallback initialization and no mutation from inspection or invalid configuration. Covers FR-043–046 and SC-009.
- [ ] T034 [US6] Complete src/refs/config.py and full config show; retain the basic paths command from T003 in src/refs/cli.py. Implement the exact precedence, policy defaults and project restrictions in contracts/cli.md; expose effective values and origins before init, and preserve existing data/preferences on repeat init. Validate templates, policy lists, roots and unsupported profiles, and return actionable catalog_missing/home_not_writable diagnostics. Re-run the naming and export tests with permitted overrides; extend tests/integration/test_smoke.py with settings inspection. Covers FR-043–046 and SC-009.

## Phase 11: Acceptance and packaging

**Goal:** Verify the complete slice, measure its actual weight, and prepare the owner's real-paper trial.

- [ ] T035 Complete README.md with installed usage, the 23 approved invocations, four schemas, copy/link defaults and the link to docs/restore.md. Verify the built wheel includes src/refs/data/ and the schema, run uv sync --locked plus the configured lint/type/test checks, and run the single installed smoke test in tests/integration/test_smoke.py through all six stories. Exercise every command in offline tests, and record results and remaining limitations in specs/001-academic-catalog/reviews/slice-1-acceptance.md. Covers FR-013, FR-017 and SC-002–010.
- [ ] T036 Measure application source lines, command names/invocations, classes and governing doc words per source line in specs/001-academic-catalog/reviews/slice-1-acceptance.md, alongside the recorded git-muster and canvas-ledger comparison in docs/right-sizing.md. Present the third checkpoint to the owner when code is complete. Budgets prompt judgment, not automatic cuts; do not expand scope to improve a metric.
- [ ] T037 After the owner selects a paper and authorizes any real-file replacement, carry out the capture → find → correct → open → cite → export workflow and render without the catalog. Record actual consumer versions, results, missing capabilities and unused surface in specs/001-academic-catalog/reviews/slice-1-acceptance.md. Keep this task pending if paper/access authorization is absent; do not substitute synthetic results. This is SC-001 and the gate before any slice 2 specification, not permission to migrate Zotero or build later slices.

## Dependencies and runnable milestones

```text
Setup → Foundation → US1 early → US2 early → M1: one-reference export
                                            ↓
US1 completion → US2 completion → US3 → US4 → US5 → US6
                                                      ↓
                         installed acceptance → owner checkpoint → real paper
```

M1 ends at T010; it does not wait for generated keys, general import, file intake or backup. T013–T017 then complete source behavior, and T018–T020 complete portable output. US3 adds the importer needed for existing-file adoption. US4 completes US3's file-link integration. These shared dependencies are explicit: the US2 phase runs against new outputs on its own; the US3 phase runs bibliographic import on its own; full adoption and file-link acceptance are checked after their prerequisites land. US5 backs up the data delivered by preceding stories. US6 extends the working explicit-path configuration from T003. All later phases keep the earlier runnable paths working.

The project has one initial schema during development. After T034 it contains exactly the ten logical tables in data-model.md. Do not add placeholder tables for the deferred ledger. The first usable release is the complete slice, including restore; M1 is its first demonstrable milestone.

## Parallel execution examples

| Story | Safe opportunity |
| --- | --- |
| US1 | After T010, T011 and T012 can run together because their test files are disjoint. Implementation remains ordered because models, naming and source mutations depend on one another. |
| US2 | No tasks marked parallel: the first export depends on project selection, and the completion tasks share bibliography/CLI files. Consumer fixtures can be prepared independently within T018, before implementing T019. |
| US3 | No tasks marked parallel: parser output feeds import identity and adoption. Do not concurrently edit the export tests from another phase. |
| US4 | No tasks marked parallel: resource registration precedes copy integration. Synthetic input preparation within T026 can be split by collision and interruption cases if needed. |
| US5 | No tasks marked parallel: the documented restore proof follows the actual snapshot format. |
| US6 | No tasks marked parallel: configuration tests precede the implementation that changes command defaults. |

Parallelism is optional. No agent delegation or extra review round is implied.

## Requirement coverage

Each individual active identifier is listed to keep traceability intact. SC-001 is an owner-assisted acceptance task, not a claim of build-time completion.

| ID | Tasks | ID | Tasks |
| --- | --- | --- | --- |
| FR-001 | T004–T006, T013, T017, T024 | FR-002 | T005, T013, T019, T022 |
| FR-003 | T004–T006, T012, T014 | FR-004 | T006, T012, T015 |
| FR-005 | T005–T006, T013, T015 | FR-006 | T011, T014 |
| FR-007 | T011–T012, T014 | FR-008 | T011, T013–T014, T019, T022 |
| FR-009 | T011, T013–T014 | FR-010 | T011, T013–T014 |
| FR-011 | T011, T014, T016 | FR-012 | T011, T014, T026, T029 |
| FR-013 | T002, T017, T035 | FR-014 | T002–T004, T012, T015, T029 |
| FR-015 | T012, T016 | FR-016 | T016, T020 |
| FR-017 | T002–T003, T016, T032, T035 | FR-018 | T021–T023 |
| FR-019 | T021–T022, T024 | FR-020 | T004, T006, T021–T023 |
| FR-021 | T015, T021, T023–T024 | FR-022 | T023, T027, T029 |
| FR-024 | T021, T023–T024 | FR-025 | T026–T027, T029 |
| FR-026 | T026–T027 | FR-027 | T026–T027 |
| FR-030 | T026, T028–T029 | FR-031 | T026, T028–T029 |
| FR-032 | T027–T029 | FR-033 | T026, T028–T029 |
| FR-034 | T026–T029 | FR-035 | T012, T015, T020, T026–T029 |
| FR-036 | T007–T008, T020 | FR-037 | T007, T009, T018–T020 |
| FR-038 | T007, T009, T018, T020–T021, T024 | FR-039 | T009, T018–T020 |
| FR-040 | T030–T031 | FR-041 | T030, T032 |
| FR-043 | T033–T034 | FR-044 | T003, T033–T034 |
| FR-045 | T033–T034 | FR-046 | T033–T034 |
| FR-047 | T005, T013, T017, T019, T022, T025 | FR-048 | T013, T017–T019, T022, T025 |
| SC-001 | T037 | SC-002 | T021–T025, T035 |
| SC-003 | T021–T025, T027, T029, T035 | SC-004 | T011–T014, T026, T029 |
| SC-005 | T012, T016–T017 | SC-006 | T007, T009–T010, T018–T020, T024 |
| SC-007 | T026–T029 | SC-008 | T030–T032 |
| SC-009 | T002–T003, T012, T017, T033–T035 | SC-010 | T013, T017–T019, T022, T025 |

Deferred FR-023, FR-028, FR-029, FR-042 and FR-049 have no implementation tasks. There are no tasks for collection tables, moves, journals, native filesystem metadata preservation, request replay, import administration, saved export waivers/projections, plugin selection, full restore CLI, or the deferred performance/process matrix.
