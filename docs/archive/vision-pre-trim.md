> Historical version before the owner-approved slice 1 trim. Current vision is [here](../vision.md).

# refs: Product Vision and Charter

**Status:** Draft for review; describes intended behavior, not implemented capabilities.
**Date:** 2026-09-20
**Companion:** [Development and Evaluation Brief](development.md)

**Architectural input:** [Architectural Needs and Direction](architecture.md)

## Purpose

`refs` is a personal, searchable source catalog for material worth finding, using, or citing again. It should handle formal academic references well enough for research and publication while making it easy to save an ordinary web page without organizing it first.

The product promise is: **save casually, recover by meaning, select for a purpose, and cite rigorously.**

The initial tool should standardize the user’s established reference-management workflow so routine conventions do not depend on memory. Keys, title variants, editions, sorting, and attachment handling should follow explicit, inspectable policies. Those policies can evolve through configuration or focused software changes as the workflow develops.

A primary motivation is retaining references gathered by agents while writing. The user already has agents research sources and construct project-local bibliographies outside Zotero; those references and corrections can remain isolated from the reusable library. Initially, agents will obtain metadata and submit it through the CLI. refs should make catalog retention part of that workflow, with project bibliographies produced by explicit export. Built-in identifier lookup is not required for initial use.

Bibliographic information, captured web content, external PDFs, and links to personal notes should participate in one coherent catalog. A source may begin as a casually saved link and later become a lecture example or a formal citation. That progression should enrich the existing record without requiring migration between separate bookmark and bibliography systems.

## Motivation and intended user

The initial user is a researcher and instructor working with Quarto, external document folders, Markdown notes in Obsidian, and coding or research agents. Development should optimize for this concrete workflow. Wider adoption may follow, but multi-user hosting and a general consumer application are not initial requirements.

Existing tools leave an awkward gap. Full reference managers provide bibliographic rigor but bring application and workflow complexity. Bookmark managers often encourage collecting, filing, and processing as ongoing obligations. Folders of links preserve too little information for useful retrieval. Importing everything into a notes vault creates manual work and mixes collected material with developed thinking.

Saving a source should therefore be a completed action. Tags, projects, reading status, polished metadata, and personal notes must not be prerequisites. Optional context such as “why I saved this” should be easy to preserve. Missing enrichment should not create an inbox the user is expected to clear.

## Canonical workflows and questions

### Save something useful

Save a web page through a CLI, an agent, or a later lightweight capture integration. Preserve the original URL immediately, then obtain its real title, useful metadata, and clean text when possible. Also accept supplied HTML or Markdown with its source address, so an existing clipping workflow can contribute content that direct fetching cannot obtain.

A failed extraction leaves a saved record with an honest content status. A login screen or navigation page must not silently stand in for the intended article. Optional tags, context, and project associations can be added during capture or later.

### Recover something vaguely remembered

“Find that article about why students still need to learn programming even when AI can write code.”

Search must work when the remembered wording differs from the source and when the source has no useful tags. Results should identify the saved item and provide enough source text to recognize it. Exact titles, authors, phrases, citation keys, and identifiers must remain effective lookup routes alongside meaning-based retrieval.

### Find sources for a purpose

“Which of my saved sources would help with lecture X in class Y?”

An external agent can read the lecture outline, audience, and learning objectives, query the catalog, and inspect relevant passages. It then explains how a source might serve as an example, evidence, counterargument, assigned reading, or instructor background. The catalog must make that assessment possible without requiring the user to anticipate this use when saving the source.

Retrieval should expose whether evidence comes from full text, an abstract, metadata, or a linked note. A passage showing topical relevance does not by itself establish that a source is credible evidence for a claim.

### Maintain formal references

Import BibTeX/BibLaTeX and RIS records; create and correct structured bibliographic information; link existing PDFs and notes; and preserve stable citation keys. Support the source types, contributors, dates, identifiers, and publication details needed for dependable academic citation.

Import should preserve original data and make material conversion losses or ambiguities visible. Correcting an author or title must not silently change the citation key used in existing writing. Repeated imports should avoid accidental duplication and report conflicting information rather than silently replacing it.

### Assemble and use project material

Associate a source with one or more papers, courses, lectures, or other projects without duplicating its bibliographic identity. Distinguish material associated with a project from material deliberately included in its bibliography. A useful background link need not become a citation.

Export a stable, reproducible project bibliography for Quarto. The exported file should let the project build without access to the personal catalog. Recording actual use should provide another retrieval clue, such as “the source used in last fall’s lecture.” Exact association roles remain a feature-design decision.

Bibliography files are written only by an explicit export invocation. Catalog edits must never trigger background regeneration. Build scripts, agent skills, or other external automation may invoke export deliberately; refs does not watch for changes and overwrite bibliographies on its own.

### Connect sources to developed notes

Link an existing Markdown note, or let an agent create a note when the source becomes part of active thinking. Preserve the relationship in both directions where practical. Capturing a page should not automatically create a vault note, and refreshing catalog metadata must not overwrite authored prose.

## Product principles

1. **Retrieval earns the system its place.** Search should reduce dependence on filing. Classification can improve retrieval, but untagged content must remain discoverable.
2. **Bibliographic rigor is available when needed.** Casual capture accepts incomplete information; citation preparation exposes missing or uncertain bibliographic facts without inventing them.
3. **Ownership is explicit.** The catalog owns its records and captured text. External PDFs and notes remain under their existing owners’ control.
4. **Evidence and interpretation remain distinguishable.** Preserve source-provided information, personal context, and model-generated enrichment with their origins. An inference must not silently become a source fact.
5. **Automation operates within defined authority.** Models may retrieve, score, or classify through bounded capabilities. Catalog rules control accepted changes.
6. **Agent access is a first-class interface.** Structured inputs and outputs, explicit failures, predictable selection, safe retries, and inspectable changes matter as much as readable terminal output.
7. **The library remains recoverable.** Stable identities, preservation of imports, usable exports, and documented ownership should allow migration without losing project associations or resource links.
8. **Capabilities are replaceable and comparable.** Search, extraction, summarization, tag classification, and similar capabilities should support selectable implementations and new extensions without changing or rebuilding the core application. The catalog and its rules remain stable while tools and models evolve.

## Modularity and experimentation

The user should be able to choose a capability implementation, compare alternatives on the same saved material, and add a compatible implementation through a documented extension boundary. This is an enduring product requirement: experimentation must remain practical after the first provider or search engine has been selected.

Each implementation should expose its supported capabilities and preserve enough provenance to identify the tool or model, configuration, and source version behind its results. Different search engines or classifiers need not produce identical scores or support identical features; unsupported operations and differences that affect comparison must be explicit. Changing implementations must preserve source identities, original content, project associations, and human corrections. Derived indexes or enrichments may need rebuilding or regeneration, with that work made visible.

Summarization is an optional enrichment capability within this model. Generated summaries should remain attributable and distinct from source text and authored notes. They may assist retrieval and inspection without replacing the evidence on which a citation or recommendation depends.

The extension mechanism, packaging, and compatibility contracts belong in technical planning. The requirement does not imply hot-swapping a running process or installing every alternative by default; selecting or adding an implementation may require configuration, dependency installation, or a restart.

## Essential concepts and ownership

| Concept | Meaning |
| --- | --- |
| Source | The stable catalog identity of something saved for future reference. It can accumulate metadata, captures, links, and uses. |
| Bibliographic record | Structured facts used to describe and cite a source; completeness depends on the source and intended use. |
| Capture | A dated representation obtained from a source, including extracted text and information about its origin and completeness. |
| Linked resource | An external PDF, note, or other resource associated with a source without transferring ownership. |
| Collection | Hierarchical library organization, separate from projects and subject tags. A source may have multiple memberships; one filing collection determines each managed attachment's placement. |
| Project association | A relationship between a source and a particular activity, with bibliography inclusion deliberately distinguished from general membership. |
| Approved concept | A defined subject tag with stable identity, a hierarchical position, and enough scope guidance to support consistent assignment. |
| Assignment | A manual or automatic association between a source and an approved concept, including its origin and relevant evaluation context. |

| Component | Responsibility |
| --- | --- |
| `refs` | Catalog identity, metadata, captures, resource links, project associations, vocabulary rules, search access, and bibliography exports. |
| Search component | Derived indexes and retrieval results that remain traceable to catalog sources and captures. Indexes can be rebuilt. |
| Model providers | Bounded predictions such as embeddings, relevance judgments, or membership in approved concepts. |
| External agent | User goals, lecture or project context, investigation, interpretation, and explanations of suitability grounded in retrieved evidence. |
| External document folders | Original PDFs and other linked documents. Removing a catalog entry must not delete them. |
| Obsidian or another editor | Authored notes and developed prose. The catalog records links and may support explicit export or note-creation workflows. |

One source may have several representations, such as a publisher page, a PDF, and a personal note. Their relationship should be expressible without collapsing distinct publications or versions merely because their titles resemble one another. Exact identity and merge rules belong in feature specifications.

## Controlled classification

Hierarchical tags such as `prog/python/packaging` should represent approved concepts with definitions, aliases where useful, and inclusion or exclusion guidance. Imported keywords can be retained as source metadata without automatically expanding the approved vocabulary.

Applying an existing concept and changing the vocabulary are separate operations. Automatic assignment may run under an approved policy. Creating, renaming, merging, or reorganizing concepts requires explicit authorization. Stable concept identities should survive changes to names or paths.

Classification should identify substantial subject matter, permit multiple applicable concepts, and abstain when none fits. A tag limit is a ceiling rather than a quota. Specific assignments can imply broader membership through the hierarchy; the user should not need to attach every ancestor manually. Explicit human corrections must survive subsequent automatic classification.

Model scores, acceptance policy, and human confirmation remain distinguishable. Confidence claims must be evaluated on representative material before they determine unattended assignment. Uncertain results may remain unassigned without creating mandatory review work.

## Scope and established constraints

The intended product includes bibliographic import and export, web-content capture, external resource links, project associations, lexical and semantic retrieval, and managed classification. A CLI with a reliable structured interface is the initial access surface. Capture convenience matters, but the mechanism for browser or share integration is unresolved.

SQLite is the authoritative catalog. Plain-text interchange files, generated search documents, and bibliographies may exist as supporting artifacts. Existing document folders must not be reorganized or copied into a mandatory per-reference directory structure. Resource-link portability across different local folder roots must be considered in the linking design. Attachments of any type may remain scattered; an explicit optional operation may collect them into a shared folder with verified transfers, collision handling, and a relocation record. Ordinary catalog operations must not move files implicitly.

Common preferences, including key-generation templates, should be easily editable. Configuration and catalog data should have a discoverable, backup-friendly home, with scoped project overrides and explicit migration procedures. Normalized bibliographic titles use Title Case while preserving technical spelling and deliberate exceptions; original imported values remain available. These commitments are refined for the first release in the [academic MVP brief](academic-mvp.md).

Support linked-in-place resources and explicitly managed placement under a document-library root. Existing links can be adopted into managed placement without an immediate move. Collection changes permit previewed, explicit reorganization of managed files and catalog links, preserving filenames; they do not automatically move linked-in-place files. Report external-link impacts rather than promise automatic repair. Bulk renaming remains later work.

Standardize full titles, short titles, subtitles, and edition information so the user need not remember formatting conventions. Derive a separate sort title automatically under a configurable policy, such as ignoring a leading “The,” and allow a manual override. Sorting must not alter the displayed or cited title. Preserve meaningful differences between editions and variants when identifying sources.

The initial scope excludes an integrated PDF reader or annotation editor, a note editor, a full Zotero replacement, word-processor plugins, multi-user synchronization, autonomous knowledge organization, and unrestricted two-way vault synchronization. There is no required folder taxonomy, reading queue, or processing ritual. These boundaries protect the intended daily workflow; additions require a concrete need and an explicit product decision.

## Success and development posture

`refs` succeeds when the user can save mixed material with little organizational effort, reliably recover remembered sources, discover useful lecture or research material with supporting passages, and produce dependable bibliographies. Trust also depends on truthful capture status, preserved external files, stable references, and recoverable catalog data.

Evaluation should use a messy, representative personal corpus rather than only curated examples. Measure remembered-source rank, usefulness and diversity of suggested sources, citation fidelity, classification precision and coverage, and operational effort. Numerical acceptance thresholds should be established in the relevant evaluation or feature specification before judging results; none has yet been approved.

Trying Jev is an intentional learning objective. Adopting it in production remains contingent on evidence. QMD is a preferred search candidate, not an established dependency. Wren is a useful reference for bibliographic modeling and capture interoperability, without adopting its broader application scope. The [development brief](development.md) owns these investigations and their current sequence.

This charter governs product intent and boundaries. Feature specifications refine behavior; technical plans select implementations; evaluation reports document observations. If evidence calls a product commitment into question, revise it explicitly rather than allowing implementation to redefine it silently. Update this document when scope, ownership, or success commitments change, and link detailed decisions instead of duplicating their implementation history.
