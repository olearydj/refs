# Files, Export Publication and Recovery v1

**Implementation proposal, 2026-09-21.** Slice 1 has no destructive intake, operation journal, request replay or recover command. Its safety comes from retaining the source, exclusive publication, transactions and an explicit restore procedure.

## Ownership and naming

A recorded named-root path resolving within library_root is managed; other files are linked. No stored mode or resource adopt command. Unfiled is a folder/effective filing default, not a collection row. Linking/import leaves existing files and names untouched. Resolving or changing roots never moves files. Outside files may only be transferred through explicit intake; moving/reorganizing is deferred.

`resource add --copy` and `add --file ... --copy` copy into library/Unfiled. Default basename uses the accepted short-title/optional edition-or-version/year convention, preserving extension: PracticalVim-2E-2015.pdf, ZeroToSold-v1.2.4-2020.pdf. This is the owner's standing “Rename by default” request for new intake only. --keep-name retains the original basename. Missing usable short title or issued year preserves the basename with filename_unavailable; ND key generation is not permission to fabricate a filename year. Collision never triggers an automatic suffix or overwrite. Later reorganize preserves existing names.

Paths use pathlib; descriptor/platform calls handle exclusive publication, sync and native metadata only where required. Resolve containment properly; reject escapes, unsafe symlink traversal, nonregular copy inputs and untested bundles. Such resources can be linked without copying. Missing cloud-placeholder bytes fail safely.

## Copy protocol and interruption

Casa cat/lib are on the same volume; Downloads is cross-volume. Stage privately under cat/staging, outside any synced folder. Refuse changed topology with staging_volume_mismatch. Use one catalog coordination lock with a bounded five-second wait for file effects/export/backup; this is a lock file, not a journal. Database writes remain short BEGIN IMMEDIATE transactions.

1. Validate source identity/revision, destination, naming and permissions. Capture source stat identity, size/times and independent digest.
2. Exclusively create a private stage. Copy with the macOS native metadata adapter, sync and independently hash it. Verify supported ACLs/xattrs/resource forks; recheck source stability. A changed source fails without publication.
3. Publish the complete stage to the unused destination with a same-volume no-overwrite primitive (e.g. hard-link stage to destination). This links the independent copy, never the original source. Verify destination identity/digest.
4. Recheck source record revision/activity and commit its root-relative resource locator/digest. Retain original source bytes in every outcome. Clean only the stage created and still identified by this invocation.

The publish step is atomic; the entire operation is not. A crash before publication leaves only a private stage; after publication and before registration it can leave a complete unregistered file. There is no journal proof authorizing automatic adoption/deletion of that file. Report paths when possible; after interruption inspect source and destination, use resource add to link a verified existing destination, or retry to receive a collision. An existing registered source/locator with matching digest is a no-op; an unrelated destination, even with equal bytes, is a conflict. Do not silently register a collision as this invocation's copy.

Add-with-file first commits metadata and the original path link. Copy failure returns partial with those IDs and paths; retry resource add for that source rather than creating it again. A stale registration after successful publication likewise reports the complete unregistered destination. No record claims successful intake before destination verification. Cleanup never deletes an original or unknown published file.

The guaranteed failure model is process interruption and ordinary I/O failure on supported local filesystems. Power-loss protection is best effort: SQLite synchronous FULL/fullfsync on macOS, F_FULLFSYNC for files where supported, fsync elsewhere, directory sync with platform limits reported. Do not claim fsync alone guarantees macOS power-loss durability. Cross-volume creation-date preservation is not promised. Native metadata preservation needs fixtures; copy may warn about unsupported/lost attributes because the original is retained. Source mutation after the final stability check and noncooperating external writers remain disclosed limits.

Resource check reports current availability, verified digest differences and recognized sync-conflict filenames without changing files or stored observations. Unlink/removal never delete file bytes. Open invokes an external application only for the explicitly selected or sole resource.

## Adoption and export publication

New destinations become adopted after successful explicit export. For an existing unadopted bibliography, require --adopt and an imports row proving that exact digest was read in a finished run with every block accounted for. Conflicts do not require batch reconciliation: recompute/report current entry conflicts from the preserved input and current sources. The light imports row need not store per-entry status. Replacing existing bytes also requires --overwrite. Adoption without replacement may establish a baseline only when candidate bytes are identical and all other checks pass. A malformed/unpartitionable incomplete run is not proof of import.

An adopted target binds destination, project and profile fingerprint. Explicit export replaces its unchanged baseline without another overwrite flag. Outside edits or changed binding fail by default; explicit --overwrite authorizes outside-byte replacement, while changing binding needs explicit --adopt again and the same existing-file checks. An overwrite flag alone cannot adopt an unrelated target. Preserve externally edited bytes as immutable original evidence before replacing them. An exact same-byte candidate is a no-op after authorization checks.

1. Read selected active sources in one consistent SQLite snapshot. Build/assess the entire output and report every entry/loss. Known blocking losses and unoverridden unknowns leave target, staging and baseline untouched.
2. Close the read snapshot. Stage exclusively beside the output, sync and verify. Recheck authorized current target digest immediately before publication. No simultaneous external writer is allowed; hash/rename cannot protect against every editor race.
3. Publish no-overwrite for a new file or atomic replacement of the explicitly authorized existing file, never in-place truncation. Confirm bytes, then commit export_targets baseline. The output corresponds to the recorded read snapshot; subsequent metadata edits await another export.

If killed after publication but before baseline commit, a new file is unadopted or an old baseline no longer matches. Preserve output and report the conflict on retry; use the normal import/adopt/overwrite path to establish authority again. Never infer a successful prior operation from matching bytes alone. This conservative retry is intentional until journals are justified by destructive moves. No export_projections or export_waivers are stored.

## Snapshot and documented restore

Backup uses SQLite's backup API, never a copy of only the live main database. Under the coordination lock capture configuration, create a new private .partial directory, snapshot SQLite, recheck config and derive resource inventory from the saved database. The directory contains catalog.sqlite, config.toml, resources.jsonl and manifest.json with schema/catalog identity, hashes/sizes and external_contents_included=false. Validate integrity/foreign keys and publish to a new unused directory. Incomplete imports are valid saved state, not a reason to refuse backup. No resource bytes, managed or linked, are included.

The slice 1 manual restore procedure is:

1. Check manifest version, member hashes/sizes, safe paths, database schema, integrity and foreign keys. Reject symlinks, corruption, unsupported versions and nonempty destinations.
2. Copy the verified database into a second new catalog directory with private permissions. Create a separate config pointing there; retain or explicitly remap resource roots without moving files. Create its ready marker only after validation.
3. Open through refs paths/list/show/project show. Compare IDs, keys, revisions, original hashes, corrected fields, project selections and resource inventory against the snapshot. Missing external resources are reported, not removed.
4. Keep only one mutating catalog home active against shared library/export targets. Recheck actual bibliography digests before any restored-home export; restoration grants no overwrite authority.

SQLite hot-journal recovery is distinct from restoring a snapshot. Stop other refs processes, retain all database/journal files, open the existing selected database read-write through sqlite3 so SQLite performs its own rollback recovery, and run integrity_check/foreign_key_check before normal use. Do not delete a journal manually or initialize elsewhere. If recovery fails, restore a verified snapshot into a new home and report the original failure. Implementation documentation must give the exact tested commands; no recover CLI is required.

A demonstrated restore/open comparison is a slice 1 release gate. Full restore CLI, file-inclusive bundles and logical exit wait. Any later included-file backup uses independent copies or filesystem clones, never hard links to mutable source files.
