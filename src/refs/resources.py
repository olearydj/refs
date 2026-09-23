"""Resource associations and explicit local file opening."""

import json
import re
import sqlite3
import subprocess
import unicodedata
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


PLACEMENT_KINDS = {
    'linked_unplaced': 'linked with no loc (untouched)',
    'linked_pending': 'linked with a loc (pending reorg)',
    'managed_mismatch': 'managed in the wrong folder',
    'unfinished': 'unfinished move',
    'unrecorded': 'in the library, not recorded',
}


def check(settings: Settings, reference=None, *, verify=False, kind=None) -> dict:
    if kind is not None and kind not in PLACEMENT_KINDS:
        raise RefError('invalid_kind','Choose '+', '.join(PLACEMENT_KINDS),2)
    with connect(settings.catalog_path()) as connection:
        source_id = sources.resolve(connection,reference) if reference else None
        all_items = inventory(connection)
        locs = {row['id']:row['loc'] for row in connection.execute('SELECT id,loc FROM sources')}
        operations = [dict(row) for row in connection.execute("SELECT * FROM file_operations WHERE state!='removed' ORDER BY created_at,id")]
    busy = {row['resource_id'] for row in operations}
    result, known = [], set()
    for item in all_items:
        checked = check_item(settings,item,verify)
        if checked.get('resolved_path'):
            known.add(unicodedata.normalize('NFC',checked['resolved_path']).casefold())
        if source_id and item['source_id']!=source_id or item['id'] in busy:
            continue
        loc = locs[item['source_id']]
        placement = None
        if item['root']!='library':
            placement = 'linked_pending' if loc else 'linked_unplaced'
        elif loc and unicodedata.normalize('NFC',str(Path(item['relative']).parent)).casefold()!=loc.casefold():
            placement = 'managed_mismatch'
        result.append(checked | dict(kind=placement))
    for row in operations:
        item = next((item for item in all_items if item['id']==row['resource_id']),None)
        known.add(unicodedata.normalize('NFC',row['new_path']).casefold())
        if source_id and (item is None or item['source_id']!=source_id):
            continue
        result.append(dict(kind='unfinished',id=row['resource_id'],operation_id=row['id'],resolved_path=row['old_path'],old_path=row['old_path'],new_path=row['new_path'],state=row['state'],error=row['error'],status='unfinished'))
    if source_id is None and settings.library and settings.library.is_dir():
        for path in sorted(settings.library.rglob('*')):
            if not path.is_symlink() and path.is_file() and unicodedata.normalize('NFC',str(path)).casefold() not in known:
                result.append(dict(kind='unrecorded',resolved_path=str(path),status='available',hint='Use resource add SOURCE --path on this file to record it'))
    return {'items':[item for item in result if kind is None or item['kind']==kind]}



def unlink(settings: Settings, resource_id: str, *, execute=False) -> dict:
    with connect(settings.catalog_path(),write=execute) as connection:
        item = next((item for item in inventory(connection) if item['id']==resource_id),None)
        if item is None:
            return dict(id=resource_id, unchanged=True, dry_run=not execute)
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


def register_copy(settings: Settings, source: dict, target: Path, digest: str, origin: dict, existing: dict | None, *, label=None, media_type=None) -> dict:
    locator = locate(settings,path=target)
    encoded = json.dumps(locator,sort_keys=True)
    with connect(settings.catalog_path(),write=True) as connection:
        current = sources.checked_record(connection,source['id'],source['revision'])
        if current['state'] != 'active':
            raise RefError('source_removed','Source was removed during copying; inspect the finished copy')
        if existing:
            changed_rows = connection.execute('UPDATE resources SET locator=?,path=?,root=?,relative=?,digest=?,copied_from_json=?,revision=revision+1 WHERE id=? AND revision=?',
                               (encoded,locator['path'],locator['root'],locator['relative'],digest,json.dumps(origin),existing['id'],existing['revision'])).rowcount
            if changed_rows != 1:
                raise RefError('stale_revision','Resource changed during copying; inspect the finished copy')
            resource_id = existing['id']
        else:
            resource_id = str(uuid4())
            connection.execute('INSERT INTO resources (id,source_id,locator,path,root,relative,label,media_type,digest,copied_from_json) VALUES (?,?,?,?,?,?,?,?,?,?)',
                               (resource_id,source['id'],encoded,locator['path'],locator['root'],locator['relative'],label,media_type,digest,json.dumps(origin)))
        touch_source(connection,source['id'])
        return next(item for item in inventory(connection,source['id']) if item['id']==resource_id)


def copy(settings: Settings, reference: str, path: Path, *, resource_id=None, keep_name=False, dry_run=False, label=None, media_type=None) -> dict:
    source = sources.show(settings.catalog_path(),reference)
    plan = plan_copy(settings,source,path,keep_name=keep_name,check_duplicates=resource_id is None,label=label)
    if plan.get('duplicate_resource_id'):
        return plan | dict(dry_run=dry_run,copied=False)
    source_path, target = Path(plan['path']), Path(plan['destination'])
    origin = plan['copied_from']
    existing = next((item for item in source['resources'] if item['id']==resource_id),None) if resource_id else next((item for item in source['resources'] if all(item.get(key)==value for key,value in origin.items())),None)
    if resource_id and (existing is None or any(existing.get(key)!=value for key,value in origin.items())):
        raise RefError('resource_conflict','Select the resource that records the original copy source')
    if dry_run:
        return plan
    if not source.get('loc'):
        source = sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'loc':'Unfiled'}},source['revision'])
    folder = target.parent
    warnings = plan['warnings']
    published = False
    try:
        with files.file_lock(settings.catalog_path()):
            folder.mkdir(parents=True,exist_ok=True)
            with files.verified_copy(settings.catalog_path(),source_path,target) as digest:
                published = True
                registered = register_copy(settings,source,target,digest,origin,existing,label=label,media_type=media_type)
        return registered | dict(citation_key=source['citation_key'],resolved_path=str(target),destination=str(target),copied=True,warnings=warnings)
    except (OSError,sqlite3.Error,RefError) as exc:
        if published:
            raise RefError('copy_published_unregistered','Finished copy remains unregistered; inspect it and link it explicitly',4,path=str(target),details={'cause':str(exc)},data=dict(source_id=source['id'],resource_id=existing['id'] if existing else None,original=str(source_path),destination=str(target))) from exc
        if isinstance(exc,RefError):
            raise
        raise RefError('copy_failed','Copy failed; inspect the original and retry after correcting the cause',5,path=str(source_path),details={'cause':str(exc)}) from exc


def plan_copy(settings: Settings, source: dict, path: Path, *, keep_name=False, check_duplicates=False, label=None) -> dict:
    from refs import naming

    expanded = path.expanduser()
    source_path = expanded.parent.resolve()/expanded.name
    if source_path.is_symlink() or not source_path.is_file():
        raise RefError('unsafe_copy_source','Copy a completed regular file without symlink traversal, or link it in place')
    library = settings.library
    if library is None or not library.is_dir():
        raise RefError('library_unavailable','Restore the configured library before copying; the original remains untouched')
    if source.get('state', 'active') != 'active':
        raise RefError('source_removed','Reactivate the source before copying')
    origin = locate(settings,path=source_path)
    if settings.catalog_path().stat().st_dev != library.stat().st_dev:
        raise RefError('staging_volume_mismatch','Keep catalog staging and the library on the same volume')
    name = source_path.name if keep_name else naming.filename(source,source_path.name,label)
    warnings = []
    if not keep_name and (naming.issued_year(source)=='ND' or not re.search(r'[^\W_]+',naming.short_title(source))):
        warnings.append(dict(code='filename_unavailable',message='Conventional filename unavailable; keeping the original name',path=str(source_path),details={},retryable=False))
    folder = library/(source.get('loc') or 'Unfiled')
    if any(parent.is_symlink() for parent in [folder,*folder.parents]) or not folder.resolve().is_relative_to(library) or folder.exists() and not folder.is_dir():
        raise RefError('unsafe_path','Inspect the library Unfiled path before copying')
    target = folder/name
    if label and (target.exists() or target.is_symlink()):
        raise RefError('destination_exists','Inspect the existing destination; copy never overwrites or adopts it',path=str(target))
    if check_duplicates:
        digest = files.hash_file(source_path)
        for item in source.get('resources',[]):
            try:
                existing_path = resolve_path(settings,item)
                same = existing_path.is_file() and files.hash_file(existing_path)==digest
            except (OSError,RefError):
                continue
            if same:
                notice = dict(code='duplicate_attachment',message=f"Same file content already attached as resource {item['id']} ({existing_path}); no copy made",path=str(source_path),details={'resource_id':item['id'],'path':str(existing_path)},retryable=False)
                return dict(citation_key=source['citation_key'],path=str(source_path),duplicate_resource_id=item['id'],warnings=[notice])
    if target.exists() or target.is_symlink():
        raise RefError('destination_exists','Inspect the existing destination; copy never overwrites or adopts it',path=str(target))
    preview = dict(dry_run=True,citation_key=source['citation_key'],path=str(source_path),destination=str(target),copied_from=origin,warnings=warnings)
    return preview


def capture_file(settings: Settings, data: dict, path: Path, *, linked=False, moving=False, keep_name=False, dry_run=False) -> tuple[dict, dict]:
    if dry_run:
        source = data.get('record',data) | ({'loc':data['loc']} if data.get('loc') else {})
        if moving:
            from refs.moves import admit
            admit(settings,path)
        proposal = locate(settings,path=path) if linked else plan_copy(settings,source,path,keep_name=keep_name)
        proposal['moved'] = moving
        if moving:
            from refs.moves import preview_move
            proposal.update(moves=[preview_move(None,Path(proposal['path']),Path(proposal['destination']))],unlinked_paths=[])
        return data | {'resources':[proposal]} | {key:proposal[key] for key in ('moves','unlinked_paths') if key in proposal}, proposal
    try:
        if moving:
            from refs.moves import intake
            resource = intake(settings,data['id'],path,keep_name=keep_name)
        else:
            resource = link(settings,data['id'],path=path)
        if not linked and not moving:
            resource = copy(settings,data['id'],path,resource_id=resource['id'],keep_name=keep_name)
        current = inspect_source(settings,data['id'])
        return current | dict(outcome=data['outcome'],warnings=data.get('warnings',[])+resource.get('warnings',[])) | {key:resource[key] for key in ('moves','unlinked_paths') if key in resource}, resource
    except (RefError,OSError) as exc:
        current = inspect_source(settings,data['id'])
        details = dict(cause=str(exc),original=str(path))
        if isinstance(exc,RefError) and exc.data:
            details.update(exc.data)
        raise RefError('file_action_incomplete','Metadata was saved; inspect the resource and retry resource add with the same intake option',4,details=details,data=current | dict(outcome='needs_attention') | ({key:exc.data[key] for key in ('moves','unlinked_paths') if key in exc.data} if isinstance(exc,RefError) and exc.data else {})) from exc


def zotero_attachment(connection, settings, source_id: str, item: dict, manifest: dict, *, dry_run=False) -> dict:
    """Resolve original Zotero locators; never use the extraction directory."""
    data = item['data']
    mode = data.get('linkMode')
    expression = data.get('path', '')
    if mode in ('imported_file', 'imported_url'):
        base = Path(manifest['data_directory'])/'storage'/item['key']
        suffix = Path(data.get('filename') or '')
        if not suffix.name or suffix.is_absolute() or '..' in suffix.parts:
            raise RefError('invalid_attachment_path', 'Inspect the stored attachment filename')
        path = base/suffix
    elif mode == 'linked_file':
        if expression.startswith('attachments:'):
            if not manifest.get('base_path'):
                raise RefError('attachment_base_missing', 'Supply the original linked-attachment base path')
            suffix = Path(expression.removeprefix('attachments:'))
            if suffix.is_absolute() or '..' in suffix.parts:
                raise RefError('invalid_attachment_path', 'Inspect the base-relative attachment path')
            path = Path(manifest['base_path'])/suffix
        else:
            path = Path(expression)
            if not path.is_absolute():
                raise RefError('invalid_attachment_path', 'Supply an absolute or base-relative attachment path')
    else:
        raise RefError('unsupported_attachment', 'Inspect the attachment link mode')
    locator = locate(settings, path=path) if settings else dict(path=str(path), root=None, relative=None)
    identity = json.dumps(locator, sort_keys=True)
    old = connection.execute('SELECT id FROM resources WHERE source_id=? AND locator=?', (source_id, identity)).fetchone()
    if not dry_run and not old:
        connection.execute('INSERT INTO resources (id,source_id,locator,path,root,relative,label,media_type) VALUES (?,?,?,?,?,?,?,?)',
                           (str(uuid4()), source_id, identity, locator['path'], locator['root'], locator['relative'], data.get('title'), data.get('contentType')))
        touch_source(connection, source_id)
    return dict(**locator, status='available' if path.is_file() else 'missing', unchanged=bool(old))
