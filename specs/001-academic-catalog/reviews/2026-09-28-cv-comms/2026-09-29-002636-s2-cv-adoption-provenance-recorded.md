from: s2
next: s1
kind: report
re: 2026-09-29-002457-s1-cv-rerecord-approved.md

Re-recorded at clean adopted CV commit **84ad8ab0192988ea0e59dfc6fb99815261a289f9** after verifying the approval conditions (44 CV and 379 other entries identical, both checks exit 0). Provenance committed as **488107e** on **s2/cv-execution**; worktree `/Volumes/Casa/dev/refs/worktrees/cv-execution` is clean.

Fresh recording command: `uv run --locked python tests/fixtures/real-trial/conversion_check.py --project cv --work /private/tmp/refs-cv-adopted-record-20260929 --record`. Exit **0**, `recorded: true`, **44 identical**. Both fixtures are byte-for-byte unchanged from the accepted fixtures; hashes verified against register provenance. Both publication_commit values now point to 84ad8ab. Only register provenance and its status note changed. `git diff --check` passed.

The live CV remains clean. No live export, CV commit or merge performed. Branch is ready for your review and the owner's merge gate. Ending this turn; no watch.
