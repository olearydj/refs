# JOSE Danvas bibliography conversion, 2026-09-26

The initial attempt below stopped at step 7 because CSL JSON changed four protected software names. After the fix merged, the resumed conversion passed both comparisons and adopted the Quarto export; the final section records that outcome and its commits. This report preserves the initial failure as evidence.

## Inventory and backup

Refs started on main at `3ceb929`; `/Volumes/Casa/pub/2026-jose-danvas` is at `379cde3`. Both tracked worktrees were clean. The current manuscript cites all eleven bibliography keys, verified from Pandoc's citation AST; there are no uncited extras. The bibliography contains six DOI-bearing articles and five online entries. `_quarto.yml` reads `references.bib`, with no custom CSL style specified. The scratch Quarto builds used that exact configuration and manuscript.

`scripts/sync-jose-paper.py` transforms manuscript front matter and body for JOSE, but its bibliography transformation is exactly `read_bytes()` from `references.bib`, followed by `write_bytes()` to `worktrees/danvas-jose/paper.bib`. It does not parse, filter, reorder, normalize, or rename bibliography entries. Its `--check` compares those bytes. The two bibliography files are identical, SHA-256 `83abcd481cd937df73fb5b7e581f8d286e9ab020a68205e4d3a7f428593d02b3`.

The requested backup is `/Volumes/Casa/refs-backups/2026-09-26-before-jose-danvas`. Refs's `validate_snapshot` passed: manifest member sizes and hashes, SQLite integrity, foreign keys, supported schema, catalog identity and resource inventory. As the manifest states, external file contents are excluded. Catalog snapshot SHA-256: `f348eb0344f14ad128336f1bf111daf0aa1de8cd76bb3fcaadd0cbc7ac41d23a`.

## Local sources and import outcomes

The search covered the project, `/Volumes/Casa/refs/lib`, and `~/Downloads`, including the DEVONthink exports beneath `_from2020mbp`. Filename searches used source titles and author/tool names; text searches matched normalized DOI or full title in the first two pages of 4,328 PDFs. No matching article PDF was found. This is a bounded text search, not an OCR search or proof that no scanned copy exists. Five extraction failures were unrelated by filename: two copies of an HTML response stored with a PDF suffix and three encrypted personal documents. Nothing was downloaded.

The project's docs and both `.ho` notes were searched for saved pages and source notes. No saved primary pages were found. The existing `docs/phase-4-literature-and-related-software.md` contains substantive review notes for all five online sources. Each web record links to this one file in place, labeled `literature-review`, with loc unset. It is a research note, not a capture of the cited web page or evidence of full-text access. SHA-256 before and after linking: `f1e3a77a1d5d2afe0121beeccebe4fd8112fb78fb2e0bdfb9ae215790554f8a9`.

The single import used origin `jose-danvas`, batch `972f58a2-03e7-4f0d-9f05-d237d7fdbb45`. Counts: 11 applied, 0 unchanged, 0 conflict, 0 invalid. Every key was preserved. None bound to an existing source by DOI, so there are no field conflicts to list. Project `jose-danvas` cites all eleven.

| Key | Import | Local resource | CSL JSON reference comparison | Portable BibTeX reference comparison |
| --- | --- | --- | --- | --- |
| `nijhuis2003coursemanagement` | Applied, new | PDF not found; file-less | DOI letter case only | DOI letter case only |
| `lee2015canvasinteractions` | Applied, new | PDF not found; file-less | Identical | Identical |
| `instructure2026canvasapi` | Applied, new | Review note linked; primary source URL-only | Identical | Web-entry formatting only |
| `ucfopen2026canvasapi` | Applied, new | Review note linked; primary source URL-only | Identical | Web-entry formatting only |
| `jupyter2019nbgrader` | Applied, new | PDF not found; file-less | **`nbgrader` becomes `Nbgrader`** | Identical |
| `ro2019orgcoursepack` | Applied, new | PDF not found; file-less | **`Org-mode` becomes `Org-Mode`** | Identical |
| `bosk2026canvaslms` | Applied, new | Review note linked; primary source URL-only | **`canvaslms` becomes `Canvaslms`** | Web-entry formatting only |
| `jjuanrivvera2026canvascli` | Applied, new | Review note linked; primary source URL-only | Identical | Web-entry formatting only |
| `weng2026canvascli` | Applied, new | Review note linked; primary source URL-only | **`canvas-cli` becomes `Canvas-Cli`** | Web-entry formatting only |
| `sandve2013reproducible` | Applied, new | PDF not found; file-less | Identical | Identical |
| `bainbridge1983ironies` | Applied, new | PDF not found; file-less | Identical | Identical |

Import issued one `unprotected_capital` warning for Sandve's `metadata.container-title`, `PLoS Computational Biology`; both exports and renders retain that spelling. There were no import limitations or refusals. With no article PDF found, there were no copy operations into `papers/educ`; originals stayed in place. All eleven records currently have loc unset.

## Export gate

Both profiles exported eleven entries to `/private/tmp/refs-jose-conversion/`. CSL JSON SHA-256: `2128633775ce767414648aa2e878bb3c549499306ed09e6623618c32e85d2667`. Portable BibTeX SHA-256: `e4d681a00c8a3f61fd1ef71148264174e1f7acbbc32f9d6327922068589f3791`.

Quarto 1.10.18 / Pandoc 3.10 rendered two isolated project copies: the original bibliography and scratch CSL JSON. The fresh baseline's complete extracted text equals the current project PDF's text. The candidate's only extracted-text differences are the four software-name changes and DOI letter casing listed above. All three candidate pages were visually inspected; no clipping or overlap was found. Manuscript prose and citations remain unchanged. Initial sandboxed renders could not write the TeX font cache; reruns with cache access and automatic TeX package installation disabled succeeded. No source or export workaround was used.

Entry-by-entry Pandoc citeproc comparisons used the manuscript and JOSE projection with each corresponding bibliography. The portable output's five `type_fallback` warnings disclose `webpage` becoming `@misc`. Pandoc consequently changes quotation marks/emphasis for those entries. Those are formatting differences, not lost displayed facts. DOI normalization lowercases `S0149` without changing the identifier. The portable output retains all authors, titles, dates, volumes, issues, pages, DOIs, URLs and accessed dates from the input; Pandoc's parsed type becomes generic for the five web entries. This is a Pandoc comparison, not a fresh official Inara compilation or certification of every possible JOSE style.

The CSL output retains bibliographic metadata, but `serialize_csl` in `src/refs/bibliography.py` emits only `record['metadata']` plus the key. Imported `title_protection` is outside that object, so citeproc loses the protected spelling instruction. The exporter returns no warning about this. These four technical-name changes fail the conversion gate. No manual markup, style modification, metadata workaround, or refs implementation change was attempted.

## Second target and resumption boundary

Multiple destinations and explicit profiles already work. A future second target would be `worktrees/danvas-jose/paper.bib`, using `portable-bibtex-v1` and the same `jose-danvas` selection. The current `.refs.toml` format selects one default output/profile; a second explicit command or project-config file can select the JOSE destination. No new export engine is required.

Before that target is adopted, the sync script must stop writing `paper.bib`, and its bibliography check must stop requiring byte equality with `references.bib`; the manuscript projection remains its responsibility. The existing target's bytes already match the imported file digest, satisfying refs's import-proof prerequisite for adoption. Replacing those bytes later requires explicit guarded adoption with `--adopt --overwrite`, following a renewed comparison and the publication-branch workflow. This was not executed. Keeping the old writer active would overwrite the generated target on the next sync and trigger refs's outside-edit guard.

Nothing is retired: `references.bib` still supplies both Quarto and JOSE's synchronized bibliography. No `references.json`, `.refs.toml`, or `docs/refs.md` was added to the publication, and README/AGENTS were not changed. The separate adoption and documentation commits remain conditional on resolving the failed gate and rerunning the comparison. `paper.qmd` was never edited.

Candidates for a later owner decision: carry protected-case instructions through CSL JSON to prevent the four observed software-name changes, with a consumer check covering them; transfer JOSE bibliography ownership from the sync script to an explicit refs target to prevent two writers replacing each other's output. The conversion does not establish a need for a new general multi-target subsystem. Missing PDFs are recorded as missing files, not an adapter defect or permission to download.

## Verification and evidence

All 676 pre-existing source rows remain byte-for-byte equal to the backup's SQL values. The catalog now has 687 sources; `jose-danvas` has eleven cited records and five links to the one unchanged review note. SQLite integrity passes with no foreign-key findings. Hashes of the manuscript, both existing bibliographies, build configuration, sync script, JOSE manuscript, current PDF and linked note remain unchanged. Both publication repositories remain clean, and `sync-jose-paper.py --check` passes.

Local evidence is retained at `/private/tmp/refs-jose-conversion/`: `inventory.json`, `backup-validation.json`, `import.json`, `pdf-search.json`, resource command envelopes, both exports and export envelopes, `reference-comparison.json`, both scratch render directories/logs, and `final-verification.json`. The bounded search path list is `/private/tmp/jose-source-paths.txt`. These are temporary local evidence paths, not published artifacts.

Timing: kickoff 21:26:53 CDT; import completed 21:28:59; both scratch exports completed 21:29:41; render/source/catalog verification completed 21:32:32. Thus intake through exports took about three minutes, with another three minutes for verification, excluding report writing. There are no publication commit hashes because the gate stopped adoption. The refs findings commit contains this report and the guide entry only.

## Resumed step 7: accepted and adopted

Resumed on 2026-09-26 using refs 0.7.0 on main at `6459999`, which contains the title-protection merge `105803c`. No entries were re-imported and no catalog metadata, project selection or resource links were changed. Both existing scratch targets were re-exported from the eleven cited catalog records. The CSL JSON export now carries nocase spans and has SHA-256 `6c172d67ddc26b39d31447b4a24f9583a2bc3c16367d6bebdc4e01ffa5fad89f`; the portable BibTeX bytes retain their earlier SHA-256 `e4d681a00c8a3f61fd1ef71148264174e1f7acbbc32f9d6327922068589f3791`.

Both entry-by-entry comparisons passed with no lost or altered bibliographic facts. All four formerly failing entries now render identically to their baseline: `bosk2026canvaslms`, `jupyter2019nbgrader`, `ro2019orgcoursepack` and `weng2026canvascli`. In the CSL comparison, ten entries are text-identical; `nijhuis2003coursemanagement` differs only by DOI letter casing, `S0149` to `s0149`. In the portable BibTeX comparison, five articles are text-identical, Nijhuis has that same DOI normalization, and the five web entries have only the already-disclosed quotation/emphasis changes from the misc fallback. No new differences appeared.

Quarto 1.10.18 and bundled Pandoc 3.10 rendered isolated baseline and candidate copies, followed by the adopted project. The project's unspecified CSL setting resolves to the bundled Chicago Manual of Style 18th edition (author-date). The fresh baseline's full extracted text equals the pre-conversion PDF; the candidate's full text differs only by the one DOI letter case. All three candidate pages were visually inspected without clipping, overlap, or changed pagination. The adopted PDF's full extracted text equals the candidate's, and all three adopted page images are pixel-identical to the reviewed candidate. The JOSE comparison used Pandoc citeproc as before, not a new official Inara build.

Publication commit `ba418b7` contains only `references.json`, the one bibliography-line change in `_quarto.yml`, and `.refs.toml` selecting `jose-danvas` and `csl-json-v1`. Commit `af6ce45` separately adds `docs/refs.md` and points to it from README and AGENTS. The configured export dry-run selects the correct target, reports eleven entries, matches the adopted hash, and has no warnings or pending recovery. `paper.qmd`, `references.bib`, JOSE's `paper.md` and `paper.bib`, the sync script and the linked review note all retain their pre-resume hashes. Both publication worktrees are clean, and the unchanged sync script's `--check` passes.

Nothing is retired. Quarto now consumes the generated JSON, while JOSE's `paper.bib` remains the byte-for-byte copy of `references.bib` produced by the existing script. Replacing that script's bibliography write/check with a second refs target remains a separate decision; the documentation makes the temporary two-consumer workflow explicit.

The accepted [export and reference-list fixtures](../../../tests/fixtures/real-trial/converted/jose-danvas/) contain `references.json`, `quarto-references.txt` extracted from the adopted PDF, and `verification.json` with tool versions, source commits, style/export/text hashes and each key's diff disposition. Baseline publication commit: `379cde3`; unchanged JOSE worktree: `2dd2973`. Additional scratch evidence, including the per-key before/after text and render logs, is in `/private/tmp/refs-jose-conversion/resumed/`. The register now covers the adopted Quarto consumer; the unadopted JOSE target is explicitly excluded from that status.
