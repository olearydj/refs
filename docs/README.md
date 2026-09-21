# refs Design Packet

**Current stage, 2026-09-21:** The owner-approved slice 1 trim is applied. Constitution 2.0.0 is in force; no amendment is pending. The next step is the owner's second right-sizing checkpoint. **Do not generate tasks yet.** No application or live migration has run.

## Authority and read order

Explicit owner decisions take precedence. Read [vision](vision.md), [accepted decisions](behavior-decisions.md), the [slice 1 spec](../specs/001-academic-catalog/spec.md), then [plan](../specs/001-academic-catalog/plan.md). The plan links four contracts and the data model. [Right-sizing](right-sizing.md) supplies the budget and preservation floor; [bibliographic model](bibliographic-model.md) explains the selected authority.

[Audit §§11–14](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) separate literal replies from interpretations. The trim keeps stable identities/keys, originals, revisions, internal boundaries and verified copy/restore, while deferring journals, stored waivers/projections, batch reconciliation and plugin machinery. Projects are cited-only. New copy intake renames by convention unless --keep-name; linked files and later reorganize preserve names.

## Evidence and history

The [archive](archive/README.md) contains historical drafts/research, not extra requirements. Git preserves audited baseline 3f9447e, revision 4209e5d and constitution 8435765. [Semantic review](../specs/001-academic-catalog/reviews/semantic-row-review-2026-09-21.md) and [mapping examples](../specs/001-academic-catalog/reviews/model-examples-2026-09-21/README.md) support the model without certifying a runtime importer. Earlier checklist assessments remain historical; they do not certify this trim.

See the [trim measurement](../specs/001-academic-catalog/reviews/2026-09-21-slice-1-trim.md) for the checkpoint. After owner judgment, generate tasks for the declared slice only, then run analyze. [Quickstart](../specs/001-academic-catalog/quickstart.md) owns implementation acceptance. No slice 2 specification work until slice 1 is used on one real paper.
