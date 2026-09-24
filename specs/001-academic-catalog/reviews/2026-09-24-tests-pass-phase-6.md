# Tests pass phase 6: owner-copy rehearsal

The supplied `/Volumes/Casa/tmp/refs-rehearsal-20260924` was read as a source only. Each part used a fresh APFS copy-on-write home under `/Volumes/Casa/tmp/refs-phase6.2V9Id6`; the harness removed those homes and left the supplied copy and the external corpus checkout in place. The corpus manifest and machine-readable results remain in that work directory. Its refs and Pandoc subprocesses denied reads and writes to the real refs catalog, Box tree, Zotero directory and default config path. No application code or phase 7 work changed.

The three principal parts took 334.31 seconds in total: 4.49 for moves, 13.52 for daily use and 316.30 for the corpus. The largest measured peak of additional physical temporary disk was 408,993,792 bytes, against the manifest's 2,000,000,000-byte ceiling; the final corpus used 18 of 20 permitted files and 3,949 of 5,000 permitted entries, and took 316.30 of 900 permitted seconds. APFS clones have a 4.4 GB logical size but shared blocks; the figures above are free-space deltas. Earlier development passes and targeted diagnostic reruns were separate bounded runs and are not included in the principal-part total.

## Move protocol

The process receiving `SIGKILL` was the Python process invoking `refs.cli.main()` for `reorg --execute`, with a test hook installed in that same process. It was not a worker process. Each case started from a fresh clone, temporarily made one real managed resource linked outside its loc, then resumed with a new `python -m refs` command. The original was gone after resume, the resource pointed at the destination, and the destination SHA-256 matched `622b4f1f082f6bfe2cb4f699f946ab92d91cab4fcbcea08c2a3fc1f97ce22c07` in every case.

| Kill point | Persisted state at kill | State after resume | Digest and locator |
| --- | --- | --- | --- |
| `staged` | staged | removed | Matched |
| `published_uncommitted` | staged | removed | Matched |
| `published` | published | removed | Matched |
| `recorded` | recorded | removed | Matched |
| `unlinked` | recorded | removed | Matched |
| `removed` | removed | removed | Matched |
| Inside copy | staged | removed | Matched |
| Inside record transaction | published | removed | Matched |
| After row creation, before copy | staged | removed | Matched |
| After unlink, before final save | recorded | removed | Matched |

The ten cases had zero move findings. Their peak additional physical disk was 1,130,496 bytes; the working clone was removed after each case.

## Daily use

The first action removed `hart2006tlx`, a cited source with a managed file, from a copied catalog after exporting `zotero-library`. The file SHA-256 remained `1081aa585fee113a2e3af322b05ff2159308ed69bf4102e983e45323d7ed3b64`, and the existing bibliography SHA-256 remained `71cbb5c58db3310c96ea209db52a9e402e3ee6c9498f2f9fcc1aff3828c0c0e1`. The source entered `removed`; `reactivate --execute` restored `active`. `paths`, `show`, `search`, `list`, `project show`, `collection list`, `import list` and `resource check --verify` all exited zero. The snapshot validated. Resource check listed 556 recorded files as available and one unrecorded `.DS_Store`; this is the known OS-file scan polish item. Daily-use peak additional physical disk was 24,702,976 bytes.

## Corpus

The external manifest names five owner bibliography copies, the 562-entry Better BibTeX library export copy and twelve fixtures from the fetched `retorquere/zotero-better-bibtex/test/fixtures/import` checkout. All 18 files partitioned; none was refused whole. Every one of the 3,949 entry spans received a named result. The first import yielded 2,704 applied, 212 unchanged, 711 conflicts and 322 invalid; no entry disappeared. A repeat of every import applied zero: 2,916 unchanged, 711 conflicts and 322 invalid. Conflicts and invalid entries remained explicit rather than being silently accepted on the second pass.

| File | Entries | Applied | Unchanged | Conflict | Invalid | Export or render |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Pipyer paper | 11 | 3 | 7 | 1 | 0 | Project citation refused: `import_origin_ambiguous` |
| Danvas paper | 11 | 11 | 0 | 0 | 0 | Pandoc rendered |
| DEMA paper | 7 | 7 | 0 | 0 | 0 | Pandoc rendered |
| Manufacturing paper | 41 | 29 | 1 | 11 | 0 | Project citation refused: `import_origin_ambiguous` |
| Dissertation | 292 | 70 | 9 | 213 | 0 | Project citation refused: `import_origin_ambiguous` |
| Owner Better BibTeX export | 562 | 111 | 93 | 358 | 0 | Project citation refused: `import_origin_ambiguous` |
| Better BibTeX issue 873 | 988 | 883 | 0 | 11 | 94 | Blocked: one `invalid_identifier` |
| Better BibTeX issue 1436-1 | 506 | 435 | 0 | 1 | 70 | Blocked: two `invalid_identifier` |
| Better BibTeX issue 1436-2 | 1,053 | 753 | 99 | 98 | 103 | Project citation refused: `import_origin_ambiguous` |
| Better BibTeX Mendeley web pages | 465 | 391 | 3 | 18 | 53 | Pandoc rendered |
| Better BibTeX issue 3514 | 6 | 6 | 0 | 0 | 0 | Blocked: one `unassessed_mapping` |
| Better BibTeX issue 1358 | 1 | 1 | 0 | 0 | 0 | Pandoc rendered |
| Better BibTeX issue 2744 | 1 | 0 | 0 | 0 | 1 | Empty selection |
| Better BibTeX issue 94 | 1 | 1 | 0 | 0 | 0 | Pandoc rendered |
| Better BibTeX issue 2752 patent | 1 | 1 | 0 | 0 | 0 | Pandoc rendered |
| Better BibTeX issue 1081 | 1 | 1 | 0 | 0 | 0 | Pandoc rendered |
| Better BibTeX issue 1544 | 1 | 0 | 0 | 0 | 1 | Empty selection |
| Better BibTeX issue 664 | 1 | 1 | 0 | 0 | 0 | Pandoc rendered |

Eight writable exports rendered through Pandoc with exit 0 and no renderer warnings. Three exports correctly wrote no file because of the codes in the table; five could not build a project through `--from-import` because historical origins overlap, and two had no accepted entries and were not rendered. The export blocker details were confirmed in a three-file diagnostic subset: an escaped URL in issue 873, two escaped URLs in issue 1436-1, and a translator with no assessed portable projection in issue 3514.

`resource check --verify` after the corpus reported 556 available managed files, 181 missing linked files with a loc, one missing linked file without a loc, and one unrecorded available `.DS_Store`. The corpus added 182 linked paths: 58 from the dissertation, 123 from the Better BibTeX export and one from issue 873. Those fixture paths do not carry file bytes into the copied home, and the sandbox prevented reads of the real paths. Backup and restore succeeded. The full corpus run compared table counts and reopened a restored catalog with 739 resource-check items; a separate one-file follow-up compared all rows in all 20 tables and reopened the restored catalog with 557 resource-check items.

## Findings and dispositions

| Finding | Evidence | Disposition |
| --- | --- | --- |
| Full month names are rejected as integers | The corpus had 46 nonnumeric month or date refusals, including `month = {August}` from issue 873. | The minimal synthetic case is [month-name.bib](../../../tests/fixtures/real-trial/minimized/month-name.bib). This is an importer gap for ordinary full month names; seasons and concatenated expressions in the same count need separate decisions. |
| A translator blocks portable export | Issue 3514 imported six entries, but `Hauck_2023j` caused `unassessed_mapping` for `translator`. | The minimal synthetic case is [translated-chapter.bib](../../../tests/fixtures/real-trial/minimized/translated-chapter.bib). Add an assessed projection or documented omission before treating this input as portable. |
| TeX-escaped URLs block export | Three imported entries in issues 873 and 1436-1 had `invalid_identifier`; no `.bib` was written. | [unsafe-url.bib](../../../tests/fixtures/real-trial/minimized/unsafe-url.bib) reproduces the block. This is a deliberate refusal to emit unsafe identifier text; correction of the preserved URL is needed before export. |
| Missing publication identity is refused | 186 entries lacked a usable title, URL or traditional book part. | This is the catalog admission rule working on incomplete upstream fixtures; no synthetic fixture is needed to infer a repair. The original entry is retained. |
| Unsupported vocabulary or syntax is refused | 27 unsupported entry types, 22 TeX or math forms, nine malformed creator forms, and six other parser refusals were explicit. | These are current input-contract limits rather than silent losses. Each affected entry remains preserved; extending any one form should start from the upstream entry that requires it. |
| Empty keys have a generic validation error | A sample of the 26 generic profile refusals in the Mendeley fixture had `@article{,` with no citation key. | [empty-key.bib](../../../tests/fixtures/real-trial/minimized/empty-key.bib) reproduces the generic refusal. Admission is correct; the error should name the empty key. The other generic entries were not individually reduced. |
| Source identity or current values disagree | 710 `value_conflict` and one `identity_conflict` appeared against the owner-copy catalog. The most common differing paths were pages (336), title protection (180), titles (114), abstracts (91), and authors (75). | The clone contains Zotero and Pipyer history, while the incoming bibliographies and upstream fixtures were not meant to overwrite it. The one identity conflict safely refused incompatible signals. Review individual entries before any reconciliation; these counts are a limitation of this aggregate exercise, not evidence for bulk overwrite. |
| Historical origins block bulk project citation | Five files returned `import_origin_ambiguous` from `project cite --from-import`. | The contract refuses to guess which origin owns an overlapping source. Cite those sources individually or define an explicit multi-origin selection rule in later work; this rehearsal did not bypass that refusal with direct SQL. |
| Fixture links are not present in the working home | 182 newly linked paths were reported missing after imports. | The corpus deliberately copies bibliography bytes, not the referenced attachments. The missing status is accurate, and the sandbox prevented access to the real paths. A future file-inclusive corpus needs a separate size and privacy decision. |
| OS metadata appears as an unrecorded library file | The copied library's `.DS_Store` appeared in both daily use and the post-corpus check. | This is the already recorded polish item to ignore OS metadata by rule; it did not affect the 556 recorded files. |

The synthetic minimized fixtures were checked in fresh temporary catalogs: `month-name.bib` and `empty-key.bib` imported as invalid, `translated-chapter.bib` imported then blocked export with `unassessed_mapping`, and `unsafe-url.bib` imported then blocked export with `invalid_identifier`. The current phase stops at findings; none of the application behaviors above was changed.
