"""SQLite's derived lexical projection; original bytes are never indexed."""

import json


def projection(record: dict):
    yield 'citation_key', 'catalog', record['citation_key']
    for name, value in record['metadata'].items():
        yield 'metadata.' + name, 'metadata', value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    for entry in record.get('context', []):
        yield 'context', entry['origin'], entry['text']
    for tag in record.get('legacy_tags', []):
        yield 'legacy_tags', 'import', tag


def refresh(connection, record: dict) -> None:
    connection.execute('DELETE FROM search_projection WHERE source_id=?', (record['id'],))
    if record['state'] == 'active':
        connection.executemany('INSERT INTO search_projection (source_id, field, origin, text) VALUES (?, ?, ?, ?)',
                               [(record['id'], field, origin, text) for field, origin, text in projection(record)])


def matches(connection, query: str) -> dict[str, list[dict]]:
    # Quote the whole input so operators and punctuation are always literal.
    phrase = '"' + query.replace('"', '""') + '"'
    rows = connection.execute('SELECT source_id, field, origin, text FROM search_projection WHERE search_projection MATCH ? ORDER BY rank', (phrase,))
    result = {}
    for row in rows:
        result.setdefault(row['source_id'], []).append(dict(field=row['field'], origin=row['origin'], text=row['text']))
    return result
