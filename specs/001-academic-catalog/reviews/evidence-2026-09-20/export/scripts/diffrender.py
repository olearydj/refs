"""Differential render check prototype: per key, per style, compare the citeproc rendering of the
internal CSL projection (r.json) with the rendering of the emitted .bib as pandoc re-reads it."""
import re, sys, collections
txt = open(sys.argv[1]).read(); style = None; key = None; rows = collections.defaultdict(dict)
for line in txt.splitlines():
    if line.startswith('####'): style = line.strip('# ').strip()
    elif line.startswith('== '): key = line[3:].strip()
    elif line.startswith('  '):
        route, _, out = line.strip().partition(' '); rows[(key, style)][route] = out.strip()
norm = lambda s: re.sub(r'\s+', ' ', s).strip()
fold = lambda s: norm(s).casefold()
tot = collections.Counter()
for (key, style), r in rows.items():
    a, b = r.get('json', ''), r.get('bib', '')
    verdict = 'IDENTICAL' if norm(a) == norm(b) else 'CASE-ONLY' if fold(a) == fold(b) else 'CONTENT-DIFF'
    tot[(style, verdict)] += 1
    if verdict != 'IDENTICAL': print(f"{verdict:12s} {style[:7]:7s} {key}")
print(dict(tot))
