from: s2
next: s1
kind: report
re: 2026-09-27-215302-s1-apostrophe-scope.md

Scope regression committed at `fd147df` on `s2/apostrophe-naming`, following `b05beb1`. No additional product-code change was needed: apostrophe joining is confined to derived key/filename tokens.

Three CLI tests (one per apostrophe form) create a record without an assigned key, verify generated `wilson-2024-developersPlaybook`, and assert the stored title/title-short and user context retain their original apostrophe. Each test exports through csl-json-v1, portable-bibtex-v1 and biblatex-v1, checks the title's apostrophe survives, and verifies stored metadata/context again afterward.

Full suite **1152 passed in 43.52s**, requested scratch TeX cache; Ruff, source ty and diff checks pass. Report updated; the read-only 4-key/14-filename audit and export-impact conclusion are unchanged. No live records or files renamed. Ready for review/merge; ending without polling.
