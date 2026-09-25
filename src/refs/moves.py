"""One persisted copy/verify/record/delete protocol for intake and reorganization."""

import json
import os
import shutil
import sqlite3
import unicodedata
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from refs import files, naming, resources, sources
from refs import logging as action_log
from refs.catalog import connect
from refs.results import RefError

interrupted_report: ContextVar[dict | None] = ContextVar('interrupted_move_report',default=None)


def checkpoint(point, operation):
    """Test seam for process interruption at real protocol boundaries."""


def preserved_target(folder: Path, name: str, reserved: set) -> Path:
    name = unicodedata.normalize('NFC', name)
    candidate, index = folder/name, 0
    while candidate.exists() or candidate.is_symlink() or files.path_key(candidate) in reserved:
        index += 1
        candidate = folder/(Path(name).stem + naming.suffix(index+1) + Path(name).suffix)
    reserved.add(files.path_key(candidate))
    return candidate


def identity(path):
    return list(files.file_identity(path))


def safe_path(path: Path, base: Path | None = None):
    if base is not None and not path.is_relative_to(base):
        raise RefError('unsafe_path','Keep the destination inside the library')
    if any(part.is_symlink() for part in [path, *path.parents]):
        raise RefError('unsafe_path','Move paths cannot traverse symbolic links')


def flush(path, directory=False):
    descriptor = os.open(path, os.O_RDONLY | (os.O_DIRECTORY if directory else 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def log_state(row, state):
    action_log.log_mutation('resource.move', {'operation_id':row['id'],'resource_id':row['resource_id']},
                            {'state':row.get('state')}, {'state':state}, old_path=row['old_path'],
                            new_path=row['new_path'], digest=row.get('digest'),
                            resource_revision_before=row['resource_revision'],
                            resource_revision_after=row['resource_revision']+int(state in ('recorded','unlinked','removed')),
                            source_revision_before=row['source_revision'],
                            source_revision_after=row['source_revision']+int(state in ('recorded','unlinked','removed')))


def save(settings, row, **values):
    values['updated_at'] = datetime.now(UTC).isoformat()
    if 'state' in values and values['state'] != row['state'] and values['state'] != 'published':
        log_state(row, values['state'])
    with connect(settings.catalog_path(),write=True) as c:
        c.execute('UPDATE file_operations SET '+','.join(key+'=?' for key in values)+' WHERE id=?',(*values.values(),row['id']))
    row.update(values)


def verified(path, saved_identity, digest):
    return path.is_file() and not path.is_symlink() and identity(path)==json.loads(saved_identity) and files.hash_file(path)==digest


def pointer_matches(settings, row):
    with connect(settings.catalog_path()) as c:
        item = next((item for item in resources.inventory(c) if item['id']==row['resource_id']),None)
    return item is not None and files.path_key(resources.resolve_path(settings,item))==files.path_key(row['new_path'])


def create(settings, resource_id, target):
    with connect(settings.catalog_path()) as c:
        item=next((item for item in resources.inventory(c) if item['id']==resource_id),None)
        if item is None:
            raise RefError('resource_missing','Select a recorded resource')
        source=sources.record(c,item['source_id'])
    original=resources.resolve_path(settings,item)
    if settings.library is None or not settings.library.is_dir():
        raise RefError('library_unavailable','Restore the library before moving')
    safe_path(original)
    safe_path(target,settings.library)
    if not original.is_file():
        raise RefError('unsafe_move_source','Move only a completed regular file')
    if target.exists():
        raise RefError('destination_exists','Inspect the occupied destination; moves never overwrite')
    staging=settings.catalog_path()/'staging'
    safe_path(staging)
    operation_id = str(uuid4())
    action_log.log_mutation('resource.move', {'operation_id':operation_id,'resource_id':resource_id},
                            None, {'state':'staged'}, old_path=str(original), new_path=str(target), digest=None,
                            resource_revision_before=item['revision'], resource_revision_after=item['revision'],
                            source_revision_before=source['revision'], source_revision_after=source['revision'])
    staging.mkdir(exist_ok=True)
    if staging.stat().st_dev != settings.library.stat().st_dev:
        raise RefError('staging_volume_mismatch','Keep staging and library on the same volume')
    stage=staging/('move-'+str(uuid4()))
    stage.touch(exist_ok=False)
    now=datetime.now(UTC).isoformat()
    row=dict(id=operation_id,resource_id=resource_id,old_path=str(original),new_path=str(target),old_name=original.name,new_name=target.name,staging_path=str(stage),original_identity=json.dumps(identity(original)),staging_identity=json.dumps(identity(stage)),destination_identity=None,digest=None,source_revision=source['revision'],resource_revision=item['revision'],loc=source.get('loc'),state='staged',last_state=None,error=None,created_at=now,updated_at=now)
    with connect(settings.catalog_path(),write=True) as c:
        c.execute('INSERT INTO file_operations ('+','.join(row)+') VALUES ('+','.join('?' for _ in row)+')',tuple(row.values()))
    return row


def record_destination(settings,row):
    target=Path(row['new_path'])
    locator=resources.locate(settings,path=target)
    with connect(settings.catalog_path(),write=True) as c:
        item=next((item for item in resources.inventory(c) if item['id']==row['resource_id']),None)
        if item is None:
            raise RefError('resource_missing','Inspect the unfinished operation')
        source=sources.checked_record(c,item['source_id'],row['source_revision'])
        if item['revision'] != row['resource_revision'] or source.get('loc') != row['loc'] or source['state'] != 'active':
            raise RefError('stale_revision','Source placement or resource changed; inspect the move')
        origin={key:item[key] for key in ('path','root','relative')}
        log_state(row, 'recorded')
        c.execute('UPDATE resources SET locator=?,path=?,root=?,relative=?,digest=?,copied_from_json=?,revision=revision+1 WHERE id=?',
                  (json.dumps(locator,sort_keys=True),locator['path'],locator['root'],locator['relative'],row['digest'],json.dumps(origin),item['id']))
        resources.touch_source(c,source['id'])
        c.execute("UPDATE file_operations SET state='recorded',updated_at=? WHERE id=?",(datetime.now(UTC).isoformat(),row['id']))
    row['state']='recorded'


def replan_stale(settings, row):
    """Restart a pre-recorded move after catalog edits, retaining its operation ID."""
    if (row['last_state'] if row['state']=='failed' else row['state']) not in ('staged','published'):
        return
    with connect(settings.catalog_path()) as c:
        item=next((item for item in resources.inventory(c) if item['id']==row['resource_id']),None)
        if item is None:
            return
        source=sources.record(c,item['source_id'])
    if (item['revision'],source['revision'],source.get('loc')) == (row['resource_revision'],row['source_revision'],row['loc']):
        return
    if source['state']!='active' or not source.get('loc'):
        raise RefError('stale_revision','Source is not active and placed; inspect the move')
    original=resources.resolve_path(settings,item)
    if not original.is_file() or original.is_symlink():
        raise RefError('unsafe_move_source','Current resource is not a regular file')
    stage,target=Path(row['staging_path']),Path(row['new_path'])
    saved=json.loads(row['staging_identity'])
    for path in (target,stage):
        if path.exists() or path.is_symlink():
            if not path.is_file() or path.is_symlink() or identity(path)[:2]!=saved[:2]:
                raise RefError('move_conflict','Move copy changed; inspect the unfinished operation')
    # Unlink the destination first: it may share the staging inode.
    if target.exists():
        target.unlink()
    if stage.exists():
        stage.unlink()
    new_target=settings.library/source['loc']/row['new_name']
    safe_path(new_target,settings.library)
    if new_target.exists() or new_target.is_symlink():
        raise RefError('destination_exists','Inspect the occupied destination; moves never overwrite')
    new_stage=stage.with_name('move-'+str(uuid4()))
    new_stage.touch(exist_ok=False)
    save(settings,row,state='staged',last_state=None,error=None,old_path=str(original),
         new_path=str(new_target),old_name=original.name,staging_path=str(new_stage),
         original_identity=json.dumps(identity(original)),staging_identity=json.dumps(identity(new_stage)),
         destination_identity=None,digest=None,source_revision=source['revision'],
         resource_revision=item['revision'],loc=source['loc'])


def resume(settings,row):
    original,target,stage=(Path(row[key]) for key in ('old_path','new_path','staging_path'))
    publication_verified = False
    try:
        replan_stale(settings,row)
        if row['state']=='failed':
            save(settings,row,state=row['last_state'],error=None)
        original,target,stage=(Path(row[key]) for key in ('old_path','new_path','staging_path'))
        if row['state']=='staged':
            if target.exists() or target.is_symlink():
                if not row['digest'] or not verified(target,row['staging_identity'],row['digest']):
                    raise RefError('destination_exists','Occupied destination is not the recorded staged file')
            else:
                if identity(original)!=json.loads(row['original_identity']):
                    raise RefError('source_changed','Original changed; inspect the unfinished move')
                safe_path(stage)
                if not stage.is_file() or identity(stage)[:2]!=json.loads(row['staging_identity'])[:2]:
                    raise RefError('staging_changed','Inspect the staging file before retrying')
                if stage.stat().st_size:
                    previous=stage
                    stage=stage.with_name('move-'+str(uuid4()))
                    stage.touch(exist_ok=False)
                    save(settings,row,staging_path=str(stage),staging_identity=json.dumps(identity(stage)))
                    previous.unlink()
                with stage.open('wb') as outgoing, original.open('rb') as incoming:
                    shutil.copyfileobj(incoming,outgoing)
                    outgoing.flush()
                    os.fsync(outgoing.fileno())
                digest=files.hash_file(original)
                if identity(original)!=json.loads(row['original_identity']) or files.hash_file(stage)!=digest:
                    raise RefError('source_changed','Original changed during copying; keep it and inspect')
                save(settings,row,staging_identity=json.dumps(identity(stage)),digest=digest)
                checkpoint('staged',row)
                safe_path(target,settings.library)
                log_state(row, 'published')
                target.parent.mkdir(parents=True,exist_ok=True)
                os.link(stage,target)
                if files.hash_file(target)!=digest:
                    raise RefError('integrity_error','Published bytes differ; original retained')
                checkpoint('published_uncommitted',row)
            publication_verified = True
            save(settings,row,state='published',destination_identity=json.dumps(identity(target)))
            checkpoint('published',row)
        if row['state']=='published':
            if not publication_verified and not verified(target,row['destination_identity'],row['digest']):
                raise RefError('destination_changed','Published file changed; original retained')
            record_destination(settings,row)
            checkpoint('recorded',row)
        if stage.exists() and not stage.is_symlink() and identity(stage)[:2]==json.loads(row['staging_identity'])[:2]:
            stage.unlink()
        if row['state']=='recorded':
            if not verified(target,row['destination_identity'],row['digest']) or not pointer_matches(settings,row):
                raise RefError('move_conflict','Destination or resource pointer changed; original retained')
            if original.exists() or original.is_symlink():
                if not verified(original,row['original_identity'],row['digest']):
                    raise RefError('source_changed','Original changed; it was not deleted')
                flush(target)
                flush(target.parent,directory=True)
                log_state(row, 'unlinked')
                original.unlink()
                checkpoint('unlinked',row)
                row['state'] = 'unlinked'
            save(settings,row,state='removed',error=None)
            checkpoint('removed',row)
        return row
    except (OSError,sqlite3.Error,RefError) as exc:
        if isinstance(exc,RefError) and exc.issue['code'] == 'log_unwritable':
            raise
        save(settings,row,last_state='recorded' if row['state']=='unlinked' else row['state'],state='failed',error=str(exc))
        raise RefError('move_incomplete','Move incomplete; inspect the report and rerun the command',4,data=dict(moves=[report(row)],unlinked_paths=[]),details={'cause':str(exc)}) from exc


def report(row):
    return {key:row.get('id') if key=='operation_id' else row.get(key) for key in ('operation_id','resource_id','old_path','new_path','old_name','new_name','state','error')}


def move(settings, resource_id, target: Path):
    target=target.with_name(unicodedata.normalize("NFC",target.name))
    with files.file_lock(settings.catalog_path()):
        with connect(settings.catalog_path()) as c:
            previous=c.execute('SELECT * FROM file_operations WHERE resource_id=? ORDER BY created_at DESC LIMIT 1',(resource_id,)).fetchone()
        row=dict(previous) if previous else None
        if row and row['state']=='removed' and files.path_key(row['new_path'])!=files.path_key(target):
            row=None
        if row and (row['last_state'] if row['state']=='failed' else row['state']) not in ('recorded','removed') and files.path_key(row['new_path'])!=files.path_key(target):
            raise RefError('move_conflict','Requested destination differs from the unfinished move')
        if row is None:
            row=create(settings,resource_id,target)
        return report(resume(settings,row))


def admit(settings, path: Path):
    """Reject a new move of an already recorded file, including hard-link aliases."""
    with connect(settings.catalog_path()) as c:
        for item in resources.inventory(c):
            existing=resources.resolve_path(settings,item)
            if files.path_key(existing)==files.path_key(path) or existing.exists() and path.exists() and existing.samefile(path):
                raise RefError('resource_already_recorded',f"File is already resource {item['id']}; use reorg",details={'resource_id':item['id']})


def intake(settings, reference, path: Path, *, keep_name=False, dry_run=False, label=None, media_type=None):
    source=sources.show(settings.catalog_path(),reference)
    path=path.expanduser().absolute()
    with connect(settings.catalog_path()) as c:
        old=c.execute('SELECT o.* FROM file_operations o JOIN resources r ON r.id=o.resource_id WHERE r.source_id=? AND o.old_path=? ORDER BY o.created_at DESC LIMIT 1',(source['id'],str(path))).fetchone()
    if old and old['state']=='removed' and not path.exists():
        current=sources.show(settings.catalog_path(),source['id'])
        item=next(item for item in current['resources'] if item['id']==old['resource_id'])
        destination=resources.resolve_path(settings,item)
        return item | dict(citation_key=current['citation_key'],moved=True,destination=str(destination),
                           moves=[],unlinked_paths=[],warnings=[],**({'dry_run':True} if dry_run else {}))
    if old and old['state']!='removed':
        resource_id,target=old['resource_id'],Path(old['new_path'])
        plan=dict(path=str(path),destination=str(target),copied_from={'path':str(path)},warnings=[])
    else:
        admit(settings,path)
        plan=resources.plan_copy(settings,source,path,keep_name=keep_name,label=label)
        if plan.get('duplicate_resource_id'):
            return plan | dict(dry_run=dry_run,moved=False,moves=[],unlinked_paths=[])
        target=Path(plan['destination'])
        resource_id=None
    if dry_run:
        return plan | dict(dry_run=True,moved=True,citation_key=source['citation_key'],moves=[report(dict(old)) if old and resource_id else preview_move(resource_id,path,target)],unlinked_paths=[])
    if resource_id is None:
        if not source.get('loc'):
            sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'loc':resources.UNFILED}},source['revision'])
        resource_id=resources.link(settings,source['id'],path=path,label=label,media_type=media_type)['id']
    result=move(settings,resource_id,target)
    current=sources.show(settings.catalog_path(),source['id'])
    item=next(item for item in current['resources'] if item['id']==resource_id)
    return item | dict(citation_key=source['citation_key'],moved=True,destination=result['new_path'],moves=[result],unlinked_paths=[],warnings=plan['warnings'])


def selection(settings, reference=None, loc=None):
    from refs.models import normalize_loc

    if reference and loc is not None:
        raise RefError('invalid_invocation','Choose --source or --loc, not both',2)
    try:
        prefix=(normalize_loc(loc) or '').casefold()
    except ValueError as exc:
        raise RefError('invalid_loc',str(exc),2) from exc
    with connect(settings.catalog_path()) as c:
        source_id=sources.resolve(c,reference) if reference else None
        records={row['id']:dict(row) for row in c.execute('SELECT id,loc,state FROM sources')}
        items=resources.inventory(c)
        unfinished=[dict(row) for row in c.execute("SELECT * FROM file_operations WHERE state!='removed' ORDER BY created_at,id")]
    def selected(source, old_loc=None):
        value=(source.get('loc') or old_loc or '').casefold()
        return (source_id is None or source.get('id')==source_id) and (not prefix or value==prefix or value.startswith(prefix+'/'))
    by_resource={item['id']:item for item in items}
    pending=[row for row in unfinished if selected(records.get(by_resource.get(row['resource_id'],{}).get('source_id'),{}),row['loc'])]
    reserved={files.path_key(row['new_path']) for row in unfinished}
    busy={row['resource_id'] for row in unfinished}
    paths={item['id']:resources.resolve_path(settings,item) for item in items}
    by_path={}
    by_file={}
    for resource_id,path in paths.items():
        by_path.setdefault(files.path_key(path),set()).add(resource_id)
        try:
            stat=path.stat()
        except FileNotFoundError:
            continue
        by_file.setdefault((stat.st_dev,stat.st_ino),set()).add(resource_id)
    planned=[]
    for item in sorted(items,key=lambda item:(item['root']!='library',item['id'])):
        source=records[item['source_id']]
        if item['id'] in busy or source['state']!='active' or not source['loc'] or not selected(source):
            continue
        path=paths[item['id']]
        if item['root']=='library' and not resources.misplaced(settings,item,source['loc']):
            continue
        if settings.library is None or not settings.library.is_dir():
            raise RefError('library_unavailable','Restore the library before reorganizing')
        target=preserved_target(settings.library/source['loc'],path.name,reserved)
        entry=preview_move(item['id'],path,target)
        shared=set(by_path[files.path_key(path)])
        if path.exists():
            stat=path.stat()
            shared.update(by_file[(stat.st_dev,stat.st_ino)])
        if len(shared)>1:
            entry.update(state='shared',error='Shared by resources '+', '.join(sorted(shared)))
        planned.append(entry)
    return pending,planned


def reorg(settings, *, reference=None, loc=None, execute=False):
    pending,planned=selection(settings,reference,loc)
    proposed=[report(row) for row in pending]+planned
    result=dict(dry_run=not execute,moves=proposed,unlinked_paths=unlinked_paths(settings,proposed))
    if not execute:
        return result
    result['moves']=[]
    current=None
    failure=None
    try:
        for row in pending:
            current=report(row)
            with files.file_lock(settings.catalog_path()):
                result['moves'].append(report(resume(settings,row)))
            current=None
        # Finishing a recorded move can expose a later loc edit as a new mismatch.
        _,planned=selection(settings,reference,loc)
        for item in planned:
            current=item
            result['moves'].append(item if item['state']=='shared' else move(settings,item['resource_id'],Path(item['new_path'])))
            current=None
    except (RefError,OSError,sqlite3.Error,KeyboardInterrupt) as exc:
        failure=exc
    finally:
        if failure is not None:
            partial=(failure.data or {}).get('moves',[]) if isinstance(failure,RefError) else []
            result['moves'].extend(partial or ([current | dict(state='failed',error=str(failure))] if current else []))
    if isinstance(failure,RefError):
        raise RefError(failure.issue['code'],str(failure),failure.exit_code,data=result,details=failure.issue['details']) from failure
    if isinstance(failure,KeyboardInterrupt):
        setattr(failure,'data',result)
        interrupted_report.set(result)
        raise failure
    if failure is not None:
        raise RefError('move_incomplete',str(failure),4,data=result,details={'cause':str(failure)}) from failure
    return result


def unlinked_paths(settings, planned):
    if not planned:
        return []
    with connect(settings.catalog_path()) as c:
        known={str(resources.resolve_path(settings,item)) for item in resources.inventory(c)}
        known.update(row[0] for row in c.execute("SELECT old_path FROM file_operations WHERE state!='removed'"))
    known={files.path_key(path) for path in known}
    parents={Path(item['old_path']).parent for item in planned}
    parents={path for path in parents if not any(other!=path and path.is_relative_to(other) for other in parents)}
    found=set()
    for parent in parents:
        for folder, dirs, names in os.walk(parent,followlinks=False):
            base=Path(folder)
            dirs[:]=[name for name in dirs if not (base/name).is_symlink() and base/name not in (settings.library,settings.catalog_path())]
            for name in names:
                path=base/name
                if not path.is_symlink() and path.is_file() and files.path_key(path)!=files.path_key(settings.config) and files.path_key(path) not in known:
                    found.add(str(path))
    return sorted(found)


def preview_move(resource_id, original, target):
    return dict(operation_id=None,resource_id=resource_id,old_path=str(original),new_path=str(target),old_name=original.name,new_name=target.name,state='planned',error=None)
