import json, sys, typer
from pydantic import BaseModel
class Env(BaseModel):
    ok: bool; key: str
app = typer.Typer(add_completion=False, rich_markup_mode=None, pretty_exceptions_enable=False)
@app.callback()
def cb(): pass
@app.command()
def show(key: str, as_json: bool = typer.Option(False, "--json")):
    print(Env(ok=True, key=key).model_dump_json())
app()
