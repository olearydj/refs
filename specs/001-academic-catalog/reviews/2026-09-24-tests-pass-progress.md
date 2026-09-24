# Tests pass progress, 2026-09-24

## Phase 4

The rewrite follows the investigation's weak-assertion examples at lines 36–40, refusal examples at lines 44–48, layer finding at lines 50–52, and missing command options at line 75. Relative to the accepted phase 3 baseline `811547b`, 49 named test functions were rewritten, seven were added, and none was deleted. The added functions include parameterized cases, so the collected case count rose from 596 to 610 before the final error-code additions. Pure tests were moved to `tests/unit`; tests that open SQLite or exercise file effects were moved to `tests/integration`. The two-process allocation test now holds `BEGIN IMMEDIATE` until both subprocesses announce that they reached the catalog write boundary.

The recorded coverage command is `COVERAGE_PROCESS_START="$PWD/.coveragerc" PYTHONPATH="$PWD/tests/coverage_bootstrap${PYTHONPATH:+:$PYTHONPATH}" uv run --locked coverage run -m pytest -q && uv run --locked coverage combine && uv run --locked coverage report --skip-covered`. It ran 610 tests and measured 87% combined line and branch coverage over `src/refs` (3,816 statements, 405 missed, 1,692 branches, 264 partial branches). The demo passed 121 checks and the real-trial harness reported zero failures. Coverage is a measurement, not a gate.

No test was deleted: each weak case had a distinct behavior to keep. The hash-call-count test in `test_moves.py` was deliberately kept because the file contract explicitly requires hashing each original and destination twice; the digest and recovery tests guard the result separately. An `open --resource` CLI test uses an unavailable synthetic resource ID so that it exercises argument parsing without launching a desktop application.

The table below gives a disposition for each literal `RefError` code defined in `src/refs` that was absent as an asserted code string in the tests at the phase 4 audit. "Boundary guard" names an existing test that checks the behavior and state at risk through a broader public error. "Removal candidate" means the later code review must decide whether the branch deserves a direct test or can be removed; no code removal is approved here. Safety branches in that class should gain direct tests if reachable. This static inventory does not prove that a branch is reachable.

| Code | Disposition | Evidence or next check |
| --- | --- | --- |
| `alias_conflict` | Boundary guard | Alias disagreement is pinned as `invalid_bib_entry` with the conflicting-alias message in mapping convergence. |
| `backup_incomplete` | Boundary guard | Snapshot interruption leaves a partial directory and no published snapshot in `test_backup.py`. |
| `citation_key_required` | Removal candidate | Check whether the public parser can reach this branch after record validation. |
| `date_conflict` | Boundary guard | Patent issue date versus date is refused in `test_zotero_patent_date.py`. |
| `destination_changed` | Boundary guard | Pre-delete destination change keeps the original in `test_moves.py`. |
| `export_intent_conflict` | Removal candidate | No test independently changes pending export intent. |
| `export_published_unrecorded` | Boundary guard | Interrupted publication records pending digest and recovers in `test_skeleton_export.py`. |
| `import_missing` | Removal candidate | Add a missing-batch command case if this is a supported user correction. |
| `import_origin_ambiguous` | Removal candidate | Add two runs with one origin and assert the selection policy. |
| `import_partial` | Boundary guard | Mixed BibTeX input returns a partial envelope and per-entry statuses in `test_import.py`. |
| `integrity_error` | Boundary guard | Copy and move digest mutations retain originals in `test_copy.py` and `test_moves.py`. |
| `invalid_attachment_path` | Removal candidate | Test stored and base-relative traversal through the Zotero adapter. |
| `invalid_bib_input` | Removal candidate | Check whether `add --format bib` with multiple entries reaches this code. |
| `invalid_export_value` | Boundary guard | Unsafe TeX content is projected safely in `test_skeleton_export.py`. |
| `invalid_key` | Removal candidate | Add a direct invalid-key command case if this parser branch remains public. |
| `invalid_loc` | Boundary guard | Invalid loc CLI refusal and unchanged catalog are checked in `test_loc.py`. |
| `invalid_locator` | Removal candidate | Check an absent resource path and root pair. |
| `invalid_patch` | Removal candidate | Add a malformed `--set` JSON or patch-file case. |
| `invalid_project` | Removal candidate | Distinguish missing project from other citation failures. |
| `invalid_query` | Removal candidate | Add malformed search syntax if the branch is reachable. |
| `invalid_status` | Removal candidate | Exercise `import show --status` with an unsupported value. |
| `invalid_zotero_item` | Boundary guard | Malformed Zotero items have per-entry invalid outcomes in `test_zotero_import.py`. |
| `key_author_required` | Boundary guard | Creator normalization refuses unsupported spelling in naming tests. |
| `key_conflict` | Removal candidate | Add a CLI key collision case with unchanged source keys. |
| `open_failed` | Removal candidate | A direct test would need a synthetic launcher seam; no desktop application may be launched. |
| `project_ambiguous` | Removal candidate | Check duplicate project-name admission if the schema permits it. |
| `recovery_required` | Removal candidate | Distinguish an unfinished catalog from a missing catalog in a command test. |
| `resource_conflict` | Removal candidate | Check a copy directed at a resource that records another source file. |
| `revision_required` | Boundary guard | Executing reconcile without a preview token is refused in `test_import_reconcile.py`. |
| `root_unavailable` | Removal candidate | Exercise a named root absent from configuration. |
| `source_ambiguous` | Removal candidate | Check duplicate source selection if it is representable. |
| `source_missing` | Removal candidate | Add a missing-key command with the public error code. |
| `staging_changed` | Boundary guard | Staged retry with a foreign staging inode never deletes it in `test_moves.py`. |
| `unadopted_target` | Boundary guard | Existing unadopted bibliography remains untouched in export tests. |
| `unknown_creator_role` | Removal candidate | Feed an unsupported Zotero creator role and preserve the item outcome. |
| `unknown_schema` | Boundary guard | Unknown schema request is refused in `test_interface.py`. |
| `unknown_zotero_type` | Removal candidate | Exercise an unsupported native Zotero type. |
| `unpartitionable_input` | Boundary guard | Malformed BibTeX corpus entries are reported in `test_import.py`. |
| `unsupported_attachment` | Removal candidate | Exercise an unsupported Zotero attachment link mode. |
| `unsupported_file_expression` | Removal candidate | Exercise an unsupported BibTeX file expression without reading external files. |
| `unsupported_format` | Boundary guard | Capture format refusals are checked in `test_capture.py`. |

`staging_volume_mismatch`, `invalid_kind`, `project_conflict`, `invalid_arguments`, and `import_origin_missing` gained direct code assertions after the coverage run above and are absent from the remaining inventory. The final phase 4 commit will rerun the full gate with these additions.

## Phase 5

Hypothesis `6.168.0` resolved under the project's three-day cooldown and is locked as a development dependency. Eight named properties cover partitioning arbitrary bytes, a supported book's parse–serialize–parse round trip, identifier normalization idempotence, key syntax, preserved-name collisions, loc normalization, date zeros, and protected title terms. Each has a falsifiable invariant in its docstring and at least one saved explicit example from a real shape or boundary. The first run found two test mistakes rather than product defects: an exported bibliography entry must be partitioned before the one-entry parser reads it, and an all-stopword title may correctly refuse key generation with `citation_key_required`. The corrected properties pass without changing `src/refs`.

The new restore test captures a move at the recorded state, backs up the catalog, restores it into a second temporary home with the documented procedure, resumes reorg, and checks the resource pointer, operation state, and file digest. No owner files are involved.

The corpus pilot classified the five bibliography copies under `tests/fixtures/real-trial/papers`: 7 DEMA entries, 11 Danvas entries, 292 dissertation entries, 41 manufacturing entries, and 11 Pipyer entries. All 362 entries partitioned and parsed individually, with zero file-level refusals and zero invalid entries. The existing real-trial run then reported zero failures for import, re-import, project export, rendering comparison, copy intake, and backup. This pilot uses the repository copies only; the larger phase 6 corpus and owner-supplied catalog copy have not been run.

The phase 5 gate passed: 620 tests, Ruff clean, ty clean, demo 121 checks, and real-trial failures 0. The phase 4 coverage measurement above predates the nine new phase 5 test cases; no coverage percentage is claimed for the enlarged suite yet.
