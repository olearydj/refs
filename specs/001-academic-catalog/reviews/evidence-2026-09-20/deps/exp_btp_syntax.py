import sys, warnings, bibtexparser
from bibtexparser import model
src = open(sys.argv[1], encoding="utf-8").read()
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    lib = bibtexparser.parse_string(src)
print("WARNINGS:", [str(x.message)[:200] for x in w])
print("n blocks", len(lib.blocks), "entries", len(lib.entries), "failed", len(lib.failed_blocks), "strings", len(lib.strings), "preambles", len(lib.preambles), "comments", len(lib.comments))
for b in lib.blocks:
    t = type(b).__name__
    print(f"--- {t} start_line={b.start_line} raw_len={len(b.raw) if b.raw is not None else None}")
    if isinstance(b, model.Entry):
        print("   type=%r key=%r" % (b.entry_type, b.key))
        for f in b.fields:
            print("   field %r line=%s enclosing=%r value=%r" % (f.key, f.start_line, f.enclosing, f.value))
        print("   meta:", b.parser_metadata)
    elif isinstance(b, model.ParsingFailedBlock):
        print("   error:", type(b.error).__name__, str(b.error)[:200])
        print("   raw:", repr(b.raw[:200]))
        ig = getattr(b, "ignore_error_block", None)
        if ig is not None: print("   ignore_error_block:", repr(ig)[:300])
    elif isinstance(b, model.String):
        print("   key=%r value=%r enclosing=%r" % (b.key, b.value, b.enclosing))
    elif isinstance(b, model.Preamble):
        print("   value=%r" % b.value)
    else:
        print("   comment=%r" % b.comment[:200])
# raw coverage: do raw blocks reconstruct the source?
raws = [b.raw for b in lib.blocks]
joined = "\n".join(r for r in raws if r)
print("RAW COVERAGE: source chars", len(src), "sum raw chars", sum(len(r) for r in raws if r))
print("source == '\\n'.join(raw)?", joined == src)
