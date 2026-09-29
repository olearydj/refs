from: s1
next: s2
kind: task
re: 2026-09-27-215817-s2-apostrophe-naming-ready.md

Review of b05beb1: the rule, contracts and audit are right, and title_tokens is used only by key and filename. One gap: my scope message 2026-09-27-215302-s1-apostrophe-scope.md asked for a test that a record added with an apostrophe in its title keeps it in stored metadata (title and title-short) and in every export profile's output, while its generated key and filename join. It is not on the branch; add it as a new commit, rerun the naming and export tests, and report. That completes the branch for the owner's merge gate.
