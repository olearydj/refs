"""Aggregate-only statistics over .bib files. Prints counts, never entry content."""
import re, sys, collections, os
files = sys.argv[1:]
entry_re = re.compile(r'^\s*@\s*([A-Za-z]+)\s*[{(]\s*([^,\s]*)', re.M)
field_re = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_:+-]*)\s*=\s*(.*)$', re.M)
tot_types = collections.Counter(); tot_fields = collections.Counter()
for f in files:
    raw = open(f, 'rb').read()
    try: txt = raw.decode('utf-8'); enc='utf-8'
    except UnicodeDecodeError: txt = raw.decode('latin-1'); enc='NOT-utf8'
    types = collections.Counter(t.lower() for t, k in entry_re.findall(txt))
    keys = [k for t, k in entry_re.findall(txt) if t.lower() not in ('comment','string','preamble')]
    fields = collections.Counter(n.lower() for n, v in field_re.findall(txt))
    vals = [(n.lower(), v) for n, v in field_re.findall(txt)]
    nonascii = sum(1 for c in txt if ord(c) > 127)
    texesc = len(re.findall(r'\\[\'"`^~=.uvHckb]\s*\{?[A-Za-z]|\{\\[a-zA-Z]+\}', txt))
    month_macro = sum(1 for n, v in vals if n == 'month' and re.match(r'^[a-z]{3}\s*,?\s*$', v.strip()))
    month_other = sum(1 for n, v in vals if n == 'month') - month_macro
    bare_macro = sum(1 for n, v in vals if n not in ('month',) and re.match(r'^[A-Za-z][A-Za-z0-9_]*\s*(#|,?\s*$)', v.strip()))
    dbl_brace_author = sum(1 for n, v in vals if n in ('author','editor') and v.strip().startswith('{{'))
    braces_in_title = sum(1 for n, v in vals if n == 'title' and re.search(r'\{[^{}]*\{', v))
    dbl_brace_title = sum(1 for n, v in vals if n == 'title' and v.strip().startswith('{{'))
    keychars = collections.Counter(c for k in keys for c in k if not c.isalnum())
    keycase = sum(1 for k in keys if k != k.lower())
    ci_dupes = len(keys) - len({k.lower() for k in keys}); dupes = len(keys) - len(set(keys))
    date_forms = collections.Counter()
    for n, v in vals:
        if n in ('date','urldate','origdate','eventdate'):
            s = v.strip().strip(',').strip('{}"')
            form = re.sub(r'\d', 'D', s)
            date_forms[(n, form)] += 1
    print(f"\n=== {f}\n bytes={len(raw)} enc={enc} entries={len(keys)} nonascii_chars={nonascii} tex_escapes~={texesc}")
    print(" types:", dict(types.most_common()))
    print(" fields:", dict(fields.most_common()))
    print(f" month_macro={month_macro} month_other={month_other} bare_macro_values={bare_macro} @string={types.get('string',0)} @comment={types.get('comment',0)} @preamble={types.get('preamble',0)} jabref-meta={'jabref-meta' in txt}")
    print(f" crossref={fields.get('crossref',0)} xdata={fields.get('xdata',0)} related={fields.get('related',0)} ids={fields.get('ids',0)} file={fields.get('file',0)} keywords={fields.get('keywords',0)} abstract={fields.get('abstract',0)} langid={fields.get('langid',0)} language={fields.get('language',0)}")
    print(f" corporate_double_brace_creator={dbl_brace_author} title_with_inner_braces={braces_in_title} title_fully_double_braced={dbl_brace_title}")
    print(f" key_nonalnum_chars={dict(keychars)} keys_with_uppercase={keycase} dup_keys={dupes} case_insensitive_dup_keys={ci_dupes}")
    print(" date_forms:", {f"{n}:{fm}": c for (n, fm), c in date_forms.most_common(12)})
    biblatex_mark = sum(fields.get(x,0) for x in ('date','journaltitle','location','institution','urldate','langid','eprinttype'))
    bibtex_mark = sum(fields.get(x,0) for x in ('year','journal','address','school','howpublished'))
    print(f" dialect_markers: biblatex-ish={biblatex_mark} (date={fields.get('date',0)} journaltitle={fields.get('journaltitle',0)} location={fields.get('location',0)}) bibtex-ish={bibtex_mark} (year={fields.get('year',0)} journal={fields.get('journal',0)} address={fields.get('address',0)} howpublished={fields.get('howpublished',0)})")
    for t, c in types.items():
        if t not in ('comment','string','preamble'): tot_types[t] += c
    tot_fields.update(fields)
print("\n=== AGGREGATE types:", dict(tot_types.most_common()))
print("=== AGGREGATE fields:", dict(tot_fields.most_common()))
