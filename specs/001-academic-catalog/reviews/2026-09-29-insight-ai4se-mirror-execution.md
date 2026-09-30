# INSIGHT and AI4SE mirror execution — 2026-09-29

**Complete in the catalog; documentation ready for session 1's subagent.** Two new records, two verified managed copies, five existing records reused unchanged apart from project memberships, and cited-only projects with six and four works. The internal technical report is dropped entirely. Neither paper was edited, exported or rendered. No export target or conversion-register row was added.

## Backup and approved scope

The owner approved the proposal through `comms/2026-09-29-221022-s1-mirror-proposal-decision.md`, with duplicate copies in unfiled instead of links and omission of the internal report. The proposal now records both amendments. Backup `/Volumes/Casa/refs-backups/2026-09-29-before-insight-ai4se-mirror` was created and its manifest/database/resource inventory validated before intake. External file contents are not included in this catalog backup.

## Import and record completion

Extracted only the two approved BibTeX entries from INSIGHT's existing file, preserving their exact entry bytes. Dry run and actual import both reported **2 applied, 0 unchanged, 0 conflicts, 0 invalid**. Each source's preserved BibTeX original was checked byte-for-byte against the paper. Then replaced the canonical metadata with the approved speech/patent fields, preserving the supplied citation keys. The imported `misc` native label initially caused the dry-run retype to refuse the contradictory type; cleared that label during the approved retype, leaving the original evidence intact. No failed mutation or duplicate import resulted.

| Key | Record ID | Canonical result |
|---|---|---|
| `ledford2024mbe` | `f6278c9a-847d-48f1-aced-a7f0f36ccb41` | `speech`: Data Element Mapping and Analysis (DEMA): A Systematic Method to Implement a Complete Digital Thread |
| `ledford2024patent` | `e1762317-472a-4a5e-ba90-327609c91309` | `patent`: Physical Components Using Data Element Mapping and Analysis |

The talk has Allison B. Ledford, April 17, 2024, the MBE & QIF Summit at MxD in Chicago, the NIST deck URL and protected DEMA spelling. The patent has its official title, all four full inventor names, US 12,131,134 B1 and October 29, 2024, US jurisdiction, USPTO authority and the Google Patents URL. Neither has invented context. Exact metadata, original hashes and CLI receipts are in the [evidence JSON](2026-09-29-insight-ai4se-mirror-execution.json).

The five reused records retained every field, revision and resource; only their `projects` associations gained the approved memberships. The owner's author name remains Danny J. O'Leary. No `oleary2025techreport` record exists, and nothing remains pending for it.

## Sources and verified copies

Both source PDFs remain in dema-docs, unchanged. Each copy was dry-run first, admitted through `resource add --copy`, then rehashed at both source and destination. Both destinations are under `/Volumes/Casa/refs/lib/unfiled`. No owner fetch is needed.

| Key / label | Destination | SHA-256 |
|---|---|---|
| `ledford2024mbe` / `slides` | `/Volumes/Casa/refs/lib/unfiled/DataElementMappingAndAnalysisDEMAASystematicMethodToImplementACompleteDigitalThread-2024-slides.pdf` | `930acdb69fbe6afb84730886abce7bb14c44985dbe641789d60949dc9f72c7d6` |
| `ledford2024patent` / `published` | `/Volumes/Casa/refs/lib/unfiled/PhysicalComponentsUsingDataElementMappingAndAnalysis-2024-published.pdf` | `d9ad6b2042ef734a249eadda41a65160b12d5d8ef4172eb1960768cb7ddf465b` |

## Projects and descriptions

### `insight-dema-llm`

ID: `c8acaa9f-3cd1-403b-8fdd-d9b922476051`. Cited count: **6**.

> Bibliography mirror of the published INSIGHT DEMA-LLM article. The paper keeps its own references.bib and frozen published references; refs mirrors only the six works it cites. Refs records are kept as correct as possible and may be more correct than the paper's printed entries. This is intentional; refs does not supply or rewrite the paper's bibliography.

Keys: `ledford2023dissertation`, `ledford2023ieee`, `ledford2024mbe`, `ledford2024patent`, `ledford2025syseng`, `oleary2025ai4se`.

### `ai4se-pipyer-proposal`

ID: `5b2e39c9-4b7a-4ba5-9cc1-eb097a9b35c5`. Cited count: **4**.

> Bibliography mirror of the rejected AI4SE/SE4AI 2026 Pipyer abstract, archived as submitted. The paper keeps proposal/references.bib and its frozen submitted references; refs mirrors only the four works it cites. Refs records are kept as correct as possible and may be more correct than the submitted entries. This is intentional; refs does not supply or rewrite the paper's bibliography.

Keys: `ledford2023ieee`, `ledford2025syseng`, `oleary2025ai4se`, `olearyledford2026insight`.

The evidence JSON contains the complete final `refs project show` output data for both projects. Counts and exact key sets match the delivered reference lists: INSIGHT excludes its unused internal-report entry; AI4SE excludes its unused dissertation entry and maps paper key `oleary2026insight` to catalog key `olearyledford2026insight`.

## Publication documentation handoff

Final file bytes are supplied beside this report:

- [INSIGHT docs/refs.md](2026-09-29-insight-ai4se-mirror-insight-refs.md), to copy to `/Volumes/Casa/pub/2026-insight-dema-llm/docs/refs.md`.
- [AI4SE docs/refs.md](2026-09-29-insight-ai4se-mirror-ai4se-refs.md), to copy to `/Volumes/Casa/pub/rejected/2026-ai4se-pipyer/docs/refs.md`.

The INSIGHT text includes the owner's exact replacement sentence about the internal report. Session 1's subagent stages and commits only `docs/refs.md` in each repository. Existing owner changes, including INSIGHT's untracked publication/revision directories, remain untouched. There is no `.refs.toml` or export target to install.

## Verification, timing and findings

Both publication repositories' tracked hashes and dirty status match preflight. Existing export-target rows equal the backup. The two original entries and both source/destination pairs match their hashes. All five reused records are unchanged apart from project membership. The full refs suite passed: **1,207 tests**. No conversion gate was run because these projects remain mirrors of frozen papers. Diff checks passed; no product code changed.

Work resumed after the 22:10 CDT owner decision and completed in the same turn. The branch remains `s2/insight-ai4se-mirror-proposal`; no merge was performed. Next action is session 1's review and documentation-only publication commits.

Findings for refs: none requiring a product change. Findings for the guide: a mirror project's membership follows the delivered cited list, not every entry in its bibliography file; the explicit project descriptions and local notes explain why catalog accuracy can exceed the frozen paper. No guide edit is proposed in this pass.
