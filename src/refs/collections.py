"""Read-only views of imported collections and direct memberships."""

from pathlib import Path

from refs.catalog import connect
from refs.results import RefError


def resolve(connection, path: str) -> str:
    rows = connection.execute('SELECT id FROM collections WHERE path=?', (path,)).fetchall()
    if len(rows) != 1:
        raise RefError('collection_ambiguous' if rows else 'collection_missing',
                       'Use a unique imported collection path; inspect collection list', details={'path':path,'candidates':[row[0] for row in rows]})
    return rows[0][0]


def list_collections(catalog: Path) -> dict:
    with connect(catalog) as connection:
        items = [dict(row) for row in connection.execute("SELECT c.*, (SELECT count(*) FROM source_collections sc JOIN sources s ON sc.source_id=s.id WHERE sc.collection_id=c.id AND s.state='active') AS count FROM collections c ORDER BY c.path,c.library_uri,c.id")]
        return dict(items=items, catalog_revision=connection.execute('SELECT revision FROM catalog_meta').fetchone()[0])
