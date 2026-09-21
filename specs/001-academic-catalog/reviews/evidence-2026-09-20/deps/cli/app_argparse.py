import argparse, json, sys
def main():
    p = argparse.ArgumentParser(prog="refs"); sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show"); s.add_argument("key"); s.add_argument("--json", action="store_true")
    a = p.parse_args(); json.dump({"ok": True, "key": a.key}, sys.stdout); print()
main()
