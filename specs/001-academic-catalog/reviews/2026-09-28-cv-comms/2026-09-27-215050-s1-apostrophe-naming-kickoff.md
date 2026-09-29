from: s1
next: s2
kind: task
re: -

Owner, verbatim: "do a kickoff for the apostophe handling issue, for s2". New pass: re-read comms/README.md (no polling; ack with task, folder and session id; end your turn after each message; session 1 wakes you with codex queue). Main is at 072cdd5.

The issue. records.md's title-token rule says "punctuation separates words, letters/digits stay together", so an apostrophe inside a word splits it: "The Developer's Playbook ..." gave key wilson-2024-developerS and file TheDeveloperSPlaybookForLargeLanguageModelSecurity-2024.pdf; existing managed files include ...InstructureSCanvasLMS... and ...LargeLanguageModelSAccuracy.... The creator policy already removes apostrophes ("allow surname hyphens, remove spaces/apostrophes"); the title rule lacks the same exception.

Task, on branch s2/apostrophe-naming from main: an apostrophe between letters (straight ', typographic U+2019 and modifier U+02BC) joins the letters instead of separating words, for title tokens in generated keys and for the conventional filename: "Developer's" -> "Developers", "Model's" -> "Models", "O'Reilly" -> "OReilly". Other punctuation keeps separating. One rule, tests per docs/testing-convention.md (key and filename, all three apostrophe forms, a leading or trailing apostrophe, and a counterexample where other punctuation still separates), and the contract sentence in records.md (and files-and-recovery.md if the filename rule is stated separately). Keep it the smallest change; do not touch creator keys.

Existing keys and filenames do not change: assigned keys never regenerate, and existing names are preserved. Read-only, list every existing catalog key and managed or linked filename that the new rule would have produced differently, with old and new form, for the owner to decide separately whether to rename any (wilson-2024-developerS was created tonight and is cited by no project). Full suite with TEXMFVAR and TEXMFCACHE at /private/tmp/refs-csl-tex-cache, Ruff, ty. If any export byte could change, run the all-project conversion check without --record and report; I expect none, since keys are stored. Report here with the branch, commit and the list; merging is the owner's gate.
