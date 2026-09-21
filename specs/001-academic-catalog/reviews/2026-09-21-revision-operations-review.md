# Independent Operations Review of Revised Academic Catalog Design

**Date:** 2026-09-21. **Scope:** read-only review of governing documents; only this report and independent assessments in requirements.md were written. No live catalogs, attachments, dependency installations or application tests were used. Reviewed audit sections 10–12 in full, the current specification, plan, data model, CLI/configuration/file/recovery/interchange/search contracts, records contract, quickstart, constitution and docs index.

## Verdict

The revision substantially improves ownership, slice boundaries and recovery evidence, but is not yet ready for executable task generation. Resolve the separate pending Principle II amendment, the additional capability conflict below, and the concrete command/concurrency gaps. These are design findings, not failed runtime tests. The larger bibliography review is independent of this report.

## Known pending constitutional gate

**K01 — Principle II amendment pending (Critical).** Constitution Principle II requires adopting an existing linked file without an immediate move; the accepted root-derived ownership rule removes the outside-root managed state. The plan correctly reports the conflict. An explicit separate amendment is required; neither this review nor a later analyze run can reinterpret it away. No additional product question is needed about A2 itself.

## Findings

| ID | Severity | Location | Finding and required resolution |
| --- | --- | --- | --- |
| O01 | Critical | constitution Principles IV/V; contracts/capabilities.md paragraphs 1/3; plan.md Constitution review | Search is introduced in slice 1, but the contract defers selectable external implementations and an alternative demonstration until a later real alternative appears. IV requires selectable implementations as capabilities are introduced, adding one without modifying/rebuilding core, and V requires the replacement demonstration when delivered. An internal function alone does not meet that wording. Either provide the smallest compliant selectable boundary and alternative proof now, or obtain a separate explicit constitutional amendment. Do not describe the current deferral as compliant. |
| O02 | High | data-model.md Transactions, paragraph 2; contracts/cli.md operations row and paragraph following pagination | A hot SQLite journal may require explicit writable recovery before read-only queries can inspect operations. The only named recovery command is recover OP, which assumes a discoverable operation and conflates SQLite rollback recovery with external-effect recovery. A crash during an ordinary metadata write need not have a prepared file-operation ID at all. Specify a catalog-level recovery command, its lock/confirmation behavior and post-recovery integrity checks, distinct from recover OP. Add the metadata-write crash fixture. |
| O03 | High | data-model.md resources/operations rows; contracts/files-and-recovery.md prepared state; contracts/cli.md resource primary/unlink rows | Source and project revisions are defined, but the file protocol captures a resource revision and resource commands accept --if-revision without defining its authority. Specify whether resources have their own revision or use the parent source aggregate revision; define exactly which resource mutations advance it, return it in resource results, and use that same token for reservations and stale checks. Otherwise independently implemented modules can compare incompatible tokens. |
| O04 | Medium | spec.md FR-044 and Story 6 scenario 1; contracts/cli.md init row; configuration.md initialization | Spec requires repeatable setup preserving existing data/preferences; CLI says creation with no overwrite but leaves existing-valid-catalog behavior undecided. State that identical repeated setup is a validated no-op, and define a non-mutating conflict for different requested locations/settings or an incomplete directory. Include the configuration file as an independently protected output. |
| O05 | Medium | contracts/cli.md pagination paragraph; data-model.md catalog_meta row | Pagination must expose changes using a catalog snapshot/revision, but no catalog revision or snapshot token is defined. Source/project revisions cannot reveal every catalog-wide change between pages. Select a monotonic catalog change counter or another concrete token, define which mutations advance it, and expose it in list/search. |
| O06 | Low | spec.md A-05/A-11; requirements.md historical paragraphs | The draft assumptions still say transliteration-package selection requires research/planning despite the later explicit no-dependency choice and versioned Latin policy. Historical checklist notes correctly remain historical, but active assumptions should distinguish completed decisions from remaining implementation research so task generation does not reopen the chosen policy. |

## Strengths verified in the written design

- The catalog/config/library separation is explicit, with canonical Casa paths, no fallback initialization and agent access diagnostics. The live database/staging are outside the synced library.
- Root-derived ownership, Unfiled, no stored mode and catalog-only folder filing are consistent across the revised operating contracts.
- Copy-first intake preserves the source and stages outside the synced tree. Same-volume publication is explicitly separated from whole-operation atomicity. Equal digests alone do not establish destination ownership.
- Native metadata preservation and cross-volume creation-date limits are stated without claiming byte hashes prove metadata fidelity.
- Request identity excludes settings while prepared intents retain destinations. Partial add-with-file results preserve source/resource identities, allowing repair without duplicate capture.
- Snapshotting uses SQLite backup, allows unresolved operations, identifies excluded bytes, and requires a separate-location restore before release. Copies/clones replace hard links for independent backup.
- Export replacement, all-entry blocked reports, adoption baselines, preserved external edits and projection-aware fallback re-import have explicit boundaries.

## Task-readiness consequences

Repair the findings in governing documents before turning them into implementation tasks. Keep slice 1 as the plan declares, including bibliography import needed for adoption, portable output, copy intake and a demonstrated restore helper. The helper path tools/restore_snapshot.py appears in quickstart and must receive an explicit slice 1 task even though the installed restore CLI waits until slice 4. Include both catalog-journal and external-operation recovery tests; they are different failure domains.

No live-paper or real cross-volume result is claimed by document review. The plan correctly makes actual importer/consumer tests, representative filesystem interruption checks, and second-directory restoration implementation release gates. A passing checklist cannot substitute for those results.

## Checklist reassessment

Updated only markers CHK006 and CHK013 to unchecked and appended an assessment for every original item in requirements.md. Original item text/IDs and historical notes remain intact. Current count is 14 satisfied and 2 not satisfied; constitutional findings separately prevent readiness. Bibliography checklist reassessment belongs to the independent bibliography reviewer.


## Focused follow-up — 2026-09-21

Re-read the changed search boundary, plan, configuration, CLI recovery interface, model revision rules and specification assumptions, and rechecked copy/restore boundaries. Original findings above remain the historical initial assessment.

| Finding | Current disposition | Verified design correction |
| --- | --- | --- |
| O01 | Closed at design stage | capabilities.md now requires explicit selection through refs.search.v1, bounded read-only projection access and a runnable separately installed literal-search package, without modifying the core wheel. Configuration and plan include this in slice 1. The alternative demonstration remains an implementation acceptance obligation. |
| O02 | Closed at design stage | CLI now defines recover --catalog-state --execute separately from recover OP, with coordination, explicit writable SQLite recovery, integrity/foreign-key/schema checks and no automatic external effects. Carry the hot-journal metadata-write crash case into generated tests. |
| O03 | Closed at design stage | resources now have their own revision starting at 1; the model defines increments for locator/label/primary/filing changes, parent-source relationship changes, and the dual captured check at copy commit. Resource result schemas must expose this token and resource --if-revision must use it. |
| O04 | Closed at design stage | configuration.md now gives identical valid setup a byte/revision-preserving no-op; incompatible or incomplete destinations and changed settings conflict without overwriting catalog/config. |
| O05 | Closed at design stage | catalog_revision is a positive monotonic catalog counter; semantic-changing transactions advance it once and list/search return catalog ID plus revision. Reads/previews/no-ops do not advance it. |
| O06 | Closed | A-05/A-11 distinguish the settled no-dependency decision from implementation verification of the Latin table and overrides. |
| K01 | Still open | The Principle II sentence has not been amended; explicit authorization remains pending. No review finding or checklist mark can replace that governance step. |

Copy-only slice 1 remains explicit in plan, configuration and file contract; move still fails as unsupported until slice 2. The restore procedure explicitly forbids automatic operation resumption, identifies external file exclusions and restricts active mutation to one home controlling shared targets. No new operations-side design blocker was found in this focused follow-up. This does not certify bibliography findings or runtime behavior.

Current operations-review verdict: O01–O06 are resolved in the written design; task generation still awaits K01 and any separate bibliography-review gate. Updated requirements.md current markers to 16 of 16 satisfied and appended this follow-up without removing the earlier 14-of-16 assessment. These are specification-quality marks only. Actual search replacement, journal recovery, stale-resource writes, repeat initialization, copy interruption and restore proof must be implemented and verified by the resulting tasks.
