"""Guarded library parsing with independent byte framing and scoped mappings."""

import logging
import re
from urllib.parse import urlparse

import bibtexparser
from bibtexparser.model import Entry
from pydantic import ValidationError
from pylatexenc.latex2text import LatexNodes2Text

from refs.models import REGISTRY, SourceCreate
from refs.results import RefError

# The parser reports malformed blocks through logging before returning failed_blocks.
# Refs turns those blocks into its own per-entry result instead of leaking a warning
# outside the JSON envelope through logging's last-resort stderr handler.
logging.getLogger('bibtexparser.splitter').addHandler(logging.NullHandler())

MONTHS = dict(zip('jan feb mar apr may jun jul aug sep oct nov dec'.split(), range(1, 13), strict=True))
FULL_MONTHS = dict(zip('january february march april may june july august september october november december'.split(), range(1, 13), strict=True))
MARKER = re.compile(rb'@([A-Za-z]+)\s*([{(])')


def month_number(value: str) -> int:
    text = value.strip().casefold()
    month = int(text) if text.isdecimal() else MONTHS.get(text) or FULL_MONTHS.get(text)
    if month is None or not 1 <= month <= 12:
        raise ValueError(f'Invalid month: {value}')
    return month


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



def preserved_fields(raw: bytes) -> set[str]:
    return {field.key.lower() for entry in bibtexparser.parse_string(raw.decode('utf-8')).entries for field in entry.fields if field.key.lower() == 'howpublished'}

def decode(value: str) -> str:
    # Unknown macros must not disappear through the text decoder.
    allowed = {'relax', 'textit', 'textbf', 'emph', 'textrm', 'texttt', 'textnormal', 'LaTeX', 'TeX', 'ae', 'AE', 'oe', 'OE', 'aa', 'AA', 'o', 'O', 'l', 'L', 'ss', 'i', 'j', 'textbackslash', 'textasciitilde', 'textasciicircum', 'textbraceleft', 'textbraceright', 'c', 'v', 'u', 'H', 'k', 'r', 'b', 'd', 't'}
    if '$' in value or any(name not in allowed for name in re.findall(r'\\([A-Za-z]+)', value)):
        raise ValueError('Unsupported TeX command or math; preserve and preprocess explicitly')
    return LatexNodes2Text().latex_to_text(value).strip()


def names(value: str) -> list[dict]:
    from bibtexparser.middlewares import SeparateCoAuthors, SplitNameParts
    separated = SeparateCoAuthors()._transform_field_value(value)
    result = []
    for name in separated:
        if re.match(r'\s*(?:family|given|prefix|suffix|useprefix)\s*=', name):
            parts = {}
            for component in re.split(r',\s*(?=[a-z]+\s*=)', name):
                key, separator, contents = component.partition('=')
                key = key.strip()
                if not separator or key not in ('family', 'given', 'prefix', 'suffix', 'useprefix') or key in parts:
                    raise ValueError('Invalid extended creator name')
                parts[key] = decode(contents.strip())
            if parts.get('useprefix', 'false').lower() not in ('true', 'false'):
                raise ValueError('useprefix must be true or false')
            person = {key: parts[key] for key in ('family', 'given', 'suffix') if parts.get(key)}
            if parts.get('prefix'):
                particle = 'non-dropping-particle' if parts.get('useprefix', 'false').lower() == 'true' else 'dropping-particle'
                person[particle] = parts['prefix']
            if not person.get('family') and not person.get('given'):
                raise ValueError('Creator name needs family or given')
            result.append(person)
            continue
        if name.startswith('{') and name.endswith('}'):
            result.append({'literal': decode(name)})
            continue
        parts = SplitNameParts()._transform_field_value([name])[0]
        result.append({key: decode(' '.join(tokens)) for key, tokens in [('given', parts.first), ('family', parts.last), ('dropping-particle', parts.von), ('suffix', parts.jr)] if tokens})
    if not result or any(not name for name in result):
        raise ValueError('Creator field could not be parsed; correct the preserved entry')
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
        parsed_month = month_number(fields['month']) if 'month' in fields else None
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
        value: dict = {'schema_version': '1.0', 'metadata': metadata, 'native_type': {'namespace':'bibtex', 'value':kind}, 'provenance': [{'origin': 'import', 'access': 'unknown'}]}
        protection = {}
        consumed = set()
        enclosing = {key.lower(): value for key,value in entry.parser_metadata.get('removed_enclosing', {}).items()}
        unsupported = {field for field, contents in fields.items() if field not in enclosing and not contents.isdecimal() and field != 'month'}
        for field in unsupported:
            if field in ('author', 'editor', 'translator', 'bookauthor', 'holder'):
                raise ValueError(f'Cannot resolve creator field {field}')
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
                    if field == 'url' and (urlparse(contents).scheme not in ('http', 'https') or not urlparse(contents).netloc):
                        limitations.append(dict(field='url', reason='Non-HTTP(S) or relative URL preserved verbatim; supply an absolute URL to use it'))
                        continue
                    incoming = contents
                elif field == 'urldate':
                    incoming = date(decode(contents))
                elif field == 'keywords':
                    incoming = [term.strip() for term in decode(contents).split(',') if term.strip()]
                else:
                    incoming = decode(contents)
                    if field in ('language', 'langid'):
                        from refs.languages import normalize
                        incoming = normalize(incoming)
                assign(path, incoming)
                if 'title' in path:
                    protection_text = re.sub(r'\\(?:[A-Za-z]+|[^A-Za-z])\s*\{[^{}]*\}', '', contents)
                    terms = [decode(group) for group in re.findall(r'(?<![\\\w])\{([^{}]+)\}', protection_text) if not group.startswith('\\')]
                    if terms:
                        protection[path[9:]] = dict(protected_terms=terms, preserve_case=contents.startswith('{') and contents.endswith('}') and decode(contents) in terms)
            except ValueError as exc:
                if field in ('author', 'editor', 'translator', 'bookauthor', 'holder') or str(exc).startswith('Conflicting aliases'):
                    raise
                limitations.append(dict(field=field, reason=str(exc)))
        for field in set(fields) - consumed:
            limitations.append(dict(field=field, reason='Unmapped field preserved verbatim'))
        notes = [decode(fields[field]) for field in ('note',) if field in fields and field not in unsupported]
        if notes:
            metadata['note'] = '\n'.join(notes)
        parts = None
        if 'year' in fields and 'year' not in unsupported:
            year = fields['year']
            if year.isdecimal():
                parts = [int(year)]
                month = fields.get('month', '')
                if month and 'month' not in unsupported:
                    parts.append(parsed_month)
            else:
                metadata['issued'] = {'literal': year}
                limitations.append(dict(field='year', reason='Unparseable year retained as literal date'))
        if 'date' in fields and 'date' not in unsupported:
            supplied = date(fields['date'])
            if parts:
                supplied_parts = supplied.get('date-parts', [[]])[0]
                overlap = min(len(parts),len(supplied_parts))
                if not supplied_parts or supplied_parts[:overlap] != parts[:overlap]:
                    raise ValueError('Date and year/month disagree')
                supplied = {'date-parts':[parts if len(parts)>len(supplied_parts) else supplied_parts]}
            if 'month' in fields and 'month' not in unsupported and 'date-parts' in supplied:
                month = parsed_month
                supplied_parts = supplied['date-parts'][0]
                if len(supplied_parts)>1 and supplied_parts[1] != month:
                    raise ValueError('Date and month disagree')
                if len(supplied_parts)==1:
                    supplied_parts.append(month)
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
