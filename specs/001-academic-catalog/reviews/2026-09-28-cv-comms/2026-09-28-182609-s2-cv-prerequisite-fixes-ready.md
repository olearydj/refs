from: s2
next: s1
kind: report
re: 2026-09-28-182209-s1-cv-prerequisite-fixes.md

Ready for review and the owner's merge gate: `691b803` on `s2/cv-prerequisite-fixes`, based on `641d61a`. Worktree `/Volumes/Casa/dev/refs/worktrees/cv-prerequisite-fixes` is clean.

Both fixes implemented: bare BibTeX ampersands survive text decoding (escaped ampersands still work), and update dry-run replaces editable fields so a cleared native_type cannot survive in the preview. The CLI regression checks paper-conference → speech through preview, execution, stored state and identical CSL exports; preview leaves database bytes unchanged. New tests reproduce both defects against main.

Full suite: 1,207 passed, including corpus and rehearsal tests, with the requested TeX cache environment. Ruff and ty passed. All-project conversion check without --record: exit 0, 379 identical entries across five projects and twelve consumers. No fixtures recorded.

The CV before/after disposable catalogs show six restored ampersands across five entries: ARMR container; engineering-economy title and container; Pipyer, AI-enhanced DEMA and innovation-culture howpublished descriptions. The latter three are decoded original fields used by the proposal mapping, not newly modeled metadata. Yes, incoming text for existing modeled records changes on re-import. Re-importing these five entries into the old-code disposable catalog produced two conflicts and three unchanged records, zero applied/invalid; the old populated fields were not silently overwritten. Existing bad text needs explicit correction or conflict resolution.

Committed evidence: `specs/001-academic-catalog/reviews/2026-09-28-cv-prerequisite-fixes.md` and `.json`, with exact before/after strings and per-consumer counts. Full scratch gate: `/private/tmp/refs-cv-prerequisite-conversion/gate.json`; disposable comparison and scripts: `/private/tmp/refs-cv-fixes-evidence/`; successful suite: `/private/tmp/refs-cv-fixes-suite-final.log`. This ran the automated corpus/rehearsal tests, not a new external 545-file corpus campaign.

Live CV and catalog unchanged; CV proposal not revised. Ending this turn without polling.
