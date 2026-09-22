"""Typer command boundary; application services return ordinary values."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Annotated

import typer

from refs import bibliography, importing, projects, recovery, resources, search, sources
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


def report(ctx: typer.Context, command: str, data: dict, **text_context) -> None:
    emit(command, data, json_output=ctx.obj["json_output"], warnings=data.get("warnings", []), text_context=text_context)


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
    report(ctx, "init", storage.init(selected, library, dry_run), catalog_path=str(selected.catalog_path()), library=str(library) if library else None)


@app.command()
def add(ctx: typer.Context, format: Annotated[str, typer.Option()],
        input: Annotated[str, typer.Option()],
        file: Annotated[Path | None, typer.Option()] = None,
        link: Annotated[bool, typer.Option()] = False,
        keep_name: Annotated[bool, typer.Option()] = False,
        dry_run: Annotated[bool, typer.Option()] = False):
    if (link or keep_name) and file is None or link and keep_name:
        raise RefError('invalid_invocation', 'Use --link or --keep-name with --file, never both', 2)
    if format not in ("refs", "csljson", "bib"):
        raise RefError("unsupported_format", "Choose --format refs, csljson or bib", 2)
    raw = sys.stdin.buffer.read() if input == "-" else Path(input).read_bytes()
    locator = "stdin" if input == "-" else str(absolute(input))
    if format == 'bib':
        data = importing.add(settings(ctx).catalog_path(), raw, locator, dry_run=dry_run, settings=settings(ctx))
    else:
        data = sources.add(settings(ctx).catalog_path(), raw, locator, format=format, dry_run=dry_run)
    if file is not None:
        data = resources.capture_file(settings(ctx),data,file,linked=link,keep_name=keep_name,dry_run=dry_run)
    report(ctx, 'add', data)


@app.command('import')
def import_bibliography(ctx: typer.Context, input: Annotated[Path, typer.Option()],
                        format: Annotated[str, typer.Option()] = "bib",
                        origin: Annotated[str | None, typer.Option()] = None,
                        dry_run: Annotated[bool, typer.Option()] = False):
    path = absolute(str(input))
    if format != 'bib':
        raise RefError('unsupported_format', 'Choose --format bib for import', 2)
    data = importing.run(settings(ctx).catalog_path(), path.read_bytes(), str(path), dry_run=dry_run, origin=origin, settings=settings(ctx))
    if data['counts']['conflict'] or data['counts']['invalid']:
        raise RefError('import_partial', 'Inspect reported entries and use update to settle conflicts', 4, data=data)
    report(ctx, 'import', data)


@app.command()
def show(ctx: typer.Context, reference: str):
    report(ctx, "show", resources.inspect_source(settings(ctx), reference))


@project_app.command("create")
def project_create(ctx: typer.Context, name: str,
                   description: Annotated[str, typer.Option()] = "",
                   dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "project create", projects.create(settings(ctx).catalog_path(), name, description, dry_run=dry_run))


@project_app.command("cite")
def project_cite(ctx: typer.Context, project: str, reference: str,
                 dry_run: Annotated[bool, typer.Option()] = False):
    catalog = settings(ctx).catalog_path()
    data = projects.cite(catalog, project, reference, dry_run=dry_run)
    report(ctx, "project cite", data, citation_key=sources.show(catalog, data['source_id'])['citation_key'], project_name=projects.show(catalog, data['project_id'])['name'])


@app.command("export")
def export_bibliography(ctx: typer.Context, project: Annotated[str, typer.Option()],
                       output: Annotated[Path, typer.Option()],
                       profile: Annotated[str, typer.Option()] = bibliography.PROFILE,
                       allow_unknown_mappings: Annotated[bool, typer.Option()] = False,
                       overwrite: Annotated[bool, typer.Option()] = False,
                       adopt: Annotated[bool, typer.Option()] = False,
                       dry_run: Annotated[bool, typer.Option()] = False):
    try:
        data = bibliography.export(settings(ctx).catalog_path(), project, output.expanduser(), profile=profile, dry_run=dry_run, allow_unknown=allow_unknown_mappings, overwrite=overwrite, adopt=adopt)
    except RefError as exc:
        if exc.issue['code'] == 'export_blocked' and not ctx.obj['json_output']:
            exc.issue['path'] = str(absolute(str(output)))
        raise
    report(ctx, 'export', data)


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
    previous_key = sources.show(settings(ctx).catalog_path(), reference)["citation_key"]
    report(ctx, "key set", sources.change_identity(settings(ctx).catalog_path(), reference, if_revision, new_key=key, execute=execute and not dry_run), previous_key=previous_key)


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


@project_app.command("show")
def project_show(ctx: typer.Context, project: Annotated[str | None, typer.Argument()] = None):
    report(ctx, "project show", projects.show(settings(ctx).catalog_path(), project))


@project_app.command("uncite")
def project_uncite(ctx: typer.Context, project: str, reference: str,
                   dry_run: Annotated[bool, typer.Option()] = False):
    catalog = settings(ctx).catalog_path()
    data = projects.uncite(catalog, project, reference, dry_run=dry_run)
    report(ctx, "project uncite", data, citation_key=sources.show(catalog, data['source_id'])['citation_key'], project_name=projects.show(catalog, data['project_id'])['name'])


resource_app = typer.Typer(no_args_is_help=True)
app.add_typer(resource_app, name='resource')


@resource_app.command('add')
def resource_add(ctx: typer.Context, reference: str,
                 path: Annotated[Path | None, typer.Option()] = None,
                 root: Annotated[str | None, typer.Option()] = None,
                 relative: Annotated[str | None, typer.Option()] = None,
                 label: Annotated[str | None, typer.Option()] = None,
                 media_type: Annotated[str | None, typer.Option()] = None,
                 copy: Annotated[bool, typer.Option()] = False,
                 keep_name: Annotated[bool, typer.Option()] = False,
                 dry_run: Annotated[bool, typer.Option()] = False):
    selected = settings(ctx)
    if keep_name and not copy:
        raise RefError('invalid_invocation','Use --keep-name only with --copy',2)
    if copy:
        resources.locate(selected,path=path,root=root,relative=relative)
        original = path if path is not None else selected.roots[root]/relative
        data = resources.copy(selected,reference,original,keep_name=keep_name,dry_run=dry_run,label=label,media_type=media_type)
    else:
        data = resources.link(selected,reference,path=path,root=root,relative=relative,label=label,media_type=media_type,dry_run=dry_run)
    report(ctx, 'resource add', data)


@resource_app.command('unlink')
def resource_unlink(ctx: typer.Context, resource: str,
                    if_revision: Annotated[int, typer.Option(min=1)],
                    execute: Annotated[bool, typer.Option()] = False,
                    dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, 'resource unlink', resources.unlink(settings(ctx),resource,if_revision,execute=execute and not dry_run))


@resource_app.command('check')
def resource_check(ctx: typer.Context, source: Annotated[str | None, typer.Option()] = None,
                   verify: Annotated[bool, typer.Option()] = False):
    report(ctx, 'resource check', resources.check(settings(ctx),source,verify=verify))


@app.command('open')
def open_resource(ctx: typer.Context, reference: str,
                  resource: Annotated[str | None, typer.Option()] = None):
    report(ctx,'open',resources.open_source(settings(ctx),reference,resource_id=resource))


@app.command('backup')
def backup_catalog(ctx: typer.Context, output: Annotated[Path, typer.Option()],
                   dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx,'backup',recovery.backup(settings(ctx),output,dry_run=dry_run))


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
