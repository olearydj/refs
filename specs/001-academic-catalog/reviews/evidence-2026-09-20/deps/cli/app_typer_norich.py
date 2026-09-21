import json, sys, typer
app = typer.Typer(add_completion=False, rich_markup_mode=None, pretty_exceptions_enable=False)
@app.callback()
def cb(): pass
@app.command()
def show(key: str, as_json: bool = typer.Option(False, "--json")):
    json.dump({"ok": True, "key": key}, sys.stdout); print()
app()
