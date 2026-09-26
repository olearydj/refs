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

## 2026-09-25 — full rerun on the merged performance code

Both gates completed from fresh sample clones on `db99931`, carrying the performance batch and the live-proven parallel driver. Work and results are under `/Volumes/Casa/tmp/refs-corpus3-perf.cjs40te2`: `bib-report.json`, `json-report.json`, each gate's `shard-N/report.json` and `stderr.txt`, unchanged-file-list manifests, the per-file comparison JSON files, and `type-census.json`. The 120 BibTeX files came from `refs-corpus3-close.T7ELYa/bib-manifest.json`; the 425 JSON files came from the original `refs-corpus3.UJF8YT/json-all.json`. Only the ceilings changed: 100,000,000,000 temporary bytes and 86,400 seconds. Each gate used the driver's default 14 workers; BibTeX finished before JSON started. Nothing resumed, no shard failed, no serial fallback was used, and no harness change was needed.

### Counts, repeated imports, export and recovery

| Gate or route | Files | Entries | Applied | Unchanged | Conflict | Invalid | Created | Already present |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BibTeX | 120 | 33,635 | 29,426 | 45 | 897 | 3,267 | 0 | 0 |
| JSON, all applicable routes | 425 | 26,819 | 26,288 | 4 | 23 | 417 | 87 | 0 |
| Native Zotero | 400 | 2,354 | 2,036 | 4 | 17 | 297 | 0 | 0 |
| CSL arrays | 24 | 24,465 | 24,252 | 0 | 6 | 120 | 87 | 0 |
| Inapplicable result object | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

The native Zotero bundles all reached per-item processing; there were no whole-file or wrapper-conversion refusals. CSL's 24,352-element array used batch import, and the 23 smaller arrays kept the per-record add path. Repeat BibTeX imports applied zero, with 29,471 unchanged, 897 conflict, and 3,267 invalid. Repeat JSON operations applied or created zero, with 26,292 unchanged, 87 already present, 23 conflict, and 417 invalid. Each gate's counts sum to its entry count, and every manifest file appears exactly once in its merged report.

| Entry refusal code | BibTeX | JSON |
| --- | ---: | ---: |
| `invalid_bib_entry` | 3,267 | 0 |
| `value_conflict` | 887 | 23 |
| `alias_conflict` | 10 | 0 |
| `invalid_zotero_item` | 0 | 51 |
| `unknown_zotero_type` | 0 | 147 |
| `key_author_required` | 0 | 175 |
| `invalid_record` | 0 | 38 |
| `unknown_creator_role` | 0 | 4 |
| `invalid_patch` | 0 | 2 |

BibTeX produced 72 rendered exports, 17 blocked exports, 26 empty selections, and five project-citation refusals (`import_origin_ambiguous`). Its export blocking findings were `invalid_identifier` 873, `case_colliding_key` 26, `invalid_export_value` two, and `accessed_unassessed` one. JSON produced 360 rendered exports, 16 blocked exports, 48 empty selections, and one inapplicable file, with no project-citation refusal. Its blocking findings were `unassessed_mapping` 3,436, `given_only_name` two, `unassessed_extension` three, `issued_date_lost_or_changed` seven, `accessed_unassessed` one, and `invalid_identifier` one. Every rendered export returned zero with no Pandoc stderr.

All 28 shards passed resource verification and backup/restore, comparing all 21 schema-6 tables with matching rows. Each checked all 556 available managed resources; these are the same sample resources repeated across independent clones, not 15,568 unique files. BibTeX also retained named linked-file findings in its shard reports; all JSON shard checks contained only the 556 available managed resources. The dated `before-schema-6-<date>.sqlite` safety copy in a working clone is an expected first-open upgrade artifact. Successful gates removed their working homes, retaining reports and progress records. The supplied sample catalog's SHA-256 remained `d4c75afdcb436136d15bc855e3ebb399731bbadf56479f0993864c09373f26d5`.

### Every changed first-pass outcome against the pre-performance record

The comparison uses all 120 rows of `refs-corpus3-close.T7ELYa/bib-resume-result.json` and all 377 saved rows of `refs-corpus3-close.T7ELYa/json/corpus-progress.json`. There are 25 changed BibTeX files and 28 changed comparable JSON files; every changed count distribution is listed below, with omitted statuses meaning zero. The other 95 BibTeX and 349 comparable JSON distributions, including their entry refusal-code counts, are unchanged. The remaining 48 JSON files have no completed pre-performance result. `bib-outcome-changes.json` and `json-outcome-changes.json` retain each changed file's absolute path and both outcome and refusal-code distributions.

The pre-performance gates used one pooled catalog per route; the parallel gates give each round-robin shard an independent sample clone. Earlier files in other shards therefore cannot provide a binding candidate or citation-key history. This changes applied, unchanged and conflict outcomes and limits what the comparison can attribute to the performance code alone. Every BibTeX file retains its exact invalid count. In JSON, the large CSL array has two fewer `invalid_patch` outcomes; all other comparable files retain their invalid counts. That history-sensitive fill defect remains present with two refusals, and its minimized fixture remains the input for owner triage. No type is added or proposed as admitted here.

| BibTeX file | Pre-performance outcome | Merged-code outcome |
| --- | --- | --- |
| dissertation/references.bib | 70 applied; 9 unchanged; 213 conflict | 76 applied; 4 unchanged; 212 conflict |
| zotero-bbt-export.bib | 111 applied; 93 unchanged; 358 conflict | 194 applied; 11 unchanged; 357 conflict |
| Unabbreviate on import #1436-2.bib | 753 applied; 99 unchanged; 98 conflict; 103 invalid | 950 applied; 103 invalid |
| Async import, large library #720.bib | 8,888 applied; 63 conflict; 14 invalid | 8,906 applied; 45 conflict; 14 invalid |
| Better BibTeX.009.bib | 1 applied; 1 conflict; 1 invalid | 2 applied; 1 invalid |
| DOIs excluded from export in 6.7.86 #2555.bib | 1 unchanged | 1 applied |
| Detect journal abbreviation in the publication field #1951.bib | 1 conflict | 1 applied |
| Import support for the online type in BBT #1358.roundtrip.bib | 1 conflict | 1 applied |
| Jabref groups import does not work #717.3.8.bib | 1 applied; 3 conflict | 4 applied |
| Jabref import - groups lost #1730-5.bib | 4 unchanged | 4 applied |
| LaTeX commands in Zotero should be exported untouched #1380.roundtrip.bib | 1 unchanged | 1 applied |
| Maintain the JabRef group and subgroup structure when importing a BibTeX db #97.bib | 464 applied; 3 conflict; 444 invalid | 466 applied; 1 conflict; 444 invalid |
| Problem when importing BibTeX entries with percent sign #95 or preamble #96.bib | 1 conflict | 1 applied |
| Unabbreviate on import #1436-3.bib | 6,016 applied; 65 unchanged; 593 conflict; 492 invalid | 6,429 applied; 17 unchanged; 228 conflict; 492 invalid |
| importing a title-cased bib #1246.roundtrip.bib | 1 conflict; 1 invalid | 1 applied; 1 invalid |
| litprog.bib | 231 applied; 1 unchanged; 79 invalid | 232 applied; 79 invalid |
| printing-history.bib | 250 applied; 5 conflict; 410 invalid | 255 applied; 410 invalid |
| stanford-cstr.bib | 1,657 applied; 6 conflict; 82 invalid | 1,662 applied; 1 conflict; 82 invalid |
| texbook1.bib | 245 applied; 6 unchanged; 7 conflict; 128 invalid | 258 applied; 128 invalid |
| texbook2.bib | 366 applied; 8 unchanged; 2 conflict; 155 invalid | 376 applied; 155 invalid |
| texbook3.bib | 476 applied; 64 unchanged; 79 conflict; 249 invalid | 617 applied; 2 conflict; 249 invalid |
| texgraph.bib | 88 applied; 17 unchanged; 4 conflict; 64 invalid | 109 applied; 64 invalid |
| tugboat.bib | 5,070 applied; 1 unchanged; 20 conflict; 105 invalid | 5,091 applied; 105 invalid |
| type.bib | 25 applied; 2 conflict; 5 invalid | 27 applied; 5 invalid |
| typeset.bib | 490 applied; 188 unchanged; 101 conflict; 135 invalid | 777 applied; 2 conflict; 135 invalid |

| JSON file | Pre-performance outcome | Merged-code outcome |
| --- | --- | --- |
| BBT does not escape # in first argument of href in note #2617.json | 1 applied; 1 unchanged | 2 applied |
| Better BibLaTeX.009.json | 1 applied; 1 unchanged | 2 applied |
| Better BibLaTeX.019.json | 1 conflict | 1 applied |
| Better BibLaTeX.022.json | 1 conflict | 1 applied |
| Better BibLaTeX.stable-keys.json | 6 conflict | 1 applied; 5 conflict |
| Better BibTeX.018.json | 1 conflict | 1 applied |
| BetterBibLaTeX sets option useprefixtrue with no way to turn off #3281-2.json | 1 unchanged | 1 applied |
| BibTeX export is incompatible with Zotero 6 Preprint item type. #2080.json | 1 conflict | 1 applied |
| CSL exporters; ignore [Fields to omit from export] setting #1179.json | 12 applied; 14 conflict | 26 applied |
| Choose fields to exclude for each exported file #1827.json | 1 conflict | 1 applied |
| Collected notes.json | 17 applied; 16 unchanged; 1 conflict; 2 invalid | 34 applied; 2 invalid |
| Deterministic ordering for CSL #1178 #1400.csl.json | 26 already_present | 26 created |
| Duplicate note is not correctly commented out in biblatex output #3040.json | 1 unchanged | 1 applied |
| Edition Numbers in BibTeX Exports #1446.roundtrip.json | 1 unchanged | 1 applied |
| Export of Contributor to WITH #2837.json | 1 unchanged | 1 applied |
| Language field in the metadata exported incorrectly #1921.json | 46 applied; 2 unchanged; 38 invalid | 48 applied; 38 invalid |
| Normalizing English language tag #3100.json | 2 applied; 1 conflict | 3 applied |
| POST to pull-export #3258.json | 22 unchanged; 29 conflict | 51 applied |
| Page, issue and volume range sign in CSL JSON is hyphen instead of en dash #3327.json | 1 conflict | 1 applied |
| Postscript error aborts CSL JSON export #1155.csl.json | 4 already_present | 4 created |
| Postscript error aborts CSL JSON export #1155.json | 2 applied; 1 unchanged; 1 conflict | 4 applied |
| Really Big whopping library.csl.json | 24,250 applied; 6 conflict; 96 invalid | 24,252 applied; 6 conflict; 94 invalid |
| Spaces not stripped from citation keys #294.json | 1 unchanged | 1 applied |
| Underscores break capital-preservation #300.json | 1 conflict | 1 applied |
| auto-export.json | 3 unchanged | 3 applied |
| cayw.json | 1 applied; 1 conflict; 1 invalid | 2 applied; 1 invalid |
| condense in cite key format not working #308.json | 1 unchanged | 1 applied |
| formula grouping.json | 1 unchanged | 1 applied |

The 377 matched JSON files change from 26,125 applied, 57 unchanged, 77 conflict, 413 invalid, 56 created and 30 already present to 26,235 applied, four unchanged, 22 conflict, 411 invalid and 86 created. The entire BibTeX gate changes from 28,187 applied, 570 unchanged, 1,611 conflict and 3,267 invalid to the counts above. The earlier JSON `lock_timeout` citation refusal did not recur.

### Wall times and ten slowest files per gate

Driver wall time includes gate setup, shard processes, resource checks, backup/restore and report merging. The serial-equivalent column sums each completed file's measured `wall_seconds`; it excludes shard setup and final verification, and reflects file timings measured under concurrent load rather than a separate serial benchmark. The merged `peak_temporary_bytes` is not meaningful: it sums volume-wide readings that include the other shards' allocations. Disk measurement was left unchanged; it is not used here as an aggregate peak estimate.

| Gate | Workers | Driver wall time | Slowest shard wall time | Sum of per-file wall times | Per-file sum / driver wall |
| --- | ---: | ---: | ---: | ---: | ---: |
| bib | 14 | 183.32 s | 182.49 s | 585.09 s | 3.19× |
| json | 14 | 157.26 s | 156.98 s | 575.53 s | 3.66× |

Together, the sequentially launched gates took 340.58 seconds (5.68 minutes) of driver wall time. The BibTeX pre-performance gate's 9,180.03 seconds (153 minutes, including its deadline and retry) became 183.32 seconds, about a 50-fold elapsed-time reduction combining the code changes, parallel execution, different binding histories and earlier retry overhead. The large CSL file's earlier reconstructed 6,261.57 seconds became a directly measured 117.16 seconds, about 53 times shorter; its earlier timing excluded checkpoint setup and final Pandoc work as described above. The 24-hour ceilings did not end either gate.

| Bib rank | File | Measured wall time |
| --- | --- | ---: |
| 1 | Async import, large library #720.bib | 156.35 s |
| 2 | Unabbreviate on import #1436-3.bib | 107.29 s |
| 3 | tugboat.bib | 56.77 s |
| 4 | stanford-cstr.bib | 25.39 s |
| 5 | Unabbreviate on import #1436-2.bib | 21.57 s |
| 6 | zotero-bbt-export.bib | 14.40 s |
| 7 | Maintain the JabRef group and subgroup structure when importing a BibTeX db #97.bib | 13.88 s |
| 8 | Some bibtex entries quietly discarded on import from bib file #873.bib | 12.37 s |
| 9 | font.bib | 11.48 s |
| 10 | Unabbreviate on import #1436-1.bib | 10.85 s |

| Json rank | File | Measured wall time |
| --- | --- | ---: |
| 1 | Really Big whopping library.csl.json | 117.16 s |
| 2 | Bulk performance test.json | 16.70 s |
| 3 | Export as Collected Notes does not list subcollections #1768.json | 2.53 s |
| 4 | POST to pull-export #3258.json | 2.16 s |
| 5 | CSL exporters; ignore [Fields to omit from export] setting #1179.json | 2.09 s |
| 6 | Compare export times.json | 1.81 s |
| 7 | Capitalize all title-fields for language en #383.json | 1.67 s |
| 8 | (non-)dropping particle handling #313.json | 1.64 s |
| 9 | Capitalisation in techreport titles #160.json | 1.60 s |
| 10 | Language field in the metadata exported incorrectly #1921.json | 1.54 s |

### Unsupported-type census for owner proposals

The source census is independent of which validation error is reported first. It finds 520 unsupported BibTeX entries, 15 unsupported CSL entries, and 147 unsupported Zotero primary items (13 types, seven items with children). The same unsupported vocabulary and counts remain; no new type is admitted. These cumulative round-three counts are the input for the owner's later proposals.

| Route | Unsupported type | Count | One example entry |
| --- | --- | ---: | --- |
| bib | `audio` | 10 | Import error with character '+' in BibTeX field name #2660.bib: 10.13:91a |
| bib | `booklet` | 32 | font.bib: Anonymous:1986:MCF |
| bib | `collection` | 7 | BBT does not import groups from JabRef 5.1 #1641.bib: Hornborg2012 |
| bib | `constitution` | 6 | Import error with character '+' in BibTeX field name #2660.bib: 11.9:23 |
| bib | `dataset` | 6 | Import error with character '+' in BibTeX field name #2660.bib: 10.9:75a |
| bib | `film` | 1 | web_page and other mendeley idiocy.bib: `<empty key>` |
| bib | `generic` | 24 | web_page and other mendeley idiocy.bib: Callahan2011 |
| bib | `hardware` | 2 | Import error with character '+' in BibTeX field name #2660.bib: 10.10:78a |
| bib | `image` | 11 | Import error with character '+' in BibTeX field name #2660.bib: 10.14:97a |
| bib | `inreference` | 3 | Better BibLaTeX import improvements #549.bib: Algar1985 |
| bib | `jurisdiction` | 8 | Import error with character '+' in BibTeX field name #2660.bib: 11.4:1 |
| bib | `legadminmaterial` | 3 | Import error with character '+' in BibTeX field name #2660.bib: 11.7:19 |
| bib | `legal` | 1 | Import error with character '+' in BibTeX field name #2660.bib: 11.10:29 |
| bib | `legislation` | 8 | Import error with character '+' in BibTeX field name #2660.bib: 11.5:8 |
| bib | `legmaterial` | 4 | Import error with character '+' in BibTeX field name #2660.bib: 11.6:14 |
| bib | `movie` | 2 | Improve import of films #1837.bib: Marka.S:2011movie |
| bib | `nameonly` | 28 | Import error with character '+' in BibTeX field name #2660.bib: 9.44:1a |
| bib | `periodical` | 177 | Import error with character '+' in BibTeX field name #2660.bib: 10.1:12a |
| bib | `presentation` | 4 | Import error with character '+' in BibTeX field name #2660.bib: 10.5:60 |
| bib | `proceedings` | 159 | Some bibtex entries quietly discarded on import from bib file #873.bib: Etzioni:SWAgents |
| bib | `reference` | 1 | Import error with character '+' in BibTeX field name #2660.bib: 10.2:33c |
| bib | `softwareversion` | 1 | import software related biblatex entries #1544.bib: delebecque:hal-02090402v1 |
| bib | `talk` | 1 | Import Jabref fileDirectory, unexpected reference type #1058.bib: Afonso2011 |
| bib | `video` | 20 | Film references do not export properly for APA formating #2494.bib: formanOneFlewCuckoo1975 |
| bib | `webpage` | 1 | accessDate must be ISO date #2376.bib: r42 |
| csl | `broadcast` | 3 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.csl.json: friends:leia:tv |
| csl | `dataset` | 1 | Setting the item type via the cheater syntax #587.csl.json: noauthor_object_nodate |
| csl | `entry-encyclopedia` | 2 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.csl.json: Blair2004 |
| csl | `legal_case` | 1 | Better CSL JSON does not include authority field #2019.csl.json: WhiteState1966 |
| csl | `motion_picture` | 2 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.csl.json: Doe2015 |
| csl | `musical_score` | 1 | Setting the item type via the cheater syntax #587.csl.json: mozart_sonatas_1960 |
| csl | `pamphlet` | 1 | Setting the item type via the cheater syntax #587.csl.json: clark_mesopotamia_1957 |
| csl | `performance` | 1 | Does setting a type via cheater syntax work currently #2473.csl.json: nachwilliamshakespeareHamlet2001 |
| csl | `review-book` | 2 | Setting the item type via the cheater syntax #587.csl.json: kamp_deconstructing_2006 |
| csl | `video` | 1 | Extra field type video not exported #3536.csl.json: marreEdge1992 |
| zotero | `artwork` | 1 | Does setting a type via cheater syntax work currently #2473.json: Hamlet nach William Shakespeare |
| zotero | `bill` | 1 | Customise name-separator and list-separator #1927.json: of Rights |
| zotero | `case` | 5 | @jurisdiction; map court,authority to institution #326.json: Dalain |
| zotero | `dataset` | 3 | Add support for new Zotero item types #2496.json: MY DGS – annotated. Public Corpus of German Sign Language |
| zotero | `encyclopediaArticle` | 85 | Better BibTeX does not export collections #901.json: Abduction |
| zotero | `film` | 3 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.json: A film |
| zotero | `forumPost` | 2 | add date, origdate functions, and format-date filter #1488.json: Forum post with full date and time |
| zotero | `letter` | 13 | Bulk performance test.json: Brev fra Byplannævnet, Hovedstadsafdelingen, til Byudviklingsudvalget for Københavnsegnen |
| zotero | `map` | 21 | Bulk performance test.json: Helhedsplan permanent vand |
| zotero | `podcast` | 1 | raw bibtex fields with colon in extra #2750.json: ‘Unfinished business’: Ring CEO Liz Hamren leads Amazon’s home monitoring products into the AI era |
| zotero | `statute` | 3 | @legislation; map code,container-title to journaltitle #327.json: Loi n<sup>o</sup> 2011-525 du 17 mai 2011 de simplification et d'amélioration de la qualité du droit |
| zotero | `tvBroadcast` | 6 | Export of creator-type fields from embedded CSL variables #365 uppercase DOI #825.json: The one with the Princess Leia fantasy |
| zotero | `videoRecording` | 3 | Bulk performance test.json: Bruno Latour & Antoine Hennion: L’Ange de l’œuvre. Étienne Souriau, from Aesthetics to an Ontology of Uncertain Beings |

Verification after the completed gates: 721 tests passed in the full locked suite. The report accounting checks confirmed one result per manifest file, 60,454 total entries, no created or applied outcomes on repetition, and row-matching restore results in every shard. This closes rerun item 7; the existing bound-source fill defect, unsupported-type proposals, named export limits and deferred shared batch driver remain with the owner. No harness change was required.
