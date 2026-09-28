from: s2
next: s1
kind: report
re: 2026-09-27-150051-s1-arxiv-option-d.md

Option D is implemented in new commit e237ae5028fed1d75c0073434700b48f022d073b on s2/csl-fidelity-fixes, following fcb67449b11d0d92d3724a882a79a9b4a5a734e7. Worktree /Volumes/Casa/dev/refs/worktrees/csl-fidelity-fixes is clean. Nothing merged.

Report: specs/001-academic-catalog/reviews/2026-09-27-arxiv-projection.md in that branch.

The export guard is exactly article + archive arXiv (case-insensitive) + extensions.identifiers.arxiv present. Only missing publisher/number are filled; existing conflicting values remain. Archive is omitted only when it repeats the emitted publisher (case-insensitive). The catalog and admission logic are unchanged. Tests cover the independent guard conditions, version retention, conflicts, mixed case, and source preservation, with fixed IEEE/Chicago render expectations. The contract documents the rule and shrank by one word in this commit.

Verification: 1,098 tests passed with --require-tools (44.16s); Ruff src/tests, ty src and git diff --check clean. The historical baseline comparison continues to check every BibLaTeX record and the remaining non-arXiv CSL records; arXiv output is now explicitly covered by its new contract/render tests.

The all-project walk completed without --record:

| Project | Consumer | Entries | Changed |
|---|---|---:|---:|
| jhl-report | quarto | 92 | 0 |
| jhl-report | site | 103 | 0 |
| jose-danvas | quarto | 11 | 0 |
| jose-danvas | jose | 11 | 0 |
| manufacturing-training-media-tradeoffs | html | 39 | 0 |
| manufacturing-training-media-tradeoffs | elsevier | 39 | 0 |

All 295 entries are identical to the accepted fixtures, so no changed entries require before/after transcription. Exact gate: /private/tmp/refs-csl-fidelity/walk-arxiv/gate.json and gate.md. Suite log: /private/tmp/refs-csl-fidelity/arxiv-full-suite.log. Quarto used its existing cache with approved escalation; all exports and rendering remained in scratch. No fixtures recorded, live export targets or catalog records changed, or publication files written.

The dema-llm proposal has not been revised. I have read the updated comms protocol and am watching for the next message, including owner messages.
