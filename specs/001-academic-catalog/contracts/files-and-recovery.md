# File Operations and Recovery Contract v1

## Filesystem API convention

Use `pathlib.Path` for path values and ordinary operations. Publish a new regular file with `destination.hardlink_to(staged)` from sibling staging; an existing destination is a conflict. For authorized replacement, use `staged.replace(destination)`. Keep descriptor-level os calls for fsync and required open flags, and fcntl for advisory locking. Direct `os.link` is reserved for a demonstrated need for controls absent from pathlib. These calls remain subject to the journal, verification, and flush ordering below. See the [dependency audit](../dependency-audit.md#pathlib-and-durable-publication).

## Ownership and Supported Storage

Link-in-place is always explicit and never copies, relocates, or renames the target. New-file acquisition defaults to managed move; explicit copy/link overrides remain available. Existing imported links remain linked until adoption. Each managed resource has one filing collection, including reserved `Unfiled`. Filing changes update intent; `reorganize --execute` moves only explicitly selected resources.

Managed mutation initially supports regular files on tested local filesystems with no-overwrite publication, advisory locks, and durable flush. Reject symlinks/special files for destructive transfer, while ordinary linking may record them with diagnostics. Preserve filenames and verified contents. Inspect ACLs, extended attributes, and macOS resource forks; copy and verify supported metadata, or refuse destructive move when required fidelity cannot be demonstrated. Do not claim that byte equality proves annotation or all metadata portability. Multi-file units are inventoried; until a tested bundle protocol exists, preserve them in place with `unsupported_bundle_transfer` rather than move only the HTML member.

The guarantee covers process interruption and ordinary refs-induced failures of readable stable inputs. It excludes hardware/media loss, deletion by unrelated processes, and simultaneous noncooperating writes during publication. Local cloud-sync attachment directories are usable when files are materialized and stable. The live catalog is not placed in a network or actively synchronized folder. Refusing an unsafe transfer leaves a valid metadata record and linked original resource with a partial acquisition result; it does not strand the only reference to the file.

## Coordination

Setup creates one durable lock file in the catalog home. Use a per-home advisory `flock` for transfer, export, recovery, backup, and restore operations. Wait at most five seconds, then return retryable `busy` with exit 6. Never remove/recreate an in-use lock file or use an expiring lease. Serialize cooperating operations for one home; separate homes targeting the same file and arbitrary external editors are outside that lock.

Persist resource/target reservations and captured revisions before external effects. Catalog removal/unlink/reorganization checks active reservations and rejects interfering changes. Do not hold a database write transaction while hashing or copying bytes. A preview opens existing data read-only and creates no lock, reservation, or staging file. All path/fingerprint/revision checks repeat at execution.

## Transfer Protocol

| State | Durable record and action | Recovery behavior |
| --- | --- | --- |
| `prepared` | Record action, paths, resource revision, original stat identity/size/times/digest, desired destination and staging name. Verify destination does not exist. | Inspect saved source and staging paths; changed source becomes conflict. |
| `staged` | Exclusively create a sibling staging file; copy, flush/fsync, independently verify bytes and supported attributes, then recheck source stability. | An incomplete/unknown staging file is never published; retain source and report resumable cleanup. |
| `published` | Atomically create destination without replacing an existing name, using tested no-overwrite publication. Flush destination directory. Recheck destination digest. | If destination matches the intent, continue; if unknown, stop without deleting either file. |
| `catalog_committed` | In a short transaction compare reserved resource revision, set the verified new locator/digest, and record state. | Catalog points to verified destination; source may still exist. |
| `cleanup_pending` | For move, fresh source identity/content and destination verification must match before deleting source; flush source directory afterward. | Changed source is retained and reported as conflict/cleanup pending; never delete it merely because destination exists. |
| `complete` | Source removal verified for move, or original retained for copy; persist outcome and release reservation. | Matching retry returns original result, no second copy or move. |

Before each effect, the journal includes enough intent to recognize success even if the process dies before updating the state. `recover --execute` checks actual files as well as recorded states. If a destination was published but catalog commit failed, the original remains intact and recovery can safely complete the link update. Failed cleanup is partial completion with both paths disclosed, not a successful move. No-overwrite publication failure never falls back to a replacing rename. Different existing content is always a collision; identical existing content is also a conflict in v1 unless the journal proves it was published by this same operation.

`add --file` first preserves source metadata and a link to the original, then executes intake. A metadata success/file failure returns partial status, source identity, original locator, and operation ID. Retrying the same request resumes file work rather than recreating metadata. Import itself never uses this acquisition path.

## Bibliography Adoption and Export

A canonical target is bound to one project/format and raw-byte baseline. An export to a nonexistent path creates and adopts it without an extra flag. For an existing unadopted file, require `--adopt --reconciliation BATCH`: the batch must refer to the exact current file digest, and every source entry must be applied or unchanged after reconciliation, with no conflict/invalid/pending entries; structural comments and preambles remain retained artifacts. `leave_unresolved` does not permit initial adoption. An unrelated existing destination cannot inherit adoption from another path. Rebinding an adopted target to a different project or format is rejected in v1; choose a new output path. `--overwrite` never implies rebinding.

For adopted targets, compare current bytes to the saved last-success digest. If equal, explicit export can replace them with no additional overwrite option. If different, return `external_edit` with a comparison; `--overwrite` explicitly permits replacement of that adopted target's current bytes, or an explicit adoption/reconciliation operation establishes the reviewed state. An overwrite flag alone does not adopt an unrelated file. Identical candidate/current bytes require no write; adoption state still needs explicit resolution when no prior adoption exists.

1. Read selected sources and project membership from one consistent catalog snapshot; record selection revisions and effective configuration fingerprint.
2. Build deterministic complete output and validate supported citation representation. Persist `prepared` intent with old/observed/candidate digests, staging path, and previous target bytes before creating external staging files.
3. Exclusively stage beside the target, flush and verify data, then record `staged`. Immediately recheck current target against the authorized observed state. A changed digest conflicts even if an earlier preview passed.
4. Publish a new target without overwrite or atomically replace the authorized existing file; flush the directory. No in-place truncating writes.
5. Record `published`, then commit the new target baseline and operation outcome. Recovery may recognize candidate bytes and complete bookkeeping. Unknown bytes never become a baseline automatically.

An external editor can race between the final comparison and replacement; portable hashing/rename cannot prevent every noncooperating race. The supported workflow requires no simultaneous outside writes during publication. Prior bytes are retained while unresolved, and the limitation is shown in advanced help/recovery documentation rather than presenting an absolute filesystem transaction guarantee. Catalog changes made after the read snapshot appear only on the next explicit export.

## Backup and Restore

Backups are directory bundles described in [interchange](interchange.md). Acquire the coordination lock and reject unresolved file operations with their IDs. Read preference bytes and a digest; obtain a consistent SQLite backup through its supported backup API, then recheck preferences. If the config changed externally, retry or fail instead of combining mismatched state. Derive the resource inventory from the saved snapshot.

Claim a new output directory exclusively. Write staged members and validate hashes, database integrity, and foreign keys. Publish a final `manifest.json` declaring `state=complete` only after all members are durable. A directory without that completion state is not a valid backup. Never represent a copy of only an open live database file as a backup. External file contents remain excluded, including managed attachments; inventory states that responsibility.

Restore claims a new empty home, rejects unknown versions, escaping paths, symlinks, missing members, bad hashes, or invalid foreign keys, then writes and verifies data before creating the home ready marker. Ordinary commands refuse an incomplete restore. Restore preserves identifiers and config, marks adopted outputs for current-file revalidation, and never moves attachments. If a resource root is unavailable, diagnostics report it without invalidating recovered metadata.

Schema migration is explicit and uses a verified pre-migration backup plus transactional database changes. Recovery cannot promise arbitrary rollback of changed external files. Full logical export is independent of restore and excludes runtime locks and disposable indexes while retaining records, relationships, originals, and provenance.
