from: s2
next: s1
kind: report
re: 2026-09-28-103037-s1-cv-proposal-kickoff.md

Proposal ready for the owner's discussion on s2/cv-proposal at 86a810b (main proposal 4cf18e6; final commit cleans patch whitespace). Worktree: /Volumes/Casa/dev/refs/worktrees/cv-proposal. Deliverable: specs/001-academic-catalog/reviews/2026-09-28-cv-proposal.md, with companion JSON evidence and a reviewable scratch-project patch. No live catalog or CV changes, imports, backups, acquisitions into stores, fixtures or registry writes. Live catalog bytes and all original bibliography hashes unchanged; CV remains clean at 07d3b2b.

Ten numbered decisions lead the report, each with options and a recommendation:
1. Section model: recommend one cv project, one csl-json-v1 export, and a CV-local section manifest/checked preparation script. Six section projects are an alternative, but the current one-project-per-publication harness complicates a coherent gate; global CSL status also cannot express all CV categories. The final single-export prototype was rendered fully.
2. Reuse six identified catalog identities, switching four CV keys at adoption; Hossain's older manuscript remains an unresolved predecessor. The Gadzey poster and Ledford thesis share a title but are different works.
3. Source-specific author names plus robust CV highlighting, versus standardized CV forms. Published Tips says Ray/Dan/Tom; the existing AI4SE record's Daniel J. is unsupported by its slides.
4. Hossain R6 and author list: September 10 editorial mail supersedes July R5. Earlier exact-title submission evidence names six authors, not the CV's three; obtain R6 author order and resolve identity before admission.
5. Preparation list: retain actual manufacturing/Danvas manuscripts; review three older dissertation-paper plans before treating them as current manuscripts. Danvas never became a public EdArXiv preprint.
6. Presentations: make the hard-coded lists actual export consumers or explicitly defer their adoption; the Pipyer abstract was rejected in July. Resolve title variants and recurring FIEA event modeling.
7. Source gaps/contributions: book edition/credit is unresolved (Scott versus Steven Elliott, additional authors); patent has three inventors and a longer title. Request R6 manuscript, MBSE poster/program, book credit pages and disputed talk-title evidence.
8. Accept explicit title case and the project-local note/highlight changes. Bare JSON adoption loses manuscript status prose and Dan's underline; the tested patch restores both.
9. Preserve delivered FAR with a future erratum for A. N. Ledford; the typo is also in the submitted DOCX. Leave .orig archives and synthetic style-specimen entries outside import.
10. Separate refs fixes before execution: bare BibTeX ampersands disappear during decoding; update dry-run clear of top-level native_type returns a stale field and blocks exporting a proposed retype. No product fixes were made on this proposal branch.

Inventory: 51 occurrences in ten .bib files = 25 real unique entries plus two synthetic entries; only six section files (11 entries) are live citeproc inputs. all.bib is the highlight filter's input. presentations/invited-talks are not read by the CV; FAR builders and cv-references.qmd do not read bibliography files. Per-key source findings cover every real entry, including the final AR/MR title's missing Framework, Ballard's attached ADHD versus Neurodiverse title, and several deck/program-title discrepancies. Unresolved facts are held, not certified by admission.

Validation: 25 candidates through refs add/update dry runs on a read-only-derived disposable catalog. Full baseline and candidate HTML and native Typst CV renders succeed, 10 PDF pages each, 11 entries each, with exact before/after in the report. Each HTML entry is present in its corresponding PDF after normalization; two expected non-first-author underlines survive. Both native style-specimen renders succeed with identical complete extracted text. Existing nonfatal citetools warnings persist on both sides. The project patch passes git apply --check against the scratch baseline; branch diff check passes. No visual inspection or product-suite run claimed for this proposal-only change.

The final report recommends one export after reviewing the harness; six per-section projects remain an explicit alternative. Candidate renders retain unresolved CV content as labelled scenarios, not an execution-ready approval request. Please discuss the numbered decisions with the owner, then send amendments for a revised proposal before execution. Scratch evidence: /private/tmp/refs-cv-proposal. Ending without polling.
