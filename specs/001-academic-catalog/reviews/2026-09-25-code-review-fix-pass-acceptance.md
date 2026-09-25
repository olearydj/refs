# Code review fix pass acceptance, 2026-09-25

## Status and scope

The four batches implement the [accepted brief](../plan.md#code-review-fix-pass-brief-hold-the-code-as-well-as-it-holds-the-files) against the [investigation](2026-09-24-code-review-investigation.md) and its [reader appendix](2026-09-24-code-review-appendix.md). Batch 1 is merged at `b5badb9`, batch 2 at `2ded4aa`, batch 3 at `4f06ae0`, and batch 4 is the `dead-code` worktree for owner merge. The table below covers every finding in the investigation, including the incidental command-surface notes. “Kept” means the finding remains visible, with a reason; it does not claim the original concern was disproved.

## Investigation dispositions

| Finding | Disposition | Evidence or reason |
| --- | --- | --- |
| Pre-recorded move retries keep stale revisions and loc | Fixed | `33dad55` re-plans from current facts; the trace test edits the source before retry. |
| Completed intake can move a later reorganization backward | Fixed | `c0466d7` returns the current resource without a new operation. |
| Reorg can move an original shared by resources | Fixed | `50a71ce` reports both owners and excludes the shared file. |
| Reorg loses partial path report on OS, SQLite, or interrupt failure | Fixed | `3284d90` carries the accumulated report, including through the CLI interrupt envelope. |
| Zotero import catches programming errors around writes | Kept | A narrower transaction and exception boundary needs its own write-fault test; changing import commit behavior was outside this pass. |
| Duplicate attachment guard covers only one copy route and blocks conversion | Fixed | `352a7f6` applies the rule to all copy/move intake routes and excludes the resource being converted. |
| CLI add loc transaction, intake mode, repeated execute flag, and cite rereads | Fixed | `6aedf8c` puts loc in creation, shares intake resolution, and returns renderer fields. |
| Editable copies, revalidation, and JSON round trips repeated | Fixed | `8ad1391` shares the application-owned helpers. |
| Key allocation duplicated and validated on one route only | Fixed | `065c4c9` shares validated allocation; `f6617b5` translates write collisions. |
| Revision updates ignore row count; unique collisions escape | Fixed | `f6617b5` checks guarded updates and classifies concurrent writer conflicts. |
| Search loads all records before page selection | Fixed | `bbc650c` pages identities and matched fields in the search boundary before record resolution. |
| Domain modules own SQL and a backend would touch many modules | Kept | D2 selected narrow seams and a shrinking SQLite syntax allowlist over a new storage layer; the optional server backend remains a separate design decision. |
| User payload read errors become storage errors | Fixed | `109b6b1` shares the payload reader and emits `invalid_input` with path and exit 2. |
| Failure envelopes lose command; uncaught faults print tracebacks | Fixed | `032d891` records the command and emits `internal_error` at exit 5. |
| SQLite lock detection relies on message text | Fixed | `109b6b1` uses `sqlite_errorcode`. |
| Registry claims export authority for unread prose columns | Fixed | `f8fce1e` marks those columns documentation and narrows the right-sizing claim. |
| Structured registry-driven export projection | Deferred to export pass | D3 requires a separate brief and corpus acceptance for a structured `portable_projection`; exporter output is unchanged here. |
| Renderer rewrites one domain error and sniffs `@misc` prose | Kept | The planned human-output pass replaces the renderer; this pass did not change human output. |
| Invalid Zotero JSON uses an `itemType` sentinel | Kept | Adapter parsing still uses `invalid_json`; changing its entry classification needs a focused import behavior pass. |
| Protected-term notice singles out R | Kept | It remains a special notice, but changing warnings is observable output outside this pass. |
| Export limitation handling matches message prose | Kept | Export projection still consumes preserved limitation text; changing the classification belongs with the structured registry export pass. |
| Alias conflict classified three ways | Fixed | `a702656` centralizes assignment and `alias_conflict`. |
| Label changes collision versus duplicate order | Fixed | `352a7f6` checks duplicate bytes first for either label state. |
| Path comparison and case normalization written six ways | Fixed | `fd955c2` shares `path_key`. |
| Identifier equivalence differs across routes | Fixed | `065c4c9` shares the identifier field list; validator normalization remains the entry rule. |
| arXiv archive test appears in three places | Kept | The three uses have different import and export contexts; collapsing them without output change needs export-pass evidence. |
| Filename fallback and misplacement rules repeated | Fixed | `fd955c2` makes filename and placement answer their own rule. |
| Schema version repeated and recovery chain hand-kept | Fixed | `fd955c2` uses one ordered migration structure. |
| Month tables and person-name joins repeated | Fixed | `065c4c9` shares both. |
| Unused `edition_display`, `doi_identity`, and tests-only `migrate` | Fixed | `8550820` removes them and uses guarded `connect` upgrade in tests. |
| Duplicate recovery version check, BibTeX loop/month lookups, production assert | Fixed | `8550820` removes the redundant paths. |
| Origin-match copy branch seems dead | Kept | `352a7f6` made it reachable for link-to-managed conversion by excluding the converting resource. |
| Project and collection revision columns never read | Kept | D4 explicitly retains this cheap concurrency seam, documented in the data model by `f8fce1e`. |
| SourceRecord and Result schema models only print schemas | Fixed | `f8fce1e` adds a real show/envelope validation test. |
| One-value export profile and mixed identity API | Fixed | `0a1854d` uses the profile constant and separate `rekey`/`set_state`. |
| Unreachable error codes and inconsistent `integrity_error` exits | Fixed | `5f550fe` removes dead branches; `b15655b` standardizes reachable integrity failures at exit 5. |
| Other reader-noted no-op branches and always-one-value settings | Kept | The extra `_add`, search guard, preservation pre-check, impossible collection value, and `apply_entry` setting are small local paths; removal was not among D4's named targets and has no demonstrated user effect. |
| Server backend requires SQL dialect, transaction, and catalog-layout work | Kept | D2 deliberately kept SQLite and prohibited new domain SQLite syntax; the inventory below is the explicit boundary. |
| Human-output lambda renderer and error rendering split | Kept | The planned plain-table human-output pass owns the replacement. |
| Upgrade notices on stdout and duplicated JSON warnings | Fixed earlier | Both were fixed by the human output pass (e9f3a3a) before this batch: notices go to stderr and warnings appear once, at the envelope's top level. Corrected by the reviewing session after the merge. |
| `import --input -` unavailable | Fixed | `109b6b1` accepts standard input through the shared payload reader. |
| Undocumented `project cite --from-import` | Kept | Help/contract surface work remains with the named help pass. |
| Generated `--no-` booleans, untyped choice help, and missing command help | Kept | The help pass owns this CLI presentation work. |

The extra length findings in the reader appendix were addressed by `ec77311`: Pydantic config tables, reconcile selection/application, Zotero import phases, pure exact matching, BibTeX/Zotero parse helpers, and bibliography preserved-field helpers. `f8fce1e` also splits serialization into names, titles, dates, language, publisher, identifiers, notes, and extensions without changing export output.

## SQLite boundary and size

`tests/contract/test_sqlite_boundary.py` freezes 13 SQLite-only statements in domain modules: seven in `importing.py`, one in `sources.py`, three in `bibliography.py`, and two in `projects.py`; its allowlist must shrink or stay equal. The listed constructs are `INSERT OR IGNORE`, `rowid`, `json_extract`, and `ON CONFLICT`; no `instr`, `PRAGMA`, or `executescript` remains in the domain allowlist. `catalog.py`, `recovery.py`, and adapters are deliberately outside this guard. The allowlist did not grow during the pass.

Application Python under `src/refs` was 5,304 lines at the brief (`e4539cf`) and is 5,712 lines at batch 4 (`ec77311`): **+408** across the pass. From the batch-3 merge (`4f06ae0`, 5,596 lines), batch 4 is **+116**. The owner chose to preserve the tested concern splits and report this positive delta rather than compress the implementation for a line target. These counts include the migration, model, and adapter code and exclude tests and documentation.

## Verification and acceptance boundary

Each batch-4 code commit passed the full suite and Ruff/ty. The final suite, smoke demo, and isolated real-trial harness are the release checks for this record; the harness reported zero failures and retained 556 supplied author lists, two editor-only records, and four without supplied creators. No owner catalog or external attachment tree was changed. The deferred export registry rewrite and kept help/renderer/backend findings require their own decisions or planned passes; they are not implied by this acceptance.
