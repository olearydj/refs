"""Aggregate heuristic: are stored titles Title Case or sentence case? Prints counts only."""
import re, sys, collections
MINOR = set("a an the and but or nor for so yet as at by in of on per to up via with from into is are vs".split())
for f in sys.argv[1:]:
    txt = open(f, encoding='utf-8', errors='replace').read()
    c = collections.Counter(); lang = collections.Counter()
    for m in re.finditer(r'^\s*title\s*=\s*[{"](.*?)[}"],?\s*$', txt, re.M | re.I):
        t = re.sub(r'[{}]', '', m.group(1))
        words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", t)][1:]
        major = [w for w in words if w.lower() not in MINOR and len(w) > 3]
        if len(major) < 3: c['too_short'] += 1; continue
        frac = sum(1 for w in major if w[0].isupper()) / len(major)
        c['title_case' if frac >= 0.8 else 'sentence_case' if frac <= 0.34 else 'mixed'] += 1
    for m in re.finditer(r'^\s*langid\s*=\s*[{"](.*?)[}"]', txt, re.M | re.I): lang[m.group(1).lower()] += 1
    print(f, dict(c), 'langid:', dict(lang))
