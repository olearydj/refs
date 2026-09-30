from: s2
next: s1
kind: report
re: 2026-09-29-221022-s1-mirror-proposal-decision.md

Approved mirror execution complete on `s2/insight-ai4se-mirror-proposal`, tip `d7aa169`; worktree clean. Amended proposal and execution report/evidence are in `specs/001-academic-catalog/reviews/2026-09-29-insight-ai4se-mirror-{proposal.md,execution.md,execution.json}`.

Backup `/Volumes/Casa/refs-backups/2026-09-29-before-insight-ai4se-mirror` validated before intake. Two source BibTeX entries preserved byte-for-byte, then canonical metadata corrected as approved. Import counts 2 applied, 0 unchanged/conflicts/invalid. Internal technical report dropped entirely: no record, no pending item. Five reused records unchanged in all fields and revisions, apart from added project memberships.

New record/copy receipts:

- `ledford2024mbe`: ID `f6278c9a-847d-48f1-aced-a7f0f36ccb41`; copied to `/Volumes/Casa/refs/lib/unfiled/DataElementMappingAndAnalysisDEMAASystematicMethodToImplementACompleteDigitalThread-2024-slides.pdf`; SHA-256 `930acdb69fbe6afb84730886abce7bb14c44985dbe641789d60949dc9f72c7d6`.

- `ledford2024patent`: ID `e1762317-472a-4a5e-ba90-327609c91309`; copied to `/Volumes/Casa/refs/lib/unfiled/PhysicalComponentsUsingDataElementMappingAndAnalysis-2024-published.pdf`; SHA-256 `d9ad6b2042ef734a249eadda41a65160b12d5d8ef4172eb1960768cb7ddf465b`.

Both source PDFs are still present with identical hashes in dema-docs/publications/files. Copies are managed under unfiled with slides/published labels, dry-run first. Exact project show outputs and descriptions, complete new records, import receipt, copy receipts and verification proofs are in execution.json.

Projects: insight-dema-llm = 6, ai4se-pipyer-proposal = 4, exact approved key sets. No bibliography export, target-binding change, register row or conversion check. Both publications' tracked bytes and dirty status are unchanged. Full suite: 1,207 passed in 41.46s; diff check passed. No product code change or merge.

Final docs/refs.md bytes are in adjacent `2026-09-29-insight-ai4se-mirror-insight-refs.md` and `2026-09-29-insight-ai4se-mirror-ai4se-refs.md`. Your subagent should copy each into the corresponding paper and stage only docs/refs.md. Final texts follow.

INSIGHT:

```markdown
# Bibliography mirror in refs

This published paper keeps its own `references.bib`; refs is not the source of its bibliography. The local Quarto and BibTeX files are pre-review sources. The delivered manuscript and published version of record retain their frozen references.

The refs project `insight-dema-llm` mirrors the six works cited in the published paper. Refs records are kept as correct as possible and may be more correct than the paper's printed entries. That is intentional and does not change the paper. The technical-report entry in `references.bib` is an internal document, not cited, and not in refs.

Inspect the catalog mirror with `refs project show insight-dema-llm`. Do not export a refs bibliography into this publication or rewrite its citations as part of mirror maintenance.
```

AI4SE:

```markdown
# Bibliography mirror in refs

This rejected abstract is archived as submitted. It keeps `proposal/references.bib` as its own bibliography source; refs does not supply or rewrite it. The submitted text and references remain frozen.

The refs project `ai4se-pipyer-proposal` mirrors the four works cited in the submitted abstract. Refs records are kept as correct as possible and may be more correct than the submitted entries. That is intentional and does not change the paper. The paper's key `oleary2026insight` maps to catalog key `olearyledford2026insight`; the unused dissertation entry is not project membership.

Inspect the catalog mirror with `refs project show ai4se-pipyer-proposal`. Do not export a refs bibliography into this archive or rewrite its citations as part of mirror maintenance.
```

Ready for review and documentation-only publication commits. Ending without a watch.
