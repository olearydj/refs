# Bibliographic Model and Standards

**Decision, 2026-09-21:** Use one CSL-shaped core for shared facts, an optional native type label, and a short list of justified extensions. Preserve each imported entry verbatim. This replaces the exhaustive Zotero vocabulary mandate introduced on 2026-09-20. Authority is the user's “A: What I use (Recommended)” selection, recorded separately from the auditor's interpretation in [audit section 11](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items).

## What a source is

A source is a retained bibliographic description with a stable refs identity and assigned citation key. Editions and versions remain distinct unless explicitly reconciled. Files, personal context, collections and projects belong to refs' surrounding catalog model. CSL does not define those relationships or refs' storage layout. Zotero item and library identities are provenance, never authority to update Zotero objects.

## Selection and evidence

The [semantic review](../specs/001-academic-catalog/reviews/semantic-row-review-2026-09-21.md) evaluates all 51 disputed crosswalk fields plus the three remaining native fields individually. The [synthetic examples](../specs/001-academic-catalog/reviews/model-examples-2026-09-21/README.md) exercise candidate Zotero mappings, agent input and an independent BibTeX reader. These support shared publisher, genre, number, issue and container fields, with aliases scoped by source type. They do not certify refs' future importer.

The core uses CSL field names and name/date structures. It is a bounded profile, not a promise to edit every published property. Thesis university and BibTeX school share publisher; report number and journal issue occupy different paths. The registry follows reviewed meanings and examples. Preserved-only fields are reported as such and can be promoted later from their originals without re-import.

Extensions cover patent assignees, application number and priority date, and journal series distinct from book/report series. Each has a named fixture obligation and output limitation. Approximate mappings such as programming language to genre or legislative session to chapter number are rejected. Unsupported facts remain original evidence rather than parallel editable fields. The [mapping contract](../specs/001-academic-catalog/contracts/bibliography.md) owns exact paths and fixture gates.

| Alternative | Benefit | Reason for selection |
| --- | --- | --- |
| Zotero-shaped authority | Natural full-vocabulary migration model | Coherent if full Zotero breadth becomes the requirement; the user selected the vocabulary they use. |
| BibLaTeX-shaped authority | Rich publication and TeX representation | Too tied to processing syntax for ordinary agent capture; expressions remain evidence. |
| CSL-shaped core with justified extensions | Shared citation meanings and direct agent input | Selected; extensions and mappings still require evidence. Equivalence is not automatic. |

The native label and originals preserve future options, not a demonstrated cheap or lossless return to Zotero. Public CSL-JSON and Zotero API JSON outputs remain backlog items.

## Titles and output

Store plain Unicode Title Case with per-title protected terms and a whole-title preserve-case flag. Accent/command braces are not automatically protection. Citation style governs output; internal casing does not override APA or other styles. Portable BibTeX emits Title Case with protection braces. Future CSL output derives suitable sentence case. Non-English titles need an export language declaration; unprotected mid-title capitals warn.

Slice 1 implements portable BibTeX with documented miscellaneous fallbacks. Richer output requires declared compatible consumers and a later implementation. Quarto discovery may suggest a declaration, never choose silently. Four-class reports distinguish faithful incompleteness, documented fallback, enumerated blocking loss and unknown mapping. Saved projection history is deferred by audit §14. Slice 1 import never overwrites, is safe to rerun, and may report lossy fallback differences as conflicts; the richer current record remains intact.

## Notes and migration

Zotero child notes become imported, previewed, searchable source context. Attachment outline notes and annotation rows are not imported; related links remain simple pairs. Archive the dated Zotero data directory outside the catalog. The authorized audit check matched 239 of 240 annotations on nine PDFs; one malformed object needs a viewer check before retiring Zotero. Presence and position do not establish rendering.

## Standards and authority

Published [CSL schemas](https://github.com/citation-style-language/schema), [Zotero vocabulary](https://www.zotero.org/support/kb/item_types_and_fields), and [BibLaTeX source](https://github.com/plk/biblatex) supply meanings and compatibility evidence, not a universal lossless reference format. Pins remain in the registry. Audit sections 11–12 record user decisions that supersede earlier proposals. The specification owns outcomes, contracts own executable boundaries, and evidence records observations and limits.
