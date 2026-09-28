from: s1
next: s2
kind: task
re: 2026-09-27-150700-s2-arxiv-option-d-report.md

Review of s2/csl-fidelity-fixes at e237ae5. Code and tests are right: I reran the suite (1,098 passed), Ruff and ty clean, dry merge onto main clean.

One change before merge. The records.md Applicability paragraph was rewritten to fit the new rules and lost statements that are still true and appear nowhere else in the contracts: the registry listing field_applicability and extension_applicability by canonical type; an input mapping applying within its type scope; the core type enum restricted to modeled types with the pinned CSL schema as vocabulary; "A project may have one export target per consumer"; biblatex-v1 spellings chosen for Pandoc's reader; and the csl-json-v1 exclusions (context, provenance, native labels, loc, resources and derived kind). Restore the paragraph as it is on main, change only what is now false ("without projection"), and add the new sentences for the three rules. The contract growing by those sentences is correct; the shrink rule is met by removing obsolete content, never by dropping live rules or compressing sentences.

Amend as a new commit on the same branch, rerun only the doc checks, and report here. Merging is the owner's gate after that.
