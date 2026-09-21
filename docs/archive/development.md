> Historical design/research, archived 2026-09-21. Current scope is in the [slice 1 specification](../../specs/001-academic-catalog/spec.md); proposals here do not add requirements.

# refs: Development and Evaluation Brief

**Historical proposal notice, 2026-09-21:** Examples and earlier defaults below are source rationale. Audit sections 11–12 and the revised [feature contracts](../../specs/001-academic-catalog/contracts/cli.md) supersede the single-home, mode/adopt, broad vocabulary and output-profile proposals. Follow the current [plan](../../specs/001-academic-catalog/plan.md) for delivery slices.


**Bibliographic standards follow-through (2026-09-20):** The [model decision](../bibliographic-model.md) and [feature mapping contract](../../specs/001-academic-catalog/contracts/bibliography.md) now define the standards profile, structured field coverage, preservation limits, and acceptance obligations. Earlier proposals below remain source rationale.
**Feature status (2026-09-20):** This document retains source rationale and earlier review proposals. Current behavior is in the [clarified academic specification](../../specs/001-academic-catalog/spec.md); implementation decisions are in its [plan](../../specs/001-academic-catalog/plan.md) and [contracts](../../specs/001-academic-catalog/contracts/cli.md). Later clarification answers supersede conflicting older defaults below.

**Status:** Initial proposal for review; no implementation or evaluation is claimed complete.
**Date:** 2026-09-20
**Product authority:** [Product Vision and Charter](../vision.md)

**Architectural input:** [Architectural Needs and Direction](architecture.md)

**First release:** [Academic MVP](academic-mvp.md), informed by [local workflow research](workflow-research.md).

## Purpose and binding inputs

Resolve the uncertainties that determine whether `refs` can deliver useful retrieval and dependable citation with a small maintainable core. Experiments should support explicit adoption, revision, or rejection decisions. A completed integration or successful model call is insufficient evidence of product fitness.

The charter establishes SQLite as the authoritative catalog, external ownership of linked files and notes, stable source and citation identities, managed vocabulary changes, replaceable capability implementations, and the division between catalog capabilities and external-agent judgment. The initial interface is a CLI with structured input/output. These are inputs to planning; changing them requires an explicit product decision.

## Current decisions and hypotheses

The first release prioritizes academic daily use, CLI/configuration behavior, key generation, normalization, and migration fidelity. QMD and Jev remain intended investigations after the first useful academic workflow. RIS is deferred from the MVP. Product scope and first-release scope are intentionally different.

| Item | Status | Decision still needed |
| --- | --- | --- |
| Jev controlled tagging | Intended experiment | Whether its accuracy, calibration, coverage, and operating characteristics justify production use. |
| Pipyer evaluation workflows | Preferred experiment orchestration | Adapter shape and complete usage/error accounting for Jev and comparison methods. |
| QMD search | Preferred candidate | Whether supported ingestion, filtering, result mapping, and retrieval quality fit the catalog. |
| Defuddle extraction | Preferred candidate | Capture quality on representative pages and handling of supplied content versus fetched HTML. |
| CSL-JSON and Pandoc | Candidate normalization/conversion tools | Preservation strategy for bibliographic fields, original imports, resource links, and unmapped data. |
| Wren and Zotero connector behavior | Reference and investigation candidate | Whether reusable designs or capture interoperability offer enough benefit for their integration cost. |

Buku and Karakeep remain useful comparisons for narrow implementation questions. Their overall workflows are not the intended product model. No implementation language, package structure, vector storage choice, or production model provider is selected by this brief.

## Modularity design and proof

Use the initial integrations to discover practical extension boundaries for search, extraction, optional summarization, and classification. Technical planning must define how implementations are selected and added, how compatibility and supported capabilities are declared, and how configuration, errors, provenance, and derived artifacts cross those boundaries. Keep catalog rules and authority outside individual providers.

Prove the extension path by adding and selecting an alternative implementation for a bounded capability without modifying or rebuilding the core application. The Jev comparison is a natural first case. Verify that both implementations can operate on the same versioned inputs, produce inspectable results, and preserve catalog data and human decisions when selection changes. Search planning must separately address engine-specific indexes, filtering, and rebuild requirements; success with a model adapter alone does not prove search-engine replaceability.

Record the extension contract and evidence in the relevant feature artifacts. Build enough abstraction to support demonstrated alternatives without requiring every capability to have several production implementations in the first release.

## Architectural input to investigations

Use [Architectural Needs and Direction](architecture.md) to connect experiments to anticipated workflows, ownership, failure modes, and extension requirements. Each investigation should report which proposed boundaries it supports, which assumptions it challenges, and what remains unresolved. Provider quality and architectural fit are separate questions; both need evidence.

The [ArjanCodes review](arjancodes-review.md) remains supporting research. Development should be guided by refs' needs and the resulting architectural reasoning. Feature plans should refine the relevant contracts and acceptance scenarios rather than adopt a named design style.

## Shared evaluation material

Start with a small representative corpus spanning scholarly records, ordinary articles, technical documentation, linked PDFs, and a few external notes. Include imperfect metadata, duplicate candidates, inaccessible pages, incomplete captures, long sources, and incidental topic mentions. Expand only when the initial sample cannot resolve a decision.

Record source identity, capture version, extraction method, and content availability. Keep personal material outside tracked fixtures unless deliberately selected for sharing; use synthetic or suitable public fixtures for reproducible repository checks.

Prepare remembered-source queries, lecture-source requests with audience/objective context, and a modest approved vocabulary. Human judgments should distinguish applicable tags from incidental mentions and useful evidence from mere topical similarity. Separate development and held-out evaluation material before tuning prompts or thresholds. Agree acceptance criteria before inspecting held-out results, and report sample limitations.

## Investigation 1: Capture and bibliographic fidelity

**Question:** Can ordinary capture and import preserve the information needed for search, external links, and accurate bibliography output?

For the academic MVP, establish the migration route and exercise BibTeX/BibLaTeX handling with corporate authors, protected capitalization, dates, identifiers, custom fields, keywords, and attachment paths. Verify the user's key-generation, Title Case normalization, title/edition conventions, and derived-versus-overridden sort-title behavior against representative records. Preserve original inputs and identify meaningful differences explicitly. Defer RIS conversion and broad web capture; later compare direct fetching with supplied HTML/Markdown and record failures or incomplete content honestly.

An exploratory local Pandoc 3.11 test already demonstrated silent loss of attachment/custom fields during conversion to CSL-JSON and loss of keywords on subsequent BibLaTeX export. This is motivation for reproducible fixtures, not a comprehensive fidelity assessment.

**Decision output:** A supported capture/import boundary, preservation and loss-reporting policy, and initial bibliography fixtures. Do not promise arbitrary lossless round-tripping.

## Investigation 2: QMD as the search component

**Question:** Can QMD provide useful retrieval behind `refs` while the catalog retains identity and ownership?

Prototype through QMD’s supported interface. Its reviewed public SDK indexes filesystem collections; generated search documents are therefore a candidate adapter. Such documents would be disposable projections of catalog content, with stable source IDs and capture versions. They would not become user-maintained records. Verify the pinned version’s actual capabilities before committing to this approach.

Check ingestion, refresh, deletion, metadata filters, source grouping, and passage mapping. Include project/tag-filtered queries whose relevant results are scarce, so filtering errors cannot hide behind broad matches. Verify that superseded or removed material does not remain visible as current evidence.

Compare lexical retrieval, hybrid retrieval, and hybrid retrieval with QMD reranking. Measure remembered-source rank, distinct useful sources for lecture requests, passage support, latency, indexing effort, and local resource requirements. An optional Jev reranking comparison should use the same candidates to isolate ranking effects.

**Decision output:** Adopt QMD with a bounded adapter, investigate a specific gap, or reject it with recorded reasons. Avoid depending on undocumented database writes or building a second search engine before establishing the limitation.

## Investigation 3: Jev and controlled tagging

**Question:** Does Jev apply the approved vocabulary accurately enough to reduce organizational work?

Use pipyer to compare Jev membership judgments with a conventional structured-output LLM and a simple similarity-to-definition baseline. Hold source content and concept definitions constant. Start with a modest vocabulary that can be evaluated directly; assess candidate-selection recall separately if shortlisting becomes necessary.

Preserve raw outputs, resolved model versions, question and taxonomy versions, content identity, latency, usage, failures, and cost or an explicit unavailable-cost marker. A Jev adapter must account for provider operations explicitly; a generic Python step should not make those costs disappear from comparison records.

Measure assignment precision, coverage, useful specificity, hierarchy errors, and repeatability. Evaluate calibration only for outputs intended as probabilities, with sample counts and uncertainty. Similarity scores are not automatically comparable probabilities. Evaluate the final acceptance policy as well as raw judgments, including abstention and survival of human corrections.

**Decision output:** Provider and assignment-policy recommendation, unsupported cases, and evidence sufficient to accept, revise, or reject automatic application. Learning that Jev is unsuitable still fulfills the experiment’s purpose.

## Development sequence and promotion

1. Specify academic MVP behavior using the workflow research: configuration, CLI, keys, normalization, migration, resource links, and export ownership.
2. Deliver the first useful academic workflow and trial it on one real paper. Use lexical search over available metadata and abstracts; establish backup/restore and fidelity evidence before whole-library cutover.
3. Add any deferred project configuration when it relieves actual daily friction. Basic collections, managed intake, and explicit reorganization are now early requirements under A2. Broad bulk consolidation and bulk renaming remain later-version possibilities.
4. Run bounded QMD and Jev investigations with representative queries, vocabulary, and agreed evaluation criteria. Promote richer capture and classification through their own feature specifications.

The first implementation plan must address interrupted operations, safe retries, conflicts, backup/export recovery, and index rebuilding at a level proportionate to a personal catalog. Detailed schemas, command contracts, and scheduling belong in that plan and its feature specification.

Use a bounded feature brief when work is ready for specification: outcome, binding inputs, open decisions, exclusions, acceptance evidence, and completion conditions. Once promoted, the feature specification owns detailed behavior; update the originating brief with status and links rather than maintaining parallel requirements. Evaluation reports preserve methods, observations, limitations, and the resulting decision. A separate backlog becomes useful only when there are enough independent candidates to manage.

## Research basis

The following sources informed the initial direction and were reviewed on 2026-09-20. They describe candidate capabilities, not guarantees about a pinned implementation. Record exact versions and reproducible inputs in subsequent investigations.

- [QMD SDK and retrieval documentation](https://github.com/tobi/qmd): integration and search candidate.
- [TypeSafe Noul](https://docs.typesafe.ai/primitives/noul), [model versions](https://docs.typesafe.ai/models), and [documented limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13): Jev experiment design.
- [Defuddle](https://github.com/kepano/defuddle): extraction candidate.
- [Pandoc bibliography handling](https://pandoc.org/MANUAL.html#specifying-bibliographic-data) and [Quarto citations](https://quarto.org/docs/authoring/citations.html): interchange and publication workflow.
- [Wren](https://github.com/thewrenapp/wren): bibliographic and capture design comparison.
- [GitHub Spec Kit](https://github.com/github/spec-kit): candidate process for translating reviewed feature intent into specifications and implementation plans.
