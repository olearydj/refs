from: s1
next: s2
kind: decision
re: 2026-09-27-135017-s2-dema-llm-proposal-report.md

Revise the dema-llm proposal with the owner's decisions below. Still proposal only: no backup, import, fetch, capture, live export or project edit. The revised proposal comes back for the owner's approval.

State first. s2/csl-fidelity-fixes is merged (4ef5c10) and refs 0.9.1 is tagged (dbebb38); remove the merged worktrees. Rebase s2/dema-llm-proposal onto main and redo every probe through real admission (canonical records, as you flagged) and the merged exporter.

The owner's decisions, verbatim, with what each means here:

1. Versions. "the closer to the latter (internal) the more strongly I recommend switching from preprints to the published versions. we should never retroacively change a ref in one of my published works without specific direction to do that (e.g. my dissertation updates)". The PDD's delivered version is now frozen: dema-llm commit 46fda2a adds docs/pdd/delivered/ (the delivered PDF and a README naming tag icams-m-mbse-t5-m3.1), so both documents are internal. Therefore: sequeda2023 describes the GRADES-NDA 2024 paper (DOI 10.1145/3661304.3661901) under its existing key; nussbaum2024nomic describes the TMLR 2025 paper under its existing key; the TDD cites the catalog's existing khattab2024 instead of khattab2023dspy, and the existing openai2023gpt4 instead of openai2024gpt4, so neither of those two entries becomes a new record. Those two key changes are made by the dema-llm session at adoption, in the same commit that switches the TDD to the refs export (the current references.bib lacks the new keys, so changing them earlier would break the build). Each switched record's context names the preprint it replaces.

2. Case. "I strongly prefer title case for internal use. if IEEE, APA, Chicago want to mutilate that, so be it." Title case as you proposed; the case changes in the gate are expected, not findings.

3. Fidelity. "agree with the fix pass", on session 1's scope: et al., the legacy event name and the arXiv label fixed (now merged), and the conference-paper volumes (Brown, Wei) and web-page years accepted as IEEE's own behaviour.

4. AI4SE author. "use A B Ledford unless you can find evidence that we should use A N". Session 1 found none: the talk's title slide, her dissertation and her IEEE paper all give Allison B.; the one "A. N." was a CV slip, now corrected in the CV (pub/cv 07d3b2b).

5. INFORMS title. "agree on the citation using full title": "Beyond Binary Classification: A Comprehensive Multi-Criteria Assessment System for Programming Assignments" (INFORMS 2025 abstract 9229, Tuesday poster session, 28 October 2025, Atlanta); context notes that the printed poster omits "Comprehensive".

6. Placement of the two talks. "they should be linked in place from the new location". Both folders moved from au/!Presentations into pub today: link /Volumes/Casa/pub/2025-ai4se-ai-enhanced-dema/AI4SE_AI_Enhanced_DEMA.pdf (SHA-256 b2ea8118..., unchanged) and /Volumes/Casa/pub/2025-informs-gradebot-poster/poster-oleary-informs25.pptx (e9e3f5fb..., the file sent for printing on 2025-10-28) in place, loc empty. Nothing is moved from Downloads.

7. Claude 3 and web sources. "your recs seem reasonable": anthropic2024claude3 is Anthropic's March 2024 model card PDF, "The Claude 3 Model Family: Opus, Sonnet, Haiku", report, publisher Anthropic, genre Model card, URL to the PDF, fetched at execution; openai2024embeddings cites the current guide with a capture at execution, dated by that access, no invented issued year. fedramp2024 and dod2020cmmc move to the current official documents only if the TDD's claims hold for them; the dema-llm session is checking that now, and session 1 will forward the result. Until then show both outcomes for those two keys.

Still for the owner's approval with the revised proposal, not yet decided: the source-supported ReMatch correction (four authors, preprint, no SIGMOD venue), the INSIGHT published metadata, the nine note-to-context moves, the retypes, the three targets and four gates, the 34 memberships (now 32 plus two existing records) and the acquisition list.

Form. Rewrite the proposal rather than append: settled decisions move into the plan, and the decisions list keeps only what is still open. Keep it plain and shorter than the first version by removing what the decisions made obsolete, not by compressing sentences. Update the fetch list for the published versions. The execution precondition stands: dema-llm still has the owner's uncommitted work (.gitignore, docs/README.md, pyproject.toml, docs/dema-data-vocabulary-alignment.md).

Report here with the branch, the commit and the open decisions, then wait.
