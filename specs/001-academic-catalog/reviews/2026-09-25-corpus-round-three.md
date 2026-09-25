# Corpus round three

The round-three manifest contains the 105 round-two bibliography files, 15 Nelson Beebe bibliographies shipped in TeX Live 2026basic, and 425 files from `test/fixtures/export` in the Better BibTeX checkout at `9c116f5c472e6f53934c16950f8e467f07433294`. The 545-file, 60,454-entry manifest, bounded batch manifests, and machine-readable results are under `/Volumes/Casa/tmp/refs-corpus3.UJF8YT`. The Beebe source root came from `kpsewhich -var-value TEXMFDIST`: `/usr/local/texlive/2026basic/texmf-dist/bibtex/bib/beebe`. Its 15 files are `epodd.bib`, `font.bib`, `litprog.bib`, `printing-history.bib`, `serif.bib`, `stanford-cstr.bib`, `texbook1.bib`, `texbook2.bib`, `texbook3.bib`, `texgraph.bib`, `texjourn.bib`, `texnique.bib`, `tugboat.bib`, `type.bib`, and `typeset.bib`; `manifest.json` records the full source path and size of each. The 425 export fixtures comprise 400 native Zotero bundles, 24 CSL JSON arrays, and one result object that is inapplicable as input. Every element of each CSL array went through the existing `add --format csljson` route.

Each batch started from a disposable clone of `/Volumes/Casa/tmp/refs-rehearsal-20260924` and removed its working home after the gate. The owner's copy was unchanged: the SHA-256 of `cat/catalog.sqlite` was `d4c75afdcb436136d15bc855e3ebb399731bbadf56479f0993864c09373f26d5` before and after. Preflight verified the manifest count, entry spans, and at least twice the 8,000,000,000-byte temporary-disk ceiling in free space; the gate checked disk between files and passed its remaining 3,600-second deadline to each command and Pandoc process. The batches stayed within 600 files, 80,000 entries, 60 minutes, and 8 GB each. Separate homes avoid cross-batch identity interactions.

## Round-two regression check, run before the ratchet

| Batch | Files | Entries | Applied | Unchanged | Conflict | Invalid | Time | Peak additional disk |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Owner copies and first import fixtures | 20 | 3,954 | 2,739 | 212 | 714 | 289 | 143.97 s | 352,038,912 B |
| Remaining import fixtures except issue 720 | 84 | 8,520 | 7,357 | 7 | 16 | 1,140 | 663.06 s | 719,306,752 B |
| Issue 720 large library | 1 | 8,965 | 8,906 | 0 | 45 | 14 | 1,066.43 s | 1,625,694,208 B |
| **Total** | **105** | **21,439** | **19,002** | **219** | **775** | **1,443** | **1,873.46 s** | **1,625,694,208 B maximum** |

The old and new per-file results account for exactly the same 21,439 entry spans. The five changed alias decisions moved from `invalid_bib_entry` to `alias_conflict` after the fix pass; the accepted `Jun.` month rule admitted one formerly invalid entry in the second batch. The other classifications, including the large issue 720 file, match round two. The large-file batch first encountered the old 4 GB free-space check when shared APFS free space fell during the run; its working home was removed and the same file completed under this round's approved 8 GB ceiling. That diagnostic attempt is excluded from the table. There was no fix-pass regression in the round-two corpus.

Across the completed regression batches, refusal codes were `invalid_bib_entry` 1,443, `value_conflict` 769, `alias_conflict` five, and `identity_conflict` one. Re-import applied zero entries: 19,221 unchanged, 775 conflicts, and 1,443 invalid. Sixty-five exports rendered through Pandoc with exit zero, eight were blocked, 27 had empty selections, and five project citations refused `import_origin_ambiguous`. Blocked-export findings remained `invalid_identifier` 658, `case_colliding_key` 40, `invalid_export_value` two, and `accessed_unassessed` one. All 556 recorded managed resources remained available in every batch; the owner-copy batch reported 182 missing linked paths, the second batch four linked paths of which three were missing, and the large batch no additional links. Backup and restore compared all 20 tables and reopened each restored home; resource checks contained 738, 561, and 556 items.

## Ratchet results

| Route and batch | Files | Candidate entries | Applied or created | Unchanged | Conflict | Invalid | Whole-file refusal | Time | Peak additional disk |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| TeX Live Beebe BibTeX | 15 | 12,196 | 4,793 applied | 284 | 5,376 | 1,743 | 0 | 368.04 s | 1,465,782,272 B |
| BBT native Zotero | 400 | 2,354 | 768 applied | 59 | 56 | 221 | 4 files, 1,250 entries | 588.84 s shared JSON batch | 2,719,358,976 B shared JSON batch |
| BBT CSL arrays | 24 | 24,465 | 223 created | 0 | 0 | 24,242 | 0 | same JSON batch | same JSON batch |
| BBT result object | 1 | 0 | 0 | 0 | 0 | 0 | inapplicable | same JSON batch | same JSON batch |

Beebe's entry refusal codes were `alias_conflict` 5,174, `invalid_bib_entry` 1,743, `value_conflict` 177, and `identity_conflict` 25. Re-import applied zero: 5,077 unchanged, 5,376 conflict, and 1,743 invalid. Two exports rendered through Pandoc with exit zero and no stderr, five were blocked, three were empty, and five project citations refused `import_origin_ambiguous`. The blocked exports contained 190 `invalid_identifier` findings. Resource check found 556 available managed resources; backup and restore matched all 20 tables and reopened a home with 556 checked items.

The native Zotero route processed all 1,104 entries in the 396 accepted bundles: 768 applied, 59 unchanged, 56 conflicts, and 221 invalid. Its named refusal codes were `invalid_zotero_item` 51, `unknown_zotero_type` 104, `key_author_required` 62, `unknown_creator_role` four, and `value_conflict` 56. Four whole bundles refused `invalid_zotero_input` because a child note had an unsupported parent type; those bundles contained 1,250 candidate primary entries and are counted separately. Native re-import applied zero: 827 unchanged, 56 conflict, and 221 invalid. Two project citations refused `import_origin_ambiguous`; 333 exports rendered through Pandoc with exit zero, 57 were empty, and four were blocked. Their blocking findings were `given_only_name` two, `unassessed_mapping` one, `unassessed_extension` three, and `invalid_identifier` one.

The CSL route attempted all 24,465 elements: 223 created and 24,242 invalid, including 24,238 `invalid_record` and four `key_author_required`. Re-add created zero: 223 `already_present` and 24,242 invalid. One export rendered through Pandoc with exit zero, 20 were empty, and three were blocked, with `issued_date_lost_or_changed` two and `unassessed_mapping` eight. Across the JSON batch, resource check found all 556 managed files available and backup/restore matched every row of all 20 tables; the restored home checked 556 items. No accepted export produced Pandoc stderr. The inapplicable result object was classified and counted as a file, but never sent to an import command.

The five completed batches took 2,830.34 seconds in aggregate; each stayed below its own 3,600-second ceiling, and the largest additional physical disk use was 2,719,358,976 bytes against 8,000,000,000. The final JSON result is `json-all-result.json`; the earlier `json-all-before-fix.json` and `json-all-code-fix.json` preserve the diagnostic states. All working homes were removed. These gates used only source fixtures and disposable catalog copies.

## Findings and dispositions

| Finding | Evidence and count | Disposition |
| --- | --- | --- |
| Round-two admission and export limits repeat. | The 1,443 baseline invalid entries, eight blocked exports, and five origin-ambiguous citations reproduce round two, apart from the five accepted alias classifications and one accepted month value. | Kept as named limits; no regression. |
| Beebe `number` and `issue` disagree during binding. | 5,169 of 5,174 `alias_conflict` outcomes are on `metadata.issue`, typically a BibTeX `number` alongside a different `issue`; three concern publisher and two publisher-place. | Proposed input-contract decision for the owner, affecting 5,169 entries. The importer does not guess which value wins. |
| Beebe admission limits include unsupported vocabulary. | Of 1,743 invalid entries, 362 have an unsupported entry type, 336 have `month = {????}`, and 212 contain unsupported TeX or math; seasons and concatenated month expressions also recur. | Kept as explicit refusals with preserved original entries. Any broader BibTeX vocabulary needs a separate assessed rule. |
| Native BBT `Extra` appears as an array of lines. | 498 items carry array-form `extra`; 473 are in processable bundles. The first JSON gate called most of them malformed and applied only 430 native entries. | The disposable fixture wrapper joins those lines into Zotero's string field before import; the final gate applied 768. This does not change refs' Zotero input contract. Commit `b093f4f`, pinned by `test_bbt_native_wrapper_keeps_items_and_children_inside_disposable_directory`. |
| Zotero field conflicts lacked a refusal code. | The first JSON gate found 29 conflicts across nine bundles with paths but no code. The final gate found 56 field conflicts, all named `value_conflict` after the fixture-wrapper correction. | Fixed at the import result site in commit `6fa9530`. The minimized [Zotero fixture](../../../tests/fixtures/real-trial/minimized/zotero-value-conflict.json) and `test_zotero_value_conflict_names_code_and_keeps_current_title` pin the code and unchanged record. |
| Child notes under unsupported Zotero parent types block the directory reader. | Four native bundles, holding 1,250 candidate primary entries, refuse as whole inputs with `invalid_zotero_input` and an unresolved parent. | Proposed input-contract decision for the owner. The harness preserves the parent relation and does not invent a source or discard the child. |
| Native Zotero vocabulary remains bounded. | Processed bundles report 104 `unknown_zotero_type`, 51 `invalid_zotero_item`, 62 `key_author_required`, and four `unknown_creator_role`. | Kept as named per-item limits. No unassessed type, role, or creator spelling is mapped automatically. |
| CSL numeric-string date parts dominate refusals. | 24,212 of 24,238 `invalid_record` outcomes first fail on digit-string date parts: `issued` 21,185, `accessed` 3,026, and `event-date` one. The [CSL input schema](https://github.com/citation-style-language/schema/blob/master/schemas/input/csl-data.json) permits strings as well as numbers in date parts. | Proposed narrow input-contract widening for the owner, affecting 24,212 elements. This run leaves refs' integer-only profile unchanged. |
| Export refuses unassessed projections and unsafe values. | Beebe has 190 unsafe identifiers; native Zotero blocks four exports for names, mapping, extension, or identifier findings; CSL blocks three for date loss or unassessed mapping. | Kept as named safety limits; no blocked export was rendered. |

The JSON gate itself is pinned by `test_csl_array_worker_counts_each_add_and_readd` and the native-wrapper test in commit `4e86a0a`. The product fix and wrapper adjustment each passed the full 703-test suite, Ruff, and ty on `src/refs`. Final verification repeated 703 passing tests, 121 demo checks, and the isolated real-trial harness with zero failures. The round-three gate introduced no table, command, dependency, or changed input contract.

## Unsupported type census across rounds one to three

This census counts source entries by their declared type, independently of which validation error an import reported first. Round two includes round one's files; round three includes round two's files and adds Beebe BibTeX and BBT JSON. Counts are therefore cumulative within each route, not additive across columns. BibTeX has 27 unsupported-type entries in the 18-file round-one manifest, 157 in the 105-file round-two manifest, and 520 in the 120 BibTeX files of round three; the latter includes 363 Beebe entries. Round three adds 15 CSL entries with unsupported types and seven Zotero parent items of unsupported types with child notes or attachments. The earlier reports count 143 and 362 `invalid_bib_entry` outcomes whose first reported reason was unsupported type; this source census also counts entries with another first failure. No type is admitted by this census.

| Route | Unsupported type | Round 1 | Round 2 | Round 3 | Example entry |
| --- | --- | ---: | ---: | ---: | --- |
| bib | `audio` | 0 | 10 | 10 | Import error with character '+' in BibTeX field name #2660.bib: 10.13:91a |
| bib | `booklet` | 0 | 0 | 32 | font.bib: Anonymous:1986:MCF |
| bib | `collection` | 0 | 7 | 7 | BBT does not import groups from JabRef 5.1 #1641.bib: Hornborg2012 |
| bib | `constitution` | 0 | 6 | 6 | Import error with character '+' in BibTeX field name #2660.bib: 11.9:23 |
| bib | `dataset` | 0 | 6 | 6 | Import error with character '+' in BibTeX field name #2660.bib: 10.9:75a |
| bib | `film` | 1 | 1 | 1 | web_page and other mendeley idiocy.bib: <empty key> |
| bib | `generic` | 24 | 24 | 24 | web_page and other mendeley idiocy.bib: Callahan2011 |
| bib | `hardware` | 0 | 2 | 2 | Import error with character '+' in BibTeX field name #2660.bib: 10.10:78a |
| bib | `image` | 0 | 11 | 11 | Import error with character '+' in BibTeX field name #2660.bib: 10.14:97a |
| bib | `inreference` | 0 | 3 | 3 | Better BibLaTeX import improvements #549.bib: Algar1985 |
| bib | `jurisdiction` | 0 | 8 | 8 | Import error with character '+' in BibTeX field name #2660.bib: 11.4:1 |
| bib | `legadminmaterial` | 0 | 3 | 3 | Import error with character '+' in BibTeX field name #2660.bib: 11.7:19 |
| bib | `legal` | 0 | 1 | 1 | Import error with character '+' in BibTeX field name #2660.bib: 11.10:29 |
| bib | `legislation` | 0 | 8 | 8 | Import error with character '+' in BibTeX field name #2660.bib: 11.5:8 |
| bib | `legmaterial` | 0 | 4 | 4 | Import error with character '+' in BibTeX field name #2660.bib: 11.6:14 |
| bib | `movie` | 0 | 2 | 2 | Improve import of films #1837.bib: Marka.S:2011movie |
| bib | `nameonly` | 0 | 28 | 28 | Import error with character '+' in BibTeX field name #2660.bib: 9.44:1a |
| bib | `periodical` | 0 | 2 | 177 | Import error with character '+' in BibTeX field name #2660.bib: 10.1:12a |
| bib | `presentation` | 0 | 4 | 4 | Import error with character '+' in BibTeX field name #2660.bib: 10.5:60 |
| bib | `proceedings` | 1 | 3 | 159 | Some bibtex entries quietly discarded on import from bib file #873.bib: Etzioni:SWAgents |
| bib | `reference` | 0 | 1 | 1 | Import error with character '+' in BibTeX field name #2660.bib: 10.2:33c |
| bib | `softwareversion` | 1 | 1 | 1 | import software related biblatex entries #1544.bib: delebecque:hal-02090402v1 |
| bib | `talk` | 0 | 1 | 1 | Import Jabref fileDirectory, unexpected reference type #1058.bib: Afonso2011 |
| bib | `video` | 0 | 20 | 20 | Film references do not export properly for APA formating #2494.bib: formanOneFlewCuckoo1975 |
| bib | `webpage` | 0 | 1 | 1 | accessDate must be ISO date #2376.bib: r42 |
| csl | `broadcast` | 0 | 0 | 3 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.csl.json: friends:leia:tv |
| csl | `dataset` | 0 | 0 | 1 | Setting the item type via the cheater syntax #587.csl.json: noauthor_object_nodate |
| csl | `entry-encyclopedia` | 0 | 0 | 2 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.csl.json: Blair2004 |
| csl | `legal_case` | 0 | 0 | 1 | Better CSL JSON does not include authority field #2019.csl.json: WhiteState1966 |
| csl | `motion_picture` | 0 | 0 | 2 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.csl.json: Doe2015 |
| csl | `musical_score` | 0 | 0 | 1 | Setting the item type via the cheater syntax #587.csl.json: mozart_sonatas_1960 |
| csl | `pamphlet` | 0 | 0 | 1 | Setting the item type via the cheater syntax #587.csl.json: clark_mesopotamia_1957 |
| csl | `performance` | 0 | 0 | 1 | Does setting a type via cheater syntax work currently #2473.csl.json: nachwilliamshakespeareHamlet2001 |
| csl | `review-book` | 0 | 0 | 2 | Setting the item type via the cheater syntax #587.csl.json: kamp_deconstructing_2006 |
| csl | `video` | 0 | 0 | 1 | Extra field type video not exported #3536.csl.json: marreEdge1992 |
| zotero | `artwork` | 0 | 0 | 1 | Does setting a type via cheater syntax work currently #2473.json: Hamlet nach William Shakespeare |
| zotero | `encyclopediaArticle` | 0 | 0 | 1 | Bulk performance test.json: All Watched Over by Machines of Loving Grace (TV series) |
| zotero | `map` | 0 | 0 | 2 | Bulk performance test.json: Brönsholm By. Karlebo Sogn, Lynge Kronborg Herred, Frederiksborg Amt. Matrikulskort i 1:4000. Trykt i juli 1939. Gyldighedsperiode 1939-77 |
| zotero | `podcast` | 0 | 0 | 1 | raw bibtex fields with colon in extra #2750.json: ‘Unfinished business’: Ring CEO Liz Hamren leads Amazon’s home monitoring products into the AI era |
| zotero | `tvBroadcast` | 0 | 0 | 1 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.json: The one with the Princess Leia fantasy |
| zotero | `videoRecording` | 0 | 0 | 1 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.json: The one with the Princess Leia fantasy |

The examples identify the source file and its entry key, CSL id, or Zotero parent title. Each source path is in the corresponding manifest under `/Volumes/Casa/tmp/refs-phase6.2V9Id6`, `/Volumes/Casa/tmp/refs-corpus2.kMP4Kz`, or `/Volumes/Casa/tmp/refs-corpus3.UJF8YT`. The repeatable counter is `tests/fixtures/real-trial/corpus_type_census.py`; its minimized three-route fixture test pins the counting rule.
