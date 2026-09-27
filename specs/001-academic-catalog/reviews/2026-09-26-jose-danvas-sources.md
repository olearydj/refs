# JOSE Danvas sources pass — 2026-09-26

Completed against refs 0.7.0 at `26b56cb`, with publication at `af6ce45`. Catalog changes are applied; the candidate bibliography is **not adopted**. The owner decides whether the wording changes land before or after pre-review. Nothing is retired: JOSE’s `paper.bib` still derives from `references.bib` through the unchanged sync script.

## Backup and scope

Validated backup: `/Volumes/Casa/refs-backups/2026-09-26-before-jose-sources`, catalog revision 4106. SHA-256: catalog `6d97867fc8cb379d67c7ddf317304459212b59e3863eed1606cb35d6024bac7c`; configuration `61b3093d2ecf1caa6a5dfb3360fac24ac486a5590cdd443e37c54e249a16d0d2`; resource manifest `ef6e8ffaa8f40dd8381a5730031096396436fe73a659e541875c2f14baf64bb9`. This catalog backup inventories external resources; it does not contain their bytes.

The project’s `docs/phase-4-literature-and-related-software.md` names no examined version for any of the four repositories. All four version fields remain absent. Current repository commits below pin the new captures, not the historically examined versions. The former accessed dates (2026-09-01 for Bosk, jjuanrivvera and Weng; 2026-08-30 for CanvasAPI and Instructure) are retained in context. All five accessed dates now read 2026-09-26, the capture date in America/Chicago (retrieved on 2026-09-27 UTC).

Guarded updates started at revision 2 for each record. `bosk2026canvaslms`, `ucfopen2026canvasapi`, `jjuanrivvera2026canvascli` and `weng2026canvascli` now have type `software`, kind `repository`, genre `Source code repository`, publisher `GitHub`, and loc `unfiled`. `list --kind repository` returns exactly these four. The obsolete BibTeX `online` native-type labels were cleared when retyping; preserved original import entries remain available. Instructure remains `webpage`, with container-title `Canvas LMS REST API Documentation`; normalization adds acronym protection for that new field. Authors, titles, and their existing title protection are unchanged. PyPI notes contain `https://pypi.org/project/canvaslms/` and `https://pypi.org/project/canvasapi/` respectively; current PyPI releases were not used to guess examined versions.

## Five unlinks and retained context

Unlinked the shared project literature-review note from each of those four repositories and `instructure2026canvasapi`. The project document remains in place, unchanged (SHA-256 `f1e3a77a1d5d2afe0121beeccebe4fd8112fb78fb2e0bdfb9ae215790554f8a9`). Source-specific context retains the review’s descriptions: Bosk’s POSIX composition; CanvasAPI’s object API and role as Danvas’s underlying library; jjuanrivvera’s broad API, MCP, Agent Skill and host guards; Weng’s JSON, mutation gates, read-only mode and audit logging; and Instructure’s official REST API scope. Context identifies the review and its date; these are documented claims, not independent behavioral audits.

## Captures and eleven attachments

Four single-file JSON captures each contain the full UTF-8 README fetched at the default branch’s observed commit, GitHub repository metadata JSON, commit metadata, retrieval timestamps and HTTP provenance. README bytes were checked against GitHub’s blob SHA. Scratch filenames include the repository, full commit hash and capture date. Bundling the README and API metadata keeps one capture attachment per repository, hence eleven total attachments rather than fifteen. The Instructure capture is the API index HTML. Remote badges, images and linked pages were not crawled.

All five scratch captures were attached with `resource add --move --label capture`, yielding conventional names under `/Volumes/Casa/refs/lib/unfiled/`; scratch inputs no longer exist. Their original hash/date filenames remain in resource provenance, and commit/date also remain inside each JSON bundle. The six existing article PDFs were already attached and were neither fetched again nor moved in this pass. All eleven final file hashes match the catalog; the five capture hashes match their pre-move scratch bytes.

| Key | Default branch | Captured commit | Examined version |
| --- | --- | --- | --- |
| `bosk2026canvaslms` | `master` | `d64e8d50c50b93e0592ded1496a27a9b2ec8f6a9` | Not recorded; left empty |
| `ucfopen2026canvasapi` | `develop` | `513588f3077fbc7470c28ae56fa541b5ddce6849` | Not recorded; left empty |
| `jjuanrivvera2026canvascli` | `main` | `d69e80bca3923905651fee58172b67ccfa75f72b` | Not recorded; left empty |
| `weng2026canvascli` | `main` | `9bcd21e348f2c48eb5aef9a1a6020c8029639548` | Not recorded; left empty |

All following paths are relative to `/Volumes/Casa/refs/lib/unfiled/`.

| Key | Final filename | SHA-256 |
| --- | --- | --- |
| `bainbridge1983ironies` | `IroniesOfAutomation-1983.pdf` | `0999b9f8b33da251486db93df85dc868912fdee66fde885ed93ff1ed144892e6` |
| `bosk2026canvaslms` | `CanvaslmsACLIToCanvasLMS-2026-capture.json` | `1ba7a5a936d3f1b7fae9bc43bd6e61b98cdcb7c1b1e184520e9431860049d2d5` |
| `instructure2026canvasapi` | `CanvasLMSRESTAPIAndExtensionsDocumentation-2026-capture.html` | `56c7f38ed257add73d4b5ae4b4682eaf9ac5abffeee1ddd54773e3a3aa0cb5ff` |
| `jjuanrivvera2026canvascli` | `CanvasCLI-2026-capture.json` | `314d48d43d1bac0b5f62d8a2af26c7a4edff4e8790c659d94f8f238968a25503` |
| `jupyter2019nbgrader` | `NbgraderAToolForCreatingAndGradingAssignmentsInTheJupyterNotebook-2019.pdf` | `6668b7d29b7b52af07836fb3ce98ed6a8da2657e8003137f8ae8c180e935c7e4` |
| `lee2015canvasinteractions` | `ApplyingDataMiningMethodsToUnderstandUserInteractionsWithinLearningManagementSystemsApproachesAndLessonsLearned-2015.pdf` | `8097ee434b2c6aace80aa8ff857dce141def9bce894afbf23461b5d0e1980a8d` |
| `nijhuis2003coursemanagement` | `UsingAWebBasedCourseManagementSystemAnEvaluationOfManagementTasksAndTimeImplicationsForTheInstructor-2003.pdf` | `72985095075c6ec517ffe834e3339e13cae241fc9367f9d4a6f71b3dc069e1d2` |
| `ro2019orgcoursepack` | `OrgCoursepackAModularAndReusableTeachingMaterialsTemplateInOrgMode-2019.pdf` | `4e6ce2c2a08d64d06bfad29f5cbd352637a3199522cd14592cd0d2bbb93a6eb0` |
| `sandve2013reproducible` | `TenSimpleRulesForReproducibleComputationalResearch-2013.pdf` | `35648a3880bdd8bf30e8212a3847b7bd35f504ee5ccbd1ad3856d206acd181db` |
| `ucfopen2026canvasapi` | `CanvasAPIPythonAPIWrapperForInstructureSCanvasLMS-2026-capture.json` | `8147c6186dbdc067492552eb8df0939a37fa56ebb8b1e9881ea6d9424ff5e722` |
| `weng2026canvascli` | `CanvasCliAgentFriendlyCLIForCanvasLMS-2026-capture.json` | `b70e1458b46e42e15fdb7808d7080bb20bd3b56094a4ab587f52c30b7ab22432` |

## Export gate: exact reference wording

Scratch export: `/private/tmp/refs-jose-sources-2026-09-26/references.json`, profile `csl-json-v1`, eleven entries. Quarto 1.10.18, bundled Pandoc 3.10, the project’s own PDF settings and default Chicago Manual of Style 18th edition (author-date). Both isolated full-paper renders succeeded. Fresh baseline PDF text is identical to the current project PDF. The paper body is identical; reference order is unchanged. Entry-by-entry citeproc comparisons and the full PDF text diff agree: exactly five references change, the four software entries and Instructure. The other six are identical, including `nbgrader` and `Org-mode`; protected names remain intact.

The comparisons below give exact rendered words and punctuation, with line wrapping removed. Software titles change from quoted webpage titles to italicized software titles. Chicago adds “Source code repository. GitHub, released.” even with version unset; “released” is style-generated wording, not a newly asserted release version. Instructure gains its requested container title. Accessed dates and PyPI notes do not print in this style.

### bosk2026canvaslms

Before: Bosk, Daniel. 2026. “canvaslms: A CLI to Canvas LMS.” https://github.com/dbosk/canvaslms.

After: Bosk, Daniel. 2026. canvaslms: A CLI to Canvas LMS. Source code repository. GitHub, released. https://github.com/dbosk/canvaslms.

### instructure2026canvasapi

Before: Instructure, Inc. 2026. “Canvas LMS REST API and Extensions Documentation.” https://canvas.instructure.com/doc/api/.

After: Instructure, Inc. 2026. “Canvas LMS REST API and Extensions Documentation.” Canvas LMS REST API Documentation. https://canvas.instructure.com/doc/api/.

### jjuanrivvera2026canvascli

Before: jjuanrivvera. 2026. “Canvas CLI.” https://github.com/jjuanrivvera/canvas-cli.

After: jjuanrivvera. 2026. Canvas CLI. Source code repository. GitHub, released. https://github.com/jjuanrivvera/canvas-cli.

### ucfopen2026canvasapi

Before: University of Central Florida Center for Distributed Learning. 2026. “CanvasAPI: Python API Wrapper for Instructure’s Canvas LMS.” https://github.com/ucfopen/canvasapi.

After: University of Central Florida Center for Distributed Learning. 2026. CanvasAPI: Python API Wrapper for Instructure’s Canvas LMS. Source code repository. GitHub, released. https://github.com/ucfopen/canvasapi.

### weng2026canvascli

Before: Weng, David. 2026. “canvas-cli: Agent-Friendly CLI for Canvas LMS.” https://github.com/thedavidweng/canvas-cli.

After: Weng, David. 2026. canvas-cli: Agent-Friendly CLI for Canvas LMS. Source code repository. GitHub, released. https://github.com/thedavidweng/canvas-cli.

## Verification and findings

Verified eleven attachment digests, all five moved inputs absent, all five former note resource IDs absent, four repository-kind results, six unchanged article source/resource rows, SQLite integrity and foreign keys, unchanged authors/titles and existing title protection, and unchanged hashes for ten publication files: `paper.qmd`, `references.bib`, `references.json`, `_quarto.yml`, `.refs.toml`, the sync script, JOSE’s `paper.bib` and `paper.md`, the current PDF, and the literature-review note. No publication files were edited. No runtime code changed, so verification used catalog invariants, file hashes and actual consumer renders rather than rerunning the code suite.

No catalog command refused or warned, and no export mapping was lost. The first network attempt was sandbox-blocked; the authorized public fetch succeeded with network permission. The operational accommodation is the single-file JSON capture bundle. Surprises: the historical comparison supplies no versions; the style adds bare “released”; Instructure changes too when its container title is supplied. The accepted conversion fixture is deliberately unchanged because this candidate has not been adopted. A routine project re-export would now carry these pending metadata changes, so it must wait for the owner’s wording decision.

This pass implements the owner’s source decisions without proposing runtime features. Repository kind prevents a source-code repository from being treated as a generic webpage; contextual notes instead of a linked review prevent mistaking commentary for the source; commit-pinned captures prevent moving default branches from erasing the evidence examined today; the scratch gate prevents unreviewed bibliography wording changes during pre-review. The separate JOSE target still needs replacement of the sync script’s bibliography half and its own render gate. Nothing is retired.
