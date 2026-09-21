# Feature Specification: Academic Catalog Workflow

**Feature Branch**: None; this workspace has no Git repository or branch hook.

**Feature Directory**: `specs/001-academic-catalog`

**Created**: 2026-09-20

**Status**: Draft — first clarification pass complete; remaining proposals and planning follow-ups recorded

**Input**: User description: "continue with $speckit-specify based on the files described in docs/README.md"

## Clarifications

### Session 2026-09-20

- Q: When adding a newly downloaded file to a reference, what should refs do with the file by default? → A: Move it into the configured document library and record its new location; allow per-addition overrides and preserve existing imported links in place.

- Q: Where should refs place a newly added file when you have not chosen a filing collection? → A: Move it into an Unfiled folder within the document library; a collection can be chosen later, with file movement requiring explicit reorganization.

- Q: If an import contains some conflicting references, should refs import the conflict-free references immediately or wait until the entire batch is resolved? → A: Import conflict-free references immediately; retain and report conflicting entries with their original data for later resolution.

- Q: After a bibliography has been adopted as refs-generated output, how should later explicit exports replace that file? → A: Replace it on explicit export if it has not been edited outside refs; otherwise require reconciliation or explicit overwrite.

- Q: How should newly generated citation keys handle accented or non-Latin names? → A: Remove accents and transliterate non-Latin names deterministically, preserving original bibliographic names and allowing explicit overrides. Assess a small, proven library/package if beneficial; do not assume transliteration is straightforward or suitable without representative evaluation.

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
6. **Given** missing creators, dates, protected technical spelling, or colliding generated keys, **When** new keys and normalized metadata are previewed and saved, **Then** the accepted conventions and draft normalization rules apply, existing keys remain intact, and the response returns the actual allocated key. Accented and non-Latin creator names use the supported deterministic transliteration policy while preserving original names; unsupported input requests an override, and distinct names yielding the same token remain distinct sources.
7. **Given** sources shared across collections and projects, **When** a list is filtered by collection, project membership, or citation selection and ordered by sort title, **Then** only matching sources appear in the specified order, with displayed titles unchanged.

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
2. **Given** a newly downloaded file and a configured document library, **When** the file is added without an intake override, **Then** managed move is the default, its action and destination are visible before execution, the destination file is verified before the original is removed, its name is preserved, and the resulting catalog link is reported. An explicit link-in-place or copy choice overrides that default.
3. **Given** a source with memberships in two collections, **When** one is assigned as an attachment's filing collection, **Then** it has one managed destination; adding or removing ordinary memberships does not move the file.
4. **Given** an existing Zotero link, **When** it is adopted into managed placement, **Then** its current location remains unchanged until a separate reorganization is executed.
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

The first release must retain the bibliographic breadth established by the published Zotero item/field/creator vocabulary, while accommodating meaningful citation data supplied through BibTeX/BibLaTeX and agent submissions. Shared citation classification must not erase native distinctions such as preprint versus published article, or different communication/broadcast types. The standards decision and technical representation are documented in [bibliographic model rationale](../../docs/bibliographic-model.md); exact schemas and mappings belong to the planning contracts.

Supported bibliographic facts must be inspectable and editable through structured operations, including fields outside the common title/author/date subset. Preserve chapter/container/multivolume title distinctions, ordered contributor roles and personal-name particles, corporate names, dates at supplied precision with their distinct roles and uncertainty, literal/numeric editions, ordered publication parties/places, source-specific identifiers and native fields. A narrow daily workflow must not force recognized bibliographic facts into inaccessible raw blobs.

Catalog acceptance, structured usability, search coverage, target-specific citation export, and original preservation are separate guarantees. Import/export reports must identify limitations at field and source level. An export supports a named, documented subset; it must not silently reinterpret an unsupported selected source as a generic reference. Imported child/standalone notes, annotation records, attachment metadata and asserted related-item links must retain origin and parent/target relationships with read-only inspection and full-library export. This does not add note/annotation editors, rendering, full-text indexing, related-item management, or a full Zotero replacement.

### Functional Requirements

#### Capture, identity, and conventions

- **FR-001**: The system MUST let a researcher or agent create, inspect, and explicitly correct structured source metadata, preserving supplied origin and personal context independently of project citation use. Saving requires a recognizable title, original address, or explicit container-and-part identification, but not tags, projects, files, or complete citation metadata.
- **FR-002**: The system MUST preserve source type, ordered creators and roles, literal corporate names, title variants, dates at supplied precision, numbered edition and version distinctions, identifiers, publication details, abstracts, historical tags, and resource references when supplied. Unknown fields MUST remain recoverable with their original input and any limits on editing or export disclosed.
- **FR-003**: Every saved source MUST have a stable identity and unique usable citation key. A creation or reconciliation result MUST identify created, unchanged, updated, or conflicted outcomes and return the actual retained or allocated identity and key. Retrying an explicitly identified completed submission MUST NOT create a duplicate.
- **FR-004**: Assigned keys and existing filenames MUST remain unchanged by metadata edits, imports, preference changes, and ordinary organization. Explicit replacement of a key MUST preview the old and new values, enforce uniqueness, and warn that external citations are not rewritten.
- **FR-005**: The system MUST distinguish original imported values, derived values, explicit overrides, and supplied or generated claims by origin. It MUST NOT infer that complete bibliographic metadata means a source was read or that it supports a manuscript claim.
- **FR-006**: New generated keys MUST use a lowercase author token, publication year, and two complete eligible words from the maintained short title in lower camel case, separated by hyphens. Use the first author, falling back to the first editor; with neither, use the title fragment followed by year without repetition. Use uppercase `ND` for missing year. One eligible title word is sufficient. Examples include `smith-2024-turingTrap`, `smith-ND-turingTrap`, and `turingTrap-ND`.
- **FR-007**: Key generation MUST exclude a small explicit configurable stopword list, preserve existing keys on collision, and allocate the next free suffix `-a` through `-z`, then `-aa`, `-ab`, and onward for distinct new sources. Generated creator tokens MUST remove accents and transliterate non-Latin names through a documented deterministic policy, while preserving original bibliographic names. Explicit key and key-author overrides MUST be supported without changing bibliographic authorship; invalid or duplicate overrides MUST be rejected. If a usable token cannot be produced by the supported policy, require an explicit override instead of inventing a spelling. Transliteration collisions MUST use the key-collision policy and MUST NOT imply identical source identity. Policy changes MUST NOT alter assigned keys. Remaining draft token rules and evaluation constraints are in A-05.
- **FR-008**: Normalized English titles MUST use conventional Title Case while preserving protected technical spelling and explicit exceptions. Original text MUST remain available. Language or factual uncertainty MUST be retained and reported rather than resolved by inventing creator, edition, or subtitle information. Draft casing rules are in A-06.
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

- **FR-018**: The first release MUST provide one verified route from Zotero and support the BibTeX/BibLaTeX imports required by the trial manuscript. It MUST preserve original import inputs and leave source catalogs, manuscript files, and attachment contents unchanged during import.
- **FR-019**: Import preview MUST identify preserved keys and fields, proposed normalization, unsupported data, duplicate candidates, unresolved paths, and conflicts before application. Unsupported source types MUST be reported without silent coercion into another type.
- **FR-020**: Identity reconciliation MUST use explicit catalog/origin identity or consistent identifiers as evidence. Title similarity alone MUST NOT merge records. Conflicting identifiers, incompatible editions or versions, and identical keys on distinct sources MUST require explicit reconciliation, preserving both inputs. Draft matching order and batch behavior are in A-03.
- **FR-021**: Repeat import of unchanged recognized input MUST leave source and relationship counts unchanged. Incoming differences MUST remain inspectable and MUST NOT overwrite human corrections automatically. Users MUST be able to retain current values or explicitly apply selected incoming values.
- **FR-022**: Import MUST retain collections as collections, historical keywords as metadata, and external attachment links in place. It MUST NOT infer projects or citation selections from collection membership or promote keywords into approved taxonomy.
- **FR-023**: Import reports MUST distinguish catalog preservation from full usability of notes, snapshots, and annotations. Unrepresented material MUST remain recoverable through original inputs and a report of its location and limitations; a migration MUST NOT claim complete Zotero fidelity without verification.
- **FR-024**: An import containing conflicting entries MUST apply conflict-free references immediately and retain conflicting entries unapplied with their original data and conflict reasons for later reconciliation. The result MUST distinguish imported, unchanged, unresolved, and failed entries and account for every input entry; partial completion MUST NOT be reported as complete success. Retrying or resolving remaining entries MUST NOT duplicate previously applied sources or relationships. An interruption MUST preserve applied work and identify unapplied or recovery-needed entries.

#### Resources and collections

- **FR-025**: Sources MUST support multiple labeled attachments of arbitrary type, linked through absolute paths or configured named roots. Linking MUST preserve filenames, including spaces, without requiring a common folder layout.
- **FR-026**: Users MUST be able to inspect resource paths and availability, change root mappings, and unlink resources. Missing roots or files MUST remain visible without automatic relocation or deletion.
- **FR-027**: Users MUST be able to choose a primary resource and explicitly select another for opening. With no primary, one linked resource may be opened automatically; multiple resources MUST return labeled choices rather than guess. Opening MUST use an external application and MUST NOT modify the file.
- **FR-028**: Hierarchical collections MUST be distinct from projects and tags and support creation, inspection, membership changes, renaming, and parent changes. A source may have multiple memberships.
- **FR-029**: Collection hierarchy changes MUST reject cycles and duplicate sibling names. Deleting a collection with children, memberships, or filing assignments MUST require explicit resolution of those dependents; it MUST NOT delete sources or files.
- **FR-030**: Each managed attachment MUST have exactly one filing collection. When none is chosen at intake, use the `Unfiled` filing collection and place the file in the document library's `Unfiled` folder without requiring an organization decision. Later filing reassignment MUST NOT move the file until explicit reorganization. Removing a membership used for filing MUST require explicit reassignment of the filing collection or a switch to linked-in-place status, without moving the file as part of the membership edit.
- **FR-031**: New-file intake MUST offer link-in-place, managed move, and managed copy with a visible action, destination, and resulting ownership mode. Newly downloaded attachments MUST default to managed move into the configured document library, with an explicit per-addition choice overriding the default (A-01). Existing imported links MUST remain in place. Missing or unusable destinations MUST fail visibly while preserving the original file. Collection-folder mapping follows A-02.
- **FR-032**: Existing links MUST be adoptable into managed placement without an immediate move. Later reorganization MUST preview affected files and explicitly execute a selected set of moves, preserving filenames and updating catalog paths. Membership, project, and tag edits MUST NOT trigger moves.
- **FR-033**: Managed transfers MUST prevent overwriting a different existing file, verify destination contents before removing an original, detect a source changed during transfer, and retain old-to-new paths and completion state for recovery. Failure MUST preserve at least one complete verified copy and MUST NOT leave a successful catalog link to a missing destination.
- **FR-034**: Recognized multi-file resources, such as a saved HTML page and its companion directory, MUST be handled as a unit. If that unit cannot be determined or transferred safely, the operation MUST preserve it in place and report that limitation. Potential broken external links MUST be reported without rewriting authored notes.
- **FR-035**: Removing a project association, citation selection, resource link, or catalog source MUST be distinct actions. Source removal MUST preview affected catalog relationships and require explicit execution; it MUST NOT delete attachment files, rewrite notes, or change previously exported bibliographies.

#### Project bibliographies

- **FR-036**: Users MUST be able to create and inspect projects, associate sources, separately select citations, and remove those associations or selections. Citation selection implies project association; unselecting a citation retains membership, while removing membership with a selected citation requires explicit removal of both. Duplicate association or selection MUST be a no-op.
- **FR-037**: Bibliography export MUST include each explicitly selected source once with its assigned key, preserve citation-relevant creator semantics and protected capitalization, and remain reproducible for unchanged selected data and preferences. The output MUST be usable independently of the catalog.
- **FR-038**: Only an explicit export invocation MUST write a bibliography, including invocations by external scripts or agents. Catalog edits and membership changes MUST NOT export automatically. Existing output MUST follow A-07's adoption and external-edit protection policy. An explicit export MUST be sufficient to replace an adopted file unchanged outside refs since its last export; external edits MUST produce a conflict requiring reconciliation or explicit overwrite.
- **FR-039**: Export MUST distinguish warnings for incomplete metadata from errors that prevent usable output, including invalid or duplicate keys or unsupported required source representation. It MUST NOT invent facts, silently drop selected citations, or leave truncated output after failure. Empty selection MUST be reported explicitly and remain subject to replacement rules.

#### Recovery and configuration

- **FR-040**: Users MUST be able to create a consistent catalog backup at a selected destination, including preferences, original inputs, provenance, relationships, and a resource inventory. The result MUST state which external contents are excluded and which version of the recovery format it uses.
- **FR-041**: Restoration MUST validate compatibility and use an empty destination, preserve saved identities and relationships, and report incomplete or failed restoration. It MUST NOT overwrite an existing catalog or claim that restoration of links proves external file contents are protected.
- **FR-042**: Full library export MUST provide documented structured metadata, original input material, provenance, preferences, collections, projects, citation selections, overrides, and resource references usable for migration away from refs. Excluded external contents MUST be listed. This is separate from a project bibliography and from backup restoration.
- **FR-043**: Users MUST be able to inspect actual catalog, configuration, and resource-root locations and effective preferences with their origins. Common naming preferences and resource mappings MUST be editable without manipulating storage internals or changing application code.
- **FR-044**: Setup MUST be explicit and repeatable without replacing existing catalog data or preferences. A missing or invalid selected home MUST produce a diagnostic rather than initialize implicitly or fall back silently to another catalog. The backup unit and responsibility for external files MUST be explained.
- **FR-045**: Scoped project defaults MUST support project selection and export destination/format, with a way to disable discovery or select a file explicitly. Projects MUST NOT select a different global catalog, change global naming policies, define resource roots, or introduce credential helpers. Draft resolution rules are in A-04.
- **FR-046**: Unknown or invalid preferences MUST report the value and its origin before mutations. Preference changes MUST affect future operations; existing keys, names, and manual overrides MUST remain intact until a separate explicit operation is invoked.

#### Bibliographic coverage and mapping accountability

- **FR-047**: Published baseline bibliographic types, fields, and contributor roles MUST have documented structured creation, inspection, and correction paths. Additional recognized citation/native fields MUST be retained as validated structured values rather than only original artifacts. Unknown or unparsed content MUST remain recoverable with its usability limits disclosed.
- **FR-048**: Each import/export mapping MUST distinguish ingestion, structured usability, indexing, target-specific export, and original preservation. Native type, name, date, title-level, edition, identifier, and publication-list distinctions MUST survive unless a target-specific limitation is explicitly reported. Unsupported essential citation semantics MUST prevent publication of the output rather than silently change meaning.
- **FR-049**: Imported notes, attachment metadata, annotations and asserted related-item links MUST retain stable origin and parent/target associations, including missing or unresolved targets. They MUST be inspectable as inert structured data and included in full-library export; preservation MUST NOT be reported as proof of rendering or external-file usability.

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
- **SC-002**: A representative sample of at least 30 records covers journal articles, books, chapters, conference material, preprints, software/web material, a thesis, and a patent, plus creator, date, key, and attachment edge cases. Every imported key is preserved, every required supplied field and relationship is retained, and every unsupported element is identified and recoverable; unexplained losses are zero.
- **SC-003**: Repeating unchanged imports and identified submissions, including retries after interruption, creates zero duplicate sources or relationships. Every deliberate identity/key conflict in the sample is reported without silent overwrite or merge. In a mixed conflict test, every conflict-free entry is applied, every conflicting entry remains recoverable and unapplied, and the report accounts for 100% of input entries.
- **SC-004**: All reviewed key/title/edition fixtures produce their stated results, including overrides and missing creators or dates; changing preferences or metadata causes zero unintended changes to assigned keys, filenames, or overrides. All reviewed name-transliteration fixtures reproduce the same token under the same policy, preserve original bibliographic spelling, apply explicit overrides, and handle collisions without merging source identities; unsupported forms yield an actionable override request.
- **SC-005**: A predefined set of at least 20 lookup cases spanning keys, identifiers, titles, creators, abstracts, and context finds the intended sources, including untagged sources. Exact key and unique-identifier lookups identify the intended record in every case; ambiguous text results expose enough matching context for the researcher to identify the target without opening the old reference manager.
- **SC-006**: The trial manuscript renders all selected citations with their intended identities, creator roles, and protected spelling, with zero unselected sources or unresolved citation keys. Repeated exports from unchanged inputs are identical, and catalog edits alone change zero bibliography files. An adopted, externally unchanged file is replaced by explicit export without an extra overwrite option; every tested external edit is detected and preserved until reconciliation or explicit overwrite.
- **SC-007**: Every resource safety case in Story 4, including destination collision and interruption, preserves at least one complete copy; successful transfers resolve through their catalog links and retained relocation records. Ordinary metadata, membership, and removal operations cause zero unauthorized file moves, renames, deletions, or note edits.
- **SC-008**: A restore into a separate empty location reproduces 100% of the saved source identities, keys, supported metadata, overrides, provenance, and relationships. Every unavailable external resource is reported, and full library export accounts for all saved records and relationships without unexplained omissions.
- **SC-009**: All local workflows in Stories 1–6 complete without model services or provider credentials. Invalid configuration, stale edits, and unsafe replacements produce actionable failures with no unintended changes in every defined failure scenario.
- **SC-010**: The documented baseline vocabulary has zero unaccounted types, fields, or creator roles. Representative mapping fixtures cover chapter/container/multivolume titles, native type collapse, preprint/publication distinction, software, patents, corporate/personal names, qualified dates, descriptive editions, publication lists, custom fields, supporting items, and inheritance. Each fixture verifies retained structured values, edits, explicit target limitations, and full-export preservation; rendered citation checks cover each initially supported output mapping.

## Assumptions

The accepted requirements above derive from the constitution and the reviewed decisions, particularly T1, E1, S1, K1–K4, A1, A2, and C1. The following numbered defaults resolve gaps for this draft. Entries marked resolved record explicit answers from the clarification session; other entries remain proposals introduced during specification, not claims of prior user approval. The clarification pass can revise remaining proposals before technical planning.

- **A-01 — Intake default (resolved 2026-09-20)**: Newly downloaded attachments default to managed move into the configured document library, with the resulting location recorded. Each addition may explicitly choose link-in-place or managed copy instead. Every managed transfer exposes its action and destination before execution. Existing imported links remain in place. If the document-library destination is not configured or usable, report the problem and preserve the original file rather than silently selecting another action.
- **A-02 — Managed destinations (unfiled destination resolved 2026-09-20)**: When no filing collection is chosen, managed intake uses the `Unfiled` filing collection and its `Unfiled` folder beneath the configured document-library root. Filing can be changed later without moving the file until explicit reorganization. The remaining draft mapping policy maps collection hierarchy to relative folders, permits explicit per-collection folder mappings, and requires an explicit mapping for unsafe path components or collisions rather than silently sanitizing them. Collection naming edits do not themselves move files. Only explicitly selected managed reorganization is in scope; whole-library consolidation remains deferred.
- **A-03 — Identity and imports (batch handling resolved 2026-09-20)**: Prefer an explicit catalog identity, then a previously recorded source-system identity, then a consistent normalized persistent identifier. Contradictory evidence always requires reconciliation. An identical imported key with no contradictory evidence is a candidate for explicit matching, not sufficient permission to overwrite. Incoming differences require review, with current human corrections retained by default. Conflict-free references are imported immediately even when other entries conflict. Conflicting entries remain unapplied with their original data and reasons retained for later reconciliation; reports account for every input entry, and retries do not duplicate completed work. Identity matching order and field-level reconciliation defaults in this entry remain draft proposals. General merge tools, relationship inference between publications, and fuzzy automatic merging are deferred.
- **A-04 — Configuration**: The draft home order is explicit invocation, explicit environment selection, the user's configured XDG configuration root, then `~/.config/refs/`. Invalid explicit choices fail. For permitted project settings, invocation choices override one selected project file, then user settings, then defaults. Automatic discovery uses the nearest `.refs.toml` from the working directory through the containing Git worktree root; outside a worktree, only the working directory is inspected. Relative paths use the declaring file's directory; invocation-relative paths use the working directory. Project files cover only project selection and export defaults. Exact command syntax and configuration vocabulary belong in later contracts.
- **A-05 — Key token details (name transliteration resolved 2026-09-20)**: The proposed initial exclusion list is `a`, `an`, `the`, `and`, `or`, `of`, `to`, `for`, `in`, `on`, `with`, and `your`, applied case-insensitively. Select words from left to right; punctuation separates title words, while letters and digits stay together. The first selected word is lowercased and the second has an uppercase initial and lowercase remainder. Personal creator tokens use the family name in lowercase, retain internal hyphens, and remove spaces and apostrophes. A configured corporate alias takes precedence over a literal corporate name. For generated creator tokens, remove accents and transliterate non-Latin names using a documented deterministic policy; for example, `García` yields `garcia`. Preserve original names and let explicit overrides take precedence. Different original names can yield the same token; this invokes normal key-collision handling, never an identity merge. Unsupported input that cannot produce a usable token requires an override, as do missing usable title words or punctuation outside the defined token rules. Planning must assess whether a small, established transliteration package is beneficial, considering script coverage, language-dependent ambiguities, output stability across versions, dependency cost, and maintenance evidence. Package selection and exact supported mappings require representative evaluation rather than assuming a universal romanization is correct. Fix the adopted policy behavior with examples, including composed/decomposed accented forms, non-Latin names from the migration sample, unsupported forms, collisions, and explicit overrides. The same supported name must produce the same token under the same policy, and changing policy must not regenerate assigned keys. Explicit keys must be nonempty, unique, contain no whitespace, and be representable by the chosen bibliography format. Imported keys are preserved; incompatible export keys require an explicit user decision rather than automatic rewriting. Examples from accepted decisions remain binding.
- **A-06 — Titles and sorting**: For English Title Case, the draft minor words are `a`, `an`, `the`, `and`, `but`, `or`, `nor`, `for`, `so`, `yet`, `as`, `at`, `by`, `in`, `of`, `on`, `per`, `to`, `up`, and `via`. Capitalize first and last words and the first word after an explicit subtitle boundary; apply the same rules to hyphen-separated parts, with first/last rules based on their positions in the whole title. Preserve protected terms, initially `AI`, `GPT-4`, `LaTeX`, `PhD`, `Python`, `R`, `nbgrader`, and `pH`, ahead of casing rules. Preserve non-English or uncertain-language titles pending explicit correction. Sort by the case-insensitive sort title, then numbered edition when available, then publication year, then citation key; missing edition/year values follow present values. Ignore opening quotation marks when recognizing an initial English article. Locale-specific collation and ambiguous edition reinterpretation are deferred; values remain available unchanged.
- **A-07 — Export replacement (resolved 2026-09-20)**: Identical output is a no-op. Before first treating an existing manuscript bibliography as refs-generated output, its contents must be imported or explicitly reconciled and adoption explicitly authorized. For an adopted file unchanged outside refs since its last successful export, explicit export replaces differing output without another overwrite option. If the file was edited outside refs, preserve it and report a conflict with a visible comparison; replacement requires reconciliation or explicit overwrite. Adoption is specific to the output destination and does not authorize replacing an unrelated existing file at a new destination. A successful export establishes the new comparison baseline; failed exports must not advance it. No background regeneration is introduced. Stable citation-key ordering and BibLaTeX as the initial output default remain draft preferences, with required alternative output selected by manuscript compatibility.
- **A-08 — Trial and evidence dependencies**: The user will select one active paper and authorize use of a representative migration sample before live migration or manuscript replacement. Sample size and lookup coverage in the success criteria are proposed acceptance targets for this feature. The existing research supplies local observations, not proof of conversion fidelity, annotation portability, current backup coverage, or restore success. The specification itself does not authorize moving real library files or replacing a real bibliography.
- **A-09 — Recovery and removal scope**: Initial snapshots and full library exports include catalog-owned material and a complete inventory of external resources; external attachment contents require separate backup. Restore uses an empty destination. General undo, trash, and complete event-history interfaces are deferred; preview, explicit execution, backups, and interrupted-operation recovery provide the initial protection. A managed transfer's recovery record is required even without a general history browser.
- **A-10 — Scope boundary**: One personal local library is the initial operating context, with safe concurrent agent updates. Built-in identifier lookup, RIS, semantic search, PDF-content search, broad web extraction, model classification, summaries, general extension distribution, integrated readers/editors, multi-user synchronization, unrestricted vault synchronization, and broad bulk file consolidation/renaming are excluded. Explicit filename generation and selected managed reorganization remain included. Later capabilities must respect the constitution's replacement and evidence requirements when introduced; this feature does not require their implementation to prove the academic workflow.

- **A-11 — Remaining review and planning follow-ups**: This clarification pass resolved five user choices. General collection-folder mapping, detailed identity matching order, configuration discovery/precedence, and remaining title/key token defaults remain explicit proposals; they were not separately approved by the five answers. Carry them into planning as stated assumptions and return to clarification if evidence requires a material behavior change. Transliteration package selection, supported script mappings, import adapter selection, and recovery/export formats require planning research. Select the real paper and representative sample before live acceptance work. Numerical operating-scale and latency targets remain to be set from the intended library workload; this pass establishes correctness outcomes without claiming a performance target.
- **A-12 — Standards revision (2026-09-20)**: The targeted bibliographic-model review replaces the earlier narrow field/type assumptions. Published vocabularies are compatibility baselines, not a demand to copy Zotero storage or implement every citation format. Native structured metadata and read-only supporting-item inspection are in scope; public CSL import/export, general relationship editing, annotation/note editors, and unrestricted BibLaTeX custom processing remain outside this feature. Existing key author/editor fallback is unchanged.

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
