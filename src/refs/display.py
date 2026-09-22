"""Plain readable views for the three retrieval commands."""

from refs.naming import issued_year


def authors(record: dict) -> list[str]:
    return [name.get('literal') or ' '.join(name[part].strip() for part in ('given', 'dropping-particle', 'non-dropping-particle', 'family', 'suffix') if name.get(part))
            for name in record['metadata'].get('author', [])]


def readable(command: str, data: dict) -> str:
    if command == 'show':
        metadata = data['metadata']
        lines = [f"Key: {data['citation_key']}", f"Type: {metadata['type']}",
                 'Authors: ' + ('; '.join(authors(data)) or '(not supplied)'),
                 'Year: ' + issued_year(data), 'Title: ' + metadata.get('title', '(not supplied)')]
        for field, label in [('container-title', 'Container'), ('volume', 'Volume'), ('issue', 'Issue'), ('page', 'Pages'), ('DOI', 'DOI'), ('URL', 'URL')]:
            if field in metadata:
                lines.append(f'{label}: {metadata[field]}')
        resources = data.get('resources', [])
        lines.append('Files:' if resources else 'Files: (none)')
        for resource in resources:
            lines.append('  ' + str(resource.get('path') or resource.get('id', '(unavailable)')))
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
