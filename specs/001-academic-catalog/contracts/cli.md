# CLI Contract v1

**Status:** planned interface. Slice 1 is explicitly bounded below; later commands are design reservations, not available features.

## Invocation and mutation rules

`refs [--config PATH] [--catalog PATH] [--project-file PATH | --no-project-config] [--json] COMMAND`. Paths/configuration follow configuration.md. Global help/version are textual exceptions; schema provides machine discovery. Human output is default. JSON is one UTF-8 result object plus newline on stdout, including usage failures; progress goes to stderr. No command prompts.

Mutations accept --dry-run and --request-id TEXT unless noted. Dry run validates without persistent changes, stages or reservations. Execution rechecks revisions and collisions. Request IDs contain 1–128 nonwhitespace printable ASCII characters. Identity fingerprints contain command, target selectors and semantic payload, excluding formatting, preview and configuration. Store settings separately. A changed payload under the same ID is request_id_reused; a completed identical request replays. Interrupted file effects follow captured intent and explicit recovery, never silently retarget after config changes.

Removal, rekey, reactivation and reorganize preview unless --execute is provided. Ordinary explicit add/copy/export operations need no second confirmation. REF is an exact source UUID or citation key; ambiguity errors rather than guesses. UUIDs identify resources, operations and import entries. Project names are exact and unique. Input paths accept - for stdin where a file payload is supported.

## Slice 1 commands

| Command | Inputs | Result/effect |
| --- | --- | --- |
| init | --library-root PATH optional; global --config/--catalog | Explicit creation with private permissions and ready marker, no overwrite. Library default is the chosen lib path; metadata-only setup can explicitly disable intake. |
| paths; config show; config validate | show optionally --sources | Separate config/catalog/root paths and origins, including missing/unwritable locations. No implicit catalog creation. |
| schema NAME | source-create, source-patch, source-record, result, config, reconcile, snapshot-manifest | Packaged generated schemas, no network. |
| add | --format refs\|csljson\|bib --input PATH; optional --file PATH --intake copy\|link | One record; optional verified non-destructive copy or link. No move in slice 1. File failure after metadata success is partial with IDs. |
| show REF | none | Complete canonical values, revision, native label, provenance, context, resources, limitations. |
| update REF | --patch PATH or repeated --set PATH=JSON; --if-revision N | Same validator and revision guard for humans and agents. |
| normalize REF | --if-revision N; --execute | Preview/apply derived normalization, preserving explicit overrides. |
| key preview | --input PATH | Components, policy and warnings without key reservation. |
| key set REF | --key TEXT --if-revision N --execute | Explicit replacement; external citations are not rewritten. |
| filename REF | --extension TEXT | Accepted filename preview only. |
| search QUERY; list | --project PROJECT, --cited, --limit N, --offset N; list --sort title\|key | Exact lookup and lexical retrieval with matching origin. --cited requires project. Collection filters arrive in slice 2. |
| index rebuild | --execute | Explicit derived projection rebuild. |
| import | --format bib --input PATH --origin TEXT | Per-entry application with preserved conflicts/originals; mixed files allowed. |
| import show BATCH; import resume BATCH | optional status on show | Accountable outcomes; resume pending work only. |
| import reconcile BATCH | --input PATH | Explicit identity/field decisions under revisions. |
| resource add REF | --path PATH or --root NAME --relative PATH; optional label/media type | Record an existing path without moving. Normalize absolute in-library paths to the library root. |
| resource intake REF | --path PATH --intake copy\|link; optional label | Copy into Unfiled or link; preserve filename. |
| resource list REF; resource primary RESOURCE | primary needs --if-revision N | Explicit primary selection; at most one per source. |
| resource unlink RESOURCE | --if-revision N --execute | Catalog link removal only. |
| resource check | optional --source REF, --verify | Current availability/digests/conflict-file diagnostics, no repair or timestamp write. |
| open REF | optional --resource RESOURCE | Open primary, else sole resource; otherwise return choices. Never guess or alter content. |
| project create NAME; project list; project show PROJECT | optional description on create | Project IDs, revisions and memberships. |
| project add PROJECT REF; project cite PROJECT REF; project uncite PROJECT REF; project remove PROJECT REF | remove needs --uncite if selected | Background membership and citation selection remain distinct; repeats are no-ops. |
| export | --project PROJECT --profile portable-bibtex-v1 --output PATH; optional --adopt --reconciliation BATCH, --overwrite, --allow-unknown-mappings | Explicit output only; project defaults may supply arguments. Four-class report before any write; complete projection evidence after publication. |
| export waive REF | --loss FINGERPRINT --profile-fingerprint TEXT --if-revision N | Store an explicit current blocking-loss waiver with actor/time; never blanket permission. |
| remove REF; reactivate REF | --if-revision N --execute | Preview dependent associations; preserve identity/key and external files. |
| operations list; operations show OP; recover [OP] | recover needs --execute | Inspect or resume only verified safe effects. |
| backup | --output NEW_DIRECTORY | Consistent snapshot including unresolved operations; external bytes excluded and listed. |

Import is an invokable group: flags without subcommand run import; show/resume/reconcile are subcommands. Search takes literal text, with index administration in a separate group. Pagination defaults limit=50, offset=0; limit must be 1–1000, offset nonnegative. Report total and catalog snapshot/revision; separate pages need not share a snapshot and must expose changes.

Slice 1 restoration uses the documented procedure, not an unfinished restore command. A missing catalog reports catalog_missing; no automatic init. Wrong schema yields unsupported_schema; hot-journal inspection yields recovery_required. The stable home_not_writable error carries resolved catalog path and required access.

## Later slices

Slice 2 adds collection create/list/update/add/remove/delete, resource file-under, resource assign-filing --from-folders, and selected reorganize. Assign-filing previews folder mappings/ambiguities and needs --execute, with no physical movement. There is no resource adopt or --unlink-managed. Move becomes the default for new-file intake in slice 2; linked outside files cannot be reorganized.

Slice 3 adds the published Zotero JSON extractor input and migration reconciliation details. Slice 4 adds restore, library export, backup --include-managed and explicit schema migration. Unsupported commands/profile names return unsupported_in_slice; do not silently perform an approximation.

## Result envelope

All results contain schema_version="1.0", command, status, operation_id, data, warnings and errors. status is ok, partial or error; operation_id is null for reads/previews. data is object or null; dry runs include dry_run=true. Each warning/error has code, message, nullable path, details object and retryable boolean. No resolved secrets. Partial entry application or file failure never reports complete success.

| Exit | Meaning |
| --- | --- |
| 0 | Complete/no-op; warnings alone. |
| 2 | Invalid invocation, payload, schema or configuration. |
| 3 | Missing/ambiguous target, stale revision, identity conflict, blocked export or unsafe replacement. |
| 4 | Partial application or incomplete external effects. |
| 5 | I/O, integrity, unsupported storage or recovery failure. |
| 6 | Retryable lock timeout after five seconds. |

Unpartitionable input yields exit 2 with no source writes; actual import may preserve its raw input and reports that. Mixed parseable entries yield per-entry outcomes and exit 4. Ctrl-C records interruption where possible, otherwise exits 130; durable intents guide recovery. Typer exceptions are translated through refs' own main wrapper; help text is not the machine contract.

## Catalog recovery

`recover --catalog-state --execute` is mutually exclusive with an OP argument. Without execute it inspects journal/ready-state diagnostics without opening writable recovery. With execute it acquires coordination, opens the existing selected SQLite catalog read-write so SQLite can recover its hot journal, then checks integrity/foreign keys/schema before marking it usable. It does not resume file operations or initialize a missing catalog. Failure retains a recovery_required result. `recover OP --execute` handles only an identified file/export intent after the catalog is usable.
