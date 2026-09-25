"""Reorg previews and moves only synthetic resources in a temporary home."""
import json
from pathlib import Path

import pytest

from refs import files, moves, resources, sources
from refs.catalog import connect
from refs.config import select


def setup(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path,'--loc','Papers/Topic')['data']
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    return settings,source


def test_path_key_and_misplacement_agree_for_check_and_reorg(initialized,tmp_path,reference_path):
    settings, source = setup(initialized,tmp_path,reference_path)
    folder = tmp_path / 'lib/Papers/Topic'
    folder.mkdir(parents=True)
    placed = folder / 'cafe\u0301.pdf'
    placed.write_bytes(b'placed')
    linked = resources.link(settings,source['id'],path=placed)
    assert files.path_key(placed) == files.path_key(folder / 'caf\u00e9.pdf')
    assert initialized('resource','check','--kind','managed_mismatch')['data']['items'] == []
    assert initialized('reorg','--source',source['id'])['data']['moves'] == []
    wrong = tmp_path / 'lib/Wrong/other.pdf'
    wrong.parent.mkdir()
    wrong.write_bytes(b'wrong')
    misplaced = resources.link(settings,source['id'],path=wrong)
    checked = initialized('resource','check','--kind','managed_mismatch')['data']['items']
    planned = initialized('reorg','--source',source['id'])['data']['moves']
    assert [item['id'] for item in checked] == [misplaced['id']]
    assert [item['resource_id'] for item in planned] == [misplaced['id']]
    assert linked['id'] != misplaced['id']


def test_preview_execute_noop_and_filters(initialized,tmp_path,reference_path):
    settings,source=setup(initialized,tmp_path,reference_path)
    path=tmp_path/'linked.pdf'
    path.write_bytes(b'synthetic')
    linked=resources.link(settings,source['id'],path=path)
    wrong=tmp_path/'lib/Wrong/managed.pdf'
    wrong.parent.mkdir()
    wrong.write_bytes(b'managed')
    managed=resources.link(settings,source['id'],path=wrong)
    database=(tmp_path/'cat/catalog.sqlite').read_bytes()
    preview=initialized('reorg','--loc','papers')['data']
    assert [item['resource_id'] for item in preview['moves']]==[managed['id'],linked['id']]
    assert all(item['operation_id'] is None for item in preview['moves'])
    assert path.exists() and wrong.exists() and database==(tmp_path/'cat/catalog.sqlite').read_bytes()
    assert initialized('reorg','--loc','Paper')['data']['moves']==[]
    initialized('reorg','--loc','Papers','--source',source['id'],expected=2)
    result=initialized('reorg','--source',source['id'],'--execute')['data']
    assert len(result['moves'])==2 and all(item['state']=='removed' for item in result['moves'])
    assert not path.exists() and not wrong.exists()
    assert initialized('reorg','--execute')['data']['moves']==[]
    assert {r['id'] for r in sources.show(settings.catalog_path(),source['id'])['resources']}=={managed['id'],linked['id']}


@pytest.mark.parametrize('point',['published_uncommitted','recorded'])
def test_reorg_retry_finishes_before_new_moves(initialized,tmp_path,reference_path,monkeypatch,point):
    settings,source=setup(initialized,tmp_path,reference_path)
    path=tmp_path/'first.pdf'
    path.write_bytes(b'synthetic')
    resource=resources.link(settings,source['id'],path=path)
    def kill(at,row):
        if at==point:
            raise KeyboardInterrupt
    monkeypatch.setattr(moves,'checkpoint',kill)
    with pytest.raises(KeyboardInterrupt):
        moves.reorg(settings,execute=True)
    other=tmp_path/'other.json'
    other.write_text(json.dumps({'schema_version':'1.0','citation_key':'other','loc':'Papers','metadata':{'title':'Other'}}))
    second=initialized('add','--format','refs','--input',other)['data']
    extra=tmp_path/'extra.pdf'
    extra.write_bytes(b'other')
    resources.link(settings,second['id'],path=extra)
    seen=[]
    monkeypatch.setattr(moves,'checkpoint',lambda at,row:seen.append((at,row['resource_id'])))
    result=moves.reorg(settings,execute=True)
    assert result['moves'][0]['resource_id']==resource['id']
    assert seen[0][1]==resource['id']
    assert not path.exists() and not extra.exists()
    assert moves.reorg(settings,execute=True)['moves']==[]


def test_empty_loc_skips_new_work_but_resumes_recorded(initialized,tmp_path,reference_path,monkeypatch):
    settings,source=setup(initialized,tmp_path,reference_path)
    path=tmp_path/'file.pdf'
    path.write_bytes(b'synthetic')
    resource=resources.link(settings,source['id'],path=path)
    def kill(point,row):
        if point=='recorded':
            raise KeyboardInterrupt
    monkeypatch.setattr(moves,'checkpoint',kill)
    with pytest.raises(KeyboardInterrupt):
        moves.reorg(settings,execute=True)
    current=sources.show(settings.catalog_path(),source['id'])
    sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','clear':['loc']},current['revision'])
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    result=moves.reorg(settings,loc='Papers',execute=True)
    assert result['moves'][0]['resource_id']==resource['id'] and not path.exists()
    extra=tmp_path/'ignored.pdf'
    extra.write_bytes(b'untouched')
    resources.link(settings,source['id'],path=extra)
    assert moves.reorg(settings,execute=True)['moves']==[] and extra.exists()


def test_reorg_collision_suffixes_and_casefold_placement(initialized,tmp_path,reference_path):
    settings,source=setup(initialized,tmp_path,reference_path)
    for folder in ['a','b','c']:
        path=tmp_path/folder/'same.pdf'
        path.parent.mkdir()
        path.write_bytes(folder.encode())
        resources.link(settings,source['id'],path=path)
    result=moves.reorg(settings,execute=True)
    assert {Path(item['new_path']).name for item in result['moves']}=={'same.pdf','same-b.pdf','same-c.pdf'}
    current=sources.show(settings.catalog_path(),source['id'])
    sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'loc':'papers/topic'}},current['revision'])
    assert moves.reorg(settings)['moves']==[]
    with connect(settings.catalog_path()) as c:
        assert c.execute('SELECT count(*) FROM file_operations').fetchone()[0]==3


@pytest.mark.parametrize('hardlink',[False,True])
def test_reorg_reports_shared_original_without_moving_it(initialized,tmp_path,reference_path,hardlink):
    settings,first=setup(initialized,tmp_path,reference_path)
    original=tmp_path/'shared.pdf'
    original.write_bytes(b'synthetic shared file')
    first_resource=resources.link(settings,first['id'],path=original)
    second_record=tmp_path/'second.json'
    second_record.write_text(json.dumps({'schema_version':'1.0','citation_key':'second','loc':'Papers/Other','metadata':{'title':'Second'}}))
    second=initialized('add','--format','refs','--input',second_record)['data']
    alias=tmp_path/'alias.pdf'
    if hardlink:
        alias.hardlink_to(original)
    second_resource=resources.link(settings,second['id'],path=alias if hardlink else original)
    ids={first_resource['id'],second_resource['id']}
    preview=moves.reorg(settings)['moves']
    assert {row['resource_id'] for row in preview}==ids
    assert all(row['state']=='shared' and all(id in row['error'] for id in ids) for row in preview)
    executed=moves.reorg(settings,execute=True)['moves']
    assert {row['resource_id'] for row in executed}==ids
    assert all(row['state']=='shared' for row in executed)
    with connect(settings.catalog_path()) as c:
        assert c.execute('SELECT count(*) FROM file_operations').fetchone()[0]==0
    assert original.read_bytes()==b'synthetic shared file'
    assert all(resources.resolve_path(settings,sources.show(settings.catalog_path(),source_id)['resources'][0]).exists() for source_id in (first['id'],second['id']))
