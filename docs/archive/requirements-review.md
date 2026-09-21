> Historical design/research, archived 2026-09-21. Current scope is in the [slice 1 specification](../../specs/001-academic-catalog/spec.md); proposals here do not add requirements.

# Loose Requirements and Open Choices


**Bibliographic standards follow-through (2026-09-20):** The [model decision](../bibliographic-model.md) and [feature mapping contract](../../specs/001-academic-catalog/contracts/bibliography.md) now define the standards profile, structured field coverage, preservation limits, and acceptance obligations. Earlier proposals below remain source rationale.
**Feature status (2026-09-20):** This document retains source rationale and earlier review proposals. Current behavior is in the [clarified academic specification](../../specs/001-academic-catalog/spec.md); implementation decisions are in its [plan](../../specs/001-academic-catalog/plan.md) and [contracts](../../specs/001-academic-catalog/contracts/cli.md). Later clarification answers supersede conflicting older defaults below.

**Status, 2026-09-21:** Historical requirements questions plus backlog. Nine user decisions are now recorded in audit sections 11–12 and incorporated in the revised spec/contracts. Earlier unresolved labels below do not reopen those decisions.

**Scope of this work:** Gather the remaining needs, distinguish decisions from recommendations, and identify the evidence that would resolve uncertainty. Stop before writing specs. Existing command examples and TOML keys remain illustrations.

## What Is Already Settled

The [vision](../vision.md) records the broader product intent. The [behavior decisions](../behavior-decisions.md) record accepted conventions in detail; this summary does not replace them.

- Build a SQLite catalog with an agent-friendly CLI, starting with academic daily use and explicit bibliography export for Quarto.
- Standardize the user's reference workflow through configurable conventions. Prioritize CLI, configuration, keys, and normalization over early format breadth.
- Preserve existing citation keys. Generate new keys from author/editor, year, and two eligible short-title words, with hyphen-separated components and the accepted missing-creator, `ND`, collision, and override behavior.
- Use conventional Title Case with protected technical spelling. Keep title, short title, sort title, numbered edition, and version/variant meanings distinguishable. Ignore leading English articles for title sorting; allow persistent overrides.
- Link arbitrary external attachments in place and preserve existing filenames. Newly generated filenames have no spaces. Hierarchical collections, managed placement, and explicit reorganization are early requirements; broad bulk consolidation and bulk renaming remain later work.
- Export bibliographies only on explicit invocation. External scripts or skills may invoke export; catalog edits never trigger it.
- Support selectable, comparable capability implementations without requiring changes to the core. Keep goal-directed interpretation in external agents.
- Use credential helpers when needed. Secretpath supplies configuration precedent, not a required runtime dependency.

The chosen config is ~/.config/refs/config.toml, with separate /casa/refs/cat and /casa/refs/lib data folders. The configuration contract owns precedence/project discovery. The prior single-home suggestion is superseded.

## Open Needs for the First Useful Tool

These are gaps to resolve, not a queue of mandatory interviews. Prefer representative examples and small investigations where those can answer the question without asking the user to design internals.

| Area | Loose requirement or unanswered question | Current recommendation and basis |
| --- | --- | --- |
| Adding a new reference — resolved | The user will have an agent obtain source metadata and submit it to the CLI, as already done for ad hoc project bibliographies. | Make structured submission a primary path. Retain new references and corrections in the reusable catalog, then export deliberately. Built-in identifier lookup is deferred; PDF-first extraction is not an MVP commitment. |
| First real project | Which active paper provides the first practical trial, and which bibliography is authoritative today? | Choose a small active Quarto paper. Keep published/frozen bibliographies unchanged. The dissertation is useful fidelity evidence without being the default trial target. |
| Migration unit | Which export or read-only adapter preserves keys, source types, creators, dates, custom fields, collections, and attachments? | Select one verified route. A generic `.bib` conversion alone is insufficient evidence; the local Pandoc probe lost fields. Preserve import originals and report unrepresented data. |
| Zotero-only content | How much of existing notes, snapshots, annotations, and collection structure needs to remain usable immediately? | Inventory what is actually used. Preserve available data without promising a note editor or annotation viewer. The observed external annotations still require representative PDF checks. |
| Collection mapping | How should Zotero collections and current paths map to refs collections and filing locations? | Preserve collections as collections; map projects separately where useful. Select one filing collection per managed attachment. Existing outside links remain untouched; root-based ownership replaces adoption. Unfiled is the intake default; folder assignment and selected reorganize are slice 2. |
| Import identity | When do two inputs describe the same source, a separate edition/version, or an unresolved duplicate? | Use identifiers and original source identity as evidence. Title similarity alone cannot merge records. Conflicting identifiers need review rather than automatic consolidation. |
| Repeat imports | Which fields may update, and how do original imports interact with later manual corrections? | Preserve human corrections and expose competing values. The walkthrough's whole-batch rejection on conflict is a proposal; it may be too restrictive for migration. |
| Normalization scope | Which imported fields are normalized immediately, and which ambiguous values are retained pending correction? | Preview predictable formatting separately from factual corrections. Do not turn Title Case approval into permission to infer authors, dates, editions, or subtitle boundaries. |
| Short titles | How should missing short titles be derived, and when is a subtitle boundary trustworthy? | Preserve supplied short titles; otherwise use a known main title or the full title. No invented abbreviations. Keep a manual override. |
| Key details | Complete stopwords, punctuation, accented and non-Latin names, corporate aliases, and acronym rendering still need examples. | Keep the accepted overall shape. The complete list in the configuration draft is unapproved. Requiring an explicit key when no title words survive is also a proposal. |
| Title details | Exact minor words, hyphenation, protected spans, and non-English behavior are unsettled. | Use an inspectable policy with exceptions. Separate key stopwords from Title Case rules; retain original spelling when normalization is uncertain. |
| Editions and variants | Historical `P1E`, `R2E`, `5E`, decimal editions, and combined version/license labels are ambiguous. | Review representative cases during migration. Store the original values; do not generalize from one example to the entire library. |
| Sorting | How should editions, years, punctuation, and language affect order after the sort title? | Keep the accepted leading-article behavior and override. Treat secondary ordering as a default to review, not a reason to delay basic retrieval. |
| Metadata editing | Is JSON input sufficient for early daily use, or are an editor workflow and common field shortcuts necessary? | Ensure agents can perform explicit structured changes. Add the smallest human editing path that avoids making routine corrections cumbersome. |
| Project use | How should citation selection, background membership, and removal feel in everyday use? | Preserve the distinction already in the vision. The proposed `project cite` vocabulary and implied membership are unapproved conveniences. |
| Export replacement | How much protection is useful when an explicit export targets an existing file? | Propose preview plus per-invocation `--replace` for differing output. Do not mistake the user's rejection of automatic regeneration for approval of this additional flag. |
| Export fidelity | Which missing fields should warn, and which problems make output unusable? | Check actual source types and Quarto output. Preserve technical capitalization and creator semantics. Distinguish imperfect metadata from invalid output; avoid making every optional field a blocker. |
| Multiple bibliographies | Are CV status files and separate project bibliographies needed in the first release? | Preserve these observed use cases. One project selection and one explicit output is enough for the initial paper; do not require a multi-output profile system yet. |
| Resource selection | What should opening an entry do when there are several PDFs, notes, or other files? | Explicit primary selection is the clearest option. Automatic sole-PDF/sole-file fallbacks are proposals. Preserve descriptive labels so versions and supplements can be distinguished. |
| Portable links | How should root-based paths and absolute paths coexist across machines? | Support both without rewriting external files. Root mappings should make migration manageable; missing roots must remain visible. Exact root inference is unselected. |
| Configuration scope | Which preferences can projects override, and do project files ship immediately? | Recommend a minimal project file for selection and export defaults. Keep catalog-wide naming/normalization and credentials in user settings. Exact discovery and precedence remain in the review draft. |
| Backup and migration | Which current backup jobs cover the home and external files, and what constitutes a usable restore? | Verify coverage rather than assume `.config` is backed up. Provide a consistent catalog snapshot, preferences, and a resource inventory; packaging as ZIP is only an example. |
| Mistakes and concurrency | How are stale agent updates, failed batches, accidental removals, and interrupted writes handled? | Require clear failure reporting and preservation of existing data. Revision checks are proposed. Whether undo, trash, or explicit recovery is needed remains open; do not promise full event history. |
| Leaving the tool | How can the complete library be recovered without refs, beyond a project bibliography? | Retain the need for a full structured export of metadata, relationships, and provenance. Decide its early scope separately from database backup; a `.bib` file cannot preserve the whole catalog. |

## Requirements That Were Easy to Lose

**Capture files as well as metadata.** The user reports that PDFs gathered during agent-assisted writing can remain in Downloads or other temporary locations, risking loss of the work spent finding them. Adding a reference with a file should offer moving that file into a configured document-library location and recording its resulting link. This is acquisition-time intake, distinct from deferred bulk collection of existing attachments. Whether moving is the default remains open. A proposed compromise is a configurable intake default for newly acquired files, with explicit link-in-place and copy options; existing imported links remain untouched. The library destination need not live beside the SQLite database.

Intake must preserve filenames unless renaming is separately requested, avoid overwriting a different file, verify a transfer before removing the original, and report the final path. Interrupted intake must not lose the file or claim a successful link to a missing destination. Whether intake also offers the accepted generated-filename convention is a separate scope choice. Hierarchical collections and one filing collection per managed attachment are now agreed. Exact folder mapping remains open. Explicit reorganization may move managed files when collections change; project/tag edits never authorize filesystem moves. Multiple project memberships cannot each dictate one physical file location.

**Agent capture must end in the catalog.** The immediate workflow is agent research → catalog lookup/submission → project association/citation selection → explicit bibliography export. The CLI should return the persistent identity and usable key, distinguish an existing source from a new one, and report conflicts without requiring an agent to manipulate SQLite. Supplied metadata provenance and project context should survive beyond the session. Existing ad hoc `.bib` files also need an import/reconciliation path; do not assume the reusable library already contains their references or corrections. The user explicitly identified this retention gap as a primary motivation on 2026-09-20.

**Metadata verification is not claim verification.** An agent can obtain a correct DOI and page range without having read the source. Keep supplied evidence about metadata, abstract access, and full-text review distinguishable when retained; do not infer that a bibliographically complete entry supports every claim made with it. An elaborate claim-audit subsystem is not thereby an MVP requirement.

**Removing is not deleting a file.** Distinguish removing a project association, unselecting a citation, unlinking a resource, and removing a catalog source. The last operation still must not delete external attachments. Command names and reversibility are unresolved.

**Preference changes are not migrations.** Common settings should be easy to edit, but changing a template does not change assigned keys or filenames. Recomputing derived metadata must respect explicit overrides. A configuration change affecting future imports also needs enough provenance to explain differences from earlier imports.

**Import tags are not approved taxonomy.** Preserve historical tags/keywords without requiring ontology cleanup for the academic MVP. Later automatic classification must not promote arbitrary imported strings into approved concepts. How legacy tags appear in initial search/filtering is still open.

**Bibliographic sameness is contextual.** An article and its preprint, two book editions, a correction, and a supplement can be related without sharing one identity. Preserve distinctions until there is an explicit merge/relationship policy; do not force the whole relationship model into the first slice.

**Provider-free daily use matters.** Basic academic operations should work without model services, semantic indexes, or credentials. Future provider experiments must preserve identities and manual work when a provider is changed or removed.

**Saved content and authored notes have different owners.** A linked note is useful without indexing or syncing it. Future note indexing, content capture, and remote model processing need explicit boundaries; linking a private file is not itself a request to send its contents to a provider.

**No-spaces applies to generated filenames.** It does not prohibit linking files whose existing names contain spaces or preserving titles with ordinary typography.

## Deferred Requirements Worth Keeping Visible

| Later area | Retained need | What remains undecided |
| --- | --- | --- |
| Casual web capture | Real title, URLs, metadata, clean content, capture status, optional personal context; no filing obligation. | Capture surfaces and extraction selection. Defuddle is a candidate. |
| Meaning-based retrieval | Recover vaguely remembered items and supply passages for a lecture-use assessment. | QMD integration, passage identity, refresh/deletion behavior, and comparison against lexical search. |
| Controlled tagging | Approved hierarchical concepts, bounded assignments, abstention, human corrections, and managed vocabulary growth. | Jev versus alternatives, thresholds, calibration evidence, and evaluation workflow in pipyer. |
| Summaries | Optional attributable enrichment that never replaces source evidence. | Providers, retention, cost, and whether summaries improve actual retrieval. |
| Attachments | Broad bulk consolidation and bulk renaming remain optional later work. | Basic collections, managed intake, and explicit reorganization are now early requirements; preserve filenames and report external-link risks. |
| Notes integration | Link existing notes and optionally create a note when useful. | Templates and reverse links; no unrestricted two-way sync. |
| Additional formats | RIS and further interchange support. | Priority based on actual use and conversion fidelity. |
| CSL-JSON output | Public CSL-JSON export of selected or all sources, for citeproc-only manuscripts and as a working route back into Zotero. User-requested backlog item, 2026-09-21; this supersedes A-12's exclusion of public CSL export as a standing deferral, not as first-slice scope. | Deferred beyond slice 1 by the 2026-09-21 profile decision; informed by the canonical-model review in the [independent audit](../../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md) (F-I05, F-I10, section 5). |
| Zotero API JSON output | Export in Zotero's published API v3 item format so a library can return to Zotero with exact item types, type-specific fields, creator roles, collections, tags, and notes. User-requested backlog item, 2026-09-21. Not a database-level export: Zotero cannot open a refs catalog. | Deferred until wanted. Kept cheap by three early commitments: retain each source's Zotero item key and library URI, keep a native item-type label on every record, and preserve per-entry original Zotero JSON. Linked-file attachment creation through the API needs verification. |
| Extension distribution | Add/select compatible implementations without rebuilding the core. | Installation, compatibility, and dependency isolation, guided by real alternatives. |

## Evidence Still Needed

The [workflow research](workflow-research.md) is an observation log, not a migration certification. All 562 observed citation keys were pinned, but that does not establish conversion fidelity. Existing attachment paths were checked for existence, not full readability or annotation preservation. Backup notes do not prove current coverage. Sample bibliography parsing does not prove correct rendered citations. No QMD or Jev evaluation is claimed complete.

The most useful additional evidence is narrow: a representative migration sample, one active manuscript, and a few ambiguous title/edition cases. The ordinary new-source route is now settled as agent-supplied metadata; the [manufacturing-paper session evidence](workflow-research.md#agent-supplied-references-in-the-manufacturing-paper) illustrates the existing practice. Broader competitor research is unlikely to resolve these daily-workflow choices.

## Where to Stop

This requirements collection, the review drafts, and the existing architectural reasoning are the deliverable for this discussion. Do not expand them into database schemas, exact JSON contracts, exit-code tables, dependency selections, feature specs, or implementation tasks here. Unanswered choices may remain explicit and unresolved for the later development process.

The previously mentioned one-to-two-week allowance remains an unvalidated estimate. Migration fidelity and daily capture needs could change it; reducing format coverage alone does not justify promising a delivery date.
