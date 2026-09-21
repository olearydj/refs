import sys, difflib, bibtexparser
from bibtexparser import model
import bibtexparser.middlewares as m
src = '''@misc{n,
  author = {van der Berg, Johannes and de la Fontaine, Jr., Jean and King, Jr, Martin Luther and {World Health Organization} and {Barnes and Noble, Inc.} and Ludwig van Beethoven and Charles Louis Xavier Joseph de la Vall{\\'e}e Poussin and Jean-Paul Sartre and others},
}'''
lib = bibtexparser.parse_string(src, append_middleware=[m.SeparateCoAuthors(), m.SplitNameParts()])
for b in lib.blocks:
    if isinstance(b, model.Entry):
        for n in b["author"]:
            print("  ", dict(first=n.first, von=n.von, last=n.last, jr=n.jr))
    else: print(type(b).__name__, b.error)
print("##### ROUND TRIP")
for fn in ["fx/syntax.bib","fx/content.bib","fx/biblatex.bib"]:
    s = open(fn).read()
    lib = bibtexparser.parse_string(s)
    out = bibtexparser.write_string(lib)
    print("=====", fn, "identical:", out == s, "len in/out", len(s), len(out))
    open("out/roundtrip_"+fn.split("/")[1], "w").write(out)
    d = list(difflib.unified_diff(s.splitlines(), out.splitlines(), lineterm="", n=0))
    print("\n".join(d[:400]))
