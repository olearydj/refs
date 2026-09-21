# refs Design Notes

**Current stage:** The [academic catalog specification](../specs/001-academic-catalog/spec.md) has completed its first clarification pass, and the [technical plan](../specs/001-academic-catalog/plan.md), research, data model, contracts, and validation guide are ready for review. Tasks and application implementation have not started. Earlier commands and architecture proposals in this source packet are historical input; the feature contracts contain current planning selections.

**Readiness:** Review the [plan](../specs/001-academic-catalog/plan.md) and [CLI contract](../specs/001-academic-catalog/contracts/cli.md), including the revised [bibliographic profile](../specs/001-academic-catalog/contracts/bibliography.md), then use `$speckit-tasks`. [Research](../specs/001-academic-catalog/research.md) records selected dependencies, alternatives, and limitations. The [local dependency audit](../specs/001-academic-catalog/dependency-audit.md) records sibling-project evidence and the Typer/pathlib conventions. The [specification checklist](../specs/001-academic-catalog/checklists/requirements.md) records requirements quality, not implementation completion.

## Start Here

| Document | Purpose |
| --- | --- |
| [Vision](vision.md) | Product intent, ownership, scope, and enduring needs. |
| [Academic MVP](academic-mvp.md) | Proposed first useful release, focused on leaving Zotero for daily academic work. |
| [Behavior decisions](behavior-decisions.md) | Accepted naming/title conventions, agent-supplied capture (C1), collections and managed placement (A2), alongside unresolved proposals. |
| [Configuration and CLI](configuration-and-cli.md) | Proposed settings and an illustrative everyday walkthrough. |
| [Loose requirements](requirements-review.md) | Open choices, overlooked needs, deferred requirements, and evidence gaps. |

## Supporting Material

| Document | Purpose |
| --- | --- |
| [Bibliographic model and standards](bibliographic-model.md) | Recovered model intent, standards comparison, selected profile rationale, and links to exact coverage/mapping contracts. |
| [Architectural needs](architecture.md) | Anticipated variation, ownership boundaries, and architectural consequences. |
| [Workflow research](workflow-research.md) | Observations from local applications, Zotero, publications, notes, and session history; includes limitations. |
| [Development and evaluation brief](development.md) | Earlier proposed investigation sequence, including QMD and Jev; input to later planning. |
| [ArjanCodes review](arjancodes-review.md) | Supporting design research, not a prescribed programming philosophy. |

## Reading Status Correctly

### Latest Scope Decisions

- Agents obtain new-source metadata and submit it through the CLI. Retaining references, corrections, and collected PDFs beyond an individual writing project is a primary motivation. Built-in identifier lookup is deferred.
- Collections are hierarchical library organization, distinct from projects and subject tags. A source may have multiple memberships; each managed attachment has one filing collection.
- Files may remain linked in place or use managed placement. New-file intake can move a file into the document library. Existing links can be adopted without an immediate move.
- Reorganization of managed attachments is explicit and previewed, updates catalog paths, and preserves filenames. Ordinary membership changes do not move files. External note links may still need attention.
- Basic collections, managed intake, and reorganization are early requirements. Broad bulk consolidation and bulk renaming remain deferred. A2 refines A1's earlier blanket deferral of collection operations.

### Open Choices for the Next Stage

Five answers are recorded in the feature spec: new downloads move into the document library by default; unfiled intake uses `Unfiled`; conflict-free imports proceed while conflicts are retained; explicit export replaces adopted unchanged bibliographies while outside edits conflict; generated name tokens use deterministic transliteration with overrides and package evaluation. Remaining mapping, matching, configuration, and detailed naming defaults are concrete reviewable planning selections in the contracts. Select a real paper and representative migration sample before live trials; schema, annotation, recovery, and rendered-citation fidelity remain acceptance work. See [loose requirements](requirements-review.md) for historical rationale.

### Local Spec Kit State

The `.specify/` scripts/templates and `.agents/skills/speckit-*` workflows are present. [Constitution v1.0.0](../.specify/memory/constitution.md) was established on 2026-09-20. The active feature is `specs/001-academic-catalog`, recorded in `.specify/feature.json`; its specification, built-in quality checklist, technical plan, research, data model, seven contracts, a bibliographic coverage inventory, and quickstart guide exist. No tasks or application implementation exists. The project is not yet a Git repository; repository initialization remains separate setup work, and the feature directory does not depend on a branch name.

Continue from the active specification, constitution, and accepted decisions. Keep the first feature bounded around the academic catalog workflow; use the vision and architecture as constraints without pulling deferred search/classification experiments into the first release. Detailed behavior belongs in the feature specification as it is reviewed; the documents below remain its source rationale and historical review material.

### Authority

Explicit user decisions take precedence over proposals. Accepted items are recorded in the behavior decision sheet; illustrative commands and configuration do not become accepted merely because they appear in a document. The loose-requirements document indexes gaps rather than establishing a second detailed contract.

The user's subsequent constitution, specification, clarification, and planning requests authorized the current stage. Earlier stop-before-specification instructions in the source packet describe the previous discussion. Task generation, implementation, and live migration remain subsequent work.
