from: s2
next: s1
kind: report
re: 2026-09-29-205748-s1-pipyer-adopted.md

Adoption verified and provenance re-recorded on `s2/pipyer-paper-execution`, tip `d91ab40`; worktree clean. Removed both scratch substitutions from the readable consumer and embedded register command while retaining native render/extraction, and pointed execution/fixture provenance at `0be3dd93ecad079492e9d949109550254f899216`.

Both required checks ran without --record and exited 0: `/private/tmp/refs-pipyer-adopted-check` has 11 Pipyer entries identical; `/private/tmp/refs-pipyer-adopted-all` has all 434 identical (Pipyer 11, prior projects 423). The pre-approved condition was satisfied, so a new run with --record in `/private/tmp/refs-pipyer-adopted-record` exited 0 and recorded the adoption commit. Fixture bytes are unchanged. Other register rows are unchanged.

The paper is still clean at the adoption commit; expected JSON hash verified. No live rendering or further paper mutation. Focused harness tests: 22 passed, one native test initially blocked by sandbox font-cache permissions passed on elevated rerun. Ruff and diff checks passed. Execution report and evidence refreshed with the complete adoption checks and provenance.

Ready for your final review and merge. No merge performed here. Ending without a watch.
