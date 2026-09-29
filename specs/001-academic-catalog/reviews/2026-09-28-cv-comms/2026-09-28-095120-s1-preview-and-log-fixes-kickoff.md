from: s1
next: s2
kind: task
re: -

Owner, verbatim: "yes" (to one small fix branch for two findings from a usage report of the Bostrom intake on 2026-09-28). New pass: re-read comms/README.md (ack with task, folder and session id; no polling; end your turn after each message). Main is at 47f6f2f.

Branch s2/preview-and-log-fixes from main, two rules, each with tests per docs/testing-convention.md:

1. add's dry-run preview omits the label segment. Session 1 reproduced it: `refs add --format refs --input <new record> --file <pdf> --copy --label "probe label" --dry-run` previews unfiled/ProbeLabelPreview-2020.pdf, while execution names the file with the label segment (the Bostrom intake got ...-2012-Author-hostedfulltextjournalarticle.pdf). `resource add ... --label ... --dry-run` previews correctly (LLMOps-2025-probelabel.pdf). Make add's preview use the same naming path as execution, and test that preview and execution names are equal with and without a label, for add and resource add.

2. Help and read-only commands need a writable mutation log. In a sandbox, `refs --help` printed help but exited 2 because the log was unwritable; the ledger already notes `refs show` warning for the same reason. Help must exit 0 without touching the log, and read-only commands (show, list, search, summary, kinds, resource check, schema, config show, paths) must work, without error, when the log is unwritable; commands that mutate keep failing closed if they cannot log first. Test both sides, including that a mutation still refuses when the log is unwritable.

Do not change the label's character rule (the owner has an open question on turning spaces into hyphens). Contract sentences where the behaviour is stated. Full suite with TEXMFVAR and TEXMFCACHE at /private/tmp/refs-csl-tex-cache, Ruff, ty. No export change is expected; if any export path is touched, run the all-project conversion check without --record. Report here; merging is the owner's gate.
