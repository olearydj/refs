"""Pinned language aliases shared by validation, display and export."""

import hashlib
import json
import re
from importlib.resources import files

RAW = files('refs').joinpath('data/languages.json').read_bytes()
PROVENANCE = json.loads(files('refs').joinpath('data/provenance.json').read_text())
if hashlib.sha256(RAW).hexdigest() != PROVENANCE['languages']['sha256']:
    raise RuntimeError('Packaged language table failed its provenance hash check')
DATA = json.loads(RAW)


def normalize(value: str) -> str:
    literal = value.strip()
    return DATA['aliases'].get(literal.casefold(), literal)


def tag(value: str) -> str | None:
    value = normalize(value)
    if re.fullmatch(r'[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*', value) and value.split('-')[0].casefold() in DATA['tags']:
        return value
    return None


def limitations(metadata: dict) -> list[dict]:
    value = metadata.get('language')
    if value and tag(value) is None:
        return [dict(field='language', reason=f'Unrecognized language retained literally: {value}; supply a language tag if known')]
    return []


def portable(value: str) -> str | None:
    recognized = tag(value)
    if recognized is None:
        return None
    return DATA['portable'].get(recognized.casefold(), recognized)
