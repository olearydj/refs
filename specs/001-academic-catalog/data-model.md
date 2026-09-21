# Data Model: Academic Catalog Workflow

**Status:** revised preimplementation design, 2026-09-21. No catalog or migration has been created. [Records](contracts/records.md) owns value validation; [files and recovery](contracts/files-and-recovery.md) owns external effects. Slice 1 owns the entities below except those explicitly marked later.

## Authority and constraints

SQLite is the sole catalog authority. Bibliographic facts live once in sources.metadata_json using the bounded CSL-shaped profile. Creators and standard identifiers are not separately editable tables. Lookup/search projections are derived and rebuildable. Immutable imported originals are evidence, not fallback authority for cleared or type-incompatible modeled fields.

| Entity | Fields and constraints | Relationships and lifecycle |
| --- | --- | --- |
| catalog_meta | `catalog_id is a stable UUID; schema_version and catalog_revision are positive integers.` | One row; no implicit creation/migration on open. |
| sources | `id is a stable UUID; citation_key is unique using binary comparison; state is active or removed; revision starts at 1.` Metadata is validated canonical JSON; native_type is optional; context and title protection are validated JSON; timestamps are UTC. | Keys remain reserved on removal. Explicit reactivate restores the same ID/key and retained links/associations after preview; no implicit resurrection on import. Active queries exclude removed sources. |
| field_provenance | `source_id and field_path are required; origin is user, agent, import or derived.` Value fingerprint, original-entry reference, policy versions and explicit-clearing/type-supersession state. | No claim of complete event sourcing; current fact origin and retained originals suffice. |
| originals | `sha256 is unique; bytes and byte_length must match the digest.` Format, origin, entry locator and adapter version. | Preserve per-entry originals and necessary bibliography context. Whole Zotero databases stay in an external archive with path/hash/versions recorded, never catalog BLOBs. |
| import_batches and import_entries | `entry status is pending, applied, unchanged, conflict or invalid; batch_id plus locator is unique.` Original reference, candidates, normalized proposal, conflicts, applied source ID/fingerprint. | Every block has an outcome. One entry and its source changes commit together. Replays return prior outcomes; partial batches remain inspectable. Batch administration and Zotero migration expand in slice 3. |
| origin_identities | `namespace plus library_identity plus item_key is unique.` Source ID and most recent input fingerprint. | A new identity cannot steal an existing binding. Zotero URI/item key are provenance, not write permission. |
| resources | `id is a stable UUID; source_id and locator are required; resource revision starts at 1; at most one primary resource exists per source.` Locator is absolute or named-root plus relative path. Managed resources require a verified SHA-256 after intake. | No mode column. Managed means a named-root locator resolves within library_root; other locators are linked. An absent explicit filing ID has the effective reserved Unfiled collection. Absolute paths newly recorded inside the library are normalized to its named-root locator. Availability is observed state. |
| collections and source_collections (slice 2) | `Collection hierarchy is acyclic; sibling names are unique after NFC and casefold; Unfiled cannot be deleted or reparented.` Source/collection pairs are unique. | One effective filing collection per managed resource; filing assignment adds missing source membership. Membership edits never move files. Slice 1 has only the reserved Unfiled assignment. |
| projects and project_sources | `Project name is unique and nonblank; project_id plus source_id is unique; cited is boolean.` | Cite adds association, uncite retains association, removing a cited association requires explicit uncite. Project revision increments for changed associations. |
| export_targets | `Canonical destination is unique; baseline advances only after verified publication.` Project/profile binding, last byte digest, profile fingerprint and operation ID. | Outside edits conflict. New paths need separate adoption. Restore never authorizes replacement without checking actual current bytes. |
| export_projections | `target_id plus operation_id plus source_id is unique.` Source revision, profile fingerprint, emitted entry digest and mapped field/type decisions. | Evidence for unchanged lossy re-import. Keep original richer types/current corrections; never match by citation key alone. |
| export_waivers | `A waiver binds exact loss fingerprint, source revision and destination profile fingerprint.` Actor and timestamp required. | Changes invalidate it; unknown override is only an operation flag, not a stored waiver. |
| operations and file_operations | `Non-null request_id is unique within the catalog; reserved resources/targets cannot be concurrently removed or relocated.` Request digest, settings fingerprint, result, effect intent, stat identities/digests, staging paths and state. | Request identity excludes settings; retries after config repair must not create metadata twice. Captured destinations never silently change: unresolved file effects require explicit recovery/replanning. |
| source_relations (slice 3) | `Asserted endpoint pairs retain their origin; unresolved endpoints remain explicit.` | Simple related-item pairs; no inferred merges or supporting-item subsystem. |
| search projection | `Every result identifies source ID, revision and matching field.` | Derived from active title, creators, abstracts, context and legacy tags; never PDF content or arbitrary original evidence. |

## Transactions, removal and retry

Changed source aggregates increment revision once; no-ops do not. Conditional updates must affect exactly one row. Enable foreign keys per connection. Use rollback journal mode, synchronous FULL and a five-second busy timeout; writes start with BEGIN IMMEDIATE. Close an export read snapshot before recording its external-effect intent. Do not upgrade a deferred read transaction into a write or hold write locks while copying/hashing files.

Read-only commands never create, migrate or semantically mutate the catalog. If a hot SQLite journal requires recovery, return recovery_required; an explicit recover operation opens for recovery. Do not silently turn read-only inspection into writable recovery or use immutable mode on a live catalog.

Removal retains source, original inputs, keys, relationship history and resource locators, with an inactive state. External files remain untouched. Reactivation previews retained relationships and conflicts; restores valid associations and reports unresolved ones without reusing keys. Import replay referring to a removed source reports source_removed instead of recreating it.

Command/target/payload determine request identity. Effective settings are recorded separately. A changed setting can repair a previously missing location, but cannot silently retarget a prepared file operation. Resume uses the captured intent or returns a specific replan-required result. A completed request returns its saved outcome regardless of later settings changes.

## Resource ownership and root relocation

Root containment uses resolved canonical paths, not string prefix comparison. No `..`, unsafe symlink traversal or absolute relative-path components. A root mapping into library_root makes named-root resources managed by location; their effective filing collection is Unfiled until explicitly assigned. Changing mappings never physically moves files. Bulk folder-to-filing assignment is a slice 2 previewed catalog-only operation, separate from selected reorganize.

The old Zotero tree initially remains a named external root. An explicitly authorized whole-tree move later changes one root mapping; no per-file rename is required. This design does not execute that move or claim a cross-volume mv is atomic. Root resolution and resource verification follow before filing assignment.

## External state and recovery

Copy states are prepared → staged → published → catalog_committed → complete, with conflict/recovery_needed on unsafe evidence. Slice 2 move adds cleanup_pending before complete. Export states are prepared → staged → published → baseline_committed → complete. Before each external effect, intent records enough identity to inspect a crash occurring before the next state update. A digest alone never proves ownership of an existing destination.

Backup includes a consistent database, exact configuration bytes, root/resource inventory and unresolved operation IDs. File contents are excluded unless explicitly included as independent copies/clones. Slice 1 restore is a documented verified procedure into a second catalog directory, not a full bundle/restore CLI. Later restore/import schema versions remain independent from bibliographic-profile versions. An incomplete restored directory must not open as ready.

## Revision details

Every transaction that changes semantic catalog state increments catalog_revision once; no-op/read/preview leaves it unchanged. List/search report catalog_id plus catalog_revision as their change token. Resource label, locator, primary or filing changes increment that resource revision once; stale resource writes fail. Changing primary increments both affected resource revisions and the parent source revision once. Resource relationship changes increment the parent source revision; copy locator commit compares both captured revisions. Observation-only checks do not write timestamps or revisions. Projects have revisions starting at 1; association changes increment their project revision once.
