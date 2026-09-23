# Slice 3 acceptance

## Status

T052–T060 are implemented and the supplied disposable sample passed all three move-integrity scenarios. T061 verification is complete; the build is stopped for owner review. T062–T067 remain owner-executed and have not run. This record does not authorize the real cutover.

The placement decision is resolved by the owner's pre-cutover rules below. T061a is complete. The earlier rehearsal is retained here as historical evidence; its collection fallback and two unassigned managed sources are superseded.

## Real sample and results

Input: /Volumes/Casa/tmp/refs-rehearsal-20260923. Only this supplied copy was read. Each scenario copied it into a fresh temporary home and remapped attachment locators before moving. The harness hashed the input files before and after all scenarios and verified they were unchanged. The sample and retained homes have not been deleted.

Actual sample counts are 575 sources and 556 resources on 510 sources. There are 65 sources without files, not 11; all 65 kept empty loc. Assignment applied 503 Box-folder locs and 5 single-collection locs. The two remaining sources are the pre-existing managed Unfiled cases above.

The command was:

```sh
uv run --locked python tests/fixtures/real-trial/move_rehearsal.py --sample /Volumes/Casa/tmp/refs-rehearsal-20260923
```

Actual JSON output follows. The findings count covers move-integrity assertions, not the open placement decision.

```json
[
  {
    "scenario": "clean",
    "resources": 556,
    "moves": 554,
    "unlinked_files": 50,
    "findings": 0,
    "home": "/private/var/folders/d3/2qdml55n4vd1lcrt4q_5dl3w0000gn/T/refs-move-rehearsal-r67h9naw/home"
  },
  {
    "scenario": "published_uncommitted",
    "resources": 556,
    "moves": 554,
    "unlinked_files": 50,
    "findings": 0,
    "home": "/private/var/folders/d3/2qdml55n4vd1lcrt4q_5dl3w0000gn/T/refs-move-rehearsal-bv_ls45j/home"
  },
  {
    "scenario": "recorded",
    "resources": 556,
    "moves": 554,
    "unlinked_files": 50,
    "findings": 0,
    "home": "/private/var/folders/d3/2qdml55n4vd1lcrt4q_5dl3w0000gn/T/refs-move-rehearsal-8e20jhs2/home"
  }
]
```

In every scenario all 556 resources retained their IDs and matching digests and resolved under the library. There were 556 distinct recorded paths, no missing moved files, and no staging files left. The library had one additional pre-existing .DS_Store. All 554 operations finished as removed; the two already-managed Unfiled resources needed no move. A subsequent reorg was a no-op.

All 40 storage attachments moved into their sources' loc folders. The eight colliding snapshots in papers/aiml produced 2310.html and 2310-b.html; 2311.html, 2311-b.html and 2311-c.html; and 2402.html, 2402-b.html and 2402-c.html. Thus three names were retained and five received suffixes. The clean run and both actual SIGKILL/resume runs produced the same names.

Each retained home contains assignments.json and move-report.json with the complete assignments, operation IDs, old/new paths and untouched-file list.

## Untouched and failed items

Each completed report lists 50 untouched files: seven .DS_Store files, 37 .zotero-ft-cache files, one .zotero-ft-info file, and these five PDFs, relative to tree/Box:

- lib/ds-ml-ai/Thomas et al. - 2025 - AI Value Creators.pdf
- lib/e-ship/ZeroToSoldMobile-2020.pdf
- lib/sw-dev/carpentry/Johnson - 2023 - Boost Your Git DX Make your Git development exper.pdf
- lib/sw-dev/carpentry/Johnson - 2023 - Boost Your Git DX Make your Git development exper2.pdf
- papers/aiml/ExploringMITCurricwithLLM-2023.pdf

Their hashes were unchanged. Reports cover the moved folders; they do not claim an inventory of unrelated folders elsewhere in the supplied tree. The pre-existing library .DS_Store also remains unrecorded and untouched.

The first real run failed its untouched-file assertion because that scan compared NFD disk names with NFC catalog paths. The actual move had completed and passed resource-digest checks. The scan now compares normalized NFC paths, with a regression using the Büttner filename shape. All three scenarios were rerun from fresh copies and passed. The initial diagnostic home is /private/var/folders/d3/2qdml55n4vd1lcrt4q_5dl3w0000gn/T/refs-move-rehearsal-0jf7ck7l/home. No failed operations remain in the three final homes.

## Verification and size

Final verification from the repository root:

- uv sync --locked passed; 24 packages resolved and 23 checked.
- uv run --locked pytest: 583 passed in 118.86 seconds.
- uv run --locked ruff check .: All checks passed.
- uv run --locked ty check src/refs: All checks passed.
- scripts/demo.sh --smoke: PASS refs demo: 121 checks (US1, US2, US3, US4, US5, US6).
- tests/fixtures/real-trial/run.sh: Trial failures: 0. Full log: /private/tmp/refs-trial-dui0v1pb/run.log.

The restore tests execute the documented procedure after both publication-before-state-commit and recorded-before-delete interruptions. They verify identical operation rows, loc, resource IDs and visible unfinished status in the second temporary home. Attachment and staging bytes are excluded from the snapshot; the tests do not claim those bytes were restored.

T060's follow-up commit is 0b24066. The harness implementation was committed as 924a818. T061 records the final verification and stops before any owner-executed task.

Relative to c836a0a, application Python grew from 4,206 to 4,653 lines, a delta of 447 against the roughly 700-line estimate. The two new migration files add 41 SQL lines. The one-time assignment tool is 65 lines; rehearsal code and tests are counted separately. The schema adds one sources.loc column and one file_operations table, for 15 logical tables total. No runtime dependency was added; the four dependencies and three-day cooldown remain unchanged. Reorg is the only new installed command.

The resource ID in file_operations is historical and deliberately has no foreign key; application validation checks existence at operation creation. The owner confirmed this choice so completed history survives unlink.

Earlier build verification found that the old bibliography harness could follow absolute attachment paths in copied BibTeX inputs. An early run may have read those links; it did not modify owner files. The committed isolation wrapper now copies inputs to temporary storage, neutralizes attachment fields, and on macOS denies reads and writes to the live refs, Box and Zotero locations. Subsequent runs use that wrapper.

## Owner-executed cutover

T062–T067 have not run. Retain the required CCC backup and rename the intake folder as T062a directs before real assignment or reorg. The next catalog open upgrades automatically after a safety copy; record its path here from the owner's output. The owner then performs assignment preview/apply, reorg preview/execute, resource check, vault repair and final acceptance. No commands against the live catalog, attachment trees or vault were executed for this rehearsal.


## T061a: revised placement and lowercase folder

Initial assignment now uses the Box-tree folder, otherwise the managed-file folder relative to the library, otherwise `unfiled` for non-topic storage. Collections do not determine placement. Migration 005 upgrades the catalog to schema 5, rewriting the old capitalized source loc and leading managed relative-path segment while preserving IDs and locator formatting. It never renames a directory. The owner performs the real folder rename once with `mv`; only fresh temporary rehearsal copies were renamed here.

The same rehearsal command above was rerun. Each home retains `assignment-preview.json`, `assignments.json` and `move-report.json`. Actual output:

```json
[
  {
    "scenario": "clean",
    "resources": 556,
    "sources_with_files": 510,
    "sources_assigned": 510,
    "fileless_sources": 65,
    "moves": 554,
    "already_placed": 2,
    "unlinked_files": 50,
    "findings": 0,
    "home": "/private/var/folders/d3/2qdml55n4vd1lcrt4q_5dl3w0000gn/T/refs-move-rehearsal-ia1qmb2d/home"
  },
  {
    "scenario": "published_uncommitted",
    "resources": 556,
    "sources_with_files": 510,
    "sources_assigned": 510,
    "fileless_sources": 65,
    "moves": 554,
    "already_placed": 2,
    "unlinked_files": 50,
    "findings": 0,
    "home": "/private/var/folders/d3/2qdml55n4vd1lcrt4q_5dl3w0000gn/T/refs-move-rehearsal-jjnbsl3k/home"
  },
  {
    "scenario": "recorded",
    "resources": 556,
    "sources_with_files": 510,
    "sources_assigned": 510,
    "fileless_sources": 65,
    "moves": 554,
    "already_placed": 2,
    "unlinked_files": 50,
    "findings": 0,
    "home": "/private/var/folders/d3/2qdml55n4vd1lcrt4q_5dl3w0000gn/T/refs-move-rehearsal-wefu4c7a/home"
  }
]
```

Every scenario assigned 510 of 510 sources with files; all 65 file-less sources remained unplaced. The five storage-only sources bailenson2018exper, creswell2019educa, likert1932techn, roscoe1971incre and shabanov2024effor received `unfiled`. The two managed sources thomas-2025-aiValue and zhang-2023-exploringMIT received their managed folder, now `unfiled`.

The actual move count is 554, plus two resources already correctly placed after the simulated folder rename. All 556 resources were verified under the library with matching digests and distinct paths. Moving those two again would contradict reorg's mismatch-only selection. All 40 storage attachments moved. The eight snapshots retained exactly the three original and five suffixed names listed above in every scenario. Both kill-and-resume scenarios completed without missing or duplicated files. No operations failed; the same 50 unrecorded files and the library's pre-existing .DS_Store remained untouched. The supplied sample's hashes were unchanged, and it was not deleted.

Verification: `uv sync --locked` passed; `uv run --locked pytest -q` reported 584 passed in 126.41 seconds; Ruff and ty both reported all checks passed. Demo output was `PASS refs demo: 121 checks (US1, US2, US3, US4, US5, US6)`. The real-input harness reported `Trial failures: 0`; its log is `/private/tmp/refs-trial-4n9xoyhf/run.log`. The new migration regression verifies that the filesystem retains its old directory name until the owner renames it. No live catalog or attachment tree was changed. T062–T067 remain unchecked.


## T061b: automatic catalog upgrades

Owner decision, 2026-09-23: "normally it is handled automagically"; "agree with A". Opening a supported older catalog now saves a consistent SQLite safety copy under the existing file lock, then applies pending migrations. Read commands and dry runs follow the same path. Human output prints one line naming the upgrade and copy; the JSON envelope includes a schema_upgraded warning. The assignment tool also retains the notice in its JSON report. A denied safety copy leaves the old database unchanged and returns unsupported_schema. A newer schema still refuses. Existing dated copies are not overwritten, and initialization remains explicit.

Regression checks cover text and JSON read-command upgrades, no repeated notice on a second open, safety-copy refusal, newer-schema refusal, dry-run upgrade without creating the proposed project, and upgrade while the file lock is already held. All fixtures use temporary paths. Final verification: uv sync --locked passed; pytest reported 590 passed in 127.36 seconds; Ruff and ty reported all checks passed. Demo: PASS refs demo: 121 checks (US1, US2, US3, US4, US5, US6). Real-trial harness: Trial failures: 0, with log at /private/tmp/refs-trial-1x3626m0/run.log.

Application Python is 4,716 lines, up 60 in T061b and 510 from the slice baseline of 4,206, within the roughly 700-line estimate. No table, dependency, migration file or installed command was added in T061b. The owner-only T062a now follows the CCC backup and precedes assignment: rename the physical Unfiled folder to unfiled with mv, then let the first catalog open upgrade automatically. The actual live safety-copy path remains pending owner output; no live catalog was opened and no owner step was run. T062, T062a and T063–T067 remain unchecked.
