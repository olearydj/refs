# Files, Export Publication and Recovery v1

**Slice 3 implementation proposal.** Moves use the protocol below; retained-original copies keep the existing copy protocol.

## Ownership and naming

A recorded named-root path resolving within library_root is managed; other files are linked. Loc is optional: no loc means not placed, and reorg ignores those files. Move intake writes Unfiled explicitly when no --loc is given; --link leaves loc empty. Linking/import and root changes leave files untouched. Explicit intake and reorg use lib/<loc>.

Both intake commands offer mutually exclusive --link, --copy and --move. `add --file` defaults to move; `resource add` defaults to link. Copy retains the original; move verifies before deleting it. Move admission refuses a file already recorded as any source's resource, naming that resource; this does not prevent resuming an admitted move or reorg. Check move admission before initial link registration. Copy and move require a reachable library.

New copy and move intake use the accepted filename convention: a short title, an optional edition or version, and the year, with no spaces and the original extension. A label supplied at intake adds a final segment after the year, keeping only letters, digits, dots and hyphens from the label, as in BoostYourGitDX-2023-r2023-06-03.pdf. An empty resulting segment is omitted. --keep-name preserves the original basename. If the short title or issued year is unusable, keep the original basename and report filename_unavailable. An intake collision does not authorize a suffix or overwrite. Reorg preserves names subject to D6 collisions below.

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

Moves use copy, verify, re-record, delete. The catalog file-effect lock serializes refs writers. Intake registers the original link first, retaining it until recorded. Save `file_operations` intent before copying; keep filesystem work outside SQLite write transactions.

| State | Meaning and next action |
| --- | --- |
| staged | Save intent and exclusive staging path. Copy under cat/staging with the checks above; fsync. Persist filesystem identity, size, mtime and digest before publication. |
| published | Publish without overwrite; verify the destination digest. Retain the staging name until this state commits. Matching staging/destination identity proves publication after interruption; equal bytes alone cannot authorize adoption. |
| recorded | In one transaction, recheck source/resource revisions and loc, re-record the resource as library root plus relative destination, and set this state to mark pending removal. Keep the resource ID. |
| removed | Original deletion succeeded; complete. |
| failed | Save the error and last completed state. Preserve existing files; retry that state's checks. |

Before deletion, check exactly: destination identity and digest match the recorded values; original identity and digest match; the resource row points at the destination. Fsync the destination file and directory before unlink; sync failure stops deletion. This is not a macOS power-loss guarantee. Commit removed after unlink. If interrupted after unlink, verify destination and resource pointer, observe the missing original, and complete. Original and destination are each hashed twice by design: at staging/publication and before deletion.

Re-running resumes unfinished operations for selected sources before selecting new mismatches, even with loc now empty. Identify operations by resource and saved paths. Before recorded, a changed destination conflicts; staged work can be rebuilt from an unchanged original, and published work verified and recorded. Recorded work uses only the pre-delete checks above. A later loc change is a new mismatch for the next reorg, never a deletion block.

Rehearse kills between publish and re-record, and between re-record and delete. Retry proves publication and completes registration in the first case; it completes pending removal in the second, without duplicate resources or overwrite.

Write NFC basenames. Under D6, when preserved names collide, the first file keeps its name; later files take -b, -c before the extension. Record old/new names in the operation and report. Eight Zotero snapshots would otherwise occupy three names in lib/papers/aiml. Intake convention collisions still refuse.

Completed reports pair every old/new path and list untouched unlinked extras, enabling the owner's seven vault repairs. Resource check separately reports linked with no loc (untouched), linked with loc (pending reorg), managed in the wrong folder, and unfinished operations. An unfinished intake's original is an unfinished move, not an ordinary link.

Cutover follows CCC backup, review and rehearsal. `tools/assign_initial_loc.py` previews and reports through the application's update path without marking corrected fields: the folder of a Box-tree file; otherwise the single collection; otherwise none. For 35 sources with files in both trees, storage files follow the Box folder. File-less sources keep empty loc. Assign locs to every source with a file, then run reorg. The tool moves nothing.

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
