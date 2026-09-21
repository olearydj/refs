# Feature Specification: Academic Catalog, Slice 1

**Created:** 2026-09-20. **Revised:** 2026-09-21. **Branch:** main. **Status:** trimmed design awaiting the owner's second right-sizing checkpoint; no tasks or implementation yet.

## Scope and authority

Deliver one personal, offline capture-to-bibliography workflow: save and correct references, find them, cite them in a project, explicitly export portable BibTeX, link or copy attachments, and restore a catalog snapshot into a second home. This specification now covers slice 1 only. The [plan](plan.md) records deferrals without designing later slices. Use on one real paper precedes any slice 2 specification work.

The [constitution 2.0.0](../../.specify/memory/constitution.md), [accepted conventions](../../docs/behavior-decisions.md), and owner decisions govern outcomes. Contracts contain **implementation proposals** that make those outcomes testable; their exact syntax, algorithms and validation choices are not retrospective owner quotations. Existing FR/SC identifiers are retained for traceability, with deferred IDs explicitly listed below.

## Clarifications

The [audit sections 11–14](reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) preserve questions, options, literal replies and interpretations separately. In particular:

| Question/topic | Literal owner reply | Interpretation applied here |
| --- | --- | --- |
| Metadata breadth | “A: What I use (Recommended)” | Bounded CSL-shaped authority, justified extensions and verbatim originals. |
| Notes | “B: Fold into context (Recommended)” | Later Zotero migration imports child notes into context, not a supporting-item subsystem. |
| Export failure | “A: Block, with override (Recommended)” | Four classes; unknown override retained, stored loss waivers deferred by the trim. |
| First slice | “B: Core + copy-only intake (Recommended)” | Core, non-destructive copy, demonstrated restore. |
| Ownership | “B: Derive mode from location (Recommended)” | Named library-root files are managed; others linked. |
| Title case | “A, with a clarification. APA etc should govern exported material. My prefs for internal representation do not superceed that. I just don't want to see sentence case titles in the database. They are an abomination.” | Internal Title Case, protected terms, style-governed output. |
| Profile | “A: Portable default, richer by declaration (Recommended)” | Only portable BibTeX ships now. |
| Transliteration | “C: No dependency (Recommended)” | Built-in Latin normalization/table, otherwise explicit override. |
| Locations | “A, but /casa/refs/cat and /casa/refs/lib” | Separate configuration, catalog and library. Full clarification is in audit §12. |
| Constitution | “proceed with 1-3” | Applied v2.0.0; no pending amendment gate. |
| Background project membership | “No, cited only for now (Recommended)” | A project's sources are its citations; keep a cited column as a future seam. |
| Rename on intake | “Rename by default” | New copy intake renames by convention unless --keep-name; linked files and later reorganize keep names. |
| Trim | “I'm satisfied with changes based on my answers” | The keep/fold/defer list in audit §14 supersedes earlier delivery commitments. |

Earlier clarification replies were `b` for move default, `a` for Unfiled, `a` for mixed imports, `b` for adopted-output replacement, and `a - use a library / package if something small and proven exists and is beneficial. seems like this could be more problematic than it seems on face` for name handling. Those are literal replies, not the assistant-written answer sentences formerly attributed to the owner. Move remains deferred; the later no-dependency decision settles name handling. Existing-key preservation follows constitution I, not an invented quotation.

## User stories and acceptance

| Story | Priority | Independent acceptance scenario |
| --- | --- | --- |
| US1 Retain and recover references | P1 | In an empty catalog, add incomplete and complete records, correct under a revision guard, search metadata/context, and recover stable keys without a project or model service. Stale correction fails. |
| US2 Use a bibliography in one paper | P1 | Create a project, cite/uncite sources, explicitly export, and render with the catalog unavailable. Catalog edits alone leave output untouched. |
| US3 Import existing bibliography | P2 | Import a synthetic mixed .bib, preserve every original, report conflicts, re-run without duplicates, and use update to settle a value conflict. Inputs remain untouched. |
| US4 Keep research files | P2 | Link a file unchanged; copy another into Unfiled with the conventional name; exercise keep-name, collision, changed-source and interruption cases. The source is never deleted. |
| US5 Recover the catalog | P2 | Snapshot, restore into a second empty home, open it, and compare identities, keys, corrections, projects and resource inventory. File bytes are explicitly excluded. |
| US6 Inspect preferences | P2 | Inspect paths/effective settings before initialization, reject invalid project overrides, and fail on a missing Casa volume without creating a fallback catalog. |

## Functional requirements

Requirements below derive from the constitution and decisions above. Detailed policy lists and mechanics are proposals in the four [contracts](plan.md#contracts).

### Sources, conventions and access

- **FR-001–002:** Accept refs JSON, CSL-shaped JSON or a Bib entry with recognizable title, URL or container/part identification; tags, files and projects are optional. Retain supported names, dates, identifiers, edition/version, context and original evidence without inventing missing facts.
- **FR-003–005:** Give each source a stable ID and unique assigned key; distinguish original, derived and explicitly corrected values and access claims. Metadata edits, imports and preferences do not change assigned keys or attachment names. Explicit rekey previews the change and warns about external citations. New copy intake alone follows FR-012's naming exception. Request-ID replay is deferred; duplicate candidates are reported, not silently merged.
- **FR-006–007:** Generate author-year-two-short-title-word keys, lowercased author and lowerCamel title, separated by hyphens. Fall back to editor, then title-year; use uppercase ND for a missing year. One eligible title word suffices. Allocate -a…-z, -aa… transactionally. Keep explicit key/author overrides and configurable stopwords. Built-in Latin normalization plus a versioned table handles supported names; other scripts request an override, never guessed romanization. Token collisions are not identity matches.
- **FR-008–011:** Store Unicode Title Case with per-title protected terms and a whole-title case flag. Seed from protection braces, not accent/command grouping. Citation styles govern exported presentation. Preserve non-English spelling; require language at export when known non-English. Unprotected internal capitals warn. Preserve supplied short titles; otherwise derive from an explicit main-title boundary or full title, never split colons blindly. Keep numeric editions, versions and ambiguous shorthand distinct. Sort ignoring leading whole-word A/An/The; manual sort overrides persist.
- **FR-012:** New copy intake uses the accepted no-spaces short-title, optional edition/version and year filename, e.g. PracticalVim-2E-2015.pdf. --keep-name preserves the input basename. If short title or year cannot produce a name, preserve the original and report the fallback. Linking, import, metadata edits and later reorganize preserve names. No standalone filename command.
- **FR-013–014:** Provide readable and structured noninteractive CLI results, schemas, actionable failures and previews without persistent effects. Validate before mutation, reject stale revisions, and distinguish complete, partial and failed work. A retry cannot silently overwrite a file or newer value; there is no promise of stored operation replay.
- **FR-015–017:** Exact key/identifier lookup and lexical search cover title, creators, abstract, context and legacy tags, with matching origin shown. List by project and title/key order. A project filter means cited sources in this slice. No PDF-content search, collection filter or background membership. Local operations need no credentials/model service; reads do not create or semantically mutate a catalog.

### Imports and resources

- **FR-018–021:** Import .bib entries using type-scoped supported BibTeX/BibLaTeX aliases; preview normalizations, candidates and limitations. Preserve exact entry bytes and necessary file context. Import never overwrites existing source values, including deliberately cleared values. Conflicting identity evidence, editions or versions block that entry; title similarity never authorizes merging. Re-running preserves source/resource counts; repeated conflicts may recur. Plain update settles a metadata conflict. A lossy export re-import may report its downgrade as a conflict: projection-aware suppression is deferred, and richer current values remain untouched.
- **FR-022:** Preserve imported legacy tags and external file links; do not infer projects or approved taxonomy. Collections and Zotero migration are deferred.
- **FR-024:** Apply conflict-free entries independently and account for every input block in the report. Preserve conflicting/invalid originals, leave their proposals unapplied and return partial status. One light import-run row holds digest/counts; no per-entry status table, resume or reconcile command. After interruption, rerun the input safely.
- **FR-025–027:** Support multiple labeled resources using absolute or named-root paths. Show links and availability; unlink removes only a catalog link. Open a sole resource or explicitly selected resource; multiple candidates return choices. Primary-resource administration is deferred.
- **FR-030–034 (slice 1 subset):** Derive managed ownership from a named-root path within library_root, with no mode flag. Unfiled is the intake folder/effective filing default, not a collection table. Explicit copy independently verifies source/stage bytes and stability, publishes without overwrite, and retains the original. An interruption may leave a complete unregistered destination, reported for inspection; no automatic deletion or recovery journal. Link unsupported bundles in place rather than copying incomplete units. Paths/root changes never move files. Later explicit intake is the only exception to keeping outside linked files in place.
- **FR-035:** Removal/reactivation preserves identity, reserved key and external files; preview affected associations and require explicit execution. Removed sources are excluded from active searches and export, never implicitly resurrected by import.

### Projects, export and recovery

- **FR-036:** Provide project create, show (no argument lists projects), cite and uncite. Every association is cited in slice 1. Uncite removes that project's association only; repeats are no-ops. Retain the cited column for future background membership.
- **FR-037–038:** Explicit export alone writes a deterministic portable bibliography of each active cited source once, using assigned keys. First adoption of an existing file requires its exact digest to have been imported, reports all currently observed conflicts, and requires --adopt --overwrite to replace it. An unchanged adopted target needs only explicit export; outside edits conflict unless --overwrite explicitly authorizes replacement. Preserve overwritten outside bytes. Blocked output leaves the existing file untouched.
- **FR-039:** Report all affected entries using four classes: faithful incompleteness warns; documented fallback warns; enumerated meaning-changing loss blocks; unknown/unassessed mapping blocks unless --allow-unknown-mappings authorizes that run. The flag never overrides known blocking loss or structural errors. Stored waivers are backlog. Case-only duplicate keys are a portable-profile error.
- **FR-040–041:** Snapshot catalog/config and resource inventory consistently, identifying excluded external bytes. Demonstrate restoring into a separate empty home and opening it before accepting slice 1. Reject corruption, unsupported schema and nonempty destinations. Resource availability failures do not move/delete anything. A backup of links is not a backup of files.
- **FR-043–046:** Inspect settings and their origins. Configuration is ~/.config/refs/config.toml; chosen canonical data paths are /Volumes/Casa/refs/cat and /Volumes/Casa/refs/lib. Never sync the live catalog/staging or initialize elsewhere when the chosen location is unavailable. Explicit init is repeatable without overwrite. Invalid configuration fails before mutation; projects cannot override catalog, roots or naming policy. Report home_not_writable with the resolved path and required access.
- **FR-047–048:** One authoritative editable path per modeled fact; optional native label; four justified extensions; immutable originals for everything else. Each mapping specifies input type scope, alias, transform, conflict behavior, output assessment and fixture. Report preservation, editing, search and export separately. Known generic misc and subtype downgrades are assessed fallbacks, not automatically unknown. Current corrections/clears always beat originals.

### Deferred identifiers

FR-023/049 (Zotero notes, identities and related pairs), FR-028/029 (collections), FR-042 (logical full-library exit), and the later portions of FR-018/022/030–034/040–041 remain deferred. Their former detailed text is in Git commit 4209e5d. This document neither schedules nor expands them; [plan](plan.md#deferred-work) is the scope ledger.

## Success criteria

- **SC-001/004/005:** The installed smoke workflow captures, corrects, searches and retrieves sources/keys with origin and warnings. Naming fixtures cover missing facts, protection, Latin overrides and collisions; two concurrent key allocations preserve uniqueness.
- **SC-002/003:** Representative .bib fixtures preserve assigned keys and originals, account for every entry, and re-run without duplicates or overwrites. Conflicts remain visible; parser corruption counterexamples fail safely.
- **SC-006:** Portable output renders meaningful authors, issued dates, journal/institution, edition and protected spelling through Pandoc, Biber and classic BibTeX/elsarticle-num. It contains no unselected citations, is byte-reproducible and works without the catalog. Blocked and externally edited targets are preserved.
- **SC-007:** Copy collision, source-change and interruption fixtures retain source bytes and never overwrite a destination. Successful links resolve; metadata/project/removal operations cause no file changes.
- **SC-008/009:** A verified second-home restore preserves all saved identities, keys, originals, corrections, project selections and links. Configuration/stale-write failures are actionable. All slice 1 operations work offline.
- **SC-010:** Every implemented/promoted mapping passes discriminating input, conflicting-alias, edit/clear and output fixtures. Agent input participates in convergence. Zotero probes remain design evidence, not a slice 1 runtime importer. No registry enumeration or parsing-only check substitutes for rendering evidence.

## Assumptions and limits

**A-04:** Separate config/catalog selection and project precedence are defined in [CLI/configuration](contracts/cli.md). **A-12:** The bounded CSL-shaped core supports agent input now; public CSL-JSON and Zotero JSON output remain backlog. Other former A-series implementation defaults are consolidated in contracts rather than duplicated here.

This is a design, not an implementation passing those criteria. No real migration, file relocation, PDF inspection or manuscript replacement is authorized by this revision. The owner selects the paper for the first live trial. Power-loss protection has disclosed limits; the guaranteed failure model is process interruption on supported local filesystems.
