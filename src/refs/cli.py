"""Typer command boundary; application services return ordinary values."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Annotated

import typer

from refs import bibliography, projects, search, sources
from refs import catalog as storage
from refs.config import absolute, select
from refs.results import RefError, emit

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
project_app = typer.Typer(no_args_is_help=True)
app.add_typer(project_app, name="project")


@app.callback()
def configure(ctx: typer.Context,
              config: Annotated[str | None, typer.Option()] = None,
              catalog: Annotated[str | None, typer.Option()] = None,
              json_output: Annotated[bool, typer.Option("--json")] = False):
    ctx.obj = dict(config=config, catalog=catalog, json_output=json_output)


def report(ctx: typer.Context, command: str, data: dict) -> None:
    emit(command, data, json_output=ctx.obj["json_output"], warnings=data.get("warnings", []))


def settings(ctx: typer.Context):
    return select(ctx.obj["config"], ctx.obj["catalog"])


@app.command()
def paths(ctx: typer.Context):
    report(ctx, "paths", settings(ctx).describe())


@app.command()
def init(ctx: typer.Context, library_root: Annotated[str | None, typer.Option()] = None,
         no_library: Annotated[bool, typer.Option()] = False,
         dry_run: Annotated[bool, typer.Option()] = False):
    selected = settings(ctx)
    if no_library and library_root is not None:
        raise RefError("invalid_invocation", "Choose --library-root or --no-library", 2)
    library = absolute(library_root) if library_root is not None else None if no_library else selected.library
    report(ctx, "init", storage.init(selected, library, dry_run))


@app.command()
def add(ctx: typer.Context, format: Annotated[str, typer.Option()],
        input: Annotated[str, typer.Option()],
        dry_run: Annotated[bool, typer.Option()] = False):
    if format not in ("refs", "csljson"):
        raise RefError("unsupported_format", "Choose --format refs or csljson", 2)
    raw = sys.stdin.buffer.read() if input == "-" else Path(input).read_bytes()
    locator = "stdin" if input == "-" else str(absolute(input))
    report(ctx, "add", sources.add(settings(ctx).catalog_path(), raw, locator, format=format, dry_run=dry_run))


@app.command()
def show(ctx: typer.Context, reference: str):
    report(ctx, "show", sources.show(settings(ctx).catalog_path(), reference))


@project_app.command("create")
def project_create(ctx: typer.Context, name: str,
                   description: Annotated[str, typer.Option()] = "",
                   dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "project create", projects.create(settings(ctx).catalog_path(), name, description, dry_run=dry_run))


@project_app.command("cite")
def project_cite(ctx: typer.Context, project: str, reference: str,
                 dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "project cite", projects.cite(settings(ctx).catalog_path(), project, reference, dry_run=dry_run))


@app.command("export")
def export_bibliography(ctx: typer.Context, project: Annotated[str, typer.Option()],
                       output: Annotated[Path, typer.Option()],
                       profile: Annotated[str, typer.Option()] = bibliography.PROFILE,
                       allow_unknown_mappings: Annotated[bool, typer.Option()] = False,
                       dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "export", bibliography.export(settings(ctx).catalog_path(), project, output.expanduser(), profile=profile, dry_run=dry_run, allow_unknown=allow_unknown_mappings))


key_app = typer.Typer(no_args_is_help=True)
app.add_typer(key_app, name="key")


@app.command("update")
def update_source(ctx: typer.Context, reference: str,
                  if_revision: Annotated[int, typer.Option(min=1)],
                  patch: Annotated[str | None, typer.Option()] = None,
                  set_values: Annotated[list[str] | None, typer.Option("--set")] = None,
                  dry_run: Annotated[bool, typer.Option()] = False):
    if bool(patch) == bool(set_values):
        raise RefError("invalid_invocation", "Choose --patch or --set", 2)
    try:
        if patch:
            value = json.loads(sys.stdin.read() if patch == "-" else Path(patch).read_text())
        else:
            values = {}
            for item in set_values or []:
                name, raw = item.split("=", 1)
                if name in values:
                    raise ValueError("Repeated patch path")
                values[name] = json.loads(raw)
            value = {"schema_version": "1.0", "set": values}
    except (ValueError, UnicodeError) as exc:
        raise RefError("invalid_patch", str(exc), 2) from exc
    report(ctx, "update", sources.update(settings(ctx).catalog_path(), reference, value, if_revision, dry_run=dry_run))


@key_app.command("set")
def set_key(ctx: typer.Context, reference: str, key: Annotated[str, typer.Option()],
            if_revision: Annotated[int, typer.Option(min=1)],
            execute: Annotated[bool, typer.Option()] = False,
            dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "key set", sources.change_identity(settings(ctx).catalog_path(), reference, if_revision, new_key=key, execute=execute and not dry_run))


@app.command()
def remove(ctx: typer.Context, reference: str, if_revision: Annotated[int, typer.Option(min=1)],
           execute: Annotated[bool, typer.Option()] = False,
           dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "remove", sources.change_identity(settings(ctx).catalog_path(), reference, if_revision, state="removed", execute=execute and not dry_run))


@app.command()
def reactivate(ctx: typer.Context, reference: str, if_revision: Annotated[int, typer.Option(min=1)],
               execute: Annotated[bool, typer.Option()] = False,
               dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "reactivate", sources.change_identity(settings(ctx).catalog_path(), reference, if_revision, state="active", execute=execute and not dry_run))


@app.command("search")
def search_sources(ctx: typer.Context, query: str, project: Annotated[str | None, typer.Option()] = None,
                   limit: Annotated[int, typer.Option(min=1, max=1000)] = 50,
                   offset: Annotated[int, typer.Option(min=0)] = 0):
    report(ctx, "search", search.retrieve(settings(ctx).catalog_path(), query, project=project, limit=limit, offset=offset))


@app.command("list")
def list_sources(ctx: typer.Context, project: Annotated[str | None, typer.Option()] = None,
                 limit: Annotated[int, typer.Option(min=1, max=1000)] = 50,
                 offset: Annotated[int, typer.Option(min=0)] = 0,
                 sort: Annotated[str, typer.Option()] = "title"):
    report(ctx, "list", search.retrieve(settings(ctx).catalog_path(), project=project, limit=limit, offset=offset, sort=sort))


@app.command("schema")
def inspect_schema(ctx: typer.Context, name: str):
    from refs.models import schema
    report(ctx, "schema", schema(name))


def main() -> None:
    args = sys.argv[1:]
    try:
        app(args=args, standalone_mode=False)
    except typer.TyperException as exc:
        emit("invocation", error=RefError("invalid_invocation", exc.format_message(), 2),
             json_output="--json" in args)
        raise SystemExit(2) from None
    except RefError as exc:
        emit("invocation", error=exc, json_output="--json" in args)
        raise SystemExit(exc.exit_code) from None
    except (OSError, sqlite3.Error) as exc:
        locked = isinstance(exc, sqlite3.OperationalError) and "locked" in str(exc)
        error = RefError("lock_timeout" if locked else "storage_error", str(exc),
                         6 if locked else 5, retryable=locked)
        emit("invocation", error=error, json_output="--json" in args)
        raise SystemExit(error.exit_code) from None
    except KeyboardInterrupt:
        raise SystemExit(130) from None
