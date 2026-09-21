import sys, traceback
from pybtex.database import parse_string, parse_file
from pybtex import errors
for fn in ["fx/syntax.bib","fx/syntax_valid.bib","fx/content_valid.bib","fx/biblatex.bib"]:
    print("#####", fn)
    for strict in (True, False):
        errors.set_strict_mode(strict)
        try:
            db = parse_file(fn, bib_format="bibtex")
        except Exception as e:
            print(" strict=%s EXC %s: %s" % (strict, type(e).__name__, str(e)[:200])); continue
        print(" strict=%s entries=%s preamble=%r" % (strict, list(db.entries.keys()), db.preamble[:60]))
        for k,e in db.entries.items():
            if k in ("macro1","CaseKey","names1","prot1","chap1","inproc1","dates1"):
                print("   ", k, e.type, dict(e.fields))
                for role, ps in e.persons.items():
                    for p in ps:
                        print("       ", role, dict(first=p.first_names, middle=p.middle_names, prelast=p.prelast_names, last=p.last_names, lineage=p.lineage_names))
        break
