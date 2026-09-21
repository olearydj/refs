import json, sys, typer
import typer.exceptions as te
print("typer.exceptions public names:", [n for n in dir(te) if not n.startswith("_")], file=sys.stderr)
print("typer top-level exc names:", [n for n in dir(typer) if "Err" in n or "Exit" in n or "Abort" in n or "Exception" in n], file=sys.stderr)
app = typer.Typer(add_completion=False, rich_markup_mode=None, pretty_exceptions_enable=False)
@app.callback()
def cb(): pass
@app.command()
def show(key: str): print(json.dumps({"ok": True, "key": key}))
try:
    rv = app(standalone_mode=False)
    sys.exit(0 if rv is None else rv)
except Exception as e:
    print(json.dumps({"ok": False, "error": {"code": "usage", "type": f"{type(e).__module__}.{type(e).__name__}", "message": getattr(e, "message", str(e)), "exit_code": getattr(e, "exit_code", None)}}))
    sys.exit(2)
