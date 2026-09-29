from: s1
next: s2
kind: task
re: -

Owner, verbatim: "cv is next, right? big boy. run thru the proposal and then lets discuss it". Proposal half only (conversion-guide steps 1 to 4), read-only: no catalog writes, no import, no backup, no fetch into stores, no edit in the CV repo. Main is at 171cf63. Protocol: ack and go straight on; end your turn after the report.

Project: /Volumes/Casa/pub/cv (git, clean at 07d3b2b). The owner's CV: cv-master.qmd renders Typst PDF and an HTML preview through citeproc with styles/apa-cv.csl; the citetools extension (_extensions/bcdavasconcelos/citetools/multiple-bibliographies.lua) reads per-section files named in the front matter (bibliography_proceedings, _published, _forthcoming, _submission, _preparation, _otherpublications -> refs/*.bib); nocite @* prints every entry; filters/highlight-djo.lua highlights the owner's name and references bib files; refs/ also holds presentations.bib, invited-talks.bib, all.bib, style-specimen.bib and two .orig files. far/ holds faculty activity report builders and drafts (far/25-26 is historical; far/26-27 is current). The inventory review (specs/001-academic-catalog/reviews/2026-09-26-bibliography-inventory.md) counted 51 entries in ten files, 4 already in the catalog; open decision C there is the owner's own works, now being taken up here.

This one is different from earlier conversions: every entry is the owner's own work, the list is organized by publication status, and the same works are already records in the catalog under other keys (for example oleary2025ai4se, oleary2025binary-classification and olearyledford2026insight from dema-llm, the manufacturing and jose-danvas papers themselves if present). The proposal must lay these out for the owner as decisions, with options and a recommendation each, not settle them:

1. Sections. How the ten per-status files map onto refs: one refs project and target per section file (keeps the CV's wiring), one project with status held in the record (CSL status) and sections derived, or another shape; what moving a work from preparation to submission to forthcoming to published costs under each.
2. Identity and keys. Every CV entry that matches an existing catalog record (by DOI, title, event), the key each side uses, and the options (the CV switches to the catalog key at adoption, versus anything else); preprint and published versions of the owner's papers under the preprint rule in the guide.
3. Names. The owner's and coauthors' name forms across entries and existing records (Danny J./Dan, A. B. Ledford), and what the highlight filter matches, so highlighting survives.
4. Consumers. Every reader of these files: the CV (PDF, HTML), the highlight filter, all.bib's reader if any, the FAR builders, anything else; which are live; style-specimen.bib's role; the .orig files.
5. Correctness. Check every entry against its source (DOI, publisher page, program, the owner's own files under /Volumes/Casa/pub and presentation folders): dema-llm had invented details, and the CV's A. N. Ledford slip was found only by chance.
6. Anything else that needs the owner's judgment.

Use the guide's rules (published works keep their references; one target per profile; title case unless the owner decides otherwise for the CV; keys stay as assigned unless the owner directs a switch at adoption). Predict renders from records passed through refs admission (dry runs against a disposable catalog copy) and from a full render of each consumer. Deliverable: specs/001-academic-catalog/reviews/2026-09-28-cv-proposal.md on branch s2/cv-proposal, with the decisions as a numbered list up front, each with options and a recommendation, then the inventory, planned records, renders and findings. Report here with the branch and the decisions list.
