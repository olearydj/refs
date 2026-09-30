from: s2
next: s1
kind: report
re: 2026-09-29-200038-s1-pipyer-proposal-kickoff.md

Proposal ready at **69ae3a7**, branch **s2/pipyer-paper-proposal**, clean worktree `/Volumes/Casa/dev/refs/worktrees/pipyer-paper-proposal`, based on 315a370. Deliverable: `specs/001-academic-catalog/reviews/2026-09-29-pipyer-paper-proposal.md`; companion JSON preserves complete canonical proposals, admission receipts, source lookup, inventory and exact native PDF comparison.

Numbered owner decisions up front:
1. Recommend switching this internal paper from kapoor2024 to the May 2025 TMLR publication, new refs-generated key kapoor-2025-aiAgents, with the preprint retained/linked. Alternative: keep preprint.
2. Recommend the guide's current-on-access Pydantic AI 2.51.0 (released September 25), since no accessed date exists. Alternative: explicitly except the record and retain implementation-used 1.106.0 (released June 5), pinned in Pipyer's uv.lock. The proposed render uses 2.51.0 and does not claim Pipyer was tested against it; the distinction is prominent. An alternative choice requires revising the admitted candidate/render before approval.

Verified existing references.bib exactly equals BOTH its adopted target baseline and a current portable-bibtex-v1 export. All 11 keys already belong to pipyer-paper; original import was 11 applied, no conflicts/invalid. No repeat bulk import/project creation is proposed. Plan one new references.json csl-json-v1 target, retire the unused .bib and its registration via export --forget at adoption. Future Inara paper.bib would use biblatex-v1, but no future target is configured now.

Source findings include omitted MLflow author Corey Zumar, targets name protection, Snakemake's source dash, and van de Water's non-dropping particle (changes in-text citation). Shared DSPy remains unchanged with its prior accepted proceedings-versus-PDF discrepancy disclosed. Qiu stays arXiv v2; R-LAM stays v1; no published replacements found. Owner fetch list: Nature Nextflow, OpenReview TMLR Kapoor, and Snakemake PDF. Local bounded search scanned 1,511 first pages for the ten unattached works; DSPy is already attached and its local cover was verified.

Ten update previews, one unchanged DSPy preview, one new-publication add preview passed refs admission on a disposable catalog; applied scratch canonical records matched previews. Both full native PDF renders succeeded using the approved Mermaid renderer: four pages each, 11 references, **2 identical / 9 expected wording changes / 0 unexplained**. Exact before/after text is in the report. All citation identities resolve and native PDF links lead to the reference pages. Two in-text changes: Kapoor 2024→2025 and Water→van de Water. All four candidate pages visually checked. Fresh baseline text exactly matches the existing saved proof.

No live catalog/project writes, import, backup, source acquisition into stores, fixture recording or merge. Live project hashes and clean de88944 state rechecked. Diff check passed. Scratch: `/private/tmp/refs-pipyer-proposal`. Ending this turn for review/owner decisions; no watch.
