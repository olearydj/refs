"""Guarded library parsing with independent byte framing and scoped mappings."""

import re

import bibtexparser
from bibtexparser.model import Entry
from pydantic import ValidationError
from pylatexenc.latex2text import LatexNodes2Text

from refs.models import REGISTRY, SourceCreate
from refs.results import RefError

MONTHS = dict(zip('jan feb mar apr may jun jul aug sep oct nov dec'.split(), range(1, 13), strict=True))
MARKER = re.compile(rb'@([A-Za-z]+)\s*([{(])')


def partition(raw: bytes) -> list[dict]:
    """Capture balanced block spans, not field syntax or values."""
    result = []
    cursor = 0
    while match := MARKER.search(raw, cursor):
        # A percent-comment line cannot introduce an entry.
        line = raw[raw.rfind(b'\n', 0, match.start())+1:match.start()]
        if b'%' in line:
            cursor = raw.find(b'\n', match.end())
            if cursor < 0:
                break
            continue
        opening = match[2][0]
        closing = ord('}') if opening == ord('{') else ord(')')
        depth, braces, quoted, escaped = 1, 0, False, False
        end = match.end()
        while end < len(raw):
            char = raw[end]
            if escaped:
                escaped = False
            elif char == ord('\\'):
                escaped = True
            elif opening == ord('{'):
                if char == opening:
                    depth += 1
                elif char == closing:
                    depth -= 1
            else:
                if char == ord('{'):
                    braces += 1
                elif char == ord('}'):
                    braces -= 1
                elif char == ord('"') and not braces:
                    quoted = not quoted
                elif char == closing and not braces and not quoted:
                    depth -= 1
            end += 1
            if depth == 0:
                break
        if depth or braces:
            raise RefError('unpartitionable_input', 'Cannot partition input safely; repair the incomplete block', 2)
        kind = match[1].decode().lower()
        result.append(dict(kind=kind if kind in ('string', 'comment', 'preamble') else 'entry',
                           start=match.start(), end=end, raw=raw[match.start():end]))
        cursor = end
    if not result and raw.strip() and any(not line.lstrip().startswith(b'%') for line in raw.splitlines() if line.strip()):
        raise RefError('unpartitionable_input', 'Cannot partition input safely; supply Bib entries', 2)
    return result


def decode(value: str) -> str:
    # Unknown macros must not disappear through the text decoder.
    allowed = {'textit', 'textbf', 'emph', 'textrm', 'texttt', 'textnormal', 'LaTeX', 'TeX', 'ae', 'AE', 'oe', 'OE', 'aa', 'AA', 'o', 'O', 'l', 'L', 'ss', 'i', 'j', 'textbackslash', 'textasciitilde', 'textasciicircum', 'textbraceleft', 'textbraceright', 'c', 'v', 'u', 'H', 'k', 'r', 'b', 'd', 't'}
    if '$' in value or any(name not in allowed for name in re.findall(r'\\([A-Za-z]+)', value)):
        raise ValueError('Unsupported TeX command or math; preserve and preprocess explicitly')
    return LatexNodes2Text().latex_to_text(value).strip()


def names(value: str) -> list[dict]:
    from bibtexparser.middlewares import SeparateCoAuthors, SplitNameParts
    separated = SeparateCoAuthors()._transform_field_value(value)
    result = []
    for name in separated:
        if name.startswith('{') and name.endswith('}'):
            result.append({'literal': decode(name)})
            continue
        parts = SplitNameParts()._transform_field_value([name])[0]
        result.append({key: decode(' '.join(tokens)) for key, tokens in [('given', parts.first), ('family', parts.last), ('dropping-particle', parts.von), ('suffix', parts.jr)] if tokens})
    return result


def date(value: str) -> dict:
    if re.fullmatch(r'\d{4}(?:-\d{2}){0,2}', value):
        return {'date-parts': [[int(part) for part in value.split('-')]]}
    return {'literal': value}


def parse(raw: bytes) -> dict:
    """Return one validated proposal and explicit preserved-only limitations."""
    limitations = []
    try:
        text = raw.decode('utf-8')
        if MARKER.search(raw, 1):
            raise ValueError('Embedded entry marker requires inspection')
        library = bibtexparser.parse_string(text)
        if len(library.blocks) != 1 or not isinstance(library.blocks[0], Entry):
            raise ValueError('Malformed or duplicate fields; inspect the preserved entry')
        entry = library.blocks[0]
        if entry.raw != text:
            raise ValueError('Parser did not retain the complete entry')
        fields = {field.key.lower(): field.value for field in entry.fields}
        if len(fields) != len(entry.fields):
            raise ValueError('Case-colliding fields require inspection')
        # Compare the library field list with surface assignments. This is a
        # corruption guard, not an alternative field parser.
        surface = re.sub(r'\\.', '  ', text)
        depth = 0
        quoted = False
        masked = []
        for char in surface:
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
            elif char == '"' and depth == 1:
                quoted = not quoted
            masked.append(' ' if depth > 1 or quoted else char)
        header, _, body = ''.join(masked).partition(',')
        assignments = re.findall(r'(?:^|,)\s*([\w-]+)\s*=', body)
        if [name.lower() for name in assignments] != list(fields):
            raise ValueError('Field assignments disagree with parser output')
        # Missing equals can be swallowed into the preceding bare value.
        if any(re.search(r',\s*[\w-]+\s*(?:,|$)', field.value) for field in entry.fields if field.key not in entry.parser_metadata.get('removed_enclosing', {})):
            raise ValueError('Possible missing equals in field list')
        kind = entry.entry_type.lower()
        canonical = REGISTRY['bib_type_aliases'].get(kind)
        if canonical is None:
            raise ValueError('Unsupported entry type')
        metadata = {'type': canonical}
        value: dict = {'schema_version': '1.0', 'metadata': metadata, 'provenance': [{'origin': 'import', 'access': 'unknown'}]}
        protection = {}
        consumed = set()
        enclosing = entry.parser_metadata.get('removed_enclosing', {})
        unsupported = {field for field, contents in fields.items() if field not in enclosing and not contents.isdecimal() and not (field == 'month' and contents.lower() in MONTHS)}
        for field in unsupported:
            limitations.append(dict(field=field, reason='Unresolved macro or concatenation'))
        traditional = kind == 'inbook' and 'booktitle' not in fields and ('chapter' in fields or 'pages' in fields)

        def assign(path, incoming):
            target: dict = value
            parts = path.split('.')
            for part in parts[:-1]:
                target = target.setdefault(part, {})
            if parts[-1] in target and target[parts[-1]] != incoming:
                raise ValueError(f'Conflicting aliases for {path}')
            target[parts[-1]] = incoming

        for row in REGISTRY['rows']:
            field = row['source_field']
            if row['input_format'] != 'bib' or kind not in row['type_scope'] or field not in fields:
                continue
            consumed.add(field)
            if field in unsupported or field in ('year', 'month', 'date', 'howpublished', 'note', 'file'):
                continue
            path = row['canonical_path']
            if field == 'title' and traditional:
                path = 'metadata.container-title'
            if path.startswith('metadata.') and canonical not in REGISTRY['field_applicability'].get(path[9:], []):
                limitations.append(dict(field=field, reason='Field is not applicable to this type'))
                continue
            if kind == 'book' and field == 'number' and 'series' not in fields:
                limitations.append(dict(field=field, reason='Series number requires series evidence'))
                continue
            if field == 'eprint' and not (fields.get('archiveprefix') or fields.get('eprinttype')):
                limitations.append(dict(field=field, reason='Preprint locator requires repository evidence'))
                continue
            contents = fields[field]
            try:
                if field in ('author', 'editor', 'translator', 'bookauthor', 'holder'):
                    incoming = names(contents)
                elif field in ('doi', 'url'):
                    incoming = contents
                elif field == 'urldate':
                    incoming = date(decode(contents))
                elif field == 'keywords':
                    incoming = [term.strip() for term in decode(contents).split(',') if term.strip()]
                else:
                    incoming = decode(contents)
                    if field in ('language', 'langid'):
                        incoming = {'english':'en', 'american':'en-US', 'british':'en-GB', 'german':'de', 'french':'fr', 'spanish':'es'}.get(incoming.lower(), incoming)
                assign(path, incoming)
                if 'title' in path:
                    terms = [decode(group) for group in re.findall(r'(?<![\\\w])\{([^{}]+)\}', contents) if not group.startswith('\\')]
                    if terms:
                        protection[path[9:]] = dict(protected_terms=terms, preserve_case=contents.startswith('{') and contents.endswith('}') and decode(contents) in terms)
            except ValueError as exc:
                if str(exc).startswith('Conflicting aliases'):
                    raise
                limitations.append(dict(field=field, reason=str(exc)))
        for field in set(fields) - consumed:
            limitations.append(dict(field=field, reason='Unmapped field preserved verbatim'))
        notes = [decode(fields[field]) for field in ('howpublished', 'note') if field in fields and field not in unsupported]
        if notes:
            metadata['note'] = '\n'.join(notes)
        parts = None
        if 'year' in fields and 'year' not in unsupported:
            year = fields['year']
            if year.isdecimal():
                parts = [int(year)]
                month = fields.get('month', '')
                if month and 'month' not in unsupported:
                    parts.append(MONTHS.get(month.lower()) or int(month))
            else:
                metadata['issued'] = {'literal': year}
        if 'date' in fields and 'date' not in unsupported:
            supplied = date(fields['date'])
            if parts and ('date-parts' not in supplied or supplied['date-parts'][0][:len(parts)] != parts):
                raise ValueError('Date and year/month disagree')
            metadata['issued'] = supplied
        elif parts:
            metadata['issued'] = {'date-parts': [parts]}
        if 'month' in fields and 'year' not in fields and 'date' not in fields:
            limitations.append(dict(field='month', reason='Month without year remains unresolved'))
        if kind in ('phdthesis', 'mastersthesis'):
            degree = 'PhD thesis' if kind == 'phdthesis' else "Master's thesis"
            if 'genre' not in metadata:
                metadata['genre'] = degree
        value['title_protection'] = protection
        source = SourceCreate.model_validate(value)
        # Assigned legacy keys are evidence, even when portable export rejects them.
        source.citation_key = entry.key
        proposals = [fields['file']] if 'file' in fields else []
        return dict(source=source, limitations=limitations, resource_proposals=proposals)
    except (ValueError, ValidationError) as exc:
        raise RefError('invalid_bib_entry', str(exc), 2, details={'limitations': limitations}) from exc
