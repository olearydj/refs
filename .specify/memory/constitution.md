<!--
Sync Impact Report
Version change: 1.0.0 → 2.0.0 (MAJOR: an ownership obligation in Principle II is redefined; delivery timing in Principles IV and V is changed).
Authority: explicit owner authorization on 2026-09-21. The owner was shown three numbered items (1: Git baseline; 2: this Principle II wording; 3: keep the internal search boundary in slice 1 and move the entry point and proof package to "when a second implementation is evaluated", folded into the same 2.0.0 amendment) and replied "proceed with 1-3". Principle II follows the owner's A2 decision "B: Derive mode from location (Recommended)" recorded in audit section 11.
Modified principles:
- II: the sentence about adopting an existing link without an immediate move is replaced by the root-based ownership rule. The authoring session's draft said other files "MUST remain linked and untouched"; that was narrowed because it would have forbidden the owner's chosen move intake from outside the library.
- IV: capabilities sit behind application-owned documented boundaries from first delivery; selectable implementations, and adding one without modifying or rebuilding the core, are required when a second implementation is evaluated.
- V: the replacement demonstration is required when a second implementation is evaluated, not at first delivery.
Added or removed sections: none. Ratification date retained.
Dependent artifacts to synchronize (not done by this edit): plan.md "Constitution review" and "Structure" (search entry point and proof package leave slice 1; the internal search boundary stays); contracts/capabilities.md; spec, data-model, file and configuration contracts that still describe Principle II as a pending conflict; reviews/2026-09-21-revision-summary.md and proposed-principle-ii-amendment.md status; docs/README.md current-stage paragraph.
-->

# refs Constitution

## Core Principles

### I. Preserve Identity and Evidence

SQLite MUST remain the authoritative catalog. Source identities, assigned citation keys, project associations, and explicit human corrections MUST survive metadata edits, preference changes, reimports, and provider replacement. Imports MUST preserve original input and expose material conversion losses, ambiguities, and conflicts. Similar titles alone MUST NOT authorize merging distinct sources or editions.

Source information, normalized metadata, personal contributions, and generated enrichment MUST remain distinguishable by origin. Missing facts MUST NOT be invented. Retrieval MUST identify the source representation behind its evidence and its availability or completeness; complete metadata MUST NOT imply full-text review or support for a claim. Derived indexes MUST remain rebuildable without becoming a second authority. These rules protect both existing writing and future reuse.

### II. Make Ownership and Effects Explicit

Linked-in-place files and authored notes MUST remain under their owners' control. Removing a catalog entry or relationship MUST NOT delete external files; metadata updates MUST NOT overwrite authored prose or rename attachments. Collection membership, project association, citation selection, and physical placement MUST remain distinct. Each managed attachment MUST have one filing collection, even when its source has several collection memberships.

Managed intake MUST follow an explicit, inspectable intake policy. Managed reorganization MUST be previewed and explicitly invoked; membership edits MUST NOT move files automatically. Transfers MUST preserve filenames unless renaming is separately requested, prevent destructive collisions, verify the destination before removing an original, and support recovery from interruption. Catalog links MUST be updated and external-link impacts reported. Files recorded under the configured library root MUST be treated as managed. Files elsewhere MUST remain linked; refs MUST NOT move, rename, or delete them except through an explicitly invoked intake. Assigning filing collections to files already in the library MUST NOT move them.

Bibliographies MUST be written only on explicit export invocation, including deliberate calls by external automation. Catalog changes MUST NOT trigger regeneration. Unchanged selected catalog data and export configuration MUST produce reproducible output usable by the manuscript without access to the catalog. These boundaries preserve control over files and published work.

### III. Provide Predictable Agent Operations

The CLI MUST support documented structured inputs and outputs as well as readable human output. Operations MUST return stable identities and usable citation keys where applicable, expose actionable failures and conflicts, and make changes inspectable. Agents MUST be able to capture and correct metadata through supported operations without manipulating SQLite directly. Supplied provenance and context MUST remain available beyond a writing session.

Catalog invariants MUST apply regardless of caller or provider. Mutations MUST define validation, commit boundaries, retry behavior, and interruption handling; stale or conflicting work MUST NOT silently replace newer decisions. Naming and normalization policies MUST be configurable and inspectable, with explicit overrides preserved. Basic academic operations MUST work without model services, semantic indexes, or credentials. Goal-directed research and interpretation remain the external agent's responsibility.

### IV. Keep Capabilities Replaceable

Search, extraction, classification, summarization, and similar capabilities MUST sit behind application-owned, documented boundaries from their first delivery. Selectable implementations, and adding a compatible implementation without modifying or rebuilding the core application, MUST be provided when a second implementation of that capability is evaluated. Replacement MUST preserve catalog identities, original material, relationships, and human decisions; required index rebuilds or enrichment regeneration MUST be visible.

Capability contracts MUST expose unsupported operations, meaningful differences, failures, and enough input, configuration, and tool provenance to compare results. Catalog policy MUST retain authority over accepted changes. Model predictions and imported keywords MUST NOT silently expand approved vocabulary; vocabulary changes require explicit authorization, and human classification corrections MUST survive automation. Linking private content MUST NOT itself authorize sending it to a remote provider. Interfaces and dependencies MUST address demonstrated variation or a concrete workflow need.

### V. Establish Trust Through Evidence

Feature acceptance MUST use representative records and realistic failure cases. Import and export claims MUST be supported by fidelity checks, including preserved keys, meaningful bibliographic fields, and rendered citation output; successful parsing alone is insufficient. Trusted daily use MUST demonstrate a real paper workflow and restoration into a separate location before whole-library cutover. Recovery procedures MUST identify authoritative data, configuration, and external-resource responsibilities; a backup of links MUST NOT be represented as a backup of their files.

Provider adoption MUST follow a bounded evaluation with criteria set before judging results. Comparisons MUST use identifiable inputs, disclose limitations, and distinguish retrieval or classification scores from verified evidence. Replacement claims MUST be demonstrated with an alternative implementation when a second implementation of that capability is evaluated. Verification MUST be proportionate to the affected behavior and risks; a successful integration alone does not establish product fitness.

## Product Boundaries

refs is a personal source catalog for research, teaching, and writing. Saving MUST accept incomplete metadata without requiring tags, project membership, reading status, or authored notes. Untagged sources MUST remain discoverable. Citation preparation MUST expose missing or uncertain information. The first useful workflow centers on agent-supplied metadata, academic retrieval and correction, attachment access and managed intake, collections, project citation selection, and explicit Quarto bibliography export.

Feature scope MUST follow the [docs index](../../docs/README.md), [vision](../../docs/vision.md), and [accepted behavior decisions](../../docs/behavior-decisions.md). A2 governs current collection and managed-placement scope where older research still describes A1's deferral. Deferred capabilities MUST enter through a bounded feature decision rather than become prerequisites for the academic workflow. No implementation language, provider, plugin framework, exact CLI syntax, or configuration precedence is selected by this constitution.

## Development and Review

Specifications MUST translate accepted outcomes into testable behavior and resolve relevant open choices from the [requirements review](../../docs/requirements-review.md). Proposed defaults, illustrative commands, historical observations, and template examples MUST NOT acquire authority merely through repetition. Detailed title/key conventions belong in accepted decisions and their eventual feature contracts; technical plans select implementations and explain consequential tradeoffs.

Each feature plan MUST identify applicable constitutional principles, affected ownership boundaries, acceptance evidence, and recovery requirements. Implementation review MUST check those commitments and record unresolved limitations before declaring completion. Additional layers, services, or dependencies MUST have a concrete justification. Research uses external catalogs and linked resources read-only unless an explicit task authorizes a change. Reproducible fixtures MUST use synthetic or suitable public material unless private material is deliberately authorized for inclusion.

## Governance

This constitution governs enduring development commitments. Explicit user decisions take precedence; conflicting product commitments MUST be reconciled through an explicit amendment rather than silently reinterpreted. The vision owns product intent, accepted decisions record conventions, feature specifications own detailed behavior, and plans own implementation choices. Runtime project guidance is in [AGENTS.md](../../AGENTS.md); supporting research remains evidence with stated limitations.

Amendments MUST state the change, rationale, affected principles, and any migration or documentation consequences, and MUST have explicit user authorization. Update the version and amendment date and review dependent feature artifacts for conflicts. Use MAJOR for incompatible principle removals or redefinitions, MINOR for added principles or materially expanded guidance, and PATCH for clarifications without changed obligations. Preserve the original ratification date. Review every feature plan and implementation change for compliance; exceptions require a recorded user decision and an amendment when they alter an enduring commitment.

**Version**: 2.0.0 | **Ratified**: 2026-09-20 | **Last Amended**: 2026-09-21
