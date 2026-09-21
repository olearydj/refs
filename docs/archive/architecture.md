> Historical design/research, archived 2026-09-21. Current scope is in the [slice 1 specification](../../specs/001-academic-catalog/spec.md); proposals here do not add requirements.

# refs: Architectural Needs and Direction


**Bibliographic standards follow-through (2026-09-20):** The [model decision](../bibliographic-model.md) and [feature mapping contract](../../specs/001-academic-catalog/contracts/bibliography.md) now define the standards profile, structured field coverage, preservation limits, and acceptance obligations. Earlier proposals below remain source rationale.
**Feature status (2026-09-20):** This document retains source rationale and earlier review proposals. Current behavior is in the [clarified academic specification](../../specs/001-academic-catalog/spec.md); implementation decisions are in its [plan](../../specs/001-academic-catalog/plan.md) and [contracts](../../specs/001-academic-catalog/contracts/cli.md). Later clarification answers supersede conflicting older defaults below.

**Status:** Working design input; proposed boundaries and unresolved choices, not an implementation specification.
**Date:** 2026-09-20
**Product authority:** [Product Vision and Charter](../vision.md)
**Investigation plan:** [Development and Evaluation Brief](development.md)

## Purpose and authority

Make anticipated needs and their architectural consequences explicit before detailed design. The aim is to explain what must remain stable, what should be replaceable, where correctness belongs, and which uncertainties need evidence. This brief gives feature specifications and technical plans a starting point while leaving room to revise proposed boundaries through implementation experience.

The vision owns product commitments. This document owns the current architectural reasoning across features. The development brief owns investigation sequence and evaluation work; feature specifications own detailed behavior, and technical plans own concrete contracts and implementation decisions. Record significant later decisions with their rationale and link them here rather than maintaining competing descriptions.

The [ArjanCodes review](arjancodes-review.md) is supporting research on design tradeoffs. Requirements, operating constraints, and observed behavior should determine the architecture. No implementation language, plugin framework, service topology, or model provider is selected here.

## Needs and architectural implications

| Anticipated need | Architectural implication | Evidence needed during design |
| --- | --- | --- |
| Save casual links and maintain formal references in one catalog | Stable source identity must be independent of metadata completeness, capture format, and citation readiness. | Enrich a saved link into a citable record without replacing its identity or losing associations. |
| Preserve a useful save when extraction or enrichment fails | Persist the source independently of optional work; represent partial completion and failures explicitly. | Interrupt capture, retry it, and recover one recognizable source with truthful status. |
| Retrieve by remembered wording and by meaning | Retain exact lookup and lexical retrieval alongside semantic capabilities; return source evidence through an application-owned result contract. | Run representative queries, including untagged sources, and inspect passages and content availability. |
| Compare and replace search tools, classifiers, and summarizers | Separate capability contracts, provider selection, and implementation details. Permit multiple configured instances in one run. | Compare alternatives on the same versioned inputs and add a compatible extension without changing the core. |
| Trust automatic classification without uncontrolled vocabulary growth | Predictions and catalog mutations need separate authority. Mandatory validation and human decisions belong to catalog logic. | Reject unknown concepts and stale results; preserve corrections through reclassification. |
| Keep SQLite authoritative while allowing specialized indexes | Search data and generated documents are rebuildable projections with explicit freshness and identity mapping. | Refresh and delete sources, rebuild an index, and verify that obsolete content is not presented as current. |
| Support agents, scripts, and a later lightweight capture surface | Reuse application operations behind interfaces; keep domain behavior independent of terminal formatting or transport. | Exercise the same operation with structured input and a non-CLI caller without duplicating rules. |
| Keep external PDFs and notes in existing locations | Store links and root mappings without transferring ownership; make indexing external content an explicit policy. | Remove a catalog association without touching a file, and resolve links after a root mapping changes. |
| Produce reliable project bibliographies and preserve imports | Separate original import material, normalized facts, and generated exports; make citation membership explicit. | Check fidelity fixtures and reproduce an export from an unchanged catalog selection. |
| Remain a manageable personal tool | Prefer a small local application with bounded optional dependencies; justify additional processes by concrete integration or operational needs. | Basic catalog operations work without starting model or search runtimes they do not use. |

## Proposed responsibility boundaries

These are logical responsibilities, not a prescribed directory tree or set of services.

**Catalog and policy.** Own source identities, bibliographic facts, captures, resource links, project associations, vocabulary, and accepted assignments. Enforce invariants regardless of the caller or provider. Stable citation keys, authorized vocabulary changes, human corrections, and ownership rules cannot depend on a model behaving correctly.

**Application workflows.** Coordinate operations such as capture, import, search, classify, and export. Decide when catalog changes commit, which work can fail independently, and how results or failures are reported. Keep workflows understandable without requiring a general workflow engine.

**Capability implementations.** Perform extraction, retrieval, classification, optional summarization, and conversion through bounded contracts. Translate vendor-specific inputs, responses, and errors at this boundary. A provider supplies a result or proposal; the workflow validates and applies it through catalog operations. Avoid handing every provider unrestricted catalog access as its integration API.

**Persistence and derived artifacts.** Maintain the authoritative SQLite catalog and manage versioned changes. Index adapters own their derived representations and rebuild lifecycle. Technical design must identify a transaction boundary for each catalog mutation; network operations and external indexes cannot be assumed to participate in that transaction.

**Interfaces and composition.** Parse CLI or structured requests, construct configured dependencies, invoke workflows, and render results. Provider discovery and selection happen here or through a dedicated extension facility. An external agent uses these operations and supplies purpose-specific judgment; it does not need to know storage internals.

Domain rules and application contracts should not import a particular search engine or model SDK. Adapters depend on those contracts. Simple internal behavior can remain ordinary functions; introduce interfaces where they support an actual variation or isolate an external dependency. Objects are useful for coherent state, resource lifetimes, and invariants. Additional layering needs a concrete reason.

## Modularity beyond an interface

Separate three questions: what a capability promises, how an implementation is configured and selected, and how a new implementation is installed and discovered. An injected object proves only part of the requirement. Packaging, compatibility checks, duplicate names, dependency conflicts, and load failures remain design work.

Use capability-specific contracts. A search implementation may own indexing, embeddings, retrieval, and reranking as an integrated system. Do not force those stages apart until an experiment needs an independently replaceable stage and a supported boundary exists. Likewise, classification and summarization need not share a generic text-generation interface. Preserve distinctions such as probability versus similarity, supported filters, content limits, and available provenance.

Each boundary should specify inputs, output meaning, unsupported operations, failure behavior, resource lifecycle, and provenance. Where implementations differ materially, declare capabilities or reject the request explicitly. Do not hide a missing feature behind a successful but weaker result.

External packages, subprocess adapters, and local services are possible extension mechanisms. Choose among them after examining candidate runtime requirements and installation costs. Adding a compatible implementation may require installation or restart; unrestricted hot loading is not a requirement. Compatibility guarantees and contract evolution need definition before external extensions are treated as stable.

## State, evidence, and recovery

Distinguish source material, normalized metadata, human contributions, generated enrichment, and disposable indexes. Record enough input identity, tool/model version, configuration, and capture context to explain a result and compare runs. Exact storage representation and retention policies remain open; provenance does not require retaining every intermediate forever.

Long-running work must not overwrite a newer decision. Classification and enrichment should identify the input versions they used and be checked against current catalog state before application. Search results must resolve to a source and the representation that supplied the evidence, with a way to distinguish historical or incomplete material.

Saving, enriching, and indexing may complete at different times. Design visible operation states, safe retries, and reconciliation for interrupted work. Start with the smallest execution mechanism that supports these needs; a persistent queue or background daemon requires its own justification. Specify concurrency, deduplication, and stale-write behavior before allowing unattended mutations.

Recovery must cover catalog metadata, captures, links, vocabulary, assignments, and associations. Search indexes can be rebuilt. A backup of links alone does not back up externally owned files. Export and restore procedures should make that ownership boundary explicit.

Managed placement adds an explicit ownership distinction: refs records linked-in-place files without relocating them, while managed attachments have a filing collection and may be reorganized on request. Collection membership, physical placement, and filename policy are separate concerns. Multiple memberships cannot determine multiple physical destinations for one file. Reorganization must coordinate filesystem changes with catalog links and recovery; external note links remain outside that atomic boundary. Bulk renaming is deferred.

## Questions for deeper design

The [academic MVP brief](academic-mvp.md) proposes a consolidated application home, editable TOML preferences, scoped project overrides, Title Case normalization, and optional attachment collection based on [local workflow evidence](workflow-research.md). These refine the questions below without selecting schemas or a plugin framework. Attachment relocation crosses filesystem and catalog boundaries: it needs an explicit plan and recovery record because a SQLite transaction cannot atomically move arbitrary external files.

| Question | What should decide it |
| --- | --- |
| Which language and runtime arrangement? | Maintainability, CLI distribution, candidate SDKs, model runtimes, and extension installation. |
| Which exact source, capture, and revision model? | Import fidelity, duplicate handling, stale-result checks, evidence references, and storage cost. |
| Which search boundary and projection format? | The QMD investigation, required filtering, stable passage mapping, deletion, and rebuild behavior. |
| Which extension packaging mechanism? | A second real implementation, compatibility needs, dependency isolation, and user installation effort. |
| Which work is synchronous or resumable? | Capture latency, provider failures, interruption recovery, and expected parallel agent use. |
| How are provider calls and private content controlled? | Explicit configuration of remote processing, evaluation scope, credentials, and inspectable usage/cost. |
| Which catalog operations must be atomic? | Concrete import, merge, assignment, and project-update workflows, including conflicts and retries. |

## Architectural acceptance scenarios

Use these scenarios to challenge proposed designs before treating them as settled:

1. Save a URL while extraction fails; retry successfully without losing personal context or creating an unintended duplicate.
2. Run Jev and another classifier on the same capture and vocabulary versions, retain distinguishable results, and apply a policy without erasing a human rejection.
3. Add a compatible provider through the documented extension path without modifying core application code; report an incompatible provider clearly.
4. Replace or rebuild a search index while preserving catalog identities, project filters, and inspectable evidence references.
5. Edit a source while enrichment is running; prevent the older result from silently overwriting newer state.
6. Import a bibliography, associate selected sources with a project, and produce a usable Quarto bibliography while optional model services are unavailable.
7. Restore the authoritative catalog and rebuild derived search data; identify unavailable external resources without changing or deleting them.

These scenarios guide feature-level acceptance criteria. They are not a requirement to build every subsystem before the first useful slice. Revise proposed boundaries when experiments expose a simpler design or a missing contract, and record the reason.
