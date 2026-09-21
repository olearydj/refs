import bibtexparser
s = '''@article{d1, year = {2019}, year = {2018}, title={x}}
@article{d2, title = "A" # " B", year = 2020}
@article(parens, title = {Paren delimited entry}, year = 2001)
@article{ws key, title = {key with space}}
@article{k:1/2+3, title = {odd key chars}}
@ARTICLE{Upper, TITLE = {t}}
@article{at_in_value, note = {email a@b.org and @article{fake, in value}}
@article{utf8, author = {Müller, Jörg}, title = {Łódź 山田}}
'''
lib = bibtexparser.parse_string(s)
for b in lib.blocks:
    print(type(b).__name__, "line", b.start_line, getattr(b,"key",None), [(f.key,f.value) for f in getattr(b,"fields",[])] if hasattr(b,"fields") else (str(getattr(b,"error",""))[:100], repr(b.raw[:70])))
