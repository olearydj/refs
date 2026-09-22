# refs Design Packet

**Current stage, 2026-09-22:** Slice 1 is built and accepted after the owner's Pipyer trial. Slice 2, Zotero ingest, is specified in the [plan](../specs/001-academic-catalog/plan.md#slice-2-brief-bring-the-library-across) and contracts; tasks are next. D1–D4 are decided. D3 requires resetting the trial catalog before the later authorized library import, then restoring Pipyer and Attention through the walkthrough. No migration or reset has run. File organization is slice 3.

## Authority and read order

Explicit owner decisions take precedence. Read [vision](vision.md), [accepted decisions](behavior-decisions.md), the [slice 1 spec](../specs/001-academic-catalog/spec.md), then [plan](../specs/001-academic-catalog/plan.md). The plan links five contracts and the data model. [Right-sizing](right-sizing.md) supplies the budget and preservation floor; [bibliographic model](bibliographic-model.md) explains the selected authority.

[Audit §§11–14](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) separate literal replies from interpretations. The trim keeps stable identities/keys, originals, revisions, internal boundaries and verified copy/restore, while deferring journals, stored waivers/projections, bulk reconciliation policies and plugin machinery. Projects are cited-only. New copy intake renames by convention unless --keep-name; linked files and later reorganize preserve names.

## Evidence and history

The [archive](archive/README.md) contains historical drafts/research, not extra requirements. Git preserves audited baseline 3f9447e, revision 4209e5d and constitution 8435765. [Semantic review](../specs/001-academic-catalog/reviews/semantic-row-review-2026-09-21.md) and [mapping examples](../specs/001-academic-catalog/reviews/model-examples-2026-09-21/README.md) support the model without certifying a runtime importer. Earlier checklist assessments are in [docs/archive/checklists](archive/checklists/requirements.md); they remain historical and do not certify this trim.

[Slice 1 acceptance](../specs/001-academic-catalog/reviews/slice-1-acceptance.md) records the checkpoint measurements and the real-paper trial; the [trim measurement](../specs/001-academic-catalog/reviews/2026-09-21-slice-1-trim.md) records the earlier checkpoint. The real-input harness in `tests/fixtures/real-trial/` reproduces the trials. Next: slice 2 tasks, then analysis; the [right-sizing](right-sizing.md) guardrails apply.
