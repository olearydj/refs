> Historical design/research, archived 2026-09-21. Current scope is in the [slice 1 specification](../../specs/001-academic-catalog/spec.md); proposals here do not add requirements.

# Academic MVP: Scope and Behavior Priorities


**Bibliographic standards follow-through (2026-09-20):** The [model decision](../bibliographic-model.md) and [feature mapping contract](../../specs/001-academic-catalog/contracts/bibliography.md) now define the standards profile, structured field coverage, preservation limits, and acceptance obligations. Earlier proposals below remain source rationale.
**Feature status (2026-09-20):** This document retains source rationale and earlier review proposals. Current behavior is in the [clarified academic specification](../../specs/001-academic-catalog/spec.md); implementation decisions are in its [plan](../../specs/001-academic-catalog/plan.md) and [contracts](../../specs/001-academic-catalog/contracts/cli.md). Later clarification answers supersede conflicting older defaults below.

**Status:** Proposed release boundary and behavior decisions for specification; commands and configuration below are illustrative.
**Date:** 2026-09-20
**Inputs:** [Vision](../vision.md), [architecture](architecture.md), and [workflow research](workflow-research.md).

## First Useful Outcome

Review the [behavior decision sheet](../behavior-decisions.md) to settle concrete conventions before implementation. Its proposed defaults require review; existing agreed commitments remain binding.

The [configuration and CLI review draft](configuration-and-cli.md) proposes home resolution, a minimal project file, editable preferences, and the daily workflow through backup and explicit bibliography export. Review it before promoting those details into a feature specification.

Manage references for one active paper without opening Zotero: import existing references, find and correct records, access attachments, choose a project's bibliography, and export a file that builds in Quarto. Dependable metadata and comfortable daily CLI behavior take priority over additional formats or model integrations.

**Accepted initial capture path:** An external agent researches new sources and passes metadata to the CLI. This already happens when the user creates ad hoc project bibliographies; preventing those references and corrections from being lost to the reusable library is a primary motivation. Prioritize convenient structured submission, existing-record lookup, preservation of supplied provenance, and returning stable keys for writing. Built-in DOI/ISBN/arXiv/PMID lookup can wait.

## Application Home and Configuration

The user selected visible data locations /casa/refs/cat and /casa/refs/lib on 2026-09-21. Configuration stays at ~/.config/refs/config.toml and points to canonical /Volumes/Casa/refs/cat and /Volumes/Casa/refs/lib. Catalog, lock and intake staging stay outside sync; only lib may be shared. Missing/unmounted data locations fail explicitly without creating another catalog. This replaces the former single-home/XDG proposal.

The configuration contract defines explicit config and catalog overrides for testing. Project discovery cannot change catalog identity or roots. Snapshot includes config, consistent database, provenance and resource inventory; excluded external bytes are named explicitly.

Include configuration inspection and validation early: paths, effective values, their origins, and actionable errors for unknown settings. Common preferences, particularly key templates, must be editable without SQL or code changes. Changed preferences apply to future operations unless an explicit migration or normalization operation is requested.

Use the user’s credential-helper model when authenticated providers are introduced. Secretpath is a reference for configuration ergonomics, not the chosen credential dependency. Keep helper configuration in trusted user settings, resolve credentials only for operations that need them, and never store resolved secrets in the catalog or project files. Detailed helper behavior belongs in the relevant provider specification.

### Project Overrides

Prefer a small `.refs.toml` in a writing project. Initially limit it to project selection, export filename/format, and other justified project behavior. Resolve relative paths against the declaring file. Report which project file was selected; define discovery stopping rules and a way to ignore project configuration.

Key generation and normalization are catalog conventions. Project settings must not silently re-key or renormalize shared records. If project-specific aliases become necessary, specify export mappings separately from shared identity. Machine resource roots and credential configuration belong in user settings.

A minimal project file may fit the first release. If deferred, explicit project/output arguments should exercise the same operations. Avoid a large configuration inheritance system.

## Keys and Normalization

- Preserve every imported key, including historical variants that do not match the generator.
- Configure a declarative template in TOML. Use the accepted author + year + two complete words from the short title convention for new keys, excluding articles and a small configurable list of additional stopwords. The broader exclusion policy is accepted; specify the complete default list and token rendering with fixtures.
- Specify collisions, missing authors/dates, corporate authors, accents, punctuation, stopwords, and suffixes. Template changes affect new keys; metadata corrections leave existing keys stable.
- Use editor when author is missing. With neither, generate the two selected short-title words followed by year, without repeating the title fragment. Use uppercase `ND` for missing year. Collision suffixes affect only the new key; explicit overrides remain available subject to validity and uniqueness.
- Separate key components with hyphens and use lower camel case for the title fragment: `smith-2024-turingTrap`, `smith-ND-turingTrap`, or `turingTrap-ND`. Separate collision suffixes too: `smith-2024-turingTrap-a`. Existing keys are not reformatted.
- Provide a key preview before creation or explicit regeneration. Templates must not execute arbitrary Python or shell expressions.
- Use Title Case for normalized titles, preserving protected technical spelling and intentional exceptions. Define the casing policy and exception handling before selecting an implementation.
- Retain raw imports and distinguish normalization from factual correction. Preserve creator order/roles, literal corporate names, date precision, edition, short title, identifiers, and unmapped fields.
- Reimport must distinguish unchanged records, updates, conflicts, and possible duplicates. Similar titles alone do not establish identity.

Use actual records and synthetic edge cases for the behavior specification. Verify protected terms through bibliography export and Quarto rendering, not only by inspecting stored text.

### Title Variants, Editions, and Sorting

Define one documented policy for full title, subtitle, short title, edition, display labels, and attachment filenames. Keep edition information separate from the title when it is a distinct bibliographic field; compose labels or filenames using configured templates. Normalize equivalent edition expressions where unambiguous, while preserving meaningful wording such as “Revised” or “International.” Do not strip title text or merge editions on an uncertain inference. Settle exact canonical values and display rules using representative records.

Maintain a separate sort title, automatically derived from the normalized title unless manually overridden. For example, `The Art of Statistics` sorts under `Art of Statistics` while its displayed and cited title remains unchanged. Specify the full article list, language handling, punctuation, and secondary ordering; do not assume English rules apply to every language.

Track whether a sort title is derived or overridden. Recompute derived values when their source title is corrected under the active policy; retain manual overrides until explicitly cleared. A policy change should offer deliberate recalculation with preview rather than silently rewrite the catalog. Keep sorting independent of cite-key generation and identity. Include fixtures for same-title editions, leading articles, technical capitalization, and manual overrides.

## Attachments

Support multiple attachments of arbitrary type stored anywhere. Keep link-in-place available; support named roots with relative paths and absolute links where needed. Select the preferred openable resource explicitly when several candidates exist. Metadata edits and key changes do not automatically rename files.

**Updated intake requirement:** Offer moving a newly supplied attachment into a configured document library when adding a reference. Agent-collected files currently left in Downloads are at risk of being lost along with the acquisition effort. This intake operation belongs in the initial workflow; it does not bring bulk collection or bulk renaming into the MVP. Moving by default versus only on request remains unresolved. Preserve existing filenames and imported links unless separately instructed. The configured document library may remain external to the application home. Transfer verification, collision handling, and interruption recovery apply to intake as well as any later collection operation.

Include hierarchical collections distinct from projects and subject tags. A source may have several memberships, but each managed attachment has one filing collection. Files recorded by named root inside the library are managed; other files remain linked. Existing library files can receive filing assignments without movement; there is no adopt-without-move state outside the root. Collection changes offer explicit, previewed reorganization of managed files and catalog links; linked-in-place files remain untouched. Preserve filenames. Copy-only intake to Unfiled is in slice 1; collections and move arrive in slice 2.

Defer broad bulk consolidation and bulk renaming beyond the MVP; this does not defer intake or reorganization of managed files. A separately specified collection operation could gather selected or all file-backed attachments into a shared folder. The destination may be outside the application home; no per-reference folder layout is required. Deleting a catalog record must never delete its files.

Preserve existing filenames, including spaces. For explicit filename generation, use no spaces and hyphen-separated short-title, optional edition/version, and year components, such as `PracticalVim-2E-2015.pdf`. This convention does not authorize renaming existing files.

Managed intake and reorganization need preview, explicit execution, collision handling, content verification, an old-to-new path manifest, and interruption recovery. For cross-volume moves, verify the destination before removing the original. Handle HTML snapshots and companion files as a unit. Specify copy versus move and optional renaming separately.

External note links can break even when refs' own links are updated. Report that boundary and retain the relocation map; comprehensive rewriting of external notes is outside the first release. Linking and opening scattered files can ship before consolidation.

## Release Sequence

1. **Slice 1:** agent capture and bibliography ingestion, correction/search, linking/opening, project citation selection and explicit portable BibTeX export, verified copy-only intake to Unfiled, and demonstrated snapshot restoration into a second catalog.
2. **Slice 2:** collections, folder-based filing assignment without movement, explicit selected reorganize and the accepted new-download move default.
3. **Slice 3:** one verified Zotero extractor/migration route, imported child-note context and related pairs, with external archive and preserved linked files.
4. **Slice 4:** full restore tooling, optional file-inclusive backup and logical library export before whole-library cutover.

RIS, semantic search/QMD, Jev tagging, summarization, broad web capture, PDF text indexing, and general extension distribution are deferred. Keep boundaries for later capabilities without requiring all extension infrastructure now.

Bibliography export requires an explicit invocation. Do not implement watchers, idle export, or catalog-change hooks that regenerate bibliography files. Build scripts and agent skills may call the export command as an explicit workflow step. Before adopting an existing manuscript bibliography as generated output, import and reconcile its contents and make the ownership transition deliberate. Frozen bibliographies must not change because unrelated catalog metadata changed.

Backups should contain a consistent SQLite snapshot, configuration, a format/version manifest, and external-resource inventory. State whether attachment contents are included. Support a user-selected backup destination; a snapshot beside the original provides local recovery, not independent protection. Test restoration into a separate home.

## Completion Evidence and Estimate

Daily-use readiness requires preserved identities and required metadata, key/normalization fixtures, a correctly rendered active paper bibliography, accessible attachments, predictable repeat/conflict behavior, and a successful restore into a separate home. Check annotation portability on representative PDFs before declaring Zotero unnecessary for reading existing annotations.

The earlier one-to-two-week allowance remains provisional. Reduced format coverage frees time for configuration and metadata behavior; it does not establish a shorter schedule. Re-estimate after the behavior specification and migration fixtures settle. First use on one paper should precede whole-library cutover.
