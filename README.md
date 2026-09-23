# refs

refs is a personal SQLite source catalog with explicit bibliography export. Capture a reference, find and correct it, select citations for a project, then write a portable BibTeX bibliography. Human text is the default; global `--json` selects the versioned result envelope.

## Install and run

Python 3.14 and uv are required for development. The lockfile retains a three-day dependency cooldown.

```bash
uv sync --locked
uv run --locked refs --help
uv build --wheel
```

A built wheel can be installed into a Python 3.14 environment with `uv pip install --python /path/to/environment/bin/python dist/refs-0.1.0-py3-none-any.whl`. It includes the mapping registry, naming data, migrations and code that supplies all four offline schemas. There is no runtime network lookup.

Use explicit disposable locations to try the tool:

```bash
REFS_DEMO_HOME="$(mktemp -d)"
export REFS_CONFIG="$REFS_DEMO_HOME/config.toml"
export REFS_CATALOG="$REFS_DEMO_HOME/cat"
uv run --locked refs --no-project-config init --library-root "$REFS_DEMO_HOME/lib"
uv run --locked refs --no-project-config add --format refs --input tests/fixtures/reference.json
uv run --locked refs --no-project-config show smith-2024-learningPython
uv run --locked refs --no-project-config project create example
uv run --locked refs --no-project-config project cite example smith-2024-learningPython
uv run --locked refs --no-project-config export --project example --output "$REFS_DEMO_HOME/references.bib"
```

`add` accepts `refs`, `csljson` and single-entry `bib` input. `import` processes an existing bibliography without overwriting current decisions; conflicts are settled with `update` or the reviewed `import reconcile` command. Original input bytes remain in the catalog. Existing citation keys are preserved.

## Commands

Global options precede the command: `--config PATH`, `--catalog PATH`, `--project-file PATH`, `--no-project-config` and `--json`.

| Invocation | Purpose |
| --- | --- |
| `init` | Create an explicitly selected catalog; `--reuse-config` recreates a missing catalog at its configured location and refuses an existing ready catalog. |
| `paths` | Show resolved locations and their origins, including before init. |
| `config show` | Show effective settings, origins and validation results. |
| `schema NAME` | Print an offline `source-create`, `source-patch`, `source-record` or `result` schema. |
| `add --format FORMAT --input PATH` | Capture one reference; `--dry-run` previews it. |
| `show REF` | Inspect a source, its files and projects. |
| `update REF --if-revision N --set PATH=JSON` | Correct fields; alternatively use `--patch PATH`. |
| `key set REF --key KEY --if-revision N --execute` | Explicitly change a citation key. |
| `remove REF --if-revision N --execute` | Retain a source and its reserved key as removed. |
| `reactivate REF [--if-revision N] --execute` | Reactivate that same source. |
| `search QUERY` | Find sources with matching-field evidence. |
| `list` | List active sources; `list` and `search` accept `--project` and `--collection PATH`. |
| `import --format bib --input PATH` | Import entries with counts and individual outcomes. |
| `import --format zotero --input DIR --origin TEXT` | Import a published API v3 JSON directory with per-item evidence. |
| `import show BATCH [--status STATUS]` | Inspect saved outcomes, candidates, conflicting values and decisions. |
| `import reconcile BATCH --take-incoming KEY[.field]` | Preview incoming corrections; repeat the option for multiple selections. Execute with `--execute --if-batch-revision N` from that preview. |
| `collection list` | Show imported hierarchy, empty collections and direct active membership counts. |
| `resource add REF --path PATH` | Link a file; `--copy` brings it into the library. |
| `resource unlink ID --execute` | Remove an association without deleting bytes. |
| `resource check` | Report availability; `--verify` also checks copied-file hashes. |
| `open REF` | Open the sole resource; choose `--resource ID` when there are several. |
| `project create NAME` | Create a cited-source project. |
| `project show [NAME]` | Inspect one project or list them all. |
| `project cite PROJECT REF` | Include a source in a project. |
| `project uncite PROJECT REF` | Remove that citation association. |
| `export --project PROJECT --output PATH` | Explicitly publish the selected bibliography. |
| `backup --output NEW_DIRECTORY` | Save a verified catalog snapshot and resource inventory. |

Rekey, remove, reactivate and unlink preview unless `--execute` is supplied. Mutations also accept `--dry-run`. Source revisions reject stale changes; reconciliation checks its batch and source revisions. Exit codes are 0 for success, 2 for invalid input/configuration, 3 for conflicts, 4 for partial application, 5 for storage/integrity failure and 6 for retryable lock contention. Partial imports print their summary before the hint; JSON entries have `status` values `applied`, `unchanged`, `conflict` or `invalid`.

## Files and export

`add --file PATH` moves a new file into the library by default: it copies and verifies the bytes, records the managed path, then deletes the original. Use `--copy` to retain the original or `--link` to leave it in place. `resource add` still links by default and offers the same three flags. Copy and move use the source's loc, assigning `unfiled` only when it has none. Intake uses the filename convention unless `--keep-name`; reorg preserves names, adding collision suffixes when necessary.

Loc is optional. Set it with `add --loc PATH` or revision-checked `update REF --set 'loc="Papers/Topic"'`; changing or clearing it never moves files. `show` displays loc, and `list --loc` and `search --loc` filter it. Reorg previews by default:

```bash
refs --no-project-config reorg --source KEY
refs --no-project-config reorg --source KEY --execute
refs --no-project-config reorg --loc Papers
refs --no-project-config resource check --kind unfinished
refs --no-project-config resource check --kind unrecorded
```

Use these commands only with the intended configuration and catalog explicitly selected. `--source` and `--loc` are alternatives; a loc prefix matches complete path segments. Reorg skips new work for sources without loc, but retries their unfinished operations. Repeat an interrupted command to resume the recorded operation. The report lists old and new paths and untouched extras; `--json` retains operation IDs and errors. Resource checks distinguish linked files without loc, linked files awaiting reorg, managed folder mismatches, unfinished moves and unrecorded library files. Backup excludes all attachment bytes, so retain an independent file backup before a bulk move.

Only explicit export writes bibliography files. The portable profile reports missing facts and documented fallbacks, blocks meaning-changing losses, and blocks unknown mappings unless `--allow-unknown-mappings` is supplied for that run. To replace an existing unowned bibliography, import its exact current bytes, then use `export --adopt --overwrite`. Outside edits are refused unless replacement is explicitly authorized.

## Configuration

Configuration selection is flag, then `REFS_CONFIG`, then the user default. Catalog selection is flag, then `REFS_CATALOG`, then `catalog.path`. Missing catalogs never trigger fallback initialization. Agents need write access to the selected catalog and staging directory, and to the library for copying.

The nearest `.refs.toml` inside the current Git worktree may supply `project` and `export.profile`, `export.output`, and `export.consumers`. Outside Git, only the current directory is checked. `--project-file` selects one explicitly; `--no-project-config` disables discovery. A project file cannot override catalog locations, roots or naming. Invocation options take precedence. Only `portable-bibtex-v1` is implemented.

Use `config show` to inspect user naming, title and sorting policies. Policy changes affect future generation; existing citation keys and explicit corrections remain intact. Resource roots are named configuration paths; changing a root never moves file bytes.

## Demonstration and recovery

```bash
scripts/demo.sh                 # narrated; pauses only on a terminal
scripts/demo.sh --no-pause      # narrated without pauses
scripts/demo.sh --smoke         # compact end-to-end verification
scripts/demo.sh --keep          # retain the temporary home for inspection
```

The demo uses synthetic data and explicit temporary paths for all six stories. It needs `jq` and the installed project environment. Packaging checks can select another installation through `REFS_BIN` and `REFS_PYTHON`.

[Restore instructions](docs/restore.md) contain the exact tested manual restore and SQLite hot-journal commands. Backup contains no external file bytes, including managed files. Preserve those files independently. The manual procedure validates the snapshot and opens a second home; no restore or recover CLI is installed.

## Verification and current boundaries

```bash
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ty check src/refs
scripts/demo.sh --smoke
```

Tests use synthetic inputs and temporary homes. Rendering checks use Pandoc, Biber and classic BibTeX with `elsarticle-num`. Dependency pins and the three-day cooldown remain in force. Unsupported Bib macros, inheritance and TeX constructs remain preserved with limitations. Copies protect against process interruption and ordinary I/O failures; they do not promise native filesystem metadata preservation or power-loss durability.

The slice 1 checkpoint and real-paper trial are recorded in [slice 1 acceptance](specs/001-academic-catalog/reviews/slice-1-acceptance.md). Slice 2 adds Zotero ingest and read-only collection browsing. Its [acceptance record](specs/001-academic-catalog/reviews/slice-2-acceptance.md) includes the owner-executed cutover. Slice 3 adds explicit file organization; its [acceptance record](specs/001-academic-catalog/reviews/slice-3-acceptance.md) separates disposable rehearsal evidence from the pending owner-executed move.

## Zotero ingest

[The one-time extractor](tools/zotero_extract/README.md) reads a Zotero 6 userdata-121 snapshot and produces the JSON directory; it is outside the installed package. The JSON interface also allows a future local API bridge. refs preserves item JSON, assigned keys, library/item identities, native creator roles, tags and collections. Child notes become imported context; file attachments stay linked at their original locations. Attachment outlines and annotations are accounted for separately and remain in the archived Zotero data. Import never moves those files or updates Zotero objects; a later explicit reorg can bring selected files into the library.

A unique DOI or ISBN match binds compatible incoming metadata to an existing source and keeps its key. Missing fields can be filled; differing values and deliberate clears require review. `import show` presents those differences. Reconciliation previews never write. Its `batch_revision` is an opaque integer token covering the saved batch revision and the observed source revisions; pass it back unchanged for execution.

Existing catalogs upgrade automatically after a [dated safety copy](docs/restore.md#automatic-schema-upgrade), including on read commands and dry runs. Use explicit temporary homes for trials; the real file cutover requires the owner's participation.
