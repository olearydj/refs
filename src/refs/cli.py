"""Typer command boundary; application services return ordinary values."""

import json
import sqlite3
import sys
from contextlib import redirect_stdout
from contextvars import ContextVar
from pathlib import Path
from typing import Annotated

import typer

from refs import (
    bibliography,
    collections,
    importing,
    kinds,
    projects,
    recovery,
    resources,
    search,
    sources,
)
from refs import catalog as storage
from refs import logging as action_log
from refs.config import absolute, export_options, select
from refs.results import RefError, emit, upgrade_notices

failed_command: ContextVar[str] = ContextVar('refs_failed_command',default='invocation')

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
project_app = typer.Typer(no_args_is_help=True)
app.add_typer(project_app, name="project")


@project_app.callback()
def project_group(ctx: typer.Context):
    record_group(ctx)


@app.callback()
def configure(ctx: typer.Context,
              config: Annotated[str | None, typer.Option()] = None,
              catalog: Annotated[str | None, typer.Option()] = None,
              project_file: Annotated[str | None, typer.Option()] = None,
              no_project_config: Annotated[bool, typer.Option()] = False,
              verbose: Annotated[bool, typer.Option()] = False,
              json_output: Annotated[bool, typer.Option("--json")] = False):
    upgrade_notices.set([])
    failed_command.set(ctx.invoked_subcommand or 'invocation')
    ctx.obj = dict(config=config, catalog=catalog, json_output=json_output, project_file=project_file, no_project_config=no_project_config, verbose=verbose)


def record_group(ctx: typer.Context):
    failed_command.set((ctx.command.name or '') + (' ' + ctx.invoked_subcommand if ctx.invoked_subcommand else ''))


def report(ctx: typer.Context, command: str, data: dict, **text_context) -> None:
    emit(command, {key: value for key, value in data.items() if key != 'warnings'}, json_output=ctx.obj["json_output"], warnings=data.get("warnings", []), text_context=text_context)


def settings(ctx: typer.Context):
    if "selected" not in ctx.obj:
        ctx.obj["selected"] = select(ctx.obj["config"], ctx.obj["catalog"],project_file=ctx.obj["project_file"],no_project_config=ctx.obj["no_project_config"])
        if ctx.obj["selected"].catalog is not None and ctx.obj["selected"].catalog.is_dir():
            action_log.setup(ctx.obj["selected"].catalog, verbose=ctx.obj["verbose"])
    return ctx.obj["selected"]


def read_payload(argument: str | Path) -> tuple[bytes,str]:
    if str(argument)=='-':
        try:
            return sys.stdin.buffer.read(),'stdin'
        except OSError as exc:
            raise RefError('invalid_input',str(exc),2,path='-') from exc
    path=absolute(str(argument))
    try:
        return path.read_bytes(),str(path)
    except OSError as exc:
        raise RefError('invalid_input',str(exc),2,path=str(path)) from exc


def requested(execute: bool, dry_run: bool) -> bool:
    return execute and not dry_run


@app.command()
def paths(ctx: typer.Context):
    report(ctx, "paths", settings(ctx).describe())


@app.command()
def init(ctx: typer.Context, reuse_config: Annotated[bool, typer.Option()] = False, library_root: Annotated[str | None, typer.Option()] = None,
         no_library: Annotated[bool, typer.Option()] = False,
         dry_run: Annotated[bool, typer.Option()] = False):
    """Create a catalog explicitly. Keep its SQLite files outside folders synchronized by a file-copy service."""
    selected = settings(ctx)
    if no_library and library_root is not None:
        raise RefError("invalid_invocation", "Choose --library-root or --no-library", 2)
    library = absolute(library_root) if library_root is not None else None if no_library else selected.library
    report(ctx, "init", storage.init(selected, library, dry_run, reuse_config=reuse_config), catalog_path=str(selected.catalog_path()), library=str(library) if library else None)


@app.command()
def add(ctx: typer.Context, format: Annotated[str, typer.Option()],
        input: Annotated[str, typer.Option()],
        loc: Annotated[str | None, typer.Option()] = None,
        kind: Annotated[str | None, typer.Option()] = None,
        file: Annotated[Path | None, typer.Option()] = None,
        label: Annotated[str | None, typer.Option()] = None,
        link: Annotated[bool, typer.Option()] = False,
        copy: Annotated[bool, typer.Option()] = False,
        move: Annotated[bool, typer.Option()] = False,
        keep_name: Annotated[bool, typer.Option()] = False,
        dry_run: Annotated[bool, typer.Option()] = False):
    if label is not None and file is None:
        raise RefError('invalid_invocation', '--label requires --file', 2)
    mode = resources.intake_mode(path=file, link=link, copy=copy, move=move, keep_name=keep_name, default='move')
    if format not in ("refs", "csljson", "bib"):
        raise RefError("unsupported_format", "Choose --format refs, csljson or bib", 2)
    from refs.models import normalize_loc
    try:
        loc = normalize_loc(loc)
    except ValueError as exc:
        raise RefError("invalid_loc", str(exc), 2) from exc
    raw,locator = read_payload(input)
    if format == 'bib':
        data = importing.add(settings(ctx).catalog_path(), raw, locator, dry_run=dry_run, settings=settings(ctx), loc=loc, kind=kind)
    else:
        data = sources.add(settings(ctx).catalog_path(), raw, locator, format=format, dry_run=dry_run,policy=settings(ctx).values,loc=loc,kind=kind)
    file_action = None
    if file is not None:
        data, file_action = resources.capture_file(settings(ctx),data,file,mode=mode,keep_name=keep_name,label=label,dry_run=dry_run)
    report(ctx, 'add', data | ({'file_action': file_action} if file_action else {}))


import_app = typer.Typer(invoke_without_command=True)
app.add_typer(import_app, name='import')


@import_app.callback()
def import_bibliography(ctx: typer.Context, input: Annotated[Path | None, typer.Option()] = None,
                        format: Annotated[str, typer.Option()] = "bib",
                        origin: Annotated[str | None, typer.Option()] = None,
                        dry_run: Annotated[bool, typer.Option()] = False):
    record_group(ctx)
    if ctx.invoked_subcommand is not None:
        return
    if input is None:
        raise RefError('invalid_invocation', 'Supply --input PATH or an import subcommand', 2)
    path = absolute(str(input))
    if format not in ('bib', 'csljson', 'zotero'):
        raise RefError('unsupported_format', 'Choose --format bib, csljson or zotero for import', 2)
    selected = settings(ctx)
    if format == 'zotero':
        if str(input)=='-' or not path.is_dir():
            raise RefError('invalid_input','Zotero input must be a directory',2,path=str(input))
        data = importing.run_zotero(selected.catalog_path(), path, dry_run=dry_run, origin=origin, settings=selected)
    else:
        raw,locator=read_payload(input)
        runner = importing.run_csl if format == 'csljson' else importing.run
        data = runner(selected.catalog_path(), raw, locator, dry_run=dry_run, origin=origin, settings=selected)
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
def project_cite(ctx: typer.Context, project: str, reference: Annotated[str | None, typer.Argument()] = None,
                 from_import: Annotated[str | None, typer.Option()] = None,
                 dry_run: Annotated[bool, typer.Option()] = False):
    catalog = settings(ctx).catalog_path()
    if from_import is not None and reference is None:
        report(ctx, 'project cite', projects.cite_import(catalog, project, from_import, dry_run=dry_run))
        return
    if reference is not None and from_import is None:
        report(ctx, "project cite", projects.cite(catalog, project, reference, dry_run=dry_run))
        return
    raise RefError('invalid_invocation', 'Supply one source or --from-import ORIGIN', 2)


@app.command("export")
def export_bibliography(ctx: typer.Context, project: Annotated[str | None, typer.Option()] = None,
                       output: Annotated[Path | None, typer.Option()] = None,
                       profile: Annotated[str | None, typer.Option()] = None,
                       allow_unknown_mappings: Annotated[bool, typer.Option()] = False,
                       overwrite: Annotated[bool, typer.Option()] = False,
                       adopt: Annotated[bool, typer.Option()] = False,
                       forget: Annotated[Path | None, typer.Option()] = None,
                       dry_run: Annotated[bool, typer.Option()] = False):
    selected = settings(ctx)
    if forget is not None:
        if project is not None or output is not None or profile is not None or adopt or overwrite or allow_unknown_mappings:
            raise RefError('invalid_invocation', '--forget cannot be combined with export selection or replacement options', 2)
        report(ctx, 'export', bibliography.forget(selected.catalog_path(), forget, dry_run=dry_run))
        return
    project, targets, multiple = export_options(selected, project, output, profile)
    results: list[dict] = []
    for destination, target_profile in targets:
        try:
            data = bibliography.export(selected.catalog_path(), project, destination.expanduser(), dry_run=dry_run, allow_unknown=allow_unknown_mappings, overwrite=overwrite, adopt=adopt, profile=target_profile)
        except (RefError, OSError, sqlite3.Error) as exc:
            if not multiple:
                raise
            if not isinstance(exc, RefError):
                exc = RefError('storage_error', str(exc), 5, path=str(destination))
            results.append(dict(output=str(destination), profile=target_profile, outcome='refused', error=exc.issue, exit_code=exc.exit_code))
        else:
            if not multiple:
                report(ctx, 'export', data)
                return
            results.append(data | dict(outcome='preview' if dry_run else 'current' if data.get('unchanged') else 'written'))
    data = dict(targets=results, warnings=[w for result in results for w in result.get('warnings', [])])
    if any(result['outcome'] == 'refused' for result in results):
        raise RefError('export_partial', 'One or more export targets refused; inspect each target result', 4, data=data)
    report(ctx, 'export', data)


key_app = typer.Typer(no_args_is_help=True)
app.add_typer(key_app, name="key")


@key_app.callback()
def key_group(ctx: typer.Context):
    record_group(ctx)


@app.command("update")
def update_source(ctx: typer.Context, reference: str,
                  if_revision: Annotated[int | None, typer.Option(min=1)] = None,
                  kind: Annotated[str | None, typer.Option()] = None,
                  patch: Annotated[str | None, typer.Option()] = None,
                  set_values: Annotated[list[str] | None, typer.Option("--set")] = None,
                  dry_run: Annotated[bool, typer.Option()] = False):
    if (patch and set_values) or not (patch or set_values or kind):
        raise RefError("invalid_invocation", "Choose --patch or --set", 2)
    try:
        if patch:
            value = json.loads(read_payload(patch)[0])
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
    report(ctx, "update", sources.update(settings(ctx).catalog_path(), reference, value, if_revision, dry_run=dry_run,policy=settings(ctx).values,kind=kind))


@key_app.command("set")
def set_key(ctx: typer.Context, reference: str, key: Annotated[str, typer.Option()],
            if_revision: Annotated[int, typer.Option(min=1)],
            execute: Annotated[bool, typer.Option()] = False,
            dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "key set", sources.rekey(settings(ctx).catalog_path(), reference, if_revision, key, execute=requested(execute, dry_run)))


@app.command()
def remove(ctx: typer.Context, reference: str, if_revision: Annotated[int, typer.Option(min=1)],
           execute: Annotated[bool, typer.Option()] = False,
           dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "remove", sources.set_state(settings(ctx).catalog_path(), reference, if_revision, "removed", execute=requested(execute, dry_run)))


@app.command()
def reactivate(ctx: typer.Context, reference: str, if_revision: Annotated[int | None, typer.Option(min=1)] = None,
               execute: Annotated[bool, typer.Option()] = False,
               dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, "reactivate", sources.set_state(settings(ctx).catalog_path(), reference, if_revision, "active", execute=requested(execute, dry_run)))


@app.command("search")
def search_sources(ctx: typer.Context, query: str, kind: Annotated[str | None, typer.Option()] = None, loc: Annotated[str | None, typer.Option()] = None, collection: Annotated[str | None, typer.Option()] = None, project: Annotated[str | None, typer.Option()] = None,
                   limit: Annotated[int, typer.Option(min=1, max=1000)] = 50,
                   offset: Annotated[int, typer.Option(min=0)] = 0):
    report(ctx, "search", search.retrieve(settings(ctx).catalog_path(), query, loc=loc, collection=collection, project=project or settings(ctx).values.get('project'), limit=limit, offset=offset,policy=settings(ctx).values,kind=kind))


@app.command("list")
def list_sources(ctx: typer.Context, kind: Annotated[str | None, typer.Option()] = None, loc: Annotated[str | None, typer.Option()] = None, collection: Annotated[str | None, typer.Option()] = None, project: Annotated[str | None, typer.Option()] = None,
                 limit: Annotated[int, typer.Option(min=1, max=1000)] = 50,
                 offset: Annotated[int, typer.Option(min=0)] = 0,
                 sort: Annotated[str, typer.Option()] = "title"):
    report(ctx, "list", search.retrieve(settings(ctx).catalog_path(), loc=loc, collection=collection, project=project or settings(ctx).values.get('project'), limit=limit, offset=offset, sort=sort,policy=settings(ctx).values,kind=kind))


@app.command('kinds')
def list_kinds(ctx: typer.Context):
    report(ctx, 'kinds', {'items': [dict(row, announce=row.get('announce', True)) for row in kinds.REGISTRY['kinds']]})


@app.command('summary')
def catalog_summary(ctx: typer.Context):
    from refs import summary
    report(ctx, 'summary', summary.overview(settings(ctx)))


@app.command("schema")
def inspect_schema(ctx: typer.Context, name: Annotated[str | None, typer.Argument()] = None):
    from refs.models import schema
    report(ctx, "schema", schema(name) if name else {"schemas": ["source-create", "source-patch", "source-record", "result"]})


@project_app.command("show")
def project_show(ctx: typer.Context, project: Annotated[str | None, typer.Argument()] = None):
    report(ctx, "project show", projects.show(settings(ctx).catalog_path(), project))


@project_app.command("uncite")
def project_uncite(ctx: typer.Context, project: str, reference: str,
                   dry_run: Annotated[bool, typer.Option()] = False):
    catalog = settings(ctx).catalog_path()
    data = projects.uncite(catalog, project, reference, dry_run=dry_run)
    report(ctx, "project uncite", data)


resource_app = typer.Typer(no_args_is_help=True)
app.add_typer(resource_app, name='resource')


@resource_app.callback()
def resource_group(ctx: typer.Context):
    record_group(ctx)


@resource_app.command('add')
def resource_add(ctx: typer.Context, reference: str,
                 path: Annotated[Path | None, typer.Option()] = None,
                 root: Annotated[str | None, typer.Option()] = None,
                 relative: Annotated[str | None, typer.Option()] = None,
                 label: Annotated[str | None, typer.Option()] = None,
                 media_type: Annotated[str | None, typer.Option()] = None,
                 copy: Annotated[bool, typer.Option()] = False,
                 move: Annotated[bool, typer.Option()] = False,
                 link: Annotated[bool, typer.Option()] = False,
                 keep_name: Annotated[bool, typer.Option()] = False,
                 dry_run: Annotated[bool, typer.Option()] = False):
    selected = settings(ctx)
    mode = resources.intake_mode(path=path if path is not None else Path(relative) if root and relative else None, link=link, copy=copy, move=move, keep_name=keep_name)
    if mode in ('copy', 'move'):
        resources.locate(selected,path=path,root=root,relative=relative)
        original = path if path is not None else selected.roots[root]/relative
        from refs.moves import intake
        action = intake if mode == 'move' else resources.copy
        data = action(selected,reference,original,keep_name=keep_name,dry_run=dry_run,label=label,media_type=media_type)
    else:
        data = resources.link(selected,reference,path=path,root=root,relative=relative,label=label,media_type=media_type,dry_run=dry_run)
    report(ctx, 'resource add', data)


@resource_app.command('unlink')
def resource_unlink(ctx: typer.Context, resource: str,
                    execute: Annotated[bool, typer.Option()] = False,
                    dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx, 'resource unlink', resources.unlink(settings(ctx),resource,execute=requested(execute, dry_run)))


@app.command()
def reorg(ctx: typer.Context,
          source: Annotated[str | None, typer.Option()] = None,
          loc: Annotated[str | None, typer.Option()] = None,
          execute: Annotated[bool, typer.Option()] = False):
    from refs import moves
    report(ctx, 'reorg', moves.reorg(settings(ctx),reference=source,loc=loc,execute=execute))


@resource_app.command('check')
def resource_check(ctx: typer.Context, source: Annotated[str | None, typer.Option()] = None,
                   verify: Annotated[bool, typer.Option()] = False,
                   kind: Annotated[str | None, typer.Option()] = None):
    report(ctx, 'resource check', resources.check(settings(ctx),source,verify=verify,kind=kind))


@app.command('open')
def open_resource(ctx: typer.Context, reference: str,
                  resource: Annotated[str | None, typer.Option()] = None):
    """Launch the selected file in its default application. Never modifies the file."""
    report(ctx,'open',resources.open_source(settings(ctx),reference,resource_id=resource))


@app.command('backup')
def backup_catalog(ctx: typer.Context, output: Annotated[Path, typer.Option()],
                   dry_run: Annotated[bool, typer.Option()] = False):
    report(ctx,'backup',recovery.backup(settings(ctx),output,dry_run=dry_run))


config_app = typer.Typer(no_args_is_help=True)
app.add_typer(config_app,name='config')


@config_app.callback()
def config_group(ctx: typer.Context):
    record_group(ctx)


@config_app.command('show')
def config_show(ctx: typer.Context):
    report(ctx,'config show',settings(ctx).inspect())


def main() -> None:
    from refs import moves

    moves.interrupted_report.set(None)
    failed_command.set('invocation')
    args = sys.argv[1:]
    action_log.bind(" ".join(args))
    def option(name):
        return next((args[index + 1] for index, value in enumerate(args[:-1]) if value == name),
                    next((value.split("=", 1)[1] for value in args if value.startswith(name + "=")), None))
    catalog = None
    try:
        selected = select(option("--config"), option("--catalog"), project_file=option("--project-file"), no_project_config="--no-project-config" in args)
        catalog = selected.catalog
        if catalog is not None and catalog.is_dir():
            action_log.setup(catalog, verbose="--verbose" in args)
            action_log.event("command.open", argv=args)
        elif catalog is not None:
            def opening():
                action_log.setup(catalog, verbose="--verbose" in args)
                action_log.event("command.open", argv=args)
            action_log.defer_open(opening)
    except (RefError, OSError):
        pass  # Let Typer report selection errors through the usual envelope.
    exit_code = 0
    try:
        index=0
        while index<len(args) and args[index].startswith('--'):
            index+=2 if args[index] in ('--config','--catalog','--project-file') else 1
        bare_group=index==len(args) or index==len(args)-1 and args[index] in {'project','key','resource','config','collection'}
        if bare_group:
            failed_command.set(args[index] if index<len(args) else 'invocation')
            with redirect_stdout(sys.stderr):
                app(args=[*args,'--help'],standalone_mode=False)
            raise RefError('invalid_invocation','Choose a command',2)
        returned = app(args=args, standalone_mode=False)
        if returned == 130 and (data := moves.interrupted_report.get()) is not None:
            interrupt = KeyboardInterrupt('Move interrupted')
            setattr(interrupt,'data',data)
            raise interrupt
    except typer.TyperException as exc:
        exit_code = 2
        emit(failed_command.get(), error=RefError("invalid_invocation", exc.format_message(), 2),
             json_output="--json" in args)
        raise SystemExit(2) from None
    except RefError as exc:
        exit_code = exc.exit_code
        emit(failed_command.get(), error=exc, json_output="--json" in args)
        raise SystemExit(exc.exit_code) from None
    except (OSError, sqlite3.Error) as exc:
        locked = isinstance(exc, sqlite3.OperationalError) and getattr(exc,'sqlite_errorcode',None) in (sqlite3.SQLITE_BUSY,sqlite3.SQLITE_LOCKED)
        denied = isinstance(exc, PermissionError)
        error = RefError("home_not_writable" if denied else "lock_timeout" if locked else "storage_error", "Allow access to the selected path and retry" if denied else str(exc),
                         6 if locked else 5, retryable=locked, path=str(exc.filename) if denied and exc.filename else None)
        exit_code = error.exit_code
        emit(failed_command.get(), error=error, json_output="--json" in args)
        raise SystemExit(error.exit_code) from None
    except Exception:
        exit_code = 5
        emit(failed_command.get(),error=RefError('internal_error','Unexpected internal error',5),json_output='--json' in args)
        raise SystemExit(5) from None
    except KeyboardInterrupt as exc:
        exit_code = 130
        if data := getattr(exc, 'data', None):
            emit('reorg', error=RefError('move_interrupted',str(exc) or 'Move interrupted',4,data=data),
                 json_output='--json' in args)
        raise SystemExit(130) from None
    finally:
        moves.interrupted_report.set(None)
        if catalog is not None and catalog.is_dir():
            action_log.setup(catalog, verbose="--verbose" in args)
            action_log.event("command.close", exit_code=exit_code, outcome="ok" if exit_code == 0 else "error")


@import_app.command('list')
def import_list(ctx: typer.Context):
    report(ctx,'import list',importing.list_batches(settings(ctx).catalog_path()))


@import_app.command('show')
def import_show(ctx: typer.Context, batch: str, status: Annotated[str | None, typer.Option()] = None):
    report(ctx,'import show',importing.show(settings(ctx).catalog_path(),batch,status))


@import_app.command('reconcile')
def import_reconcile(ctx: typer.Context, batch: str,
                     take_incoming: Annotated[list[str] | None, typer.Option()] = None,
                     keep_current: Annotated[list[str] | None, typer.Option()] = None,
                     dismiss: Annotated[list[str] | None, typer.Option()] = None,
                     execute: Annotated[bool, typer.Option()] = False,
                     if_batch_revision: Annotated[int | None, typer.Option()] = None):
    report(ctx,'import reconcile',importing.reconcile(settings(ctx).catalog_path(),batch,take_incoming or [],keep_current=keep_current,dismiss=dismiss,execute=execute,revision=if_batch_revision))


collection_app = typer.Typer(no_args_is_help=True)
app.add_typer(collection_app,name='collection')


@collection_app.callback()
def collection_group(ctx: typer.Context):
    record_group(ctx)


@collection_app.command('list')
def collection_list(ctx: typer.Context):
    report(ctx,'collection list',collections.list_collections(settings(ctx).catalog_path()))
