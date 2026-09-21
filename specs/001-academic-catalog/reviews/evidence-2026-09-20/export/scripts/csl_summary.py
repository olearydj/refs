"""Compact one-line-per-entry summary of pandoc CSL JSON. usage: csl_summary.py file.json [drop,keys]"""
import json, sys
drop = set((sys.argv[2] if len(sys.argv) > 2 else '').split(','))
def name(n):
    if 'literal' in n: return 'LIT<' + n['literal'] + '>'
    parts = [f"{k[:3]}={n[k]}" for k in ('family','given','dropping-particle','non-dropping-particle','suffix') if k in n]
    return '{' + ' '.join(parts) + '}'
def date(d):
    out = []
    if 'date-parts' in d: out.append('/'.join('-'.join(str(x) for x in p) for p in d['date-parts']))
    for k in ('season','circa','literal','raw'):
        if k in d: out.append(f"{k}={d[k]}")
    return ' '.join(out)
for e in json.load(open(sys.argv[1])):
    bits = []
    for k, v in e.items():
        if k in ('id','type') or k in drop: continue
        if isinstance(v, list): v = '; '.join(name(n) for n in v)
        elif isinstance(v, dict): v = date(v)
        bits.append(f"{k}={v}")
    print(f"[{e['id']}] type={e['type']}\n     " + ' | '.join(bits))
