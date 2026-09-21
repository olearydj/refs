import json, sys, typer
from typing import Annotated
from pydantic import BaseModel, ValidationError
class ShowRequest(BaseModel):
    model_config = {"extra": "forbid", "strict": True}
    key: str
    fields: list[str] = []
class Envelope(BaseModel):
    schema_version: str = "refs.cli.v1"
    ok: bool
    result: dict | None = None
    error: dict | None = None
app = typer.Typer(add_completion=False, rich_markup_mode=None, pretty_exceptions_enable=False, no_args_is_help=False)
@app.callback()
def cb(): pass
@app.command()
def show(input: Annotated[str, typer.Option("--input", help="'-' for stdin JSON")] = "-"):
    "Show one record."
    try:
        req = ShowRequest.model_validate_json(sys.stdin.read())
    except ValidationError as e:
        print(Envelope(ok=False, error={"code": "invalid_request", "details": json.loads(e.json(include_url=False))}).model_dump_json()); raise typer.Exit(3)
    print(Envelope(ok=True, result={"key": req.key}).model_dump_json())
@app.command()
def boom():
    raise RuntimeError("unexpected")
@app.command()
def schema():
    print(json.dumps({"request": ShowRequest.model_json_schema(), "envelope": Envelope.model_json_schema()}))
@app.command()
def describe():
    cmd = typer.main.get_command(app)
    ctx = typer.Context(cmd) if False else None
    import typer._click as click
    with click.Context(cmd) as c:
        print(json.dumps(cmd.to_info_dict(c), default=str))
if __name__ == "__main__":
    app()
