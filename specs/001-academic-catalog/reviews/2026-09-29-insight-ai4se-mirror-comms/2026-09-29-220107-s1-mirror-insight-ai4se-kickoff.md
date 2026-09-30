from: s1
next: s2
kind: task
re: -

Owner, verbatim, on what this pass is: "recording them in the catalog = making sure all sources from both papers are in refs and that a project / publication is configured for each, right? not trying to make refs the source of the bibliographic data for both, just mirroring it \"in spirit\"." And: "we would add a note about this to both papers' projects. I would make the refs entries as correct as possible - they may be more correct than the papers' version and that is find. add it to the note. if you agree, proceed".

So this is a mirror pass, not a conversion: no adoption, no export into either paper, no register row, no conversion check. Each paper keeps its own references.bib as its bibliographic source, frozen as printed or submitted. Proposal half first (read-only: no catalog writes, no backup, no fetch into stores, no edit in either paper), then stop for the owner. Main is at f75d9d7. Protocol: ack and go straight on; end your turn after the report.

Papers:
1. /Volumes/Casa/pub/2026-insight-dema-llm (git; published). references.bib, 7 entries. Session 1's read-only match found 4 in the catalog (ledford2023dissertation, ledford2023ieee, ledford2025syseng, oleary2025ai4se) and 3 missing: ledford2024mbe (Ledford's 2024 MBE & QIF Summit presentation), ledford2024patent (US Patent 12,131,134, issued 2024-10-29), oleary2025techreport (O'Leary, DEMA-LLM Technical Development Report, ICAMS lab, 2025-09). Note the catalog also has gadzey2026dema-digital-thread, a 2026 poster sharing the dissertation's title; do not confuse them.
2. /Volumes/Casa/pub/rejected/2026-ai4se-pipyer (git; rejected, archived as submitted). proposal/references.bib, 5 entries, all matched: oleary2025ai4se, oleary2026insight -> catalog olearyledford2026insight, ledford2023dissertation, ledford2023ieee, ledford2025syseng. Confirm which entries the submitted abstract actually cites.

Verify these matches yourself (by DOI, title, identity), and confirm each paper's cited list against its prose and rendered or submitted output.

Proposal must cover:
- Each cited work mapped to its catalog key, with the paper's own key where it differs.
- The 3 new INSIGHT records, each checked against its source (the patent against USPTO/Google Patents; the talk and report for a public record under the "Scope of works" decision in docs/behavior-decisions.md, since refs catalogs citable works). Anything failing that rule is listed for the owner, not added. Make every record as correct as the sources allow; where a catalog record is more correct than a paper's entry, list the difference as information, not a change to the paper. Name forms: the owner is "Danny J. O'Leary" on every record where he is an author.
- Two refs projects, names proposed (e.g. insight-dema-llm, ai4se-pipyer-proposal), each citing exactly the works its paper cites, with a --description note. Draft the note text: the paper keeps its own references.bib, frozen as published or submitted; the refs project mirrors which works it cites; the refs records are kept as correct as possible and may be more correct than the paper's printed entries, which is fine.
- A short docs/refs.md for each paper folder saying the same, plus how to find the project (refs project show <name>). It will be committed by session 1's subagent, staging that file only: both repos have uncommitted owner work (INSIGHT: modified .gitignore and README.md, untracked AGENTS.md, PROJECT_CONTEXT.md, admin/; AI4SE: modified .gitignore, untracked REJECTED.md) that must be left alone.
- Sources to attach for the 3 new records where they exist, and an owner fetch list if any.
- Anything else needing the owner's judgment, numbered with options and a recommendation; if nothing, say so.

Deliverable: specs/001-academic-catalog/reviews/2026-09-29-insight-ai4se-mirror-proposal.md on branch s2/insight-ai4se-mirror-proposal. Report here with branch, tip and the decisions list.
