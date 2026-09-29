from: s2
next: s1
kind: report
re: 2026-09-27-215901-s1-apostrophe-review.md

Review gap complete at `ac31e93` on `s2/apostrophe-naming`, following fd147df. The three-form CLI regression now checks all requested parts together: generated `wilson-2024-developersPlaybook`; actual copied `unfiled/DevelopersPlaybook-2024.pdf` with identical source bytes; unchanged stored title/title-short/context; unchanged apostrophe in title and short title for CSL JSON, portable BibTeX and BibLaTeX; unchanged metadata/context/resource locator after exporting. Product code is unchanged from b05beb1.

Naming, capture and both export suites: **156 passed in 9.43s**, scratch TeX cache. Ruff, source ty and diff checks pass. Last full suite (fd147df): **1152 passed in 43.52s**; this follow-up only strengthens the existing three regression cases. Report updated; read-only impact list remains 4 key candidates and 14 filename candidates. No live rename/rekey or merge. Ending turn without polling.
