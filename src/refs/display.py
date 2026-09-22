"""Plain readable views for the three retrieval commands."""

import json

from refs.naming import issued_year


def authors(record: dict) -> list[str]:
    return [name.get('literal') or ' '.join(name.get(part, '') for part in ('given', 'non-dropping-particle', 'family', 'suffix')).strip()
            for name in record['metadata'].get('author', [])]


def readable(command: str, data: dict) -> str:
    if command == 'show':
        metadata = data['metadata']
        lines = [f"Key: {data['citation_key']}", f"Type: {metadata['type']}",
                 'Authors: ' + ('; '.join(authors(data)) or '(not supplied)'),
                 'Year: ' + issued_year(data), 'Title: ' + metadata.get('title', '(not supplied)')]
        for field, value in metadata.items():
            if field not in ('type', 'author', 'issued', 'title'):
                lines.append(f'{field}: {value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)}')
        # Retain date precision, state and all provenance in the readable view.
        for field, value in data.items():
            if field not in ('metadata', 'citation_key', 'resources', 'projects'):
                lines.append(f'{field}: {value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)}')
        if 'issued' in metadata:
            lines.append('Issued: ' + json.dumps(metadata['issued'], ensure_ascii=False))
        lines.append('Files: ' + (json.dumps(data.get('resources'), ensure_ascii=False) if data.get('resources') else '(none)'))
        lines.append('Projects: ' + (', '.join(item['name'] for item in data.get('projects', [])) or '(none)'))
        return '\n'.join(lines)
    lines = []
    for record in data['items']:
        creator = next(iter(authors(record)), '(no author)')
        line = f"{record['citation_key']} | {creator} | {issued_year(record)} | {record['metadata'].get('title', '(no title)')}"
        if command == 'search':
            line += ' | matched: ' + ', '.join(dict.fromkeys(match['field'] for match in record['matches']))
        lines.append(' '.join(line.splitlines()))
    return '\n'.join(lines) if lines else '(no sources)'
