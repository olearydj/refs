"""Typer command boundary; application services return ordinary values."""

import sqlite3
import sys
from typing import Annotated

import typer
from typer._click.exceptions import ClickException

from refs import catalog as storage
from refs.config import absolute, select
from refs.results import RefError, emit

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)


@app.callback()
def configure(ctx: typer.Context,
              config: Annotated[str | None, typer.Option()] = None,
              catalog: Annotated[str | None, typer.Option()] = None,
              json_output: Annotated[bool, typer.Option("--json")] = False):
    ctx.obj = dict(config=config, catalog=catalog, json_output=json_output)


def report(ctx: typer.Context, command: str, data: dict) -> None:
    emit(command, data, json_output=ctx.obj["json_output"])


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


def main() -> None:
    args = sys.argv[1:]
    try:
        app(args=args, standalone_mode=False)
    except ClickException as exc:
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
