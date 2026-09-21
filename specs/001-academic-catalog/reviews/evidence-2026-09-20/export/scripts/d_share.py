"""Share of entries per real .bib that fall outside the v1 export mapping table (counts only)."""
import re, sys, collections
MAPPED = {'article','book','inbook','incollection','inproceedings','conference','thesis','phdthesis','mastersthesis','report','techreport','unpublished','online','software','patent'}
GATED = {'misc'}  # design: "requires type review" / "reviewed fallback" per source
for f in sys.argv[1:]:
    txt = open(f, encoding='utf-8', errors='replace').read()
    types = [t.lower() for t in re.findall(r'^\s*@\s*([A-Za-z]+)\s*[{(]', txt, re.M) if t.lower() not in ('comment','string','preamble')]
    n = len(types); c = collections.Counter(types)
    gated = sum(c[t] for t in GATED); unm = {t: k for t, k in c.items() if t not in MAPPED | GATED}
    # how many @misc look like web pages / software / preprints by field signature (heuristic, counts only)
    blocks = re.split(r'\n(?=\s*@)', txt); sig = collections.Counter()
    for b in blocks:
        if re.match(r'\s*@misc', b, re.I):
            s = 'url-only web/doc' if re.search(r'^\s*(url|howpublished)\s*=', b, re.M|re.I) else 'other'
            if re.search(r'arxiv', b, re.I): s = 'arxiv preprint'
            sig[s] += 1
    print(f"{f}\n   n={n} mapped={n-gated-sum(unm.values())} review-gated @misc={gated} ({gated/n:.0%}) unmapped={unm or 0} -> whole-file export {'BLOCKED' if unm else 'blocked until every @misc individually reviewed' if gated else 'ok'}; misc signatures={dict(sig)}")
