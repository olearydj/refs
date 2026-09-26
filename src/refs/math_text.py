"""Balanced TeX math spans are opaque; transformations apply to the text around them."""

import re

DELIMITERS = re.compile(r'\$\$|\$|\\[()]')


class UnbalancedMath(ValueError):
    pass


def escaped(value: str, position: int) -> bool:
    start = position
    while start and value[start - 1] == '\\':
        start -= 1
    return (position - start) % 2 == 1


def spans(value: str, *, strict: bool = False) -> list[tuple[int, int]]:
    result, position = [], 0
    while match := DELIMITERS.search(value, position):
        opening = match.group()
        position = match.end()
        if escaped(value, match.start()):
            continue
        closing = r'\)' if opening == r'\(' else opening
        end = next((candidate for candidate in re.finditer(re.escape(closing), value[position:])
                    if not escaped(value, position + candidate.start())), None) if opening != r'\)' else None
        if end is None:
            if strict:
                raise UnbalancedMath(f'Unbalanced math delimiter: {opening}')
            continue
        position += end.end()
        result.append((match.start(), position))
    return result


def transform(value: str, text_transform, *, strict: bool = False) -> str:
    pieces, position = [], 0
    for start, end in spans(value, strict=strict):
        pieces.extend((text_transform(value[position:start]), value[start:end]))
        position = end
    return ''.join(pieces) + text_transform(value[position:])
