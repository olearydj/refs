"""SQLite's derived lexical projection; original bytes are never indexed."""

import json

from refs import naming
from refs.models import IDENTIFIER_FIELDS, Metadata, normalize_arxiv, normalize_doi, person_name


def projection(record: dict):
    yield 'citation_key', 'catalog', record['citation_key']
    for name, value in record['metadata'].items():
        field = next((field for key, field in Metadata.model_fields.items() if (field.alias or key) == name), None)
        if isinstance(value, list) and field and 'Name' in str(field.annotation):
            for person in value:
                parts = ('given', 'dropping-particle', 'non-dropping-particle', 'family', 'suffix', 'literal')
                yield 'metadata.' + name, 'metadata', person_name(person, parts)
        elif name in ('title', 'abstract'):
            yield 'metadata.' + name, 'metadata', value
    for entry in record.get('context', []):
        yield 'context', entry['origin'], entry['text']
    for tag in record.get('legacy_tags', []):
        yield 'legacy_tags', 'import', tag


def refresh(connection, record: dict) -> None:
    # The FTS table cannot index a plain column, so a source's rows are found by rowid through search_rows.
    rows = [row[0] for row in connection.execute('SELECT rowid FROM search_rows WHERE source_id=?', (record['id'],))]
    if rows:
        connection.execute(f"DELETE FROM search_projection WHERE rowid IN ({','.join('?' * len(rows))})", rows)
        connection.execute('DELETE FROM search_rows WHERE source_id=?', (record['id'],))
    if record['state'] == 'active':
        for field, origin, text in projection(record):
            cursor = connection.execute('INSERT INTO search_projection (source_id, field, origin, text) VALUES (?, ?, ?, ?)',
                                        (record['id'], field, origin, text))
            connection.execute('INSERT INTO search_rows (rowid, source_id) VALUES (?, ?)', (cursor.lastrowid, record['id']))


def matches(connection, query: str) -> dict[str, list[dict]]:
    # Quote the whole input so operators and punctuation are always literal.
    phrase = '"' + query.replace('"', '""') + '"'
    rows = connection.execute('SELECT source_id, field, origin, text FROM search_projection WHERE search_projection MATCH ? ORDER BY rank', (phrase,))
    result = {}
    for row in rows:
        result.setdefault(row['source_id'], []).append(dict(field=row['field'], origin=row['origin'], text=row['text']))
    return result


def identifier(field: str, value: str) -> str:
    if field == 'DOI':
        return normalize_doi(value)
    return ''.join(char for char in value.casefold() if char.isalnum())


def exact_matches(record: dict, query: str) -> tuple[list[dict], bool]:
    fields = []
    exact = False
    key = record['citation_key']
    metadata = record['metadata']
    if query == key:
        fields.insert(0, dict(field='citation_key', origin='catalog', text=query))
        exact = True
    elif not any(char.isspace() for char in query) and key.startswith(query):
        fields.insert(0, dict(field='citation_key', origin='catalog', text=key))
    for field in (field for field in IDENTIFIER_FIELDS if field != 'URL'):
        stored = metadata.get(field)
        if stored and identifier(field, str(stored)) == identifier(field, query):
            fields.insert(0, dict(field='metadata.' + field, origin='metadata', text=stored))
            exact = True
    for scheme, stored in record.get('extensions', {}).get('identifiers', {}).items():
        if (normalize_arxiv(query) if scheme == 'arxiv' else query) == stored:
            fields.insert(0, dict(field='extensions.identifiers.' + scheme, origin='metadata', text=stored))
            exact = True
    return fields, exact


def ordering(record: dict, sort: str, policy: dict | None = None):
    if sort == 'key':
        return (record['citation_key'],)
    edition = record['metadata'].get('edition')
    year = naming.issued_year(record)
    return (naming.sort_title(record,policy), (False, edition) if isinstance(edition, int) else (True, 0),
            (False, int(year)) if year != 'ND' else (True, 0), record['citation_key'])


def page(connection, query: str | None, *, loc: str | None, project_id: str | None, collection_id: str | None,
         limit: int, offset: int, sort: str, policy: dict | None) -> tuple[list[dict], int]:
    clauses=["s.state='active'"]
    arguments=[]
    if project_id:
        clauses.append('EXISTS (SELECT 1 FROM project_sources ps WHERE ps.source_id=s.id AND ps.project_id=? AND ps.cited=1)')
        arguments.append(project_id)
    if collection_id:
        clauses.append('EXISTS (SELECT 1 FROM source_collections sc WHERE sc.source_id=s.id AND sc.collection_id=?)')
        arguments.append(collection_id)
    rows=connection.execute('SELECT s.id,s.revision,s.citation_key,s.loc,s.metadata_json,s.details_json FROM sources s WHERE '+ ' AND '.join(clauses), arguments)
    lexical=matches(connection,query) if query else {}
    found=[]
    for row in rows:
        if loc is not None and (row['loc'] or '').casefold()!=loc.casefold():
            continue
        metadata=json.loads(row['metadata_json'])
        record=json.loads(row['details_json']) | dict(id=row['id'],revision=row['revision'],citation_key=row['citation_key'],metadata=metadata)
        fields=list(lexical.get(row['id'],[]))
        exact=False
        if query:
            exact_fields, exact = exact_matches(record, query)
            fields = exact_fields + fields
            if not fields:
                continue
        found.append(dict(id=row['id'],revision=row['revision'],matches=fields,exact_match=exact,order=ordering(record,sort,policy)))
    found.sort(key=lambda item:(not item['exact_match'],item['order']))
    return [{key:value for key,value in item.items() if key!='order'} for item in found[offset:offset+limit]],len(found)
