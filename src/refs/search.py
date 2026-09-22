"""Application-owned read-only search boundary."""

from pathlib import Path

from refs import collections, naming, projects, sources
from refs.adapters.search_sqlite import matches
from refs.catalog import connect
from refs.results import RefError


def retrieve(catalog: Path, query: str | None = None, *, project: str | None = None, collection: str | None = None,
             limit: int = 50, offset: int = 0, sort: str = 'title', policy: dict | None = None) -> dict:
    if not 1 <= limit <= 1000 or offset < 0 or sort not in ('title', 'key'):
        raise RefError('invalid_query', 'Use limit 1–1000, nonnegative offset, and title or key sort', 2)
    query = query.strip() if query else query
    with connect(catalog) as connection:
        project_id = projects.resolve(connection, project)['id'] if project else None
        collection_id = collections.resolve(connection,collection) if collection else None
        lexical = matches(connection, query) if query and query.strip() else {}
        records = [sources.record(connection, row[0]) for row in connection.execute("SELECT id FROM sources WHERE state='active'")]
        items = []
        for record in records:
            if collection_id and not connection.execute('SELECT 1 FROM source_collections WHERE collection_id=? AND source_id=?', (collection_id,record['id'])).fetchone():
                continue
            if project_id and not connection.execute('SELECT 1 FROM project_sources WHERE project_id=? AND source_id=? AND cited=1', (project_id, record['id'])).fetchone():
                continue
            found, exact = list(lexical.get(record['id'], [])), False
            if query:
                if query == record['citation_key']:
                    found.insert(0, dict(field='citation_key', origin='catalog', text=query))
                    exact = True
                elif not any(char.isspace() for char in query) and record['citation_key'].startswith(query):
                    found.insert(0, dict(field='citation_key', origin='catalog', text=record['citation_key']))
                for field in ('DOI', 'ISBN', 'ISSN', 'PMID', 'PMCID'):
                    stored = record['metadata'].get(field)
                    if stored and identifier(field, str(stored)) == identifier(field, query):
                        found.insert(0, dict(field='metadata.' + field, origin='metadata', text=stored))
                        exact = True
                for scheme, stored in record.get('extensions', {}).get('identifiers', {}).items():
                    if query == stored:
                        found.insert(0, dict(field='extensions.identifiers.' + scheme, origin='metadata', text=stored))
                        exact = True
                if not found:
                    continue
            items.append(record | {'matches': found, 'exact_match': exact})
        items.sort(key=lambda item: (not item['exact_match'], ordering(item, sort, policy)))
        revision = connection.execute('SELECT revision FROM catalog_meta').fetchone()[0]
        return dict(items=items[offset:offset + limit], total=len(items), limit=limit, offset=offset, catalog_revision=revision)


def identifier(field: str, value: str) -> str:
    if field == 'DOI':
        return sources.doi_identity(value)
    return ''.join(char for char in value.casefold() if char.isalnum())


def ordering(record: dict, sort: str, policy: dict | None = None):
    if sort == 'key':
        return (record['citation_key'],)
    edition = record['metadata'].get('edition')
    year = naming.issued_year(record)
    return (naming.sort_title(record,policy), (False, edition) if isinstance(edition, int) else (True, 0),
            (False, int(year)) if year != 'ND' else (True, 0), record['citation_key'])
