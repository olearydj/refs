from: s2
next: s1
kind: report
re: 2026-09-28-233904-s1-cv-execute.md

CV execution is complete and stopped at the owner acceptance gate. Commit **4ca205e** on **s2/cv-execution**, worktree `/Volumes/Casa/dev/refs/worktrees/cv-execution` (clean), based on approved main `122b0c5`.

Report: `specs/001-academic-catalog/reviews/2026-09-28-cv-execution.md`; companion JSON holds intake receipts, backup validation, final membership/resources, exact approved/actual render strings, activities and gate summaries. The reviewable adoption patch is alongside it as `2026-09-28-cv-adoption.patch`.

The live catalog now contains the approved 22-work CV membership: 15 new identities, six updated existing identities, and unchanged Judgment Economy reuse. Sixteen original CV BibTeX entries were preserved byte-for-byte against their approved identities. The backup was validated before mutation; its manifest excludes external file contents. Nine own-work files were linked in place unchanged, the patent PDF was acquired through a verified managed move, and Hossain R6 was linked to the earlier record. Family testimony is unchanged. GameTech remains an activity, with no catalog record. Known missing sources remain R6, MBSE2026, the error-patterns draft and three chapter scans.

Native HTML and Typst PDF: **22 entries each, all 44 expected-identical against the approved candidate**. All 19 activity rows match in both formats. Native PDF: 11 pages. All-project check: **379 existing entries identical**, with individual and all-project CV extractions equal. Exit **3 only for the two missing CV fixtures**. No unexpected differences. The register excludes the non-rendering docs/sessions symlink after an initial scratch refusal. Harness tests: 23 passed; Ruff, ty and diff checks passed.

No `--record`, export into the live CV, CV commit, or merge was performed. The live CV remains clean at `07d3b2b`; all eight live export-target rows remain unchanged from backup. The register currently embeds execution-only scratch preparation; after acceptance/adoption, remove that patch application while retaining native render/extraction. The patch prepares data/activities.yml and project-local bibliography changes; remaining legacy bibliography cleanup and project documentation belong to adoption. Do not rerun intake against the mutated catalog.

Scratch outputs: `/private/tmp/refs-cv-execution/cv-gate-02` and `/private/tmp/refs-cv-execution/all-gate`. Ready for your review and the owner's gate acceptance. Ending this turn; no watch.
