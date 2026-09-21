import json, sys, glob, os, re
pins = {"typer":"0.27.1","pydantic":"2.13.4","bibtexparser":"2.0.1","pylatexenc":"2.10","Unidecode":"1.4.0","uv-build":"0.12.1"}
def key(v):
    return [int(x) if x.isdigit() else x for x in re.split(r'[.\-]', v)]
for f in sorted(glob.glob("pypi/*.json")):
    name = os.path.basename(f)[:-5]
    d = json.load(open(f))
    info = d["info"]; rel = d["releases"]
    def date(v):
        fs = rel.get(v) or []
        return min((x["upload_time"] for x in fs), default="NONE")
    latest = info["version"]
    print(f"== {name}: latest={latest} ({date(latest)}) requires_python={info.get('requires_python')}")
    print("   license:", repr((info.get("license") or "")[:80]), "| license_expression:", info.get("license_expression"))
    print("   classifiers:", [c for c in info["classifiers"] if "Development Status" in c or "License" in c or "3.14" in c])
    print("   yanked latest:", any(x.get("yanked") for x in rel.get(latest, [])))
    # all versions sorted by date, last 8
    vs = sorted(((date(v), v) for v in rel if rel[v]), )
    print("   recent:", [(v, t[:10]) for t, v in vs[-8:]])
    if name in pins:
        p = pins[name]
        print(f"   PIN {p}: exists={p in rel} date={date(p)} files={[ (x['filename'], x.get('requires_python'), x.get('yanked')) for x in rel.get(p, [])][:6]}")
