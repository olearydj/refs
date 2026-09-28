from: s1
next: s2
kind: decision
re: 2026-09-27-135017-s2-dema-llm-proposal-report.md

Owner decision on the dema-llm proposal's decision 5, verbatim: "agree with the fix pass. kick that off while we review 2 and 3". The scope the owner agreed to is below. The proposal itself is not approved; its other decisions are with the owner now and will come back as a revision request. Do not execute any part of it.

Task: one refs fix branch, `s2/csl-fidelity-fixes`, in a fresh worktree from main at 78708e1. Three items, each one rule with tests per docs/testing-convention.md and a contract sentence where the export contract describes that profile.

1. Truncated author lists. BibTeX `and others` currently becomes a creator with family name "others", which IEEE CSL prints as "and others". Pandoc's own conversion of the same input is `{"literal": "others"}`, which citeproc prints as the style's et-al form (session 1 checked this with the dema-llm ieee.csl: "H. Touvron, L. Martin, et al."). Make every profile's consumer print its et-al form for a truncated list: csl-json-v1 as pandoc represents it, biblatex-v1 and portable-bibtex-v1 as `and others`. Decide whether the rule belongs at admission or export and say why; count read-only how many existing catalog records carry a family-name "others" and say what happens to them. No record is changed by this branch.

2. Event name for older styles. csl-json-v1 writes `event-title` only; the vendored IEEE CSL (Zotero, updated 2024-03-27, also used by the family document) reads the older `event`. When a record has `event-title`, csl-json-v1 also writes `event` with the same value, unless the record already has `event`.

3. The arXiv label. Investigate before writing any rule, and stop after the investigation. Report how the CSL 1.0.2 specification and Zotero's CSL JSON export represent a preprint's repository and identifier, how refs stores one today (archive, number, extensions.identifiers.arxiv; the existing catalog record openai2023gpt4 is an example), and what each candidate representation renders through the dema-llm ieee.csl and through the Chicago author-date style the other converted projects use. Send that as kind: question to s1 with the options and renders; implement nothing for item 3 until a decision comes back.

Verification before reporting: full suite, Ruff and ty clean, and `uv run --locked python tests/fixtures/real-trial/conversion_check.py --all` without --record, with every changed entry listed with exact before and after and attributed to item 1 or 2. Nothing is recorded, merged, exported to a project or changed in the catalog. Report here as kind: report, next: s1, with the branch, commits and the walk's per-entry differences. Then wait for my next message.
