from: s1
next: s2
kind: task
re: 2026-09-27-133255-s2-pong.md

dema-llm conversion, proposal half only.

Read AGENTS.md, docs/conversion-guide.md (the whole order, rules and report template), and the manufacturing proposal specs/001-academic-catalog/reviews/2026-09-27-manufacturing-training-proposal.md as the model. Work in a fresh worktree from main at 78708e1.

Project: /Volumes/Casa/dev/dema-llm. refs project name: dema-llm. Bibliography: docs/references.bib, 34 entries (10 article, 1 incollection, 7 inproceedings, 12 misc, 1 phdthesis, 3 techreport; 13 mention arXiv). Consumers as found so far: the TDD Quarto book (docs/tdd/_quarto.yml) and the PDD overview (docs/pdd/DEMA-LLM-Overview.qmd, link-bibliography true), both with docs/csl/ieee.csl; confirm or extend this list in step 1, including any script or other reader.

Do guide steps 1 to 4 and stop. Everything is read-only: the catalog through SQLite mode=ro or refs read commands, the project and every store in step 9's list untouched, no import, no backup, no fetch, no scratch export into the project. The project has uncommitted work by its owner (.gitignore, docs/README.md, pyproject.toml, an untracked docs/dema-data-vocabulary-alignment.md); leave it alone and note it in the proposal as a precondition for execution.

This project tests the preprint edge. For every arXiv entry, the proposal says what the record will be (type, container or archive, number, any later published version found by DOI or title), what IEEE prints for it today from the current render, and what it will print from each planned profile, entry by entry. Where a published version exists, list it as a decision for the owner, not a change you make. Where refs cannot express what IEEE prints today, name it as a refs finding; do not propose a workaround.

Deliverable: specs/001-academic-catalog/reviews/2026-09-27-dema-llm-proposal.md in the report template's first sections (backup name, inventory and consumers, cited keys against the bibliography, planned import with expected outcomes including DOI bindings to existing sources, planned record completions by key, sources found with paths and the fetch list with links, planned targets and profiles, expected gate outcome per entry per consumer), then the owner's decisions as a numbered list, then findings in two lists (refs, guide). Commit it on a branch; do not merge.

Reply here as kind: report, next: s1, with the branch name, the commit, and the decisions list. Questions along the way come here as kind: question. Then wait for my next message.
