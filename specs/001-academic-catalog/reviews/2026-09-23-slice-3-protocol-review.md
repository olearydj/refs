# Slice 3 move protocol: independent review, 2026-09-23

Scope: the "Move protocol and journal" section of [files-and-recovery.md](../contracts/files-and-recovery.md#move-protocol-and-journal) and its reflections in the data model, CLI contract and spec, as committed in a1803c9. Method: reading against the constitution and the brief, plus read-only queries on the owner's catalog for the shapes the protocol must handle. Findings use the design-lens format: principle, the concrete issue, the simpler alternative, evidence.

## Answers to the authoring session's two questions

Q1, proving publication after a crash. Sound. Publication already uses a hard link into place, so the staged file's device and inode survive at the destination; recording that identity plus the digest before publishing, and comparing both on retry, distinguishes our file from an occupied destination. Record size and mtime as well; inode reuse is the only theoretical gap and the digest closes it.

Q2, finishing deletion after re-recording. Sound in shape, wrong in one check; see finding 1.

## Findings

1. Major. Deletion must depend on file facts, not catalog revisions. Principle: an interrupted operation needs an exit that is always reachable. Issue: before deleting the original, the draft rechecks source and resource revisions and loc. Once the row is in state recorded, the catalog already points at the destination; any unrelated edit to the source afterwards, a metadata correction, a loc change for the next reorg, bumps a revision and makes the pre-delete check fail forever. The row is stuck in recorded, the original lingers, and nothing can complete it. Alternative: revision and loc checks belong in the recorded transaction only. Before deletion, check exactly three things: the destination still has the recorded identity and digest, the original still has the recorded identity and digest, and the resource row still points at the destination. A later loc change is simply a new mismatch for the next reorg. Evidence: the draft's own resume rule already says recorded work "re-verifies before deletion"; this narrows what it verifies.

2. Major, owner judgment. Default reorg must not move deliberately linked files. Principle: constitution II, files elsewhere remain linked except through explicitly invoked intake, and the never-cut list. Issue: the CLI row selects "folder/loc mismatches, including linked files entering lib", so an unscoped reorg adopts every linked file. That makes `--link` a choice that lasts until the next reorg, and it is the same command the owner will run routinely after editing locs. Alternative: default reorg handles managed files only, those already under lib whose folder disagrees with loc, plus unfinished operations. Bringing linked files in is an explicit selector, `reorg --from PREFIX`, which is what the cutover is: `--from "~/Box Sync/zotero"` and `--from ~/Zotero/storage`. Evidence: the owner today intends every file to move, so nothing is lost by the narrower default, and the seam costs one option.

3. Major, owner judgment. Preserved names collide. Principle: rules, not patches; no overwrite and no suffix. Issue: under the loc mapping, eight Zotero HTML snapshots from eight different sources would land in `lib/papers/aiml` as three names: `2402.html` three times, `2311.html` three times, `2310.html` twice. Preserve-names plus refuse-on-collision strands them as linked with a report line, and there is no rename to fix them with. Alternative: a move preserves the name unless the preserved name would collide in the destination folder; then the file takes the convention name, short title, year and label, which carries the source's identity; if that still collides, refuse and report. One rule for every collision; the report states which files were renamed and why. Evidence: the query above; no source has two files of one name, so within-source collisions do not arise.

4. Minor. The initial assignment tool: "file folder" must mean the folder of a Box-tree file; 35 sources have a file in both trees, and the storage file follows the Box folder. Setting loc through the update path must not mark loc as a corrected field; it is refs-owned placement, not bibliographic correction.

5. Minor. Before the cutover, resource check will list 551 folder/loc disagreements. Distinguish "linked, outside the library" from "managed, wrong folder" so the report stays readable, and label an unfinished intake's original as an unfinished move, not as a linked file.

6. Minor. The original is hashed at staging and again before deletion, the destination at publication and again before deletion. On the 4.3 GB library that is minutes on a local disk and is the right trade; say so in the contract so nobody optimizes it away.

7. Observation. Intake by move first registers the original as a linked resource, then moves it. This makes intake and reorg one path, which is right, and it means an interrupted intake leaves a resource pointing at Downloads until re-run. Acceptable; finding 5 covers how it is reported.

Word budget: the four documents grew by 867 words against about 900 allowed, offset by 1,303 removed from the plan. Within budget.

## Disposition

Findings 1, 4, 5 and 6 go back to the authoring session as revisions. Findings 2 and 3 wait for the owner's reply, recorded in the brief, then follow. Tasks wait for all of them.
