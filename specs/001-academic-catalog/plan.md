# Implementation Plan: Academic Catalog Workflow

**Branch**: No Git branch exists. Spec Kit resolves the feature label `001-academic-catalog` from `.specify/feature.json`.

**Date**: 2026-09-20 | **Spec**: [Academic Catalog Workflow](spec.md)

**Input**: Clarified feature specification and the documents catalogued in [docs/README.md](../../docs/README.md).

**Status**: Phase 0 research and Phase 1 design revised after the bibliographic standards review. Application code, dependency lock, tasks, and live migration are not produced by this planning pass.

## Summary

Deliver one installed local CLI that retains agent-supplied references, reconciles existing sources, preserves keys and files, searches metadata, selects project citations, and explicitly exports reliable bibliographies. Newly downloaded attachments move into the configured document library by default, using `Unfiled` when needed. Import applies conflict-free entries and retains conflicts. Adopted bibliography outputs can be replaced by explicit export while outside edits require reconciliation or overwrite.

Use Python 3.14, a versioned bibliographic profile grounded in published Zotero/CSL/BibLaTeX vocabularies, boundary libraries, and SQLite as the authority. Keep normalized data, raw imports, revision checks, and operation outcomes in the catalog. Filesystem changes use explicit durable recovery states. Search is a replaceable read-only capability over a catalog-owned projection. [Research](research.md) records decisions and alternatives; the [local dependency audit](dependency-audit.md) grounds package and filesystem API choices in current sibling projects; [contracts](contracts/cli.md) define executable behavior without requiring an agent to know storage details.

## Technical Context

**Language/Version**: Python 3.14; `requires-python = ">=3.14,<3.15"` for the initial certified runtime. Broaden support only after the same contract and recovery checks pass.

**Primary Dependencies**: Typer `>=0.27,<0.28`; Pydantic `>=2.13,<3`; bibtexparser `==2.0.1`; pylatexenc `~=2.10` for explicitly used TeX text/group parsing; Unidecode `==1.4.0`. Standard library handles SQLite, TOML reads, hashing, file locks, paths, archives represented as directories, and entry-point discovery. Use `pathlib.Path` for paths and supported file operations, including `destination.hardlink_to(staged)`; retain descriptor-level os operations and fcntl for durability and locking. Schemas are pinned packaged inputs; no runtime schema download. bibtexparser is a provisional syntax adapter whose semantic suitability must pass the profile fixtures. No runtime model/network dependency. Use uv, the `uv_build>=0.12.1,<0.13` build backend, and a portable three-day dependency cooldown; exact resolutions are created during implementation.

**Storage**: One local `catalog.sqlite`, with relational identities/relationships, validated JSON metadata, original input BLOBs, and a rebuildable FTS5 projection. `config.toml` owns preferences; SQLite records applied policy provenance and export adoption state. No second authoritative preference database. Recovery bundle and full library export formats are distinct.

**Testing**: pytest and pytest-cov for unit, CLI-contract, and integration cases; subprocess tests for concurrent processes and interruption; Ruff and ty for static checks. Synthetic/public fixtures cover parsing and normalization; a user-selected local corpus and real manuscript are later release gates. Compare installed-command behavior, not only direct function calls.

**Target Platform**: macOS and Linux on tested local filesystems with advisory locking, fsync, atomic replacement, no-overwrite hard-link publication, and SQLite FTS5. Links may reference other storage; managed transfer must fail safely if its required filesystem primitives or metadata fidelity are unavailable. Windows, network-hosted catalogs, and actively synchronized live database files are outside initial certification.

**Project Type**: Single distributable Python CLI package; application functions are callable independently of terminal formatting. No daemon or public network service.

**Performance Goals**: At 10,000 sources and 30,000 resource links, warmed metadata search/list p95 ≤1 second over 100 fixed queries on the recorded reference machine. Measure installed-command startup separately. Report transfer progress in bytes with no universal transfer deadline. These are engineering targets introduced by this plan, not measured results.

**Constraints**: Five-second bounded database/coordination-lock wait; structured noninteractive failures; stable assigned keys; preservation of source input; explicit exports; no file move caused by membership edits; preserve verified bytes across process interruption. External content must remain stable during the final transfer/export publication window. Stronger protection against arbitrary simultaneous editors is not promised by portable filesystem primitives.

**Scale/Scope**: One personal catalog and up to four concurrent CLI processes; first practical trial on one paper and at least 30 representative records. All six user stories and FR-001–FR-049 are covered by design obligations; adapter and citation fidelity remain unexecuted gates. Whole-library cutover requires later fidelity and restore evidence.

## Constitution Check

Pre-research review found no exception necessary: the feature retains catalog authority, explicit ownership, agent-accessible operations, replaceability, and measurable acceptance. The post-design check below evaluates the concrete design, not unexecuted test results.

| Principle | Pre-research gate | Post-design result and required evidence |
| --- | --- | --- |
| I. Preserve Identity and Evidence | PASS | Stable IDs/keys, original artifacts, field provenance, explicit conflicts, and rebuildable search are defined in [data model](data-model.md). Verify reimport, edits, and full export. |
| II. Make Ownership and Effects Explicit | PASS | Managed/linked modes, reserved `Unfiled`, explicit reorganization, and destination-specific bibliography adoption are defined in [file operations](contracts/files-and-recovery.md). Verify interruption and outside-edit cases. |
| III. Provide Predictable Agent Operations | PASS | Versioned input/output envelopes, precise patch rules, retry identities, finite lock waits, and local-only daily operations are defined in [CLI](contracts/cli.md) and [records](contracts/records.md). |
| IV. Keep Capabilities Replaceable | PASS | Read-only search projection and versioned entry-point boundary have an external replacement proof in [capabilities](contracts/capabilities.md). Deferred model capabilities are not prerequisites. |
| V. Establish Trust Through Evidence | PASS | [Quickstart](quickstart.md) and coverage below define representative fidelity, installed CLI, recovery, and real-paper validation. Research observations are explicitly limited. |

No constitutional waiver is used. Filesystem guarantees cover refs-induced failures on supported stable local inputs, not destruction of storage or concurrent writers outside the coordination protocol. Transliteration is presented as a reproducible key transformation with overrides, not authoritative romanization.

## Project Structure

### Documentation (this feature)

```text
specs/001-academic-catalog/
├── spec.md
├── plan.md
├── research.md
├── dependency-audit.md
├── data-model.md
├── quickstart.md
├── checklists/requirements.md
└── contracts/
    ├── cli.md
    ├── records.md
    ├── bibliography.md
    ├── bibliographic-coverage.json
    ├── configuration.md
    ├── interchange.md
    ├── files-and-recovery.md
    └── capabilities.md
```

`tasks.md` is produced later by `$speckit-tasks`.

### Source Code (repository root)

The following is the planned layout; these files are created during implementation.

```text
pyproject.toml
uv.lock
src/refs/
├── __init__.py
├── cli.py
├── models.py
├── config.py
├── catalog.py
├── normalization.py
├── search.py
├── operations.py
├── files.py
├── bibliography.py
├── recovery.py
├── migrations/
└── adapters/
    ├── bibtex.py
    ├── zotero.py
    └── search_sqlite.py
tests/
├── unit/
├── contract/
├── integration/
└── fixtures/
    ├── public/
    └── search_plugin/
```

**Structure Decision**: Start with small modules organized by actual responsibility. CLI parsing calls application operations; those enforce policy using catalog and file helpers. Adapters translate external representations into refs-owned models. Pure key/title functions are ordinary functions. No generic repository hierarchy or one class per operation is prescribed. The search interface is justified by an enduring replacement requirement; its proof plugin is a fixture, not a shipped second search service.

## Delivery Sequence and Validation Coverage

This is a design sequence, not the task list. Implement foundation/configuration and boundary models first, then capture/search, bibliography output, import/reconciliation, managed files, and recovery. Each user story has an independently runnable fixture; full daily-use release includes all six. Do not postpone recovery design until after destructive operations are built.

| Requirement group | Owning design | Acceptance evidence |
| --- | --- | --- |
| FR-001–FR-012 | Records, normalization, data model | Key/title/edition fixtures, raw preservation, explicit overrides; SC-002/SC-004. |
| FR-013–FR-017 | CLI, capabilities, config | Structured subprocess commands, stale edits, exact lookup, filters, offline use; SC-001/SC-005/SC-009. |
| FR-018–FR-024 | Interchange and import state | Repeated and mixed-conflict batches, malformed blocks, snapshot schema checks; SC-002/SC-003. |
| FR-025–FR-035 | Resource model and recovery protocol | Link/adopt/intake/reorganize/remove, collision and crash cases; SC-007. |
| FR-036–FR-039 | Project relationships and export protocol | Citation membership, rendering, outside edits and adoption, interruption; SC-006. |
| FR-040–FR-042 | Recovery bundle and full export | Separate-home restore, corruption rejection, complete relationships/raw inputs; SC-008. |
| FR-043–FR-046 | Configuration contract | Resolution origins, invalid preferences, setup, project isolation; SC-009. |
| FR-047–FR-049 | Bibliographic profile, coverage registry, supporting records | Vocabulary coverage, B01–B15 plus supporting/inheritance cases; SC-010. |

**Release gates**: All specification correctness outcomes pass; the bibliographic vocabulary has no unaccounted entries, and every claimed target mapping passes structured edit/export and rendering fixtures; package normalization fixtures are fixed; the installed CLI passes contract checks; interruption cases preserve data; a supported Zotero/BBT snapshot schema is certified; a separate-home restore succeeds; the chosen paper renders correctly. The user must select/authorize the live paper and sample before external migration, moves, or bibliography adoption. No package or migration fidelity is inferred merely from successful installation or parsing.

**Documentation authority**: The clarified spec owns behavior. This plan resolves its stated technical follow-ups and carries remaining product defaults into concrete contracts as reviewable planning selections. Future changes to behavior must update the spec explicitly. Earlier walkthrough syntax and batch policies remain historical input, not a competing contract.

## Complexity Tracking

No constitutional violations. The operation journal is necessary because file publication and SQLite commits are separate; a plain move cannot provide recovery. The search entry point is necessary to demonstrate compatible replacement without core edits. All other deferred provider infrastructure remains absent.
