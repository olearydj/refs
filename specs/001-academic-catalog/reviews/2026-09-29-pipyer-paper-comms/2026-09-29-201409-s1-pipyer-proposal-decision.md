from: s1
next: s2
kind: decision
re: 2026-09-29-200933-s2-pipyer-proposal-ready.md

Session 1 asked the owner: "Approve the pipyer proposal with Kapoor switched to the TMLR publication and Pydantic AI kept at 1.106.0?" Owner, verbatim (selected option): "Approve, 1A + 2B (Recommended)", whose description read: "Cite the TMLR 2025 publication; except Pydantic AI from the release-on-access rule and cite 1.106.0, the version Pipyer pins. Codex re-predicts that one entry, then executes."

Why 2B, as put to the owner: paper.qmd cites pydanticai2026 as Pipyer's own dependency ("LLM components return declared, schema-checked outputs through PydanticAI"), and /casa/dev/pipyer/uv.lock resolves pydantic-ai 1.106.0; citing 2.51.0 would name a version Pipyer has not run on.

Session 1 merged the proposal into main as ebb845f (merge of 69ae3a7). Execute on a new branch s2/pipyer-paper-execution from main:

1. Revise pydanticai2026 under 2B: software, kind repository, version 1.106.0, issued 2026-06-05 (from PyPI history). The README and API captures are taken at the v1.106.0 release tag's commit, not the default branch, each named with that commit and the capture date. Context states in one sentence that the version is the one Pipyer's uv.lock pins, cited by the owner's exception to the current-on-access rule (2026-09-29). Do not invent an accessed date; say how the entry renders. Re-predict this entry from a disposable admission and render. If it prints as the 1.106.0 release with its June 5 date and the repository URL, carry on without stopping; if not, stop and report.
2. Then steps 5 to 10 as the proposal states for everything else: backup, no re-import, record completions, kapoor-2025-aiAgents added and linked to kapoor2024, project membership switched, ordinary fetches attached under unfiled with short labels, register row on the execution branch with the scratch preparation, the conversion check without --record, and the per-entry result. The Mermaid approval in 2026-09-29-200402-s1-pipyer-mermaid-decision.md covers the check's renders.
3. Owner fetches: the owner has been asked to download the Nextflow (Nature Biotechnology 35:316-319), Kapoor TMLR (OpenReview Zy4uFzMviZ) and Snakemake (Bioinformatics 28(19):2520-2522) PDFs into ~/Downloads. Verify each edition before attaching with resource add --move. If they are not there when you reach attachment, finish everything else, then send a question naming what is missing and end your turn; do not report the pass complete with them unattached or undisclosed.

Do not edit the project; adoption is done afterwards by session 1's subagent, at the owner's acceptance of the gate. Report here with the branch, tip and gate table.
