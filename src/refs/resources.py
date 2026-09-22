"""Resource associations and explicit local file opening."""

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from refs import files, sources
from refs.catalog import changed, connect
from refs.config import Settings
from refs.results import RefError


def inventory(connection, source_id=None) -> list[dict]:
    rows = connection.execute('SELECT * FROM resources'+(' WHERE source_id=?' if source_id else '')+' ORDER BY id', (source_id,) if source_id else ())
    result = []
    for row in rows:
        item = dict(row)
        item.pop('locator')
        copied_from = item.pop('copied_from_json')
        if copied_from:
            item['copied_from'] = json.loads(copied_from)
        result.append(item)
    return result


def locate(settings: Settings, *, path: Path | None = None, root: str | None = None, relative: str | None = None) -> dict:
    if (path is None) == (root is None) or root is not None and relative is None or path is not None and relative is not None:
        raise RefError('invalid_locator', 'Supply --path or both --root and --relative', 2)
    if root is not None:
        if root not in settings.roots:
            raise RefError('root_unavailable', 'Configure the named resource root before linking', details={'root':root})
        suffix = Path(relative or '')
        if suffix.is_absolute() or '..' in suffix.parts:
            raise RefError('unsafe_path', 'Use a relative path contained within the named root')
        base = settings.roots[root]
        resolved = (base/suffix).resolve()
        if not resolved.is_relative_to(base.resolve()):
            raise RefError('unsafe_path', 'Resource path escapes its named root')
        value = dict(path=None, root=root, relative=str(suffix))
    else:
        assert path is not None
        resolved = path.expanduser().resolve()
        value = dict(path=str(resolved), root=None, relative=None)
    if settings.library and resolved.is_relative_to(settings.library):
        value = dict(path=None, root='library', relative=str(resolved.relative_to(settings.library)))
    return value


def resolve_path(settings: Settings, resource: dict) -> Path:
    if resource['path'] is not None:
        return Path(resource['path'])
    root = settings.roots.get(resource['root'])
    if root is None:
        raise RefError('root_unavailable', 'Restore or configure the missing resource root', details={'root':resource['root']})
    target = (root/resource['relative']).resolve()
    if not target.is_relative_to(root.resolve()):
        raise RefError('unsafe_path', 'Resource path now escapes its configured root')
    return target


def touch_source(connection, source_id):
    connection.execute('UPDATE sources SET revision=revision+1,updated_at=? WHERE id=?', (datetime.now(UTC).isoformat(),source_id))
    changed(connection)


def link_in(connection, settings: Settings, reference: str, *, path=None, root=None, relative=None, label=None, media_type=None, dry_run=False) -> dict:
    source_id = sources.resolve(connection, reference)
    source = connection.execute('SELECT citation_key,state FROM sources WHERE id=?',(source_id,)).fetchone()
    if source['state'] != 'active':
        raise RefError('source_removed', 'Reactivate the source before adding resources')
    locator = locate(settings,path=path,root=root,relative=relative)
    encoded = json.dumps(locator,sort_keys=True)
    existing = connection.execute('SELECT id FROM resources WHERE source_id=? AND locator=?',(source_id,encoded)).fetchone()
    if existing:
        return next(item for item in inventory(connection,source_id) if item['id']==existing[0]) | dict(unchanged=True,citation_key=source['citation_key'])
    item = dict(id=str(uuid4()),source_id=source_id,revision=1,**locator,label=label,media_type=media_type,digest=None)
    if not dry_run:
        connection.execute('INSERT INTO resources (id,source_id,locator,path,root,relative,label,media_type) VALUES (?,?,?,?,?,?,?,?)', (item['id'],source_id,encoded,locator['path'],locator['root'],locator['relative'],label,media_type))
        touch_source(connection,source_id)
    return item | dict(dry_run=dry_run,citation_key=source['citation_key'],resolved_path=str(resolve_path(settings,item)))


def link(settings: Settings, reference: str, **options) -> dict:
    with connect(settings.catalog_path(),write=not options.get('dry_run',False)) as connection:
        return link_in(connection,settings,reference,**options)


def check_item(settings: Settings, item: dict, verify=False) -> dict:
    try:
        target = resolve_path(settings,item)
        status = 'available' if target.exists() else 'missing'
        if status == 'available' and verify and item['digest'] and target.is_file() and files.hash_file(target) != item['digest']:
            status = 'digest_changed'
        if 'conflicted copy' in target.name.lower() or 'sync-conflict' in target.name.lower():
            status = 'sync_conflict'
        return item | dict(resolved_path=str(target),status=status)
    except (RefError,OSError) as exc:
        return item | dict(status=exc.issue['code'] if isinstance(exc,RefError) else 'unavailable',message=str(exc))


def inspect_source(settings: Settings, reference: str) -> dict:
    result = sources.show(settings.catalog_path(),reference)
    result['resources'] = [check_item(settings,item) for item in result['resources']]
    return result


def check(settings: Settings, reference=None, *, verify=False) -> dict:
    with connect(settings.catalog_path()) as connection:
        source_id = sources.resolve(connection,reference) if reference else None
        items = inventory(connection,source_id)
    return {'items':[check_item(settings,item,verify) for item in items]}


def unlink(settings: Settings, resource_id: str, revision: int, *, execute=False) -> dict:
    with connect(settings.catalog_path(),write=execute) as connection:
        item = next((item for item in inventory(connection) if item['id']==resource_id),None)
        if item is None:
            raise RefError('resource_missing','Inspect the source and use an existing resource ID')
        if item['revision'] != revision:
            raise RefError('stale_revision','Reload the resource and use its current revision')
        key = connection.execute('SELECT citation_key FROM sources WHERE id=?',(item['source_id'],)).fetchone()[0]
        if execute:
            connection.execute('DELETE FROM resources WHERE id=?',(resource_id,))
            touch_source(connection,item['source_id'])
    return item | dict(dry_run=not execute,citation_key=key)


def launch(path: Path):
    subprocess.run(['open',str(path)],check=True)


def open_source(settings: Settings, reference: str, *, resource_id=None) -> dict:
    source = inspect_source(settings,reference)
    items = source['resources']
    if resource_id is None and len(items)>1:
        return dict(choices=items,citation_key=source['citation_key'])
    chosen = next((item for item in items if resource_id is None or item['id']==resource_id),None)
    if chosen is None or chosen['status'] != 'available':
        raise RefError('resource_unavailable','Inspect resources and select an available file')
    path = resolve_path(settings,chosen)
    try:
        launch(path)
    except (OSError,subprocess.CalledProcessError) as exc:
        raise RefError('open_failed','The external opener failed; inspect the file and open it manually',5,path=str(path)) from exc
    return dict(path=str(path),citation_key=source['citation_key'],resource_id=chosen['id'])


def import_links(connection, settings: Settings, source_id: str, proposals: list[str], origin: str, *, dry_run=False):
    items, warnings = [], []
    for expression in proposals:
        for value in expression.split(';'):
            try:
                parts = value.split(':')
                path = parts[1] if len(parts)==3 and parts[1].startswith('/') else value
                if ':' in path or '\\' in path or not path.strip():
                    raise RefError('unsupported_file_expression','Inspect the preserved file expression and link the file explicitly')
                target = Path(path).expanduser()
                if not target.is_absolute():
                    if not Path(origin).is_absolute():
                        raise RefError('unsupported_file_expression','Relative file paths require an absolute bibliography location')
                    target = Path(origin).parent/target
                items.append(link_in(connection,settings,source_id,path=target,dry_run=dry_run))
            except RefError as exc:
                warnings.append(exc.issue)
    return items,warnings
