# Data Model: Slice 1

**Implementation proposal, 2026-09-21.** SQLite is the sole authority. Ten logical tables; no operations, per-entry status, collection, waiver, projection-history or field-provenance tables. FTS shadow tables are implementation internals.

| Table | Stored values and invariants |
| --- | --- |
| catalog_meta | One stable catalog UUID, schema version and monotonically increasing catalog revision. No implicit init or upgrade. |
| sources | Stable UUID, binary-unique citation key, active/removed state, revision, UTC timestamps; validated metadata/context/native type/extensions/title protection and overrides. Key-generation provenance holds policy/table/Unicode versions. A compact corrected_fields JSON marker identifies explicit sets, clears and type-superseded paths; origins/access claims remain distinguishable on the row. |
| originals | Immutable exact entry bytes, SHA-256, length, format, origin, file digest/locator and needed comments/definitions; nullable source association for unresolved input. Deduplicate by digest plus origin/locator association so repeated import does not duplicate evidence. Retain exact .bib file bytes once for adoption inspection as well as addressable entries; no whole Zotero databases. |
| origin_identities | Unique namespace/library identity/item key binding to source ID, plus input fingerprint. Bindings cannot be stolen. Source-system identity is provenance, not write authority over another system. |
| resources | Stable ID, source ID, revision, label/media type, absolute or named-root relative locator, verified digest for copied files. Unique source/locator association. No mode flag or primary-selection machinery. Missing files remain locators, not deletion instructions. |
| projects | Stable ID, unique nonblank name, description and revision. |
| project_sources | Unique project/source pair and cited boolean. Every slice 1 row has cited=true. Cite inserts, uncite deletes; repeats are no-ops. Keep the column for future background membership. |
| export_targets | Unique canonical destination, project/profile fingerprint and last successful byte digest. No operation ID or per-source projection. Advance only after verified publication. |
| imports | One row per actual import run: ID, origin, exact file digest, start/finish timestamps and aggregate counts (applied/unchanged/conflict/invalid); incomplete finish stays visible after interruption. No per-entry state or saved replay outcome. |
| search projection | Derived FTS5 metadata/context/legacy-tag text keyed by source ID; matching fields returned with current source revision. Rebuildable, never an authority or file-content index. |

## Authority and mutations

Bibliographic facts live once in sources.metadata_json under the bounded CSL-shaped [record profile](contracts/records.md). The optional native label is not a second editable fact namespace. Original bytes never revive a cleared modeled value or a field incompatible with a changed type. corrected_fields marks every explicit update, including clear; imported omissions propose nothing. The marker is current state, not a history ledger.

Enable foreign keys on each connection. Mutations validate then use BEGIN IMMEDIATE with five-second busy timeout; conditional updates affect exactly one expected revision. Changed source aggregates increment once; no-ops do not. Allocate keys in that transaction. Do not hold write transactions during file copy/hash. Resource registration rechecks source activity/revision after publication and fails safely if stale.

Read-only commands do not create/migrate or perform writable hot-journal recovery. On recovery_required, the documented procedure opens only the selected existing database for SQLite recovery and integrity checks; there is no recover command. Mutating commands may let SQLite perform its normal rollback recovery before validation. A corrupt or unsupported database is not silently replaced.

## Import identity and re-runs

Inspect explicit source/origin identity and persistent identifiers together; contradictory signals or distinct editions conflict. A key alone is a candidate, not authority to overwrite. Exact previously applied original-entry association or a unique consistent identity establishes a repeat. A new accepted entry, its evidence association and identities commit together. Conflicts/invalid entries retain raw evidence without changing current source values; the run report supplies per-entry reasons and may be saved by the caller. Aggregate counts commit with each processed entry. After interruption rerun the file and classify entries again; do not replay saved results.

Plain update settles a metadata disagreement, marking corrected fields. Re-running never reverses the correction. A same-key identity collision can be addressed through ordinary add with a distinct explicit key or key set after inspection; no general merge/reconcile surface is implied. A removed-source match reports source_removed, never recreates it.

## Ownership, removal and recovery

Normalize absolute paths inside library_root to the library named root. Determine containment using resolved paths, not string prefixes; reject escaping relative components and unsafe symlink traversal for copying. Files under that recorded root are managed, others linked. Unfiled is only the new-copy destination and effective filing default; existing in-root links need no collection row. Root remapping changes resolution, never moves files.

Source removal retains the row, key, originals and relationships, but hides it from active searches/export; reactivation restores the same ID/key after preview. Unlink deletes only the association. Projects exclude removed sources while retaining their citation associations for explicit reactivation. Uncite affects only its selected project. Snapshot/restore includes every table and correction marker; external resource bytes are separately inventoried and excluded.
