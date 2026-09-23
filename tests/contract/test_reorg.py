"""Reorg previews and moves only synthetic resources in a temporary home."""
import json
from pathlib import Path

import pytest

from refs import moves, resources, sources
from refs.catalog import connect
from refs.config import select


def setup(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path,'--loc','Papers/Topic')['data']
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    return settings,source


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
