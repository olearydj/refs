# JOSE Danvas bibliography conversion, 2026-09-26

Catalog intake is complete; publication adoption stopped at step 7 because the CSL JSON render changes four protected software names. No publication files were changed or committed. This is conversion evidence, not authorization to implement a refs feature. The owner's instruction to stop if a diff is not clean governs even though the portable BibTeX rendered-fact comparison passed.

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
