# JOSE second bibliography target — proposal, 2026-09-27

Status: **proposal only; adoption is not approved**. Rebased as a fresh proposal from refs main `6484dcc`, which includes multiple targets (`e4cff52`) and the `biblatex-v1` implementation/contract (`60b5ad7`, `6484dcc`). The merged profile passed 999 tests, Ruff and ty; this documentation-only pass reruns the real second-target gate rather than the product suite. The prior uncommitted proposal was carried over before removing the three owner-authorized merged worktrees and branches.

The rerun resolves the prior portable-profile rendering limit: with `paper.bib` exported using `biblatex-v1`, **all eleven JOSE reference entries match the Quarto reference wording exactly**, including the four repository versions and release dates. No catalog or publication changes were made. Adoption remains subject to the owner's approval of this plan.

## Backup and scope

After approval, create and validate `/Volumes/Casa/refs-backups/2026-09-27-before-jose-second-target`. No backup has been created in this read-only proposal phase. Also record the publication and nested worktree heads and clean status before edits. The publication is at `2573802`; the nested Danvas `jose-paper` worktree is at `2dd297359ec7883459f4eb502b406c001d1d3a7b`. Both were clean on inspection. Keep `paper.qmd`, `paper.md` and all other manuscript content unchanged. No submission, push, release or deployment is proposed.

Scratch evidence is at `/private/tmp/refs-jose-biblatex-second-target/`. The rehearsal opened `/Volumes/Casa/refs/cat/catalog.sqlite` read-only, backed it up into scratch and ran the real export CLI against only that disposable snapshot. All files under the real catalog directory and twelve publication/manuscript/workflow files were hash-identical before and after. The rehearsal proved both ordered targets can be written together and that the imported bytes suffice for guarded adoption of the copied legacy bibliography.

## Inventory and consumers

The Quarto consumer reads `paper.qmd` and `references.json` via `_quarto.yml`, producing `output/pdf/paper.pdf` with the bundled Chicago Manual of Style 18th edition (author-date). The JOSE pipeline reads `worktrees/danvas-jose/paper.md` and `paper.bib`. The current sync script reads `paper.qmd`, performs the front-matter/body projection, reads `references.bib` as bytes and writes those bytes unchanged to `paper.bib`. Its `--check` requires both the manuscript projection and byte equality of the bibliography. The only active script reader of the publication’s `references.bib` found is this sync script; current documentation also refers to the legacy workflow and must be updated when it is retired.

`worktrees/danvas-jose` is a separate Git worktree of `/Volumes/Casa/dev/danvas`, not tracked content of the publication repository. Its bibliography change therefore requires its own commit on `jose-paper`, in addition to the publication workflow commit. All eleven sources are cited by both manuscripts. The accepted JSON and six article records remain unchanged.

## Import outcomes by key

No standalone import or record correction is proposed for any of the eleven keys; guarded adoption assesses the preserved legacy bytes against current records. `references.bib` and current JOSE `paper.bib` both have SHA-256 `83abcd481cd937df73fb5b7e581f8d286e9ab020a68205e4d3a7f428593d02b3`. Completed catalog import `972f58a2-03e7-4f0d-9f05-d237d7fdbb45` has that digest, so the existing `--adopt` proof is satisfied. The real `paper.bib` destination is not yet bound; `references.json` is already bound with baseline digest `f65cf654ce2d20d7d2c10d801030128421a33f2fa4c20f453087f4bccad14e4c`.

## Record completions by key

None are proposed. The four software records already have the repository kind, publisher GitHub, versions and release dates: `bosk2026canvaslms` 6.21 / 2026-09-17; `ucfopen2026canvasapi` 3.6.0 / 2026-04-16; `jjuanrivvera2026canvascli` 1.15.0 / 2026-09-25; `weng2026canvascli` 0.4.1 / 2026-09-21. Instructure remains a webpage with its documentation container title. Preserve all authors, titles, protected names, issued/accessed values, original entries and citation keys. The six article records need no changes.

## Sources found, fetched, and fetch list for the owner

No new sources or downloads are required. Existing article PDFs and five primary captures remain attached. The gate uses the owner-authorized Pandoc/citeproc build over JOSE's `paper.md` and `paper.bib`, with default Chicago author-date, matching the Quarto style. It verifies reference wording; it does not claim to reproduce the official Inara layout or venue-specific style. No Docker image was pulled or service started for this rerun.

## Attachments with final names and hashes

No attachment, label, path or resource digest changes are proposed. The eleven existing attachments remain as recorded in the sources-pass report. The new export is a generated bibliography, not a resource attachment. Scratch JSON export SHA-256: `f65cf654ce2d20d7d2c10d801030128421a33f2fa4c20f453087f4bccad14e4c`; scratch BibLaTeX SHA-256: `d2c5dc528ec0ea9d9a51ee3cd9207c0caaf8846fdb7042919c27f9735c0d8b60`.

## Planned targets and execution

Replace the publication’s legacy single `[export]` settings with this list, in order:

```toml
project = "jose-danvas"

[[export.targets]]
output = "references.json"
profile = "csl-json-v1"

[[export.targets]]
output = "worktrees/danvas-jose/paper.bib"
profile = "biblatex-v1"
```

Refs resolves configured paths relative to the publication `.refs.toml`; target binding uses the resolved destination path and does not restrict destinations to the discovering Git root. The scratch rehearsal successfully bound both destinations with this layout, including a simulated `.git` file in the nested worktree. No second `.refs.toml` is needed when running from the publication. Discovery from inside `worktrees/danvas-jose` stops at that worktree’s Git root and does not find the parent configuration; from there pass `--project-file /Volumes/Casa/pub/2026-jose-danvas/.refs.toml`. The same explicit selection was verified in the rehearsal.

After approval and the backup, adopt only the JOSE destination explicitly with `refs --project-file /Volumes/Casa/pub/2026-jose-danvas/.refs.toml export --output /Volumes/Casa/pub/2026-jose-danvas/worktrees/danvas-jose/paper.bib --profile biblatex-v1 --adopt --overwrite`, then run `refs export` from the publication to check both configured targets. Existing import proof authorizes adoption; `--overwrite` acknowledges the planned replacement of different legacy bytes, not an unrelated outside edit. Each target keeps its own digest guard; a partial batch must be inspected per target rather than assumed atomic.

Change `scripts/sync-jose-paper.py` so its projection function returns only manuscript text, remove the bibliography read/write and equality check, and update its status messages. Keep its branch guard, front-matter conversion, body projection and manuscript equality check. Verify `--check` passes when `references.bib` is absent and refuses a stale copied manuscript in an isolated test. Retire `references.bib` in the same publication workflow commit as the script change. Update README, AGENTS and `docs/refs.md` to name both refs targets and the manuscript-only synchronization check; remove their now-stale source/linking claims. The thin PROJECT_CONTEXT source-map bullet calling `references.bib` canonical also needs correction to `references.json`; this specific correction is included in the proposed scope for approval.

For the conversion harness, add a JOSE consumer that runs `quarto pandoc worktrees/danvas-jose/paper.md --bibliography worktrees/danvas-jose/paper.bib --citeproc --pdf-engine=lualatex -V geometry:margin=1in -o output/jose-paper.pdf`, extracting the final References section. The existing harness intentionally excludes all `worktrees/` content, so adding only the consumer row is insufficient. Propose a small tested register option to copy explicitly named input files into scratch despite directory exclusions, limited here to `worktrees/danvas-jose/paper.md`; reject escaping paths and symlinks. The second export creates the scratch `paper.bib`, while Git internals and the software environment remain excluded. Preserve the existing Quarto consumer and use a distinct `jose` fixture with tool/style provenance. Run the project gate after execution and record fixtures with `--record` only after the owner accepts its results.

## Export gate table

Verified from refs `6484dcc`, publication `257380218a02ce946379a2f21baad246b2df02d8`, and nested JOSE worktree `2dd297359ec7883459f4eb502b406c001d1d3a7b`. Tools: Quarto 1.10.18, bundled Pandoc 3.10, lualatex and pdftotext 26.09.0. Both exports contain eleven entries and report zero export warnings. Both targets bind and write in order on the disposable catalog; explicit parent-config discovery from the nested worktree also passes.

The Quarto PDF rebuilt from scratch CSL JSON has eleven identical entries against the accepted current PDF. Baseline and candidate JOSE PDFs were built with `quarto pandoc paper.md --citeproc --bibliography paper.bib --pdf-engine=lualatex -V geometry:margin=1in -o paper.pdf`, and their final References sections extracted. Keyed citeproc extraction compares unwrapped wording using the same manuscript and default Chicago style against the accepted Quarto JSON; JSON bytes are unchanged from the publication. This separates citation wording from PDF line breaks. Prediction for adoption, now verified in scratch: **eleven identical JOSE/Quarto entries, zero missing or lost facts**.

Against the legacy JOSE bibliography, the mechanical count is five identical and six changed: the five related-software entries gain the already accepted catalog facts, and the sixth change is DOI case only. The DOI-case difference in the Pandoc comparison is normalization, `S0149` → `s0149`, not a changed identifier. Precisely, the exported catalog DOI is already lowercase; the legacy Pandoc render retains its uppercase input, so this is not evidence that Pandoc alone lowercases DOI text. Candidate JOSE and Quarto render the same normalized DOI.

| Key | Quarto vs accepted PDF | New JOSE vs Quarto | New JOSE vs legacy JOSE | Predicted wording / assessment |
| --- | --- | --- | --- | --- |
| `bainbridge1983ironies` | identical | identical | identical | Unchanged article. |
| `bosk2026canvaslms` | identical | identical | changed | V. 6.21. GitHub, released September 17. |
| `nijhuis2003coursemanagement` | identical | identical | changed | DOI case normalization only; all article facts unchanged. |
| `instructure2026canvasapi` | identical | identical | changed | Documentation container title prints, matching Quarto. |
| `jjuanrivvera2026canvascli` | identical | identical | changed | V. 1.15.0. GitHub, released September 25. |
| `lee2015canvasinteractions` | identical | identical | identical | Unchanged article. |
| `jupyter2019nbgrader` | identical | identical | identical | Unchanged article. |
| `ro2019orgcoursepack` | identical | identical | identical | Unchanged article. |
| `sandve2013reproducible` | identical | identical | identical | Unchanged article. |
| `ucfopen2026canvasapi` | identical | identical | changed | V. 3.6.0. GitHub, released April 16. |
| `weng2026canvascli` | identical | identical | changed | V. 0.4.1. GitHub, released September 21. |

Exact before and after wording for each legacy-JOSE change follows; every after value is also the exact Quarto reference wording.

### bosk2026canvaslms

Before: Bosk, Daniel. 2026. “canvaslms: A CLI to Canvas LMS.” https://github.com/dbosk/canvaslms.

After: Bosk, Daniel. 2026. canvaslms: A CLI to Canvas LMS. Source code repository. V. 6.21. GitHub, released September 17. https://github.com/dbosk/canvaslms.

### nijhuis2003coursemanagement

Before: Gervedink Nijhuis, G. J., and B. A. Collis. 2003. “Using a Web-Based Course-Management System: An Evaluation of Management Tasks and Time Implications for the Instructor.” Evaluation and Program Planning 26 (2): 193–201. https://doi.org/10.1016/S0149-7189(03)00005-3.

After: Gervedink Nijhuis, G. J., and B. A. Collis. 2003. “Using a Web-Based Course-Management System: An Evaluation of Management Tasks and Time Implications for the Instructor.” Evaluation and Program Planning 26 (2): 193–201. https://doi.org/10.1016/s0149-7189(03)00005-3.

### instructure2026canvasapi

Before: Instructure, Inc. 2026. “Canvas LMS REST API and Extensions Documentation.” https://canvas.instructure.com/doc/api/.

After: Instructure, Inc. 2026. “Canvas LMS REST API and Extensions Documentation.” Canvas LMS REST API Documentation. https://canvas.instructure.com/doc/api/.

### jjuanrivvera2026canvascli

Before: jjuanrivvera. 2026. “Canvas CLI.” https://github.com/jjuanrivvera/canvas-cli.

After: jjuanrivvera. 2026. Canvas CLI. Source code repository. V. 1.15.0. GitHub, released September 25. https://github.com/jjuanrivvera/canvas-cli.

### ucfopen2026canvasapi

Before: University of Central Florida Center for Distributed Learning. 2026. “CanvasAPI: Python API Wrapper for Instructure’s Canvas LMS.” https://github.com/ucfopen/canvasapi.

After: University of Central Florida Center for Distributed Learning. 2026. CanvasAPI: Python API Wrapper for Instructure’s Canvas LMS. Source code repository. V. 3.6.0. GitHub, released April 16. https://github.com/ucfopen/canvasapi.

### weng2026canvascli

Before: Weng, David. 2026. “canvas-cli: Agent-Friendly CLI for Canvas LMS.” https://github.com/thedavidweng/canvas-cli.

After: Weng, David. 2026. canvas-cli: Agent-Friendly CLI for Canvas LMS. Source code repository. V. 0.4.1. GitHub, released September 21. https://github.com/thedavidweng/canvas-cli.

Evidence retained in scratch: `gate.py`, `exports.json`, `jose-entry-gate.json`, `quarto-entry-gate.json`, `quarto-jose-parity.json`, baseline/candidate citeproc JSON and PDF extractions, and catalog/publication hash manifests. No accepted fixture was recorded or replaced.

### Guarded adoption assessment

The rehearsal's `--adopt --overwrite` reports the expected legacy-value conflicts below while writing current catalog values to the scratch target. These are adoption-input conflicts, not export warnings or refused targets. They are disclosed for approval; no reconciliation back to old webpage records is proposed. The original bytes already exist in catalog history.

| Key | Legacy input → current catalog |
| --- | --- |
| `instructure2026canvasapi` | `metadata.accessed.date-parts`: [[2026, 8, 30]] → [[2026, 9, 26]] |
| `ucfopen2026canvasapi` | `metadata.type`: "webpage" → "software"; `metadata.accessed.date-parts`: [[2026, 8, 30]] → [[2026, 9, 26]]; `metadata.issued.date-parts`: [[2026]] → [[2026, 4, 16]]; `native_type.namespace`: "bibtex" → null; `native_type.value`: "online" → null |
| `bosk2026canvaslms` | `metadata.type`: "webpage" → "software"; `metadata.accessed.date-parts`: [[2026, 9, 1]] → [[2026, 9, 26]]; `metadata.issued.date-parts`: [[2026]] → [[2026, 9, 17]]; `native_type.namespace`: "bibtex" → null; `native_type.value`: "online" → null |
| `jjuanrivvera2026canvascli` | `metadata.type`: "webpage" → "software"; `metadata.accessed.date-parts`: [[2026, 9, 1]] → [[2026, 9, 26]]; `metadata.issued.date-parts`: [[2026]] → [[2026, 9, 25]]; `native_type.namespace`: "bibtex" → null; `native_type.value`: "online" → null |
| `weng2026canvascli` | `metadata.type`: "webpage" → "software"; `metadata.accessed.date-parts`: [[2026, 9, 1]] → [[2026, 9, 26]]; `metadata.issued.date-parts`: [[2026]] → [[2026, 9, 21]]; `native_type.namespace`: "bibtex" → null; `native_type.value`: "online" → null |

## Commits

Merged refs changes: `e4cff52` (multiple targets), `60b5ad7` (BibLaTeX profile), `6484dcc` (profile contract). This proposal is the only tracked change in the fresh `codex/jose-second-target-proposal` worktree. No product or harness code changes are included in this pass.

After approval: one publication workflow commit groups `.refs.toml`, the manuscript-only sync change, retirement of `references.bib` and workflow documentation; a separate commit in the nested Danvas `jose-paper` worktree records generated `paper.bib`; a subsequent refs commit adds the second consumer, narrow scratch-input support and tests, accepted fixtures, and guide register/findings. No manuscript-content commit is proposed. Fixture recording remains contingent on the owner's acceptance of the executed gate.

## Timing

No external intake. This rerun performed one snapshot, ordered dual-target scratch adoption, two JOSE PDF builds, a Quarto PDF build, keyed reference extraction and catalog/publication hash checks in one local rehearsal. All commands completed successfully; the prior profile's full-suite result is historical validation, not a new suite run for this proposal.

## Findings and approval boundary

The new profile resolves the prior loss of rendered software version and release date while preserving all eleven Quarto reference wordings. Both consumer targets can share one publication configuration even though the JOSE file belongs to a nested worktree of another repository. Existing imported bytes satisfy adoption proof; the legacy-value conflicts are retained and disclosed rather than used to undo accepted source corrections. The harness still needs the proposed narrow scratch-input support before registering JOSE's nested manuscript as a second consumer.

**Owner approval requested for the planned targets and execution above**, including guarded adoption with the disclosed legacy conflicts, retirement of the now-unread `references.bib`, manuscript-only synchronization, separate publication/nested-worktree commits, and the subsequent harness/register/documentation update. The catalog, publication and nested worktree remain unchanged; no adoption, retirement, fixture recording or publishing has occurred. Execution stops here because the owner explicitly requested proposal approval and the conversion guide's step 4 says: “Only an approved proposal proceeds.”
