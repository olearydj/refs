from: s2
next: s1
kind: report
re: 2026-09-27-205011-s1-exit-code-for-missing-fixtures.md

Ready for review: `s2/check-missing-fixtures-exit` at `f5a6284`, based on main `0dc67c0`, worktree `/Volumes/Casa/dev/refs/worktrees/check-missing-fixtures-exit`.

Chose exit **3**, the next unused code after 0 (identical accepted gate), 1 (failure) and 2 (invalid invocation). It means all consumers rendered/extracted successfully and absent accepted fixtures are the only finding, including a first `--record` run's pre-record status. An existing fixture's changed or missing entry, or any consumer/project error, takes precedence and returns 1 even when another fixture is absent. Newly extracted entries without a baseline retain their existing `changed` rows for review, but are not treated as changes against an accepted fixture. JSON exit_code and process status agree. Recording behavior is otherwise unchanged.

One detail found in the implementation: changed-only gates previously returned 0 (an existing test explicitly pinned it), despite the task's description. I changed that to 1 as your requested rule says and updated that regression test. The README now lists all four codes in one sentence.

Verification: 22 focused CLI/extraction checks pass; full suite **1123 passed in 38.86s** with TEXMFVAR and TEXMFCACHE set to `/private/tmp/refs-csl-tex-cache`; Ruff, `ty check src/refs` and `git diff --check` pass. Tests cover first missing-fixture checks and recording, subsequent identical status, and absent-fixture precedence alongside identical, changed, missing or failed consumers, while checking real inputs and fixtures remain unchanged. Full log `/private/tmp/refs-missing-fixtures-full.log`.

No merge performed. Ending this turn without polling; queue the next message when ready.
