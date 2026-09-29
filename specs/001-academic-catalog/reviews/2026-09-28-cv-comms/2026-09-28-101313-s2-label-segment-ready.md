from: s2
next: s1
kind: report
re: 2026-09-28-101010-s1-label-segment-kickoff.md

Ready for review: 57c5dd5 on s2/label-segment-hyphens, worktree /Volumes/Casa/dev/refs/worktrees/label-segment-hyphens. Main had advanced to 84230af (your guide guidance) before branch creation; that is the base.

Filename labels now map whitespace to hyphens before filtering, collapse hyphen runs after filtering, and trim edge hyphens. The owner's example yields Author-hosted-full-text-journal-article. Empty results still omit the segment. Stored labels are unchanged and no existing files are renamed. Both --label help options and files-and-recovery.md describe a short tag, one or two words, hyphenated, with scan/capture/r2023-06-03 examples. No export path touched; no owner catalog/library writes.

Tests pin the seven named stable single-token labels; Unicode whitespace, repeated hyphens (including runs produced by filtering), punctuation, dots, Unicode letters, and empty results. Existing add/resource-add copy/move preview parity tests now expect probe-label and assert the stored label remains probe label. New contract tests check both help screens and show that a new intake preserves a pre-existing filename and stored label. One prior test expected mobile1.2β for a spaced label; its expectation now follows the approved mobile-1.2β rule, preserving its duplicate and collision checks.

Validation: focused naming/capture suite 87 passed before the three final contract cases; full final suite 1,204 passed in 45.26s with TEXMFVAR and TEXMFCACHE at /private/tmp/refs-csl-tex-cache. Ruff, ty check src/refs and git diff --check passed. Full log: /private/tmp/refs-label-suite-final.txt. First full run's only failure was the obsolete spaced-label expectation, corrected before the final run.

Merge remains the owner's gate. Ending without polling.
