"""Application-owned read-only search boundary."""

from pathlib import Path

from refs import collections, projects, sources
from refs.adapters.search_sqlite import identifier as identifier
from refs.adapters.search_sqlite import page
from refs.catalog import connect
from refs.models import normalize_loc
from refs.results import RefError


def retrieve(catalog: Path, query: str | None = None, *, loc: str | None = None, project: str | None = None, collection: str | None = None,
             limit: int = 50, offset: int = 0, sort: str = 'title', policy: dict | None = None) -> dict:
    if not 1 <= limit <= 1000 or offset < 0 or sort not in ('title', 'key'):
        raise RefError('invalid_query', 'Use limit 1–1000, nonnegative offset, and title or key sort', 2)
    try:
        loc = normalize_loc(loc)
    except ValueError as exc:
        raise RefError("invalid_loc", str(exc), 2) from exc
    query = query.strip() if query else query
    with connect(catalog) as connection:
        project_id = projects.resolve(connection, project)['id'] if project else None
        collection_id = collections.resolve(connection,collection) if collection else None
        selected,total=page(connection,query,loc=loc,project_id=project_id,collection_id=collection_id,
                            limit=limit,offset=offset,sort=sort,policy=policy)
        items=[sources.record(connection,item['id']) | {'matches':item['matches'],'exact_match':item['exact_match']} for item in selected]
        revision = connection.execute('SELECT revision FROM catalog_meta').fetchone()[0]
        return dict(items=items, total=total, limit=limit, offset=offset, catalog_revision=revision)
