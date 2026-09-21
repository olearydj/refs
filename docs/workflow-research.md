# Workflow Research for the Academic MVP

**Date:** 2026-09-20. **Status:** Observations and design implications; not an exhaustive migration audit.

## Method and Limits

Read local project documentation, bibliography files, Zotero preferences, both Zotero SQLite databases through read-only connections, and relevant notes in the current and dissertation-era Obsidian vaults. Queried existing CASS history without maintenance or reindexing. Parsed selected bibliographies with the installed Pandoc to inspect their shapes; successful parsing does not establish lossless conversion or correct rendering. No source catalogs, attachments, manuscript files, or user configuration were changed.

File availability checks tested existence, not checksums, full readability, or embedded annotations. The backup evidence is a dated setup note, not an inspection of current CCC tasks or a restore test. Historical workflow notes inform requirements but do not override current user instructions.

## Findings and Implications

### Catalog Shape and Immediate Retrieval

The current `/Users/djo/Zotero/zotero.sqlite` contains 562 non-attachment/note/annotation source records, with no deleted records excluded from that count. These include 233 journal articles, 201 books, 36 conference papers, 24 preprints, and 23 book sections, plus smaller groups of other types. All 562 have titles; 555 have dates, 453 abstracts, 235 DOI fields, 234 short titles, and 215 ISBN fields. Creator roles include authors, editors, book authors, series editors, contributors, inventors, and presenters; six creator records use single-field names. There are 58 collections and nine items with multiple collection memberships.

**Implication:** The MVP cannot assume every academic reference is a journal article or every creator is a personal author. Search existing abstracts as well as titles, creators, keys, and identifiers. This offers immediate value without making PDF extraction or semantic search a prerequisite. Preserve collections on migration while leaving their mapping to projects explicit.

### Keys and Metadata Corrections

The current Better BibTeX key table contains 562 keys, all pinned, covering every source record. The configured generator is `auth.lower+year+title.lower.substring(1,5)`. Actual keys include short and nonconforming historical variants; a template is a generation policy, not a validity rule for imported keys. The [setup note](/Volumes/Casa/obsidian/vault/dojo/zotero-obsidian-setup.md) documents compatibility with Bookends, collision suffixes, and an explicit unpin/refresh/repin operation after metadata correction.

**Implication:** Preserve imported keys exactly; make generation and explicit regeneration inspectable. Changing preferences or normalizing a title must not rename an existing key. Specify the behavior of missing authors/dates, corporate names, punctuation, stopwords, collisions, and manual overrides using actual examples before implementing the template language.

Subsequent user decision: new keys should use author + year + two complete words from the short title, ignoring articles. This supersedes reproducing the historical five-character generator for new entries; imported keys remain unchanged.

The user's current instruction establishes Title Case as the normalized catalog convention. Existing records mix capitalization styles and contain technical names. Preserve imported originals and protected spelling; title normalization is not a blind string capitalization operation. Short title, edition, full date, and creator roles need separate treatment.

### Attachments and Annotations

**Follow-up on subdirectories (2026-09-20):** A read-only attachment-path inventory confirms collection-shaped subdirectories beneath `/Users/djo/Box Sync/zotero`, including `lib/ds-ml-ai` (100 absolute attachment records), `dissertation/digital-twins` (57), `dissertation/mixed-reality` (50), and `courses/insy-7730-pd1` (20). These are record counts, not deduplicated physical-file counts. The current profile's `prefs.js` retains ZotFile settings `subfolder = true`, `subfolderFormat = "/%c"`, `dest_dir = "/Users/djo/Box Sync/zotero"`, and `source_dir = "/Users/djo/Downloads"`. The [setup note](/Volumes/Casa/obsidian/vault/dojo/zotero-obsidian-setup.md:77) explains that `%c` expands to the collection path and multiple collections prompt a choice. Thus the recorded organization is based on collection hierarchy, not author/year or an inferred subject classifier. Preferences and existing paths establish the configured convention; this inspection did not execute the plugin to test its present runtime behavior.

The user now requests an option to move a file into the document library at reference creation, motivated by collected PDFs remaining in Downloads. Preserve this as an initial intake requirement, distinct from deferred bulk consolidation. Default action and destination layout remain open; do not automatically reproduce collection-based routing in refs.

There are 792 attachment records: 511 absolute file paths, 43 `storage:` paths, and 238 empty paths. All 554 file-backed paths resolved on this machine. MIME counts across attachment records are 515 PDF, 274 HTML, two JPEG, and one DOCX. The old migration note describes 281 attachments as stored; current path inspection establishes only 43 storage-backed file paths, with the other 238 records lacking paths. Do not translate that historical count into 281 physical files.

All 240 annotation records have `isExternal=1`. The [legacy integration template note](/Volumes/Casa/obsidian/main/00-System/01-Plugins/_meta/zotero-integration-templates.md) prefers PDF annotations and explicitly filters annotation provenance. This supports testing embedded PDF annotations before assuming a database-only annotation conversion is necessary. It does not prove all annotations survive without Zotero.

The [setup workflow](/Volumes/Casa/obsidian/vault/dojo/zotero-obsidian-setup.md) uses short-title, edition, and year for filenames, independently of citation keys. It also warns that moving files can break Obsidian links.

**Implication:** Accept arbitrary attachment types and several resources per source. Scattered locations remain valid. Choosing a preferred PDF must be explicit when several candidates exist. Optional collection into a shared folder needs collision handling, verification, interruption recovery, and an old-to-new path manifest. Do not make filename changes an automatic consequence of metadata edits. External links are a separate concern from catalog link updates.

### Publication Workflows and Export Authority

Inspected bibliographies for the dissertation (292 parsed records), manufacturing-training paper (41), Pipyer paper (11), Danvas JOSE paper (11), and DEMA INSIGHT paper (7), plus CV bibliography files. This is a shape survey, not a fidelity audit. Records include books, chapters, conference papers, software/web material, manuscripts, theses, and a patent. Some BibTeX miscellaneous entries become an unspecified CSL type through this conversion, reinforcing the need to retain original type and fields.

The [dissertation build guide](/Volumes/Casa/pub/dissertation/docs/build.md) says bibliography auto-export was disabled for the published reference release to prevent drift; exports should be regenerated deliberately. Current Zotero preferences still enable idle exports for the general library BibTeX and JSON destinations, but do not list the dissertation destination among those active export entries. The historical migration note lists all three destinations. This is a real distinction between a live reference feed and a frozen publication bibliography.

The [Danvas publication instructions](/Volumes/Casa/pub/2026-jose-danvas/AGENTS.md) and [Pipyer publication instructions](/Volumes/Casa/pub/pipyer-paper/AGENTS.md) treat local bibliography files as canonical manuscript inputs. The [CV instructions](/Volumes/Casa/pub/cv/AGENTS.md) organize bibliography data by publication status. Existing projects are not already operating under refs' proposed generated-export ownership.

**Implication, refined by subsequent user clarification:** Support explicit export invocations only. Do not add automatic regeneration on catalog changes, including for general-library feeds. Build scripts or agent skills can invoke export deliberately. Require deliberate adoption before treating an existing hand-maintained bibliography as generated. Provide a preview or check of changes before replacing it. Preserve project-specific keys and fields; do not infer bibliography inclusion from all members of a Zotero collection.

### Configuration, CLI, and Backup Conventions

[Secretpath configuration](/Volumes/Casa/dev/secretpath/docs/config.md) uses editable TOML under `~/.config`, local overrides, and config inspection commands. [Danvas configuration](/Volumes/Casa/dev/danvas/docs/configuration.md) separates user and project concerns with explicit precedence, but uses a platform-standard macOS location. [Danner's CLI contract](/Volumes/Casa/dev/danner/specs/003-agent-help/contracts/cli.md) specifies offline help, examples, structured output, error recovery, and interface discovery. Git Muster intentionally has no configuration. These are patterns to select from, not one uniform house framework. The user subsequently clarified that credential helpers have replaced Secretpath in their workflow; only its configuration ergonomics are a reference for refs.

`/Users/djo/.config` is itself a Git repository. Its current ignore rules do not cover a refs database. The [CCC setup note](/Volumes/Casa/obsidian/vault/dojo/desktops/ccc-backup-setup.md), dated January 2026, describes backups of both the Data and Casa volumes. This supports a consolidated refs home as an understandable migration unit, but actual backup inclusion and restore remain to be checked.

**Implication:** Recommend `~/.config/refs/` as a visible, relocatable application home with editable preferences and SQLite data in separate files. Exclude runtime data from dotfiles Git while keeping it included in system backups. Provide effective-config inspection with setting origins and a path inventory. A SQLite-consistent snapshot plus configuration and a resource manifest should support migration; an in-directory snapshot alone is not protection against losing that directory.

The [XDG specification](https://specifications.freedesktop.org/basedir/latest/) normally separates configuration and data. Co-location here would be a deliberate user-oriented choice. For live database backup, use a SQLite-supported mechanism such as its [online backup API](https://www.sqlite.org/backup.html), not an assumption that copying one open database file is sufficient.

### CASS Evidence

Lexical searches covered Zotero, bibliography, citation keys, title case, ZotLit, and configuration. Several Codex hits expanded to empty messages; the two relevant native session files were inspected directly instead. No index repair was attempted. ZotLit hits were from this refs conversation, so they do not independently establish existing usage.

- **OpenCode:** `/Users/djo/.local/share/opencode/opencode.db/ses_2b3d1c2c9ffeUjKhWkM0Z66yYZ`, lines 35–41, records the distinction between Zotero state and externally linked files during migration. The durable migration note corroborates it.
- **Claude Code:** CASS archive source `/Users/djo/.config/claude/projects/cass-recovery-2026-08-19/-Volumes-Casa-pub-paper-1-manufacturing-training_815e1a81-67af-42f8-af69-848817f34553.jsonl__815e1a81-67af-42f8-af69-848817f34553.jsonl` (resolves through CASS; not a current local file), lines 37–39, checks pinned keys before correcting metadata to avoid breaking citations.
- **Codex:** [CV session](/Users/djo/.codex/sessions/2026/08/29/rollout-2026-08-29T17-31-36-01a04fa6-5880-74a0-bb5c-1c52d37bc54b.jsonl:288), native line 288, reports incomplete published metadata and inconsistent publication-status records. This supports field completeness checks and deliberate propagation of corrections, not automatic overwriting of project bibliographies.
- **Codex:** [teaching session](/Users/djo/.codex/sessions/2026/09/08/rollout-2026-09-08T08-10-43-01a08124-6fa0-7321-bbf1-42cd3a732d82.jsonl:587), native lines 587 and 601, documents Title Case headings. This is contextual evidence; the current direct instruction is the authority for bibliographic titles.

## Priority Consequences

### Agent-Supplied References in the Manufacturing Paper

On 2026-09-20 the user clarified that agents will obtain metadata and submit it through the CLI initially. They already use agents to construct ad hoc bibliographies outside Zotero; avoiding references being lost from the reusable library is a primary motivation for refs. Built-in identifier lookup is therefore deferred, not an unresolved prerequisite for leaving Zotero.

Read-only CASS searches recovered sessions for `/Volumes/Casa/pub/manufacturing-training-media-tradeoffs`. The `/casa` alias search returned no matches; using the recorded `/Volumes/Casa` workspace succeeded. CASS reported a healthy, fresh index. Lexical searches used `bibliography`, `Zotero`, and `bib* OR citation OR zotero`; semantic search was unnecessary for these exact workflow terms. CASS expansion returned empty or misaligned content for relevant hits, so the located native JSONL transcripts were inspected directly. No index maintenance or manuscript changes were performed.

Strong evidence comes from agent `claude_code`, session `642706e1-5208-48b1-bd55-6b4dcfdcc3c9`, native source `/Users/djo/.claude/projects/-Volumes-Casa-pub-manufacturing-training-media-tradeoffs/642706e1-5208-48b1-bd55-6b4dcfdcc3c9.jsonl`. The following are native file line numbers, not CASS hit offsets:

- [Lines anchored at 1573](/Users/djo/.claude/projects/-Volumes-Casa-pub-manufacturing-training-media-tradeoffs/642706e1-5208-48b1-bd55-6b4dcfdcc3c9.jsonl:1573): the user asks to incorporate more dissertation references. At 1613 the agent identifies eleven existing entries; the tool call at 1625 copies them into the paper's bibliography while stripping fields including abstracts, file links, keywords, notes, and annotations. The project artifact deliberately carries less information than the source library.
- [Lines anchored at 1644](/Users/djo/.claude/projects/-Volumes-Casa-pub-manufacturing-training-media-tradeoffs/642706e1-5208-48b1-bd55-6b4dcfdcc3c9.jsonl:1644): the agent queries Crossref by DOI and bibliographic text. At 1647 it writes two page ranges and a DOI into the local `references.bib`; at 1660 it reports the completed corrections. These inspected actions target the project file, not a central catalog. They do not establish whether any later session propagated the corrections elsewhere.
- [Lines anchored at 1663](/Users/djo/.claude/projects/-Volumes-Casa-pub-manufacturing-training-media-tradeoffs/642706e1-5208-48b1-bd55-6b4dcfdcc3c9.jsonl:1663): the user separately requests citation checking. At 1667 the agent uses identifiers from the bibliography to locate open-access copies. Metadata completion and verification of manuscript claims are distinct operations.
- [Line 2056](/Users/djo/.claude/projects/-Volumes-Casa-pub-manufacturing-training-media-tradeoffs/642706e1-5208-48b1-bd55-6b4dcfdcc3c9.jsonl:2056): the agent reports reading Zotero through a read-only connection and using linked Box PDFs for full-text checks. It also reports several manuscript sources absent from the library, including Crossman, Newell and Rosenbloom, Fitts and Posner, and Anderson. This is a historical agent report, not a new independent database audit. It supports the user's stated retention problem without proving permanent loss of any particular reference.

**Implication:** Agent research and correction should feed the persistent catalog, with project association and explicit export following. Prioritize structured submission, reliable existing-record lookup, conflict reporting, stable returned keys, and retention of supplied provenance/context. Project export can omit bulky fields without discarding them from the catalog. Reconcile historical ad hoc bibliographies as another input source; Zotero alone cannot be assumed to contain the complete working library. Do not require agents to repeat identifier retrieval that they have already performed, or infer full-text verification from complete metadata.

### Remaining Priorities

Define keys, normalization, effective configuration, and CLI behavior before implementing imports. Deliver bibliography migration, abstract-aware lexical search, attachment access, project selection, and explicit export before semantic retrieval or classification. Include consistent backup and restore in the first trusted release. Subsequent decision A1 defers attachment collection and bulk renaming to later versions if useful; neither is an MVP gate. Retain RIS as later format coverage.

Open checks include representative PDF annotation preservation, exact title/key transformation fixtures, bibliography ownership adoption per project, and current backup coverage. The normal initial route for new records is now settled: agent research followed by CLI submission.
