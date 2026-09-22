# Slice 2 synthetic acceptance

Date: 2026-09-22. Scope: T038 through T050. T051 has not run. Every catalog, extraction, attachment and restore used synthetic fixtures at explicit temporary paths. The owner's catalog, Zotero data and Box tree were not accessed.

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

Not started. The owner must participate in identifying the reset paths and running reset/extraction. The real gate and whole-library rendering remain required. Existing schema-1 catalogs need the documented explicit migration, or the separately authorized reset and `init --reuse-config`; ordinary commands do not silently upgrade them.
