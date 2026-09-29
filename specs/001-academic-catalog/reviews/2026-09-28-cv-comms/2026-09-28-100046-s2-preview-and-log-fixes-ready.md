from: s2
next: s1
kind: report
re: 2026-09-28-095120-s1-preview-and-log-fixes-kickoff.md

Ready for review: c0e6f3e on s2/preview-and-log-fixes, based on main 47f6f2f. Worktree: /Volumes/Casa/dev/refs/worktrees/preview-and-log-fixes.

Both fixes are complete. add's preview now passes the label into the same copy planner used by execution. Source inspection also found that add --copy omitted the label during execution and its preflight, so both now receive it too. The label character rule is unchanged. Eight CLI cases cover add/resource add, copy/move, and absent/spaced labels: each pins the exact conventional basename, compares preview with execution, verifies preview leaves the database and files untouched, and verifies executed destination bytes and original retention/removal.

Explicit root/group/leaf --help now bypasses log selection and the bare-command error path, returning 0 without opening the log. Twelve help cases cover absent, writable, and unwritable logs. Diagnostic log open/write failures are silent best effort, so read-only commands work without a writable log; twelve CLI cases cover all requested commands plus project show, import list, and collection list, asserting no errors or stderr and unchanged database/log bytes. Mandatory mutation logging remains intact. The existing unwritable-log mutation refusal test still pins exit 5, log_unwritable, and unchanged database, now with empty stderr rather than an extra diagnostic warning. Existing durable mutation, fsync-before-unlink, and verbose console tests also pass.

Updated CLI and file contracts, and reconciled the logging brief's two obsolete sentences about every command logging and failures warning. No export implementation or serialization path changed, so no all-project conversion check was required and no fixtures were recorded. No owner catalog or library files touched.

Validation: focused capture/logging suite 63 passed; full suite with TEXMFVAR and TEXMFCACHE at /private/tmp/refs-csl-tex-cache: 1,184 passed in 43.11s; Ruff, ty check src/refs, and git diff --check passed. Logs: /private/tmp/refs-preview-log-focused.txt and /private/tmp/refs-preview-log-suite.txt.

Merge remains the owner's gate. Ending this turn without polling.
