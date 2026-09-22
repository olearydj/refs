"""Plain readable views for the three retrieval commands."""

from refs.naming import issued_year


def authors(record: dict) -> list[str]:
    return [name.get('literal') or ' '.join(name[part].strip() for part in ('given', 'dropping-particle', 'non-dropping-particle', 'family', 'suffix') if name.get(part))
            for name in record['metadata'].get('author', [])]



def metadata_text(value) -> str:
    if isinstance(value, list):
        return '; '.join(metadata_text(item) for item in value)
    if isinstance(value, dict):
        if any(key in value for key in ('family', 'given', 'literal')):
            return authors({'metadata': {'author': [value]}})[0]
        if 'date-parts' in value:
            dates = ' – '.join('-'.join(str(number).zfill(4 if index == 0 else 2) for index,number in enumerate(parts)) for parts in value['date-parts'])
            extras = {key:item for key,item in value.items() if key != 'date-parts'}
            return dates + ('; ' + metadata_text(extras) if extras else '')
        return '; '.join(f'{key}: {metadata_text(item)}' for key,item in sorted(value.items()))
    return str(value)

def readable(command: str, data: dict) -> str:
    if command == 'show':
        metadata = data['metadata']
        lines = [f"Key: {data['citation_key']}", f"Type: {metadata['type']}",
                 'Authors: ' + ('; '.join(authors(data)) or '(not supplied)'),
                 'Year: ' + issued_year(data), 'Title: ' + metadata.get('title', '(not supplied)')]
        for field in sorted(set(metadata) - {'type', 'author', 'title'}):
            if metadata[field] not in (None, '', [], {}):
                lines.append(f'{field}: {metadata_text(metadata[field])}')
        if data.get('limitations'):
            lines.append('Limitations: ' + '; '.join(f"{item['field']}: {item['reason']}" for item in data['limitations']))
        resources = data.get('resources', [])
        lines.append('Files:' if resources else 'Files: (none)')
        for resource in resources:
            lines.append('  ' + str(resource.get('resolved_path') or resource.get('path') or resource.get('relative') or resource.get('id', '(unavailable)')))
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
