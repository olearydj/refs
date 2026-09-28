from: s2
next: s1
kind: report
re: 2026-09-27-140446-s1-csl-fidelity-fix-kickoff.md

Items 1 and 2 are ready for review on s2/csl-fidelity-fixes, commit fcb67449b11d0d92d3724a882a79a9b4a5a734e7, based on 78708e1. Worktree /Volumes/Casa/dev/refs/worktrees/csl-fidelity-fixes is clean. Main remains at 78708e1 and shows the local untracked worktrees/ directory. Nothing merged.

Report: specs/001-academic-catalog/reviews/2026-09-27-csl-fidelity-fixes.md in that branch.

The exact bare family/literal others sentinel is projected at export, covering already-stored records without a migration: CSL literal others; both Bib profiles unbraced and others. Actual consumers print et al. Given-name people and organization counterexamples remain intact. Read-only catalog scan found zero family-name others records. CSL adds the legacy event alias using setdefault; admission stays unchanged. The current catalog schema accepts event-title only, and matching exported aliases re-import successfully.

Verification: 1,086 tests passed with --require-tools; Ruff src/tests and ty src clean; diff --check clean. Initial test failures from my test wiring were fixed, and the historical all-CSL-bytes-identical assertion now permits only the intentional event alias. TeX used a writable scratch cache. The all-project conversion walk completed without --record; Quarto’s existing cache required escalation after sandbox access failed.

| Project | Consumer | Entries | Changed |
|---|---|---:|---:|
| jhl-report | quarto | 92 | 0 |
| jhl-report | site | 103 | 0 |
| jose-danvas | quarto | 11 | 0 |
| jose-danvas | jose | 11 | 0 |
| manufacturing-training-media-tradeoffs | html | 39 | 0 |
| manufacturing-training-media-tradeoffs | elsevier | 39 | 0 |

Every one of the 295 entries is identical to its accepted fixture; there are no changed entries to list with before/after or attribute to items 1 or 2. Consumer regressions cover the affected cases directly. Exact evidence: /private/tmp/refs-csl-fidelity/walk-complete/gate.json and gate.md. No fixtures were recorded, catalog records changed, or live publication files exported.

Item 3 remains unimplemented and awaits your answer to 2026-09-27-141043-s2-arxiv-representation-question.md, which includes exact renders and the correction to my proposal’s noncanonical arXiv probes. I am watching comms for the next message.
