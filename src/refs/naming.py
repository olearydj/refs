"""Pure naming transformations; assigned keys are never regenerated implicitly."""

import hashlib
import json
import re
import unicodedata
from copy import deepcopy
from importlib.resources import files
from pathlib import Path

from refs import languages, math_text
from refs.results import RefError, notice

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


def title_case(text: str, protection: dict, boundary: int | None = None, minor_words=None) -> str:
    text = math_text.transform(text, lambda part: unicodedata.normalize('NFC', part))
    if protection.get('preserve_case'):
        return text
    words = list(re.finditer(r"[^\W_]+(?:['’][^\W_]+)*", text))
    spans = protected_spans(text, protection.get('protected_terms', [])) + math_text.spans(text)
    pieces, end = [], 0
    for index, match in enumerate(words):
        word = match.group()
        if not any(a <= match.start() and match.end() <= b for a, b in spans):
            after_colon = index > 0 and any(char in ':!?' for char in text[words[index - 1].end():match.start()])
            first_after_boundary = after_colon or boundary is not None and match.start() >= boundary and (index == 0 or words[index - 1].start() < boundary)
            word = word.lower() if word.lower() in (MINOR if minor_words is None else {word.casefold() for word in minor_words}) and index not in (0, len(words)-1) and not first_after_boundary else word[0].upper() + word[1:]
        pieces.extend([text[end:match.start()], word])
        end = match.end()
    return ''.join(pieces) + text[end:]


def normalize(record: dict, policy: dict | None = None, fields: set[str] | None = None) -> tuple[dict, list[dict]]:
    policy = policy or {}
    record = deepcopy(record)
    metadata = record['metadata']
    warnings = []
    protections = record.setdefault('title_protection', {})
    for field, text in metadata.items():
        if 'title' not in field or not isinstance(text, str) or fields is not None and field not in fields:
            continue
        if policy.get('titles', {}).get('policy') == 'preserve' and field not in protections:
            protections[field] = {'protected_terms': [], 'preserve_case': True}
            continue
        letter_words = re.findall(r'[^\W\d_]+',text)
        shouted = bool(letter_words) and all(word.isupper() for word in letter_words)
        acronyms = [word for word in letter_words if len(word)>=2 and word.isupper()] if not shouted else []
        protection = protections.setdefault(field, {'protected_terms': [], 'preserve_case': False})
        protection['protected_terms'] = list(dict.fromkeys(protection.get('protected_terms', []) + acronyms + [term for term in policy.get('titles',{}).get('protected_terms',GLOBAL_TERMS) if protected_spans(text, [term])]))
        for term in protection['protected_terms']:
            if not protected_spans(text, [term]):
                warnings.append(notice('protected_term_missing', f'Protected term is absent: {term}', path=f'metadata.{field}'))
        language = (languages.tag(metadata.get('language', '')) or '').lower()
        if not language and any(char.isalpha() and not char.isascii() for char in text):
            warnings.append(notice('title_language_unknown_or_nonenglish', 'Title language is unknown; spelling retained', path=f'metadata.{field}'))
            continue
        if language and not language.startswith('en'):
            continue
        spans = protected_spans(text, protection['protected_terms']) + math_text.spans(text)
        if not protection.get('preserve_case') and (shouted or any(any(char.isupper() for char in match.group()[1:]) and not any(a <= match.start() and match.end() <= b for a, b in spans) for match in re.finditer(r'\w+', text))):
            warnings.append(notice('unprotected_capital', 'Review unprotected internal capitals', path=f'metadata.{field}'))
        main = record.get('title_parts', {}).get('main_title') if field == 'title' else None
        metadata[field] = title_case(text, protection, len(unicodedata.normalize('NFC', main)) if main else None,policy.get('titles',{}).get('minor_words'))
        if main:
            record['title_parts']['main_title'] = metadata[field][:len(unicodedata.normalize('NFC', main))]
    return record, warnings


def short_title(record: dict) -> str:
    return record['metadata'].get('title-short') or record.get('title_parts', {}).get('main_title') or record['metadata'].get('title', '')


def title_tokens(text: str) -> list[str]:
    # U+02BC is a Unicode letter, but is punctuation here unless between letters.
    joined = re.sub(r"(?<=[^\W_ʼ])['’ʼ](?=[^\W_ʼ])",
                    lambda match: '' if text[match.start()-1].isalpha() and text[match.end()].isalpha() else ' ', text)
    return re.findall(r'[^\W_ʼ]+', joined)


def sort_title(record: dict, policy: dict | None = None) -> str:
    override = record.get('overrides', {}).get('sort_title')
    if override:
        return override.casefold()
    text = record['metadata'].get('title', '').lstrip('"“‘\'').casefold()
    articles=(policy or {}).get('sorting',{}).get('ignore_leading_articles',['a','an','the'])
    return re.sub(r'^(?:'+'|'.join(re.escape(word.casefold()) for word in articles)+r')\s+', '', text) if articles else text


def issued_year(record: dict) -> str:
    parts = record['metadata'].get('issued', {}).get('date-parts', [])
    return str(parts[0][0]) if parts and parts[0] else 'ND'


def key(record: dict, policy: dict | None = None, *, warnings: list[dict] | None = None) -> str:
    settings=(policy or {}).get('keys',{})
    stopwords={word.casefold() for word in settings.get('stopwords',STOPWORDS)}
    words = [word for word in title_tokens(short_title(record)) if word.lower() not in stopwords][:settings.get('title_words',2)]
    if not words:
        raise RefError('citation_key_required', 'Supply a citation key when no title tokens are usable', 2)
    title_token = words[0].lower() + ''.join(word[0].upper() + word[1:] for word in words[1:])
    names = record['metadata'].get('author') or record['metadata'].get('editor') or []
    creator = record.get('key_author')
    if not creator and names:
        creator = names[0].get('family') or names[0].get('literal') or names[0].get('given')
    if creator and names and names[0].get('literal') and not record.get('key_author'):
        creator=settings.get('corporate_aliases',{}).get(unicodedata.normalize('NFC',creator),creator)
    year = issued_year(record)
    if year=='ND':
        year=settings.get('missing_year','ND')
    token = ''
    if creator:
        try:
            token = creator_token(creator)
        except RefError as exc:
            if record.get('key_author') or exc.issue['code'] != 'key_author_required':
                raise
            if warnings is not None:
                warnings.append(notice('creator_token_fallback', 'Creator gave no usable token; the key uses the title, and key_author can be supplied',
                                       details={'creator': creator, 'reason': exc.issue['message']}))
    template=settings.get('template','{author}-{year}-{title}') if token else settings.get('without_creator','{title}-{year}')
    return template.format(author=token,year=year,title=title_token)


def suffix(index: int) -> str:
    result = ''
    while index:
        index, remainder = divmod(index-1, 26)
        result = chr(97 + remainder) + result
    return '-' + result if result else ''


def provenance(policy: dict | None = None) -> dict:
    return dict(naming_settings=(policy or {}).get('keys',{}),origin='generated', policy=LATIN['policy'], table_version=LATIN['version'], table_sha256=hashlib.sha256(LATIN_BYTES).hexdigest(), unicode_version=unicodedata.unidata_version)


def filename(record: dict, original: str, label: str | None = None, *, report_fallback: bool = False):
    year = issued_year(record)
    words = title_tokens(short_title(record))
    if year == 'ND' or not words:
        return (original, True) if report_fallback else original
    name = ''.join(word[0].upper() + word[1:] for word in words)
    edition = record['metadata'].get('edition')
    version = record['metadata'].get('version')
    if isinstance(edition, int):
        name += f'-{edition}E'
    elif version:
        name += '-v' + re.sub(r'[^\w.-]', '', version.removeprefix('v'))
    slug = ''.join(char for char in label or '' if char.isalpha() or char.isdigit() or char in '.-')
    result = f'{name}-{year}' + (f'-{slug}' if slug else '') + Path(original).suffix
    return (result, False) if report_fallback else result
