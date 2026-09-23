# refs Design Packet

**Current stage, 2026-09-22:** Slices 1 and 2 are delivered. The owner's Zotero library (562 sources, 58 collections, 551 file links) was imported on 2026-09-22 with zero conflicts and a zero-finding fidelity gate against the live database; Zotero is now an archive, copied alongside the catalog snapshots. All 51 [tasks](../specs/001-academic-catalog/tasks.md) are complete; [slice 2 acceptance](../specs/001-academic-catalog/reviews/slice-2-acceptance.md) holds the cutover transcript and three open data-review items for the owner. Files remain linked in place under the old Zotero tree; the [slice 3 brief](../specs/001-academic-catalog/plan.md#slice-3-brief-organize-files) (organize files, 2026-09-23) awaits the owner's four decisions.

## Authority and read order

Explicit owner decisions take precedence. Read [vision](vision.md), [accepted decisions](behavior-decisions.md), the [slice 1 spec](../specs/001-academic-catalog/spec.md), then [plan](../specs/001-academic-catalog/plan.md). The plan links five contracts and the data model. [Right-sizing](right-sizing.md) supplies the budget and preservation floor; [bibliographic model](bibliographic-model.md) explains the selected authority.

[Audit §§11–14](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) separate literal replies from interpretations. The trim keeps stable identities/keys, originals, revisions, internal boundaries and verified copy/restore, while deferring journals, stored waivers/projections, bulk reconciliation policies and plugin machinery. Projects are cited-only. New copy intake renames by convention unless --keep-name; linked files and later reorganize preserve names.

## Evidence and history

The [archive](archive/README.md) contains historical drafts/research, not extra requirements. Git preserves audited baseline 3f9447e, revision 4209e5d and constitution 8435765. [Semantic review](../specs/001-academic-catalog/reviews/semantic-row-review-2026-09-21.md) and [mapping examples](../specs/001-academic-catalog/reviews/model-examples-2026-09-21/README.md) support the model without certifying a runtime importer. Earlier checklist assessments are in [docs/archive/checklists](archive/checklists/requirements.md); they remain historical and do not certify this trim.

[Slice 1 acceptance](../specs/001-academic-catalog/reviews/slice-1-acceptance.md) records the checkpoint measurements and the real-paper trial; the [trim measurement](../specs/001-academic-catalog/reviews/2026-09-21-slice-1-trim.md) records the earlier checkpoint. The real-input harness in `tests/fixtures/real-trial/` reproduces the trials. Next: slice 2 tasks, then analysis; the [right-sizing](right-sizing.md) guardrails apply.
