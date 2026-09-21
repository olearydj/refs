# File Operations and Recovery Contract v1

## Scope and ownership

Slice 1 links files and performs verified non-destructive copy into library/Unfiled. Slice 2 adds move and explicit selected reorganize. Mode is derived from a named-root locator resolving inside library_root; there is no mode flag, adopt command or managed-but-elsewhere state. In-library files have an effective filing collection, initially Unfiled. Assigning filing from folders changes catalog data only. Outside linked resources are never reorganized or deleted by refs.

Use pathlib for paths, stat, supported hard-link publication and ordinary operations. Use descriptor-level os/fcntl only where required for locking, exclusive creation, sync or identity-safe platform primitives. Preserve existing basenames; no automatic renaming on collision. The selected catalog and library are separate folders on Casa, on the same volume; Downloads is cross-volume. Build and test the cross-volume copy path first. Stage intake in cat/staging, outside the synced library, and publish only completed files. Refuse unsafe changed topology with staging_volume_mismatch; do not silently stage partial files inside a share.

Regular readable stable files are supported. Reject destructive transfer of symlinks/special files and untested multifile bundles. Linked bundles can remain inventoried. A cloud placeholder must be materialized before copy; read failure leaves the original. Report potential external-link breakage on relocation. Existing external note files are never rewritten.

## Guarantees and metadata

The guarantee covers process death, ordinary I/O failure and cooperating refs processes on tested local filesystems. Power-loss protection is best effort: SQLite synchronous FULL and fullfsync on macOS, file F_FULLFSYNC where supported, ordinary fsync elsewhere, directory sync where supported with limitations reported. Do not describe os.fsync alone as a macOS power-loss guarantee. Hardware destruction and noncooperating writers during final publication are outside the guarantee.

Independently hash source and staged copy; verify supported metadata before any destructive cleanup. On macOS use a bounded native copyfile-equivalent adapter to preserve ACLs, extended attributes and resource forks, with fixture evidence. Do not infer metadata preservation from byte equality or shutil.copy2. Cross-volume creation-date preservation is not promised; report that limitation. If required attributes cannot be preserved/verified, refuse move and retain source; copy may complete with explicit metadata-loss warnings because it retains the original.

## Coordination and states

One durable lock file in cat coordinates file effects, export, backup and recovery with a five-second flock wait. Lock contention returns retryable busy. Never replace an in-use lock. Persist resource/target reservations and expected revisions. Metadata deletion/unlink must reject active reservations. Previews create no catalog rows, locks, staging files or request reservations. Do not hold SQLite write transactions while copying/hashing.

| State | Effect and evidence | Recovery |
| --- | --- | --- |
| prepared | Store source device/inode/size/times/digest, action, captured destination, resource revision and staging path with operation ID plus attempt nonce. | Changed source or settings that retarget the effect require explicit replan; no duplicate source creation. |
| staged | Exclusively create private staging; copy, sync, verify bytes/attributes, then recheck source stability. | Incomplete stages cannot publish; retain source and report cleanup/resume. |
| published | Create destination with no-overwrite hard link from same-volume completed staging. Record staging inode before publication; verify destination identity/digest. | Matching digest alone is insufficient. Only matching recorded staging inode proves this operation published the file. Any unrelated existing destination, even equal bytes, conflicts. |
| catalog_committed | Compare reservation/revision and commit new root-relative locator, mandatory managed digest and operation state. | Catalog now references verified destination; source remains. |
| cleanup_pending (slice 2 move only) | Exclusively rename source to a quarantine name in its original directory, then verify captured identity and digest against destination before unlinking that quarantined object. | If a replacement was captured, never delete it. Restore its name only with no-overwrite semantics; if another file exists, keep both and report recovery paths. |
| complete | Copy retains original; move confirms authorized source cleanup; release reservation and retain outcome. | Matching retries return the saved result. |

The copy publication step is atomic, not the whole protocol. The rare same-volume source-link optimization in slice 2 requires completed stable downloads: link, catalog commit, identity-safe cleanup. It shares mutable content until unlink and is not an independent copy or backup. Reorganize is restricted to selected managed files and uses the same interruption/cleanup safeguards.

Add-with-file commits metadata and an original resource link before intake. A subsequent failure returns partial with source ID, resource ID and operation ID, never loses the source reference. Request identity excludes configuration, while captured effect intent remains fixed. After configuration repair, retry can resume prepared safe work or demand explicit replan if effects already exist. No silent retargeting or creation of a second source.

`resource check --verify` reports missing files, digest differences, unavailable roots and recognized sync-conflict filename patterns without altering them. It never treats sync as backup. Recommend share versioning separately; no sync service is configured by refs.

## Export adoption and publication

New destinations become adopted when first successfully exported. An existing unadopted bibliography requires explicit adoption and reconciliation of its exact current digest; every entry must be accounted for and conflicts resolved. Comments and originals remain preserved. An overwrite flag does not adopt an unrelated file. Targets bind project/profile; changed bindings require explicit re-adoption rather than inheriting authority silently.

An adopted target may be replaced on explicit export when its current digest matches the last successful baseline. External edits conflict until reconciliation or explicit overwrite. When overwrite replaces external edits, preserve those bytes as an original. Identical candidate bytes are a no-op. Never write in place.

1. Read selection and sources in one consistent SQLite snapshot; close the read transaction before writing operation intent.
2. Construct and assess all output and all losses in memory. On a blocked report, create no output or stage file and leave the baseline unchanged.
3. Store intent and necessary prior/candidate digests; exclusively stage beside the destination so publication is same-volume. Intake's cat staging rule does not apply to bibliography output on other volumes.
4. Sync/verify the stage and recheck the authorized current digest immediately before publication. Publish no-overwrite for new output or atomic replacement for authorized existing output.
5. Commit baseline and per-source projection evidence only after verified publication. Recovery compares actual bytes and saved intent; unknown content never becomes a baseline automatically.

No portable compare/hash/rename sequence protects against every noncooperating concurrent editor. State the no-simultaneous-external-write precondition. Recovery preserves necessary previous bytes until the effect is resolved. Export does not silently omit selected entries; unknown override and waivers appear in the complete report.

## Slice 1 snapshot and restore

Backup is allowed with unresolved file operations; include their intent and IDs. Under the coordination lock, capture config bytes/hash, use SQLite's backup API, recheck config, then derive resource inventory from that saved database. Write to a new .partial directory, validate hashes/integrity/foreign keys, and rename to the final unused destination. Never copy only a live SQLite main file. The snapshot identifies excluded external bytes, including managed files.

Slice 1 supplies a documented restore procedure: validate snapshot hashes and schema; copy database into a second new catalog directory with private permissions; create its lock/ready marker only after integrity checks; supply a separate config pointing there; open with refs show/list and compare IDs, keys, provenance, selections and inventory. Do not resume recorded file operations automatically in the restored home. Only one active mutating home may control shared external targets. This demonstrated restore is a release gate, not a deferred promise.

Slice 4 adds the full restore command, versioned bundle machinery, optional managed-file inclusion and logical library export. Included files must be independent copies or filesystem clones, never hard links; verify digests. Restore checks reject nonempty destinations, unsupported versions, escaping paths, symlinks and missing/corrupt members. Recheck export baselines against actual current files before any later export. Catalog removal never deletes file bytes.
