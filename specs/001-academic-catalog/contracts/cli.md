# CLI and Configuration Contract v1

**Scope:** Slices 1 and 2 are delivered. Slice 3, delivered 2026-09-24, adds loc, explicit reorg and the move protocol.

## Invocation and results

`refs [--config PATH] [--catalog PATH] [--project-file PATH | --no-project-config] [--json] COMMAND`. Human output is default; JSON is one UTF-8 object plus newline on stdout, including usage failures. Progress goes to stderr. Help/version are textual exceptions. No interactive prompts. File payloads accept `-` for stdin. REF is an exact source UUID or citation key; ambiguity fails. Projects use exact names or IDs.

Unreadable or missing `--input` and `--patch` payloads report `invalid_input` with exit 2 and the selected path; `-` reads stdin through the same payload reader.

Mutations support --dry-run: validate and report intended effects without operation rows, locks, staging or key reservations. Opening an older catalog first performs the automatic schema upgrade and safety copy, even for a preview. Actual execution rechecks revisions/collisions; previewed generated keys are not reserved. Removal, reactivation, unlink and rekey require --execute after their default preview. Add/copy/export are explicit actions and require no extra confirmation. There is no --request-id or stored replay contract.

All results contain schema_version="1.0", command, status, data, warnings and errors. status is ok, partial or error; data is object or null. Warnings/errors contain code, message, nullable path, details and retryable. Return source/resource/import IDs where applicable; move results also identify file_operations rows. Never claim complete success after partial application. JSON exceptions are handled by refs' wrapper, not delegated to Typer help formatting.

Project cite and uncite results include citation_key and project_name; add with a file includes file_action, key set includes previous_key, and an `export_blocked` error names the destination in its path member in both output modes.

Failure envelopes name the command that failed; unexpected failures use `internal_error` with exit 5 and no traceback, invalid argument combinations use `invalid_invocation` with exit 2, and a bare command group writes help to stderr with one `invalid_invocation` envelope on stdout in JSON mode.

| Exit | Meaning |
| --- | --- |
| 0 | Complete/no-op, possibly warnings. |
| 2 | Invalid invocation/input/schema/configuration. |
| 3 | Missing/ambiguous identity, stale revision, conflict, blocked export or unsafe replacement. |
| 4 | Partially applied import or metadata saved but file action incomplete. |
| 5 | I/O/integrity/storage/recovery failure. |
| 6 | Retryable lock timeout after five seconds. |

Ctrl-C exits 130 where the process can handle it; a killed process cannot promise a report. Re-run imports safely; inspect source/destination after interrupted copy or export per the file contract. Unpartitionable input writes no sources; preserve its raw evidence only during actual import and report that. Mixed valid/invalid blocks return per-entry outcomes and exit 4.

## Commands

| Invocation | Inputs and effect |
| --- | --- |
| init | --reuse-config creates a catalog at an existing configuration’s catalog path using its configured library only when no ready catalog exists; refuse a ready catalog. Without the flag, behavior is unchanged. Explicit creation using selected config/catalog and optional --library-root PATH; --no-library permits metadata-only use. Private permissions; no overwrite. |
| paths | Resolve config/catalog/library and origins even before initialization. |
| config show | Inspect effective values, origins and validation diagnostics; replaces config validate. |
| schema NAME | Exactly source-create, source-patch, source-record, result; packaged, offline. |
| add | --format refs\|csljson\|bib --input PATH accepts one reference. With --file PATH, slice 3 uses the intake flags below. --keep-name preserves the basename. --dry-run shows normalization, key components and the destination. |
| show REF | Canonical record, revision, origins/corrections, context, limitations and resource list/availability. |
| update REF | --patch PATH or repeated --set PATH=JSON; --if-revision N required. |
| search QUERY | Exact key/normalized identifier match first, then literal lexical query; --project PROJECT, --limit N, --offset N; matched fields and source identities. |
| list | Same filters/pagination; --sort title\|key. |
| key set REF | --key TEXT --if-revision N --execute; preview otherwise, warn external citations remain unchanged. |
| import | --format bib --input PATH --origin TEXT; preview or apply .bib with per-entry report and aggregate run counts. |
| resource add REF | --path PATH or --root NAME --relative PATH; --link (default), --copy or --move; optional --keep-name, --label and media type. Copy/move intake uses lib/<loc> and the labelled filename convention. |
| resource unlink RESOURCE | --execute; association only, never file deletion. |
| resource check | Optional --source REF, --verify; availability/digest/root diagnostics, no repair/write. |
| open REF | Optional --resource RESOURCE; use sole resource or return choices; external opener, no content editing. |
| project create NAME | Optional description; unique name, repeats with identical values are no-ops. |
| project show [PROJECT] | Project and active cited sources, plus removed-source diagnostics; no argument lists projects. |
| project cite PROJECT REF | Add active source with cited=true; duplicate is no-op. `--from-import ORIGIN` refuses when a source belongs to more than one import origin. |
| project uncite PROJECT REF | Delete that association, leave source/other projects/files; absent association is no-op. |
| export | --project PROJECT --output PATH --profile portable-bibtex-v1; optional --adopt, --overwrite, --allow-unknown-mappings. Allowed defaults from config; complete four-class report. |
| remove REF | --if-revision N --execute; tombstone while retaining identity/key/relationships. |
| reactivate REF | Optional --if-revision N and --execute; restore same identity/key, report retained associations. |
| backup | --output NEW_DIRECTORY; consistent catalog/config snapshot and external-file inventory. |

--keep-name is valid with add --file unless --link is supplied. For resource add, it requires --copy or --move. It is invalid without a file. Repeated resource linking of the same source/locator is a no-op. Add with a duplicate candidate reports the identity rather than silently creating another or merging differences. Search/list default limit=50, offset=0; limit 1–1000, nonnegative offset. Report total/catalog revision; separate pages need not share a snapshot. All project associations are cited, so no --cited flag is needed.

## Slice 2 commands

| Invocation | Inputs and effect |
| --- | --- |
| import --format zotero --input DIR --origin TEXT | Apply or preview the [JSON directory](interchange.md); preserve input and persist per-entry accounting. Existing Bib invocation remains supported. |
| import list | Saved runs newest first: batch ID, origin, date, counts by status, batch revision. |
| import show BATCH [--status STATUS] | Show the saved run and entries, optionally filtered by applied, unchanged, conflict or invalid. |
| import reconcile BATCH (--take-incoming or --keep-current) KEY[.field]... [--execute --if-batch-revision N] | Preview or apply the [explicit incoming-value decisions](records.md#identity-and-non-overwriting-import); preview includes batch_revision and current source revisions; execution rechecks both and reports remaining conflicts. |
| collection list | Show imported hierarchy and membership counts. |
| list/search --collection PATH | Filter active sources by membership in the selected imported collection; retain existing project filters, sorting and pagination. |

BATCH is the saved import ID. Collection paths identify the imported hierarchy; ambiguous paths fail visibly. Collections remain imported history; loc controls filing.

## Slice 3 commands

| Invocation | Inputs and effect |
| --- | --- |
| add --loc PATH | Set source loc; show includes it. |
| add --file PATH | --move by default; --copy retains the original; --link leaves it in place. |
| resource add REF | --link by default; --copy and --move bring files into lib/<loc>. |
| update REF --set loc=JSON | Change loc through the existing revision-checked update; no file moves. Clear leaves it unplaced; loc never marks corrected_fields. |
| list/search --loc PATH | Exact case-insensitive loc filter, combined with existing filters. |
| reorg [--source REF \| --loc PREFIX] [--execute] | Preview by default. Select managed files disagreeing with a set loc, linked files with a set loc, and unfinished moves. Prefix matches complete path segments. Execute the [move protocol](files-and-recovery.md#move-protocol-and-journal), using D6 collision suffixes. |
| resource check [--kind KIND] | Show all kinds or filter to linked_unplaced, linked_pending, managed_mismatch, unfinished, or unrecorded. Unfinished includes intake originals; unrecorded scans library files against the resources table. For unrecorded files, recommend resource add on the reported path. |

The intake flags are mutually exclusive. Move without --loc writes unfiled; --link leaves loc empty. Only --move refuses files already recorded as resources of any source. Reorg is explicit intake for selected outside files under Principle II. Its completed report has `data.moves`, each with `operation_id`, `resource_id`, `old_path`, `new_path`, `old_name`, `new_name`, `state` and `error`; `data.unlinked_paths` lists untouched extras. Preview uses the same paths with null operation_id for new work, without creating operations. Human output lists every old/new pair.

## `add` and `import` are one engine with two contracts

Both routes pass through the same validator, identity rule, binding, originals table and format adapters; a source created either way is indistinguishable afterwards. They stay separate commands because they answer different callers, and the difference is the unit of work, not scale (owner discussion, 2026-09-22).

| | `add` | `import` |
| --- | --- | --- |
| Input | One record (refs JSON, CSL-JSON, one BibTeX entry), optionally with `--file` | A whole file or Zotero JSON directory, with `--origin` |
| Result | One outcome: created, already present, needs attention; key returned | A batch: per-entry applied, unchanged, conflict, invalid; every entry accounted for |
| Persisted run | None, unless the bound source has differing values: then one `imports` row with origin `add` and one entry, so `import show` and `import reconcile` apply | An `imports` row keyed by file digest and one `import_entries` row per entry |
| Re-run | Same record reports already present | Same file reports every entry unchanged |
| Conflicts | In the result envelope | Persisted; `import show` and `import reconcile` |
| Files | `--file` copies into the library or links | Records links found in the input; never copies |
| Malformed input | The record is refused, exit 2 | The entry becomes `invalid`; the rest apply, exit 4 |

Merging them would make one command carry two behaviours behind a flag; the shared interior is already one thing.

## Configuration and paths

Keep the SQLite catalog and its working files outside folders synchronized by a file-copy service. This is setup guidance: refs reports the selected path but does not detect every sync service or forbid a chosen location.

Select config by --config, then REFS_CONFIG, then ~/.config/refs/config.toml; select catalog by --catalog, then REFS_CATALOG, then config catalog.path. Explicit empty/invalid choices fail. No --home/REFS_HOME fallback. Canonical chosen data paths are /Volumes/Casa/refs/cat and /Volumes/Casa/refs/lib (owner's /casa aliases). Ordinary commands never create a missing catalog or substitute a location when Casa is unmounted.

Init creates only at explicitly selected valid locations. Missing volume mountpoints, incompatible/nonempty unrecognized destinations or conflicting existing config produce init_conflict. A ready compatible catalog/config is a no-op. Existing config is not overwritten; partial initialization reports the files for inspection rather than declaring ready. Create a ready marker only after schema/integrity checks. Normal setup does not authorize relocation or sync configuration.

```toml
schema_version = 1
[catalog]
path = "/Volumes/Casa/refs/cat"
[resources]
library_root = "/Volumes/Casa/refs/lib"
[resources.roots]
library = "/Volumes/Casa/refs/lib"
[keys]
template = "{author}-{year}-{title}"
without_creator = "{title}-{year}"
missing_year = "ND"
title_words = 2
stopwords = ["a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "with", "your"]  # shipped default; the owner's own config adds is, are, was, be, as, at, by, from, into, not
transliteration_policy = "creator-latin-v1"
[keys.corporate_aliases]
[titles]
policy = "english-title-case-v1"
minor_words = ["a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as", "at", "by", "in", "of", "on", "per", "to", "up", "via"]
protected_terms = ["AI", "GPT-4", "LaTeX", "PhD", "Python", "R", "nbgrader", "pH"]
[sorting]
ignore_leading_articles = ["a", "an", "the"]
[export]
profile = "portable-bibtex-v1"
```

Each resource root has a name and an absolute local path. The library_root setting and roots.library must agree. Relative paths in configuration are resolved against the configuration file; command-line paths are resolved against the current directory. Expand a leading ~, but never evaluate shell expressions. When the library is disabled, metadata capture, linking and export remain available. Copy and move intake fail if the library is unavailable; neither silently becomes a link.

Catalog/staging require agent write access to /Volumes/Casa/refs/cat, and intake also to lib. home_not_writable names the resolved failing path and required access. catalog_missing, unsupported_schema and recovery_required are distinct failures. Never sync the live database or staging; library sync, if later configured by the owner, is not backup.

## Project defaults and policy validation

Discover the nearest .refs.toml between cwd and Git worktree root, recognizing .git files/directories; outside Git inspect cwd only. --project-file selects explicitly; --no-project-config disables discovery. Do not merge ancestors. Allowed keys: project, export.profile, export.output, export.consumers. Invocation wins over project, then user config, then defaults. Project files cannot change catalog, roots, naming or credentials. Invalid selected config fails before mutation, with path/value/origin. A declared richer profile fails as unsupported; consumer detection never silently chooses one.

Key templates allow author/year/title tokens and literal separators only; without_creator excludes author. title_words is 1 or 2; Configured keys.stopwords, titles.minor_words, titles.protected_terms and sorting.ignore_leading_articles add to the built-in lists, with built-ins first and case-insensitive deduplication. config show reports these effective lists with a default+config origin when configured. The built-in entries cannot be removed by configuration. Other nonblank policy lists deduplicate case-insensitively. Corporate aliases map exact NFC literal names to explicit valid tokens. Policy changes affect future generation, never existing keys or explicit corrections. Title Case capitalizes first/last words and words after an explicit subtitle boundary; minor words otherwise stay lowercase. Hyphen parts use their position in the whole title. Protected terms/whole-title flags win. Sort case-insensitively by sort title, numeric edition, year, then binary key; missing numeric values follow present ones. Strip only an initial whole-word article, ignoring opening quotation marks for comparison.

## Result member names

The source-add outcome member is `data.outcome`, with the names `created`, `already_present` and `needs_attention`. Search and list use `data.items`, `total`, `limit`, `offset` and `catalog_revision`. Each item uses `matches` for its matching-field evidence and `exact_match` for its exact-match indicator. A match has the members `field`, `origin` and `text`. Project inspection uses `items` for the project list, and `sources` and `removed_sources` for a selected project's source lists. Export assessments use `class`, `mapping_id` and `override` inside warning details; blocked-entry details use `entries`, with each entry named by `citation_key`, `code`, `class`, `path` and `message`.

Configuration inspection uses `data.config`, `values`, `origins`, `paths` and `diagnostics`. Effective setting names are dotted keys in `values` and `origins`.
