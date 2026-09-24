# Code review appendix: the three readers' reports, 2026-09-24

Raw output of the three independent readings behind the [code review investigation](2026-09-24-code-review-investigation.md), kept as evidence and as the line-level work list for a later fix pass. Not governing text. Each reader worked from the same lens (docs/right-sizing.md "Design lens", "Rules, not patches", and the archived ArjanCodes review) plus the server-direction lens. Paths are under `src/refs/` unless stated; line numbers are at commit 473df8f. Two claims were spot-checked by the reviewing session and hold: the broad exception catch around Zotero writes, and the unread registry projection columns (whose values are prose, so they could not drive code as they stand).

---

## Reader 1: domain cluster (models, naming, sources, importing, bibliography, languages, projects, collections, search)

**Error and connection helpers.** `RefError(code, message, exit_code=3, *, path, details, retryable, data)` at results.py:11. `catalog.connect(catalog, write=False)` at catalog.py:19 is a context manager that opens SQLite, sets `row_factory=sqlite3.Row`, upgrades the schema, runs `BEGIN IMMEDIATE` (write) or `BEGIN` (read) and commits on normal exit. `catalog.changed(connection)` at catalog.py:56 bumps `catalog_meta.revision`. Every cluster module except models, naming and languages calls `connect()` and writes SQL itself. There is no storage layer.

**Recorded intent the code departs from.** plan.md:21 says "Domain functions use refs-owned values/errors, independent of Typer and SQLite row types". plan.md:23 says the search boundary "takes literal query/filter/limit/offset and returns source IDs, revisions, matching fields". right-sizing.md:29 lists "domain logic separate from Typer and SQLite" as a seam. right-sizing.md:73 says "Mappings live in the registry table the exporter reads, not in branches of its code". No doc records the departures below as deliberate.

### 1. Findings

| # | Sev | Principle | Concrete issue | Simpler alternative | Evidence | Recorded departure? |
|---|---|---|---|---|---|---|
| F1 | blocking (latent) | App-owned errors at the boundary; short transactions | `importing.apply_zotero` (309-312) catches `ValueError, TypeError, KeyError, AttributeError` around the whole body, including `sources.insert_source` (306) and `bind_and_fill` → `store_record` writes. Any programming error after a write is relabelled `invalid_zotero_item`. `connect()` still commits on normal exit (catalog.py:50-51), so a partly written source is kept while the entry is recorded as invalid. | Catch only around `zotero.parse` + `SourceCreate.model_validate`. Let the rest propagate so `connect` rolls back. | apply_entry (191) catches only `RefError`/`ValidationError`, so the two paths behave differently. | No |
| F2 | major | Registry-driven mappings (right-sizing.md:73) | The exporter hard-codes most mappings in branches: thesis degree strings (bibliography.py:91), container-title target by kind (179-188), the source→target list (227), note labels (264, 268), identifier targets (273), publisher target by entry type (238-245), number/genre by kind (247-263). Registry rows carry `portable_projection` and `export_class`, which no code reads. `REGISTRY['preserved_only']` is also unread by the exporter. The importers (adapters/bibtex.py:181, adapters/zotero.py:148) do read `rows`. | Drive projection from `REGISTRY['rows']` the way the importers drive ingestion. Keep code only for value-dependent assessments. | Two sources of truth; drift is silent. | No; the doc states the opposite rule. |
| F3 | major | Consumer-shaped interfaces; domain independent of SQLite | No storage layer. `execute()` counts: sources 19, importing 40, projects 17, bibliography 11, search 4, collections 3. Domain functions take an untyped `connection` and write SQL inline. | One `store.py` owning the SQL for sources/originals/imports/projects; domain code passes and receives dicts or models. | A backend change touches six domain modules. | Partly: plan.md:21 claims independence from row types, honoured via `dict(row)`, but not from SQL. |
| F4 | major | Interfaces shaped by the consumer (plan.md:23) | The search boundary is `search_sqlite.matches(connection, query)` only. Filters, limit and offset run in Python after `search.retrieve` loads every active source through `sources.record` (search.py:25), plus two queries per record for collection and project filters (30, 32). `record()` runs 5-6 queries plus a possible BibTeX parse (sources.py:41-42). | Push loc/project/collection filters and paging into the boundary; resolve full records only for the returned page. | Every `search`/`list` reads the whole catalog. | Contradicts plan.md:23 |
| F5 | major | Module boundaries follow responsibilities; no cycles | `sources` ↔ `importing` cycle broken by function-local imports (sources.py:92). `sources.record` imports `bibtex.preserved_fields` and `resources.inventory` locally (40, 46). `models` imports `naming` locally (357). `importing` imports `search.identifier` locally three times (54, 76, 99). | Move identity/binding (`match`, `bind_and_fill`, `isbn_plan`, `differences`, `preserve`, `bindings`, identifier normalization) into one module both entry points depend on. Put `identifier()` next to `normalize_doi` in models. | Import direction runs importing→search for identifier normalization, which is backwards. | No |
| F6 | major | One definition of "editable record" | "Record → editable canonical dict" written 5 times: sources.py:209-211, importing.py:111-112, 144, 520-521, bibliography.py:73. "Pop citation_key, validate, re-attach" written 5 times: sources.py:219-234, importing.py:141-143, 166-169, 287-291, 530-535. Deep copy via `json.loads(json.dumps())` 6 times. | `editable(record) -> dict` and `revalidate(canonical) -> dict` in models or sources. | Each copy handles `loc`/`citation_key` slightly differently (sources.py:210 pops a None loc; importing.py:111 does not). | No |
| F7 | major | Rule over a kind of value | `patch_path` allows `metadata.<field>` only for the 49 `REGISTRY['core_fields']` (sources.py:177). The model accepts about 47 more CSL fields (models.py:187-234), so `update --set metadata.original-title=...` is rejected as "Unknown metadata path". Date-member paths do use `Metadata.model_fields` (172-173). | One whitelist: `Metadata.model_fields` aliases. | Two field lists in one function. | No |
| F8 | major | App-owned transaction semantics | Optimistic checks rely on SQLite's database-wide write lock. `store_record` runs `UPDATE ... WHERE id=? AND revision=?` without checking `rowcount` (sources.py:160). Key allocation is SELECT-then-INSERT (sources.py:116-118, importing.py:301-303). `projects.create` is SELECT-then-INSERT (projects.py:22-30). None translate `sqlite3.IntegrityError`. | Check `rowcount == 1` and raise `stale_revision`. Translate unique violations to `key_conflict`/`project_conflict` in the storage function. | Safe under `BEGIN IMMEDIATE` today. On a server at READ COMMITTED, writes would be silently lost or raw driver errors escape. | No |
| F9 | minor | Interface consistency | Policy is passed three ways: `sources.add/update(policy=dict)`, `importing.run/add(settings=Settings)` then `settings.values if settings else None` (importing.py:165, 288, 300, 304), and `search.retrieve(policy=)`. | Pass the `policy` dict to naming everywhere; pass `Settings` only where resources need file roots. | Three conventions for one value | No |
| F10 | minor | Consumer-shaped interface | `bibliography.serialize` receives hidden underscore keys (`_projection_notices`, `_howpublished`) that `export()` merges into the records (426; read at 99, 308, 327). | Explicit `preserved: dict[key, ...]` argument. | serialize's real inputs are invisible in its signature | No |
| F11 | minor | Consumer-shaped interface | `run_zotero` builds dummy `SourceCreate` objects titled 'ISBN group candidate' to feed `isbn_plan` (importing.py:329-330). The ISBN comes from raw Zotero data, not the adapter's mapped value. | `isbn_plan(connection, isbns: list[str])`. | The bib path (231-236) parses properly, so the two routes can count differently. | No |
| F12 | minor | Flags vs separate operations | `change_identity` is two operations (rekey, set state) selected by which keyword is non-None (sources.py:243-274). It uses f-string column SQL (269) and a special case for `state=='active'` (246). | `rekey()` and `set_state()`. | The CLI calls it three ways (cli.py:211, 218, 225) | No |
| F13 | minor | App-owned result type | `Result`/`Issue` models (models.py:456-470) exist only for `schema` output. `results.emit` builds the envelope separately (results.py:34-36). `SourceRecord` (435-453) is never validated against `sources.record()` output, which is `SELECT *`-shaped (sources.py:19-23). | Validate record output in tests against `SourceRecord`, or generate one from the other. | Schema and reality can drift silently | No |
| F14 | minor | Error set that matches reality | `BLOCKING_CODES` (bibliography.py:47) is redundant with the `class=='blocking'` test in `enforce_losses` (52). Three of its codes are never emitted. | Drop the set; class decides. | Tested only with synthetic losses (tests/contract/test_export.py:30-33) | No |
| F15 | minor | Rule over a kind | Conflict-vs-invalid classification is two hand-kept tuples that differ: importing.py:194 has `likely_match` (never raised); importing.py:312 has `alias_conflict`. | Use `exc.exit_code == 2` → invalid, else conflict. | Divergent lists for one rule | No |
| F16 | minor | Performance | `sources.record` does 6+ queries and may parse BibTeX on every call. `insert_source`/`store_record` call it twice (sources.py:143/145, 162/164). `list_batches` → `inspect_batch` calls `sources.record` for every entry of every batch (importing.py:452, 474). | Cache inside the call, or read the columns needed | 562-entry Zotero batch | No |
| F17 | minor | Configuration vs code | `GLOBAL_TERMS` (naming.py:17) holds the owner's vocabulary ('nbgrader', 'GPT-4') as a code constant. | Put it in the default config. | Already overridable via `policy.titles.protected_terms` (77) | No |

### 2. Rules versus patches

| Location | Branch or magic value | Rule it should be |
|---|---|---|
| bibliography.py:370-371 | `'R' in terms and '{R}' not in raw` → `title_protection_added` | Any protected term unbraced in the original gets the notice. |
| bibliography.py:91 | Degree strings `'phd','phd thesis','doctoral thesis','dissertation','masters',"master's thesis",'msc','ma'` | A registry table genre → portable thesis type, shared with its inverse at adapters/bibtex.py:263-264. |
| bibliography.py:102 | `limitation['reason'].startswith('Preserved from import:')`, matching prose built at sources.py:45 | Limitations carry a `kind` code; match on the code, never on message text. |
| bibliography.py:102, 104 | Skip `field=='language'`; skip `field=='year'` when issued is literal | "A limitation is superseded when its canonical path has its own assessment"; sources.py:33-37 already has a different mechanism (corrected_fields). |
| sources.py:41; adapters/bibtex.py:70; bibliography.py:353 | `'howpublished'` hard-coded in three places | Registry `preserved_only` list for bib, as the Zotero side has. |
| bibliography.py:113, 250; models.py:341 | `str(metadata.get('archive','')).casefold()=='arxiv'` repeated | The validator already moves arXiv identity into `extensions.identifiers.arxiv`; the exporter should read only that. |
| bibliography.py:160 | `entry_type in ('book','collection')` | 'collection' is not a portable type; dead member. |
| bibliography.py:96-97 | `kind in ('webpage','post-weblog')` Pandoc note | Registry per-type fallback message |
| bibliography.py:330 | Protect `number` in note only for patent/standard | Identifiers placed in notes are always case-protected. |
| bibliography.py:117 | Two values for one slot → `work_identity_changed` (e.g. `issue` and `collection-number` both target `number`, 227) | A distinct `slot_conflict` code. |
| importing.py:35 vs 107/122 vs search.py:41 | DOI-only equivalence in `differences`, DOI+ISBN in `bind_and_fill`, five identifiers in search | "Identifier fields compare by `identifier(field, value)`", applied in all three. |
| search.py:47 | arXiv normalized, OCLC compared raw | Every identifier scheme has one normalizer. |
| importing.py:119 | Skip `native_type.*` when types are equal | Native label differences are provenance; state it as a registry or path rule. |
| importing.py:329 | `itemType=='book'` on raw Zotero data | Use the adapter-mapped canonical type. |
| importing.py:425 | `removeprefix('http://zotero.org/')` in importing | Belongs in the Zotero adapter's relation parser. |
| sources.py:237 | `- {'loc'}` from corrected fields | A declared set of non-bibliographic (filing) paths |
| sources.py:246 | `state != 'active'` needs a revision | Acceptable as a rule; name it. |
| sources.py:190 | Sentinel `'__validate_path__'` | Validate the path against the model's field tree directly. |
| models.py:417 | Hand-listed patchable top-level paths | `SourceCreate.model_fields - {schema_version, citation_key}` |
| models.py:137 vs 113 | `type` Literal duplicates `REGISTRY core_fields.type.enum` | Keep one. |
| naming.py:112, 129, 157; search.py:70; resources.py:281 | Sentinel string `'ND'` for "no year", also the policy default | `issued_year() -> int \| None`; apply `missing_year` only when formatting. |

Already rules: `naming.normalize` protects any all-caps word of two or more letters (naming.py:75); `' and '` inside a publisher or family name is braced (bibliography.py:147, 235); the chapter exception to the title requirement (models.py:131); the ISBN one-to-one binding rule (importing.py:75-83).

### 3. SQLite leakage

| Kind | Location |
|---|---|
| `json_extract` | sources.py:108; importing.py:178; projects.py:71-72 (in a JOIN condition) |
| `INSERT OR IGNORE` | importing.py:21, 148, 422, 428; bibliography.py:473 |
| `ON CONFLICT ... DO UPDATE ... excluded` | projects.py:85; bibliography.py:459, 476 |
| `rowid` | importing.py:450, 473 |
| `instr(lower(CAST(raw_bytes AS TEXT)), ...)` on a BLOB | sources.py:41 |
| FTS5 `MATCH`/`rank` via direct adapter import | search.py:6, 24 → adapters/search_sqlite.py:31; sources.py:12, 143, 162, 272 |
| Positional `INSERT ... VALUES` with no column list | sources.py:142; projects.py:30, 43, 85; importing.py:148, 422, 428; bibliography.py:459, 476 |
| f-string column names in SQL | sources.py:269; importing.py:249, 360, 549 |
| `SELECT *` rows as API output | sources.py:19-23; projects.py:12-15, 22-26, 53; collections.py:19; importing.py:444 |
| sqlite3 types in domain code | bibliography.py:4, 485 |
| Row objects used past the query | importing.py:444-467, 543-544; bibliography.py:377-403, 468-469; `.rowcount` at bibliography.py:410 |
| JSON-in-TEXT decoded in domain code | sources.py:23-28, 34; importing.py:58, 68, 117, 451, 456, 546; projects.py (via json_extract) |
| Transaction control in domain code | importing.run: N+3 transactions (225, 237, 243, 253); run_zotero: N+4 (331, 334, 344, 351, 364); bibliography.export: 4-5 (420, 439, 455, 463, 407); sources/projects/search/collections: one per call |
| Reliance on SQLite write serialization | sources.py:116-118, 160; importing.py:301-303; projects.py:22-30 |
| ISO timestamps compared as TEXT | projects.py:73 |
| Full scans in Python where a DB would index | importing.py:57-60 (`isbn_plan`), 67-70 (`match`, O(N·M) per import); search.py:25 |

### 4. Dead or unreachable code

| Item | Status |
|---|---|
| `naming.edition_display` (naming.py:147) | Never called in src; tests only. Dead. |
| `sources.doi_identity` (sources.py:65) | Pure alias of `models.normalize_doi`. Redundant. |
| `sources._add` split from `add` (78-85) | Only caller is `add`. Harmless. |
| `SourceRecord`, `OriginalReference`, `Issue`, `Result` (models.py:426-470) | Used only by `schema()`. |
| bibliography.py:160 `'collection'` | Unreachable value |
| search.py:24 `query and query.strip()` | Redundant after line 20 |
| sources.py:99 pre-check | Subsumed by the unconditional `preserve()` at 103; sha256 computed three times. |
| Project and collection `revision` columns | Incremented (projects.py:44, 86, 98; importing.py:393) but never checked. |

Parameters always passed the same value: `bibliography.export(profile=...)` has one legal value (418); `change_identity(revision=None)` only arrives with `state='active'`; bibliography.py:447 calls `apply_entry` without `settings`.

Error codes:

| Code | Where | Reachable? | Tests? |
|---|---|---|---|
| cited_authors_changed, in_text_citation_changed, protected_spelling_changed | bibliography.py:47 | Unreachable; never emitted by `serialize`. | Synthetic only (test_export.py:30) |
| integrity_error | bibliography.py:483 | Unreachable outward; rewrapped at 485 as `export_published_unrecorded`. | No |
| import_conflict (default) | importing.py:267 | Unreachable; every conflict/invalid entry sets `code`. | Name only in a test name |
| likely_match as RefError | importing.py:194 | Unreachable; only ever a warning. | Warning form only |
| revision_required | sources.py:247 | Unreachable via CLI. | No |
| invalid_export_value | bibliography.py:24 | Never escapes; converted to a loss at 336. | No |
| invalid_key "blank" | sources.py:256 | Only for the empty string. | No |
| source_missing | sources.py:21 | Uncertain; `resolve` raises first. | No |
| source_ambiguous / project_ambiguous | sources.py:55; projects.py:14 | Near-unreachable (needs a key equal to another row's UUID). | No |
| export_intent_conflict, outside_edit | bibliography.py:446, 458, 472 | Race-only | outside_edit yes |
| collection_ambiguous | collections.py:12 | Reachable | Yes |
| unknown_schema, unsupported_profile, invalid_status, invalid_query (sort) | models.py:476; bibliography.py:418; importing.py:448; search.py:15 | Reachable | No |
| invalid_record, invalid_loc, invalid_project, stale_revision, source_removed, identity_conflict, export_blocked, work_identity_changed, issued_date_lost_or_changed | various | Reachable | Yes |
| citation_key_required, key_author_required, key_conflict, invalid_patch (6 sites), invalid_selection, ambiguous_selection, import_missing, import_origin_missing/ambiguous, invalid_bib_entry/input, invalid_zotero_item, project_conflict, project_missing, target_binding_conflict, unadopted_target, adoption_requires_import/overwrite, unsupported_record, case_colliding_key, invalid_identifier, value_conflict, export_published_unrecorded | various | Reachable | Not asserted by name |

### 5. Long or deeply nested functions

| Function | Lines | Depth | Earned? |
|---|---|---|---|
| bibliography.serialize (57-338) | 282 | 8 | No. Four closures and a hand-written mapping table. Split by concern (names, dates, publisher, identifiers, extensions) and drive from the registry. |
| bibliography.export (416-488) | 73 | 6 | Partly. Three `target_state` calls and two INSERT forms could become a `record_intent()` helper. |
| bibliography.preserved_bib_fields (342-374) | 33 | 5 | No. Three unrelated notice rules in one loop. |
| importing.reconcile (484-551) | 68 | 5 | No. Select and propose/apply phases are separable. |
| importing.run_zotero (320-374) | 55 | 4 | No. Six phases; the relation fix-up duplicates `associate`. |
| importing.bind_and_fill (95-149) | 55 | 3 | Partly. Compatibility and fill/conflict classification could be a pure function over two dicts. |
| importing.apply_entry (152-203) | 52 | 4 | Partly. Parallels apply_zotero; a shared normalize → validate → bind → insert step would shorten both. |
| search.retrieve (12-55) | 44 | 5 | No. Exact-identifier matching (35-49) should be a pure `exact_matches(record, query)`. |
| sources.update (201-240) | 40 | 5 | Borderline. Title-protection pruning (222-229) is its own rule. |

Also dense: naming.normalize (64-94) has lines 77 and 88 over 200 characters. sources.record (18-49) mixes storage and limitation policy.

### 6. Duplication

| Logic | Locations |
|---|---|
| Citation-key allocation loop | sources.py:113-119 ↔ importing.py:299-304 (only the first validates via `valid_key`) |
| "Supplied" key_provenance dict | sources.py:112 ↔ importing.py:182 ↔ importing.py:298 |
| likely_match title query with json_extract | sources.py:107-111 ↔ importing.py:178-180 |
| Editable-canonical extraction and revalidation | see F6 |
| Protected-term regex `(?<!\w)term(?!\w)` | naming.py:43 ↔ bibliography.py:35 |
| Date-parts → ISO string | bibliography.py:201 ↔ 211 ↔ 287 |
| arXiv archive test | models.py:341 ↔ bibliography.py:113 ↔ 250 |
| Identifier field lists | search.py:41 ↔ bibliography.py:273 ↔ importing.py:103/107/122 |
| Zotero relation → origin_identities lookup | importing.py:366-370 ↔ 425-428 |
| Import counter UPDATE (f-string) | importing.py:249 ↔ 360 ↔ 549 |
| run / run_zotero skeleton | importing.py:220-255 ↔ 320-374 |
| apply_entry / apply_zotero pipeline | importing.py:152-203 ↔ 281-317 |
| Status vocabularies | importing.py:223, 326, 447, 467 and 186, 199, 201, 315, 353 |
| Warning-dict literal (same shape as `Issue`) | naming.py:80, 83, 89; sources.py:111, 261; importing.py:180, 437; helper only at bibliography.py:43 |
| ValidationError → RefError issues | models.py:401-402 ↔ sources.py:206 ↔ 233 |
| Exactly-one-row resolve | sources.py:52 ↔ projects.py:11 ↔ collections.py:9 |
| `SELECT revision FROM catalog_meta` | collections.py:20 ↔ search.py:54 ↔ bibliography.py:427 |
| Project revision bump + `changed` | projects.py:43-45 ↔ 85-87 ↔ 97-99 |
| Pinned-data load and hash check | models.py:46-50 ↔ languages.py:8-12; naming.py:13 loads creator-latin-v1.json with no hash check |
| Filename fallback condition | naming.py:157 ↔ resources.py:281 |
| `loc is None → pop` | sources.py:24-25 ↔ 210-211 |
| Schema name list | models.py:474-476 ↔ cli.py:246 |

### 7. Best-designed pieces

1. Identifier normalization at the validator every route passes through (models.py:28-39, 101-133, 324-351): small pure functions; `collapse_identifier_aliases` moves arXiv identity into `extensions.identifiers.arxiv` once for all routes; the registry is hash-checked at import.
2. naming.py as a pure module with a pinned table and recorded provenance (naming.py:20-38, 115-144); languages.py follows the same pattern.
3. Digest-guarded, recoverable export (bibliography.py:376-413, 462-488): `target_state` returns `(current, recoverable, known)`; an interrupted publish finishes on re-run.

Honourable mentions: `RefError` plus `models.parse` translating `ValidationError` into `invalid_record` (models.py:397-402); `importing.inspect_batch`'s review token (importing.py:464-465); per-entry import transactions preserving every original (importing.py:200-202).

---

## Reader 2: storage and files cluster (catalog, files, moves, resources, recovery, config, migrations)

**Headline.** No blocking finding. No traced path deletes or overwrites a file the contract says must survive. Every unlink site checks, by device and inode or by identity plus digest, that the file is refs' own. Publication uses `os.link`, which never overwrites. Six majors: operations that can never finish and block `reorg`; a re-run of a completed intake that moves a file back; reorg ignoring files shared by several resources; the old→new report lost on non-RefError aborts; the documented copy-retry remedy broken by fix (c); the schema version hard-coded in about 12 places.

### 1. Findings

| # | Sev | Principle | Concrete issue | Simpler alternative | Evidence | Deliberate? |
|---|---|---|---|---|---|---|
| F1 | major | Liveness of destructive ops | `source_revision`, `resource_revision` and `loc` are captured once in `create` (moves.py:89) and never refreshed. If the move fails or is interrupted before `recorded` and the owner then edits the source, `record_destination` raises `stale_revision` (102-104) on every retry, forever. Likewise after `resource unlink` on a resource with an open operation (`unlink`, resources.py:159-168, does not check `file_operations`; retries then fail with `resource_missing` at 101 or `move_conflict` at 162). `reorg --execute` resumes pending operations first and aborts on the first error (276-279), so one stuck row blocks all unfiltered reorgs. Nothing is lost. | When a pre-`recorded` operation fails its revision check, re-plan it: discard the staged copy (proven ours by inode) and restart from `staged` with fresh revisions. Or let `unlink` refuse while an operation is open. | tests/integration/test_moves.py:119-130 asserts the first failure only. | No. Contract L48 says "a retry repeats that state's checks"; plan defers recover commands. |
| F2 | major | Unintended placement | A re-run of a completed `--move` intake whose original is gone takes the resume branch (moves.py:210-212) and reuses the old destination as `target`. `move()` then sees the latest operation for the resource; if a later `reorg` moved the file, that operation's `new_path` differs (188), so `move()` creates a new operation moving the file from `lib/<loc>` back to `lib/unfiled/...`, unpreviewed. | Resume only when that operation is unfinished. When it is `removed` and the path is gone, return the current resource without calling `move`. | test_move_intake.py:100 covers only an immediate re-run. | No; contradicts contract L7. |
| F3 | major | A rule applied on one route only | `admit` (moves.py:197-203) runs only for intake. `reorg` moves a file that several resources record. The first move deletes the original; the other resource dangles; its own move raises `unsafe_move_source` (77-78), aborting every later `reorg`. Bytes survive under lib. | In `selection`, group by resolved path or `samefile`, and refuse or report shared originals before planning. | `UNIQUE(source_id, locator)` (001:97) allows the same path under different sources. The owner's data has none today. | No. |
| F4 | major | The contract's reporting promise | `reorg` catches only `RefError` (moves.py:285). `resume` catches `OSError` and `RefError`, not `sqlite3.Error` (173). OSErrors from `create` (staging mkdir or touch, 83, 87), SQLite busy errors from plain writers, and KeyboardInterrupt escape and lose the accumulated old→new list (contract L65). | Wrap the loop in `try/finally` and emit `result['moves']` on any exception, or catch `BaseException`, attach the report and re-raise. | The 551-file reorg is exactly where Ctrl-C happens. | No. |
| F5 | major | Contract conformance; patch placed where found | Fix (c), duplicate detection (resources.py:289-299), runs only for `resource add --copy` without a resource id. The contract's remedy for a partial `add --file --copy` is "retry resource add --copy" (L28; message at resources.py:333). That retry now always returns `duplicate_attachment`, so the link can never become a managed copy. It also makes the origin-match branch (239) and `resource_conflict` (240-241) unreachable. The rule doesn't cover move intake or `add --file --copy`. | Exclude the resource whose locator equals `origin` from the duplicate scan. Apply duplicate detection as a rule for every copy or move intake route. | tests/integration/test_copy.py:97-100 asserts the duplicate result for exactly this retry. | Fix (c) is recorded; its conflict with the remedy is not. |
| F6 | major | Single source of truth | The schema version is spread over about 12 places: catalog.py:40, 124, 126, 152, 154-155, 157-161, 162, 178; recovery.py:26, 29-36 (an if-chain replaying each file), 43. Four copies of the `catalog_meta` rebuild (002-005:1-9), forced by `CHECK (schema_version = N)`. Adding migration 006 without editing recovery.py:26-36 makes `validate_database` reject the catalog, so `backup` breaks. | One ordered `MIGRATIONS` list with `CURRENT = len(...)+1`, used by `connect`, `upgrade_connection`, `ensure_schema` and `validate_database`. Relax the CHECK, or a single `UPDATE catalog_meta SET schema_version=?`. | The FD-leak defect in slice 3 was in this path. | The plain runner is deliberate; the duplication is not. |
| F7 | major | Performance and cloud side effects | In `resources.check`, `check_item(settings, item, verify)` runs for every resource before the `--source` filter (132-137). `resource check --source X --verify` hashes the whole catalog. | Build `known` from `resolve_path` only; call `check_item` after the filter. | By reading. | No. |
| F8 | minor | Safety TOCTOU | Plain writers (`resource unlink`, `update`) don't take the file lock, so between `pointer_matches` (moves.py:161) and `original.unlink()` (168) the pointer can change. Worst case: a destination left unrecorded; no bytes lost. | Accept and document, or take the lock in `resources.unlink`. | Contract L36 overstates. | Partly. |
| F9 | minor | Wrong vocabulary | The copy path reuses the export primitive `files.publish` (86-93) and `current_digest` (26-33). A destination that appears after planning reports `outside_edit`, "Destination changed before publication", instead of `destination_exists`. | Call `os.link` directly in `verified_copy` and map `FileExistsError` to `destination_exists`. | — | No. |
| F10 | minor | Misreport | In `copy`, `published=True` (resources.py:253) stays set if `register_copy` succeeds but the cleanup unlink raises; result is `copy_published_unregistered` although registered. | Set a `registered` flag. | — | No. |
| F11 | minor | Consistency | Move staging dir created with default mode (moves.py:83) and the stage file by `touch` before the row exists (87); copy path creates staging 0o700 (files.py:116). | Share one `staging_dir()` helper. | — | No. |
| F12 | minor | Path identity written 6+ ways | NFC plus casefold at moves.py:258, resources.py:135/142/147/153 and `preserved_target` (moves.py:23,26,250); NFC only at 297,307; exact string at 188,190,210; `resolve` plus `samefile` at 202. `intake` uses `absolute()`, not `resolve()` (208). | One `path_key(p)` (resolve, NFC, casefold). | — | No. |
| F13 | minor | Consumer-shaped interface | "Find one resource" loads the full inventory: moves.py:62, 68, 99; resources.py:161; O(n·m) at 146. `admit` stats every resource file inside a read transaction (199-203) and fails every intake if any resource has an unconfigured root. | `resource(connection, id)` with `WHERE id=?`. In `admit`, skip unresolvable roots. | — | No. |
| F14 | minor | Fewer layers | `config.policies` (126-201) is 76 lines with 8 levels of hand validation while Pydantic is a dependency. | A Pydantic model for the config tables. | — | No. |
| F15 | minor | Not earned | `toml_text` (config.py:15-28) is a recursive TOML writer used once, for a fixed shape; emits `null` for None, invalid TOML. | An f-string template. | — | No. |
| F16 | minor | Rule vs patch | `plan_copy` restates `naming.filename`'s fallback condition (resources.py:281 vs naming.py:157). | `naming.filename` returns `(name, fell_back)`. | — | No. |
| F17 | minor | Rule vs patch | `if label and target.exists()` (resources.py:287-288) orders checks by a flag. | An occupied destination is refused regardless of label. | 89b08c7; test_label_filename.py:14-15. | No. |
| F18 | minor | Cohesion / cycle | resources.py mixes linking, health check, open, BibTeX file expressions, Zotero attachments, copy and orchestration of `add --file`; imports `moves` lazily (310,315,320) while `moves` imports `resources`. Intake dispatch duplicated in cli.py:283-288 and resources.py:318-325. | Move `capture_file` into moves.py or a small intake module; `zotero_attachment` next to the Zotero import. | — | No. |
| F19 | minor | Dead in production | `catalog.migrate` (136-142) used only by tests; bypasses the lock and the safety copy. | Delete it; tests go through `connect()`. | — | Docstring says "explicit offline upgrade", but no command exists. |
| F20 | minor | Guard not enforced | `resume` needs the caller to hold the file lock (moves.py:113); only convention enforces it. | `assert` the key is in `files._held_locks`, or take `file_lock` inside `resume`. | — | No. |
| F21 | minor | Performance | `unlinked_paths` walks the parent of every planned original, even in dry run (270, 298-308). A resource linked directly in `~` walks the home directory. | Limit to resource roots, or skip for dry runs. | — | No. |
| F22 | minor | Error mapping by message text | `"readonly" in str(exc)` (catalog.py:37) and `"locked" in str(exc)` (cli.py:349). | Use `exc.sqlite_errorcode`, mapped inside `connect`. | — | No. |
| F23 | minor | Density | Lines of 250-420 characters (moves.py:89, 220; resources.py:258, 333; recovery.py:106). | Wrap them. | — | No. |

### 2. Contract conformance

Move protocol (contract L34-65): every step conforms, including: row written before copying with no filesystem work in a write transaction (insert at 90-91; the empty stage is touched before the row at 87, a harmless orphan); identity as device, inode, size and mtime (files.py:103-105); staged with exclusive stage, checks, flush, saved identity and digest (86-87, 124, 139-142); published by hard link without overwrite, digest verified, staging name kept until commit (146-151, unlink at 158); retry after publication proven by staging identity, not equal bytes (120-122); recorded in one transaction rechecking source revision, resource revision and loc (98-109; also checks `state=='active'`, not required but not forbidden); pre-delete checks limited to destination identity and digest, original identity and digest, and pointer, then flush and unlink (161-170; no revision or loc recheck, correct; pinned by test_later_source_edit_does_not_block_delete); failed flush prevents deletion; interrupted-while-staged recopy and destination-change conflict (129-134; 188-191); retry after unlink (161-170); unfinished operations first even when loc emptied (244-249, 276-281; with `--loc P`, an operation whose source loc moved outside P is not resumed, arguable); NFC basenames and `-b`/`-c` suffixes (183, 20-27, 253; the intake dry-run preview shows the pre-NFC name at 220); admission before linking and not on resume (215, 224; missing on reorg, F3); report of old beside new plus unlinked files (178-179, 291-309; intake hard-codes `unlinked_paths=[]` at 220, 228; lost on non-RefError aborts, F4); "the file lock serializes refs writers" is partial (F8).

Copy protocol (contract L15-32): conforms throughout, with: `staging_volume_mismatch` checked three times (files.py:113-118; resources.py:277); library-folder write permission not pre-checked, surfacing later as `copy_failed`; collision reported with the export vocabulary (F9); "retry resource add --copy" converts the link: does not conform (F5); no fsync of the temporary file before publication, allowed by contract.

### 3. Rules versus patches

Rules written once: the collision suffix; NFC for moved basenames (moves.py:183); sync-conflict filename recognition (resources.py:100); the BibTeX file-expression rule (resources.py:196-199); new catalogs replay the same migration files (catalog.py:104-107); snapshot validation derives the expected schema from those files (recovery.py:23-40); identity-proven ownership before any unlink (files.py:82, 141; moves.py:127, 158).

Rules duplicated with drift: path equality (F12); the misplacement test (moves.py:258 and resources.py:142); the filename fallback (F16); the schema version (F6).

Patches: fix (c) scoped to one route (F5); `if label and ...` ordering (F17); error mapping by message substring (catalog.py:37, cli.py:349); migration 005 rewriting both JSON spacing forms of one literal (005:11-15), acceptable for a one-time migration but showing the locator is stored twice; `results.emit` branching on specific codes and data keys (results.py:40-51).

### 4. SQLite leakage, transactions and lock structure

Leakage: `connect` sets `row_factory=Row` (catalog.py:29); `inventory` relies on it via `dict(row)` (resources.py:23), so recovery sets it by hand (recovery.py:68, 103); rows used with `row['x']` throughout moves.py and resources.py; `sqlite3.Connection` objects passed across modules as parameters (`inventory`, `link_in`, `import_links`, `zotero_attachment`, `touch_source`, `sources.record`, `checked_record`, `resolve`). SQL in non-storage modules: moves.py:52, 91, 106-107, 109, 186, 210, 242, 244, 296; resources.py:20, 68, 74, 79, 84, 128-129, 164, 166, 219-220, 226-227, 363, 365-366; recovery.py:25, 37-39, 42. Driver exceptions caught in domain code: resources.py:256, bibliography.py:485, cli.py:348-349. SQLite-only SQL: FTS5 (001:70), `json_valid` CHECKs, triggers with `RAISE(ABORT)`, `CHECK(schema_version = N)`; 002-005 `ALTER TABLE ... RENAME` plus positional `INSERT ... SELECT`; recovery uses `sqlite_master`, `PRAGMA table_info`, `integrity_check`, `foreign_key_check`, `:memory:` replay, URI `mode=ro`. PRAGMAs and transaction control outside `connect`: catalog.py:101-108, 140-142, 163-177 (ensure_schema issues its own `BEGIN IMMEDIATE` and runs migrations through `executescript('BEGIN IMMEDIATE; ... COMMIT;')` at 130); recovery.py:20-45, 67, 102. Five things tied to the catalog being a directory: the database file (catalog.py:21), the ready marker (24), `files.lock` (files.py:46; catalog.py:117), `staging/` (files.py:113, moves.py:81; same-volume rule at resources.py:277), the `before-schema-*` copies (catalog.py:162). Config has no DSN concept (config.py:48-51). Loose but portable: ISO text timestamps for ordering; `ORDER BY created_at DESC LIMIT 1` without a tiebreak (moves.py:186, 210); identities as JSON text.

Connections, locks and filesystem work:

| Function | Connections | File lock | Filesystem work under lock or transaction |
|---|---|---|---|
| `catalog.connect` | 1; write uses `BEGIN IMMEDIATE`, read a deferred `BEGIN` | via `ensure_schema` only | — |
| `catalog.ensure_schema` | 3 extra | yes (156) | Write transaction held while creating, backing up and fsyncing the safety copy (164-175), deliberate; a small window between `rollback` (175) and the migration's `BEGIN IMMEDIATE` (130) where a plain writer can slip in. |
| `catalog.init`, `catalog.migrate` | direct `sqlite3.connect` | no | — |
| `moves.move` | read, then via `create`, `resume`, `save` | yes (184), across the whole copy, both hashes, link and unlink | By design; other file-effect commands time out after 5 s during a large move. |
| `moves.reorg` | selection read outside the lock | per operation | Plan computed unlocked; `create` rechecks. |
| `moves.create`, `save`, `record_destination`, `pointer_matches` | short | caller's | None inside write transactions. |
| `moves.intake` | show, update and link as separate write transactions | only inside `move` | `admit` stats every resource inside a read transaction (199-203). |
| `moves.selection`, `unlinked_paths` | read | no | Walk after the connection closes. |
| `resources.copy` | `sources.update` write outside the lock; `register_copy` write | yes (250), across `verified_copy` and registration | `register_copy` transaction opens inside the `verified_copy` context, after the FS work. |
| `resources.link`, `unlink`, `check`, `inspect_source`, `open_source` | read or write | no | `link_in` calls `resolve()` inside its write transaction (77). |
| `import_links`, `zotero_attachment` | the caller's import write transaction | no | `resolve()` and `is_file()` per attachment inside the import write transaction (205, 361, 368). |
| `recovery.backup` | `connect`, snapshot read, 3-4 validation connections | yes (92), across mkdtemp, snapshot, hashing, validation and publication | Deliberate. |
| `files.file_lock` | — | re-entrant through a `ContextVar` keyed by `catalog.resolve()` (36-61) | — |

### 5. Dead or unreachable code, and error codes

Dead: `catalog.migrate` (136-142); recovery.py:42-44 repeats the check at 25-27; resources.py:239-241 unreachable with current callers (F5); resources.py:361 `settings`-None branch reachable only without settings; `moves.checkpoint` is an intentional test seam.

Codes raised in the cluster that no test names: moves: `move_incomplete`, `move_conflict`, `source_changed`, `staging_changed`, `destination_changed`, `integrity_error`, `resource_missing`, `unsafe_move_source`, `resource_already_recorded` (only `details.resource_id` checked), `staging_volume_mismatch`; copy: `copy_failed`, `copy_published_unregistered` (exit code only), `unsafe_copy_source`, `resource_conflict`; lock: `lock_timeout` (no test touches `file_lock`); backup and recovery: `backup_exists`, `backup_incomplete`, `configuration_changed`, `snapshot_invalid`, `recovery_required`; other: `invalid_config`, `invalid_kind`, `invalid_locator`, `root_unavailable`, `unsafe_target`, `open_failed`, `resource_unavailable`, `unsupported_attachment`, `invalid_attachment_path`. Asserted: `destination_exists` (3), `stale_revision` (3), `outside_edit` (3), `unsupported_schema` (3), `unsupported_file_expression` (3), `source_removed` (2), `schema_upgraded` (2), `catalog_missing`, `home_not_writable`, `init_conflict`, `invalid_invocation`, `invalid_loc`, `library_unavailable`, `unsafe_path`, `file_action_incomplete`, `attachment_base_missing`, `duplicate_attachment`, `filename_unavailable` (1 each).

### 6. Long or deeply nested functions

| Function | Lines | Depth | Earned? |
|---|---|---|---|
| `config.policies` (126) | 76 | 8 | No; a Pydantic model would replace most of it. |
| `moves.resume` (113) | 63 | 4 | Mostly; the state machine reads top to bottom. The row construction and recopy block (129-142) could be extracted. |
| `catalog.init` (60) | 60 | 2 | Partly; the `reuse_config` block and the mount check could be helpers. |
| `recovery.backup` (84) | 41 | 3 | Yes; a linear protocol. |
| `resources.import_links` (191) | 18 | 5 | Fine. |

Near the threshold: `catalog.connect` (36), `ensure_schema` (34, depth 4), `resources.check` (34), `moves.selection` (34), `resources.capture_file` (28, very dense).

### 7. Duplication

1. Copy-and-verify: files.py:119-133 and moves.py:135-141 (deliberate at contract level, not in code). 2. Staging setup, symlink and volume checks: files.py:113-118, moves.py:81-85, resources.py:277-278. 3. The re-record `UPDATE resources SET locator,...,revision+1`: resources.py:219-220 and moves.py:106-107. 4. `INSERT INTO resources`, three variants: resources.py:84, 226-227, 365-366; `zotero_attachment` (363-367) repeats `link_in` (79-85). 5. Locator encoding `json.dumps(sort_keys=True)`: resources.py:78, 213, 362; moves.py:107. 6. Find-by-id through a full inventory: moves.py:62, 68, 99; resources.py:161, 146. 7. Unfinished-operations query: moves.py:244 and resources.py:129, 296. 8. Defaulting loc to `unfiled`: moves.py:222-223, resources.py:244-245, 283. 9. Intake-mode dispatch: cli.py:283-288 and resources.py:318-325. 10. Misplacement test: moves.py:258 and resources.py:142. 11. "Unlink only if the inode is ours", three variants: files.py:82 (inode only), 141, moves.py:158. 12. Schema version and migration list (F6); `catalog_meta` rebuild in 002-005. 13. Ad hoc `sqlite3.connect` plus `row_factory`: catalog.py:100, 140, 163, 168; recovery.py:20, 23, 67, 102.

### 8. Best-designed pieces

1. The move state machine and journal (moves.py:113-175, migrations/004): each committed state records what is proven; publication proven by inode; deletion guarded by file facts only; no filesystem work in SQL transactions; the `checkpoint` seam lets tests kill at each boundary; about 60 lines carry the contract.
2. `RefError` and the result envelope (results.py:11-21).
3. `files.verified_copy`, `files.staged` and `files.file_lock` (files.py:39-142): small context managers only where there is lifecycle; exclusive creation and no-overwrite publication; cleanup removes only the invocation's own inode; the re-entrant lock removed the nested-lock deadlock.

Runner-up: `ensure_schema` (catalog.py:145-178).

---

## Reader 3: interface and adapters (cli, render, display, results, __main__, adapters, tools)

Commands run: `refs --help` and each subcommand's `--help`, plus invocations that fail during argument parsing and never open a catalog. One stderr capture was left at `/tmp/x_ignore_not_allowed` (harmless).

### 1. Findings

| # | Sev | Principle | Concrete issue | Simpler alternative | Evidence | Deliberate? |
|---|---|---|---|---|---|---|
| F1 | major | Application-owned errors; exit mapping in one place | `main()` maps every `OSError` to `storage_error` exit 5 and every `PermissionError` to `home_not_writable` (cli.py:348-354). The CLI reads user input files itself, so bad input comes out as an I/O failure: `add --input missing.json` (86), `import --input` missing or a directory (120), `update --patch missing.json` (191; handler at 200 catches only ValueError/UnicodeError). Contract gives exit 2 for invalid input. Lock detection is a substring match on "locked" (349). | One `read_payload(arg)` helper (handles `-`) raising `RefError('invalid_input', …, 2, path=…)`. Keep main's OSError branch for catalog storage only. Detect locks with `exc.sqlite_errorcode in (SQLITE_BUSY, SQLITE_LOCKED)`. | test_config.py:85 is the only test with expected=5; none covers exit 6. | No |
| F2 | major | One JSON object on stdout with the command named | (a) Every failure caught in `main()` is emitted with `command="invocation"` (342, 346, 353), even domain errors from `show`, `export`. (b) With `standalone_mode=False`, `no_args_is_help=True` groups print help and then an envelope with an empty message: `refs --json project` puts help plus `{"…","message": ""}` on stdout, exit 2. (c) Any exception outside RefError, TyperException, OSError, sqlite3.Error and KeyboardInterrupt gives a raw traceback (e.g. KeyError inside a service, or `typer.Abort`). | Record the command path in ctx.obj and use it in `main`. Catch `Exception` last as `internal_error`, exit 5. Handle the no-args case explicitly. | Verified with the commands listed. test_results.py:8-12 covers only an unknown command. | No |
| F3 | major | The CLI only parses, dispatches and reports | `add` dispatches on format to two services (88-91); sets loc in a second transaction after creation (92-96), so a crash between leaves the source without loc and an existing source with a different loc silently keeps the old one; decides `moving=not link and not copy` (99); validates loc itself (81-85) though the model (models.py:312) and search.py:16-19 also do. `resource add` repeats intake dispatch and path assembly (281-288) that `resources.capture_file` also performs (319-325). `export` resolves config defaults (162-167). `execute=execute and not dry_run` is copied four times (211, 218, 225, 296). | One domain entry per command with loc passed into the create transaction, intake mode resolved in one function, export defaults resolved in config. | cli.py:1 docstring says "application services return ordinary values". | No; growth, not design |
| F4 | major | Each adapter owns its format's quirks | Zotero quirks outside adapters/zotero.py: `linkMode` values, the `attachments:` prefix and `storage/<key>` resolution (resources.py:336-366); note HTML stripping, `linked_url` context, stripping `http://zotero.org/` from `dc:relation` (importing.py:398-440); `zotero.CHILDREN` checks (importing.py:339, 348). BibTeX quirks outside adapters/bibtex.py: bibliography.py:340-374 re-parses bib originals with `bibtexparser` directly; sources.py:40-45 does a SQL `instr(..., 'howpublished')` prefilter. | The Zotero adapter returns `attachment_path(item, manifest)`, `context(item)`, `relations(item)`. The bib adapter exposes `original_facts(raw)`. | Adapter docstrings claim ownership. | No |
| F5 | minor | Consumer-shaped interfaces | The CLI makes extra reads to feed the text renderer: `sources.show`/`projects.show` after cite/uncite (150, 259, identical) and `previous_key` before `key set` (210; separate connection, a race). These go only into `text_context`, so JSON never carries `project_name`, `citation_key`, `previous_key`. `add` `file_action` is text-only (100). `export_blocked` gets its `path` only when not `--json` (171-172). | Services return what consumers need; bibliography sets `path` on `export_blocked`. | render.py:111, 115-116 depend on these keys. | No |
| F6 | minor | One place for rendering | `results.emit` holds command- and code-specific human error rendering (39-58) and imports render lazily (41, 44, 62). Success rendering in render.py, error rendering in results.py. Upgrade notices print to stdout in human mode (31-32); contract puts progress on stderr. | `emit` builds the envelope and chooses JSON or `render.human(result)`; render.py owns both. | human-output-notes.md treats warnings and errors as a style class. | Notices-to-stdout undocumented |
| F7 | minor | Exit-code mapping in one place | Exit codes chosen at about 150 raise sites; default 3. `integrity_error` is 3 at moves.py:148 but 5 at bibliography.py:483 and files.py:78. `invalid_arguments` (cli.py:144) is a one-off synonym for `invalid_invocation`. `import_partial` (exit 4) is decided in the CLI from counts (121-122). | Fix moves.py:148 to 5; fold `invalid_arguments`; let `importing.run` raise the partial result. | AST scan. | Per-site choice deliberate; drift not |
| F8 | minor | Rules at the validator | The same fault is classified differently by route: alias conflict is `ValueError` → `invalid_bib_entry` exit 2 → `invalid` in bib (bibtex.py:177-178, 222-223); `RefError('alias_conflict', 3)` → `conflict` in Zotero (zotero.py:82, importing.py:312); `invalid_record` exit 2 in CSL (csl.py:24). Two `assign` path-setters are near-duplicates (bibtex.py:172-179; zotero.py:73-83). The URL pre-check is written twice (bibtex.py:202-204, zotero.py:166-167) and duplicates models.py:127-130; the CSL route refuses the same URL. | One `assign_path` in models raising `alias_conflict` with one classification; one `portable_url(value)` predicate used by all three adapters. | The "rules, not patches" examples are exactly this. | No |
| F9 | minor | Adapters own their format | csl.py:26-27 silently drops any CSL key not in `Metadata` with no limitation; bib and Zotero adapters report "Preserved from import". The CSL alias table is inline (csl.py:21). | Return `dict(source, limitations)`; move the aliases to the registry. | bibtex.py:225-226; zotero.py:171. | No |
| F10 | minor | Type introspection | search_sqlite.py:10 finds name lists with `'Name' in str(field.annotation)`; sources.py:172 uses `get_args`. | Use `get_args` against `Name`. | — | No |
| F11 | minor | Hidden global state | `upgrade_notices` is a module-level ContextVar written by catalog.py:178, drained by `emit` (results.py:27-28), reset in the callback (cli.py:37); tools/assign_initial_loc.py:69-70 reads it directly. | Acceptable for one notice; alternatively return notices from `connect()`. | — | Undocumented; defensible |
| F12 | minor | Envelope shape | `report()` passes `data.get("warnings")` as top-level warnings but leaves them inside `data` (cli.py:42): warnings carried twice. | Pop them from data. | — | No |
| F13 | minor | Typed choices | `--format`, `--sort`, `--kind`, `--status` and `schema NAME` are plain `str`, validated by hand (cli.py:79-80, 117-118; search.py:14, resources.py:123, importing.py:447). Help shows `<str>`. | `Literal`/Enum options. | --help output | No |

### 2. Command surface versus contract

Contract options the CLI lacks: `resource unlink --if-revision` (cli.py:292-296, none); `reactivate --if-revision` optional (222); `--version` absent; `import --input -` fails because the option is a `Path` (108, 116). Choices invisible in help for `list --sort`, `add --format`. CLI options the contract does not name: `project cite --from-import ORIGIN` (140); `--dry-run` on init, key set, remove, reactivate, resource unlink, project create/cite/uncite, backup (redundant on execute-gated commands; `reorg` lacks it); `schema` with no NAME lists schemas (244-246); completion options. Typer artefacts: every bool option gets a `--no-X` twin, including `--no-no-project-config` and `--no-no-library`; completion options on the root; metavars `<str>`, `<path>`; `--config`/`--catalog`/`--project-file` typed `str` not `Path` (32-34). Help text: only `open` has a docstring (318); the `import` group callback doubles as the bib/zotero import command (103-123). The help pass is deliberately deferred; the `--no-no-*` flags are defects.

### 3. Rules versus patches

| Location | Kind | Note |
|---|---|---|
| render.py:21-23 | Patch | Rewrites the domain message for `empty_selection`. |
| render.py:53-54 | Patch | `type_fallback` description chosen by sniffing `'@misc'` in the message. |
| render.py:138 | Patch | `command != 'add'` exemption from the "Unchanged:" prefix. |
| render.py:132-135, 140-141 | Patch-ish | `add` re-renders as `resource add`; `import_conflicts` appended for any command. |
| render.py:29-46 | Rule in the wrong place | Export warning-code descriptions live in the renderer, away from the codes. |
| results.py:40-51 | Mixed | Branches on specific codes; `moves` and pydantic `issues` (52-57) are shape rules. |
| cli.py:171-172 | Patch | `export_blocked` path set only for human output. |
| cli.py:349-350 | Patch | Lock by substring; every PermissionError treated as "home". |
| zotero.py:49-50 | Patch | Unparseable item JSON becomes a fake `itemType: 'invalid_json'` sentinel. Untested. |
| zotero.py:74-77 | Rule, deliberate | DOI/arXiv normalized before the alias-conflict comparison. |
| zotero.py:160-165 | Branch per field name | Date fields enumerated by name and `assignee` special-cased. |
| bibtex.py:186, 189-196, 261-264 | Mostly rules | Thesis → genre mapping is a small mapping in code, not the registry. |
| bibtex.py:74 | Rule | Allowlist of TeX macros. |
| search.py:39, 47 | Mild | Prefix match only without whitespace; arXiv the only scheme normalized. |

### 4. Dead or unreachable code; error codes

Dead or odd: bibtex.py:227 loops over a one-element tuple; bibtex.py:237 and 250 duplicate `MONTHS.get(...) or int(...)`; cli.py:148 assert on the production path; render.py:14 stray blanks; `main()` sits at cli.py:337 with commands after it; search.py:14 limit/offset already enforced by Typer; zotero.py:49-50 sentinel untested.

| Code | Raised at | Test status |
|---|---|---|
| invalid_invocation | cli.py:62, 78, 115, 167, 188, 280, 342 | Code (unknown command only) |
| unsupported_format | cli.py:80, 118 | None |
| invalid_loc | cli.py:85, search.py:19 | Indirect (exit) |
| import_partial | cli.py:122 | Indirect (status, exit 4) |
| invalid_arguments | cli.py:144 | None |
| invalid_patch | cli.py:201 | None |
| home_not_writable | cli.py:351 | Code |
| lock_timeout (exit 6) | cli.py:351 | None end to end |
| storage_error | cli.py:351 | None |
| unpartitionable_input | bibtex.py:58, 64 | Indirect (match) |
| invalid_bib_entry | bibtex.py:272 | Indirect (bare raises) |
| invalid_record | csl.py:33, 35 | Code |
| invalid_zotero_input | zotero.py:70 | None by code |
| alias_conflict | zotero.py:82, 185 | Indirect |
| date_conflict | zotero.py:130 | Indirect |
| unknown_zotero_type | zotero.py:144 | Indirect |
| unknown_creator_role | zotero.py:176 | None |
| invalid_zotero_item | zotero.py:198; importing.py:311 | None |
| invalid_query | search.py:15 | None |
| export_blocked | cli.py:171, results.py:46 | Code |

Test `expected=` exit-code tally: 0×5, 2×11, 3×25, 4×7, 5×1, 6×0.

### 5. Long or deeply nested functions

| Function | Lines | Nesting | Earned? |
|---|---|---|---|
| bibtex.parse (119-272) | ~154 | 6 plus a nested `assign` | Partly. Three separable pieces: surface-assignment guard (135-155), registry field loop (181-224), date assembly (230-260). |
| bibtex.partition (18-65) | 48 | 4 | Mostly; a byte state machine. Extract `block_end`. |
| zotero.parse (139-199) | 61 | 4 | Moderately; Extra parse (179-190) could be `extra_lines`. |
| zotero.read (19-70) | 52 | 4 | Earned as one admission gate. |
| render.render_text (99-142) | 44 | 2, but lines of 200-420 chars | Not earned. |
| render.warning_lines (16-60) | 45 | 3 | Half data; move the table out. |
| results.emit (24-63) | 40 | 3 | Not earned; mixes envelope with error rendering. |
| tools/zotero_extract/extract.py `extract` (14-169) | ~156 | 4 | Earned for a one-time script. |

On the `render_text` lambda table: the dispatch shape is right; the lambdas close over `data`, `key`, `revision` and assume source-shaped data; several are nested conditionals on one line (118 `resource add`, 121 `open`); keys are command names not output classes; four post-processing branches special-case commands (132-141). For the rich pass: a module-level dict of named functions keyed by output class plus a `command → class` map; confirmations as a plain dict of format strings. Must change: renderers return `str` (render.py, display.py; display.py:51 flattens with `' | '`); error rendering must move from results.py:39-58; `emit`'s `print` calls become a console; upgrade notices to stderr. Reusable: `display.authors`, `display.metadata_text`, `naming.issued_year`, `resources.PLACEMENT_KINDS`, `move_text`'s pair data (157-160), the warning grouping in `warning_lines`, `import_text`'s entry walk (69-90), the "Preview:"/"Unchanged:" prefix rule (136-139).

### 6. Duplication

| What | Copies |
|---|---|
| Person-name joining in particle order | display.py:7; search_sqlite.py:12-13; bibliography.py:320 (family-only variant at 140) |
| Month tables | bibtex.py:14; bibliography.py:48; zotero.py:94-95 |
| Dotted-path assign with conflict check | bibtex.py:172-179; zotero.py:73-83 |
| Absolute-HTTP(S) URL test | models.py:128-129; bibtex.py:202; zotero.py:166 |
| Resource display path fallback, different orders | render.py:118, 119, 121, 152; display.py:42 |
| Intake-mode dispatch and mutual exclusion | cli.py:77 vs 279; cli.py:281-288 vs resources.py:319-325 |
| loc validation wrapping | cli.py:81-85; search.py:16-19; models.py:312 |
| `execute and not dry_run` | cli.py:211, 218, 225, 296 |
| Default project from config | cli.py:162, 232, 240 |
| cite/uncite text-context lookups | cli.py:150 and 259 |
| howpublished and original-bib reading | bibtex.py:69-70; sources.py:40-45; bibliography.py:340-374 |
| "Managed folder of a resource" NFC casefold | resources.py:142; moves.py:258; tools/assign_initial_loc.py:22-31 |
| Zotero multipart date | tools/zotero_extract/extract.py:63-66 vs zotero.py:111-113 (defence in depth, undocumented) |
| JSON reporting in tools | tools/assign_initial_loc.py:69-70 prints its own JSON rather than `results.emit` |

### 7. The search boundary

Two functions in adapters/search_sqlite.py: `refresh(connection, record)` (22) and `matches(connection, query)` (29), returning application-owned dicts, query always quoted as a literal phrase (31). Callers import the module directly (search.py:6, sources.py:12). Both take the catalog's SQLite connection; the index is an FTS5 table in migration 001 (70). Exact key and identifier matching and all filtering happen in Python (search.py:25-52). Real as a module seam; a second implementation could not be added without touching callers (two imports, no selection mechanism, a SQLite-connection signature, no rebuild-all entry). Deliberately deferred by right-sizing.

### 8. Best-designed pieces

1. `RefError` + `emit` + `main()` (results.py:11-37, cli.py:337-356).
2. `bibtex.partition` (bibtex.py:18-65): frames blocks on raw bytes; refuses rather than guesses.
3. adapters/search_sqlite.py (36 lines): pure `projection(record)`, idempotent `refresh`, only active records, originals never indexed, FTS query always a literal phrase.

Honourable mentions: `zotero.read` (19-70) as a single admission gate; `zotero.date_range` (86-107).
