"""Pure naming transformations; assigned keys are never regenerated implicitly."""

import hashlib
import json
import re
import unicodedata
from importlib.resources import files
from pathlib import Path

from refs.results import RefError

LATIN_BYTES = files('refs').joinpath('data/creator-latin-v1.json').read_bytes()
LATIN = json.loads(LATIN_BYTES)
STOPWORDS = set('a an the and or of to for in on with your'.split())
MINOR = set('a an the and but or nor for so yet as at by in of on per to up via'.split())
GLOBAL_TERMS = ['AI', 'GPT-4', 'LaTeX', 'PhD', 'Python', 'R', 'nbgrader', 'pH']


def creator_token(text: str) -> str:
    text = unicodedata.normalize('NFC', text).lower()
    expanded = ''.join(LATIN['replacements'].get(char, char) for char in text)
    result = []
    latin = False
    for char in unicodedata.normalize('NFKD', expanded):
        if unicodedata.combining(char) and latin:
            continue
        latin = 'LATIN' in unicodedata.name(char, '')
        if char.isascii() and (char.isalpha() or char.isdigit() or char == '-'):
            result.append(char)
        elif char in " '’":
            continue
        else:
            raise RefError('key_author_required', 'Use key_author for this unsupported creator spelling', 2, details={'character': char})
    token = ''.join(result)
    if not token or not any(char.isalnum() for char in token):
        raise RefError('key_author_required', 'A creator token needs letters or digits', 2)
    return token


def protected_spans(text: str, terms: list[str]) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for term in terms
            for match in re.finditer(r'(?<!\w)' + re.escape(unicodedata.normalize('NFC', term)) + r'(?!\w)', text)]


def title_case(text: str, protection: dict, boundary: int | None = None) -> str:
    text = unicodedata.normalize('NFC', text)
    if protection.get('preserve_case'):
        return text
    words = list(re.finditer(r"[^\W_]+(?:['’][^\W_]+)*", text))
    spans = protected_spans(text, protection.get('protected_terms', []))
    pieces, end = [], 0
    for index, match in enumerate(words):
        word = match.group()
        if not any(a <= match.start() and match.end() <= b for a, b in spans):
            first_after_boundary = boundary is not None and match.start() >= boundary and (index == 0 or words[index - 1].start() < boundary)
            word = word.lower() if word.lower() in MINOR and index not in (0, len(words)-1) and not first_after_boundary else word[0].upper() + word[1:]
        pieces.extend([text[end:match.start()], word])
        end = match.end()
    return ''.join(pieces) + text[end:]


def normalize(record: dict) -> tuple[dict, list[dict]]:
    record = json.loads(json.dumps(record))
    metadata = record['metadata']
    warnings = []
    protections = record.setdefault('title_protection', {})
    for field, text in metadata.items():
        if 'title' not in field or not isinstance(text, str):
            continue
        protection = protections.setdefault(field, {'protected_terms': [], 'preserve_case': False})
        protection['protected_terms'] = list(dict.fromkeys(protection.get('protected_terms', []) + [term for term in GLOBAL_TERMS if protected_spans(text, [term])]))
        for term in protection['protected_terms']:
            if not protected_spans(text, [term]):
                warnings.append({'code': 'protected_term_missing', 'message': f'Protected term is absent: {term}', 'path': f'metadata.{field}', 'details': {}, 'retryable': False})
        if not metadata.get('language', '').lower().startswith('en'):
            warnings.append({'code': 'title_language_unknown_or_nonenglish', 'message': 'Title spelling retained without English normalization', 'path': f'metadata.{field}', 'details': {}, 'retryable': False})
            continue
        spans = protected_spans(text, protection['protected_terms'])
        if not protection.get('preserve_case') and any(any(char.isupper() for char in match.group()[1:]) and not any(a <= match.start() and match.end() <= b for a, b in spans) for match in re.finditer(r'\w+', text)):
            warnings.append({'code': 'unprotected_capital', 'message': 'Review unprotected internal capitals', 'path': f'metadata.{field}', 'details': {}, 'retryable': False})
        main = record.get('title_parts', {}).get('main_title') if field == 'title' else None
        metadata[field] = title_case(text, protection, len(unicodedata.normalize('NFC', main)) if main else None)
        if main:
            record['title_parts']['main_title'] = metadata[field][:len(unicodedata.normalize('NFC', main))]
    return record, warnings


def short_title(record: dict) -> str:
    return record['metadata'].get('title-short') or record.get('title_parts', {}).get('main_title') or record['metadata'].get('title', '')


def sort_title(record: dict) -> str:
    override = record.get('overrides', {}).get('sort_title')
    if override:
        return override.casefold()
    text = record['metadata'].get('title', '').lstrip('"“‘\'').casefold()
    return re.sub(r'^(?:a|an|the)\s+', '', text)


def issued_year(record: dict) -> str:
    parts = record['metadata'].get('issued', {}).get('date-parts', [])
    return str(parts[0][0]) if parts and parts[0] else 'ND'


def key(record: dict) -> str:
    words = [word for word in re.findall(r'[^\W_]+', short_title(record)) if word.lower() not in STOPWORDS][:2]
    if not words:
        raise RefError('citation_key_required', 'Supply a citation key when no title tokens are usable', 2)
    title_token = words[0].lower() + ''.join(word[0].upper() + word[1:] for word in words[1:])
    names = record['metadata'].get('author') or record['metadata'].get('editor') or []
    creator = record.get('key_author')
    if not creator and names:
        creator = names[0].get('family') or names[0].get('literal') or names[0].get('given')
    year = issued_year(record)
    return f'{creator_token(creator)}-{year}-{title_token}' if creator else f'{title_token}-{year}'


def suffix(index: int) -> str:
    result = ''
    while index:
        index, remainder = divmod(index-1, 26)
        result = chr(97 + remainder) + result
    return '-' + result if result else ''


def provenance() -> dict:
    return dict(origin='generated', policy=LATIN['policy'], table_version=LATIN['version'], table_sha256=hashlib.sha256(LATIN_BYTES).hexdigest(), unicode_version=unicodedata.unidata_version)


def edition_display(value: int | str) -> str:
    if isinstance(value, int):
        ending = 'th' if 10 <= value % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
        return f'{value}{ending} ed.'
    return value


def filename(record: dict, original: str) -> str:
    year = issued_year(record)
    words = re.findall(r'[^\W_]+', short_title(record))
    if year == 'ND' or not words:
        return original
    name = ''.join(word[0].upper() + word[1:] for word in words)
    edition = record['metadata'].get('edition')
    version = record['metadata'].get('version')
    if isinstance(edition, int):
        name += f'-{edition}E'
    elif version:
        name += '-v' + re.sub(r'[^\w.-]', '', version.removeprefix('v'))
    return f'{name}-{year}{Path(original).suffix}'
