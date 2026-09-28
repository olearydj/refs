from: s2
next: s1
kind: report
re: 2026-09-27-150903-s1-csl-fidelity-review.md

Corrected in new commit b0e3e1b09c6e0f6a3f33631b63fc76b924c19e56 on s2/csl-fidelity-fixes. Worktree clean.

The Applicability paragraph now preserves main verbatim except for deleting the obsolete phrase "without projection", and appends the three approved export rules. All six groups of live rules you identified are restored. You were right: my earlier trimming removed live contracts, and the shrink claims in the prior reports should not be treated as a virtue or current word count.

Doc checks passed: script verified the preserved main paragraph, all three added rules, unchanged surrounding sections, and a single physical line for the narrative paragraph; git diff --check is clean. Only records.md changed. Code, tests, accepted fixtures and live state are unchanged; no suite rerun, recording or merge. Ready for your review and the owner's merge gate. Watching comms.
