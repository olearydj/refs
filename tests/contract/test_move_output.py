import json

import pytest

from refs import moves, resources
from refs.config import select
from refs.render import render_text
from refs.results import RefError, emit


def prepare(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path,'--loc','Placed')['data']
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    tree=tmp_path/'tree'
    tree.mkdir()
    path=tree/'file.pdf'
    path.write_bytes(b'synthetic')
    resources.link(settings,source['id'],path=path)
    extra=tree/'extra.txt'
    extra.write_bytes(b'untouched')
    return settings,path,extra


def test_preview_success_and_extras(initialized,tmp_path,reference_path):
    settings,path,extra=prepare(initialized,tmp_path,reference_path)
    occupied=tmp_path/'lib/Placed/file.pdf'
    occupied.parent.mkdir()
    occupied.write_bytes(b'keep me')
    preview=moves.reorg(settings)
    entry=preview['moves'][0]
    assert set(entry)=={'operation_id','resource_id','old_path','new_path','old_name','new_name','state','error'}
    assert entry['operation_id'] is None and entry['new_name']=='file-b.pdf'
    assert preview['unlinked_paths']==[str(extra)]
    text=render_text('reorg',preview,[])
    assert f'{path} -> {occupied.with_name("file-b.pdf")}' in text
    assert f'Left untouched (not linked): {extra}' in text
    result=moves.reorg(settings,execute=True)
    assert result['moves'][0]['operation_id'] and result['moves'][0]['state']=='removed'
    assert result['unlinked_paths']==[str(extra)] and extra.read_bytes()==b'untouched'
    assert occupied.read_bytes()==b'keep me'


def test_partial_and_resumed_report(initialized,tmp_path,reference_path,monkeypatch,capsys):
    settings,path,extra=prepare(initialized,tmp_path,reference_path)
    def fail(point,row):
        if point=='recorded':
            raise OSError('synthetic interruption')
    monkeypatch.setattr(moves,'checkpoint',fail)
    with pytest.raises(RefError) as caught:
        moves.reorg(settings,execute=True)
    error=caught.value
    entry=error.data['moves'][0]
    assert entry['state']=='failed' and entry['error']=='synthetic interruption'
    assert error.data['unlinked_paths']==[str(extra)] and path.exists()
    emit('reorg',error=error)
    assert f"{path} -> {entry['new_path']}" in capsys.readouterr().err
    emit('reorg',error=error,json_output=True)
    assert json.loads(capsys.readouterr().out)['data']['moves'][0]['operation_id']==entry['operation_id']
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    result=moves.reorg(settings,execute=True)
    assert result['moves'][0]['operation_id']==entry['operation_id'] and not path.exists()


def test_intake_preview_and_result_use_move_shape(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    path=tmp_path/'download.pdf'
    path.write_bytes(b'synthetic')
    preview=initialized('resource','add',source['id'],'--path',path,'--move','--dry-run')['data']
    assert preview['moves'][0]['operation_id'] is None and preview['unlinked_paths']==[]
    added=initialized('add','--format','refs','--input',reference_path,'--file',path)['data']
    assert added['moves'][0]['state']=='removed'
    assert added['moves'][0]['resource_id']==added['resources'][0]['id']


def test_staging_cleanup_failure_does_not_follow_original_deletion(initialized,tmp_path,reference_path,monkeypatch):
    from pathlib import Path
    settings,path,extra=prepare(initialized,tmp_path,reference_path)
    unlink=Path.unlink
    def refuse_stage(self,*args,**kwargs):
        if self.parent==settings.catalog_path()/'staging':
            raise PermissionError('synthetic staging permission failure')
        return unlink(self,*args,**kwargs)
    monkeypatch.setattr(Path,'unlink',refuse_stage)
    with pytest.raises(RefError) as caught:
        moves.reorg(settings,execute=True)
    assert caught.value.data['moves'][0]['state']=='failed' and path.exists()
    monkeypatch.setattr(Path,'unlink',unlink)
    assert moves.reorg(settings,execute=True)['moves'][0]['state']=='removed'


def test_untouched_scan_matches_nfd_disk_to_nfc_catalog(initialized,tmp_path,reference_path):
    import unicodedata

    from refs.catalog import connect
    settings,path,extra=prepare(initialized,tmp_path,reference_path)
    nfd=path.parent/unicodedata.normalize('NFD','Büttner - Training.pdf')
    nfd.write_bytes(b'synthetic real-shaped filename')
    source=initialized('show','smith-2024-learningPython')['data']
    resource=resources.link(settings,source['id'],path=nfd)
    nfc=unicodedata.normalize('NFC',str(nfd))
    with connect(settings.catalog_path(),write=True) as c:
        c.execute('UPDATE resources SET path=? WHERE id=?',(nfc,resource['id']))
    assert moves.unlinked_paths(settings,[dict(old_path=str(path))])==[str(extra)]
