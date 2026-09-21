# Independent Design Audit: Academic Catalog Workflow

*Date:* 2026-09-20. *Reviewer:* independent audit agent (Claude Code session), at the user's request. *Stage:* after `$speckit-plan` and `$speckit-checklist`, before `$speckit-tasks`. *Companion:* the evaluated [bibliographic checklist](../checklists/bibliography.md).

This report reviews a baseline and proposes changes. It does not modify any audited document. The only files written by this audit are this report and the assessment annotations in the custom checklist.

## 1. Executive Assessment and Readiness Verdict

*Verdict: not ready for task generation.* The appropriate rework is renewed planning of the bibliographic model and migration route, plus a scope re-slice, preceded by a short user clarification pass. The workflow-level product decisions (agent capture, explicit export, preserved keys, collections and managed intake, Title Case, key format) are sound and should be kept. The restart is targeted: constitution, user stories 1, 2, 4 and 6, and most of the CLI envelope survive.

Five conclusions carry the verdict.

1. The bibliographic breadth mandate was never a user decision. FR-047 to FR-049, SC-010, the "Bibliographic semantic scope" section, and A-12 state an assistant recommendation as MUST-level scope. The native transcript shows the user approved a process in which the assistant said the Zotero baseline would be "a proposal to evaluate, not as an already accepted decision". Every recorded user statement about scope pushes toward small and fast ("not much more really", "does way more than necessary", "gets me a working tool quickly"). See F-S01.
2. The canonical model breaks its own first rule. "One authoritative value per fact" is contradicted by the registry itself: 51 of 121 Zotero fields are given a Zotero-native path while the same fact also has a CSL or core path, and BibLaTeX adds a third path for several of them. A thesis type, a report number, and a degree-granting institution each have two or three editable homes depending on the import route. See F-B01.
3. The inventory enumerates vocabulary the user does not have and omits the vocabulary the user does have. The user's library uses 16 of 37 Zotero types, 46 of 121 fields, and 7 of 37 creator roles. Every manuscript bibliography found is traditional-BibTeX shaped (`year`, `journal`, `address`, `school`, `month = jan`, `@phdthesis`, `@misc` with `howpublished`); none of those fields or type aliases appears in the registry, and the corpus contains zero `crossref`, `xdata`, or `@string`, which the contracts treat at length. See F-B02, F-B03, F-I03.
4. Export is aimed at the wrong consumers and would block or damage the user's real bibliographies. The default profile is "BibLaTeX 3.22", which nothing on this machine runs; fed to the manufacturing paper's actual `natbib` pipeline, BibLaTeX-dialect output loses every year, journal, school and institution while all citation keys still resolve, so SC-006 would pass. Separately, under the v1 mapping table and the "block the whole bibliography" rule, 8 of 9 surveyed bibliographies are blocked or review-gated, mostly by ordinary `@misc` web references written by agents. See F-I10, F-I01, F-I05.
5. Several mechanisms are both heavier and weaker than simple alternatives. The same-volume managed move is specified as a byte copy that loses creation date, download provenance, Finder tags and ACLs, when a hard link of the source is atomic, lossless and 280 times faster; `os.fsync` is not durable on macOS; the Zotero adapter requires a Better BibTeX database that current Better BibTeX no longer has; `pylatexenc` is described as pinned but is a range that resolves to a version with different behavior. See F-A01, F-A03, F-I06, F-D02.

Counts by severity: 2 Blocking, 29 Major, 12 Minor, 2 Observations (45 findings). Checklist: 36 of 36 items evaluated, 16 satisfied, 20 not satisfied.

*Main design recommendation:* replace the three-vocabulary "typed native namespace" profile with a demand-driven profile: one CSL-shaped core as the single authority for shared facts, names and dates; a native type label; a short, explicitly justified extension list admitted only by demonstrated need with a fixture; and per-entry originals preserved verbatim for everything else. Re-slice delivery so that agent capture to `.bib` export works first, and treat Zotero migration as a one-time extractor feeding a published-JSON input contract. Section 5 compares this with the alternatives and gives the strongest argument against it.

## 2. Scope, Methods, Sources, and Limitations

### 2.1 Baseline reviewed

No Git repository exists, so the baseline is identified by content hash (SHA-256 prefix) as read on 2026-09-20 at about 21:20 CDT: `spec.md` 33e7a862a4c2, `plan.md` 876a673a819c, `data-model.md` 926094a7370f, `research.md` 2bc9ecce7106, `bibliography.md` d8ea98d37615, `records.md` b70058e690aa, `interchange.md` 3dbe9a3762eb, `cli.md` 2fbbd69ed410, `files-and-recovery.md` 88fb0d865d04, `configuration.md` 84e6896ebabf, `capabilities.md` e265541ce944, `bibliographic-coverage.json` caeaee1672c0, constitution e4f24659d3a6, `docs/bibliographic-model.md` b086788e0893. No `tasks.md`, source code, `pyproject.toml`, or repository had appeared at the time of writing.

Read in full: `AGENTS.md`, `PROJECT_CONTEXT.md`, `docs/README.md`, the handoff `.ho/2026-09-20-001.md`, the constitution, every document in the docs index (the ArjanCodes review and the dependency audit's per-project inventories were skimmed beyond their conclusions), and every artifact under `specs/001-academic-catalog/`. The coverage inventory was analyzed structurally in full with Python, not through its summary counts. The `speckit-checklist` skill was read for ownership and marker semantics.

### 2.2 Evidence classes

Each material statement below carries one of: *[I]* inspected definition, documentation or source; *[X]* executed result in this audit; *[N]* inference; *[U]* unknown or unverified. Parser acceptance, schema validity, vocabulary enumeration, simple round trips, and a citation processor producing output are treated as different kinds of evidence and are not substituted for each other.

### 2.3 Research performed

| Track | Method | Key versions and references |
| --- | --- | --- |
| Registry verification | Re-fetched the three pinned upstream files and compared SHA-256; compared all 40 types, 770 type-field rows and creator lists against `schema.json`; joined the registry to Zotero's own CSL crosswalk (`csl.fields`, `csl.names`) through base fields; compared the BibLaTeX rows with `\DeclareDatamodelFields` in `blx-dm.def`; fetched `biblatex.def` v3.22 (SHA-256 ef81ea8b415e...) for aliases and inheritance | zotero-schema `b86c79b5` (version 45), CSL schema `40b3ce0b`, BibLaTeX v3.22; all three hashes match the registry [X] |
| User-decision recovery | CASS lexical search (read-only; index reported stale by 44 minutes, not refreshed), then direct parsing of native Codex JSONL; every quoted user statement below was checked against the native transcript line | DEV session `rollout-2026-09-20T14-43-17-01a0c058...jsonl` (38 user messages), REFS session `rollout-2026-09-20T19-39-49-01a0c167...jsonl` (23 user messages). DEV:9 is a 60 KB pasted ChatGPT conversation; only its "You said" turns are the user's words |
| Local library shape | Read-only `sqlite3` open (`mode=ro`) of `~/Zotero/zotero.sqlite`; counts and field names only | Zotero 6.0.37, userdata 121, global schema 28, Better BibTeX 7.0.0, ZotFile 5.1.2 [X] |
| Manuscript bibliographies and render paths | Read-only aggregate statistics over the `.bib` files under `/Volumes/Casa/pub`, `/Volumes/Casa/dev` and the research folder (976 entries); Quarto configuration and extension inspection | All declare `references.bib`. Three consumers read them: Pandoc citeproc (most projects, and Quarto's default PDF path), classic `bibtex` with `natbib` and `elsarticle-num.bst` (manufacturing paper: its Elsevier extension sets `cite-method: natbib`, verified), and `biblatex` with Biber (dissertation PDF, one DEMA document). Styles: APA 7, IEEE, AGU, Elsevier, Chicago author-date [X] |
| Export fidelity | Synthetic fixtures through `pandoc -f biblatex or bibtex -t csljson`, `pandoc --citeproc` with APA and Chicago author-date, classic `bibtex` with the manuscript's own `elsarticle-num.bst`, and `biber --tool --validate-datamodel` | Pandoc 3.11, Quarto 1.10.18, Biber 2.21 [X] |
| Dependencies | PyPI JSON metadata; synthetic parsing, round-trip, startup-time and SQLite capability experiments under `uv run --no-project --python 3.14` | CPython 3.14.2, SQLite 3.50.4, uv 0.12.1, bibtexparser 2.0.1, pylatexenc 2.10 and 2.11, Typer 0.27.2, Pydantic 2.13.5, Unidecode 1.4.0, anyascii 0.3.3, pybtex 0.26.1 [X] |
| Zotero migration | Zotero and Better BibTeX source, changelogs and developer documentation; `userdata.sql` at each release tag; local read-only inspection | Zotero tags 5.0.96 through 10.0 and `main`; Better BibTeX v8.0.0 through v9.0.64 [I][X] |
| Storage and file protocol | APFS experiments in a scratch directory: link, `renamex_np`, copy variants with xattr/ACL/resource-fork/creation-date checks; `fsync` versus `F_FULLFSYNC` timing; four-process SQLite concurrency in rollback and WAL modes; crash-point recovery; BLOB growth and backup cost | macOS 26.4.1, APFS; CPython `posixmodule.c` 3.14 [X][I] |

Five bounded sub-agents performed the history, dependency, Zotero, export, and storage tracks with instructions to challenge the working recommendation. Their conclusions were reconciled here, not concatenated; where I disagree with or qualify one, the finding says so.

### 2.4 Limitations

- All experiments used synthetic inputs. No real library record was converted, no real manuscript was rendered, nothing was moved, and no dependency was installed into any project.
- Experiment scripts and raw outputs are in a session-temporary scratch directory (`/private/tmp/claude-501/.../scratchpad/{schemas,history,deps,zotero,export,fsops}`) and will not persist. Commands and observed results that matter are restated in the findings so they can be reproduced. They can be copied into `reviews/evidence/` on request.
- Sub-agent narratives were returned as session text, not files; their raw scripts and outputs are in the scratch directory. One of my own draft conclusions (that no classic BibTeX consumer exists) was refuted by the export track and corrected before publication; see F-I10.
- Installed BibLaTeX is 3.21 with Biber 2.21, so the pinned 3.22 data model was inspected but not executed. Quarto bundles Pandoc 3.10; experiments used Pandoc 3.11.
- No cross-volume, exFAT, SMB, or FileProvider file experiment was possible in the sandbox. Statements about those are [I] or [N].
- Whether Zotero was running during inspection, whether the local API returns external annotations, and how a Zotero 6 to 10 upgrade would behave on this data are [U].
- CASS `view`, `export` and `sessions` failed under the sandbox; native JSONL was read directly instead. One tangential OpenCode session could not be opened.
- This is a review of written requirements and design. It is not a security review and not legal advice on licensing.

## 3. Findings

Severity: *Blocking* undermines a core guarantee or prevents coherent task generation; *Major* is a consequential gap, inconsistency or unsupported choice; *Minor* is a bounded clarification; *Observation* is a nonblocking consideration. Disposition: *User decision*, *Research*, or *Revision*.

### 3.1 Intent, scope, and traceability

#### F-S01 (Blocking) The bibliographic breadth mandate is an unapproved recommendation written as a requirement

- *Location:* `spec.md` "Bibliographic semantic scope", FR-047 to FR-049, SC-010, A-12; `docs/bibliographic-model.md` "Intent and recovered context" and "Decision"; `contracts/bibliography.md` "Independent coverage guarantees" (Usable row).
- *Claim:* "The first release must retain the bibliographic breadth established by the published Zotero item/field/creator vocabulary"; "All 37 Zotero bibliographic types and their recognized fields/roles have validated creation/inspection/edit paths"; imported notes, annotations, attachment metadata and related-item links are in scope.
- *Evidence:* [X] Native transcript, REFS session. The user asked two questions (line 669: "I don't see where specs/001 spells out the zotero-like data model ... am I missing something or does this not need to be stated?"; line 710: "what 'standard' should we follow in both cases?"). The assistant's process proposal (line 789) says: "My preceding recommendation to use Zotero's published schema should enter this document as a **proposal to evaluate**, not as an already accepted decision." The user replied "excellent. proceed as described" (line 806). The recommendation was then adopted into spec, data model, contracts and registry in the same turn. The user's next two actions were `$speckit-checklist` and commissioning this audit to "reconsider all but the basic premise". No user message asks for every Zotero type, for note or annotation import, or for more rigor. The Wren "40+ item types" text cited as breadth evidence (DEV:105) is a README quotation that the user immediately limited: "a step farther than I want to go". The only user words about notes are "maybe link to external notes, eg md in a vault". `docs/requirements-review.md` line 35 had correctly left "How much of existing notes, snapshots, annotations ... needs to remain usable immediately?" as an open question.
- *Consequence:* Tasks generated now would implement roughly 250 canonical paths, a supporting-item subsystem, and coverage machinery that no recorded decision supports, against a constitution that says proposals "MUST NOT acquire authority merely through repetition".
- *Recommendation:* Put the breadth question to the user explicitly (question D1 in section 8) before any replanning. Until answered, relabel FR-047 to FR-049, SC-010 and the scope section as proposals in the same way A-01 to A-07 are labelled.
- *Disposition:* User decision.

#### F-S02 (Major) Scope and mechanism count are out of proportion to a 562-source personal library, and no first slice is defined

- *Location:* `plan.md` "Delivery Sequence" ("full daily-use release includes all six"), "Complexity Tracking"; `contracts/cli.md`; `data-model.md`.
- *Evidence:* [X] The design as written has 49 functional requirements, 38 acceptance scenarios, 50 CLI commands, 19 entity tables plus an FTS projection, 7 durable state machines, 10 recovery or administration commands, 251 distinct canonical metadata paths (127 of them in extension namespaces), and about 44,600 words of governing text, all produced between 14:43 and 21:19 on one day. The library has 562 sources. `docs/development.md` line 99 asks for recovery design "at a level proportionate to a personal catalog"; the user said "I'd prefer to approach this in a way that gets me a working tool quickly" (DEV:592) and "I think it can be trimmed further" (DEV:602). "Complexity Tracking" lists only two items and declares no violations.
- *Counterexample:* The primary motivation (C1: agent-found references are lost in ad hoc `.bib` files) needs `add`, lookup, `project cite`, and `export`. Under the plan that outcome ships only after import reconciliation, managed transfers with an eight-state journal, backup bundles, full library export, a search plugin proof, and a certified Zotero adapter.
- *Recommendation:* Define slices with their own exit criteria (section 7). Slice 1 is capture, lookup, correction, project selection and `.bib` export with link-in-place resources and a simple backup. Managed intake, Zotero migration, reconciliation refinements, and full export follow in that order. Record deferred mechanisms in "Complexity Tracking" with the evidence that would readmit them.
- *Disposition:* Revision, after D1.

#### F-S03 (Major) The primary workflow is underserved: agents must author a bespoke schema, and humans have no ordinary editing path

- *Location:* `contracts/cli.md` `add`, `update`; `contracts/records.md`; A-12 ("public CSL import/export ... remain outside this feature").
- *Evidence:* [I] `add --input` accepts only the refs source-create schema. Agents obtain metadata as CSL-JSON (Crossref, DataCite, and `doi.org` content negotiation all return it) or as a BibTeX entry. The workflow-research transcript shows exactly that: Crossref queries followed by edits to `references.bib`. `import` accepts BibTeX but is a batch operation with `--origin`, batch identity and reconciliation, which is the wrong weight for one reference. A-12 excludes CSL input on the grounds that it is a "new public format", although `refs-csl-v1` already exists internally. `docs/requirements-review.md` lists "Metadata editing: is JSON input sufficient ... or are an editor workflow and common field shortcuts necessary?" as open; the contracts answer it implicitly with JSON patch files plus `--if-revision` only.
- *Counterexample:* To fix one page range a human must run `show --json`, read the revision, write a patch file, and run `update --patch file --if-revision N`.
- *Recommendation:* Accept `add --format csljson|bibtex|refs` for single records (the mapping is needed anyway). Add one human path, for example `refs edit REF` opening the record in `$EDITOR` with revision checking on save, or `update REF --set path=value`. Both are small and directly serve C1.
- *Disposition:* Revision; confirm with user under D1.

#### F-S04 (Major) "Accepted" labels are stronger than the record for several decisions

- *Location:* `docs/behavior-decisions.md` T1, E1, S1, K2, K4, A2, and "Agreed: Preserve existing keys"; `spec.md` Clarifications and the Assumptions preamble.
- *Evidence:* [X] Native transcript, DEV session. T1, E1 and S1 rest on the single word "proceed" (line 857) in reply to a message posing three questions with recommendations. K2 rests on "ok" (line 929); the concrete stopword list in A-05 was never shown. A2 rests on "agree. bulk rename is another possibility, later" (line 1252); the user's own requirement was "an equivalent to collections and a way to reorg files if collections change" (line 1242), while the three-concept taxonomy, single filing collection, linked versus managed modes and adopt-without-move are assistant design. "Preserve existing keys" was never typed by the user; "preserve existing, yes" (line 1017) is about filenames. The five clarification answers were the letters "b", "a", "a", "b" and one sentence; the spec records them as full sentences that fold in assistant elaborations, including a "managed copy" mode from a rejected option. Genuinely explicit user text exists for K1, K3, hyphens in K4, A1, C1, explicit-only export, Title Case, the RIS cut, and Typer.
- *Consequence:* Story 4, the transfer protocol and SC-007 descend from a one-word agreement. None of these items looks wrong, but the constitution's governance clause depends on the distinction being accurate.
- *Recommendation:* A five-minute confirmation pass listing the weakly accepted items in one table for yes or change. Relabel anything not confirmed as "proposed, unopposed".
- *Disposition:* User decision (D7).

#### F-S05 (Minor) Stale or contradictory status statements

- *Evidence:* [I] The constitution's Sync Impact comment says `docs/README.md` "still describes the constitution as a placeholder" and "remove before committing"; the README no longer says that. The only handoff note describes a project with no spec. `checklists/requirements.md` says "46 functional requirements and nine success criteria" in its first note and 49 and 10 in its revision note. A-11 says "Numerical operating-scale and latency targets remain to be set"; the plan sets them. `spec.md` Status says "first clarification pass complete" with no mention of the standards revision.
- *Recommendation:* Correct during the next authorized documentation pass; write a handoff note for the spec and plan session.
- *Disposition:* Revision.

### 3.2 Bibliographic model and standards

#### F-B01 (Blocking) Duplicate authorities: the registry contradicts "one authoritative value per fact"

- *Location:* `contracts/bibliography.md` "One authoritative value per fact"; `contracts/bibliographic-coverage.json` `zotero.types[].fields[]`, `csl.fields[]`, `biblatex.fields[]`; `contracts/records.md` `publication`, `citation_fields`, `extensions`.
- *Claim:* "A projection never stores another editable copy"; "A property mapped to a core path is rejected here as a duplicate authority"; "A Zotero native field uses the crosswalk's shared path only when the meaning is equivalent."
- *Evidence:* [X] Joining each Zotero field, through its base field, to the CSL variable that Zotero's own published crosswalk assigns, then comparing registry paths, yields 51 distinct Zotero fields whose registry path is `metadata.extensions.zotero.fields.*` while the corresponding CSL variable has a different core or `citation_fields` path. Reproduce with `schema.json` `csl.fields.text|date` and the registry. Groups: CSL `genre` at `publication.genre` versus `genre`, `thesisType`, `reportType`, `manuscriptType`, `letterType`, `mapType`, `postType`, `presentationType`, `websiteType`, `type`, `programmingLanguage` in the Zotero namespace, plus BibLaTeX `type` in the BibLaTeX namespace; CSL `number` at `publication.number` versus `number`, `reportNumber`, `patentNumber`, `billNumber`, `docketNumber`, `documentNumber`, `episodeNumber`, `publicLawNumber`, `identifier`, `archiveID`; CSL `medium` versus seven Zotero format fields; `authority` versus `court`, `legislativeBody`, `issuingAuthority`, `organization`; `dimensions` versus `artworkSize`, `runningTime`; and identically named pairs `scale`, `section`, `references`, `partTitle` and `part-title`. BibLaTeX adds `chapter` versus CSL `chapter-number`, `part` versus CSL `part`, `eprint`/`eprinttype` versus Zotero `archiveID` and `repository`, the `holder` name list versus the Zotero `assignee` string, and `langid`/`language` versus `metadata.language`. Institutions split the other way: Zotero `institution` and `university` map to `publication.publishers`, BibLaTeX `institution` maps to `publication.institutions`. Only `priorityDate` and journal `series` are declared deliberate exceptions in the contract.
- *Counterexample:* A PhD thesis migrated from Zotero stores its degree in `extensions.zotero.fields.thesisType` and its university in `publication.publishers`. The same thesis imported from the manuscript's `@phdthesis{..., school = {...}}` stores `extensions.biblatex.fields.type` and `publication.institutions`. An agent submitting it uses `publication.genre`. The three records do not compare equal, reconciliation reports no conflict because the paths differ, an edit to one path does not change the others, and a BibLaTeX `@thesis` exporter reading `institutions` emits no institution for the Zotero-migrated record. [X] Pandoc itself renders `@thesis` `institution` as CSL `publisher` and `type` as `genre`, confirming these are single facts.
- *Consequence:* Matching, conflict detection, editing, search, and export all become route-dependent. The design's answer to the expressiveness problem relocates the ambiguity into namespaces instead of resolving it.
- *Recommendation:* One fact, one path, chosen at the most general published level. Use the CSL variable where Zotero's crosswalk says the base field maps to it, and keep the specific Zotero field name and BibLaTeX entry subtype as provenance labels on the value, not as parallel editable fields. Permit a native path only where a registry row states the semantic difference in words and a fixture demonstrates it.
- *Alternatives:* A Zotero-shaped core or a BibLaTeX-shaped core would also remove the duplication (section 5). Any of the three is coherent; the present mixture is not.
- *Disposition:* Research and replanning, after D1.

#### F-B02 (Major) The coverage inventory is an enumeration, not a mapping, and SC-010 cannot fail

- *Location:* `bibliographic-coverage.json`; `spec.md` SC-010; `quickstart.md` "Bibliographic profile acceptance".
- *Evidence:* [X] All 770 Zotero rows share one `export` string ("explicit projection or omission/error report; see bibliography contract"). All 138 BibLaTeX rows share one `export` string and one `fixture_family` string ("B01-B15 plus value-kind and native-field cases"). All 51 BibLaTeX entry types share one `status` string and carry no shared-type projection. Creator entries hold only `creatorType` and `primary`. `handling` has three values on the Zotero side. The registry matches the upstream vocabularies exactly (no missing or extra type, field or declared BibLaTeX field), which is what it was generated to do. Because the registry is both the denominator and the mapping, "zero unaccounted types, fields, or creator roles" is true by construction.
- *Consequence:* The registry's size suggests assurance it does not contain. It carries no per-type field applicability for BibLaTeX, no reverse projection, no loss statement, and no role mapping, which are the things an implementer needs.
- *Recommendation:* Replace it with a mapping registry for the demand-driven set: one row per (source vocabulary, field, type scope) with canonical path, transformation, reverse projection per target, stated loss, and a concrete fixture ID. Generate the exhaustive enumeration as a report when wanted; do not treat it as a contract.
- *Disposition:* Revision during replanning.

#### F-B03 (Major) The vocabulary the user actually uses is absent

- *Location:* `bibliographic-coverage.json` `biblatex.*`; `contracts/bibliography.md` "Normative vocabulary inventory" (acknowledges that "derived date-part fields, aliases, and custom datamodels are not claimed"); `contracts/interchange.md` BibTeX table.
- *Evidence:* [X] Not in the registry: `year`, `month`, `journal`, `address`, `school`, `annote`, `archiveprefix`, `primaryclass`, `hyphenation`, `key`, `pdf`, and the type aliases `phdthesis`, `mastersthesis`, `techreport`, `conference`, `electronic`, `www`. [I] Date parts are generated in `blx-dm.def` lines 118-121 and 240-261, and the aliases are driver source-map steps in `biblatex.def` v3.22 lines 1349-1366, so an inventory of `\DeclareDatamodelFields` cannot see them. [X] Manuscript statistics: dissertation (292 entries) has `year` 287, `journal` 199, `month` 38 (all macros), `address` 21, `school` 5, `file` 242, `abstract` 224, `keywords` 58, and zero `date`, `journaltitle` or `location`; the manufacturing paper (41) has `year` 41, `journal` 25, `howpublished` 3; the pattern holds in all nine files. Entry types in use: `article`, `book`, `inproceedings`, `incollection`, `misc`, `phdthesis`, `patent`, `manual`, `online`, `standard`. Zero `crossref`, `xdata`, `related`, `ids`, `@string`, `@preamble` or JabRef metadata anywhere.
- *Consequence:* The first real import would meet fields with no registered handling, while SC-010 reports complete coverage.
- *Recommendation:* Build the BibTeX and BibLaTeX mapping from the corpus outward: legacy date parts and their conflict rule with `date`, the alias table from `biblatex.def`, `howpublished`, `file`, `keywords`, `langid`, `urldate`, `copyright`, `googlebooks`, `pmid`, `pmcid`, `assignee`.
- *Disposition:* Revision.

#### F-B04 (Major) The contributor-role model stores non-roles as roles and has no equivalence table

- *Location:* `bibliographic-coverage.json` `biblatex.fields` name rows; `contracts/bibliography.md` Creators row; `contracts/records.md` `creators`.
- *Evidence:* [X] `shortauthor`, `shorteditor` and `sortname` are mapped to `metadata.creators[role=...]`. They are alternative renderings of the author list, not contributors, and would enter the globally ordered creator list. `editora`, `editorb`, `editorc` are stored as roles while their meaning lives in the separate key fields `editoratype` and so on; `editortype = compiler` changes what `editor` means. The contract names core aliases `book-author` and `series-editor`, while the registry also registers CSL `container-author` and `collection-editor`. Zotero `castMember`, `podcaster`, `scriptwriter`, `reviewedAuthor`, `seriesCreator`, `originalCreator` have published CSL equivalents (`performer`, `host`, `script-writer`, ...) that the registry does not apply. BibLaTeX `holder` is a name list and Zotero `assignee` a string, for one fact.
- *Recommendation:* A role table keyed by canonical role with source-vocabulary aliases; fold `editorXtype` into the role at import and regenerate it at export; treat `shortauthor` and `sortname` as presentation overrides.
- *Disposition:* Revision.

#### F-B05 (Major) The type system has no BibLaTeX crosswalk

- *Location:* `contracts/bibliography.md` ("`metadata.type` uses the pinned CSL type vocabulary"; "Setting type/native_types must keep their classifications consistent"); registry `biblatex.entry_types`.
- *Evidence:* [X] The 51 BibLaTeX entry rows hold `type`, `options`, `status` and nothing else. Nothing says which `metadata.type` an imported `@collection`, `@mvbook`, `@periodical`, `@set`, `@manual` or `@booklet` receives, or what "consistent" means for a CSL type paired with a BibLaTeX native type. [X] Pandoc maps `@unpublished` with `eprint` to CSL `manuscript`, while B04 says a preprint is CSL `article`; `@misc` yields an empty CSL type.
- *Recommendation:* Publish the three-way type table for the types in scope and define the consistency predicate as membership in that table.
- *Disposition:* Revision.

#### F-B06 (Major) Title Case as stored form loses proper-noun information that sentence-case styles need

- *Location:* `spec.md` FR-008, A-06; `contracts/bibliography.md` final paragraph of "Named output profiles"; user decision T1.
- *Evidence:* [X] Pandoc 3.11 with APA: `title = {A History of Alabama and the American South After Darwin}` renders "A history of alabama and the american south after darwin"; brace-protected terms survive; with no `langid`, a German title is lowercased ("Die vermessung der welt"), while `langid = {german}` leaves it untouched. Chicago author-date re-capitalizes and therefore masks the problem; APA 7, IEEE and `elsarticle-num.bst`, all in use, present sentence-case titles. The quickstart's rendering fixture uses the default style, which is the masking case. Of 292 dissertation titles, 264 are already Title Case and 240 contain inner brace protection; only 12 entries carry `langid`.
- *Analysis:* Title Case in a `.bib` file is conventional and compatible with T1. The difficulty is that protection must cover every proper noun, not only the eight protected technical terms in A-06, and normalizing a sentence-case source title to Title Case destroys the only machine evidence of which words were proper nouns. The contract's "derive target text with language/protection rules" does not say where that knowledge comes from. The design does preserve the original value, which is the right safety net.
- *Recommendation:* Keep T1. Add per-title protected spans as first-class data (an agent supplies them at capture, import takes them from existing braces), emit braces at export from those spans, require `langid` for non-English titles at export, and add an export warning for unprotected capitalized words in a title whose original form was sentence case.
- *Disposition:* User decision (D2), then revision.

#### F-B07 (Major) Supporting items are unrequested and underspecified

- *Location:* FR-023, FR-049; `data-model.md` `supporting_items`, `source_relations`; `contracts/bibliography.md` "Supporting items and asserted relationships".
- *Evidence:* [X] The library has 238 child notes, 246 attachments carrying their own note text, 240 annotations that are all `isExternal=1` (the annotations live inside the PDFs; the rows are caches), 6 related-item links, and 3 standalone attachments that are collection members. [I] The model does not say where note or annotation content is stored, lists no annotation fields, has no place for an attachment's note, no collection membership for standalone items, no removal rule, and uniqueness "within kind" where Zotero keys are unique per library across kinds. Trash, `dc:replaces` and `owl:sameAs` are not mentioned.
- *Recommendation:* Drop database-level annotation import (nothing is lost; the PDFs hold them). Treat notes as an explicit user choice: either export them once to Markdown files linked as resources, which matches "maybe link to external notes", or keep them only inside the archived snapshot. Keep related-item links as plain asserted pairs if wanted.
- *Disposition:* User decision (D3).

#### F-B08 (Minor) Names and dates lack decision rules the corpus will exercise immediately

- *Evidence:* [I] The contract says "Do not infer particle kinds from spacing", but BibTeX has a single `von` part. [X] Pandoc maps it to `dropping-particle` unless BibLaTeX extended-name `useprefix=true` is given, maps `{World Health Organization}` (single braces) to a personal name "Organization, World Health", and maps `and others` to a literal "others". The Date model has `season` and `circa` but no unspecified-digit or open-range form, names no "certified parser", and has no rule for `year` plus `month` versus `date`. [X] Pandoc drops `199X` and `2004-22/..` silently and accepts `2024-02-30`.
- *Recommendation:* Adopt Pandoc's particle rule as the default with a per-name override; state the supported EDTF level (level 0 plus approximate, uncertain, and intervals); define legacy date-part precedence.
- *Disposition:* Revision.

#### F-B09 (Observation) `original_url` conflates the capture address and the bibliographic URL

- *Location:* registry rows for CSL `URL`, BibLaTeX `url`, Zotero `url`; FR-001.
- *Evidence:* [X] All three map to `metadata.original_url`, which FR-001 also uses as the casually saved address.
- *Recommendation:* Acceptable for the academic slice; separate the two before web capture arrives.
- *Disposition:* Revision, later.

### 3.3 Import, reconciliation, and export

#### F-I01 (Major) Whole-bibliography blocking plus a narrow type table stops the user's real bibliographies

- *Location:* `contracts/bibliography.md` Exportable row ("A selected unsupported source or essential unresolved fact blocks the entire bibliography publication"), B08 and B13, "Do not use `misc` as a silent universal escape hatch"; `contracts/interchange.md` ("An ambiguous miscellaneous entry requires type review"); FR-039.
- *Evidence:* [X] Classifying entries in nine real `.bib` files against the v1 table: `dema-llm` paper 4 of 7 entries are review-gated `@misc`; manufacturing paper 3 of 41; Pipyer paper 4 of 11; `dema-llm` docs 12 of 34; the dissertation is blocked outright by one `@manual` plus 8 `@misc`; the library-wide export by two `@standard` and one `@manual`. Only one file of nine exports without intervention. The library also holds magazine articles (10), blog posts (5), presentations (2), a newspaper article and a manuscript, none of which has a row. `docs/requirements-review.md` "Export fidelity" had said: "avoid making every optional field a blocker."
- *Consequence:* The rule converts a fidelity aspiration into an availability failure for the tool's main output, the night before a deadline.
- *Recommendation:* Default to export with per-entry warnings and a deterministic documented fallback (`@misc` or `@online` with the fields that exist), recording the fallback in the report; offer `--strict` to turn warnings into a block. Reserve unconditional errors for what makes the file unusable: invalid or duplicate keys and unserializable values.
- *Disposition:* User decision (D4), then revision.

#### F-I02 (Major) "Essential", "reviewed fallback", and "verified flattening" have no definition and no storage

- *Location:* FR-039, FR-048; `contracts/bibliography.md` B05, B07, B08, B10, B11, B12 and the inheritance section.
- *Evidence:* [I] No document defines the essential set, who reviews, what evidence suffices, or where a recorded review lives; `data-model.md` has no field for it.
- *Recommendation:* If strict mode is kept, define essential as a per-type required-variable table (for example article: author or editor, title, container-title, issued; book: author or editor, title, publisher, issued) and store waivers as explicit per-source records with actor and time.
- *Disposition:* Revision.

#### F-I03 (Major) The inheritance and macro rules contradict BibLaTeX and Pandoc, and address constructs the corpus does not contain

- *Location:* `contracts/bibliography.md` "Inheritance, macros, and Better BibTeX Extra"; `contracts/interchange.md`.
- *Evidence:* [I] `biblatex.def` v3.22 line 2019 sets `\DefaultInheritance{all=true,override=false}`; lines 2021-2095 declare the special mappings, including `mvbook` to `book`/`inbook` (`title` to `maintitle`), `periodical` to `article`, and `author` to `bookauthor`. BibLaTeX therefore inherits every field not excluded, including `isbn`, `url` and `doi`. The contract inherits a short whitelist and says "Do not inherit parent identifiers ... URL". [X] Pandoc's BibLaTeX reader follows BibLaTeX: a synthetic `@inbook` child received the parent's `ISBN` and `URL`. So a record flattened by refs differs from what both Biber and Pandoc produce from the same source file. [X] `bibtexparser` 2.0.1 does not evaluate `#` concatenation (`journal = jgr # sfx` stays literal) and accepts undefined macros silently, so "resolve supported string references" is refs-owned work. [X] The corpus has zero `crossref`, `xdata` and `@string`; its only macros are month names.
- *Recommendation:* For v1, support month macros and nothing else; on encountering `crossref` or `xdata`, offer resolution through `biber --tool --tool-resolve` or `pandoc -f biblatex` as an explicit pre-step, and store the flattened result with a note. If native inheritance is ever needed, implement BibLaTeX's actual rules, not a subset.
- *Disposition:* Revision.

#### F-I04 (Major) Dialect is declared per file, but real files are mixed, and the `@inbook` rule is a heuristic

- *Location:* `contracts/cli.md` `import --format bibtex|biblatex`; `contracts/bibliography.md` B02, B15.
- *Evidence:* [X] Every surveyed file is named `.bib`, is overwhelmingly legacy-field, and several mix in BibLaTeX features (`urldate`, `@online`, `langid`). B15 says that under dialect `bibtex` an `@inbook` `title` is the book title. Common exporters emit `@inbook` with `title` as the chapter and `booktitle` as the book regardless of dialect.
- *Recommendation:* Infer per entry from fields: if `booktitle` is present, `title` is the part; if absent with `chapter` or `pages`, apply the traditional reading and flag it. Treat BibLaTeX with legacy aliases as the single input dialect, which is what Pandoc and Biber both do.
- *Disposition:* Revision.

#### F-I05 (Major) The citation-fidelity test path is not the path the manuscript uses

- *Location:* `contracts/bibliography.md` ("`refs-csl-v1` is an internal projection ... used in citation tests"); `quickstart.md`; SC-006.
- *Evidence:* [X] The manuscript path is refs to `.bib` to Pandoc's BibLaTeX reader to CSL to citeproc. Rendering the same synthetic records from directly written CSL-JSON and from `.bib` gave content differences for 6 of 17 records under both APA and Chicago (podcast, talk, article with `eid`, standard, preprint, patent) and case-only differences for 2 more under APA. [X] Pandoc drops `holder` on `@patent`, maps `maintitle` to `container-title` for chapters and to `title` for books with the volume's own title as `volume-title`, and joins publisher lists with "; ". SC-006 asks that citations render with "their intended identities, creator roles, and protected spelling" without naming the oracle.
- *Further executed losses on the `.bib` path, all with empty stderr:* `@standard` becomes CSL `legislation` and renders as a public law with its author removed, which changes the in-text citation; `eid` without `pages`, `eprintclass`, `editora`, `annotator`, `foreword`, `related` and custom fields are dropped; `ids` aliases do not resolve citations; `2020?` loses its uncertainty and `199X`, `circa 1850`, `2019/..` render as "n.d."; in BibLaTeX mode an unbraced institution containing " and " is split ("National Institute of Standards; Technology"), and five real fields in the corpus have that shape; under IEEE a book in a multivolume work loses its own title because the style never prints `volume-title`.
- *Consequence:* A fixture suite that validates the internal CSL projection can pass while the exported `.bib` renders differently. "Explicit target limitations" are defined against BibLaTeX semantics, so losses introduced by the consumer's reader would never be reported.
- *Recommendation:* Make the oracle explicit: for each export fixture, golden rendered text from the emitted file through each consumer the destination declares (Pandoc citeproc under a sentence-case style such as APA and one other; classic `bibtex` with the manuscript's `.bst`, treating its warnings as failures; `biber --tool --validate-datamodel`), compared with a render of the canonical projection so that differences are reported per entry. If a CSL core is adopted, offer `--format csljson` as a public output as well, since it is then a near-lossless projection and gives the user a second route when the `.bib` path loses something.
- *Disposition:* Revision.

#### F-I06 (Major) The Zotero route is coupled to private layouts, requires an obsolete input, and names no versions

- *Location:* `contracts/interchange.md` "Zotero Snapshot Input"; `research.md` R4; `contracts/bibliography.md` ("Pinned imported citation keys remain governed by the separately verified BBT key store"); `quickstart.md`; `plan.md` release gates ("a supported Zotero/BBT snapshot schema is certified").
- *Evidence:* [I] Better BibTeX v8.0.0 changelog: "items have a Zotero-native citation key field. This has replaced the BBT citation key field"; "The concept of pinning keys is gone"; `content/key-manager/migrate.ts` renames `better-bibtex.sqlite` to `better-bibtex.migrated`. Native `citationKey` on all regular item types arrived in zotero-schema commit `55a13120ba` (2025-12-20), shipped in Zotero 7.0.32 and 8.0. [X] This machine runs Zotero 6.0.37 (userdata 121, global schema 28) and Better BibTeX 7.0.0, so the legacy key database exists, but all 562 keys are also present as `Citation Key:` lines in Extra with 562 of 562 agreement. No design document names any Zotero, userdata, or Better BibTeX version, and the registry pins schema 45 while the installed client has 28. [I] Zotero's developer documentation says database structure "can change between Zotero releases" and that the local API (Zotero 7+) "is intended for ... command-line tools, that would otherwise need to read directly from the SQLite database"; R4 evaluates neither the local nor the web API. `userdata` moved 121, 123, 125, 129 across 2022 to 2026 with additive changes to the tables an importer reads, so a fail-closed exact-version matrix would have rejected a readable database three times in 2026. Zotero 10 uses WAL; the manifest has no sidecar rule, and a non-hot `-journal` sits beside the live database now. `library_identity` is free text, while relations embed `users/<id>` URIs. Trash, merges (`dc:replaces`), group libraries (one exists, empty) and `storage/<itemKey>/` resolution are unaddressed.
- *Recommendation:* Make Zotero API v3 item and collection JSON the adapter's input contract, because it is published, versioned, per-item, and testable with hand-written fixtures. Keep acquisition separate: for this frozen 6.0.37 install, a one-off read-only extractor from `zotero.sqlite.bak` to that JSON, locked to userdata 121 and labelled a migration script, not a maintained adapter; for any later Zotero, the local API. Key precedence: native `citationKey`, then Extra `Citation Key:`, then the legacy table. Replace "certified matrix" with a capability check plus one supervised run. Normalize key location before fingerprinting so a later Better BibTeX migration does not flag every item as changed.
- *Strongest counter-argument:* direct SQLite is the only route needing no upgrade, network or running application for this user, it is point-in-time, and the 6.0.37 schema is frozen. The recommendation accepts that and still reads SQLite once; the JSON contract pays off only if repeat import is real, which the spec says it is.
- *Disposition:* Research and revision.

#### F-I07 (Major) Reconciliation and adoption are specified without any bulk decision, which makes them unreachable at real sizes

- *Location:* `contracts/records.md` "Matching and Reconciliation" ("a decision for every conflicting field"); `contracts/files-and-recovery.md` adoption ("every source entry must be applied or unchanged ... `leave_unresolved` does not permit initial adoption").
- *Evidence:* [I][X] Manuscript entries were deliberately stripped by agents (no abstracts, files, keywords) and differ from library records in casing and braces. Whether a field absent from the incoming entry counts as a difference is not defined. Adopting the 292-entry dissertation bibliography would need a per-field decision for every differing field of every matched entry, and one unresolved entry blocks adoption of the file.
- *Recommendation:* Define absence as "no opinion". Add policy-level decisions (`--prefer current`, `--prefer incoming` for named fields, `--accept-nonconflicting`). Let adoption proceed when the remaining unresolved entries are not selected for that project, or when the user passes an explicit acknowledgment.
- *Disposition:* Revision.

#### F-I08 (Major) Removing a source makes its citation key permanently unavailable, with no way back

- *Location:* `data-model.md` invariant 7; `contracts/records.md` `create_distinct`.
- *Evidence:* [I] Removal keeps a tombstone whose key stays reserved; reimport of the same origin "requires an explicit create-distinct reconciliation", and `create_distinct` requires a new key "when the imported key is occupied". There is no undelete command (A-09 defers undo and trash).
- *Counterexample:* The user removes `smith-2024-turingTrap` by mistake and re-adds it. The source cannot regain its key, so every manuscript citing it breaks, which is the exact harm FR-004 exists to prevent.
- *Recommendation:* Add `restore REF` for tombstones (cheap, since the row is retained), or let an explicit re-add reclaim a tombstoned key after preview.
- *Disposition:* Revision.

#### F-I09 (Minor) Zotero Extra and preserved TeX each have two authorities

- *Evidence:* [I] Zotero `extra` is mapped whole to `extensions.zotero.fields.extra`, while its directives and the `Citation Key:` line are also parsed separately. [X] In this library Extra holds 562 key lines, 206 `label: value` lines (Google Books ID 130, arXiv 21, ...), 4 `tex.` directives and 6 prose lines. Separately, "Changing a mapped semantic field invalidates its stale lexical output representation" implies export emits preserved TeX when unchanged and generated text otherwise, which makes output depend on edit history.
- *Recommendation:* Parse Extra into identifiers, key, and residual prose at import and store only those. Always generate export text from canonical values plus protected spans; keep original TeX as evidence only.
- *Disposition:* Revision.

#### F-I10 (Major) Export profiles are defined against a consumer the user does not have, and the default would silently damage a real manuscript

- *Location:* `contracts/bibliography.md` "Named output profiles" (`refs-biblatex-v1` "against BibLaTeX 3.22" as default; `refs-bibtex-v1` secondary); `contracts/configuration.md` `[export] format = "biblatex"`; A-07 ("BibLaTeX as the initial output default remain draft preferences"); `quickstart.md` (renders `--to html` only).
- *Evidence:* [X] The same `references.bib` is read by three engines across the user's projects: Pandoc citeproc, classic `bibtex` with `natbib` and `elsarticle-num.bst` (the manufacturing paper; `_extensions/quarto-journals/elsevier/_extension.yml` sets `cite-method: natbib`), and `biblatex` with Biber 2.21 (dissertation PDF). Every manuscript-side file is traditional BibTeX dialect; only the library-wide Better BibTeX export is BibLaTeX dialect. Running BibLaTeX-dialect synthetic entries through `bibtex` with the manuscript's own `.bst` produced "empty year" and "empty journal" warnings for every entry, lost school, institution and report number, rendered an extended-format name as "p. u. family=Gogh, given=Vincent", and still resolved every key. The same records in BibTeX dialect rendered completely with no warnings. Citation keys are case-sensitive in Pandoc and case-insensitive in `bibtex`, which reported a case-only twin as "Repeated entry" and skipped it; `records.md` only warns about case-only collisions.
- *Consequence:* Adopting the manufacturing paper's bibliography under the default profile would strip its PDF reference list while SC-006 ("zero unresolved citation keys") passes. Traditional BibTeX dialect is the only dialect all three engines read, and it is what the user already writes. An earlier draft of this audit concluded that no classic BibTeX consumer existed; that was wrong and is corrected here.
- *Recommendation:* Make the profile a property of the adopted export destination, declared by consumer (`citeproc`, `bibtex:<bst>`, `biber`), discoverable from the manuscript's Quarto configuration. Default to one portable BibTeX-dialect profile (`year` and month macro, `journal`, `address`, `school` or `institution`, classic entry types, plus `doi`, `url`, `urldate`), which all three engines read; never emit extended names or `@online`/`@thesis`/`@report` to a `bibtex` consumer; emit article numbers as `pages` where the consumer ignores `eid`; brace any single publisher or institution containing " and "; make case-insensitive key collision an error for `bibtex` destinations. Offer full BibLaTeX dialect only when every declared consumer reads it, and CSL-JSON as an option for citeproc-only destinations.
- *Strongest counter-argument:* per-destination profiles multiply outputs, and the dissertation uses one `bibliography:` for two engines. That is an argument for the single portable default, not for the current BibLaTeX default.
- *Disposition:* Revision; confirm under D8.

#### F-I11 (Minor) The contract's own emission rule invalidates two of its mapping rows and makes B13 permanent

- *Location:* `contracts/bibliography.md` "Native field emission requires that field to be valid for the selected type in the pinned entry-field declarations"; rows B04, B05, B13.
- *Evidence:* [I][X] In `blx-dm.def`, `artwork`, `audio`, `commentary`, `image`, `jurisdiction`, `legal`, `legislation`, `letter`, `movie`, `music`, `performance`, `review`, `standard` and `video` are declared entry types with no field block, so under the rule even `title` is invalid for them; Biber reports "Invalid field 'title' for entrytype 'movie'". B13's "unsupported until a fixture-backed mapping is registered" is therefore unsupported permanently as written. B04 emits `version` on `@unpublished` and B05 maps company to `publisher` on `@software`; Biber reports both as invalid for those types. Standard styles print such fields anyway, so the data model is stricter than rendering.
- *Recommendation:* Change the rule to "valid per data model, or on a registered allow-list backed by a render fixture", or change the rows.
- *Disposition:* Revision.

### 3.4 Architecture and operational behavior

#### F-A01 (Major) The default managed move is a lossy byte copy; an atomic lossless primitive exists

- *Location:* `contracts/files-and-recovery.md` "Filesystem API convention", "Ownership and Supported Storage", transfer table; `research.md` R6; `dependency-audit.md` "pathlib and durable publication".
- *Evidence:* [X] On APFS, `os.link(src, dst)` followed by unlink, and `renamex_np(RENAME_EXCL)`, both preserved inode, creation date, all six test xattrs (including `com.apple.quarantine`, `kMDItemWhereFroms`, Finder tags), the resource fork and the ACL, and both failed with `EEXIST` on collision leaving everything untouched. Copy to staging then `hardlink_to` lost creation date in every variant; `shutil.copy2` also lost `kMDItemWhereFroms`, tags, user xattrs, resource fork and ACL. Python on macOS has no `os.listxattr`, `getxattr` or `setxattr`, so "inspect ... copy and verify supported metadata, or refuse destructive move" forces ctypes or subprocess, refuses nearly every browser download, or silently supports nothing. For 64 MiB: 0.32 ms versus 90 ms. [X] `~/Downloads` and `~/Box Sync/zotero` are on the same APFS volume; `/Volumes/Casa` is a different volume.
- *Recommendation:* Dispatch on `st_dev`: same volume uses link, catalog commit, identity-checked unlink; cross volume (or `EXDEV`/`ENOTSUP`) uses one `copyfile(3)`-equivalent copy to staging outside any synced tree, `F_FULLFSYNC`, hash, link, commit, cleanup. State that creation date cannot be preserved across volumes.
- *Strongest counter-argument:* two paths means the dangerous copy path is the rarely exercised one; if the library root is placed on `/Volumes/Casa`, every intake is cross-volume and the link path never runs. In that case build the copy path first. The user decision on library location (D5) settles the order.
- *Disposition:* Revision.

#### F-A02 (Major) Source cleanup deletes by path after a verification window

- *Location:* `contracts/files-and-recovery.md` `cleanup_pending` row.
- *Evidence:* [X] Replacing the source path between verification and `unlink` (a browser re-download does this by rename) caused the newer file to be destroyed; recording `(st_dev, st_ino)` and renaming the source aside with `RENAME_EXCL` before an identity check detected the replacement and kept the file.
- *Recommendation:* Record source identity at `prepared`; at cleanup rename aside exclusively, check identity, then unlink or rename back. With the link protocol the check is "source inode equals destination inode".
- *Disposition:* Revision.

#### F-A03 (Major) Durability wording promises more than the mechanisms deliver on macOS, and more than the stated failure model needs

- *Location:* `contracts/files-and-recovery.md` ("durable flush", "Flush destination directory"); `research.md` R2 (`synchronous=FULL`), R6; `plan.md` Target Platform.
- *Evidence:* [I] CPython 3.14 `os.fsync` is a bare `fsync` (`Modules/posixmodule.c`; no `F_FULLFSYNC` in the file). macOS `man 2 fsync` states the drive may not have written the data. SQLite uses `F_FULLFSYNC` only with `PRAGMA fullfsync=ON`, default off. [X] Median `fsync` 0.032 ms versus `F_FULLFSYNC` 4.5 ms on this machine; commits 0.25 ms versus 15 ms in rollback mode. The contract's own failure model is process interruption, for which the page cache survives and no sync is needed.
- *Recommendation:* One `durable_sync` helper using `F_FULLFSYNC` on darwin, `PRAGMA fullfsync=ON`, drop directory flushes or mark them best effort, and word the guarantee as "safe against process death; best effort against power loss, with recovery reporting".
- *Disposition:* Revision.

#### F-A04 (Major) Including settings in the request fingerprint defeats resume after the natural fix

- *Location:* `contracts/cli.md` "Fingerprints include ... effective behavior-changing settings"; `data-model.md` `operations`.
- *Counterexample:* `add --file x.pdf --request-id R1` commits metadata, then intake fails because the library root is missing. The fix is editing `config.toml`. The retry with `R1` now returns `request_id_reused`; a new ID meets duplicate detection for the source already created.
- *Recommendation:* Fingerprint command, targets and payload only; store the settings fingerprint as provenance and warn when it changed.
- *Disposition:* Revision.

#### F-A05 (Minor) "The journal proves publication" has no specified proof

- *Evidence:* [I] The `published` row continues on a digest match, while the prose calls identical content a conflict "unless the journal proves it was published by this same operation". A digest cannot distinguish the operation's own file from an identical file placed by hand. [X] Inode identity with the recorded staging or source file resolves it without hashing. Staging names also need a per-attempt nonce so a retry does not collide with its own leftover.
- *Disposition:* Revision.

#### F-A06 (Major) Retention is unbounded, dominated by whole Zotero databases stored as BLOBs

- *Location:* `data-model.md` `artifacts` ("no silent cleanup in this slice"), `file_operations` ("previous target bytes"); `contracts/interchange.md` "Common Preservation Rules", backup and full export.
- *Evidence:* [X] `zotero.sqlite` is 74,035,200 bytes, about 70 percent full-text word index of the user's PDFs and 11 percent sync cache, and it contains account identifiers. Any Zotero session changes the bytes, so digest deduplication never applies. Twelve snapshots produce an 897 MB catalog; backup then takes about 1 s and stalls writers for that time in rollback mode. Everything else plausibly adds under 50 MB a year. Every backup and every full export copies all of it again. `~/.config` is a Git repository.
- *Assessment:* This is a proportion and privacy problem, not a limit problem (the 1e9-byte BLOB limit is not approached).
- *Recommendation:* Keep per-entry originals (a JSON document or BibTeX block per imported object) in the database. For any whole-database input store digest, length, versions and an external path only. Keep previous export bytes only when `--overwrite` replaced externally edited content. Add an explicit previewed `gc`.
- *Disposition:* Revision.

#### F-A07 (Major) Backup refuses to run when most wanted, and excludes the files refs itself relocated

- *Location:* `contracts/files-and-recovery.md` "Backup and Restore"; FR-040; User Story 5; `data-model.md` `resources` ("optional expected content digest").
- *Evidence:* [I] Backup rejects unresolved file operations, which is exactly the state in which a user wants a backup before attempting `recover`; `migrate` depends on backup and is blocked too. After a managed move refs has deleted the original and is sole custodian of the only copy under a layout it chose, yet managed attachments are excluded and their digest is optional, so a restore cannot be verified.
- *Recommendation:* Back up regardless and list unresolved operation IDs in the manifest. Make SHA-256 mandatory for managed resources and add `resource check --verify`. Offer `backup --include-managed` (hard links or clones when on one volume) and consider making it the default. Replace the complete-state and ready-marker machinery with write to `<name>.partial` then rename; drop `needs_revalidation`, since every export already compares current bytes with the stored digest.
- *Disposition:* Revision; D5 affects defaults.

#### F-A08 (Minor) Rollback journaling is adequate, but three interactions must be written down

- *Evidence:* [X] Four writers, 800 `BEGIN IMMEDIATE` transactions: 0.30 s rollback, 0.11 s WAL, zero lock failures in both; key-suffix allocation 200 of 200 distinct. An 8 s read snapshot in rollback mode caused one writer failure and a 5.6 s worst transaction. Upgrading a deferred read to a write failed 25 of 200 times (rollback) and 184 of 200 (WAL), ignoring the busy timeout. After a killed writer, a `mode=ro` open fails until a read-write open rolls back the hot journal. A WAL database is unreadable from a home without write permission unless `immutable=1`.
- *Recommendation:* Keep rollback journaling. State that export closes its read transaction before writing intent; implement "read-only" as "open read-write, write nothing"; keep large artifacts out of the main file so backup snapshots stay short.
- *Disposition:* Revision.

#### F-A09 (Major) The catalog home under `~/.config/refs` is unwritable for sandboxed agents and sits inside a dotfiles Git repository

- *Location:* `contracts/configuration.md` "Home and Project Selection"; A-04. The location is a recorded user preference ("maybe just under ~/.config/refs/ ?", DEV:659), so this is a risk to put to the user, not a correction.
- *Evidence:* [X] This audit session's own sandbox permits writes only to the project directory and temporary directories; `~/.config/refs` is not writable, so every mutating `refs` command from such an agent would fail, and the contract maps that to a generic exit 5. `~/.config` is a Git repository; with the catalog ignored there, `git clean -fdx` deletes it. XDG places data under `~/.local/share`.
- *Recommendation:* Ask the user (D5). Whatever the answer, add a distinct non-retryable `home_not_writable` error carrying the resolved path, document which directory to allowlist for agents, and have `refs paths` warn when the home is inside a Git worktree.
- *Disposition:* User decision.

#### F-A10 (Minor) The search entry-point boundary and proof plugin are premature

- *Evidence:* [I] Constitution IV requires replaceable capabilities "as those capabilities are introduced" and says interfaces "MUST address demonstrated variation". `docs/arjancodes-review.md` concludes: "Verify replacement using two real implementations." The plan builds a package entry-point group and a separately installed fixture distribution now, before QMD has been evaluated, to satisfy a principle that does not yet apply.
- *Recommendation:* Keep search behind one internal function with the result shape already specified. Introduce the entry point with the QMD investigation.
- *Disposition:* Revision.

### 3.5 Dependencies and maintainability

#### F-D01 (Major) `bibtexparser` 2.0.1 is a good block splitter with silent-corruption defects, and refs must own every semantic layer anyway

- *Location:* `research.md` R1, R3 ("A custom BibTeX grammar duplicates mature parsing work"); `plan.md` Primary Dependencies.
- *Evidence:* [I] 2.0.0 final was released 2026-09-08, described upstream as "identical to v2.0.0b10" with "some stuff may still be broken"; 2.0.1 (2026-09-10) is documentation only. MIT, installs on 3.14. [X] Strengths: exact raw text and start line per block, per-field lines, retained failed and duplicate blocks, recovery after a broken entry, 10,000 entries in 0.29 s. Defects: `#` concatenation not evaluated; undefined macros accepted silently; `YEAR` and `year` both kept silently; a missing `=` is absorbed into the previous field's value with no diagnostic; a valid entry containing `@article{` inside a braced value is rejected (Pandoc and Biber accept it); a failed block's raw text can be truncated; BibLaTeX extended names turn the whole entry into an error block; `and others` becomes a person; the writer is never byte-exact and expands macros. No inheritance, dates, or data-model validation.
- *Assessment:* R3's duplication claim is partly refuted. Keeping the library as a narrowly scoped splitter behind the adapter is the lower-risk choice; a refs-owned tokenizer validated against Biber and Pandoc is a credible alternative that would remove two runtime dependencies.
- *Recommendation:* Default middleware stack only; never its LaTeX decoding or its writer; add post-parse sanity checks for the missing-`=` and embedded-`@` cases; use `biber --tool --tool-resolve --validate-datamodel` and `pandoc -f biblatex -t csljson` as differential oracles in fixtures, with versions recorded and Biber's nondeterministic `OPTIONS` order normalized.
- *Disposition:* Revision.

#### F-D02 (Major) `pylatexenc` is not pinned and is destructive on bibliographic text

- *Evidence:* [X] `~=2.10` is a range; under the cooldown resolver it selects 2.11 (2026-07-25), and `bibtexparser` also requires it transitively. `latex_to_text(r'\ensuremath{\alpha}-decay')` yields "-decay" on 2.10 and "α-decay" on 2.11. In 13 cases no LaTeX to Unicode to LaTeX round trip reproduced its input: `{NASA}` loses or escapes its braces, math is rewritten, URLs and DOIs are truncated at `%`. R1's statement that "the two semantic conversion packages are pinned" is false.
- *Recommendation:* Pin `==2.11`; use it only for one-way derived text (search, display, key input) on non-verbatim fields; never in the ingest or export path.
- *Disposition:* Revision.

#### F-D03 (Minor) Typer needs a specific floor and refs-owned envelopes and discovery

- *Evidence:* [X] Startup is fine: 32 ms versus 22.5 ms for argparse; Rich loads only for help; Pydantic adds about 30 ms and `bibtexparser` 28 ms, so import lazily. Default usage errors are human text on stderr. `app(standalone_mode=False)` inside a refs-owned `main()` lets them become JSON envelopes. The public `typer.TyperException` base exists from 0.27.2 only; 0.27.1 requires a private import. Typer vendors Click and its groups have no `to_info_dict`, so `schema` and any command discovery must be built from refs' own Pydantic models.
- *Recommendation:* `typer>=0.27.2,<0.28`; disable completion, rich markup and pretty exceptions; test envelopes and exit codes, not help text. Typer remains the right choice and is an explicit user preference.
- *Disposition:* Revision.

#### F-D04 (Minor) Decide the transliteration library before the first key is assigned

- *Evidence:* [X] Every row of R5's table reproduces. Unidecode is GPLv2+. anyascii 0.3.3 (ISC) gives identical results for all tested Latin and Cyrillic names, differs on Greek and CJK spacing, and has no strict mode (refs can supply one). R5 did not consider it. The policy ID bakes the library into key provenance. The user's caution on this topic was explicit ("could be more problematic than it seems on face").
- *Recommendation:* Present the two options to the user (D6). Personal use carries no GPL obligation; distribution of a bundle would.
- *Disposition:* User decision.

#### F-D05 (Minor) Policy pins presented as technical needs; a beta tool as a gate

- *Evidence:* [X] No Python 3.14-only feature is used (`hardlink_to` 3.10, `tomllib` 3.11, `sqlite3` autocommit 3.12); sibling projects use `>=3.13`; uv's 3.13 ships the same SQLite 3.50.4. `ty` is 0.0.x beta with about two releases a week and states diagnostics may change between any two versions; unpinned under a three-day cooldown it can break a green gate with no code change. FTS5 `remove_diacritics` does not fold `Łódź` to `lodz` or `Straße` to `strasse`. The relative `exclude-newer = "3 days"` setting is real and works (uv 0.9.17+). The cooldown comes from the user's standing global instructions, not a refs decision.
- *Recommendation:* Say the Python pin is policy; add a startup SQLite capability check; pin `ty` exactly; add a folded search column if such names should match.
- *Disposition:* Revision.

### 3.6 Requirements and acceptance quality

#### F-Q01 (Major) The built-in requirements checklist's claims are not credible

- *Location:* `checklists/requirements.md` (markers reviewed, not changed).
- *Evidence:* [I] All 16 items were checked by the agent that wrote the spec, minutes after writing it. CHK006 "testable and unambiguous" sits beside undefined "essential", "supported", "recognized", "representative", "required", and "usable". CHK001 and CHK016 "no implementation details" sit beside FR-033's transfer mechanics and A-04's Git-worktree discovery algorithm. CHK003 "written for non-technical stakeholders" does not describe FR-047 to FR-049. CHK011 "scope is clearly bounded" was checked before and after a revision that roughly tripled the model's scope.
- *Recommendation:* Treat this checklist as unevaluated until a reviewer other than the author re-runs it after the revisions below.
- *Disposition:* Revision.

#### F-Q02 (Major) Acceptance criteria can pass despite loss of useful data

- *Evidence:* [N] SC-010 holds by construction (F-B02). SC-002's "every required supplied field" never defines required. SC-006 has no rendering oracle (F-I05). Fixtures B01 to B15 are each described from one source vocabulary; nothing requires that the same reference entered through Zotero data, a `.bib` entry, and agent JSON converge to an identical canonical record, so the F-B01 thesis counterexample passes every listed fixture. SC-001 rests on the user "confirming" usability. SC-008 compares "supported metadata", which excludes whatever was dropped.
- *Recommendation:* Add cross-route convergence fixtures as the core bibliographic acceptance test; define required fields per type; name rendering oracles; express SC-002 as a field-by-field diff against the source with every difference classified.
- *Disposition:* Revision.

#### F-Q03 (Minor) Overloaded vocabulary

- "Supported" is used for catalog types, value syntaxes, crossref pairs, string references, transliteration, and schema layouts. "Recognized", "registered", "known", and "baseline" overlap. "Certified" appears for a parser, a schema matrix, and a runtime with no certifier. Define each once in a glossary or replace with the specific condition.
- *Location:* throughout `spec.md`, `bibliography.md`, `interchange.md`, `plan.md`.
- *Disposition:* Revision.

#### F-Q04 (Minor) Performance targets are unanchored

- The 10,000-source, 30,000-link, four-process, p95 one-second targets were introduced by the plan, not the user, for a 562-source library. They exclude `show` with supporting payloads and catalogs carrying snapshot BLOBs. Process startup (about 60 to 140 ms with Pydantic models) will dominate agent-perceived latency and is unmeasured by the target. Keep one smoke-level target and measure installed-command latency.
- *Location:* `plan.md` Performance Goals and Scale/Scope; `research.md` R9; A-11.
- *Disposition:* Revision.

#### F-Q05 (Observation) The project documents are candid about status

- Across `docs/` and the spec, proposals are usually labelled as proposals, limits of research are stated, and "not executed" disclaimers are frequent. The failure mode is accumulation: each disclaimer is accurate, while the total commits the project to far more than was decided. That is why the remedy is a scope decision and a re-slice, not more caveats.
- *Disposition:* none required.

## 4. Flaws in the Custom Checklist Itself

The checklist text was preserved as instructed. These observations are for its next revision.

- CHK019, CHK034 and CHK035 test consistency and are satisfied, but what is consistently specified is, in this audit's view, wrong on the merits (F-I01, F-I04, F-S03). A consistency item cannot reveal that.
- No item asks whether the breadth itself is proportionate or authorized; CHK036 comes closest. No item tests coverage of the user's actual corpus vocabulary (F-B03) or cross-route convergence (F-Q02).
- CHK013 bundles three questions (denominator, baseline, statuses); it fails on all three here, but would be clearer split.
- The checklist has no items for Zotero trash and merges, citation-key location across Better BibTeX versions, or retention and privacy of preserved originals, all of which are bibliographic-preservation requirements.
- Several items cite "Coverage registry" as if it were a mapping; F-B02 explains why it is not.

## 5. Comparison of Major Design Alternatives

### 5.1 Canonical bibliographic model

| Option | For | Against |
| --- | --- | --- |
| A. Current: CSL type plus core paths plus `citation_fields` plus typed Zotero and BibLaTeX namespaces | Nothing is unrepresentable; each vocabulary's names are familiar to its users | Duplicate authorities (F-B01); three-way crosswalk burden with no published source for two of the three legs; 251 paths for agents to learn; validation must encode per-type applicability for three vocabularies; cost is permanent |
| B. Zotero item model as the core (API JSON shape) | Trivial, lossless migration; mature type and role set; Zotero publishes the crosswalk to CSL, so citeproc rendering is solved upstream; agents and many tools know the shape | 121 type-specific field names for about 45 facts; BibLaTeX-only distinctions end up in a free-text Extra; no published Zotero-to-BibLaTeX mapping (Better BibTeX owns a large translator); the user's other inputs are `.bib` files and CSL-JSON, not Zotero JSON; ties the tool's vocabulary to the application being left |
| C. BibLaTeX data model as the core, Unicode values in JSON, no TeX | Richest titles, lists, dates (EDTF), and roles; export to `.bib` is nearly identity; Biber validates it; the dissertation already renders through biblatex | Names and dates are strings needing parsing on every use; Pandoc reads a subset and maps it its own way; agents receive CSL-JSON far more often; entry-type set is weak for software, datasets, broadcasts; custom data models make "the" model a moving target |
| D. Recommended: CSL-shaped core, native type label, short justified extension list, per-entry originals | One authority per fact by construction; JSON-native names and dates; matches what agents fetch and what citeproc consumes in five of six manuscripts; Zotero-to-CSL leg is published; `.bib` export from CSL is bounded and has Pandoc, classic `bibtex` and Biber as oracles; small enough to specify precisely | CSL collapses some types (kept as a label, not as editable structure); three-level titles, publisher lists, eprint triple, priority date and similar need extensions from day one; adding an extension later means re-deriving from originals; CSL 1.0.2 is frozen and imperfect (no `license`, weak legal types) |

Option D's extension list, from the corpus and the fixtures already written: subtitle and title addon, multivolume title trio, ordered publisher and place lists, `eprint`/`eprinttype`/`eprintclass`, `pubstate`, patent priority date and assignee, `langid`, protected spans, sort and short title modes, and the refs operational fields. Everything else found at import is preserved verbatim per entry, shown read-only, searchable as text if wanted, and promotable to an extension by a registry change plus re-derivation.

*Strongest argument against D:* it bets that the user's needs stay near today's 16 types and 46 fields. If the user starts citing legal or audiovisual material, CSL's collapsed types and thin fields will pinch, each extension will need a migration and a re-derivation pass, and the project will have re-created option A slowly with less forethought. Option B avoids that by inheriting a model already stretched by millions of libraries, and it makes the one risky event (migration) trivial. *Response:* per-entry originals make late promotion mechanical, the native type label keeps the distinction available to export, and the alternative costs are paid now, by a one-person project, for material that may never arrive. If the user answers D1 with "I want everything Zotero can represent", option B, not option A, is the coherent way to deliver that.

### 5.2 Other alternatives

| Decision | Current | Recommended | Strongest argument against the recommendation |
| --- | --- | --- | --- |
| Zotero route | Certified SQLite snapshot adapter with Better BibTeX database | API v3 JSON input contract; one-off SQLite extractor for the frozen install | A one-shot migration does not need an intermediate format |
| Managed move | Copy, verify, hard-link publish, delete | Hard link of the source on one volume; copy path across volumes | Two paths; the risky one is rarely run |
| Export failure policy | Block whole file | Warn and fall back; `--strict` opt-in | A silent `@misc` can embarrass in print; warnings get ignored |
| Public outputs | BibLaTeX 3.22 default, BibTeX secondary, CSL internal | Per-destination consumer declaration; one portable BibTeX-dialect `.bib` as default; BibLaTeX dialect and CSL-JSON as options | More than one profile doubles fixtures; one conservative `.bib` already works everywhere for a corpus that is about 92 percent common types |
| Search boundary | Entry-point plugin with proof fixture now | Internal function now, entry point with QMD | Retrofitting a boundary later can be harder than building it early |
| Backup | Bundle state machines, managed files excluded | `VACUUM INTO` plus config plus manifest; managed files included or verifiable | Including files makes backups large |

## 6. Checklist Assessment Summary

All 36 items were evaluated. Satisfied (16): CHK003, 005, 010, 012, 014, 015, 019, 021, 025, 026, 027, 028, 031, 032, 034, 035. Not satisfied (20): CHK001, 002, 004, 006, 007, 008, 009, 011, 013, 016, 017, 018, 020, 022, 023, 024, 029, 030, 033, 036. None is unevaluated.

| Section | Satisfied | Not satisfied | Principal findings |
| --- | --- | --- | --- |
| Requirement Completeness (001-004) | 003 | 001, 002, 004 | F-B02, F-B03, F-B04, F-B07 |
| Requirement Clarity (005-008) | 005 | 006, 007, 008 | F-I02, F-I09 |
| Requirement Consistency (009-012) | 010, 012 | 009, 011 | F-B01 |
| Acceptance Criteria Quality (013-016) | 014, 015 | 013, 016 | F-B02, F-Q02, F-I01 |
| Scenario Coverage (017-020) | 019 | 017, 018, 020 | F-B01, F-I07, F-A07 |
| Edge Case Coverage (021-026) | 021, 025, 026 | 022, 023, 024 | F-I04, F-B08, F-I03 |
| Non-Functional (027-029) | 027, 028 | 029 | F-A06, F-Q04 |
| Dependencies and Assumptions (030-032) | 031, 032 | 030 | F-I06 |
| Ambiguities and Conflicts (033-036) | 034, 035 | 033, 036 | F-Q03, F-S01 |

A satisfied marker records that the written requirement meets the quality criterion. Seven satisfied items (003, 014, 019, 025, 028, 034, 035) carry findings about the substance of what is clearly or consistently written; the per-item notes say which.

## 7. Prioritized Remediation Sequence

| Step | Action | Depends on | Documents or Spec Kit stage |
| --- | --- | --- | --- |
| 0 | `git init` and commit the baseline as reviewed, so revisions are diffable | none | repository setup (already flagged in the handoff) |
| 1 | User clarification pass: D1 to D8 (section 8). About fifteen minutes | 0 | `$speckit-clarify`; record answers in `spec.md` Clarifications and `docs/behavior-decisions.md` |
| 2 | Rewrite the standards decision for the chosen model option; relabel or replace FR-047 to FR-049, SC-010, the scope section and A-12; add cross-route convergence and corpus-vocabulary acceptance criteria | 1 | `docs/bibliographic-model.md`, `spec.md` |
| 3 | Re-slice delivery and move deferred mechanisms to "Complexity Tracking" with readmission evidence | 1 | `plan.md` |
| 4 | Replan the bibliographic contracts: mapping registry for the demand-driven set, role table, type table, title-protection model, date and name rules, alias table, consumer-declared export profiles with a portable default, export fallback policy and oracles | 2 | `research.md` R3, `contracts/bibliography.md`, `records.md`, `interchange.md`, registry, `data-model.md` |
| 5 | Replan the Zotero route: JSON input contract, one-off extractor, key precedence, trash and merge rules, derived library identity, originals policy | 2 | `research.md` R4, `interchange.md`, `data-model.md`, `quickstart.md` |
| 6 | Revise the file and recovery protocol: link-based move, identity-checked cleanup, durability wording, fingerprint, publication proof, retention, backup scope, removal and restore of tombstones | 3, D5 | `contracts/files-and-recovery.md`, `data-model.md`, `cli.md`, `research.md` R6 and R8 |
| 7 | Dependency corrections: Typer floor and envelope pattern, `pylatexenc` pin and scope, `bibtexparser` scope and sanity checks, transliteration choice, `ty` pin, Python pin wording | D6 | `research.md` R1 and R5, `plan.md`, `dependency-audit.md` |
| 8 | Capture path additions: `add --format csljson or bibtex`, a human edit path, bulk reconciliation policies | 4 | `cli.md`, `records.md` |
| 9 | Housekeeping: stale statements, glossary, handoff note | any | F-S05, F-Q03 |
| 10 | Re-evaluate both checklists with a reviewer other than the author, run `$speckit-analyze`, then `$speckit-tasks` for slice 1 only | 2 to 8 | `checklists/`, Spec Kit |

Suggested slices. *Slice 1:* `init`, `paths`, `config show`, `add` (three input formats), `show`, `update` and edit, `search`, `list`, `key preview`, `key set`, projects and citation selection, `export` to a portable-dialect `.bib` with digest-guarded atomic replace, `.bib` import with conflict report, link-in-place resources, `open`, backup as one snapshot file plus config. *Slice 2:* collections, managed intake and reorganize with the revised protocol. *Slice 3:* Zotero migration and reconciliation policies, first real paper trial. *Slice 4:* full library export, restore verification, tombstone restore. *Deferred until demonstrated:* supporting-item import, search entry point, full BibLaTeX-dialect and CSL-JSON output profiles beyond the portable default, native inheritance and `xdata`, bundle transfers.

## 8. Remaining Questions and Acceptance Gates

### 8.1 Decisions needed from the user

- *D1 Breadth.* Should the first release model what you use (about 16 types, 50 fields, 7 roles, preserved originals for everything else, promotable later), or everything Zotero can represent? The first is recommended; the second implies option B in section 5.
- *D2 Title casing.* Keep Title Case as the stored form (recommended), with per-title protected spans so APA-style output does not lowercase proper nouns? Are you willing to have agents supply those spans at capture?
- *D3 Zotero notes and annotations.* Your 240 annotations live inside the PDFs already. Do you want the 238 child notes exported once to Markdown and linked, kept only in an archived snapshot, or imported as records?
- *D4 Export failure policy.* When a selected source has no exact mapping, export with a warning and a documented fallback (recommended), or block the file?
- *D5 Locations.* Is `~/.config/refs` still wanted given that sandboxed agents cannot write there and `git clean -fdx` in the dotfiles repository would delete the catalog? Where will the managed document library live: beside `~/Box Sync/zotero` (same volume as Downloads) or on `/Volumes/Casa` (every intake becomes a cross-volume copy)? Is a Box client still syncing that folder?
- *D6 Transliteration library.* Unidecode (GPLv2+, strict mode built in) or anyascii (ISC, strict filter supplied by refs)? This is fixed into key provenance once the first key is generated.
- *D8 Export default.* Your manuscripts feed the same `references.bib` to Pandoc citeproc, to classic `bibtex` (Elsevier template), and to Biber (dissertation PDF). Keep one portable BibTeX-dialect `.bib` per manuscript as the default (recommended, and what you do today), with richer dialects only where every consumer reads them?
- *D7 Confirmation of weakly accepted items.* Minor-word Title Case; A, An, The for sorting; numeric editions with `2E` filename token; the stopword list in A-05; lower camel case title fragment; one filing collection per managed attachment; linked versus managed modes; preserve all existing citation keys.

### 8.2 Open research

- Whether Zotero's local API returns external annotations, and whether a trial upgrade of a copied data directory migrates the 562 keys cleanly. Needed only if the local API route is wanted.
- Behavior of the link and copy protocols on non-APFS and synced storage, if D5 places the library there.
- Pandoc `-t biblatex` from CSL-JSON as an export oracle: which fields it drops, measured on the corpus types.

### 8.3 Acceptance gates before task generation

1. D1 to D8 answered and recorded with the user's own words.
2. The standards decision document states its authority accurately, and the spec's bibliographic requirements carry either a user decision reference or a proposal marker.
3. A mapping registry exists for the in-scope set in which no fact has two editable paths, verified by a script that joins the registry to the published Zotero-to-CSL crosswalk and the BibLaTeX alias table and reports zero divergences not explicitly justified.
4. The registry covers every field name and entry type present in the nine surveyed bibliographies and every populated field and creator type in the Zotero library, verified by script against aggregate counts.
5. At least one cross-route convergence fixture per in-scope type is specified: the same reference as Zotero JSON, as a legacy-dialect `.bib` entry, and as agent input must yield identical canonical records.
6. Export acceptance names its consumers and oracles: for each declared consumer, golden output from the emitted file (Pandoc citeproc under APA and one other style, with the Pandoc version pinned to Quarto's; classic `bibtex` with `elsarticle-num.bst` and zero warnings; `biber --tool --validate-datamodel`), compared per entry with a render of the canonical projection.
7. The Zotero input contract names the versions it was designed against (Zotero 6.0.37, userdata 121, global schema 28, Better BibTeX 7.0.0) and its key precedence.
8. The file protocol states its durability claim in terms it can meet, and each crash point has a recovery outcome derived from recorded inode identity.
9. `plan.md` defines slice 1 with its own exit criteria, and `$speckit-tasks` is run for that slice only.
10. Both checklists re-evaluated by someone other than the author of the revisions.

## 9. Addendum, 2026-09-21: Compatibility Follow-ups From User Discussion

These points arose after the report was handed off. They refine existing findings and add no new severity counts. The user asked for CSL-JSON output and Zotero API JSON output to be recorded as backlog items; both are now rows in the deferred table of `docs/requirements-review.md`. The user's stated position on Zotero compatibility: not a priority, but refs "should not be entirely incompatible either". Zotero cannot open a refs catalog under any design; compatibility means import and export through published formats.

| Item | Refines | What to change, and where |
| --- | --- | --- |
| A-12 is out of date | F-S03, F-I05, F-I10 | `spec.md` A-12 excludes public CSL export. The user has now placed CSL-JSON output on the backlog, so A-12 should describe it as deferred, not excluded. |
| Native type label must be settable, validated, and present from slice 1 | F-B05, section 5.1 option D, section 7 slices | `records.md` and the type table: agents must be able to supply the native item-type label on records that never came from Zotero, validated against the three-way type table. Include it in the first slice's record schema; retrofitting it across existing records is tedious, and without it only migrated records can return to Zotero with exact types. |
| Derived Zotero library identity is a prerequisite, not only a robustness fix | F-I06 | `interchange.md`, `data-model.md` `origin_identities`: store the Zotero library URI (`users/<id>`, `groups/<id>`, or `users/local/<key>`) with each item key at first import. Export back to Zotero and related-item resolution depend on it, and it cannot be recovered later without re-importing. |
| Precedence rule for per-entry originals | F-A06, F-I06, F-I09 | `bibliography.md` or `interchange.md`: when writing any outward format, current canonical values always win; a preserved original supplies only fields refs does not model. Field provenance, which the data model already has, distinguishes the two. This keeps originals from becoming a second authority (F-B01). Storing originals as Zotero API JSON per item means the future Zotero writer's input is already in its output format. |
| Online video as a bookmark that can become a citation | F-B09, vision "save casually", section 5.1 strongest counter-argument | No new model element. A saved video URL starts as a web bookmark; when cited, the same source is enriched to CSL `motion_picture` with native label `zotero: videoRecording`, literal channel author, upload date as `issued`, platform as publisher, running time in `dimensions`. `.bib` output uses `@online` for the portable profile (`@misc` for classic `bibtex`). Raw media files are ordinary resources under FR-025. Worth one convergence fixture when web capture is specified; it also shows that the audiovisual limits of CSL do not bite for this user's foreseeable material. |

Effect on decision D1: these commitments remove most of the practical advantage of a Zotero-shaped core (an easy way back), which makes the CSL-shaped core the lower-risk choice. They do not change any recommendation in sections 3 to 8.

## 10. Addendum, 2026-09-21: Corrections After Review by the Authoring Session

The authoring session reviewed this report and section 9 in two rounds and agreed with the verdict. This addendum records where that review corrected or tightened the audit. Earlier sections are left as written so the original findings and their corrections stay traceable. The authoring session did not reproduce the experiments; the [preserved evidence](evidence-2026-09-20/README.md) remains audit evidence.

### 10.1 Corrections to earlier conclusions

| Corrects | Original statement | Correction |
| --- | --- | --- |
| Section 7 step 10; section 8.3 gate 9 | Run `$speckit-analyze`, then `$speckit-tasks` | Reversed. The analyze skill requires a complete `tasks.md` and aborts without one. Order is tasks, then analyze. If tasks cover only slice 1, `plan.md` must state the slice boundary so uncovered requirements are not reported as gaps. |
| F-A07 recommendation | `backup --include-managed` using "hard links or clones" | Clones or real copies only. A hard link shares the inode and gives no independent copy; it protects against unlinking a name, not against modification. |
| F-A01; executive summary item 5 | A hard link of the source is "atomic, lossless" | Only link creation is atomic and collision-safe. The move is link, catalog commit, unlink, with an intermediate state of two names for one file. That state is benign for crash recovery but is not an independent copy: a program writing the source in place during the window is inherited, where a copy protocol would detect it. The recommendation stands for completed downloads; the contract must state the precondition. |
| F-A03 | "`os.fsync` is not durable on macOS" | Shorthand. Apple distinguishes flushing to the device from the stronger request made by `F_FULLFSYNC`. State the intended guarantee first (process crash, or power loss), then select the mechanism. The measured timings and the recommendation are unchanged. |
| F-B07 | "Drop database-level annotation import (nothing is lost; the PDFs hold them)" | Overstated, and now conditional. `isExternal=1` is Zotero's flag for annotations it found embedded in the file, but no real PDF was opened. [X] The 240 annotation rows belong to 9 distinct linked-file attachments (2 to 72 annotations each). The gate is a read-only comparison on those 9 files that checks correspondence and accessibility of annotations, not only equal counts. It needs the user's authorization because it reads private files. |
| Section 7 slices | Backup in slice 1, "restore verification" in slice 4 | Slice 1 must include a demonstrated restore of its own snapshot into a second home. What stays in slice 4 is the bundle format, the `restore` command's validation machinery, and full library export. Every usable slice needs a proportionate, demonstrated recovery path. |
| Section 5.1 option D | "One authority per fact by construction" | True only inside the core. Extension boundaries and per-route mappings must demonstrate it through the convergence fixtures. |
| F-B01; executive summary item 2 | "51 of 121 Zotero fields" presented as duplicates | 51 counts fields whose registry path diverges from Zotero's published crosswalk. Some crosswalk entries are loose approximations (`programmingLanguage` to `genre`, `applicationNumber` to `call-number`, `session` to `chapter-number`, `priorityNumbers` to `issue`, `codeNumber` to `volume`, `committee` to `section`); collapsing those would create a false equivalence of the opposite kind. The clear duplicates are the type-of-work, number, medium, and institution-versus-publisher families and the identically named pairs. Collapse only after per-row semantic review. The thesis and report counterexamples, which the authoring session confirmed in the registry, stand. |
| F-S04; decision D7 | A table of eight items for reconfirmation | Pruned. A short reply can be valid approval; its meaning depends on the proposal it answered. The defect is provenance: record the question and options, the user's literal reply, and the resulting interpretation separately, and do not present a paraphrase as a quotation or add choices to it (the Clarifications section includes a copy mode from an option the user did not pick; "Preserve existing keys" is labelled "Agreed" without a user statement). One item merits a focused question: the structure added to A2 (single filing collection per managed attachment; linked versus managed modes), because Story 4 and the transfer protocol rest on it. |
| F-S03, F-I05, section 9 on A-12 | "A-12 excludes CSL" | A-12 says these are "outside this feature". It should distinguish outside this feature from excluded from the product. The backlog rows keep CSL-JSON and Zotero API JSON output as planned possibilities; they do not place either in slice 1. |
| Section 9, online video row | "`@online` for the portable profile (`@misc` for classic `bibtex`)" | Self-contradictory, since the portable profile exists to be readable by classic `bibtex`. The entry type follows the destination's declared consumers: `@misc` with `howpublished` and `url` for the portable default, `@online` only where every consumer reads it. |
| Section 9, closing paragraph | The compatibility commitments "remove most of the practical advantage of a Zotero-shaped core" | Stronger than the evidence supports. They preserve options; they do not guarantee a cheap return. Field mappings, relationships, attachment behavior, and a demonstrated route into Zotero still need validation. The D1 recommendation is unchanged, but it should not lean on this claim. |
| F-D01 | none | Confirmed as written: nothing found establishes that a refs-owned parser is preferable; keeping `bibtexparser` narrowly scoped remains the lower-risk choice. |

### 10.2 Agreed refinements to recommendations

- *Export failure policy (F-I01, F-I02).* Fix mapping coverage first; ordinary `@misc` references must not need ritual review because a table is incomplete. Then classify each transformation as one of four: incomplete metadata that can be represented faithfully (warn); a known, documented fallback mapping (warn, recorded in the report); an enumerated semantic loss (blocks output); or an unknown or unassessed mapping, reported as such and never treated as safe by default. The blocking list is closed and concrete, for example the set of people cited as authors would change, a fallback entry type changes the in-text citation, or the issued date is dropped; omitting an access date is not equivalent. Report all affected entries in one pass. A waiver binds to the specific loss, the source revision, and the destination profile, and lapses when any of those changes.
- *Precedence of preserved originals (section 9).* "Current canonical values win" must cover deletion. Distinguish a field refs does not model, a modeled field that is absent, and a modeled field deliberately cleared or superseded. Originals may supply approved passthrough data for the first case only. A cleared field must not be recovered from an original, and a type change must not resurrect fields incompatible with the new type.
- *Compatibility commitments (section 9).* The native type label is settable and validated from slice 1 but optional, so casually captured records need no guess. Zotero library and item identity is provenance, not refs' own identity, and holding it is not permission to update those Zotero objects in any future export.
- *Agent write access (F-A09).* This session's sandbox does not decide where the catalog lives, which remains the user's choice. It is not peculiar to one session either: Codex's default sandbox and the `cass-search` skill's documented writable-roots requirement show the same pattern. Keep the resolved-path `home_not_writable` diagnostic and the documented access requirement whatever location is chosen.
- *Redesign method (section 7 step 4).* Lead with a few cross-route examples, select the model, and let the registry follow demonstrated mappings. Do not generate another large registry first.

### 10.3 Revised next steps

1. Commit the reviewed baseline to Git when convenient; it is not a prerequisite for the decisions.
2. Resolve four product choices: metadata breadth (D1), usability of Zotero notes and annotations (D3, with the 9-file check), export fallback policy (D4, in the four-class form above), and the content of the first usable slice, plus one targeted clarification on A2's added structure. Title-case protection, locations, transliteration library, and the portable `.bib` default proceed as design decisions to confirm in passing.
3. Work a few cross-route examples, select the canonical model, then revise the affected documents, including decision provenance in `spec.md` Clarifications and `docs/behavior-decisions.md`.
4. Independent review of the revisions and re-evaluation of both checklists by someone other than their author.
5. `$speckit-tasks` for the declared slice, then `$speckit-analyze`.

Severity counts are unchanged. The checklist assessments are unchanged; the note on CHK004 should be read with the annotation correction above.

## 11. Addendum, 2026-09-21: User Decisions on the Open Items

Recorded in the provenance form agreed in section 10: the question and options as posed, the user's literal reply, and the interpretation, kept separate. Each question was preceded by a written brief giving context, options, a recommendation, and the strongest argument against it. Replies were selections from a fixed option list with a free-text alternative available; the literal reply is the selected option label. These are inputs for `$speckit-clarify` and for `spec.md` Clarifications and `docs/behavior-decisions.md`, which the authoring session owns.

| # | Question as posed | Options offered | Literal reply | Interpretation and consequences |
| --- | --- | --- | --- | --- |
| 1 (D1) | How much bibliographic vocabulary should the first release model? | A: What I use; B: Everything Zotero has; C: Repair current design | "A: What I use (Recommended)" | CSL-shaped core, a short justified extension list, optional native type label, every imported entry preserved verbatim and promotable later without re-import. FR-047 to FR-049, SC-010, the scope section and A-12 are to be rewritten accordingly. The per-row semantic review in section 10.1 still applies before any path is collapsed. |
| 2 (D3) | What should refs do with Zotero's notes and annotation records? | A: Archive only; B: Fold into context; C: Export to Markdown; D: Import as records | "B: Fold into context (Recommended)" | The 238 short child notes go into each source's searchable context, marked as imported, subject to import preview. Attachment outline notes and annotation rows are not imported. Related-item links are kept as simple pairs. A dated copy of the Zotero data directory is archived outside the catalog. The supporting-item subsystem (FR-049, `supporting_items`) is not needed for this. |
| 2a | May I run the read-only check on the 9 annotated PDFs now (counts and mismatches only)? | Yes, run it; Not now | "Yes, run it" | Authorized and run; result below. |
| 3 (D4) | Under the agreed four-class export policy, how should unknown or unassessed mappings be handled? | A: Block, with override; B: Warn and export; C: Current strict rule; D: Always export | "A: Block, with override (Recommended)" | Coverage first. Incomplete-but-faithful and documented-fallback cases warn. Enumerated meaning-changing losses block unless waived per loss, source revision, and destination profile. Unknown mappings block by default; a single-run flag exports anyway and records that in the report. Blocking writes no file, leaves the existing bibliography untouched, and reports every affected entry in one pass. |
| 4 | How much file handling belongs in the first usable slice, alongside the agreed capture-to-export core? | A: Core only; B: Core + copy-only intake; C: Core + full managed intake; D: Current plan | "B: Core + copy-only intake (Recommended)" | Slice 1 is the agreed core (section 7 as corrected in 10.1, including a demonstrated restore) plus non-destructive, verified, no-overwrite copy of new files into the library's `Unfiled` folder. The user's earlier choice of move as the intake default is unchanged and is delivered in slice 2 with collections and reorganize. Slice 1 does not depend on the library-location decision. |
| 5 (A2) | Which collection-and-file structure do you want for slice 2? | A: Confirm as designed; B: Derive mode from location; C: Decouple files from collections | "B: Derive mode from location (Recommended)" | Collections, projects and tags stay separate; one filing collection per library file; explicit, selected, previewed reorganize. A file is managed if it is recorded under the library root by root name; anything else is linked and never touched. No stored mode flag, no adopt-without-move state outside the root. Setting a filing collection replaces "adopt" for files already under the root. A per-file "leave in place" marker is the fallback if exemption from reorganize is ever wanted. |

Context the user was given for item 2, measured read-only without reading content [X]: child notes have a median of 113 characters, 233 of 238 are under 200, about 25 KB in total on 157 sources; the 246 attachment notes total about 4.4 MB, all on linked PDFs, all built from list items and links, consistent with ZotFile-generated PDF outlines [N].

### Annotation check result (closes the condition in 10.1)

[X] Script `evidence-2026-09-20/zotero/check.py` with pypdf under `uv run --no-project --python 3.14`. The 240 Zotero annotation rows belong to 9 linked PDFs. In 8 files every row has an embedded PDF annotation on the same page at an overlapping rectangle, and per-file counts agree exactly (6, 9, 12, 24, 27, 39, 49, 72). Overall 239 of 240 rows matched. The unmatched row is in a 283-page file that holds two annotations for Zotero's two rows, one of them a malformed object with no subtype that the library could not classify; a second file has nine malformed annotation objects and one square markup Zotero never imported, with no Zotero row affected. All three rows that carry a comment have the comment stored in the PDF annotation (`check2.py`). Limits: this establishes presence and position, not rendering in any particular viewer; matched types were highlights and underlines. Recommended before retiring Zotero: open the one file with the malformed annotation in a viewer.

### Still to confirm in passing

Title-case protected spans (D2), catalog home and library location (D5), transliteration library (D6), and the portable `.bib` default (D8) were agreed by both sessions to proceed as design decisions confirmed during revision, not as a separate reconfirmation pass.

## 12. Addendum, 2026-09-21: User Decisions on the Four Design Confirmations

Same provenance form as section 11. The four questions were posed by the authoring session; each was briefed here with context, options, a recommendation, and the strongest argument against it. Literal replies are quoted exactly, including the user's own clarifications.

| # | Question as posed by the authoring session | Options offered here | Literal reply | Interpretation and consequences |
| --- | --- | --- | --- | --- |
| 1 (D2) | Should title-case protection use explicit protected spans (including protection imported from BibTeX braces), while keeping the displayed title as ordinary Unicode text? | A: Per-title terms + flag; B: Offset-based spans; C: Inline braces; D: Global list only | "A, with a clarification. APA etc should govern exported material. My prefs for internal representation do not superceed that. I just don't want to see sentence case titles in the database. They are an abomination." | Stored and displayed titles are Title Case, plain Unicode. Protection is a per-title list of terms (not character offsets, which break on edits; this promotes the existing optional `protected_terms` field in `records.md`) plus a whole-title preserve-case flag for fully braced titles. Seed both from imported braces, distinguishing case protection from braces that only wrap LaTeX accents or commands; agents supply terms at capture; the global list only suggests. The citation style governs output: `.bib` export emits Title Case with braces, which is what sentence-casing styles expect; CSL-JSON export (backlog) must derive sentence case at export using the term list, because CSL styles assume sentence-case input. `langid` is required at export for non-English titles. Unprotected mid-title capitals warn; under the section 11 export policy this is not a blocking loss. |
| 2 (D8) | Should the default bibliography profile be portable BibTeX for Pandoc, Biber, and classic BibTeX, using `@misc` for web references? | A: Portable default, richer by declaration; B: Portable only; C: BibLaTeX default; D: Auto-detect per export | "A: Portable default, richer by declaration (Recommended)" | Default output is traditional BibTeX dialect (`year` and month macro, `journal`, `address`, `school` or `institution`, classic types, `@misc` with `howpublished` for web items, plus `doi`, `url`, `urldate`). A destination may later declare its consumers in the project file to receive `@online`, `@software` and similar when every declared consumer reads them. Slice 1 builds only the portable profile; the declaration is designed in, the richer profile waits for a manuscript that needs it. Detection from Quarto configuration may suggest a declaration at adoption time but is never a silent rule. In the portable profile a case-only citation-key collision is an export error, because classic `bibtex` is case-insensitive and silently skipped the twin in testing. The cost of `@misc` under citeproc (generic instead of web-page formatting) was stated to the user as real but unmeasured. |
| 3 (D6) | Should I evaluate AnyAscii as the preferred transliteration package, with its exact version recorded in key provenance and explicit overrides for unsuitable results? | A: AnyAscii; B: Unidecode; C: No dependency | "C: No dependency (Recommended)" | Built-in Unicode normalization plus a small refs-owned table for non-decomposing Latin letters (for example `ß` to `ss`, `æ` to `ae`, `ø` to `o`, `ł` to `l`, `đ` to `d`, `þ` to `th`, `ð` to `d`, `œ` to `oe`, `ı` to `i`). Any other letter, and any non-Latin name, requests the existing explicit key-author override; it never yields a silently wrong token. The policy ID is refs-owned and does not drift with a package. AnyAscii with a refs-owned strict filter is the named fallback if non-Latin authors appear; policies are versioned and assigned keys never change, so adopting it later has no retroactive effect. Remove Unidecode and the `creator-unidecode-1.4.0-v1` policy from the plan and configuration contract. |
| 4 (D5) | What catalog home and document-library location should the revised design target? Should the library use the existing `~/Box Sync/zotero` tree, and is that folder still synchronized by a Box client? | First round (withdrawn, see below). Second round: A: One refs folder on Casa; B: Separate visible folders on Casa; C: Catalog in `~/.config/refs` | First round: the user declined to answer and clarified (quoted below). Second round: "A, but /casa/refs/cat and /casa/refs/lib" | One visible parent on the Casa volume: catalog database, lock and staging in `/casa/refs/cat`; PDFs in `/casa/refs/lib`, which is the only part ever shared for sync. `config.toml` stays in `~/.config/refs/` and points at both, so sandboxed agents that do not load a shell profile still resolve them. Recommended to the user and not contradicted: write the canonical `/Volumes/Casa/refs/...` form in configuration, since `/casa` is a symlink and alias matching has failed before (see `docs/workflow-research.md` on CASS). Note the data folder `/Volumes/Casa/refs` is distinct from this source tree at `/Volumes/Casa/dev/refs`. |

### The user's clarification on item 4, verbatim

"the fact that 'box sync' is inactive is irrelevant to the decision but a good reminder that I need to set it up. I specifically dislike the idea of using XDG folders for the pdfs: `~/.local/share/refs/` this is EXACTLY the case I want to avoid as, to the average mac user, it is invisible. I agree mine should be moved to somewhere on /casa (archives?) and renamed / reconfigured for sync (syncthing?) in a way that still gives me easy access to them. the fact that the current pdf folder is stale is only evidence that I need refs and to do some cleanup that I've been putting off because it is slow and manual with Zotero, not that I don't use it"

Interpretation: my first-round proposal placed only the catalog database, not PDFs, under `~/.local/share`; the user's visibility principle applies to the catalog as well, and that recommendation is withdrawn. A living library should not sit under `/casa/archive`; the dated Zotero data-directory snapshot from section 11 item 2 can.

### Facts established for item 4 [X]

- No Box client is installed or active on this machine (no application, application-support folder, logs, or launch agents). `~/Box Sync/zotero` is an ordinary local folder: 530 files, 4.2 GB, newest file dated 2025-06-22. The user intends to set up sync; Syncthing is installed via Homebrew.
- Vault notes linking into the current PDF tree by path: 5 notes, 11 references. An earlier statement in this audit that relocation would break Obsidian links materially overstated the cost.
- `/Volumes/Casa` and the home volume are separate APFS volumes, so every intake from `~/Downloads` into `/casa/refs/lib` is a cross-volume copy.

### Design consequences of item 4

- F-A01 ordering changes: build the copy, verify, publish, then delete path first; the same-volume link path is an optimization that this user will rarely exercise. Creation date cannot be preserved across volumes; say so. Findings F-A02 to F-A05 apply unchanged.
- The live catalog must never be inside a synced folder. Stage in `/casa/refs/cat` (same volume as the library, so final publication stays atomic) so half-written files are never synced. `resource check` reports stray `sync-conflict` files and never acts on them. Syncthing is sync, not backup; recommend file versioning on the share.
- Because resources are stored as a named root plus relative path, relocating the existing 511-file tree intact is one `mv`, one configuration line, and a resolve check, with no per-file operation. Nothing needs to move before slice 1: create `/casa/refs/lib/Unfiled`, point refs at it, and copy-only intake works. At migration the existing files import under a named root pointing at the old tree; the user moves it when ready. Renaming and cleanup of individual files is slice 2 `reorganize` with previews.
- `contracts/configuration.md` home resolution changes: configuration location and catalog location are separate settings, and A-04's single-home order needs rewriting. Keep the explicit failure when the catalog path is missing (for example the volume is not mounted); never initialize elsewhere.
- F-A09's `home_not_writable` diagnostic and documented agent allowlist entry now refer to `/Volumes/Casa/refs/cat`.

All nine user decisions (sections 11 and 12) are now recorded. Nothing remains open between the two sessions.

## 13. Addendum, 2026-09-21: Right-Sizing, Constitution 2.0.0, and the Git Baseline

Recorded in the same provenance form. These followed the authoring session's revision, which incorporated the nine decisions faithfully but left slice 1 at about 41 commands and 15 to 17 tables, with governing text grown from about 44,600 to 49,468 words.

| Topic | What the owner was shown | Literal reply | Interpretation |
| --- | --- | --- | --- |
| Scale and role | A 1 to 10 calibration (5 right-sized): original plan about 8.5, revised direction about 6, slice 1 as scoped 5 | "I will rely on you to help keep us there without poo-pooing too much. mostly that should come from you asking me what we really need when the feature-creep, over-engineering, and gold-plating sets in" and "it should be good, well designed, professionally built and packaged, not elaborate" | Guardrails recorded in `AGENTS.md` (Right-Sizing) and `docs/right-sizing.md`, with sibling-tool calibration, budget, never-cut floor, provenance rule, use-before-extend, and four checkpoints. |
| Allowance | Whether slice 1 may exceed a 5 | "I think it is natural for well-architected systems to add some up-front overhead that might move us from a 5ish to a 6ish in the first slice. if you agree it is a reasonable, metered, up-front investment in good design, I would allow it" | Agreed on condition that the extra is seams (cheap now, hard to retrofit), not surface (easy to add later). Metered as about 15 commands, 10 tables, 3,500 lines. |
| Items 1 to 3 | 1: Git baseline in two commits; 2: Principle II wording narrowed so files elsewhere stay linked and are never moved, renamed or deleted "except through an explicitly invoked intake"; 3: keep the internal search boundary in slice 1 and move the entry point and proof package to "when a second implementation is evaluated", in the same 2.0.0 amendment | "proceed with 1-3" | Constitution amended to v2.0.0 (Principles II, IV, V); see its Sync Impact Report for exact text and the dependent artifacts still to synchronize. Principle IV's wording was adjusted as a necessary consequence of item 3 so that IV and V agree. |

The pre-revision archive made by the authoring session was verified against the hashes in section 2.1: `spec.md`, `plan.md`, `data-model.md`, `bibliography.md` and the registry match exactly, so it is the audited state. The sandbox of this session cannot create `.git`; the owner runs the prepared script to create the history (audited baseline; revision plus audit record plus guardrails; constitution 2.0.0).

Next: the first right-sizing checkpoint, run as a trim of slice 1 toward the metered 6 by moving surface (export waivers and projection records, the operations journal and recover commands, batch resume and reconcile, convenience commands, the search entry point and proof package) to later slices or the backlog, with governing words going down. Nothing on the seam list or the never-cut list is a candidate.

