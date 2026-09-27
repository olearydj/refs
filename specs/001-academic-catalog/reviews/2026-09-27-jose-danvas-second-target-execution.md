# JOSE second target execution — 2026-09-27

The owner approved proposal `7f07a92`. Execution has adopted both targets, retired the unused legacy bibliography and run both consumers. Fixture recording awaits the owner's acceptance of the executed gate.

## Backup and scope

`/Volumes/Casa/refs-backups/2026-09-27-before-jose-second-target` validates: every manifest member size and SHA-256 matches, SQLite integrity is `ok`, and the foreign-key check is empty. Catalog ID is `c03298ee-caee-4e20-aa0c-ddf121aafc0a`, pre-adoption revision 4140. External resource bytes are not included. No manuscript content, submission or publication action was performed.

## Inventory and consumers

Quarto reads `references.json` using `csl-json-v1`. JOSE reads `worktrees/danvas-jose/paper.bib` using `biblatex-v1`; its generated file is committed in the Danvas `jose-paper` worktree. `.refs.toml` selects both in that order. The script now projects/checks only `paper.qmd` → `paper.md`. Its bibliography copy and byte check are removed, and `references.bib` is retired in the same publication workflow commit. README, AGENTS, docs/refs and the PROJECT_CONTEXT source-map bullet describe the new ownership.

## Import outcomes by key

No standalone import or reconciliation. Explicit `--adopt --overwrite` succeeded using the already imported legacy bytes. The five expected adoption conflicts are exactly the ones disclosed in the proposal: Instructure's accessed date, and each repository's legacy webpage type, accessed date, year-only issued date and native BibTeX label. Current catalog values win; no old webpage type or date is restored. A follow-up two-target export reports both `current`, with no export warnings.

## Record completions by key

None required. All catalog source metadata and citation keys compare equal to the validated backup after adoption. Both manuscript hashes and the accepted JSON hash are unchanged. All resource rows compare equal to the backup.

## Sources found, fetched, and fetch list for the owner

No intake, fetches or outstanding source requests. Existing six article PDFs and five primary captures remain attached.

## Attachments with final names and hashes

No resource changes. The generated JSON remains SHA-256 `f65cf654ce2d20d7d2c10d801030128421a33f2fa4c20f453087f4bccad14e4c`; generated BibLaTeX is `d2c5dc528ec0ea9d9a51ee3cd9207c0caaf8846fdb7042919c27f9735c0d8b60`, exactly the approved scratch export. Original legacy bibliography bytes remain in catalog history and publication Git history.

## Export gate table

Run: `uv run --locked python tests/fixtures/real-trial/conversion_check.py --project jose-danvas --work /private/tmp/refs-jose-second-target-execution/gate`, from refs harness commit `d0eef7a`. Tools: Quarto 1.10.18, bundled Pandoc 3.10, lualatex and pdftotext 26.09.0. Both render commands succeed. The harness uses a read-only catalog snapshot and scratch project copy, including only the explicitly named nested `paper.md`.

| Consumer | Entries | Result | Baseline |
| --- | --- | --- | --- |
| Quarto | 11 | All identical | Accepted committed Quarto fixture |
| JOSE | 11 | All identical to approved proposal PDF extraction | Approved proposal scratch render; first committed fixture not yet recorded |

The harness correctly exits 1 for the missing JOSE fixture and labels its eleven entries newly added (`changed`, before null); no entry is missing and no consumer fails. An independent comparison of its complete JOSE extraction with the approved proposal's `after-pdf-references.json` is exactly equal. The proposal's keyed JOSE/Quarto comparison established all eleven reference wordings identical, including the four repository versions and release dates. Against legacy JOSE, the only changes remain the five accepted related-software entries and DOI case normalization; their exact before/after text is in the approved proposal.

Evidence: `/private/tmp/refs-jose-second-target-execution/`, including backup/adoption/export envelopes, manuscript hashes, gate JSON/Markdown, both scratch PDFs and render logs. Owner acceptance is pending; `--record` has not run.

## Commits

- Publication `f7afb1e`: two targets, manuscript-only sync, legacy retirement and workflow docs.
- Danvas `jose-paper` `3c6aff8`: generated JOSE bibliography only.
- Refs `d0eef7a`: explicit scratch inputs, refusal tests and JOSE consumer registration.

No manuscript-content commit. The proposal `7f07a92` remains the approved execution scope.

## Timing

One backup/adoption pass and one two-consumer gate; no external intake. Validation is scoped to the changed workflow and harness. All 19 harness tests passed (18 focused cases and the real two-consumer test); the two-consumer gate rendered successfully. Ruff and ty on src/refs pass. The script passes without `references.bib`, refuses a deliberately stale scratch manuscript, repairs only that manuscript, and leaves a sentinel bibliography untouched.

## Findings

Two configured targets now keep both consumers on the same source catalog. The sync script can no longer overwrite refs's JOSE export. Explicit harness inputs make the nested manuscript available without copying Git internals or unselected worktree files. The first-fixture failure remains visible until owner acceptance, preventing a newly generated candidate from silently becoming its own approved baseline.
