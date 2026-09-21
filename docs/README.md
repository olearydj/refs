# refs Design Notes

**Current stage, 2026-09-21:** The academic catalog design has been revised after the independent audit and nine recorded user decisions. [Plan](../specs/001-academic-catalog/plan.md) declares slice 1. Independent reassessment is complete: requirements 16/16 and bibliography 36/36 as written requirements. The explicit Principle II amendment remains the task-generation gate; these marks do not establish implementation readiness. No application implementation or live migration has run.

## Read order and authority

Explicit user decisions take precedence. [Vision](vision.md) owns product intent; [behavior decisions](behavior-decisions.md) owns accepted conventions and their provenance; the [spec](../specs/001-academic-catalog/spec.md) owns detailed outcomes; plan/contracts select implementation. [Audit sections 11–12](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) distinguish literal replies from the auditor's interpretations. Earlier draft commands do not become accepted through repetition.

| Document | Purpose |
| --- | --- |
| [Vision](vision.md) | Product purpose and enduring ownership boundaries. |
| [Behavior decisions](behavior-decisions.md) | Titles, keys, capture and revised A2, with provenance corrections. |
| [Academic MVP](academic-mvp.md) | First useful workflow and revised four-slice sequence. |
| [Bibliographic model](bibliographic-model.md) | Selected CSL-shaped core, alternatives and limits. |
| [Requirements review](requirements-review.md) | Historical questions and ongoing backlog, including later CSL/Zotero outputs. |
| [Configuration/CLI draft](configuration-and-cli.md) | Historical proposals; current contracts supersede conflicting examples. |
| [Architecture](architecture.md) | Broader needs and justified capability boundaries. |
| [Workflow research](workflow-research.md) | Local observations and provenance, with historical limits. |
| [Development brief](development.md) | Earlier research sequence and evaluation rationale. |
| [ArjanCodes review](arjancodes-review.md) | Supporting design research, not a prescribed framework. |
| [Right-sizing](right-sizing.md) | Owner's 1 to 10 scale, calibration against sibling tools, slice 1 budget, never-cut floor, and checkpoints. Operative summary is in `AGENTS.md`. |

## Current decisions

Use one CSL-shaped bibliographic authority, type-scoped mappings, optional native type and justified extensions, with verbatim per-entry originals. Fold imported Zotero child notes into context, exclude annotation/outline records, retain related pairs and archive Zotero externally. Titles stay Unicode Title Case with protected terms and a whole-title flag; citation styles govern exported presentation. Generate name tokens with Latin-only built-in normalization/table and overrides, without a transliteration dependency.

Slice 1 is capture-to-portable-BibTeX export, linking, verified copy into Unfiled and demonstrated snapshot restore. Collections, folder-based filing and move/reorganize are slice 2; Zotero migration is slice 3; full restore/exit tooling is slice 4. Richer bibliography output is deferred until declared consumers need it. Four-class export reporting includes scoped waivers and single-run unknown overrides; documented fallback re-import uses saved projection evidence.

Config stays ~/.config/refs/config.toml; the selected data folders are /casa/refs/cat and /casa/refs/lib, represented canonically as /Volumes/Casa/refs/.... Only lib may be synced. Root-based ownership removes the stored mode flag and adopt command. Missing/unwritable data locations fail explicitly without fallback creation. No real folder move or sync configuration is authorized by this design revision.

## Evidence and next gates

The [semantic review](../specs/001-academic-catalog/reviews/semantic-row-review-2026-09-21.md) individually disposes of the 51 disputed crosswalk fields. [Fourteen examples](../specs/001-academic-catalog/reviews/model-examples-2026-09-21/README.md) test candidate mappings and an independent reader, not refs' future importer. The [audit](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md) and preserved evidence retain their historical findings/counts. A [baseline archive](../specs/001-academic-catalog/reviews/baseline-before-revision-2026-09-21.tar.gz) preserves governing documents before this revision.

Both checklists have now been re-evaluated by independent reviewers; the [revision summary](../specs/001-academic-catalog/reviews/2026-09-21-revision-summary.md) links their findings and verified repairs. Generate tasks for the declared slice 1 only, then run speckit-analyze read-only. The constitution conflict must be explicitly amended rather than silently interpreted away. Current implementation acceptance and live-paper gates remain in [quickstart](../specs/001-academic-catalog/quickstart.md).
