# Feature Specification: Academic Catalog Workflow

**Feature Branch**: None; this workspace has no Git repository or branch hook.

**Feature Directory**: `specs/001-academic-catalog`

**Created**: 2026-09-20

**Status**: Revised design, 2026-09-21 — nine audit-session decisions incorporated; independent review and constitution reconciliation precede task generation. Slice boundaries are explicit in plan.md.

**Input**: User description: "continue with $speckit-specify based on the files described in docs/README.md"

## Clarifications

### Provenance of the 2026-09-20 clarification

These are separate records of the earlier questions, literal replies from this conversation, and resulting interpretations. The prose previously presented as answers was assistant-written. The audit's section 10 corrects that attribution. Full option text is not reconstructed here from memory; these question descriptions preserve the earlier spec record.

| Recorded question | Literal reply | Interpretation, not a quotation |
| --- | --- | --- |
| Default action for newly downloaded files | `b` | Move by default; later delivery is slice 2. This reply did not approve the copy mode from the unselected option. Slice 1 copy intake now has separate authority in audit section 11. |
| Destination without a filing choice | `a` | Use Unfiled; filing changes do not themselves move files. |
| Mixed import conflicts | `a` | Apply conflict-free entries and retain conflicts. |
| Replacement of an adopted bibliography | `b` | Explicit export replaces unchanged adopted output; outside edits conflict. |
| Accented/non-Latin names in keys | `a - use a library / package if something small and proven exists and is beneficial. seems like this could be more problematic than it seems on face` | Evaluate deterministic handling with overrides. The later Latin-only policy supersedes the broad transliteration proposal. |

### Decisions recorded on 2026-09-21

[Audit sections 11 and 12](reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) are the authoritative question/options/literal-reply/interpretation record. The table below links the decisions to their requirements; it does not quote the auditor's consequences as user speech.

| Decision | Literal reply | Consequences interpreted in this specification |
| --- | --- | --- |
| Breadth | “A: What I use (Recommended)” | CSL-shaped authority, justified extensions, optional native label, verbatim per-entry originals; FR-047–049. |
| Notes | “B: Fold into context (Recommended)” | Child notes become imported searchable context; no annotation/outline subsystem; FR-023/049. |
| Unknown export mappings | “A: Block, with override (Recommended)” | Four classes, scoped waivers and single-run unknown override; FR-039/048. |
| First slice | “B: Core + copy-only intake (Recommended)” | Capture-to-export, copy into Unfiled, demonstrated snapshot restore; move/collections later. |
| A2 ownership | “B: Derive mode from location (Recommended)” | Root-based ownership, no stored mode or adopt command; FR-030–032. |
| Title case | “A, with a clarification. APA etc should govern exported material. My prefs for internal representation do not superceed that. I just don't want to see sentence case titles in the database. They are an abomination.” | Internal Title Case; per-title terms and whole-title flag; citation style governs output; FR-008/037. |
| Profile | “A: Portable default, richer by declaration (Recommended)” | Portable BibTeX only in slice 1; richer profiles deferred; FR-037/039. |
| Transliteration | “C: No dependency (Recommended)” | Unicode normalization plus explicit Latin table; otherwise key-author override; FR-007. |
| Locations | “A, but /casa/refs/cat and /casa/refs/lib” | Separate visible data folders and config; FR-043/044, A-04. The complete earlier location clarification is quoted in audit section 12. |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retain and Recover Research References (Priority: P1)

A researcher and their agent save source metadata and corrections in a reusable catalog, find earlier work, and obtain stable keys for writing. A source remains useful even if it is never cited in the current project.

**Why this priority**: References and corrections currently retained only in individual manuscript bibliographies must survive beyond those projects.

**Independent Test**: Starting with an empty catalog, submit several references, correct one, search for them, and retrieve their keys and provenance without a manuscript, imported library, or model service.

**Acceptance Scenarios**:

1. **Given** supplied bibliographic metadata with its origin, **When** an agent saves it, **Then** the source is retained with a persistent identity and citation key, and the response identifies whether it was created, already present, or requires reconciliation.
2. **Given** a source with only a recognizable title or original address, **When** it is saved without tags, a project, an attachment, or complete citation metadata, **Then** it remains retrievable and missing citation information is visible without invented facts.
3. **Given** existing records, **When** the user searches by an exact key or identifier, or words in titles, creators, abstracts, or retained context, **Then** matching records are returned with recognizable descriptions and the origin of matching content.
4. **Given** an assigned key and an explicit sort-title override, **When** a title or generation preference changes, **Then** the assigned key and override remain unchanged, and derived values are distinguished from deliberate overrides.
5. **Given** a record changed since an agent read it, **When** the agent submits an update based on that older state, **Then** the update reports a conflict and does not silently replace the newer values.
6. **Given** missing creators, dates, protected technical spelling, or colliding generated keys, **When** new keys and normalized metadata are previewed and saved, **Then** the accepted conventions and draft normalization rules apply, existing keys remain intact, and the response returns the actual allocated key. Latin creator names use the supported deterministic policy; non-Latin names require an explicit key-author override, while preserving original names; unsupported input requests an override, and distinct names yielding the same token remain distinct sources.
7. **Given** sources shared across collections and projects, **When** a list is filtered by collection, project membership, or citation selection and ordered by sort title, **Then** only matching sources appear in the specified order, with displayed titles unchanged. Collection filtering is delivered in slice 2.

---

### User Story 2 - Use a Catalog Bibliography in One Paper (Priority: P1)

A researcher associates sources with a paper, explicitly selects its citations, and exports a bibliography that the paper can use independently of the personal catalog.

**Why this priority**: An actual manuscript establishes the first useful academic outcome and validates preservation through citation output.

**Independent Test**: With a small prepared catalog and manuscript, select citations, export, and render the manuscript with the catalog unavailable.

**Acceptance Scenarios**:

1. **Given** a project containing both background sources and selected citations, **When** its bibliography is exported, **Then** only selected citations are included, each once, with their assigned keys.
2. **Given** one source used by two projects, **When** a citation is unselected in one project, **Then** that project's background association remains and the other project's selection is unchanged.
3. **Given** a previously exported bibliography, **When** catalog metadata or project membership changes, **Then** the bibliography remains untouched until another explicit export invocation.
4. **Given** an existing manuscript bibliography not yet adopted as refs-generated output, **When** an export targets it, **Then** its existing contents must be reconciled and adoption explicitly authorized before replacement. For an adopted file unchanged outside refs since its last export, a later explicit export may replace it without another overwrite option; outside edits instead produce a conflict requiring reconciliation or explicit overwrite.
5. **Given** unchanged selected records and export preferences, **When** export is repeated, **Then** output is identical and the manuscript renders its citations without access to the catalog.
6. **Given** incomplete citation metadata or an interrupted export, **When** export is attempted, **Then** missing optional facts produce visible warnings, unusable output is rejected without fabricated values, and an existing bibliography is not left truncated.

---

### User Story 3 - Bring Existing References Across Safely (Priority: P2)

The researcher imports a representative Zotero sample and existing project bibliographies, preserving the references, corrections, collection memberships, and attachment links already in use.

**Why this priority**: Daily use must build on existing work, and Zotero alone may not contain corrections or sources retained in manuscript bibliographies.

**Independent Test**: Import preserved sample inputs into a separate catalog, compare the result with the originals, repeat the import, and reconcile a conflicting project entry without changing the source library.

**Acceptance Scenarios**:

1. **Given** sample records with pinned keys, multiple creator roles, collections, several attachment types, and custom fields, **When** an import is previewed, **Then** preserved values, proposed normalization, unsupported data, unresolved links, and conflicts are itemized without changing the input or catalog.
2. **Given** a reviewed conflict-free import, **When** it is applied and repeated unchanged, **Then** keys, required metadata, relationships, and link paths are preserved and the repeat creates no additional sources or relationships.
3. **Given** a manuscript entry that disagrees with an imported source or later human correction, **When** it is reconciled, **Then** competing values and their origins are visible and the user can retain or explicitly replace individual values.
4. **Given** different sources sharing a key, conflicting identifiers, similar titles, or distinct editions, **When** they are imported, **Then** they are not silently merged, overwritten, or re-keyed; unresolved records remain unapplied and explain the needed decision.
5. **Given** a mixed batch with an unresolved conflict, **When** import is applied, **Then** conflict-free references are imported immediately, conflicting entries remain unapplied with their original data and reasons retained, and the report distinguishes imported, unchanged, and unresolved entries. Resolving or retrying the remainder does not duplicate already imported references.
6. **Given** notes, annotations, snapshots, or unmapped fields beyond current editing capabilities, **When** migration is assessed, **Then** their preservation and usability are reported separately; successful metadata import does not claim complete annotation or snapshot compatibility.

---

### User Story 4 - Keep and Organize Research Files (Priority: P2)

The researcher links existing files where they are, brings newly acquired files into a document library when requested, and reorganizes managed attachments explicitly as collections evolve.

**Why this priority**: Collected PDFs must not remain stranded in temporary locations, while existing file organization and external note links need protection.

**Independent Test**: Use disposable files to link one in place, move one into a managed collection, assign multiple memberships, reorganize it, and recover from an interrupted transfer.

**Acceptance Scenarios**:

1. **Given** existing files with spaces in their names and multiple attachments for one source, **When** they are linked, inspected, or selected for opening, **Then** their names and contents are unchanged and ambiguous opening choices return resource identities for explicit selection.
2. **Given** a newly downloaded file and a configured document library, **When** the file is added without an intake override, **Then** managed move is the default, its action and destination are visible before execution, the destination file is verified before the original is removed, its name is preserved, and the resulting catalog link is reported. This scenario applies from slice 2. Slice 1 offers explicit copy-only intake and linking.
3. **Given** a source with memberships in two collections, **When** one is assigned as an attachment's filing collection, **Then** it has one managed destination; adding or removing ordinary memberships does not move the file.
4. **Given** files already recorded beneath the library root, **When** filing collections are assigned from their current folders, **Then** only catalog assignments change; files outside the library remain linked and untouched.
5. **Given** a renamed or relocated collection hierarchy, **When** managed reorganization is previewed and invoked, **Then** affected files and old-to-new paths are reported, names are preserved, catalog links are updated, and potential external-link breakage is disclosed.
6. **Given** a destination collision, unavailable root, permission failure, or interrupted move, **When** intake or reorganization runs, **Then** no different file is overwritten, at least one verified complete copy is retained, and the operation reports enough state to recover or retry without claiming false completion.
7. **Given** a catalog source or relationship, **When** it is removed, **Then** external attachments and authored notes remain untouched; dependent catalog relationships are shown before a source removal.
8. **Given** supplied short title, edition/version, and year, **When** a filename is explicitly generated, **Then** the accepted forms such as `PracticalVim-2E-2015.pdf` and `ZeroToSold-v1.2.4-2020.pdf` are produced, while linking or transferring an existing file preserves its name unless renaming is separately requested.
9. **Given** a newly downloaded file and no selected filing collection, **When** it is added using managed intake, **Then** it is placed in the document library's `Unfiled` folder without requiring a collection choice; later filing reassignment leaves it there until explicit reorganization.

---

### User Story 5 - Recover the Library and Leave the Tool (Priority: P2)

The researcher can identify what must be backed up, restore the catalog elsewhere, and recover its information in a documented form without depending on the application indefinitely.

**Why this priority**: A reusable personal library is only trustworthy when it can survive mistakes, machine changes, and eventual replacement.

**Independent Test**: Create a recovery snapshot and full library export from a prepared catalog, restore into an empty location, and compare records, keys, associations, and resource inventories.

**Acceptance Scenarios**:

1. **Given** a catalog with preferences, sources, imports, and relationships, **When** a backup is made, **Then** it represents a consistent recoverable state and identifies which durable material is included and which external file contents need separate protection.
2. **Given** a supported backup and an empty restore destination, **When** restoration completes, **Then** identities, keys, metadata, provenance, collection and project relationships, overrides, and resource links match the saved state.
3. **Given** a different machine or missing external root, **When** resources are checked after restoration, **Then** unresolved paths are reported without moving or deleting files; changing a root mapping resolves links without changing source identities.
4. **Given** an incompatible backup, nonempty destination, or interrupted restoration, **When** restoration is attempted, **Then** existing data is preserved and an incomplete restore is not reported as ready for use.
5. **Given** a populated library, **When** full library export is invoked, **Then** metadata, original import material, provenance, relationships, preferences, and resource references are available in a documented structured form, with file-content inclusion stated explicitly.

---

### User Story 6 - Inspect and Control Everyday Preferences (Priority: P2)

The researcher configures naming, resource locations, and project export defaults, and can understand what settings and catalog are active before making changes.

**Why this priority**: Predictable conventions and visible configuration prevent routine work from depending on remembered settings or hidden project context.

**Independent Test**: With two sample project directories and user preferences, inspect effective settings, change an allowed project default, and exercise invalid configuration without importing a real library.

**Acceptance Scenarios**:

1. **Given** a new or existing application home, **When** setup or configuration inspection runs, **Then** resolved paths and effective values are visible; repeated setup preserves existing data and preferences.
2. **Given** user preferences, permitted project defaults, and invocation choices, **When** effective configuration is inspected, **Then** each value's origin and the selected project file are reported with the draft precedence rules applied.
3. **Given** an invalid setting or a project attempt to change catalog identity, resource roots, or naming conventions, **When** an operation runs, **Then** the offending setting and source are reported before any mutation.
4. **Given** changed naming preferences, **When** another source is created, **Then** the new preference applies to that operation while earlier keys, filenames, and explicit overrides remain intact.
5. **Given** no provider configuration, **When** the researcher requests local help, capture, search, editing, linking, export, or backup, **Then** these operations require no external model service or credentials.

### Edge Cases

- Missing author and editor, missing or partial dates, one eligible title word, no eligible title words, corporate creators, accented or non-Latin names, acronyms, apostrophes, and existing unconventional keys follow FR-006 through FR-011; unsupported transformation requires an explicit override rather than invented metadata. Supported accent removal and name transliteration follow the documented policy, preserve original spelling, and treat token collisions separately from source identity.
- Two simultaneous submissions producing the same key receive distinct valid keys or an actionable conflict; replay of an identified completed operation does not create a second source (FR-003, FR-007, FR-014).
- A book edition, a preprint, a published article, and a supplement remain distinct when evidence does not establish identical source identity; same-key/different-identifier and same-identifier/conflicting-key imports require reconciliation (FR-020).
- Empty search results, absent abstracts, and ambiguous resource selection return explicit empty or choice results without fetching content, guessing a file, or demanding tags (FR-015, FR-016, FR-027).
- Empty citation selection exports an explicitly reported empty bibliography under the same replacement rules; duplicate selections do not duplicate output, and invalid citation identifiers block usable export (FR-036 through FR-039).
- A collection cycle, duplicate sibling name, deletion of an in-use collection, or an attachment whose filing collection is removed is rejected until its affected memberships and filing assignment are explicitly resolved (FR-029, FR-030).
- A managed attachment with no chosen filing collection is placed in the document library's `Unfiled` folder; unsafe or colliding collection-folder names require an explicit mapping. A linked file can remain outside every managed root (FR-025, FR-031).
- Existing same-name files, cross-volume moves, read-only locations, source changes during transfer, and HTML snapshots with companion files require preservation and recoverable status. These cases cannot be treated as a completed move based only on a new pathname (FR-033, FR-034).
- Broken links and unavailable external notes remain recorded with visible diagnostics. Catalog removal, backup, and restore do not imply permission to repair or rewrite external content (FR-026, FR-035, FR-042).
- Missing application homes, unknown settings, unsupported input types, interrupted exports, and stale edits fail explicitly without silently initializing, falling back to another catalog, or claiming success (FR-013, FR-017, FR-039, FR-044 through FR-046).

## Requirements *(mandatory)*

### Bibliographic semantic scope

The first release models the bibliographic vocabulary the user uses, rather than all of Zotero. Use one CSL-shaped authority for shared facts, type-scoped aliases, an optional validated native type label, and a short list of extensions justified by needs and fixtures. Every imported entry remains verbatim evidence. The semantic review must precede collapse of divergent paths; an approximate crosswalk does not establish equivalence.

Ingestion, editable usability, indexing, export and preservation are separate guarantees. Unsupported facts remain visible and promotable from originals without re-import. Deliberately cleared or type-incompatible modeled values can never be resurrected from those originals. Child notes become searchable imported context; attachment outlines and annotation rows are excluded from import and retained in an external dated Zotero archive. Related items are simple asserted pairs. Public CSL-JSON and Zotero API JSON outputs remain backlog items.

The plan declares four delivery slices. Slice 1 is capture-to-portable-export with linked resources, verified copy-only intake into Unfiled, and a demonstrated snapshot restore into a second catalog location. This is not a claim that the complete migration and organization feature ships in slice 1.

### Functional Requirements

#### Capture, identity, and conventions

- **FR-001**: The system MUST let a researcher or agent create, inspect, and explicitly correct structured source metadata, preserving supplied origin and personal context independently of project citation use. Saving requires a recognizable title, original address, or explicit container-and-part identification, but not tags, projects, files, or complete citation metadata.
- **FR-002**: The system MUST preserve source type, ordered creators and roles, literal corporate names, title variants, dates at supplied precision, numbered edition and version distinctions, identifiers, publication details, abstracts, historical tags, and resource references when supplied. Unknown fields MUST remain recoverable with their original input and any limits on editing or export disclosed.
- **FR-003**: Every saved source MUST have a stable identity and unique usable citation key. A creation or reconciliation result MUST identify created, unchanged, updated, or conflicted outcomes and return the actual retained or allocated identity and key. Retrying an explicitly identified completed submission MUST NOT create a duplicate.
- **FR-004**: Assigned keys and existing filenames MUST remain unchanged by metadata edits, imports, preference changes, and ordinary organization. Explicit replacement of a key MUST preview the old and new values, enforce uniqueness, and warn that external citations are not rewritten.
- **FR-005**: The system MUST distinguish original imported values, derived values, explicit overrides, and supplied or generated claims by origin. It MUST NOT infer that complete bibliographic metadata means a source was read or that it supports a manuscript claim.
- **FR-006**: New generated keys MUST use a lowercase author token, publication year, and two complete eligible words from the maintained short title in lower camel case, separated by hyphens. Use the first author, falling back to the first editor; with neither, use the title fragment followed by year without repetition. Use uppercase `ND` for missing year. One eligible title word is sufficient. Examples include `smith-2024-turingTrap`, `smith-ND-turingTrap`, and `turingTrap-ND`.
- **FR-007**: Key generation MUST use deterministic built-in Unicode normalization plus an explicit versioned table for non-decomposing Latin letters. Unsupported letters or non-Latin names MUST request a key-author override, never a guessed romanization. Preserve original names and assigned keys. Keep configurable stopwords, explicit key/author overrides and transactionally allocated collision suffixes; token collisions MUST NOT merge sources. AnyAscii with a strict refs filter is a future fallback, not a slice 1 dependency.
- **FR-008**: Stored and displayed English titles MUST be plain Unicode Title Case, with per-title protected terms and a whole-title preserve-case flag. Seed protection from imported case-protection braces, not braces solely enclosing accents or commands. Preserve originals and explicit exceptions. Citation styles MUST govern exported material. Non-English titles MUST retain spelling and have an export language declaration; unprotected mid-title capitals warn without blocking.
- **FR-009**: Supplied short titles MUST be preserved. When absent, use an explicitly known main title, otherwise the full title; do not split a colon or invent an abbreviation merely to generate a short title. Explicit short-title overrides MUST remain editable and MUST NOT re-key an existing source.
- **FR-010**: Ordinary numbered editions MUST retain a numeric meaning and support the accepted display and filename forms, such as `2nd ed.` and `2E`. Version labels, variants, and ambiguous historical shorthand MUST remain distinguishable; uncertain values such as `P1E` or `5E` MUST NOT be silently reinterpreted.
- **FR-011**: Title sorting MUST ignore a leading whole-word English `A`, `An`, or `The` while preserving displayed and cited text. Explicit sort-title overrides MUST persist until cleared. Policy-driven recomputation MUST preview changes and preserve overrides. Draft secondary ordering is in A-06.
- **FR-012**: Explicit filename generation MUST support the accepted no-spaces short-title, optional edition/version, and year convention, including `PracticalVim-2E-2015.pdf`, without making it a mandatory rename rule for existing files.

#### Agent access, retrieval, and mutation safety

- **FR-013**: All ordinary operations MUST be accessible through documented command-line interactions with readable and structured results, actionable errors, and offline examples. Structured interactions MUST return needed choices or conflicts without interactive prompts or unrelated progress text in the result.
- **FR-014**: Changes MUST validate before application and report their scope and outcome. Previews MUST make no persistent changes. Stale edits MUST be rejected without replacing newer data. Interrupted operations and retries MUST identify applied, unapplied, or recovery-needed work instead of reporting false success.
- **FR-015**: Users MUST be able to retrieve records by exact key or identifier and lexical searches across titles, creators, abstracts, and retained context, including legacy tags. Results MUST expose source identity, key, recognizable description, and matching context; untagged records MUST remain searchable.
- **FR-016**: Users MUST be able to list and filter sources by collection, project association, and explicit citation selection, and inspect sort-title order. Results MUST state whether matching evidence comes from metadata, abstracts, or personal context and MUST NOT imply linked PDF contents were searched.
- **FR-017**: Local help, configuration inspection, capture, editing, retrieval, import, resource management, export, and recovery MUST work without model services or provider credentials. Read-only operations MUST NOT create a catalog or mutate records.

#### Import and reconciliation

- **FR-018**: The feature MUST provide one verified one-time Zotero extraction route and support bibliographic imports needed by the trial manuscript. Slice 1 accepts agent CSL-shaped input and BibTeX/BibLaTeX entries; Zotero extraction/migration is slice 3. Preserve per-entry originals and leave external catalogs, manuscripts and attachments unchanged.
- **FR-019**: Import preview MUST identify preserved keys and fields, proposed normalization, unsupported data, duplicate candidates, unresolved paths, and conflicts before application. Unsupported source types MUST be reported without silent coercion into another type.
- **FR-020**: Identity reconciliation MUST use explicit catalog/origin identity or consistent identifiers as evidence. Title similarity alone MUST NOT merge records. Conflicting identifiers, incompatible editions or versions, and identical keys on distinct sources MUST require explicit reconciliation, preserving both inputs. Draft matching order and batch behavior are in A-03.
- **FR-021**: Repeat import of unchanged recognized input MUST leave source and relationship counts unchanged. Incoming differences MUST remain inspectable and MUST NOT overwrite corrections or deliberate clearing. An unchanged documented refs export fallback MUST re-import without a type conflict when stored projection evidence identifies that source and emitted facts. Citation-key equality alone MUST NOT establish this evidence; changed values follow ordinary reconciliation.
- **FR-022**: Import MUST retain collections as collections, historical keywords as metadata, and external attachment links in place. It MUST NOT infer projects or citation selections from collection membership or promote keywords into approved taxonomy.
- **FR-023**: Migration MUST preview child notes as imported searchable context, preserve related-item assertions as pairs, and report excluded attachment outlines and annotation rows. A dated Zotero data-directory archive outside the catalog MUST preserve the excluded material. Do not claim annotation rendering fidelity from embedded presence or counts.
- **FR-024**: An import containing conflicting entries MUST apply conflict-free references immediately and retain conflicting entries unapplied with their original data and conflict reasons for later reconciliation. The result MUST distinguish imported, unchanged, unresolved, and failed entries and account for every input entry; partial completion MUST NOT be reported as complete success. Retrying or resolving remaining entries MUST NOT duplicate previously applied sources or relationships. An interruption MUST preserve applied work and identify unapplied or recovery-needed entries.

#### Resources and collections

- **FR-025**: Sources MUST support multiple labeled attachments of arbitrary type, linked through absolute paths or configured named roots. Linking MUST preserve filenames, including spaces, without requiring a common folder layout.
- **FR-026**: Users MUST be able to inspect resource paths and availability, change root mappings, and unlink resources. Missing roots or files MUST remain visible without automatic relocation or deletion.
- **FR-027**: Users MUST be able to choose a primary resource and explicitly select another for opening. With no primary, one linked resource may be opened automatically; multiple resources MUST return labeled choices rather than guess. Opening MUST use an external application and MUST NOT modify the file.
- **FR-028**: Hierarchical collections MUST be distinct from projects and tags and support creation, inspection, membership changes, renaming, and parent changes. A source may have multiple memberships.
- **FR-029**: Collection hierarchy changes MUST reject cycles and duplicate sibling names. Deleting a collection with children, memberships, or filing assignments MUST require explicit resolution of those dependents; it MUST NOT delete sources or files.
- **FR-030**: Every managed attachment MUST have one effective filing collection, defaulting to Unfiled. Filing assignments and ordinary memberships MUST NOT move files. Root-based ownership replaces a stored mode flag; a library file cannot become linked merely to bypass filing checks. Removing an in-use filing membership requires reassignment.
- **FR-031**: Slice 1 MUST offer explicit non-destructive verified copy into the library Unfiled folder, plus link-in-place. Slice 2 MUST deliver the accepted move default for new downloads with visible destinations and copy/link overrides. No slice 1 command may silently substitute move. Unusable destinations MUST retain the original and report failure. Existing imported files MUST remain in place.
- **FR-032**: A file recorded by named root and relative path beneath the configured library root MUST be managed; any other file is linked and MUST NOT be relocated by refs. There MUST NOT be a stored mode flag or managed-but-elsewhere state. Existing library files MUST support previewed bulk filing assignment from their current folders without moving them. Reorganize MUST remain explicit, selected and previewed.
- **FR-033**: Managed transfers MUST prevent overwriting a different existing file, verify destination contents before removing an original, detect a source changed during transfer, and retain old-to-new paths and completion state for recovery. Failure MUST preserve at least one complete verified copy and MUST NOT leave a successful catalog link to a missing destination.
- **FR-034**: Recognized multi-file resources, such as a saved HTML page and its companion directory, MUST be handled as a unit. If that unit cannot be determined or transferred safely, the operation MUST preserve it in place and report that limitation. Potential broken external links MUST be reported without rewriting authored notes.
- **FR-035**: Removing a project association, citation selection, resource link, or catalog source MUST be distinct actions. Source removal MUST preview affected catalog relationships and require explicit execution; it MUST NOT delete attachment files, rewrite notes, or change previously exported bibliographies.

#### Project bibliographies

- **FR-036**: Users MUST be able to create and inspect projects, associate sources, separately select citations, and remove those associations or selections. Citation selection implies project association; unselecting a citation retains membership, while removing membership with a selected citation requires explicit removal of both. Duplicate association or selection MUST be a no-op.
- **FR-037**: Bibliography export MUST include each explicitly selected source once with its assigned key, preserve citation-relevant creator semantics and protected capitalization, and remain reproducible for unchanged selected data and preferences. The output MUST be usable independently of the catalog.
- **FR-038**: Only an explicit export invocation MUST write a bibliography, including invocations by external scripts or agents. Catalog edits and membership changes MUST NOT export automatically. Existing output MUST follow A-07's adoption and external-edit protection policy. An explicit export MUST be sufficient to replace an adopted file unchanged outside refs since its last export; external edits MUST produce a conflict requiring reconciliation or explicit overwrite.
- **FR-039**: Export MUST report all affected entries before publication using four classes: faithful incomplete metadata warns; documented fallback warns and is recorded; enumerated meaning-changing loss blocks unless waived for that loss, source revision and destination profile; unknown mappings block unless explicitly overridden for that run and reported. Invalid/unserializable or case-insensitively duplicate keys always block portable output. A blocked export MUST write no file and leave existing output untouched. Empty selection MUST be reported explicitly.

#### Recovery and configuration

- **FR-040**: Backup MUST preserve a consistent catalog, configuration, originals, provenance, relationships and resource inventory, including unresolved operation state. It MUST state file-content exclusions and format version. Slice 1 MUST demonstrate restoration of its snapshot into a second catalog location and successful opening. Independent copies or filesystem clones, never hard links, are required when file contents are included.
- **FR-041**: Restoration MUST validate compatibility and use an empty destination, preserve saved identities and relationships, and report incomplete or failed restoration. It MUST NOT overwrite an existing catalog or claim that restoration of links proves external file contents are protected.
- **FR-042**: Full library export MUST provide documented structured metadata, original input material, provenance, preferences, collections, projects, citation selections, overrides, and resource references usable for migration away from refs. Excluded external contents MUST be listed. This is separate from a project bibliography and from backup restoration.
- **FR-043**: Users MUST inspect separate configuration, catalog and resource-root locations and preference origins. Configuration remains at ~/.config/refs/config.toml; the chosen data locations are /casa/refs/cat and /casa/refs/lib, represented canonically as /Volumes/Casa/refs/cat and /Volumes/Casa/refs/lib. The live catalog and staging MUST remain outside any synced folder.
- **FR-044**: Initialization MUST be explicit and repeatable without overwriting data or preferences. An unavailable chosen catalog path, including an unmounted volume, MUST fail without creating another catalog. Unwritable catalog diagnostics MUST name the resolved path and required agent access. Setup must distinguish configuration from data and state backup responsibilities.
- **FR-045**: Scoped project defaults MUST support project selection and export destination/format, with a way to disable discovery or select a file explicitly. Projects MUST NOT select a different global catalog, change global naming policies, define resource roots, or introduce credential helpers. Draft resolution rules are in A-04.
- **FR-046**: Unknown or invalid preferences MUST report the value and its origin before mutations. Preference changes MUST affect future operations; existing keys, names, and manual overrides MUST remain intact until a separate explicit operation is invoked.

#### Bibliographic coverage and mapping accountability

- **FR-047**: The documented demand-driven profile MUST supply one validated editable path per modeled fact. Alias mappings MUST specify input type scope, transformation, conflicts, target representation and fixture obligation. Native type is optional from slice 1. Unmodeled fields MUST remain verbatim original evidence with visible limitations and no competing mutable copy.
- **FR-048**: Mapping reports MUST separate ingestion, usability, indexing, export and preservation. Known portable type downgrades are documented fallbacks, not unknown mappings. The blocking-loss list MUST explicitly enumerate changes to cited authors, issued dates, work identity and in-text citation behavior. Waivers MUST lapse when the particular loss, source revision or destination profile changes; unknown overrides are single-run only.
- **FR-049**: Zotero migration MUST fold previewed child notes into source context with import provenance and retain related-item pairs, including unresolved endpoints. Attachment outline notes and annotation rows MUST NOT create supporting-item records. Original excluded material remains in the external Zotero archive. Zotero library URI and item identity MUST be captured as provenance on first Zotero import without authorizing writes back.

### Key Entities *(include if feature involves data)*

- **Source**: A stable retained reference with an identity, assigned citation key, bibliographic information, optional context, and relationships independent of any manuscript.
- **Bibliographic metadata**: Source type, ordered contributors and roles, title variants, edition/version, dates, identifiers, publication details, abstracts, and historical keywords, with original and normalized values distinguishable.
- **Import record and reconciliation decision**: Original input and its origin, candidate matching identity, competing values, applied decisions, and preservation or conversion limitations, including per-entry application status and retained unresolved conflict reasons.
- **Resource**: A labeled external file or multi-file unit with a path or root mapping, availability, optional primary designation, linked-in-place or managed status, and one filing collection when managed.
- **Collection**: A named position in a hierarchy with source memberships, distinct from project use and subject classification.
- **Project and citation selection**: An activity with source associations and a separately identifiable set of sources chosen for bibliography export. An adopted bibliography output records its destination and last successful export state so later outside edits can be detected.
- **Preference and override**: A convention or location setting with scope and origin, or an explicit record-level value that derived updates must preserve.
- **Operation and recovery record**: The requested change, affected identities or paths, outcome, and information needed to recognize retries or recover interrupted work.
- **Backup and full library export**: Recoverable catalog state or documented interchange material, each with version information and explicit external-content inclusion boundaries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In one trial on a user-selected active paper, the researcher completes source capture, lookup, correction, attachment access, citation selection, and bibliography export without opening the previous reference manager or editing catalog storage directly, and confirms these operations are usable for daily work.
- **SC-002**: A representative sample of at least 30 records covers journal articles, books, chapters, conference material, preprints, software/web material, a thesis, and a patent, plus creator, date, key, and attachment edge cases. The sample expands to include every type/construct used by the selected paper. Every imported key is preserved, every required supplied field and relationship is retained, and every unsupported element is identified and recoverable; unexplained losses are zero.
- **SC-003**: Repeating unchanged imports and identified submissions, including retries after interruption, creates zero duplicate sources or relationships. Every deliberate identity/key conflict in the sample is reported without silent overwrite or merge. In a mixed conflict test, every conflict-free entry is applied, every conflicting entry remains recoverable and unapplied, and the report accounts for 100% of input entries.
- **SC-004**: All reviewed key/title/edition fixtures produce their stated results, including overrides and missing creators or dates; changing preferences or metadata causes zero unintended changes to assigned keys, filenames, or overrides. All reviewed name-transliteration fixtures reproduce the same token under the same policy, preserve original bibliographic spelling, apply explicit overrides, and handle collisions without merging source identities; unsupported forms yield an actionable override request.
- **SC-005**: A predefined set of at least 20 lookup cases spanning keys, identifiers, titles, creators, abstracts, and context finds the intended sources, including untagged sources. Exact key and unique-identifier lookups identify the intended record in every case; ambiguous text results expose enough matching context for the researcher to identify the target without opening the old reference manager.
- **SC-006**: The trial manuscript renders all selected citations with their intended identities, creators, issued dates, journal/institution information, and protected spelling through each declared consumer, with zero unselected sources or unresolved citation keys. Repeated exports from unchanged inputs are identical, and catalog edits alone change zero bibliography files. An adopted, externally unchanged file is replaced by explicit export without an extra overwrite option; every tested external edit is detected and preserved until reconciliation or explicit overwrite.
- **SC-007**: Every resource safety case in Story 4, including destination collision and interruption, preserves at least one complete copy; successful transfers resolve through their catalog links and retained relocation records. Ordinary metadata, membership, and removal operations cause zero unauthorized file moves, renames, deletions, or note edits.
- **SC-008**: A restore into a separate empty location reproduces 100% of the saved source identities, keys, supported metadata, overrides, provenance, and relationships. Every unavailable external resource is reported, and full library export accounts for all saved records and relationships without unexplained omissions.
- **SC-009**: All local workflows in Stories 1–6 complete without model services or provider credentials. Invalid configuration, stale edits, and unsafe replacements produce actionable failures with no unintended changes in every defined failure scenario.
- **SC-010**: Every promoted mapping has an input type scope and a discriminating fixture, including agent input, Zotero and bibliography routes where relevant. The 51 disputed fields have individually recorded dispositions. Tests must demonstrate shared authorities, conflicting aliases, deliberate clearing, fallback re-import idempotence and explicit unknown handling. Supported output mappings must pass consumer rendering checks; vocabulary enumeration alone cannot satisfy this criterion.

## Assumptions

The accepted requirements above derive from the constitution and the reviewed decisions, particularly T1, E1, S1, K1–K4, A1, A2, and C1. The following numbered defaults resolve gaps for this draft. Entries marked resolved record explicit answers from the clarification session; other entries remain proposals introduced during specification, not claims of prior user approval. The clarification pass can revise remaining proposals before technical planning.

- **A-01 — Intake default (resolved 2026-09-20)**: From slice 2, newly downloaded attachments default to managed move into the configured document library, with the resulting location recorded. Slice 1 supports explicit copy-only intake into Unfiled. Each addition may explicitly choose link-in-place or managed copy instead. Every managed transfer exposes its action and destination before execution. Existing imported links remain in place. If the document-library destination is not configured or usable, report the problem and preserve the original file rather than silently selecting another action.
- **A-02 — Managed destinations (unfiled destination resolved 2026-09-20)**: When no filing collection is chosen, managed intake uses the `Unfiled` filing collection and its `Unfiled` folder beneath the configured document-library root. Filing can be changed later without moving the file until explicit reorganization. The remaining draft mapping policy maps collection hierarchy to relative folders, permits explicit per-collection folder mappings, and requires an explicit mapping for unsafe path components or collisions rather than silently sanitizing them. Collection naming edits do not themselves move files. Only explicitly selected managed reorganization is in scope; whole-library consolidation remains deferred.
- **A-03 — Identity and imports (batch handling resolved 2026-09-20)**: Prefer an explicit catalog identity, then a previously recorded source-system identity, then a consistent normalized persistent identifier. Contradictory evidence always requires reconciliation. An identical imported key with no contradictory evidence is a candidate for explicit matching, not sufficient permission to overwrite. Incoming differences require review, with current human corrections retained by default. Conflict-free references are imported immediately even when other entries conflict. Conflicting entries remain unapplied with their original data and reasons retained for later reconciliation; reports account for every input entry, and retries do not duplicate completed work. Identity matching order and field-level reconciliation defaults in this entry remain draft proposals. General merge tools, relationship inference between publications, and fuzzy automatic merging are deferred.
- **A-04 — Locations (resolved 2026-09-21)**: Separate config selection from catalog selection. Use ~/.config/refs/config.toml with canonical /Volumes/Casa/refs/cat and /Volumes/Casa/refs/lib settings; explicit invocation may select a separate test catalog. Never fall back if a selected path is missing. Projects cannot change data locations or resource roots. Detailed precedence and permitted project settings are in the configuration contract.
- **A-05 — Key token details (name transliteration resolved 2026-09-20)**: The proposed initial exclusion list is `a`, `an`, `the`, `and`, `or`, `of`, `to`, `for`, `in`, `on`, `with`, and `your`, applied case-insensitively. Select words from left to right; punctuation separates title words, while letters and digits stay together. The first selected word is lowercased and the second has an uppercase initial and lowercase remainder. Personal creator tokens use the family name in lowercase, retain internal hyphens, and remove spaces and apostrophes. A configured corporate alias takes precedence over a literal corporate name. For generated creator tokens, normalize Latin letters and apply the explicit Latin table; `García` yields `garcia`. Non-Latin input requests an override. This later decision supersedes the earlier general transliteration proposal. Preserve original names and let explicit overrides take precedence. Different original names can yield the same token; this invokes normal key-collision handling, never an identity merge. Unsupported input that cannot produce a usable token requires an override, as do missing usable title words or punctuation outside the defined token rules. The audit evaluated package alternatives; the user subsequently selected the bounded dependency-free policy. The user selected no dependency on 2026-09-21. AnyAscii is only a named fallback for later needs; the Latin policy and Unicode data version are recorded in key provenance. Fix the adopted policy behavior with examples, including composed/decomposed accented forms, non-Latin names from the migration sample, unsupported forms, collisions, and explicit overrides. The same supported name must produce the same token under the same policy, and changing policy must not regenerate assigned keys. Explicit keys must be nonempty, unique, contain no whitespace, and be representable by the chosen bibliography format. Imported keys are preserved; incompatible export keys require an explicit user decision rather than automatic rewriting. Examples from accepted decisions remain binding.
- **A-06 — Titles and sorting**: For English Title Case, the draft minor words are `a`, `an`, `the`, `and`, `but`, `or`, `nor`, `for`, `so`, `yet`, `as`, `at`, `by`, `in`, `of`, `on`, `per`, `to`, `up`, and `via`. Capitalize first and last words and the first word after an explicit subtitle boundary; apply the same rules to hyphen-separated parts, with first/last rules based on their positions in the whole title. Preserve protected terms, initially `AI`, `GPT-4`, `LaTeX`, `PhD`, `Python`, `R`, `nbgrader`, and `pH`, ahead of casing rules. Preserve non-English or uncertain-language titles pending explicit correction. Sort by the case-insensitive sort title, then numbered edition when available, then publication year, then citation key; missing edition/year values follow present values. Ignore opening quotation marks when recognizing an initial English article. Locale-specific collation and ambiguous edition reinterpretation are deferred; values remain available unchanged.
- **A-07 — Export replacement (resolved 2026-09-20)**: Identical output is a no-op. Before first treating an existing manuscript bibliography as refs-generated output, its contents must be imported or explicitly reconciled and adoption explicitly authorized. For an adopted file unchanged outside refs since its last successful export, explicit export replaces differing output without another overwrite option. If the file was edited outside refs, preserve it and report a conflict with a visible comparison; replacement requires reconciliation or explicit overwrite. Adoption is specific to the output destination and does not authorize replacing an unrelated existing file at a new destination. A successful export establishes the new comparison baseline; failed exports must not advance it. No background regeneration is introduced. Stable citation-key ordering and portable BibTeX are the initial output rules; richer profiles require declared compatible consumers and later implementation.
- **A-08 — Trial and evidence dependencies**: The user will select one active paper and authorize use of a representative migration sample before live migration or manuscript replacement. Sample size and lookup coverage in the success criteria are proposed acceptance targets for this feature. The existing research supplies local observations, not proof of conversion fidelity, annotation portability, current backup coverage, or restore success. The specification itself does not authorize moving real library files or replacing a real bibliography.
- **A-09 — Recovery and removal scope**: Slice 1 snapshots and later full library exports include catalog-owned material and a complete inventory of external resources; external attachment contents require separate backup. Restore uses an empty destination. An explicit tombstone reactivation preserves the source ID and key; general undo and complete event-history interfaces are deferred; preview, explicit execution, backups, and interrupted-operation recovery provide the initial protection. A managed transfer's recovery record is required even without a general history browser.
- **A-10 — Scope boundary**: One personal local library is the initial operating context, with safe concurrent agent updates. Built-in identifier lookup, RIS, semantic search, PDF-content search, broad web extraction, model classification, summaries, general extension distribution, integrated readers/editors, multi-user synchronization, unrestricted vault synchronization, and broad bulk file consolidation/renaming are excluded. Explicit filename generation and selected managed reorganization remain included. Later capabilities must respect the constitution's replacement and evidence requirements when introduced; this feature does not require their implementation to prove the academic workflow.

- **A-11 — Remaining review and planning follow-ups**: This clarification pass resolved five user choices. General collection-folder mapping, detailed identity matching order, configuration discovery/precedence, and remaining title/key token defaults remain explicit proposals; they were not separately approved by the five answers. Carry them into planning as stated assumptions and return to clarification if evidence requires a material behavior change. Transliteration selection is settled; implementation must verify the Latin table and override cases. Input adapters and recovery/export formats are selected in the revised contracts. Select the real paper and representative sample before live acceptance work. The plan supplies an explicitly unmeasured engineering target; it is not evidence of achieved performance.
- **A-12 — Standards revision (2026-09-21)**: The user selected a demand-driven CSL-shaped core with justified extensions, optional native label and verbatim originals. CSL-shaped agent input is in slice 1; public CSL-JSON and Zotero API JSON output are backlog features, not excluded permanently. No supporting-item subsystem, annotation editor or unrestricted BibLaTeX processing is required. Slice 1 implements portable BibTeX only.

### Source Authority and Traceability

| Source | Role in this feature |
| --- | --- |
| [Constitution v1.0.0](../../.specify/memory/constitution.md) | Binding preservation, ownership, agent access, capability boundaries, and evidence principles. |
| [Docs index](../../docs/README.md) | Packet entry point and the academic feature boundary. |
| [Vision](../../docs/vision.md) | Product intent, source ownership, explicit exports, and long-term constraints. |
| [Academic MVP](../../docs/academic-mvp.md) | First paper workflow and readiness evidence. |
| [Accepted behavior decisions](../../docs/behavior-decisions.md) | Accepted title, edition, sorting, key, filename, capture, and collection behavior. A2 supersedes earlier collection deferral. |
| [Configuration and CLI draft](../../docs/configuration-and-cli.md) | Inputs to A-01 through A-07; illustrative syntax is not adopted by reference. |
| [Requirements review](../../docs/requirements-review.md) | Reconciliation, file intake, portability, backup, exit, and open-choice coverage. |
| [Architecture](../../docs/architecture.md) | Ownership and failure boundaries; no prescribed implementation structure. |
| [Workflow research](../../docs/workflow-research.md) | Local sample characteristics and evidence limitations; historical A1 scope does not supersede A2. |
| [Development brief](../../docs/development.md) | Representative validation and first-paper-before-cutover sequencing. |
| [ArjanCodes review](../../docs/arjancodes-review.md) | Supporting rationale for proportionate design; no chosen language or framework. |
