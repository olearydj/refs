from: s2
next: s1
kind: report
re: 2026-09-27-215050-s1-apostrophe-naming-kickoff.md

Ready at `b05beb1` on `s2/apostrophe-naming`, from main `072cdd5`, worktree `/Volumes/Casa/dev/refs/worktrees/apostrophe-naming`. One shared title-token function now joins U+0027/U+2019/U+02BC only between letters, used by generated keys and conventional filenames. Leading/trailing apostrophes and other punctuation separate; Unicode numeric characters do not count as letters. Creator handling and title case are untouched. Two contract sentences updated. Existing assigned keys and resource paths are unchanged.

Validation: **1,149 passed in 45.10s**, with the requested scratch TeX cache; 43 focused naming tests; Ruff, source ty and diff checks pass. All three apostrophes are covered for possessives, O’Reilly, surrounding quotes, adjacent whitespace, ASCII and Unicode numeric boundaries; hyphen/dot/slash/underscore/space remain separators. No existing export bytes can change: serializers consume stored citation keys and metadata, and neither calls generated-key or filename tokenization. No export projection changed, so the conditional all-project walk was not triggered and no fixtures were recorded.

Read-only audit: **760 sources, 762 resources; 4 changed generated-key candidates and 14 changed conventional-filename candidates** (13 managed, 1 linked), no skipped unusable key. Catalog byte hash is unchanged before/after. The complete old/new list, including every current full path, is in `specs/001-academic-catalog/reviews/2026-09-27-apostrophe-naming.md`; matching `-audit.json` includes IDs, key provenance, project citations, comparison policies and collision observations.

Key list (assigned key: old-generated → new-generated):
- `burt2014motor`: `burt-2014-motorcycleInnovator` → `burt-2014-motorcycleInnovators` (zotero-library).
- `larson-2024-engineeringExecutive`: `larson-2024-engineeringExecutive` → `larson-2024-engineeringExecutives` (no project).
- `sarkar2023shado`: `sarkar-2023-shadowsDon` → `sarkar-2023-shadowsDont` (zotero-library).
- `wilson-2024-developerS`: `wilson-2024-developerS` → `wilson-2024-developersPlaybook` (confirmed no project).

Filename list covers Bix (2), Burt (2), Larson (1), Rico (2), Sarkar (2), Sequeda publication (1), Sequeda preprint (1), Skarbez (1), CanvasAPI (1), Wilson (1). Only Larson/Sequeda publication/Wilson currently use the exact old convention; their new spelling is case-only and resolves to the same file on this filesystem. Other rows retain imported/manual filenames or predate current metadata (CanvasAPI now has a version), so the report separates current filenames from full old/new convention candidates. No candidate key exists, and no candidate path resolves to a different existing file. This is an impact list, not a rename plan; nothing was renamed or rekeyed.

No merge performed. Owner merge/rename decisions remain separate. Ending turn without polling.
