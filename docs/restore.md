# Restore a refs snapshot

A snapshot contains the catalog, configuration and a resource inventory. It contains no linked or managed file bytes. Keep external files separately. Stop writers before restoring, and keep only one mutating home active against shared library and bibliography paths. A restored catalog grants no permission to overwrite an externally changed bibliography.

## Restore into a second home

Use the installed refs Python environment. Choose an empty destination on a local filesystem. The following is the tested procedure, not a new refs command. Save the Python block as `restore_snapshot.py`, then run:

```bash
uv run --locked python restore_snapshot.py "$SNAPSHOT" "$SECOND_HOME"
```

```python restore
import shutil
import sys
import tomllib
from pathlib import Path
from refs import files, recovery
from refs.config import toml_text

snapshot = Path(sys.argv[1]).absolute()
home = Path(sys.argv[2]).absolute()
manifest = recovery.validate_snapshot(snapshot)
if home.is_symlink() or home.exists() and (not home.is_dir() or any(home.iterdir())):
    raise ValueError("Restore destination must be an empty real directory")
configuration = (snapshot / "config.toml").read_bytes()
if files.digest(configuration) != manifest["members"]["config.toml"]["sha256"]:
    raise ValueError("Snapshot configuration changed during restore")
values = tomllib.loads(configuration.decode())
original_base = Path(manifest["configuration_path"]).parent
resources = values.get("resources", {})
for name, path in resources.get("roots", {}).items():
    resources["roots"][name] = str((original_base / Path(path).expanduser()).resolve())
if resources.get("library_root"):
    resources["library_root"] = str((original_base / Path(resources["library_root"]).expanduser()).resolve())
if values.get("export", {}).get("output"):
    values["export"]["output"] = str((original_base / Path(values["export"]["output"]).expanduser()).resolve())
home.mkdir(mode=0o700, parents=True, exist_ok=True)
home.chmod(0o700)
catalog = home / "cat"
catalog.mkdir(mode=0o700)
database = catalog / "catalog.sqlite"
with database.open("xb") as output, (snapshot / "catalog.sqlite").open("rb") as source:
    database.chmod(0o600)
    shutil.copyfileobj(source, output)
if files.hash_file(database) != manifest["members"]["catalog.sqlite"]["sha256"]:
    raise ValueError("Restored database differs from snapshot")
recovery.validate_database(database)
values.setdefault("catalog", {})["path"] = str(catalog)

with (home / "config.toml").open("x") as output:
    (home / "config.toml").chmod(0o600)
    output.write(toml_text(values))
(catalog / "files.lock").touch(mode=0o600, exist_ok=False)
(catalog / "ready").touch(mode=0o600, exist_ok=False)
print("Restored catalog at", catalog)
```

Schema-4 and schema-5 snapshots also preserve loc and the file_operations rows, including unfinished moves. They contain no staged or attachment bytes. Schema-2 snapshots restore all fourteen logical tables, including saved import entries and decisions, collection hierarchy and memberships, and related-source pairs. Older snapshots are validated and restored unchanged; the first command opening a catalog below schema 5 upgrades it after saving a dated safety copy. Migration 005 only updates catalog paths and loc; the owner separately renames the library intake folder to lowercase unfiled once.

Open the restored catalog without launching any resource viewer:

```bash
refs --config "$SECOND_HOME/config.toml" --catalog "$SECOND_HOME/cat" --no-project-config paths
refs --config "$SECOND_HOME/config.toml" --catalog "$SECOND_HOME/cat" --no-project-config list
refs --config "$SECOND_HOME/config.toml" --catalog "$SECOND_HOME/cat" --no-project-config show "$SOURCE_KEY"
refs --config "$SECOND_HOME/config.toml" --catalog "$SECOND_HOME/cat" --no-project-config project show
refs --config "$SECOND_HOME/config.toml" --catalog "$SECOND_HOME/cat" --no-project-config resource check
```

Compare the saved and restored IDs, keys (including removed sources), revisions, corrections, originals, projects, import entries and decisions, Zotero identities, collections, memberships, related pairs, export baselines and resources. The integration test compares every table, including the search projection. Missing external files remain recorded and appear as missing in `resource check`. Remap roots by editing the separate restored configuration if necessary; doing so moves no files.

The ready marker is written last. If validation or copying fails, retain the incomplete destination for inspection and retry into another empty home. Never initialize over it.

## SQLite hot-journal recovery

Stop all refs processes using this catalog. Retain the database and its journal together. Do not delete the journal or initialize another catalog as a substitute for recovery. Save this block as `recover_journal.py`, then run `uv run --locked python recover_journal.py "$CATALOG"` against the selected existing catalog:

```python hot-journal
import sqlite3
import sys
from pathlib import Path
from refs.recovery import validate_database

catalog = Path(sys.argv[1]).resolve()
database = catalog / "catalog.sqlite"
with sqlite3.connect(database.as_uri() + "?mode=rw", uri=True) as connection:
    connection.execute("SELECT count(*) FROM sqlite_master").fetchone()
    if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise ValueError("SQLite integrity check failed")
    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise ValueError("SQLite foreign-key check failed")
validate_database(database)
print("SQLite recovery and integrity checks passed")
```

SQLite performs rollback recovery when the database is opened and read. If recovery fails, preserve the failed database and journal, then restore a verified snapshot into a second home. This is distinct from snapshot restoration and does not authorize changes to external files.

## Automatic schema upgrade

The first refs command that opens an older supported catalog saves `cat/before-schema-<N>-<YYYY-MM-DD>.sqlite` and applies pending migrations under the file lock. This also happens for read commands and dry runs. The notice names the safety copy; JSON carries it as a warning. If the copy cannot be written, refs refuses before migrating. An existing dated copy is never overwritten; inspect and retain it elsewhere before retrying. Newer unsupported schemas still refuse. There is no manual migration step.

Before the real slice 3 cutover, the owner renames the library's Unfiled folder to unfiled once with mv. Migration 005 updates the catalog paths, not disk names. Record the first command's upgrade notice and safety-copy path in the acceptance record.
