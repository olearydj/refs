# CV prerequisite fixes — 2026-09-28

Owner authorization, relayed by Session 1: “7 - fix” (CV proposal decision 10 in the original numbering). Branch `s2/cv-prerequisite-fixes`, based on `641d61a`. This implements only the two refs defects; the CV proposal, live CV, live catalog, conversion register and accepted fixtures are unchanged. Merge remains the owner's gate.

## Changes

BibTeX text decoding now treats a bare `&` as literal text instead of TeX alignment whitespace. The decoder's text context overrides only that special character; escaped `\&` continues to decode as `&`, and math still follows the existing separate preservation path. Tests cover titles, proceedings containers, corporate authors and notes with both spellings.

Update previews now replace the complete editable part of the current record with the canonical result instead of overlaying it. Cleared optional fields therefore stay absent. The CLI regression retypes an imported `inproceedings` record from `paper-conference` to `speech`, clears `native_type` via a patch, checks that preview leaves the database bytes unchanged, serializes the preview to CSL JSON, executes the same patch, reads the stored record, and verifies equivalent editable fields and export bytes. Execution still increments the revision; preview retains the current revision as before.

## CV before and after

Both code versions imported the five affected entries from `/Volumes/Casa/pub/cv/refs/all.bib` into separate empty disposable catalogs under `/private/tmp/refs-cv-fixes-evidence/{before,after}`. The two proceedings records expose three stored field changes. Three additional `howpublished` values change when decoded for the proposal's conversion mapping; ordinary BibTeX admission preserves those original fields without promoting them to modeled metadata. This extends the kickoff's examples by the ARMR container and the innovation-culture description. Exact strings, including old whitespace, are retained in the accompanying JSON.

- `oleary2025armr-training`, container-title: `Proceedings of the IISE Annual Conference     Expo 2025` → `Proceedings of the IISE Annual Conference & Expo 2025`.
- `oleary2025econ-uncertainty`, title: `Estimating Real-World Uncertainty: Case Studies     Stochastic Models for Graduate Engineering Economy` → `Estimating Real-World Uncertainty: Case Studies & Stochastic Models for Graduate Engineering Economy`.
- `oleary2025econ-uncertainty`, container-title: `Proceedings of the IISE Annual Conference     Expo 2025` → `Proceedings of the IISE Annual Conference & Expo 2025`.
- `oleary2026pipyer-ai4se`, howpublished (decoded original, not modeled metadata): `Paper-presentation extended abstract submitted to the AI4SE     SE4AI Research and Application Workshop, June 12, 2026; proposed presentation September 22–23, 2026` → `Paper-presentation extended abstract submitted to the AI4SE & SE4AI Research and Application Workshop, June 12, 2026; proposed presentation September 22–23, 2026`.
- `olearyledford2025ai-enhanced-dema`, howpublished (decoded original, not modeled metadata): `Workshop presentation, AI4SE     SE4AI Research and Application Workshop, George Washington University, September 2025` → `Workshop presentation, AI4SE & SE4AI Research and Application Workshop, George Washington University, September 2025`.
- `olearyficken2025innovation-culture`, howpublished (decoded original, not modeled metadata): `Conference presentation, IISE Annual Conference     Expo 2025` → `Conference presentation, IISE Annual Conference & Expo 2025`.

## Re-import impact

Yes: the canonical incoming text changes for existing BibTeX records whose modeled fields contain bare ampersands. This fix is not a catalog migration. Re-importing the same five raw entries into the old-code disposable catalog with the fixed code yielded two conflicts (ARMR and engineering economy) and three unchanged records; zero applied and zero invalid. The existing populated titles and containers were not silently overwritten. The normal reconciliation rules still govern acceptance or filling of incoming values. Existing bad text needs an explicit correction or conflict resolution. Original `howpublished` remains preserved rather than becoming a new modeled field.

## Verification

- Full locked suite with `TEXMFVAR` and `TEXMFCACHE` set to `/private/tmp/refs-csl-tex-cache`: **1,207 passed**, including corpus and rehearsal tests (43.70 seconds). This was the full automated suite, not a new 545-file external corpus campaign.
- `uv run --locked ruff check .` and `uv run --locked ty check src/refs`: passed.
- The new regressions run against the unchanged main source fail for the bare ampersand and stale `native_type`; escaped ampersand passes (two failures, one pass). The initial test setup used an unsupported `--clear` shorthand; the final regression uses the supported patch interface and the entire suite was rerun successfully.
- `conversion_check.py --all --work /private/tmp/refs-cv-prerequisite-conversion`, without `--record`: exit **0**; every entry identical across all five projects and twelve consumers. All rendering ran in scratch with native project pipelines.

| Project | Consumer | Identical entries |
| --- | --- | --- |
| jhl-report | quarto | 92 |
| jhl-report | site | 103 |
| jose-danvas | quarto | 11 |
| jose-danvas | jose | 11 |
| manufacturing-training-media-tradeoffs | html | 39 |
| manufacturing-training-media-tradeoffs | elsevier | 39 |
| dema-llm | tdd-html | 34 |
| dema-llm | tdd-pdf | 34 |
| dema-llm | pdd-docx | 6 |
| dema-llm | pdd-pdf | 6 |
| near-earth-object-monitor | neo-report | 2 |
| near-earth-object-monitor | neo-report-agu | 2 |

Scratch evidence: `/private/tmp/refs-cv-fixes-evidence/` (before/after catalogs, extracted records, re-import outcomes and scripts); `/private/tmp/refs-cv-fixes-suite-final.log`; `/private/tmp/refs-cv-fixes-regression-before.log`; `/private/tmp/refs-cv-prerequisite-conversion/gate.json` and `gate.md`. The companion JSON retains the compact CV diff and conversion counts; no source bibliography or publication file was edited.
