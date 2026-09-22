# refs Design Packet

**Current stage, 2026-09-22:** Slice 1 is built, verified and in first use. All 37 [tasks](../specs/001-academic-catalog/tasks.md) are complete, including the code-complete checkpoint (T036) and the owner's real-paper trial (T037, the Pipyer paper, 2026-09-22): capture, correction, citation, adopted export, Quarto render matching the previous build, outside-edit guard and backup, all at the real locations. Two polish batches from real-input trials are merged. The owner's catalog lives at `/Volumes/Casa/refs`; `refs` is installed with `uv tool install -e .`. Nothing from slice 2 is specified; the owner is using the tool and keeping a list of what is reached for and missing. No Zotero migration has run.

## Authority and read order

Explicit owner decisions take precedence. Read [vision](vision.md), [accepted decisions](behavior-decisions.md), the [slice 1 spec](../specs/001-academic-catalog/spec.md), then [plan](../specs/001-academic-catalog/plan.md). The plan links four contracts and the data model. [Right-sizing](right-sizing.md) supplies the budget and preservation floor; [bibliographic model](bibliographic-model.md) explains the selected authority.

[Audit §§11–14](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) separate literal replies from interpretations. The trim keeps stable identities/keys, originals, revisions, internal boundaries and verified copy/restore, while deferring journals, stored waivers/projections, batch reconciliation and plugin machinery. Projects are cited-only. New copy intake renames by convention unless --keep-name; linked files and later reorganize preserve names.

## Evidence and history

The [archive](archive/README.md) contains historical drafts/research, not extra requirements. Git preserves audited baseline 3f9447e, revision 4209e5d and constitution 8435765. [Semantic review](../specs/001-academic-catalog/reviews/semantic-row-review-2026-09-21.md) and [mapping examples](../specs/001-academic-catalog/reviews/model-examples-2026-09-21/README.md) support the model without certifying a runtime importer. Earlier checklist assessments are in [docs/archive/checklists](archive/checklists/requirements.md); they remain historical and do not certify this trim.

[Slice 1 acceptance](../specs/001-academic-catalog/reviews/slice-1-acceptance.md) records the checkpoint measurements and the real-paper trial; the [trim measurement](../specs/001-academic-catalog/reviews/2026-09-21-slice-1-trim.md) records the earlier checkpoint. The real-input harness in `tests/fixtures/real-trial/` reproduces the trials. The next step is use, then a one-page slice 2 brief from the owner's list, per [right-sizing](right-sizing.md).
