import sys, warnings, logging, bibtexparser
from bibtexparser import model
import bibtexparser.middlewares as m
src = open(sys.argv[1], encoding="utf-8").read()
def show(lib, keys=None):
    for b in lib.blocks:
        if isinstance(b, model.Entry):
            print("ENTRY", b.entry_type, b.key, "line", b.start_line)
            for f in b.fields:
                if keys and f.key not in keys: continue
                print("   %s = %r" % (f.key, f.value))
        else:
            print(type(b).__name__, getattr(b, "error", ""), repr(b.raw[:80]))
print("##### default stack"); lib = bibtexparser.parse_string(src); show(lib)
# raw exactness
for e in lib.entries:
    print("raw is exact substring of source:", e.key, e.raw in src)
print("##### + LatexDecodingMiddleware")
lib = bibtexparser.parse_string(src, append_middleware=[m.LatexDecodingMiddleware()]); show(lib, {"author","title","journal","url","doi","file","note","editor"})
print("##### + SeparateCoAuthors + SplitNameParts (no latex decode)")
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    try:
        lib = bibtexparser.parse_string(src, append_middleware=[m.SeparateCoAuthors(), m.SplitNameParts()])
        for e in lib.entries:
            for k in ("author","editor"):
                if k in e.fields_dict:
                    print(e.key, k)
                    for n in e[k]:
                        print("    ", n if not isinstance(n, m.NameParts) else dict(first=n.first, von=n.von, last=n.last, jr=n.jr))
        for b in lib.failed_blocks: print("FAILED", type(b).__name__, b.error, repr(b.raw[:60]))
    except Exception as ex:
        import traceback; traceback.print_exc()
print("warnings:", [str(x.message)[:300] for x in w])
print("##### + MonthIntMiddleware / NormalizeFieldKeys on syntax fixture")
s2 = open("fx/syntax.bib").read()
lib = bibtexparser.parse_string(s2, append_middleware=[m.NormalizeFieldKeys(), m.MonthIntMiddleware()])
for e in lib.entries:
    if e.key in ("macro1","CaseKey"):
        print(e.key, [(f.key, f.value) for f in e.fields])
for b in lib.failed_blocks: print("FAILED", type(b).__name__, str(b.error)[:150], "line", b.start_line)
