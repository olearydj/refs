from: s1
next: s2
kind: decision
re: 2026-09-27-172550-s2-dema-llm-execution-gate.md

Owner, verbatim: "html ref nums - the change is ok for this doc, tdd is internal", "html defect - write it up for dema-llm if that is the right place to investigate / fix it" (session 1 is routing that to the dema-llm session; nothing for you), and "proceed".

The gate is accepted as reported: all 80 entries, the TDD HTML renumbering, and the pre-existing HTML in-text numbering defect left for dema-llm. Session 1 verified the catalog side (747 sources, dema-llm 34 cited, three links, backup present, other targets current).

Now:
1. Record: rerun the same harness command for dema-llm with --record, from the clean publication at 7599aee, with a new --work directory. Confirm it records the four accepted fixtures and that the pre-record gate matches the accepted one.
2. Commit the fixtures and register provenance on s2/dema-llm-execution, and report here.
3. Then stop. Adoption in dema-llm is done by the dema-llm session, which session 1 kicks off after your record report. After adoption, session 1 will ask you to retire the scratch preparation in the register, point it at the adoption commit and rerun the harness without --record; expect it to match the fixtures.

No export to the project and no merge. Merging the execution branch is the owner's gate after adoption verifies.
