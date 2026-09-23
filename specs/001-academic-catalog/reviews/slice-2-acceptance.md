# Slice 2 acceptance

Date: 2026-09-22 (local). T038 through T051 are complete. The initial T038–T050 evidence below used synthetic fixtures at explicit temporary paths. The later T051 transcript records the owner-executed real cutover. Intermediate statements of outstanding work describe that point in the transcript; the completion section at the end gives current status.

**Archive location, 2026-09-22:** the cutover working directory referred to below as `~/refs-cutover-20260922` (the copied Zotero data directory, the `.bak` database, the extracted JSON, the whole-library export and its renders, 442 MB) was moved by the owner after the cutover to `/Volumes/Casa/archive/refs/zotero-2026-09-22`. Nothing in the catalog references it by path.

## Implementation commits

The five analysis decisions and appended tasks were committed as `a783263`. The owner's intervening bridge clarification, `bc05c65`, was retained.

| Task | Commit | Delivered |
| --- | --- | --- |
| T038 | `25422ad` | Pinned synthetic schema and independent fidelity gate. |
| T039 | `68b8c02` | One-time read-only extractor outside the package. |
| T040 | `b1de38a` | Migration 002 and `init --reuse-config`. |
| T041 | `ce547b8` | JSON admission, canonical mapping and identifier projections. |
| T042 | `ef6b8c6` | Persisted entry accounting and Zotero import. |
| T043 | `c93d4cf` | Collections, child context, relations and attachment locators. |
| T044 | `8877643` | Shared D3 binding and safe gap filling. |
| T045 | `30b5afb` | Batch inspection and revision-checked reconciliation. |
| T046 | `860561c` | Readable import and reconciliation reports. |
| T047 | `238cf64` | Collection browsing and search/list filters. |
| T048 | `0488b2d` | Collection text output and synthetic demo sections. |
| T049 | `5a9ef91` | Restore proof for fourteen populated logical tables. |
| T050 | This commit | Final integration, consumer, packaging and proportion evidence. |

## Verification

From the repository root, `uv sync --locked`, `uv run --locked pytest -q`, `uv run --locked ruff check .`, `uv run --locked ty check src/refs`, and `scripts/demo.sh --smoke` passed. The dependency cooldown and lockfile were unchanged.

- Pytest: 417 passed in 81.90 seconds; no skipped tests.
- Ruff: zero findings.
- ty: zero diagnostics.
- Pandoc, Biber and classic BibTeX with `elsarticle-num` all ran. The arXiv extension rendered `2407.01502` in all three; OCLC remained an explicitly reported omission. Existing particle, howpublished, protected-title and export-loss regressions also ran.
- The demo is 281 lines. Its output was `PASS refs demo: 109 checks (US1, US2, US3, US4, US5, US6)`.
- A rebuilt wheel installed into a fresh temporary environment with runtime dependency versions exported from `uv.lock`. That installed command passed the same 109-check smoke run. Archive inspection confirmed both migrations and the mapping registry, and excluded the extractor, test fixtures and upstream schema SQL.
- The documented restore procedure preserved all fourteen logical tables, including original JSON, identities, import decisions, collection parents, memberships and related endpoints. Backups contain no attachment bytes.

## Independent synthetic gate

The final fixture uses Zotero's schema-121 multipart date storage, nine creator roles, ordered coauthors, native/Extra/legacy key precedence, three collections, three memberships, three file attachments, URL context, child notes and a related pair. Its source files were unchanged after extraction/import. Tests also cover local library identities, malformed items, missing parents/bases/files, incompatible keys, contradictory dates, stale reviews, ambiguous identifiers and collection paths.

The first import reported `applied=6, unchanged=0, conflict=0, invalid=0`. Re-import reported `applied=0, unchanged=6, conflict=0, invalid=0`.

Executed with explicit paths beneath `/private/tmp/refs-slice2-acceptance-n6ehgkq7/final`:

```bash
.venv/bin/python tests/fixtures/real-trial/zotero_gate.py "$TRIAL/cat" \
  --zotero "$TRIAL/zotero/zotero.sqlite.bak" \
  --base-path "$TRIAL/zotero/base" \
  --legacy "$TRIAL/zotero/better-bibtex.sqlite" --json
```

```json
{
  "summary": {
    "zotero_items": 6,
    "zotero_collections": 3,
    "refs_bound_to_zotero": 6,
    "missing_items": 0,
    "findings": 0,
    "skipped": {
      "trash": 1,
      "annotations": 1,
      "attachment_outlines": 1
    }
  },
  "findings": []
}
```

Negative controls detect missing/wrong-library bindings, collection inventory and parent changes, creator role/order loss, altered file locators, missing child context and identifiers, and missing related pairs/endpoints. This is synthetic fidelity evidence, not acceptance of the owner's library or its rendered bibliography.

## Proportion and resolved details

Application Python under `src/refs` grew from 3,240 lines at `132d806` to 3,906, a net increase of 666. The separate extractor is 186 lines, making combined growth 852 lines against the roughly 800-line estimate. The extra work handles actual cutover hazards: multipart date fidelity, retained evidence on partial imports, and stale-source rejection after a read-only reconciliation preview. There are 23 classes, 26 callable command invocations, fourteen logical tables, two migrations and the same four runtime dependencies. The four added tables are exactly those approved; no filing, moves, journals or backlog interfaces were added.

The following readings were made concrete:

- The explicit arXiv fallback is the exception to the ordinary source-supplied-note rule. Howpublished passthrough remains unchanged.
- `batch_revision` is an opaque integer review token over the saved batch version and observed source revisions. Preview writes nothing; execution recomputes the token inside its write transaction. A source change or another reconciliation invalidates it.
- Collection counts and filters use direct active membership, not descendants. Imported hierarchy and empty collections remain visible.
- Child context uses a stable library/item URI as `original_ref`, so relocating an extraction directory does not change its context identity. Accepted reconciliation also retains a source-linked reference to its exact preserved incoming original.
- Zotero's [item serialization](https://github.com/zotero/zotero/blob/6.0.37/chrome/content/zotero/xpcom/data/item.js) and [pinned date helper](https://github.com/zotero/utilities/blob/cccf1235a318c259345fc623d5e9d6770ba19df7/date.js) establish the multipart-date conversion. The extractor emits the user text and parsed aid separately. Zero components retain partial precision; contradictory explicit values fail, and uncertain dates remain literal.

The broader role-omission classification attempted during acceptance was removed after an existing regression exposed it. Unassessed translator/contributor export behavior still blocks under the existing contract; this work does not declare whole-library rendering safe without the T051 comparison.

## Pre-cutover export reporting correction

The owner requested informational reporting for facts retained without an action to take. `issued_day_in_note`, `noncitation_omission`, `literal_publisher`, `field_in_note`, `container_in_note` and `assignee_in_note` now appear in JSON `data.info` and are absent from human output. Abstracts and tags remain unreported as before. Missing fields, consumer-dependent fallbacks, citation-field omissions and date-range projections remain warnings. Repeated warnings group by code; groups show up to five keys and direct the reader to `--json` for the remaining keys.

The existing temporary Zotero rehearsal, not the owner's catalog, exported 562 entries with 132 warnings and 445 informational notices instead of 577 warnings. Its text summary is 16 lines and 223 words. Informational counts are 227 issued-day projections, 168 noncitation omissions, 24 fields in notes, 16 literal publishers, 9 containers in notes and 1 assignee in a note.

| Warning code | Entries |
| --- | ---: |
| `arxiv_fallback` | 21 |
| `collection_editor_fallback` | 2 |
| `container_author_omission` | 3 |
| `contributor_omission` | 1 |
| `date_range_projected` | 2 |
| `field_omitted` | 3 |
| `journal_series_fallback` | 2 |
| `literal_issued_year` | 7 |
| `missing_author` | 4 |
| `missing_issued` | 6 |
| `missing_journal` | 3 |
| `oclc_omission` | 6 |
| `title_language_review` | 1 |
| `type_fallback` | 64 |
| `unassessed_import` | 7 |

Verification: `uv sync --locked` passed; 500 pytest tests passed; Ruff and ty reported no findings. The smoke result was `PASS refs demo: 109 checks (US1, US2, US3, US4, US5, US6)`. Regression fixtures cover the severity changes, grouped missing-field notices and short text for large groups. The real-trial harness now exports the whole BBT library and checks that retained facts appear as JSON info, not warnings. Its Pandoc comparison explicitly reports already-approved DOI lowercasing when that is the sole rendering difference.

The complete real-trial harness finished with `Trial failures: 0`. All five paper comparisons had zero unexplained differences. The separate BBT-input library export reported `Library export reporting: 757 warnings, 257 info; 13 text lines, 204 words`. That count differs from the Zotero-JSON rehearsal above: BBT's preserved-only input fields produce 598 `unassessed_import` notices. No mappings or import behavior changed in this reporting fix.

## T051 owner-assisted cutover

Completed by the owner, one step at a time, with results supplied in the conversation and recorded below. The assistant edited project documentation and inspected retained output files; it did not execute the real catalog operations, extraction, archive or manuscript replacement. Existing schema-1 catalogs need the documented explicit migration, or the separately authorized reset and `init --reuse-config`; ordinary commands do not silently upgrade them.

### Owner transcript: reset-path identification

The owner ran:

```bash
refs --no-project-config --config "$HOME/.config/refs/config.toml" paths
```

Actual output supplied by the owner:

```text
Configuration: /Users/djo/.config/refs/config.toml
Catalog: /Volumes/Casa/refs/cat
Library: /Volumes/Casa/refs/lib
```

The owner identified the trial backup directory as `/Volumes/Casa/refs/backups/20260922`. The reset is limited to that directory and `/Volumes/Casa/refs/cat`; configuration and `/Volumes/Casa/refs/lib` are retained. The owner subsequently executed the reset and initialization below.

### Owner transcript: reset and initialization

```bash
rm -rf -- /Volumes/Casa/refs/cat /Volumes/Casa/refs/backups/20260922 &&
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  init --reuse-config
```

Actual output supplied by the owner:

```text
Initialized catalog at /Volumes/Casa/refs/cat (library: /Volumes/Casa/refs/lib)
```

Initialization succeeded at the confirmed paths. Extraction subsequently succeeded as recorded below; import has not yet been reported.

### Owner transcript: retained extraction

```bash
mkdir "$HOME/refs-cutover-20260922" &&
cp -p "$HOME/Zotero/zotero.sqlite.bak" \
  "$HOME/refs-cutover-20260922/zotero.sqlite.bak" &&
uv run --project /Volumes/Casa/dev/refs --locked python \
  /Volumes/Casa/dev/refs/tools/zotero_extract/extract.py \
  --database "$HOME/refs-cutover-20260922/zotero.sqlite.bak" \
  --output "$HOME/refs-cutover-20260922/zotero-json" \
  --data-dir "$HOME/Zotero"
```

Actual output supplied by the owner:

```json
{"items": 1832, "collections": 58, "output": "/Users/djo/refs-cutover-20260922/zotero-json"}
```

The counts match the rehearsed database inventory. The retained database copy and extraction are outside the catalog. This is a database-backup copy, not yet evidence of the dated full Zotero data-directory archive required before retirement.

### Owner transcript: Zotero import

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  import --format zotero \
  --input "$HOME/refs-cutover-20260922/zotero-json" \
  --origin zotero
```

Actual summary and preservation footer supplied by the owner (the intervening per-entry notices are omitted here):

```text
Imported 562, unchanged 0, conflicts 0, invalid 0 from /Users/djo/refs-cutover-20260922/zotero-json
Preservation: 240 annotations skipped as catalog content; retain the original Zotero archive
Preservation: 246 attachment outlines skipped as catalog content; retain the original Zotero archive
Preservation: 3 standalone children skipped as catalog content; retain the original Zotero archive
```

The owner also supplied the per-entry output: unprotected-capital review warnings, preserved-only field notices and seven literal-date limitations. No conflict or invalid entry was reported. Fidelity gate execution is the next step; these import counts alone do not establish fidelity.

### Owner transcript: real fidelity gate

```bash
uv run --project /Volumes/Casa/dev/refs --locked python \
  /Volumes/Casa/dev/refs/tests/fixtures/real-trial/zotero_gate.py \
  /Volumes/Casa/refs/cat \
  --zotero "$HOME/Zotero/zotero.sqlite" \
  --json
```

Actual output supplied by the owner:

```json
{
  "summary": {
    "zotero_items": 562,
    "zotero_collections": 58,
    "refs_bound_to_zotero": 562,
    "missing_items": 0,
    "findings": 0,
    "skipped": {
      "trash": 0,
      "annotations": 240,
      "attachment_outlines": 246
    }
  },
  "findings": []
}
```

The real fidelity gate passed. Whole-library export and rendering, unchanged re-import, backup, the manuscript walkthrough and the full Zotero archive remain outstanding.

### Owner transcript: whole-library project

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  project create zotero-library
```

Actual output supplied by the owner:

```text
Created project zotero-library
```

### Owner transcript: cite imported library

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  project cite zotero-library --from-import zotero
```

Actual output supplied by the owner:

```text
Cited 562 in zotero-library (0 already cited)
```

### Owner transcript: whole-library export

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  export --project zotero-library \
  --output "$HOME/refs-cutover-20260922/library.bib"
```

Actual summary supplied by the owner:

```text
Wrote /Users/djo/refs-cutover-20260922/library.bib (562 entries, 132 warnings)
```

The owner supplied all 15 grouped warning lines. Their counts match the pre-cutover breakdown above exactly, including two range projections and the language-review notice for farrell2020stati. No export block occurred. Rendering comparison remains outstanding.

### Owner transcript: whole-library rendering

```bash
printf '%s\n' '---' 'nocite: "@*"' '---' \
  > "$HOME/refs-cutover-20260922/compare.md" &&
pandoc "$HOME/refs-cutover-20260922/compare.md" --citeproc \
  --bibliography /Volumes/Casa/dev/refs/tests/fixtures/real-trial/inputs/zotero-bbt-export.bib \
  -t plain -o "$HOME/refs-cutover-20260922/bbt-render.txt" &&
pandoc "$HOME/refs-cutover-20260922/compare.md" --citeproc \
  --bibliography "$HOME/refs-cutover-20260922/library.bib" \
  -t plain -o "$HOME/refs-cutover-20260922/refs-render.txt" &&
printf '%s\n' 'Both renderings completed.'
```

Actual output supplied by the owner:

```text
Both renderings completed.
```

The owner reported no other messages. Read-only comparison of the resulting files established that the cutover library export is byte-identical to the reviewed real-v3 rehearsal export (SHA-256 `ac1d4ef2a0c2d28c335e541506fd519e6bcb911fbc6ddd34e7b7a649bdf7e219`), and the BBT input is byte-identical to that rehearsal's original (SHA-256 `39b97d2588c47eda0e9584b487cefa2076908a96f4f50a9a6f9a7c429d68229b`). The saved plain renderings contain 2,404 and 2,307 lines respectively. The previously reviewed 268 per-entry differences therefore apply to these same bibliography inputs: 68 casing-only, 128 owner-accepted Google Books URL omissions with casing, and 72 other documented presentation differences. Detailed private evidence remains at `/private/tmp/refs-rehearsal-20260922/real-v3/render-differences-reviewed.md`; the current plain-text diff is `/private/tmp/refs-cutover-render.diff`. Neither the real catalog nor Zotero was opened by the assistant for this comparison.

### Owner transcript: unchanged re-import

```bash
refs --json --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  import --format zotero \
  --input "$HOME/refs-cutover-20260922/zotero-json" \
  --origin zotero \
  > "$HOME/refs-cutover-20260922/reimport.json" &&
jq '.data.counts' "$HOME/refs-cutover-20260922/reimport.json"
```

Actual output supplied by the owner:

```json
{
  "applied": 0,
  "unchanged": 562,
  "conflict": 0,
  "invalid": 0
}
```

Re-import idempotence passed on the real catalog. The complete report is retained in the cutover directory.

### Owner transcript: post-import backup

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  backup --output /Volumes/Casa/refs/backups/20260922-zotero-import
```

Actual output supplied by the owner:

```text
Wrote snapshot /Volumes/Casa/refs/backups/20260922-zotero-import (external file bytes excluded)
```

The post-import catalog snapshot succeeded. It does not substitute for the full Zotero data-directory archive or back up attachment bytes. The paper walkthrough remains outstanding.

### Owner transcript: Pipyer bibliography import

```bash
refs --json --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  import --format bib \
  --input /Volumes/Casa/pub/pipyer-paper/references.bib \
  --origin pipyer-paper \
  > "$HOME/refs-cutover-20260922/pipyer-import.json" &&
jq '.data | {counts, entries: [.entries[] | {citation_key, status, binding, conflicts}]}' \
  "$HOME/refs-cutover-20260922/pipyer-import.json"
```

The owner reported counts `{"applied":11,"unchanged":0,"conflict":0,"invalid":0}`. All eleven entries had status `applied`, empty binding objects and null conflicts. Keys: ditommaso2017, kapoor2024, khattab2024, koster2012, landau2021, pydanticai2026, qiu2026, sureshkumar2026, vandewater2026, zaharia2018 and zhang2025. The complete actual envelope is retained at `/Users/djo/refs-cutover-20260922/pipyer-import.json`.

Read-only comparison of that report's eight supplied DOIs against the retained Zotero JSON extraction, including DOI lines in Extra and normalized DOI casing/prefixes, found no overlaps. Three entries supplied no DOI. Empty binding objects are therefore expected here; this paper import does not exercise DOI binding. The separate Attention input has DOI `10.48550/ARXIV.1706.03762`, matching Zotero item AFNPWINJ with retained key vaswani2017atten, and will provide the real overlap check. No real catalog query was run by the assistant.

### Owner transcript: Attention DOI binding

```bash
refs --json --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  add --format csljson \
  --input /Volumes/Casa/dev/refs/tests/fixtures/real-trial/inputs/attention.json \
  > "$HOME/refs-cutover-20260922/attention-add.json"
cat "$HOME/refs-cutover-20260922/attention-add.json"
```

The owner supplied the complete result envelope, retained at `/Users/djo/refs-cutover-20260922/attention-add.json`. It reports `status: error`, `outcome: needs_attention`, and error code `identity_conflict`. The binding is `bound: true`, with catalog key `vaswani2017atten` and existing source ID `b45dd6f6-b906-42a3-a92f-bbee45eeda70`, now revision 3. The result reports gap fills for `metadata.publisher` and `metadata.version`, with current values arXiv and 7. It retains the Zotero key, provenance and linked PDF resource.

Three differences were reported and not overwritten: issued date `[[2017,12,5]]` versus incoming `[[2017]]`; differing abstract text; and the current HTTP arXiv URL versus incoming HTTPS. Both original inputs and their provenance are retained. This is D3's bind-and-fill partial result: it did not create a second source, and the error envelope does not mean the gap fills were rolled back. No owner decision resolving the three reported differences has yet been recorded; retaining current values allows the independent Pipyer walkthrough to continue.

### Owner transcript: Pipyer project

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  project create pipyer-paper
```

Actual output supplied by the owner:

```text
Created project pipyer-paper
```

### Owner transcript: cite Pipyer sources

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  project cite pipyer-paper --from-import pipyer-paper
```

Actual output supplied by the owner:

```text
Cited 11 in pipyer-paper (0 already cited)
```

### Owner transcript: Pipyer adoption preview

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  export --project pipyer-paper \
  --output /Volumes/Casa/pub/pipyer-paper/references.bib \
  --adopt --overwrite --dry-run
```

Actual output supplied by the owner, with line breaks restored from the pasted single line:

```text
Preview: Wrote /Volumes/Casa/pub/pipyer-paper/references.bib (11 entries, 8 warnings)
Warning: 4 entries use the portable @misc fallback (kapoor2024, pydanticai2026, qiu2026, sureshkumar2026)
Warning: 3 entries use portable arXiv fields (kapoor2024, qiu2026, sureshkumar2026)
Warning: vandewater2026: Portable names retain the particle before the family name; consumers determine dropping behavior
```

The preview passed without a block. Actual adoption and replacement have not yet been reported.

### Owner transcript: Pipyer adoption and replacement

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  export --project pipyer-paper \
  --output /Volumes/Casa/pub/pipyer-paper/references.bib \
  --adopt --overwrite
```

Actual output supplied by the owner, with line breaks restored from the pasted single line:

```text
Wrote /Volumes/Casa/pub/pipyer-paper/references.bib (11 entries, 8 warnings)
Warning: 4 entries use the portable @misc fallback (kapoor2024, pydanticai2026, qiu2026, sureshkumar2026)
Warning: 3 entries use portable arXiv fields (kapoor2024, qiu2026, sureshkumar2026)
Warning: vandewater2026: Portable names retain the particle before the family name; consumers determine dropping behavior
```

The owner completed replacement and adoption of the manuscript bibliography. Rendering remains outstanding.

### Owner transcript: Pipyer render

```bash
(cd /Volumes/Casa/pub/pipyer-paper && quarto render)
```

Actual completion output supplied by the owner:

```text
Output created: output/pdf/paper.pdf
```

Quarto produced the manuscript PDF. No warning text was supplied. Owner review of the rendered reference list has not yet been reported. The dated full Zotero data-directory archive also remains outstanding; the retained database backup and refs snapshot do not contain all Zotero storage files. T051 remains incomplete.

### Owner evidence: rendered Pipyer reference list

The owner supplied a screenshot of the rendered reference list across pages 3 and 4. Visual inspection shows all eleven imported references, protected capitalization of R and DSPy, retained arXiv descriptions and the Python software/version description. The van de Water entry renders as “Water, Robin P. van de,” consistent with the reported consumer-dependent name-particle fallback. No obvious missing entry or broken reference is visible. The screenshot does not independently establish equality with the previous manuscript build or verify in-text citations elsewhere in the paper. The screenshot is external evidence supplied in the conversation; it was not copied into Git.

### Owner transcript: full Zotero archive

The owner was instructed to quit Zotero before running:

```bash
test ! -e "$HOME/refs-cutover-20260922/zotero-archive" &&
ditto "$HOME/Zotero" "$HOME/refs-cutover-20260922/zotero-archive" &&
diff -qr "$HOME/Zotero" "$HOME/refs-cutover-20260922/zotero-archive" &&
printf '%s\n' 'Zotero archive copied and verified.'
```

Actual output supplied by the owner:

```text
Zotero archive copied and verified.
```

The retained full data-directory copy is `/Users/djo/refs-cutover-20260922/zotero-archive`, outside the catalog. The recursive comparison reported no content differences. This archive retains stored attachments and Zotero-only content; externally linked PDFs remain in Box and are not included. The final catalog snapshot after the paper walkthrough remains outstanding.

### Owner transcript: final catalog snapshot

```bash
refs --no-project-config \
  --config "$HOME/.config/refs/config.toml" \
  --catalog /Volumes/Casa/refs/cat \
  backup --output /Volumes/Casa/refs/backups/20260922-cutover-complete
```

Actual output supplied by the owner:

```text
Wrote snapshot /Volumes/Casa/refs/backups/20260922-cutover-complete (external file bytes excluded)
```

## T051 completion and remaining data review

The real cutover is complete: 562 Zotero sources imported with zero conflicts or invalid entries; the real fidelity gate reported zero findings; the whole-library export wrote and rendered using the same bibliography bytes as the reviewed rehearsal; re-import reported all 562 unchanged. The owner imported eleven additional Pipyer sources, recreated its project, adopted its bibliography and rendered the paper. Attention bound to its existing Zotero identity and retained its assigned key while filling missing values and reporting differences. The full Zotero data directory was archived and compared, and the final catalog snapshot includes the paper project, export adoption and Attention gap fills. No file organization or slice 3 work was performed.

Remaining data review is not concealed as completed reconciliation:

- Attention: closed 2026-09-22 after review. The catalog kept the better values in all three differences (full date `2017-12-05` over `2017`, the abstract, the resolving URL); `publisher` and `version` were filled. The differences were reported only in the `add` result envelope because `add` persists no batch; that gap is the next fix batch's item (a) in the plan's deferred ledger. A redundant copy of the PDF made during post-cutover review was unlinked and deleted by the owner; the record's attachment is the Box-linked file.
- farrell2020stati retains the valid but misapplied `bn` language tag (a translator mislabel on an English paper). Correction: `refs update farrell2020stati --set 'metadata.language="en"' --if-revision 2`, handed to the owner 2026-09-22.
- The previously identified patent assignee value warrants owner inspection and was preserved unchanged.
- The earlier annotation check found one malformed embedded annotation object, in `janssens2021data` (Janssens 2021, *Data Science at the Command Line*, two highlights in Zotero). The owner opens it once with `refs open janssens2021data` to confirm both highlights render. The full archive preserves the original evidence.

Facts established during post-cutover review, 2026-09-22:

- 40 of the 551 file links resolve into `~/Zotero/storage/` (Zotero-stored snapshots and downloads), not `~/Box Sync/zotero` (511). The Zotero data directory therefore remains a live file store until slice 3 relocates those files; the archive copy at `/Volumes/Casa/archive/refs/zotero-2026-09-22/zotero-archive` duplicates them.
- The 128 "missing links" in the render comparison are Google Books URLs that Better BibTeX synthesizes at export from the `google-books-id` Extra line. Under D4 refs does not model that line, so no stored URL was lost; the render difference is the decision working as chosen.
- Citation keys are deliberately mixed: the 562 imported records keep their Better BibTeX keys (`vaswani2017atten`), and only refs-generated keys use the accepted hyphenated form. A record captured before the reset under a new-style key (`vaswani-2017-attentionIs`) no longer exists; the post-reset re-add bound by DOI to the Zotero record, whose key survives. `key set` changes a key deliberately and reserves the old one.
- The live Zotero database had a leftover `zotero.sqlite-journal` after the cutover, indicating an unclean last exit; the owner removed it. The archive holds a consistent `.bak`; nothing opens the live database again.

The catalog backup excludes attachment bytes. Box-linked PDFs remain at their original paths and outside both the catalog snapshot and the copied Zotero data directory. Rendering acceptance is based on the explained rehearsal differences, byte identity of bibliography inputs, successful actual renders and the supplied reference-list screenshot; it does not claim identical rendering for every portable projection.
