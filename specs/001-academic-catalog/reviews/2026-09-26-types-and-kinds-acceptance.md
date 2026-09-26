# Types and kinds acceptance — 2026-09-26

Worktree: `/Volumes/Casa/dev/refs-types`, branch `types-kinds`, based on `bd72f03`. Main remains at `bd72f03`. The four commits are `1b44b1e` (types and mappings), `1d29509` (deferred types), `b335eab` (kinds), and `818f786` (optional update guard). The full suite passed at each commit: 778, 807, 829 and 831 tests. Final Ruff and ty checks on `src/refs` are clean. All 575 records in the owner’s sample were exported against a pre-change baseline, using a read-only catalog connection; no export bytes changed.

Both manifests retain the baseline file lists. Both gates ran sequentially through `corpus_parallel.py` from fresh clones of `/Volumes/Casa/tmp/refs-rehearsal-20260924`, with default workers, 100,000,000,000 temporary bytes and 86,400 seconds. Nothing resumed. The merged disk peak sums overlapping volume-wide readings and is not meaningful. The per-file results, progress and shard reports are retained in this directory.

## Gates

| Gate | Files | Entries | Applied | Created | Unchanged | Conflict | Invalid | Workers | Wall seconds | Sum of file seconds | Sum / wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bib | 120 | 33,635 | 29,731 | 0 | 45 | 901 | 2,958 | 14 | 191.93 | 640.72 | 3.34 |
| json | 425 | 26,819 | 26,412 | 95 | 4 | 25 | 283 | 14 | 173.27 | 590.52 | 3.41 |

The sum of per-file wall times is a serial-equivalent measurement under parallel contention, not a measured serial rerun. Every shard’s restore compared 21 tables with matching rows. Re-import applied or created no sources: BibTeX reported 29,776 unchanged, 901 conflict and 2,958 invalid; JSON reported 26,416 unchanged, 95 already present, 25 conflict and 283 invalid. All 556 managed resources remained available in every shard. There were no shard failures or serial fallbacks.

## Refusals by code

| Gate | Code | Count |
| --- | --- | ---: |
| bib | alias_conflict | 11 |
| bib | invalid_bib_entry | 2958 |
| bib | value_conflict | 890 |
| json | invalid_record | 30 |
| json | invalid_zotero_item | 52 |
| json | key_author_required | 175 |
| json | unknown_creator_role | 4 |
| json | unknown_zotero_type | 22 |
| json | value_conflict | 25 |

## Every changed import outcome, file by file

The baseline is `/Volumes/Casa/tmp/refs-corpus3-perf.cjs40te2`. Counts below are in applied / created / unchanged / conflict / invalid order. The JSON comparison files record changes in refusal reasons, re-import, export and render as well as import outcomes.

| Gate | File | Old outcome counts | New outcome counts | Newly admitted spellings in this file |
| --- | --- | --- | --- | --- |
| bib | Some bibtex entries quietly discarded on import from bib file #873.bib | 915 / 0 / 0 / 13 / 60 | 916 / 0 / 0 / 13 / 59 | proceedings: 1 |
| bib | web_page and other mendeley idiocy.bib | 391 / 0 / 3 / 18 / 53 | 410 / 0 / 3 / 20 / 32 | film: 1, generic: 24 |
| bib | import software related biblatex entries #1544.bib | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | softwareversion: 1 |
| bib | BBT does not import groups from JabRef 5.1 #1641.bib | 19 / 0 / 0 / 0 / 1 | 20 / 0 / 0 / 0 / 0 | collection: 1 |
| bib | Better BibLaTeX import improvements #549.bib | 2 / 0 / 0 / 0 / 7 | 4 / 0 / 0 / 0 / 5 | collection: 1, inreference: 1 |
| bib | Better BibTeX.003.bib | 1 / 0 / 0 / 0 / 1 | 2 / 0 / 0 / 0 / 0 | proceedings: 1 |
| bib | Film references do not export properly for APA formating #2494.bib | 0 / 0 / 0 / 0 / 4 | 4 / 0 / 0 / 0 / 0 | video: 4 |
| bib | Import Jabref fileDirectory, unexpected reference type #1058.bib | 1 / 0 / 0 / 0 / 1 | 2 / 0 / 0 / 0 / 0 | talk: 1 |
| bib | Import error with character '+' in BibTeX field name #2660.bib | 126 / 0 / 0 / 2 / 155 | 166 / 0 / 0 / 3 / 114 | audio: 10, collection: 5, dataset: 5, image: 11, inreference: 2, periodical: 2, presentation: 4, proceedings: 1, video: 15 |
| bib | Improve import of films #1837.bib | 1 / 0 / 0 / 0 / 3 | 4 / 0 / 0 / 0 / 0 | movie: 2, video: 1 |
| bib | Report number field is incorrectly translated into the issue field when importing a dataset from a .bib file #2752.bib | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | dataset: 1 |
| bib | font.bib | 818 / 0 / 0 / 1 / 190 | 858 / 0 / 0 / 1 / 150 | booklet: 4, periodical: 4, proceedings: 33 |
| bib | litprog.bib | 232 / 0 / 0 / 0 / 79 | 250 / 0 / 0 / 1 / 60 | proceedings: 20 |
| bib | printing-history.bib | 255 / 0 / 0 / 0 / 410 | 256 / 0 / 0 / 0 / 409 | proceedings: 1 |
| bib | texbook1.bib | 258 / 0 / 0 / 0 / 128 | 286 / 0 / 0 / 0 / 100 | booklet: 12, periodical: 1, proceedings: 17 |
| bib | texbook2.bib | 376 / 0 / 0 / 0 / 155 | 394 / 0 / 0 / 0 / 137 | booklet: 1, periodical: 93, proceedings: 10 |
| bib | texbook3.bib | 617 / 0 / 0 / 2 / 249 | 663 / 0 / 0 / 2 / 203 | booklet: 12, periodical: 1, proceedings: 39 |
| bib | texgraph.bib | 109 / 0 / 0 / 0 / 64 | 112 / 0 / 0 / 0 / 61 | proceedings: 3 |
| bib | texjourn.bib | 0 / 0 / 0 / 0 / 68 | 37 / 0 / 0 / 0 / 31 | periodical: 68 |
| bib | type.bib | 27 / 0 / 0 / 0 / 5 | 30 / 0 / 0 / 0 / 2 | booklet: 3 |
| bib | typeset.bib | 777 / 0 / 0 / 2 / 135 | 814 / 0 / 0 / 2 / 98 | periodical: 8, proceedings: 33 |
| json | Add support for new Zotero item types #2496.json | 1 / 0 / 0 / 0 / 1 | 2 / 0 / 0 / 0 / 0 | dataset: 1 |
| json | Better BibTeX does not export collections #901.json | 34 / 0 / 0 / 0 / 2 | 36 / 0 / 0 / 0 / 0 | encyclopediaArticle: 2 |
| json | Bulk performance test.json | 1173 / 0 / 0 / 0 / 68 | 1196 / 0 / 0 / 0 / 45 | encyclopediaArticle: 1, map: 21, videoRecording: 1 |
| json | Collected notes.json | 34 / 0 / 0 / 0 / 2 | 36 / 0 / 0 / 0 / 0 | encyclopediaArticle: 2 |
| json | Compare export times.json | 48 / 0 / 0 / 0 / 38 | 86 / 0 / 0 / 0 / 0 | encyclopediaArticle: 38 |
| json | Does setting a type via cheater syntax work currently #2473.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | artwork: 1 |
| json | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.csl.json | 0 / 1 / 0 / 0 / 6 | 0 / 6 / 0 / 0 / 1 | broadcast: 2, entry-encyclopedia: 2, motion_picture: 2 |
| json | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.json | 1 / 0 / 0 / 0 / 6 | 6 / 0 / 0 / 0 / 1 | encyclopediaArticle: 2, film: 1, tvBroadcast: 2, videoRecording: 1 |
| json | Export to BetterBibTeX .bib no longer works and fails #3352.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | encyclopediaArticle: 1 |
| json | Exporting item type film merges scriptwriter with other contributors #2802.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | film: 1 |
| json | Extra field type video not exported #3536.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | tvBroadcast: 1 |
| json | Film references do not export properly for APA formating #2494.json | 0 / 0 / 0 / 0 / 4 | 4 / 0 / 0 / 0 / 0 | film: 1, tvBroadcast: 2, videoRecording: 1 |
| json | Inconsistent Citation Key #2953.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | dataset: 1 |
| json | Language field in the metadata exported incorrectly #1921.json | 48 / 0 / 0 / 0 / 38 | 86 / 0 / 0 / 0 / 0 | encyclopediaArticle: 38 |
| json | Multiple creators in Extra not exported in Better CSL JSON #2015.csl.json | 0 / 0 / 0 / 0 / 1 | 0 / 1 / 0 / 0 / 0 | broadcast: 1 |
| json | Multiple creators in Extra not exported in Better CSL JSON #2015.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | tvBroadcast: 1 |
| json | Really Big whopping library.csl.json | 24252 / 0 / 0 / 6 / 94 | 24252 / 0 / 0 / 8 / 92 | None; see non-admission changes below |
| json | Setting the item type via the cheater syntax #587.csl.json | 0 / 0 / 0 / 0 / 5 | 0 / 2 / 0 / 0 / 3 | dataset: 1, pamphlet: 1 |
| json | add date, origdate functions, and format-date filter #1488.json | 2 / 0 / 0 / 0 / 2 | 4 / 0 / 0 / 0 / 0 | forumPost: 2 |
| json | date wrongly imported from yaml-file day gets 00 prefixed #3542.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | encyclopediaArticle: 1 |
| json | raw bibtex fields with colon in extra #2750.json | 0 / 0 / 0 / 0 / 1 | 1 / 0 / 0 / 0 / 0 | podcast: 1 |
| json | type dataset exported as @data instead of @dataset for BibLaTeX #1720.json | 1 / 0 / 0 / 0 / 1 | 2 / 0 / 0 / 0 / 0 | dataset: 1 |

### Changes outside files containing new admissions

bib: no import outcome changed in a file without a newly admitted spelling.

json: `Really Big whopping library.csl.json`: {"old": {"applied": 24252, "unchanged": 0, "conflict": 6, "invalid": 94}, "new": {"applied": 24252, "unchanged": 0, "conflict": 8, "invalid": 92}}.

Across the 592 newly admitted declared spellings, 437 entries now apply or are created, four BibTeX entries become conflicts (three value conflicts and one alias conflict), and 151 still meet another existing input refusal (149 BibTeX and two JSON). The two JSON refusals are the `emptybook` entry in the paired creator-field fixtures: each lacks a usable title, URL or book-part identification. The BibTeX limits include unsupported TeX, malformed entries, dates and missing work identification; the comparison JSON retains each changed refusal reason. These inputs are admitted by type without weakening the existing validators.

The extra large-CSL change predates this branch: main’s profile-path fix allows the two formerly invalid `metadata.source` fills to reach the normal value-conflict handling. No other file without an admitted spelling changes import outcome.

## Census after admission

The census counts declared types independently of the first refusal. BibTeX fell from 520 to 62 unsupported entries (458 admitted spellings), CSL from 15 to six (nine admitted), and Zotero from 147 to 22 (125 admitted). None of the admitted spellings remains. Admission can expose another existing input refusal or an identity/value conflict, so successful applications need not equal those source counts. Known deferred types carry the recommendation shown below; unrepresented spellings retain their refusal without a guessed mapping.

| Route | Declared type | Count | CSL type to admit | Example | Recommendation |
| --- | --- | ---: | --- | --- | --- |
| bib | constitution | 6 | legislation | Import error with character '+' in BibTeX field name #2660.bib: 11.9:23 | Admit CSL type legislation by adding a registry type row. |
| bib | hardware | 2 | — | Import error with character '+' in BibTeX field name #2660.bib: 10.10:78a | No assessed CSL mapping |
| bib | jurisdiction | 8 | legal_case | Import error with character '+' in BibTeX field name #2660.bib: 11.4:1 | Admit CSL type legal_case by adding a registry type row. |
| bib | legadminmaterial | 3 | legislation | Import error with character '+' in BibTeX field name #2660.bib: 11.7:19 | Admit CSL type legislation by adding a registry type row. |
| bib | legal | 1 | legal_case | Import error with character '+' in BibTeX field name #2660.bib: 11.10:29 | Admit CSL type legal_case by adding a registry type row. |
| bib | legislation | 8 | legislation | Import error with character '+' in BibTeX field name #2660.bib: 11.5:8 | Admit CSL type legislation by adding a registry type row. |
| bib | legmaterial | 4 | legislation | Import error with character '+' in BibTeX field name #2660.bib: 11.6:14 | Admit CSL type legislation by adding a registry type row. |
| bib | nameonly | 28 | — | Import error with character '+' in BibTeX field name #2660.bib: 9.44:1a | No assessed CSL mapping |
| bib | reference | 1 | — | Import error with character '+' in BibTeX field name #2660.bib: 10.2:33c | No assessed CSL mapping |
| bib | webpage | 1 | — | accessDate must be ISO date #2376.bib: r42 | No assessed CSL mapping |
| csl | legal_case | 1 | legal_case | Better CSL JSON does not include authority field #2019.csl.json: WhiteState1966 | Admit CSL type legal_case by adding a registry type row. |
| csl | musical_score | 1 | musical_score | Setting the item type via the cheater syntax #587.csl.json: mozart_sonatas_1960 | Admit CSL type musical_score by adding a registry type row. |
| csl | performance | 1 | performance | Does setting a type via cheater syntax work currently #2473.csl.json: nachwilliamshakespeareHamlet2001 | Admit CSL type performance by adding a registry type row. |
| csl | review-book | 2 | review-book | Setting the item type via the cheater syntax #587.csl.json: kamp_deconstructing_2006 | Admit CSL type review-book by adding a registry type row. |
| csl | video | 1 | — | Extra field type video not exported #3536.csl.json: marreEdge1992 | No assessed CSL mapping |
| zotero | bill | 1 | bill | Customise name-separator and list-separator #1927.json: of Rights | Admit CSL type bill by adding a registry type row. |
| zotero | case | 5 | legal_case | @jurisdiction; map court,authority to institution #326.json: Dalain | Admit CSL type legal_case by adding a registry type row. |
| zotero | letter | 13 | personal_communication | Bulk performance test.json: Brev fra Byplannævnet, Hovedstadsafdelingen, til Byudviklingsudvalget for Københavnsegnen | Admit CSL type personal_communication by adding a registry type row. |
| zotero | statute | 3 | legislation | @legislation; map code,container-title to journaltitle #327.json: Loi n<sup>o</sup> 2011-525 du 17 mai 2011 de simplification et d'amélioration de la qualité du droit | Admit CSL type legislation by adding a registry type row. |

## Ten slowest files per gate

| Gate | File | Wall seconds |
| --- | --- | ---: |
| bib | Async import, large library #720.bib | 163.29 |
| bib | Unabbreviate on import #1436-3.bib | 112.25 |
| bib | tugboat.bib | 58.71 |
| bib | stanford-cstr.bib | 31.13 |
| bib | Unabbreviate on import #1436-2.bib | 23.79 |
| bib | zotero-bbt-export.bib | 17.13 |
| bib | Maintain the JabRef group and subgroup structure when importing a BibTeX db #97.bib | 16.2 |
| bib | Some bibtex entries quietly discarded on import from bib file #873.bib | 13.79 |
| bib | texbook3.bib | 13.41 |
| bib | font.bib | 12.39 |
| json | Really Big whopping library.csl.json | 134.33 |
| json | Bulk performance test.json | 15.63 |
| json | Ternary in citekey formula.json | 3.66 |
| json | lone ogonek should have brace.json | 3.27 |
| json | use author dash separation rather than camel casing in citekey #1495.json | 2.76 |
| json | Wrong performance for exports Bibtex a becomes textbackslash a #3184.json | 2.47 |
| json | Compare export times.json | 2.27 |
| json | Language field in the metadata exported incorrectly #1921.json | 2.05 |
| json | POST to pull-export #3258.json | 1.92 |
| json | Export as Collected Notes does not list subcollections #1768.json | 1.92 |

## Scope counts

There are 29 invocable commands: 28 leaf commands plus the import group’s own batch action. This adds one command, `kinds`, and four option placements: `add --kind`, `update --kind`, `list --kind`, `search --kind`. `--if-revision` on update changes from required to optional. There is no new table or dependency. Application Python is 5,909 → 6,061 physical lines.

| Part | Added | Removed | Net lines |
| --- | ---: | ---: | ---: |
| application | 198 | 46 | +152 |
| tests | 335 | 11 | +324 |
| governing_docs | 8 | 5 | +3 |
| registry_packaged | 2603 | 187 | +2416 |
| registry_contract | 2602 | 186 | +2416 |

## Tests by part

`tests/contract/test_types_and_kinds.py` pins all nine portable type/genre round trips, registry/model agreement, native spellings and portable native labels, and the deferred-type details per route. `test_corpus_type_census.py` pins source counting and recommendations. `test_kinds.py` pins kind assignment on all add routes, update, conflicts and unchanged state, filtering before pagination, derived-kind removal, warnings in previews and persisted import records, origin assignment, registry-owned words, JSON output and a read-only kinds command. `test_optional_update_guard.py` pins both omitted and supplied revision guards, stale refusal and unchanged state. Existing export assertions remain in force.

The owner sample catalog SHA-256 after both gates is `d4c75afdcb436136d15bc855e3ebb399731bbadf56479f0993864c09373f26d5`, matching the pre-run hash.
