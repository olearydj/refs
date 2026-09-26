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

This census counts source entries by their declared type, independently of which validation error an import reported first. Round two includes round one's files; round three includes round two's files and adds Beebe BibTeX and BBT JSON. Counts are therefore cumulative within each route, not additive across columns. BibTeX has 27 unsupported-type entries in the 18-file round-one manifest, 157 in the 105-file round-two manifest, and 520 in the 120 BibTeX files of round three; the latter includes 363 Beebe entries. Round three adds 15 CSL entries with unsupported types and 147 Zotero primary items of unsupported types, including seven with child notes or attachments. The earlier reports count 143 and 362 `invalid_bib_entry` outcomes whose first reported reason was unsupported type; this source census also counts entries with another first failure. No type is admitted by this census.

| Route | Unsupported type | Round 1 | Round 2 | Round 3 | Example entry |
| --- | --- | ---: | ---: | ---: | --- |
| bib | `audio` | 0 | 10 | 10 | Import error with character '+' in BibTeX field name #2660.bib: 10.13:91a |
| bib | `booklet` | 0 | 0 | 32 | font.bib: Anonymous:1986:MCF |
| bib | `collection` | 0 | 7 | 7 | BBT does not import groups from JabRef 5.1 #1641.bib: Hornborg2012 |
| bib | `constitution` | 0 | 6 | 6 | Import error with character '+' in BibTeX field name #2660.bib: 11.9:23 |
| bib | `dataset` | 0 | 6 | 6 | Import error with character '+' in BibTeX field name #2660.bib: 10.9:75a |
| bib | `film` | 1 | 1 | 1 | web_page and other mendeley idiocy.bib: `<empty key>` |
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
| zotero | `bill` | 0 | 0 | 1 | Customise name-separator and list-separator #1927.json: of Rights |
| zotero | `case` | 0 | 0 | 5 | @jurisdiction; map court,authority to institution #326.json: Dalain |
| zotero | `dataset` | 0 | 0 | 3 | Add support for new Zotero item types #2496.json: MY DGS – annotated. Public Corpus of German Sign Language |
| zotero | `encyclopediaArticle` | 0 | 0 | 85 | Better BibTeX does not export collections #901.json: Abduction |
| zotero | `film` | 0 | 0 | 3 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.json: A film |
| zotero | `forumPost` | 0 | 0 | 2 | add date, origdate functions, and format-date filter #1488.json: Forum post with full date and time |
| zotero | `letter` | 0 | 0 | 13 | Bulk performance test.json: Brev fra Byplannævnet, Hovedstadsafdelingen, til Byudviklingsudvalget for Københavnsegnen |
| zotero | `map` | 0 | 0 | 21 | Bulk performance test.json: Helhedsplan permanent vand |
| zotero | `podcast` | 0 | 0 | 1 | raw bibtex fields with colon in extra #2750.json: ‘Unfinished business’: Ring CEO Liz Hamren leads Amazon’s home monitoring products into the AI era |
| zotero | `statute` | 0 | 0 | 3 | @legislation; map code,container-title to journaltitle #327.json: Loi n<sup>o</sup> 2011-525 du 17 mai 2011 de simplification et d'amélioration de la qualité du droit |
| zotero | `tvBroadcast` | 0 | 0 | 6 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.json: The one with the Princess Leia fantasy |
| zotero | `videoRecording` | 0 | 0 | 3 | Bulk performance test.json: Bruno Latour & Antoine Hennion: L’Ange de l’œuvre. Étienne Souriau, from Aesthetics to an Ontology of Uncertain Beings |

The examples identify the source file and its entry key, CSL id, or Zotero parent title. Each source path is in the corresponding manifest under `/Volumes/Casa/tmp/refs-phase6.2V9Id6`, `/Volumes/Casa/tmp/refs-corpus2.kMP4Kz`, or `/Volumes/Casa/tmp/refs-corpus3.UJF8YT`. The repeatable counter is `tests/fixtures/real-trial/corpus_type_census.py`; its minimized three-route fixture test pins the counting rule.

## Rerun after the owner-approved input decisions

The three batches of the prior 105-file manifest match the round-three record exactly in per-file and aggregate outcome counts. The Beebe batch is the first changed result; its count difference is measured against the original round-three result, not against round two. These four completed batches used the same source files in fresh disposable homes under `/Volumes/Casa/tmp/refs-corpus3-fixes.sUA4yE`, each under the 60-minute and 8-GB limits.

| Batch | Entries | Applied before → after | Unchanged before → after | Conflict before → after | Invalid before → after | New time | New peak additional disk |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prior manifest A | 3,954 | 2,739 → 2,739 | 212 → 212 | 714 → 714 | 289 → 289 | 145.89 s | 76,058,624 B |
| Prior manifest B | 8,520 | 7,357 → 7,357 | 7 → 7 | 16 → 16 | 1,140 → 1,140 | 684.35 s | 56,627,200 B |
| Prior manifest large file | 8,965 | 8,906 → 8,906 | 0 → 0 | 45 → 45 | 14 → 14 | 1,031.07 s | 1,127,796,736 B |
| Beebe | 12,196 | 4,793 → 9,860 | 284 → 285 | 5,376 → 227 | 1,743 → 1,824 | 794.87 s | 1,014,169,600 B |

In Beebe, `alias_conflict` fell from 5,174 to five. The 5,169 resolved alias refusals became 5,067 applied, one unchanged, 20 `value_conflict`, and 81 invalid on later checks; 74 of those invalid entries lack a usable publication identity and seven contain unsupported TeX or math. Re-import applied zero, with 10,145 unchanged, 227 conflict, and 1,824 invalid. One Beebe export rendered through Pandoc with exit zero, five remained blocked, three were empty, and six project citations refused `import_origin_ambiguous`, one more than before. Each completed batch passed resource verification and backup/restore with all 20 tables matching.

## Closing full-manifest rerun: checkpoint

Measured on the pre-performance code, the closing run uses the unchanged 545-file, 60,454-entry manifest, with 120 BibTeX files in one working home and 425 JSON files in another, under `/Volumes/Casa/tmp/refs-corpus3-close.T7ELYa`. The product code includes the accepted CSL batch import (`ab74c0c`); the resumable JSON harness is `5ea3977`. The BibTeX harness now has the same completed-file checkpoint rule, pinned by `test_bib_gate_resumes_after_file_deadline_without_replaying_completed_file`. The earlier separate-home regression comparison above remains the controlled comparison: pooling the prior three BibTeX batches adds cross-file identity interactions.

The BibTeX gate completed all 33,635 entries: 28,187 applied, 570 unchanged, 1,611 conflict, and 3,267 invalid. Against the original separate batches, those counts were 23,795 applied, 503 unchanged, 6,151 conflict, and 3,186 invalid. The prior 105 files in the pooled home contributed 18,327 applied, 285 unchanged, 1,384 conflict, and 1,443 invalid; their separate-home reruns were identical to the round-three record. Beebe contributed 9,860 applied, 285 unchanged, 227 conflict, and 1,824 invalid, matching its fixed-code separate-home result exactly.

BibTeX entry refusal codes were `invalid_bib_entry` 3,267, `value_conflict` 1,575, `identity_conflict` 26, and `alias_conflict` ten. Re-import applied zero: 28,757 unchanged, 1,611 conflict, and 3,267 invalid. Sixty-three exports rendered, twelve were blocked, 33 were empty, and twelve project citations refused `import_origin_ambiguous`. Blocked-export findings were `invalid_identifier` 806, `case_colliding_key` 26, `invalid_export_value` two, and `accessed_unassessed` one. Resource check retained all 556 available managed resources and reported 186 missing and one available linked resource. Backup/restore matched all 20 tables and checked 743 resources. `bib-resume-result.json` holds the complete result.

The first BibTeX attempt exhausted its 60-minute deadline without a checkpoint. The resumable attempt exhausted 120 minutes with 117 files saved, and its retry finished in 1,980.02 seconds; cumulative resumable gate time was 9,180.03 seconds (153.00 minutes), measured on the pre-performance code. Peak volume-wide additional disk measured 6,520,156,160 bytes against 8,000,000,000. JSON likewise exhausted 120 minutes with 302 files saved; its retry later exited at the automatic disk check, with 377 files saved and no active file. Neither process was manually stopped. The JSON checkpoint records 9,225,224,192 bytes of volume-wide free-space loss, while the retained work directory accounts for approximately 5.24 GB of allocated blocks. These partial results are not a completed gate. The owner has superseded the pending disk-accounting question: retain volume-wide measurement and use 100,000,000,000 temporary bytes and 86,400 seconds in the future rerun manifests. Neither the checkpoint nor its manifests are changed now.

The 377 completed JSON files account for 26,125 applied, 57 unchanged, 77 conflict, 413 invalid, 56 created, and 30 already-present outcomes. Re-import applied or created zero. Its named entry refusals so far are `invalid_zotero_item` 51, `unknown_zotero_type` 144, `key_author_required` 172, `value_conflict` 77, `invalid_record` 38, `unknown_creator_role` four, and `invalid_patch` four. One successful native import's project citation returned `lock_timeout`; its export was skipped. Final route totals and comparisons will follow completion.

The large CSL array completed 24,352 elements: 24,250 applied, six conflict, and 96 invalid; re-import applied zero and kept those six conflicts and 96 invalid outcomes. Four invalid outcomes expose a bound-source fill inconsistency: the shared CSL validator accepts `metadata.source`, but binding attempts to fill it through a patch path absent from the editable registry. `tests/fixtures/real-trial/minimized/csl-bound-source-fill.json` reduces this to two entries with one DOI and a later `source` field. This is recorded for owner triage; the closing batch adds no type or product admission rule. The census above now includes every unsupported primary Zotero type, rather than only parents with children: 147 items across 13 types, of which seven have children. `test_zotero_type_census_includes_parents_without_children` pins that distinction.

The shared batch driver is deferred to the export-registry pass: `run_csl` is the third copy of the import batch loop. Verification at this checkpoint is 713 passing tests, clean Ruff and ty checks, 121 passing demo checks, and zero isolated real-trial failures. The owner-copy catalog hash remains `d4c75afdcb436136d15bc855e3ebb399731bbadf56479f0993864c09373f26d5`.

### Slowest completed files so far

These wall-time estimates use the saved first command opening and last command closing for each completed file, excluding abandoned deadline attempts. They omit checkpoint setup and any Pandoc work after the final CLI close. The final `typeset.bib` log was removed with its successful working home before capture; its value is an upper bound from its first import to gate completion and includes final verification. Direct monotonic per-file timers are now in both harnesses, with a fault-and-resume test proving a saved file retains its own duration and an interrupted retry records only its successful attempt. The final report will retain these measurement limits.

| Rank | File | Route | Wall time |
| --- | --- | --- | ---: |
| 1 | Really Big whopping library.csl.json | CSL batch | 6,261.57 s |
| 2 | Async import, large library #720.bib | BibTeX | 1,675.36 s |
| 3 | tugboat.bib | BibTeX | 1,651.34 s |
| 4 | Unabbreviate on import #1436-3.bib | BibTeX | 1,506.58 s |
| 5 | stanford-cstr.bib | BibTeX | 759.68 s |
| 6 | font.bib | BibTeX | 342.37 s |
| 7 | typeset.bib | BibTeX | ≤305.68 s |
| 8 | texbook3.bib | BibTeX | 206.48 s |
| 9 | texbook2.bib | BibTeX | 186.64 s |
| 10 | Maintain the JabRef group and subgroup structure when importing a BibTeX db #97.bib | BibTeX | 139.49 s |

### Retained artifacts and the next-run boundary

| Directory | Contents | Deletion status |
| --- | --- | --- |
| `/Volumes/Casa/tmp/refs-corpus3.UJF8YT` | Original full manifest, bounded manifests, original round-three results, and diagnostic JSON results; all gate-home subdirectories are empty. | Retain the full manifest and original comparison results until the replacement rerun is recorded, or archive them before deletion. |
| `/Volumes/Casa/tmp/refs-corpus3-fixes.sUA4yE` | Completed fixed-code separate-home BibTeX results (`batch-a-result.json`, `batch-b-result.json`, `batch-large-result.json`, `beebe-result.json`), unused CSL slices and manifests; gate-home subdirectories are empty. | Free to delete if the report's recorded comparison figures suffice; retain or archive the result JSON files if per-file audit evidence is wanted. No checkpoint depends on this directory. |
| `/Volumes/Casa/tmp/refs-corpus3-close.T7ELYa` | Complete pooled BibTeX result at `bib-resume-result.json`, also cached under `bib-retry/bib-corpus-progress.json`; JSON saved results at `json/corpus-progress.json` and its retained home at `json/corpus`. Failed-attempt outputs and manifests are alongside them. | Retain the machine results for the report. The JSON home is disposable and will not be resumed; archive the progress file before deleting it if the partial per-file evidence is wanted. |

Inspection of the JSON progress file confirms 377 completed results and `active_index: null`, so file 378 is the next unprocessed file; the earlier description of 378 saved files was an off-by-one status count. Nothing was deleted. The saved product-and-harness digest will be invalid after the performance merge, so this checkpoint is historical evidence rather than the starting point for the next gate.

The review session owns merging `perf-batch` (`9b66700`), fixing the parallel driver to create each shard work directory and read `wall_seconds`, and proving it with a live small-manifest run. Only after that proof will item 7 rerun the whole round-three manifest on the merged code. Until then no gate runs and the four existing corpus harness scripts are frozen after this commit. Opening a retained catalog on the merged code will automatically upgrade it to schema 6 and write `before-schema-6-<date>.sqlite` beside the catalog; the measured 27k-source-copy upgrade took approximately one second. That is context for the later rerun, not an action in this closing checkpoint.
