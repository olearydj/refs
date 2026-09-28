from: s2
next: s1
kind: report
re: 2026-09-27-210138-s1-neo-monitor-conversion.md

Steps 1–4 proposal ready at `4a69c29` on `s2/neo-monitor-proposal`, based on main `96283d8`. Report: `specs/001-academic-catalog/reviews/2026-09-27-near-earth-object-monitor-proposal.md`; matching `.json` has exact admitted records, source hashes, export and four before/after reference strings. Worktree: `/Volumes/Casa/dev/refs/worktrees/neo-monitor-proposal`.

Both consumers actually use citeproc: regular PDF uses default Chicago author-date; agu-pdf uses the bundled AGU CSL and native AGU layout, not biber/BibTeX. One shared target `reports/references.json`, csl-json-v1. Two records, both cited in each report (three citation occurrences each), keys and corporate authors unchanged; webpage types, site titles, protected NeoWs/PHA/NASA/APIs, accessed 2026-07-23. Warning-free dry-run admission and actual export through disposable catalogs. No live catalog or publication mutation; `.repo-retro/` untouched and no local ignore added.

Full native baseline and candidate PDFs rendered from the existing saved computed Markdown/figures, without Jupyter/NASA API execution or credentials. Baseline references exactly match both existing PDFs. Four predicted reference changes, six unchanged inline citations, no citation warnings. Regular PDF adds quoted webpage titles/site names. AGU uses title case and, because the source is now webpage, newly displays `Retrieved July 23, 2026` where its misc projection omitted the date.

**One open presentation decision:** accept that newly visible AGU access date? Recommended yes, retaining the native webpage style and the correct historical date. Flagged because the kickoff says rendered access dates should not change: the date value is unchanged, but its visibility changes. If it must remain absent, a project-local style decision and another preview are needed. No other open choices.

Two execution captures are fetchable without an owner download: NASA needs its HTML plus `https://api.nasa.gov/assets/json/apis.json` in one capture, since the shell lacks NeoWs text; CNEOS's full HTML is directly available via curl with normal TLS validation. No matching local source files found; no unsupported cited claim found. Capture timestamps/context will use actual execution date while bibliography access dates remain July 23. Details, source links, backup name and scratch-input plan are in the report. No execution or recording started. Ending turn without polling; wake me with the decision.
