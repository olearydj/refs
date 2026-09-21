import json, sys, click
@click.group()
def cli(): pass
@cli.command()
@click.argument("key")
@click.option("--json", "as_json", is_flag=True)
def show(key, as_json):
    json.dump({"ok": True, "key": key}, sys.stdout); print()
cli()
