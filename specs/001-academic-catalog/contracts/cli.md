# CLI and Configuration Contract v1

**Implementation proposal, 2026-09-21.** This is the full slice 1 command surface approved in audit §14. Deferred commands have no placeholders.

## Invocation and results

`refs [--config PATH] [--catalog PATH] [--project-file PATH | --no-project-config] [--json] COMMAND`. Human output is default; JSON is one UTF-8 object plus newline on stdout, including usage failures. Progress goes to stderr. Help/version are textual exceptions. No interactive prompts. File payloads accept `-` for stdin. REF is an exact source UUID or citation key; ambiguity fails. Projects use exact names or IDs.

Mutations support --dry-run: validate and report intended effects without rows, locks, staging or key reservations. Actual execution rechecks revisions/collisions; previewed generated keys are not reserved. Removal, reactivation, unlink and rekey require --execute after their default preview. Add/copy/export are explicit actions and require no extra confirmation. There is no --request-id or stored replay contract.

All results contain schema_version="1.0", command, status, data, warnings and errors. status is ok, partial or error; data is object or null. Warnings/errors contain code, message, nullable path, details and retryable. Return source/resource/import IDs where applicable; there is no operation ID. Never claim complete success after partial application. JSON exceptions are handled by refs' wrapper, not delegated to Typer help formatting.

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
| init | Explicit creation using selected config/catalog and optional --library-root PATH; --no-library permits metadata-only use. Private permissions; no overwrite. |
| paths | Resolve config/catalog/library and origins even before initialization. |
| config show | Inspect effective values, origins and validation diagnostics; replaces config validate. |
| schema NAME | Exactly source-create, source-patch, source-record, result; packaged, offline. |
| add | --format refs\|csljson\|bib --input PATH accepts one reference. With --file PATH, the file is copied into Unfiled by default; --link keeps it in place. --keep-name preserves the copied file's name. --dry-run shows normalization, key components and the destination. |
| show REF | Canonical record, revision, origins/corrections, context, limitations and resource list/availability. |
| update REF | --patch PATH or repeated --set PATH=JSON; --if-revision N required. |
| search QUERY | Exact key/normalized identifier match first, then literal lexical query; --project PROJECT, --limit N, --offset N; matched fields and source identities. |
| list | Same filters/pagination; --sort title\|key. |
| key set REF | --key TEXT --if-revision N --execute; preview otherwise, warn external citations remain unchanged. |
| import | --format bib --input PATH --origin TEXT; preview or apply .bib with per-entry report and aggregate run counts. No subcommands. |
| resource add REF | --path PATH or --root NAME --relative PATH; optional --copy, --keep-name, label/media type. Default links in place; --copy uses Unfiled. |
| resource unlink RESOURCE | --if-revision N --execute; association only, never file deletion. |
| resource check | Optional --source REF, --verify; availability/digest/root diagnostics, no repair/write. |
| open REF | Optional --resource RESOURCE; use sole resource or return choices; external opener, no content editing. |
| project create NAME | Optional description; unique name, repeats with identical values are no-ops. |
| project show [PROJECT] | Project and active cited sources, plus removed-source diagnostics; no argument lists projects. |
| project cite PROJECT REF | Add active source with cited=true; duplicate is no-op. |
| project uncite PROJECT REF | Delete that association, leave source/other projects/files; absent association is no-op. |
| export | --project PROJECT --output PATH --profile portable-bibtex-v1; optional --adopt, --overwrite, --allow-unknown-mappings. Allowed defaults from config; complete four-class report. |
| remove REF | --if-revision N --execute; tombstone while retaining identity/key/relationships. |
| reactivate REF | --if-revision N --execute; restore same identity/key, report retained associations. |
| backup | --output NEW_DIRECTORY; consistent catalog/config snapshot and external-file inventory. |

--keep-name is valid with add --file unless --link is supplied. For resource add, it requires --copy. It is invalid without a file. Repeated resource linking of the same source/locator is a no-op. Add with a duplicate candidate reports the identity rather than silently creating another or merging differences. Search/list default limit=50, offset=0; limit 1–1000, nonnegative offset. Report total/catalog revision; separate pages need not share a snapshot. All project associations are cited, so no --cited flag is needed.

## Configuration and paths

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
stopwords = ["a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "with", "your"]
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

Each resource root has a name and an absolute local path. The library_root setting and roots.library must agree. Relative paths in configuration are resolved against the configuration file; command-line paths are resolved against the current directory. Expand a leading ~, but never evaluate shell expressions. When the library is disabled, metadata capture, linking and export remain available. Both add --file without --link and resource add --copy fail if the library is unavailable. Neither command silently changes the requested action. Slice 1 retains the original file after every copy; the accepted move default arrives later.

Catalog/staging require agent write access to /Volumes/Casa/refs/cat, and intake also to lib. home_not_writable names the resolved failing path and required access. catalog_missing, unsupported_schema and recovery_required are distinct failures. Never sync the live database or staging; library sync, if later configured by the owner, is not backup.

## Project defaults and policy validation

Discover the nearest .refs.toml between cwd and Git worktree root, recognizing .git files/directories; outside Git inspect cwd only. --project-file selects explicitly; --no-project-config disables discovery. Do not merge ancestors. Allowed keys: project, export.profile, export.output, export.consumers. Invocation wins over project, then user config, then defaults. Project files cannot change catalog, roots, naming or credentials. Invalid selected config fails before mutation, with path/value/origin. A declared richer profile fails as unsupported; consumer detection never silently chooses one.

Key templates allow author/year/title tokens and literal separators only; without_creator excludes author. title_words is 1 or 2; nonblank policy lists deduplicate case-insensitively. Corporate aliases map exact NFC literal names to explicit valid tokens. Policy changes affect future generation, never existing keys or explicit corrections. Title Case capitalizes first/last words and words after an explicit subtitle boundary; minor words otherwise stay lowercase. Hyphen parts use their position in the whole title. Protected terms/whole-title flags win. Sort case-insensitively by sort title, numeric edition, year, then binary key; missing numeric values follow present ones. Strip only an initial whole-word article, ignoring opening quotation marks for comparison.

## Result member names

The source-add outcome member is `data.outcome`, with the names `created`, `already_present` and `needs_attention`. Search and list use `data.items`, `total`, `limit`, `offset` and `catalog_revision`. Each item uses `matches` for its matching-field evidence and `exact_match` for its exact-match indicator. A match has the members `field`, `origin` and `text`. Project inspection uses `items` for the project list, and `sources` and `removed_sources` for a selected project's source lists. Export assessments use `class`, `mapping_id` and `override` inside warning details; blocked-entry details use `entries`, with each entry named by `citation_key`, `code`, `class`, `path` and `message`.

Configuration inspection uses `data.config`, `values`, `origins`, `paths` and `diagnostics`. Effective setting names are dotted keys in `values` and `origins`.
