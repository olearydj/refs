from: s1
next: s2
kind: task
re: 2026-09-28-104552-s2-cv-proposal-ready.md

Owner, verbatim, on the CV proposal's decision 10 (your two refs findings): "7 - fix" (numbered 7 in session 1's digest). The rest of the proposal is under discussion with the owner; do not revise it yet. Main is at 641d61a. Protocol: ack and go straight on; end your turn after the report.

Branch s2/cv-prerequisite-fixes from main, two rules, tests per docs/testing-convention.md:

1. A bare BibTeX ampersand disappears in the TeX decoder (the engineering-economy title and container, two talk descriptions). An unescaped & in a field value should survive import as a literal ampersand, as an escaped \& already does; show before/after for the CV's affected entries in a disposable catalog, and check the corpus and rehearsal tests still pass.
2. update --dry-run returns a stale top-level native_type after the canonical result clears it, so a previewed retype (paper-conference to speech) fails export validation. Make the dry-run result match what execution would store, and test a retype that clears native_type through dry run and execution, including export of the result.

Full suite with TEXMFVAR and TEXMFCACHE at /private/tmp/refs-csl-tex-cache, Ruff, ty. If rule 1 can change the stored text of any existing catalog record on re-import, say so, and run the all-project conversion check without --record. Report here; merging is the owner's gate.
