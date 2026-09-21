# CLI Contract v1

**Status**: Planned public interface for [the feature](../spec.md). These commands become available during implementation; this document does not claim they already run.

## Invocation and Global Options

`refs [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]` is the canonical grammar. Global options appear before the command: `--home PATH`, `--project-file PATH`, `--no-project-config`, `--json`, `--help`, and `--version`. `--project-file` and `--no-project-config` are mutually exclusive. Human output is the default; JSON output is one UTF-8 object plus a newline on stdout. Diagnostics/progress go to stderr. When `--json` is present, usage/validation failures also use the envelope below. Help and version are explicit textual exceptions; machine discovery uses `schema`.

Mutating commands accept `--dry-run` and `--request-id TEXT` unless noted. Dry run validates and reports proposed effects without creating catalog rows, staging files, adoption state, or request reservations. Actual execution rechecks conflicts and revisions; preview is not a reservation. Request IDs are 1–128 printable ASCII characters without whitespace; reuse with a different resolved request is an error. Completed matching requests return their prior outcome. Partial or interrupted requests resume pending safe steps after acquiring the required lock and checking journal state; unresolved conflicts require explicit reconciliation rather than automatic retry. Fingerprints include command, canonical targets, payload bytes/values, and effective behavior-changing settings; exclude output formatting and `--dry-run`.

Destructive catalog removals and rekeying use `--execute` after an inspectable preview, even with `--json`. No command prompts. Managed intake itself is authorized by the add command and its configured/default action; `--dry-run` is available, but a separate confirmation is not required for routine default intake. `reorganize` requires `--execute`. Explicit export is sufficient for an adopted unchanged target; see [file operations](files-and-recovery.md).

## Commands

`REF` means exact source UUID or exact citation key; if a string could identify two different records, return `ambiguous_reference`. Collection and project selectors accept UUID or exact canonical path/name. Resource/operation/batch/entry selectors are UUIDs. All `--input PATH` options accept `-` for stdin except multi-file snapshot inputs. Metadata schemas are in [records](records.md).

| Command | Inputs/options | Result and side effects |
| --- | --- | --- |
| `init` | `--library-root PATH` optional | Explicitly creates a home, config defaults, catalog, lock, and ready marker. Repeating against a valid home preserves it. No library root is guessed; metadata-only use remains possible. |
| `paths` | None | Resolved home/config/project/root paths; works before initialization. |
| `config show` | `--sources` | Effective values, origins, validation diagnostics; never runs credential helpers. |
| `config validate` | None | Validates configuration without opening/creating a missing catalog. |
| `schema NAME` | `source-create`, `source-patch`, `source-record`, `result`, `reconcile`, `config`, `snapshot-manifest`, `library-export` | Emits one JSON Schema document; with `--json`, schema is inside `data`. Generated from boundary models; no network access. |
| `add` | `--input PATH`; optional `--file PATH`, `--intake move\|copy\|link`, `--collection COLLECTION` | Creates/reuses source or reports conflict. `--file` denotes new-file acquisition, so default is managed move. Metadata outcome and attachment operation outcomes are reported separately. |
| `show REF` | None | Complete source record including typed citation/native fields and profile ID, revision, provenance, resource and relationship summaries, and associated imported supporting records. |
| `update REF` | `--patch PATH --if-revision N` | Explicit field patch; returns unchanged/updated/conflict. No implicit rekey or rename. |
| `normalize REF` | `--if-revision N`, optional `--execute` | Without execute, returns normalization preview; with execute, updates derived fields only, preserving overrides. |
| `key preview` | `--input PATH` | Shows generated components/policy/warnings without reserving a key. |
| `key set REF` | `--key TEXT --if-revision N --execute` | Explicit unique-key replacement with external-citation warning; without execute returns preview. |
| `filename REF` | `--extension TEXT` | Returns a generated filename and components; does not rename any file. |
| `search QUERY` | `--collection`, `--project`, `--cited`, `--limit N`, `--offset N` | Exact lookup plus lexical matches with evidence origins; no automatic resource opening. |
| `list` | Same filters; `--sort title\|key`; `--limit N`, `--offset N` | Stable paginated listing; title default. |
| `index rebuild` | `--execute` | Explicitly rebuilds the derived search projection; otherwise returns planned scope. |
| `import` | `--format bibtex\|biblatex\|zotero-snapshot --input PATH --origin TEXT` | Retains original input and applies conflict-free entries. Returns a batch and counts; dry run persists nothing. Snapshot input is a directory manifest. |
| `import show BATCH` | Optional `--status pending\|conflict\|invalid\|applied\|unchanged` | Lists entry outcomes, mapping/field coverage limitations, supporting-item records including standalone/unresolved parents, raw locators, and conflicts. |
| `import resume BATCH` | None | Retries pending/interrupted entries without duplicating completed work. It does not silently accept conflicts. |
| `import reconcile BATCH` | `--input PATH` | Applies explicit per-entry identity/field decisions with revision checks. See records contract. |
| `collection create PATH` | Optional `--parent COLLECTION` for a single name | Creates requested collection; missing parents are errors rather than implicit structure. |
| `collection list` | None | Hierarchy, IDs, memberships, filing counts, effective folder mappings. |
| `collection update COLLECTION` | `--name TEXT` or `--parent COLLECTION`; `--if-revision N` | Renames/reparents without moving files; validates cycle/sibling rules. |
| `collection add COLLECTION REF` | None | Adds membership; no move. |
| `collection remove COLLECTION REF` | Optional `--filing-reassign COLLECTION` or `--unlink-managed` | Removes membership; affected filing assignments must be explicitly resolved, with no filesystem move. |
| `collection delete COLLECTION` | `--if-revision N --execute` | Only empty, unreferenced, non-system collections; otherwise returns dependents. |
| `resource add REF` | `--path PATH` or `--root NAME --relative PATH`; optional label/media type | Explicit link-in-place operation, preserving file/path. Distinct from acquisition via `add --file` or `resource intake`. |
| `resource intake REF` | `--path PATH`, optional `--intake move\|copy\|link`, `--collection COLLECTION`, label | Acquires new attachment; move default and `Unfiled` fallback. Returns operation state and final location. |
| `resource list REF` | None | IDs, labels, paths, modes, filing/primary status, recorded availability. |
| `resource primary RESOURCE` | `--if-revision N` | Sets one primary and clears the earlier designation. |
| `resource adopt RESOURCE` | `--collection COLLECTION --if-revision N` | Changes to managed mode without moving the existing file. |
| `resource file-under RESOURCE` | `--collection COLLECTION --if-revision N` | Changes intended filing assignment and adds membership if absent; no move. |
| `resource unlink RESOURCE` | `--if-revision N --execute` | Removes catalog link after preview; no external deletion. |
| `resource check` | Optional `--source REF` | Read-only current diagnostics; does not persist check timestamps or repair anything. |
| `reorganize` | One or more `--resource RESOURCE`; `--execute` for actual moves | Explicit selected managed relocation; no broad `--all` consolidation. Preview returns paths and risks. |
| `open REF` | Optional `--resource RESOURCE` | Opens primary, otherwise sole resource; multiple candidates return choices. No editing or copying. |
| `project create NAME` | Optional description | Creates activity identity. |
| `project list` | None | Projects with membership/citation counts. |
| `project show PROJECT` | None | Project revision and associated/cited sources. |
| `project add PROJECT REF` | None | Adds background membership. |
| `project cite PROJECT REF` | None | Adds membership if needed and selects citation. |
| `project uncite PROJECT REF` | None | Removes citation selection only. |
| `project remove PROJECT REF` | Optional `--uncite` | Removes membership; rejects a cited source unless `--uncite` supplied. |
| `export` | `--project PROJECT --format biblatex\|bibtex --output PATH`; optional `--adopt --reconciliation BATCH`, `--overwrite` | Writes explicit project bibliography; project defaults can supply arguments. Existing unadopted output requires adoption evidence. Adopted outside edits conflict unless explicitly overwritten or reconciled. |
| `remove REF` | `--if-revision N --execute` | Explicit catalog removal after dependent-relationship preview; never deletes files. |
| `operations list` / `operations show OP` | Optional state filter for list | Read-only applied and recoverable outcomes. |
| `recover OP` | `--execute` | Inspects and completes only verified safe pending steps; unknown fingerprints return conflict. Without execute, preview only. |
| `backup` | `--output DIRECTORY` | New versioned consistent backup bundle; external contents excluded. |
| `restore` | `--input DIRECTORY` | Restores into selected new empty home; this command may operate without an existing home. |
| `library export` | `--output DIRECTORY` | New logical JSON/JSONL export bundle with originals and inventory. |
| `migrate` | `--execute` | Preview and explicitly apply supported catalog schema migrations with backup. |

The `import` group is invokable without a subcommand: import options select the default import operation; `show`, `resume`, and `reconcile` select administration. Search has only a literal query argument; index administration uses the separate `index` group so reserved command words remain searchable.

Listing defaults are `limit=50`, `offset=0`; limit is 1–1000 and offset is nonnegative. Each paginated result reports total matches, limit, offset, and a snapshot identifier; pagination across separate calls is not a frozen snapshot and must expose revision changes. `--cited` requires a project selector. Descendant collections are included by default; `--collection-exact` selects only direct membership.

## Result Envelope and Exit Status

```json
{
  "schema_version": "1.0",
  "command": "add",
  "status": "ok",
  "operation_id": "95be7cde-5c77-41b2-ae8f-3fd2c28c85cc",
  "data": {"source_id": "a5b4de9b-2a59-440e-bc61-40a9b016d33c", "citation_key": "smith-2024-turingTrap", "revision": 1, "outcome": "created"},
  "warnings": [],
  "errors": []
}
```

All seven envelope keys are present; `operation_id` is null for read-only operations and previews. `status` is `ok|partial|error`; dry-run data contains `dry_run:true`. Warnings/errors have `code`, `message`, `path` nullable, `details` object, and `retryable` boolean. `data` is an object or null. Results must not include resolved secrets. Partial import and metadata-success/file-failure use `partial` with complete accounting, never misleading success.

| Exit | Meaning |
| --- | --- |
| 0 | Completed or unchanged; warnings alone do not fail. |
| 2 | Invalid invocation, payload, unsupported schema, or configuration. |
| 3 | Missing/ambiguous target, stale revision, identity conflict, unsafe destination, or outside edit; no silent overwrite. |
| 4 | Partial application with unresolved/invalid entries or incomplete external effects. |
| 5 | I/O, integrity, unsupported storage, or recovery failure. |
| 6 | Retryable lock contention after the bounded wait. |

A malformed whole input that cannot be partitioned fails with exit 2 and no source writes; raw bytes may be retained by an actual import operation, and its result must report that retained artifact. Parseable mixed inputs use per-entry outcomes and exit 4. Ctrl-C returns a recoverable interrupted result when possible, otherwise process exit 130; the journal remains the authority for the next `operations`/`recover` call.
