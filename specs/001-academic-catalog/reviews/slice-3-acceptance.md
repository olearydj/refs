# Slice 3 acceptance

## Status

T052–T060 are implemented and the supplied disposable sample passed all three move-integrity scenarios. T061 verification is complete; the build is stopped for owner review. T062–T067 remain owner-executed and have not run. This record does not authorize the real cutover.

One placement decision remains open: the current assignment rule leaves thomas-2025-aiValue and zhang-2023-exploringMIT without loc. Their files were already managed under Unfiled in the sample. The tool follows the contract's Box-folder, single-collection, otherwise-no-assignment rule. The owner has been asked whether to add an existing-managed-folder fallback or set these locs explicitly.

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

T062–T067 have not run. Resolve the two locs above, retain the required CCC backup and use the documented explicit schema upgrade on the selected catalog before real assignment or reorg. Ordinary commands never upgrade an existing catalog. The owner then performs assignment preview/apply, reorg preview/execute, resource check, vault repair and final acceptance. No commands against the live catalog, attachment trees or vault were executed for this rehearsal.
