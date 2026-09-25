"""Synthetic disposable files exercise each persisted move state and crash window."""

import sqlite3
from pathlib import Path

import pytest

from refs import files, moves, resources, sources
from refs.catalog import connect
from refs.config import select
from refs.results import RefError


def prepare(initialized, tmp_path, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path, '--loc', 'Topic')['data']
    original = tmp_path/'download.pdf'
    original.write_bytes(b'synthetic completed download')
    settings = select(str(tmp_path/'config.toml'), str(tmp_path/'cat'))
    resource = resources.link(settings, source['id'], path=original)
    return settings, source, resource, original, tmp_path/'lib/Topic/download.pdf'


@pytest.mark.parametrize('point,state', [('staged','staged'), ('published_uncommitted','staged'), ('published','published'), ('recorded','recorded'), ('unlinked','recorded'), ('removed','removed')])
def test_states_and_resume(initialized, tmp_path, reference_path, monkeypatch, point, state):
    settings, source, resource, original, target = prepare(initialized,tmp_path,reference_path)
    def interrupt(at, row):
        if at == point:
            raise KeyboardInterrupt
    monkeypatch.setattr(moves, 'checkpoint', interrupt)
    with pytest.raises(KeyboardInterrupt):
        moves.move(settings, resource['id'], target)
    with connect(settings.catalog_path()) as c:
        row = dict(c.execute('SELECT * FROM file_operations').fetchone())
        assert row['state'] == state
    monkeypatch.setattr(moves, 'checkpoint', lambda *args: None)
    result = moves.move(settings, resource['id'], target)
    assert result['state'] == 'removed'
    assert not original.exists() and target.read_bytes() == b'synthetic completed download'
    assert sources.show(settings.catalog_path(), source['id'])['resources'][0]['id'] == resource['id']


@pytest.mark.parametrize('failure', ['destination', 'original', 'pointer', 'flush'])
def test_predelete_guards(initialized,tmp_path,reference_path,monkeypatch,failure):
    settings, source, resource, original, target = prepare(initialized,tmp_path,reference_path)
    def change(at, row):
        if at != 'recorded':
            return
        if failure == 'destination':
            target.write_bytes(b'changed destination')
        elif failure == 'original':
            original.write_bytes(b'changed original')
        elif failure == 'pointer':
            with connect(settings.catalog_path(),write=True) as c:
                c.execute("UPDATE resources SET relative='elsewhere.pdf' WHERE id=?",(resource['id'],))
        else:
            monkeypatch.setattr(moves,'flush',lambda *args: (_ for _ in ()).throw(OSError('flush failed')))
    monkeypatch.setattr(moves,'checkpoint',change)
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target)
    assert error.value.issue['code'] == 'move_incomplete'
    assert original.exists()
    with connect(settings.catalog_path()) as c:
        row=c.execute('SELECT state,last_state FROM file_operations').fetchone()
        assert tuple(row)==('failed','recorded')


def test_later_source_edit_does_not_block_delete(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target = prepare(initialized,tmp_path,reference_path)
    def edit(at,row):
        if at=='recorded':
            current=sources.show(settings.catalog_path(),source['id'])
            sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'loc':'Next','metadata.publisher':'New'}},current['revision'])
    monkeypatch.setattr(moves,'checkpoint',edit)
    assert moves.move(settings,resource['id'],target)['state']=='removed'
    assert not original.exists()
    assert sources.show(settings.catalog_path(),source['id'])['loc']=='Next'


def test_failed_state_retry_and_stale_registration(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    def fail(at,row):
        if at=='published':
            raise OSError('synthetic failure')
    monkeypatch.setattr(moves,'checkpoint',fail)
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target)
    assert error.value.issue['code'] == 'move_incomplete'
    assert original.exists()
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    assert moves.move(settings,resource['id'],target)['state']=='removed'


def test_occupied_equal_bytes_are_not_adopted(initialized,tmp_path,reference_path):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    target.parent.mkdir()
    target.write_bytes(original.read_bytes())
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target)
    assert error.value.issue['code'] == 'destination_exists'
    assert original.exists() and target.exists()


def test_nfc_collision_names(tmp_path):
    used=set()
    names=['2402.html']*3+['2311.html']*3+['2310.html']*2
    targets=[moves.preserved_target(tmp_path,name,used).name for name in names]
    assert targets==['2402.html','2402-b.html','2402-c.html','2311.html','2311-b.html','2311-c.html','2310.html','2310-b.html']
    assert moves.preserved_target(tmp_path,'Cafe\u0301.pdf',used).name=='Café.pdf'


def test_hashes_twice_and_stale_before_record(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    hashed=[]
    real_hash=files.hash_file
    def count(path):
        hashed.append(path)
        return real_hash(path)
    monkeypatch.setattr(files,'hash_file',count)
    moves.move(settings,resource['id'],target)
    assert hashed.count(original)==2 and hashed.count(target)==2


def test_stale_before_record_retains_original(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    def edit(at,row):
        if at=='published':
            current=sources.show(settings.catalog_path(),source['id'])
            sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'metadata.publisher':'Changed'}},current['revision'])
    monkeypatch.setattr(moves,'checkpoint',edit)
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target)
    assert error.value.issue['code'] == 'move_incomplete'
    assert original.exists() and target.exists()
    assert resources.resolve_path(settings,sources.show(settings.catalog_path(),source['id'])['resources'][0])==original


def test_stale_pre_record_retry_replans_one_operation(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    def fail(at,row):
        if at=='published':
            raise OSError('synthetic stop before record')
    monkeypatch.setattr(moves,'checkpoint',fail)
    with pytest.raises(RefError):
        moves.move(settings,resource['id'],target)
    with connect(settings.catalog_path()) as c:
        before=dict(c.execute('SELECT * FROM file_operations').fetchone())
    current=sources.show(settings.catalog_path(),source['id'])
    sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'metadata.publisher':'Changed'}},current['revision'])
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    result=moves.move(settings,resource['id'],target)
    with connect(settings.catalog_path()) as c:
        rows=[dict(row) for row in c.execute('SELECT * FROM file_operations')]
    assert result['state']=='removed' and len(rows)==1 and rows[0]['id']==before['id']
    assert rows[0]['source_revision']>before['source_revision']
    assert not original.exists() and target.read_bytes()==b'synthetic completed download'


def test_sqlite_failure_marks_move_failed_for_resume(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    record=moves.record_destination
    monkeypatch.setattr(moves,'record_destination',lambda *args: (_ for _ in ()).throw(sqlite3.OperationalError('synthetic database failure')))
    with pytest.raises(RefError) as caught:
        moves.move(settings,resource['id'],target)
    assert caught.value.issue['code']=='move_incomplete' and caught.value.exit_code==4
    with connect(settings.catalog_path()) as c:
        row=c.execute('SELECT state,last_state FROM file_operations').fetchone()
        assert tuple(row)==('failed','published')
    assert original.exists()
    monkeypatch.setattr(moves,'record_destination',record)
    assert moves.move(settings,resource['id'],target)['state']=='removed'
    assert not original.exists()


def test_unlink_refuses_resource_with_unfinished_move(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    monkeypatch.setattr(moves,'checkpoint',lambda at,row: (_ for _ in ()).throw(KeyboardInterrupt) if at=='staged' else None)
    with pytest.raises(KeyboardInterrupt):
        moves.move(settings,resource['id'],target)
    with connect(settings.catalog_path()) as c:
        operation=c.execute('SELECT id FROM file_operations').fetchone()[0]
    with pytest.raises(RefError) as caught:
        resources.unlink(settings,resource['id'],execute=True)
    assert caught.value.issue['details']['operation_id']==operation
    assert operation in str(caught.value) and original.exists()
    assert sources.show(settings.catalog_path(),source['id'])['resources'][0]['id']==resource['id']


@pytest.mark.parametrize('kind',['directory','symlink','escape'])
def test_unsafe_paths(initialized,tmp_path,reference_path,kind):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    if kind=='directory':
        original.unlink()
        original.mkdir()
    elif kind=='symlink':
        target.parent.symlink_to(tmp_path, target_is_directory=True)
    else:
        target=tmp_path/'outside.pdf'
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target)
    assert error.value.issue['code'] == {'directory':'unsafe_move_source','symlink':'unsafe_path','escape':'unsafe_path'}[kind]
    assert original.exists()


def test_source_changes_during_copy(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    real_hash=files.hash_file
    def change(path):
        digest=real_hash(path)
        if path==original:
            original.write_bytes(b'changed during copy')
        return digest
    monkeypatch.setattr(files,'hash_file',change)
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target)
    assert error.value.issue['code'] == 'move_incomplete'
    assert original.read_bytes()==b'changed during copy' and not target.exists()


def test_admission_names_existing_resource(initialized,tmp_path,reference_path):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    alias=tmp_path/'alias.pdf'
    alias.hardlink_to(original)
    for path in (original,alias):
        with pytest.raises(RefError) as error:
            moves.admit(settings,path)
        assert error.value.issue['code'] == 'resource_already_recorded'
        assert error.value.issue['details']['resource_id']==resource['id']
    assert original.exists()


def test_staged_retry_rejects_changed_destination(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    def interrupt(at,row):
        if at=='staged':
            raise KeyboardInterrupt
    monkeypatch.setattr(moves,'checkpoint',interrupt)
    with pytest.raises(KeyboardInterrupt):
        moves.move(settings,resource['id'],target)
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target.with_name('changed.pdf'))
    assert error.value.issue['code'] == 'move_conflict'
    assert original.exists()


def test_unknown_staging_file_is_never_deleted(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    def interrupt(at,row):
        if at=='staged':
            raise KeyboardInterrupt
    monkeypatch.setattr(moves,'checkpoint',interrupt)
    with pytest.raises(KeyboardInterrupt):
        moves.move(settings,resource['id'],target)
    with connect(settings.catalog_path()) as c:
        stage=Path(c.execute('SELECT staging_path FROM file_operations').fetchone()[0])
    outsider=tmp_path/'outsider'
    outsider.write_bytes(b'not ours')
    stage.unlink()
    stage.hardlink_to(outsider)
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    with pytest.raises(RefError) as error:
        moves.move(settings,resource['id'],target)
    assert error.value.issue['code'] == 'move_incomplete'
    assert stage.read_bytes()==b'not ours' and original.exists()


def test_unlink_preserves_move_history_and_file(initialized,tmp_path,reference_path):
    settings, source, resource, original, target=prepare(initialized,tmp_path,reference_path)
    moves.move(settings,resource['id'],target)
    resources.unlink(settings,resource['id'],execute=True)
    with connect(settings.catalog_path()) as c:
        row=c.execute('SELECT resource_id,state FROM file_operations').fetchone()
        assert tuple(row)==(resource['id'],'removed')
    assert target.exists() and not original.exists()
    with pytest.raises(RefError) as error:
        moves.move(settings,'missing',target.with_name('missing.pdf'))
    assert error.value.issue['code'] == 'resource_missing'
    assert target.exists()
