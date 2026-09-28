from: s2
next: s1
kind: report
re: 2026-09-27-170441-s1-dema-llm-execute.md

Stopped at the gate. Execution branch `s2/dema-llm-execution`, commit `0288d2c`, clean worktree `/Volumes/Casa/dev/refs/worktrees/dema-llm-execution`. Main report: `specs/001-academic-catalog/reviews/2026-09-27-dema-llm-execution.md`; sibling `-gate.md` gives exact before/after strings for all 80 entries across four consumers, `-gate.json` gives structured comparisons and link evidence, and `-evidence.json` retains backup/import/resource/fetch evidence. The register now has the one target and four native consumers. No --record, publication export, adoption, publication commit or merge.

Preflight passed against clean publication 7599aee: bibliography hash, citation inventory, consumers/style, existing source hashes and all 37 bindings match the proposal. Backup `/Volumes/Casa/refs-backups/2026-09-27-before-dema-llm-conversion` validated before intake and again afterward, schema 6, catalog revision 4520. Current catalog revision is 4738.

Intake: 33 original entries applied, zero conflicts/invalids; two new publication records added; GPT-4 and published DSPy reused with guarded context appends. All 33 original entry byte strings are preserved exactly. All 37 final bibliographic records match the approved canonical candidates except the two planned actual web access dates. Project dema-llm has exactly 34 cited memberships. Three version links verify in both directions; the three retained preprints are not project members.

Attachments: eight files linked in place, fifteen PDFs fetched and moved by convention under unfiled, two single-file captures moved likewise, plus the existing GPT-4 PDF: 26 resources in all, each final file hash verified. The Markdown report lists every final filename/hash. Eleven selected sources remain gaps: both Bloor reports, Bernstein/Haas, published Nomic, Christophides, Valentine, Deb chapter, Zitzler, APE, CMMC Model Overview and published Sequeda. The report has each owner locator and refusal/unresolved reason. No refusals were bypassed or failed fetch dates invented. CMMC v2.13 remains an owner fetch. The fetched ICLR DSPy PDF cover differs from its official page/existing title; this is recorded in context without changing the approved record.

Final harness: `/private/tmp/refs-dema-gate-03`. All four full native consumers rendered: TDD HTML/PDF (34 each), PDD DOCX/PDF (six each); no missing reference. Exit 1 is solely the four absent accepted fixtures. All 80 wordings match the proposal, with exact HTML/DOCX matches and normalized PDF matches; the two expected capture-date additions are September 27, 2026. The PDD comparison is existing biber versus candidate citeproc, with approved loss of backreferences.

The gate has two HTML findings to review:

- Unpredicted presentation change: all 34 TDD HTML bibliography labels renumber because the export is ordered by key. Sequeda [1] → [29], ReMatch [2] → [30]. The exact table flags every affected row. PDF and both PDD numbers stay stable.
- Pre-existing defect retained: all 43 TDD in-text citation links display a number different from the destination appendix entry, in BOTH the original and candidate HTML. Every link resolves to the correct source key; none is broken. Example: Howard displays [1], but its appendix number is [7] before and [9] after. The full-artifact check exposes this; the bibliography-only proposal previews did not. No repair or acceptance is implied.

Scratch-only preparation is explicit in the register: its first consumer writes a helper that refuses a live .git checkout, applies the four key replacements, bibliography/engine switch and approved speech fallback to the harness copy, then renders both book formats together. The PDD consumer renders both PDD formats. HTML/Word references and numbered PDF reference sections are extracted into JSON. Two extraction issues (following callout and numeric URL continuation mistaken for footer) were corrected and rechecked in fresh scratch runs. At adoption, retire this temporary preparation; its assertions intentionally expect the current legacy settings.

Validation: backup manifest/integrity; 33 originals; 37 canonical field comparisons; 34 memberships; three symmetric links; 26 file hashes; four successful native renders; all 80 predicted wordings; all 43 HTML link destinations; register validation and embedded helper compilation; git diff --check. Publication remains clean and untouched at 7599aee, including delivered artifacts. No product code changed, so no unrelated full suite was rerun.

I am watching for the owner’s gate decision through this folder. Intake is complete; the eleven fetch gaps and HTML findings are explicitly disclosed. Recording fixtures, publication adoption, further fixes and branch merge require the next owner gate.
