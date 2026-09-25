import json
import sqlite3
import sys

import pytest

from refs import cli, moves, resources
from refs.catalog import connect
from refs.config import select
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


def test_preview_success_and_extras(initialized,human,tmp_path,reference_path):
    settings,path,extra=prepare(initialized,tmp_path,reference_path)
    occupied=tmp_path/'lib/Placed/file.pdf'
    occupied.parent.mkdir()
    occupied.write_bytes(b'keep me')
    preview=moves.reorg(settings)
    entry=preview['moves'][0]
    assert set(entry)=={'operation_id','resource_id','old_path','new_path','old_name','new_name','state','error'}
    assert entry['operation_id'] is None and entry['new_name']=='file-b.pdf'
    assert preview['unlinked_paths']==[str(extra)]
    text=human('reorg')
    assert f'\t{path}\t' in text and f'\t{occupied.with_name("file-b.pdf")}\trenamed' in text
    assert f'\t{extra}\tunlinked' in text
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
    problem=capsys.readouterr().err
    assert f'\t{path}\t' in problem and f"\t{entry['new_path']}\t" in problem
    emit('reorg',error=error,json_output=True)
    assert json.loads(capsys.readouterr().out)['data']['moves'][0]['operation_id']==entry['operation_id']
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    result=moves.reorg(settings,execute=True)
    assert result['moves'][0]['operation_id']==entry['operation_id'] and not path.exists()


@pytest.mark.parametrize('failure',[OSError,sqlite3.OperationalError,KeyboardInterrupt])
def test_reorg_reports_completed_pairs_when_third_move_fails(initialized,tmp_path,reference_path,monkeypatch,capsys,failure):
    settings,path,extra=prepare(initialized,tmp_path,reference_path)
    with connect(settings.catalog_path()) as c:
        source_id=c.execute('SELECT id FROM sources').fetchone()[0]
    for index in range(4):
        original=path.parent/f'file-{index}.pdf'
        original.write_bytes(f'synthetic {index}'.encode())
        resources.link(settings,source_id,path=original)
    create=moves.create
    calls=0
    def fail_third(*args):
        nonlocal calls
        calls+=1
        if calls==3:
            raise failure('synthetic third move failure')
        return create(*args)
    monkeypatch.setattr(moves,'create',fail_third)
    with pytest.raises(KeyboardInterrupt if failure is KeyboardInterrupt else RefError) as caught:
        moves.reorg(settings,execute=True)
    error=caught.value
    if failure is not KeyboardInterrupt:
        assert error.exit_code==4
    assert len(error.data['moves'])==3
    assert [row['state'] for row in error.data['moves']]==['removed','removed','failed']
    assert all(row['old_path'] and row['new_path'] for row in error.data['moves'])
    assert 'synthetic third move failure' in error.data['moves'][2]['error']
    if failure is not KeyboardInterrupt:
        emit('reorg',error=error,json_output=True)
        envelope=json.loads(capsys.readouterr().out)
        assert envelope['status']=='partial'
        assert envelope['data']['moves']==error.data['moves']
    with connect(settings.catalog_path()) as c:
        assert c.execute('SELECT count(*) FROM file_operations').fetchone()[0]==2
    assert sum(not (path.parent/name).exists() for name in ['file.pdf',*[f'file-{i}.pdf' for i in range(4)]])==2


def test_interrupted_reorg_cli_emits_partial_report_and_exits_130(initialized,tmp_path,reference_path,monkeypatch,capsys):
    settings,path,extra=prepare(initialized,tmp_path,reference_path)
    with connect(settings.catalog_path()) as c:
        source_id=c.execute('SELECT id FROM sources').fetchone()[0]
    for index in range(4):
        original=path.parent/f'file-{index}.pdf'
        original.write_bytes(f'synthetic {index}'.encode())
        resources.link(settings,source_id,path=original)
    create=moves.create
    calls=0
    def interrupt_third(*args):
        nonlocal calls
        calls+=1
        if calls==3:
            raise KeyboardInterrupt('synthetic third move interruption')
        return create(*args)
    monkeypatch.setattr(moves,'create',interrupt_third)
    monkeypatch.setattr(sys,'argv',['refs','--json','--no-project-config','--config',str(settings.config),
                                   '--catalog',str(settings.catalog_path()),'reorg','--execute'])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code==130
    envelope=json.loads(capsys.readouterr().out)
    assert envelope['command']=='reorg' and envelope['status']=='partial'
    assert [row['state'] for row in envelope['data']['moves']]==['removed','removed','failed']
    assert all(row['old_path'] and row['new_path'] for row in envelope['data']['moves'])
    assert 'synthetic third move interruption' in envelope['data']['moves'][2]['error']
    assert envelope['data']['unlinked_paths']==[str(extra)]
    assert moves.interrupted_report.get() is None
    moves.interrupted_report.set({'moves':[{'error':'stale report'}]})
    monkeypatch.setattr(cli,'app',lambda **kwargs:130)
    cli.main()
    assert capsys.readouterr().out=='' and moves.interrupted_report.get() is None


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
