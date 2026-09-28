from: s1
next: s2
kind: decision
re: 2026-09-27-154340-s2-dema-llm-revised-proposal.md

Two tasks, in this order. Main is at cba907f (a ledger row; no code change since 0.9.1).

## Task 1: unnamed links between sources (branch s2/source-links)

Owner, verbatim: "re: linking preprints with pubs, an unnamed link is fine. the nature of the relationship should be obvious. but named links is a good backlog addition for refs" and, on building it before dema-llm executes, "1 - ok".

Refs stores links in source_relations, but only the Zotero import writes them, and nothing shows them. Add the smallest surface that lets a person link and unlink two catalog sources and see the links: prefer options on an existing command (for example update) over a new command, and say what you chose and why. The link has no name or type. `show` lists linked sources in both directions, including the six existing Zotero links. Linking is a logged mutation with the usual revision guards; removing a source keeps its links as today. No export change: links are catalog-only. Tests per docs/testing-convention.md, a contract sentence in cli.md, full suite, Ruff, ty. Report here; merging is the owner's gate.

## Task 2: revise the dema-llm proposal again

The owner's decisions, verbatim where given:

1. Preprints stay in the catalog, clearly identified and linked to the publication: "do the preprints and their attachments remain in the refs catalog? probably best if they do since other papers may refer to them. make sure they are clearly identified as preprints and that there is a link between the pp and the pub", then "1 - good." So Sequeda, Nomic and DSPy each get two records. The preprint keeps the key the bibliography gave it (sequeda2023, nussbaum2024nomic, khattab2023dspy), typed article with arXiv as repository and its arXiv identifier, with its file (Sequeda's local preprint PDF linked in place; Nomic and DSPy preprints fetched). The published version is its own record: new keys from refs's naming policy for Sequeda (GRADES-NDA 2024) and Nomic (TMLR 2025), and the existing khattab2024 for DSPy. Each pair gets an unnamed link from task 1. The TDD cites the published versions, so three keys change at adoption, in the commit that switches its bibliography.

2. GPT-4: "2 - ok". One record: the TDD cites the existing openai2023gpt4, OpenAI's requested citation; no v6 record; its context notes that the TDD cited arXiv v6 (2024).

3. The owner's own works outside this bibliography, including the second INSIGHT article, are deferred: "3, 5 - yes, defering this to the cv pass is logical". Out of scope here.

4. ReMatch: "4 - OMG a citation was hallucenated! ok". Four-author arXiv preprint confirmed by session 1: arXiv's record for 2403.01567 has no journal reference or DOI and was last revised 2024-05-30 (v2); a web search found no venue; an EMNLP 2025 industry-track paper cites it as "arXiv preprint arXiv:2403.01567". Put that evidence in the record's context.

5. Notes to context: "6 - ok". The INSIGHT DEMA article's published details as proposed.

6. One engine: "just use citeproc, maybe add a note about investigating back-ref support with it in the future". All four outputs use citeproc with the IEEE CSL, so there is one target: docs/references.json, csl-json-v1, read by the TDD and both PDD formats. The PDD PDF drops cite-method biblatex and backref at adoption; its gate compares the current biber render with the new citeproc render, so expect wording changes there and list them. The back-reference note is in the refs ledger (cba907f); nothing for you to do about it.

7. IEEE and talks: IEEE's reference guide expects the conference's city for a presented talk, and the vendored ieee.csl prints a speech's place only from publisher-place. Propose, for the owner's approval with this revision: a small edit to dema-llm's copy of ieee.csl (made by the dema-llm session at adoption) so a speech falls back to event-place, and event-place as the city (AI4SE: Washington, DC, USA, with The George Washington University kept in context; INFORMS: Atlanta, GA, USA). Show both talks' renders with the edit.

8. FedRAMP and CMMC corrected in place: "9 - ok". Use dema-llm commit c6c5ffb, docs/reports/2026-09-27-standards-check.md: fedramp2024 describes "FedRAMP Consolidated Rules for 2026", U.S. General Services Administration, release 2026.09.22.01, https://www.fedramp.gov/2026/; dod2020cmmc describes "Cybersecurity Maturity Model Certification (CMMC) Program", 32 CFR Part 170, Department of Defense, final rule 89 FR 83214 published 2024-10-15, effective 2024-12-16, https://www.ecfr.gov/current/title-32/subtitle-A/chapter-I/subchapter-G/part-170; nist2020sp80053 stays Rev. 5 with context recording the catalog release checked, 5.2.0. Choose types honestly (the CFR part is legislation or regulation in CSL terms; say which and why) and show renders.

9. Fetched files go under unfiled by the convention: "10 - 0k".

Also: dema-llm is now at 8c28e25 (46fda2a delivered PDD, c6c5ffb standards rule and report, 8c28e25 AGENTS.md untracked again and the findings noted); its four uncommitted owner paths remain the execution precondition. Keep the rewrite approach: settled items in the plan, open ones in the decisions list, shorter where decisions removed material. Report the branch, commit and open decisions here, then wait.
