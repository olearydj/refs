# Input limits batch acceptance — 2026-09-26

Branch `input-limits`, worktree `/Volumes/Casa/dev/refs-input-limits`, based on main `e48e089`. The three commits are `d223db4` (balanced math spans), `54f090a` (creator-token fallback), and `3812691` (seasons). Full-suite results were 840, 847 and 867 passed respectively. Final Ruff and ty checks on `src/refs` passed. The read-only owner export check passed over all 575 sample records, byte-identical to its pre-types export baseline; the owner catalog hash remained unchanged.

Owner refinements: the new warning is the plain string `creator_token_fallback` at its site, with a test asserting its name; no code registry was added. Season spelling is canonicalized at the CSL level: autumn and fall become season 3, and export writes lowercase spring, summer, autumn or winter. No season word is stored in `issued.literal`; original evidence retains the supplied spelling.

Both unchanged file lists were run sequentially through `corpus_parallel.py` from fresh clones of `/Volumes/Casa/tmp/refs-rehearsal-20260924`. Both manifests set 100,000,000,000 temporary bytes and 86,400 seconds, with unchanged volume-wide disk measurement. Neither gate resumed. No shard failed. The merged peak sums overlapping volume-wide readings and is not meaningful. Shard reports and checkpoints are retained here; successful gates removed their disposable homes as designed. A separate disposable JabRef import-history clone is retained for the diagnostic described below.

## Gate results

| Gate | Files | Entries | Applied | Created | Unchanged | Conflict | Invalid | Workers | Wall seconds | Sum of file seconds | Sum / wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bib | 120 | 33,635 | 30,469 | 0 | 45 | 909 | 2,212 | 14 | 194.08 | 630.97 | 3.25 |
| json | 425 | 26,819 | 26,587 | 95 | 4 | 25 | 108 | 14 | 139.77 | 521.59 | 3.73 |

The summed file times were measured under parallel contention, so the ratios are not measured serial speedups. Every shard restored matching rows across 21 tables. Each shard reported all 556 managed resources available. BibTeX also reported recorded external links, including missing linked files already represented in the inputs. Re-import applied or created nothing: BibTeX had 30,514 unchanged, 909 conflict and 2,212 invalid; JSON had 26,591 unchanged, 95 already present, 25 conflict and 108 invalid.

BibTeX exported and rendered 81 files; 18 exports blocked, 16 selections were empty, and five project selections refused because their import origin was ambiguous. JSON exported and rendered 382 files; 22 exports blocked, 20 selections were empty, and one Better BibTeX result object remained inapplicable.

## Admissions and remaining limits

| Rule | Previously invalid → applied | Previously invalid → conflict | Other outcome changes |
| --- | ---: | ---: | --- |
| Math verbatim | 622 | 4 | Six previously applied entries now explicitly refuse unmatched math delimiters; four previously applied entries become value conflicts when math-bearing metadata is preserved |
| Creator-token fallback | 175 | 0 | All 175 key_author_required refusals disappear; no new JSON conflict |
| Seasons | 126 | 0 | Two existing CSL seasonal dates lose their issued_date_lost_or_changed export finding |

Math has 626 newly valid parser proposals, of which four end in conflicts: `furtmayr_2011`, `kawakami_2006`, `liu_2004` and `sun_2002` in `Unabbreviate on import #1436-3.bib`. The remaining 622 applications and all 126 seasonal applications are reconciled with file outcome deltas. The four other added conflict outcomes are one each in the dissertation and owner Better BibTeX bibliography, plus two in `Unabbreviate on import #1436-3.bib`. Total BibTeX conflicts increase by eight, all value_conflict; alias_conflict stays at 11. Preserved math-bearing abstract/title values remain subject to the existing binding rule.

The six new unmatched-delimiter refusals are four video entries in `Film references do not export properly for APA formating #2494.bib`, whose keywords contain `Mentally ill$$QMentally ill`, and `Trivich_1978` and `Wang_1980_proc` in the JabRef fixture. They retain invalid_bib_entry and their original bytes. A targeted replay of the JabRef shard’s preceding imports and that file on a fresh clone reproduced the published gate counts exactly, resolving the distinction between new admissions and new explicit refusals. `new-jabref-refusals.json` identifies the latter two.

Unknown commands outside math, unmatched delimiters, unknown/non-month values such as ???? and invalid calendar values still refuse. Math is kept opaque rather than interpreted. Missing or unusable title tokens still require a supplied citation key; key_author remains a strict override. A season needs a structured numeric date to enter CSL season; month-only evidence without a date retains the existing unresolved-month limitation. Other pre-existing profile, type and creator-role refusals remain. No new type, table, command, option or dependency was added.

## Refusals and conflicts by code

| Gate | Code | Before | After |
| --- | --- | ---: | ---: |
| bib | alias_conflict | 11 | 11 |
| bib | invalid_bib_entry | 2958 | 2212 |
| bib | value_conflict | 890 | 898 |
| json | invalid_record | 30 | 30 |
| json | invalid_zotero_item | 52 | 52 |
| json | key_author_required | 175 | 0 |
| json | unknown_creator_role | 4 | 4 |
| json | unknown_zotero_type | 22 | 22 |
| json | value_conflict | 25 | 25 |

## Every changed import outcome, file by file

The baseline is `/Volumes/Casa/tmp/refs-types-corpus.3f49ffl3`. Counts are applied / created / unchanged / conflict / invalid. Exactly 24 files change import outcomes in each gate; the other 497 files retain theirs. No import outcome change is attributable to a rule outside this batch. The JSON comparison artifacts also retain all changes in refusals, conflict paths, re-import, export and render.

| Gate | File | Before | After | Reason |
| --- | --- | --- | --- | --- |
| bib | dissertation / references.bib | 76 / 0 / 4 / 212 / 0 | 75 / 0 / 4 / 213 / 0 | preserved math metadata exposes one additional value conflict |
| bib | zotero-bbt-export.bib | 194 / 0 / 11 / 357 / 0 | 193 / 0 / 11 / 358 / 0 | preserved math metadata exposes one additional value conflict |
| bib | Some bibtex entries quietly discarded on import from bib file #873.bib | 916 / 0 / 0 / 13 / 59 | 920 / 0 / 0 / 13 / 55 | math: 1 new parser admissions, seasons: 3 new parser admissions |
| bib | Unabbreviate on import #1436-1.bib | 435 / 0 / 0 / 1 / 70 | 445 / 0 / 0 / 1 / 60 | math: 10 new parser admissions |
| bib | Unabbreviate on import #1436-2.bib | 950 / 0 / 0 / 0 / 103 | 970 / 0 / 0 / 0 / 83 | math: 20 new parser admissions |
| bib | Async import, large library #720.bib | 8906 / 0 / 0 / 45 / 14 | 8909 / 0 / 0 / 45 / 11 | math: 3 new parser admissions |
| bib | Author splitter failure.bib | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | math: 1 new parser admissions |
| bib | Failure to handle unparsed author names (92).bib | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | math: 1 new parser admissions |
| bib | Film references do not export properly for APA formating #2494.bib | 4 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 4 | four unmatched $$ refusals |
| bib | Import of langle and rangle TeX commands #1468.bib | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | math: 1 new parser admissions |
| bib | Maintain the JabRef group and subgroup structure when importing a BibTeX db #97.bib | 466 / 0 / 0 / 1 / 444 | 893 / 0 / 0 / 1 / 17 | math: 429 new parser admissions; two previously applied unmatched-$ refusals |
| bib | Math formatting lost on import #627.bib | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | math: 1 new parser admissions |
| bib | Math markup to unicode not always imported correctly #472.roundtrip.bib | 0 / 0 / 0 / 0 / 2 | 1 / 0 / 0 / 0 / 1 | math: 1 new parser admissions |
| bib | Overline during Import #1467.bib | 3 / 0 / 0 / 0 / 5 | 7 / 0 / 0 / 0 / 1 | math: 4 new parser admissions |
| bib | Unabbreviate on import #1436-3.bib | 6429 / 0 / 17 / 228 / 492 | 6555 / 0 / 17 / 234 / 360 | math: 132 new parser admissions; four newly admitted and two previously applied entries conflict |
| bib | eprinttype field dropped on import #959.bib | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | math: 1 new parser admissions |
| bib | font.bib | 858 / 0 / 0 / 1 / 150 | 890 / 0 / 0 / 1 / 118 | math: 4 new parser admissions, seasons: 28 new parser admissions |
| bib | printing-history.bib | 256 / 0 / 0 / 0 / 409 | 281 / 0 / 0 / 0 / 384 | seasons: 25 new parser admissions |
| bib | serif.bib | 0 / 0 / 0 / 0 / 67 | 44 / 0 / 0 / 0 / 23 | seasons: 44 new parser admissions |
| bib | stanford-cstr.bib | 1662 / 0 / 0 / 1 / 82 | 1669 / 0 / 0 / 1 / 75 | math: 7 new parser admissions |
| bib | texbook1.bib | 286 / 0 / 0 / 0 / 100 | 290 / 0 / 0 / 0 / 96 | math: 1 new parser admissions, seasons: 3 new parser admissions |
| bib | texbook2.bib | 394 / 0 / 0 / 0 / 137 | 396 / 0 / 0 / 0 / 135 | math: 2 new parser admissions |
| bib | texbook3.bib | 663 / 0 / 0 / 2 / 203 | 677 / 0 / 0 / 2 / 189 | math: 6 new parser admissions, seasons: 8 new parser admissions |
| bib | typeset.bib | 814 / 0 / 0 / 2 / 98 | 830 / 0 / 0 / 2 / 82 | math: 1 new parser admissions, seasons: 15 new parser admissions |
| json | Arabic script letters in citation keys #2403.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | BBT does not recognize zh-CN #2391.json | 6 / 0 / 0 / 0 / 3 | 9 / 0 / 0 / 0 / 0 | creator fallback: 3 |
| json | Bulk performance test.json | 1196 / 0 / 0 / 0 / 45 | 1229 / 0 / 0 / 0 / 12 | creator fallback: 33 |
| json | Citation key add `_preprint` if URL contains `arxiv.org` #2163.json | 11 / 0 / 0 / 0 / 1 | 12 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Citation key is too long for Chines literature #2320.json | 1 / 0 / 0 / 0 / 4 | 5 / 0 / 0 / 0 / 0 | creator fallback: 4 |
| json | Convert Chinese name to Pinyin in citation key. #2361.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Export web page to misc type with notes and howpublished custom fields #329.json | 0 / 0 / 0 / 0 / 3 | 3 / 0 / 0 / 0 / 0 | creator fallback: 3 |
| json | Exporting to bibtex with unicode as plain-text latex commands does not convert U+2040 #1265.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Japanese rendered as Chinese in Citekey #979.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Kuroshiro hardcoded to apply to all CJK language items when option checked #1928.json | 0 / 0 / 0 / 0 / 2 | 2 / 0 / 0 / 0 / 0 | creator fallback: 2 |
| json | Quotes around last names should be removed from citekeys #856.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Really Big whopping library.csl.json | 24252 / 0 / 0 / 8 / 92 | 24332 / 0 / 0 / 8 / 12 | creator fallback: 80 |
| json | Split CJK names #2624.json | 2 / 0 / 0 / 0 / 33 | 35 / 0 / 0 / 0 / 0 | creator fallback: 33 |
| json | Treat ideographs as individual words for key generation #1353.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Unable to process Russian  ь symbol while transliteration #2413.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Word segmentation for Chinese references #1682.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | Wrong performance for exports Bibtex a becomes textbackslash a #3184.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | [authN_M] citation key syntax has off-by-one error #899.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | braces after textemdash followed by unicode #980.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | citation key format nopunctordash filter list #1880.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | date ranges #747+#746.json | 4 / 0 / 0 / 0 / 1 | 5 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | lastpage not work in better bitex #3050.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | shorttitle in citekeys always pinyinized #2770.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |
| json | transliteration for citekey #580.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | creator fallback: 1 |

## Other changed export/render outcomes, file by file

Nine JSON files keep their import counts while export findings or rendered output change. Seven are effects of the math/season rules; the podcast and dataset render changes come from the already-merged portable-genre correction `0f131dd`, which the types corpus baseline preceded. They are recorded separately here. Every rendered case below still exits 0. All other changes in files whose import counts changed are preserved in the comparison JSON.

| File | Changed result | Reason |
| --- | --- | --- |
| Date export to Better CSL-JSON #360 #811.csl.json | {"export_findings": {"old": {"issued_date_lost_or_changed": 7, "accessed_unassessed": 1}, "new": {"issued_date_lost_or_changed": 5, "accessed_unassessed": 1}}} | seasons |
| Handle HDL not included as eprint for biblatex #3250.json | {"render": {"old": {"exit": 0, "bytes": 510, "warnings": 0}, "new": {"exit": 0, "bytes": 520, "warnings": 0}}} | verbatim math export and title protection |
| Length filter double-counting characters #2525.json | {"render": {"old": {"exit": 0, "bytes": 244, "warnings": 0}, "new": {"exit": 0, "bytes": 243, "warnings": 0}}} | verbatim math export and title protection |
| Math parts in title #113.json | {"render": {"old": {"exit": 0, "bytes": 171, "warnings": 0}, "new": {"exit": 0, "bytes": 169, "warnings": 1}}} | verbatim math export and title protection |
| Mismatched conversion of braces in title on export means field never gets closed #1218.json | {"render": {"old": {"exit": 0, "bytes": 233, "warnings": 0}, "new": {"exit": 0, "bytes": 223, "warnings": 0}}} | verbatim math export and title protection |
| pre not working in Extra field #559.json | {"render": {"old": {"exit": 0, "bytes": 43, "warnings": 0}, "new": {"exit": 0, "bytes": 41, "warnings": 0}}} | verbatim math export and title protection |
| raw bibtex fields with colon in extra #2750.json | {"render": {"old": {"exit": 0, "bytes": 291, "warnings": 0}, "new": {"exit": 0, "bytes": 306, "warnings": 0}}} | inherited portable genre correction |
| tex.title= is not copied verbatim if Zotero title contains math #3376.json | {"render": {"old": {"exit": 0, "bytes": 57, "warnings": 0}, "new": {"exit": 0, "bytes": 55, "warnings": 0}}} | verbatim math export and title protection |
| type dataset exported as @data instead of @dataset for BibLaTeX #1720.json | {"render": {"old": {"exit": 0, "bytes": 149, "warnings": 0}, "new": {"exit": 0, "bytes": 174, "warnings": 0}}} | inherited portable genre correction |

## Ten slowest files per gate

| Gate | File | Wall seconds |
| --- | --- | ---: |
| bib | Async import, large library #720.bib | 166.17 |
| bib | Unabbreviate on import #1436-3.bib | 116.68 |
| bib | tugboat.bib | 59.74 |
| bib | stanford-cstr.bib | 28.9 |
| bib | Unabbreviate on import #1436-2.bib | 22.22 |
| bib | Maintain the JabRef group and subgroup structure when importing a BibTeX db #97.bib | 18.12 |
| bib | zotero-bbt-export.bib | 15.0 |
| bib | Some bibtex entries quietly discarded on import from bib file #873.bib | 12.98 |
| bib | font.bib | 12.84 |
| bib | Unabbreviate on import #1436-1.bib | 11.52 |
| json | Really Big whopping library.csl.json | 101.11 |
| json | Bulk performance test.json | 14.85 |
| json | Compare export times.json | 1.83 |
| json | POST to pull-export #3258.json | 1.78 |
| json | Export as Collected Notes does not list subcollections #1768.json | 1.71 |
| json | Language field in the metadata exported incorrectly #1921.json | 1.65 |
| json | (non-)dropping particle handling #313.json | 1.63 |
| json | Add support for new Zotero item types #2496.json | 1.47 |
| json | Arabic script letters in citation keys #2403.json | 1.43 |
| json | Apply Title Casing to tex.subtitle entry on export #2213.json | 1.43 |

## Tests and line delta

`test_input_limits_math.py` covers all three delimiter forms, byte-preserved export/re-import, two spans with decoded text between, title protection inside math, the named unknown-command refusal and the named unbalanced-delimiter refusal. `test_input_limits_creator.py` covers the Zotero route with and without key_author, the persisted creator_token_fallback notice, citation_key_required with no usable title, an unchanged supplied BibTeX key and the configured title-only template. `test_input_limits_seasons.py` covers every seasonal spelling and case, stored date parts and numeric season, canonical lowercase export/re-import, retained originals, explicit date precision and the named placeholder/non-month refusal. Existing Spring refusal assertions were replaced by the newly approved admission coverage; all numeric, malformed-month and unsupported-concatenation refusal assertions remain.

Application Python is 6,065 → 6,141 physical lines. Governing prose changed only at the three requested sentences. No harness source changed.

| Part | Added | Removed | Net lines |
| --- | ---: | ---: | ---: |
| contract | 3 | 3 | +0 |
| application | 108 | 32 | +76 |
| tests | 190 | 2 | +188 |
| fixtures | 1 | 0 | +1 |

The three commits total +265 lines across application, tests, fixture and contract. The repository worktree is clean and main remains untouched. The gate reports, comparison JSON, per-entry rule attribution, diagnostic entry evidence and manifests remain in this fresh directory for owner review.

Follow-up before merge, commit 35a0119: an unbalanced math delimiter is handled exactly as an unknown TeX command is in the same field, refusing in title, container and creator fields and recorded as a field limitation elsewhere, instead of refusing the entry from any field. The BibTeX gate rerun against the same baseline: 30,476 applied, 45 unchanged, 909 conflicts, 2,205 invalid; the four entries in the film fixture and three JabRef entries apply with a keywords limitation, and the other 118 files are unchanged. Merged to main as 35a0119 on 2026-09-26.
