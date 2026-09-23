# Files, Export Publication and Recovery v1

**Slice 3 implementation proposal.** Moves use the protocol below; retained-original copies keep the existing copy protocol.

## Ownership and naming

A file is managed when the catalog records it by the library root and a relative path that resolves inside `library_root`. Every other file is linked: the catalog records where it is and leaves it alone. A source may carry a `loc`, a relative folder path under the library that says where its files belong. A source with no loc is not placed. Its files stay wherever they are, and reorg never touches them. Move intake writes `Unfiled` as the loc when the command gives none, because a moved file needs a destination. Link intake leaves loc empty. Linking, importing and changing where a named root points never move a file. Only explicit intake and reorg place files, and they place them under `lib/<loc>`.

Both intake commands, `add --file` and `resource add`, take exactly one of three flags. `--link` records the file where it is. `--copy` copies it into the library and keeps the original. `--move` copies it into the library, verifies the copy, and then deletes the original. `add --file` moves by default, because a newly downloaded file belongs in the library. `resource add` links by default, because attaching a file that already sits where it belongs is its ordinary use. Before a move starts, refs checks that the file is not already recorded as a resource of any source. If it is, the move is refused and the message names that resource. This check runs before the original is registered as a link, and it applies only to a new move, never to resuming one that has already started. Copying and moving require a reachable library.

New copy and move intake use the accepted filename convention: a short title, an optional edition or version, and the year, with no spaces and the original extension. A label supplied at intake adds a final segment after the year, keeping only letters, digits, dots and hyphens from the label, as in BoostYourGitDX-2023-r2023-06-03.pdf. An empty resulting segment is omitted. --keep-name preserves the original basename. If the short title or issued year is unusable, keep the original basename and report filename_unavailable. An intake collision does not authorize a suffix or overwrite. Reorg preserves names and resolves collisions as the move protocol describes.

Use pathlib for ordinary paths and narrowly scoped filesystem calls for exclusive publication. Reject paths that escape the library, unsafe symlink traversal, nonregular copy inputs and unsupported bundles. Those resources may be linked in place. If a cloud placeholder cannot supply readable bytes, the copy fails and the original remains.

## Copy protocol and interruption

The catalog and library folders on Casa share a volume; Downloads is on another volume. Create temporary copies under cat/staging, outside any synced folder. If staging and the library no longer share a volume, report staging_volume_mismatch. A catalog lock coordinates file effects, export and backup, with a five-second wait limit. SQLite writes use short BEGIN IMMEDIATE transactions.

Before copying, validate the source record, destination, filename and permissions. Then:

1. Copy the source to an exclusively created temporary file under cat/staging.
2. Compare independently computed source and temporary-file hashes. Check source identity, size and modification time around the copy and hash reads; if it changed or the hashes differ, fail without publishing.
3. Publish the verified temporary file at the destination without overwriting any existing file. A same-volume hard link from the temporary file is suitable; the original source is a separate file.
4. Recheck the source record's revision and active status, then register the destination and its digest. Retain the original source in every outcome.

Publication is atomic, but the whole sequence is not. A crash before publication can leave a temporary file. A crash after publication but before registration can leave a finished copy without a catalog link. Report its path when possible and never delete that published copy automatically. After inspection, resource add can register the existing destination. Retrying the copy encounters a collision instead of silently adopting the file. A repeated link to the same registered source and path is a no-op.

Adding a reference with a file first saves metadata and an original-path link. Once verified, register the managed destination on that resource, preserving its ID and exposing the old locator as `copied_from`. Open then uses the managed copy. On failure, retain the original locator and return a partial result; retry resource add --copy. A stale source revision leaves the published destination unregistered and reported. Clean up only this invocation's identified temporary file; never delete the original.

Copies retain originals and promise content verification, not native metadata preservation or power-loss durability. SQLite transaction durability remains configured. Transfers require a completed source with no concurrent external writer.

Resource check reports current availability, digest differences and recognized sync-conflict filenames without changing files or stored observations. Unlink and source removal never delete file bytes.

## Move protocol and journal

Every move, whether it comes from intake or from reorg, follows one sequence: copy the file into the library, verify the copy, re-record the resource, and only then delete the original. The catalog's file lock serializes refs writers, so two moves never run at once. Intake by move first registers the original as a linked resource, so the catalog knows the file from the first moment and every move is a move of a resource.

A move is recorded as an operation: one row in the `file_operations` table for one file. The row holds the resource, the old path, the intended destination, the staging path, the digest, the file's identity, the state, and timestamps. Identity means the file's device and inode number, its size, and its modification time. The row is written before any copying begins, and no filesystem work happens inside a SQLite write transaction.

The row moves through the states in the table. Each state records what has been completed, so a retry knows where to continue.

| State | What has been done, and what comes next |
| --- | --- |
| staged | The operation row exists with the old path, the destination and an exclusive staging path under `cat/staging`. Next, refs copies the original to the staging path with the source-identity and hash checks from the copy protocol, flushes the staged file to disk, and saves its identity and digest in the row. |
| published | The staged file has been hard-linked to its destination in the library without overwriting anything, and the destination digest has been verified. The staging name is kept until this state is committed. Because a hard link keeps the inode, a destination whose identity equals the saved staging identity is proven to be refs' own file. Equal bytes alone prove nothing and never authorize adopting a file that was already there. |
| recorded | In one transaction, refs has rechecked the source and resource revisions and the source's loc, re-recorded the resource as the library root plus the relative destination, and set this state. The resource keeps its ID. From here on the catalog points at the new file and the original is pending removal. |
| removed | The original has been deleted. The operation is complete. |
| failed | A check failed. The row holds the error and the last state that completed. No file has been deleted or overwritten. A retry repeats that state's checks. |

Deletion is guarded by file facts only. Before removing the original, refs checks three things: the destination still has the identity and digest saved in the row, the original still has the identity and digest saved in the row, and the resource row still points at the destination. Then refs flushes the destination file and its directory to disk and unlinks the original. If a flush fails, deletion does not happen. These flushes fix the order of events; they are not a promise about power loss on macOS. After the unlink, the row is set to `removed`. Revisions and loc are not rechecked here. They were checked when the resource was re-recorded, and once the catalog points at the new file, a later edit to the source must not be able to leave the original undeleted. If the owner changes the loc after this point, that is a new mismatch for the next reorg, never a reason to keep the original.

Both the original and the destination are hashed twice on purpose: once when the copy is made or published, and once more before the original is deleted.

A retry is the same command run again. It first looks for unfinished operations among the sources it would act on, even when their locators now agree with the loc or the loc has since been emptied, and finishes those before it looks for new mismatches. A mismatch is a managed file whose folder is not its source's loc, or a linked file whose source has a loc. A retry identifies an operation by its resource and the paths saved in the row, not by a request identifier. What it does depends on the state it finds.

- Interrupted while staged. The staging file may be partial. The retry removes it and copies again from the original, which is unchanged. If the requested destination differs from the one saved in the row, the retry stops and reports a conflict.
- Interrupted after publication but before the state was committed. The destination exists but the row still says staged. The retry compares the destination's identity with the saved staging identity. If they match, publication is proven, and the retry commits `published` and continues. If they differ, something else occupies that path, and the retry stops and reports it.
- Interrupted after recorded. The catalog points at the new file and the original still exists. The retry runs the three pre-delete checks, flushes, unlinks, and commits `removed`.
- Interrupted after the unlink but before `removed` was committed. The retry verifies the destination and the resource pointer, observes that the original is gone, and commits `removed`.

The rehearsal exercises the two cases that matter most: the process killed between publication and re-recording, and the process killed between re-recording and deletion. In the first, the retry proves publication and completes the registration. In the second, it completes the removal. Neither retry overwrites a file or creates a second resource.

Names. A moved file's basename is written in NFC. Reorg preserves names. When a preserved name would collide with a file already in the destination folder, the first file keeps its name and later files take `-b`, `-c` and so on before the extension, in the order they are processed. The operation row and the report record the old and new names (D6). Collisions during intake are handled differently: intake never adds a suffix and refuses instead.

Reports. A completed move lists every old path beside its new path, so that references outside refs, such as the owner's vault notes, can be repaired by hand. refs never edits those. The report also lists files under the moved tree that no source links and that were left untouched. `resource check` reports four kinds of file separately: linked with no loc, which is untouched; linked with a loc, which is waiting for reorg; managed but in a folder that is not its source's loc; and unfinished operations, where an interrupted intake's original is shown as an unfinished move rather than as an ordinary link.

Cutover. The owner takes a CCC backup, this section passes independent review, and the rehearsal passes, in that order. Then a one-time tool, `tools/assign_initial_loc.py`, sets a loc on every source that has a file. It takes the folder of the source's file in the Box tree. If the source has no Box-tree file, it takes the source's single collection. Otherwise it sets nothing. Where a source has a file in both the Box tree and Zotero storage, the storage file follows the Box folder. The tool writes through the application's revision-checked update path, does not mark a corrected field, previews before applying, reports every assignment, and moves nothing. The owner then runs `reorg`, which performs the move.

## Adoption and export publication

New destinations become adopted after successful explicit export. For an existing unadopted bibliography, require --adopt and an imports row proving that exact digest was read in a finished run with every block accounted for. Conflicts do not require batch reconciliation: recompute/report current entry conflicts from the preserved input and current sources. The light imports row need not store per-entry status. Replacing existing bytes also requires --overwrite. Adoption without replacement may establish a baseline only when candidate bytes are identical and all other checks pass. A malformed/unpartitionable incomplete run is not proof of import.

An adopted target binds destination, project and profile fingerprint. Explicit export replaces its unchanged baseline without another overwrite flag. Outside edits or changed binding fail by default; explicit --overwrite authorizes outside-byte replacement, while changing binding needs explicit --adopt again and the same existing-file checks. An overwrite flag alone cannot adopt an unrelated target. Preserve externally edited bytes as immutable original evidence before replacing them. An exact same-byte candidate is a no-op after authorization checks.

1. Read selected active sources in one consistent SQLite snapshot. Build/assess the entire output and report every entry/loss. Known blocking losses and unoverridden unknowns leave target, staging and baseline untouched.
2. Close the read snapshot. Stage exclusively beside the output, sync and verify. In a short transaction, validate the target and record the candidate digest in export_targets.pending_digest. Recheck authorized current target digest immediately before publication. No simultaneous external writer is allowed; hash/rename cannot protect against every editor race.
3. Publish no-overwrite for a new file or atomic replacement of the explicitly authorized existing file, never in-place truncation. Confirm bytes, then set the export_targets baseline to pending_digest and clear pending_digest in one transaction. The output corresponds to the recorded read snapshot; subsequent metadata edits await another export.

On the next export, first compare the file on disk with the recorded target. If it equals the baseline, proceed normally. If it equals pending_digest, promote that digest to the baseline, clear pending_digest and proceed: refs recognises its own interrupted publication. For a new destination with no baseline, this matching intent adopts the output without import or --adopt. Any other existing bytes are an outside edit and follow the normal conflict policy. A new target that is still absent has not been published and may be retried without overwrite; a missing previously adopted file remains a conflict. Hold the catalog file-effect lock across reconciliation and publication so two refs writers cannot replace each other's pending intent. A pending digest is bound to the recorded destination and project/profile; changed bindings do not inherit its authority.

Matching bytes alone do not authorize adoption. Recovery requires matching bytes plus intent already recorded by refs. Dry runs may report recoverable pending output but never promote or clear it. This adds one nullable column, not a journal or a new command.

## Snapshot and documented restore

Backup uses SQLite's backup API, never a copy of only the live main database. Under the coordination lock capture configuration, create a new private .partial directory, snapshot SQLite, recheck config and derive resource inventory from the saved database. The directory contains catalog.sqlite, config.toml, resources.jsonl and manifest.json with schema/catalog identity, hashes/sizes and external_contents_included=false. Validate integrity/foreign keys and publish to a new unused directory. Incomplete imports are valid saved state, not a reason to refuse backup. No resource bytes, managed or linked, are included.

The slice 1 manual restore procedure is:

1. Check manifest version, member hashes/sizes, safe paths, database schema, integrity and foreign keys. Reject symlinks, corruption, unsupported versions and nonempty destinations.
2. Copy the verified database into a second new catalog directory with private permissions. Create a separate config pointing there; retain or explicitly remap resource roots without moving files. Create its ready marker only after validation.
3. Open through refs paths/list/show/project show. Compare IDs, keys, revisions, original hashes, corrected fields, project selections and resource inventory against the snapshot. Missing external resources are reported, not removed.
4. Keep only one mutating catalog home active against shared library/export targets. Recheck actual bibliography digests before any restored-home export; restoration grants no overwrite authority.

SQLite hot-journal recovery is distinct from restoring a snapshot. Stop other refs processes, retain all database/journal files, open the existing selected database read-write through sqlite3 so SQLite performs its own rollback recovery, and run integrity_check/foreign_key_check before normal use. Do not delete a journal manually or initialize elsewhere. If recovery fails, restore a verified snapshot into a new home and report the original failure. Implementation documentation must give the exact tested commands; no recover CLI is required.

A demonstrated restore/open comparison is a slice 1 release gate. Full restore CLI, file-inclusive bundles and logical exit wait. Any later included-file backup uses independent copies or filesystem clones, never hard links to mutable source files.

The snapshot manifest names the original configuration location `configuration_path`, so relative configuration paths can be interpreted during manual restore. Manifest member metadata uses `members`, with each member’s `size` and `sha256`.
