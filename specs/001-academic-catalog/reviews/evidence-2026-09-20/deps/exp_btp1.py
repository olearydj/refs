import bibtexparser, logging
from bibtexparser.bparser import BibTexParser
print("v", bibtexparser.__version__)
for fn in ["fx/syntax.bib","fx/content.bib"]:
    p = BibTexParser(common_strings=True, ignore_nonstandard_types=False, interpolate_strings=True)
    try:
        db = p.parse(open(fn).read())
    except Exception as e:
        print(fn, "EXC", type(e).__name__, str(e)[:300]); continue
    print(fn, "entries:", [e["ID"] for e in db.entries], "comments:", len(db.comments), "preambles:", db.preambles, "strings:", dict(db.strings) if len(db.strings)<10 else len(db.strings))
    for e in db.entries:
        if e["ID"] in ("macro1","CaseKey","broken3"): print("  ", e)
