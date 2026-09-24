# Tests pass acceptance, 2026-09-24

## Status and scope

The tests pass is complete through phase 7 on the evidence below. The work began with the [test investigation](2026-09-24-test-review-investigation.md) and the accepted [brief](../plan.md#tests-pass-brief-trust-the-suite). Phases 1–5 are recorded in the [progress report](2026-09-24-tests-pass-progress.md); the owner accepted the [phase 6 report](2026-09-24-tests-pass-phase-6.md) at `f8de451`. The final four repair commits are `1e88ba6` (D2), `52b8777` (month names), `b62f97c` (translator) and `2f4319d` (empty key). This record uses the final verification run after those commits. No owner catalog or attachment tree was opened by that verification.

## Test design and coverage

The [testing convention](../../../docs/testing-convention.md) names the source of expected results, pins refusal codes and unchanged state, and requires a falsifiable invariant for generated tests. Phase 4 rewrote 49 named tests, added seven, and deleted none because every reviewed case retained a distinct behavior. The progress report gives a disposition for each previously unasserted error code. Phase 5 added eight Hypothesis invariants: BibTeX partition refusal, parse–serialize–parse stability, identifier normalization, generated key syntax, collision suffix uniqueness, loc normalization, zero month/day refusal and protected title spans. Its restore test resumes a recorded move in a second home.

The final coverage command, run from the repository root, was:

```sh
COVERAGE_PROCESS_START="$PWD/.coveragerc" PYTHONPATH="$PWD/tests/coverage_bootstrap${PYTHONPATH:+:$PYTHONPATH}" uv run --locked coverage run -m pytest -q && uv run --locked coverage combine && uv run --locked coverage report --skip-covered
```

It passed 624 tests and measured **87% combined line and branch coverage** over `src/refs`: 3,829 statements with 398 missed, and 1,696 branches with 258 partial. Coverage is a measured data point, not a release threshold. The ordinary `uv run --locked pytest -q` also passed 624 tests in 127.82 seconds. `uv sync --locked`, `ruff check .` and `ty check src/refs` passed. `scripts/demo.sh --smoke` passed 121 checks. `tests/fixtures/real-trial/run.sh` reported zero failures; its library check retained 556 supplied author lists, two editor-only records and four without supplied creators.

## Guards and phase 7 contract decisions

The guard tests verify that removing a cited source retains its managed file bytes and existing bibliography, that a foreign destination after publication cannot be adopted or deleted, that a second process times out on the file lock with exit 6, and that remove preview leaves the catalog bytes unchanged. The revised export guard creates two actual record shapes: one whose issued precision cannot be projected and one with competing eprint identities. `issued_date_lost_or_changed` and `work_identity_changed` each block export through the public command while leaving the target bytes, staging area and baseline digest unchanged. The three loss codes without detectors were removed; the blocking class and its two tested detectors remain. The closed list grows only with a detector and a test.

D2 also aligned the unlink and reactivate revision options with the CLI, made an edited title drop unmatched protected terms with one named warning, and made the SQLite sync-folder caution visible in the configuration contract and `init --help`. FR-044 now states that caution as guidance rather than an unenforceable location rule. The `--version` promise remains for the release pass, as decided in the brief.

## Rehearsal and corpus dispositions

Phase 6 ran only on the owner-supplied copy at `/Volumes/Casa/tmp/refs-rehearsal-20260924`, creating and removing its own working homes. Ten actual refs-command SIGKILL points all resumed with matching digests and final `removed` operation states; move findings were zero. Daily use began by removing a source with a managed file: its file SHA-256 and the existing exported bibliography SHA-256 were unchanged, and reactivation restored the source. The phase 6 report records the per-boundary states and digests.

The bounded corpus used 18 files and accounted for all 3,949 entry spans: 2,704 applied, 212 unchanged, 711 conflict and 322 invalid on first import. Re-import applied zero. Eight writable exports rendered through Pandoc; three blocked by recorded codes, five bulk project citations refused overlapping import origins, and two selections were empty. Resource check and backup–restore completed. Wall time was 316.30 seconds and peak additional physical disk was 409 MB, below the 15-minute and 2-GB ceilings. The full per-file outcomes and reasons remain in the phase 6 report.

Three corpus gaps now have minimized fixture tests: `month-name.bib` admits full English month names and equivalent numeric or three-letter forms; `translated-chapter.bib` records translator as a documented portable omission while keeping the cited author; `empty-key.bib` reports `invalid_bib_entry` at byte 0 and retains the original bytes. The remaining cases are recorded limits: entries without a usable title, URL or book part; unsupported entry types; unsupported TeX or math; malformed creators; and TeX-escaped URLs. The import contract says originals remain preserved when admission or export refuses them. Existing identity conflicts and overlapping import origins remain explicit; no bulk overwrite or origin guess was added. Linked fixture paths that have no copied attachment bytes remain correctly reported missing. The `.DS_Store` scan polish item remains outside this pass.

## Acceptance boundary

The investigation examples have dispositions in the progress report, and the convention now governs new tests. The larger rehearsal's move and daily-use parts had zero findings. Its corpus findings were either turned into a rule and minimized regression fixture or recorded as an explicit limitation. The suite, demo and real-trial harness are green after phase 7. This tests pass did not perform the separate source-code design review, release wheel-install gate, logging pass or help-system work named later in the plan.
