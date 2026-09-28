from: s2
next: s1
kind: report
re: 2026-09-27-133313-s1-dema-llm-proposal-kickoff.md

Proposal complete; stopped at guide step 4. Branch `s2/dema-llm-proposal`, commit `db524a3cbd05aaedffe6edf906f34c866c844627`. Not merged.

Report: `worktrees/dema-llm-proposal/specs/001-academic-catalog/reviews/2026-09-27-dema-llm-proposal.md` (branch-relative `specs/001-academic-catalog/reviews/2026-09-27-dema-llm-proposal.md`).

Inventory: 34 bibliography entries, all cited in TDD; six in PDD; seven distinct arXiv-linked entries (thirteen matching lines). Four artifacts use two engines: TDD HTML/PDF and PDD DOCX use IEEE CSL, while PDD PDF uses IEEE biblatex/biber. Proposed three targets, four gates. Untouched-input dry assessment predicts 34 new records, but GPT-4 has an existing DOI-bound identity with another key/version and DSPy has an existing published-version candidate. Those need decisions before intake.

Primary/local sources contradict Sequeda title/coauthors and ReMatch authors/SIGMOD venue. Later publications found for Sequeda, Nomic and DSPy; no substitutions made. Seven primary works found locally, three further version/title candidates, 27 keys still needing acquisition or identity decisions. Exact arXiv wording and every material non-arXiv change are in the report.

Fidelity findings: literal `others` becomes a named author in three CSL references; arXiv archive labels disappear in IEEE CSL; the vendored speech macro reads legacy `event` rather than `event-title`; proceedings volumes and webpage years disappear under semantic retypes. Native biber retains the arXiv identification and speech event facts. No workaround or product/style change made.

Owner decisions (verbatim from proposal):

1. Choose the preprint or later publication separately for Sequeda (2023 arXiv versus GRADES-NDA 2024), Nomic (2024 arXiv versus TMLR 2025) and DSPy (2023 preprint versus ICLR 2024 / existing `khattab2024`). Current probe keeps the preprints. Choosing another version requires revised predictions before execution.
2. Resolve GPT-4 identity/version/year/key handling before intake: current bibliography says v6/2024 under `openai2024gpt4`; catalog holds 2023 under `openai2023gpt4` with the common DOI and earlier file. Neither duplicate creation nor changing citations/shared keys is authorized. A choice requiring an alias/export capability becomes a separate refs decision, not a conversion workaround.
3. Approve the source-supported Sequeda title/coauthors and ReMatch four-author/preprint corrections, and the INSIGHT published metadata. Approve or amend Allison B. on AI4SE: slide cover contradicts the bibliography and CV's A. N.; no external CV correction is included.
4. Decide the actual cited object for Claude 3 (model card versus launch page), the historical targets for embeddings/FedRAMP/CMMC, and whether the shorter-title GradeBot poster is the intended INFORMS source. Unresolved files stay missing; no invented dates or current-version substitution.
5. Decide how the disclosed fidelity blockers should be handled in a separate refs/style pass before this conversion can be adopted: literal `others`, CSL arXiv identification, speech event fields, proceedings volumes and webpage dates. This proposal requests no workaround and does not implement a fix.
6. Approve or amend the title-case/protection policy, the nine note-to-context moves, the obsolete forthcoming-note retirement and the semantic retypes. These cause the visible changes documented above; a style loss is not implicitly accepted by approving a type.
7. Approve three targets/four consumer gates, all 34 cited memberships, proposed file placement and the 27-key acquisition/identity list. Execution still requires a clean publication commit, revised proposal if any choice changes it, and a quoted owner decision delivered through `comms/`. Acquisition gaps may only be carried forward as explicitly disclosed missing sources. Gate acceptance, fixture recording and adoption remain later owner gates.

Verification: all 957 hashed publication/catalog inputs unchanged; publication dirty status unchanged. Fresh scratch CSL baseline matches current TDD HTML for all 34 entries, and current TDD PDF contains all 34 baseline strings after whitespace/punctuation normalization. Current PDD DOCX/PDF inspected; native biber and citeproc hypothetical probes completed only in scratch. Markdown checks pass. No unrelated full product suite run for this documentation-only change. Both refs main and the proposal worktree are clean. Catalog/store/project untouched; no import, backup, source acquisition, live export, record, adoption, merge or remote operation.

Scratch evidence: `/private/tmp/refs-dema-proposal/`. I am watching comms for your next message; owner gates remain with you.
