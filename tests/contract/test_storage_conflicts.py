"""Stale writers receive application conflicts at the guarded write site."""

import json
from contextlib import contextmanager

import pytest

from refs import projects, sources
from refs.catalog import connect
from refs.models import SourceCreate
from refs.results import RefError


def test_second_writer_citation_key_collision_is_key_conflict(initialized,tmp_path,reference_path):
    raw=reference_path.read_bytes()
    planned=SourceCreate.model_validate(json.loads(raw))
    other=initialized('add','--format','refs','--input',reference_path)['data']
    with pytest.raises(RefError) as caught:
        with connect(tmp_path/'cat',write=True) as connection:
            sources.insert_source(connection,planned,raw,'stale writer',format='refs',warnings=[],key_provenance={'origin':'supplied'})
    assert caught.value.issue['code']=='key_conflict' and caught.value.exit_code==3
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0]==1
    assert sources.show(tmp_path/'cat',other['id'])['citation_key']==planned.citation_key


def test_second_writer_project_name_collision_is_project_conflict(initialized,tmp_path,monkeypatch):
    other=initialized('project','create','shared','--description','First writer')['data']
    real_connect=projects.connect
    class StaleRead:
        def __init__(self,connection):
            self.connection=connection
        def execute(self,sql,params=()):
            if sql.startswith('SELECT * FROM projects WHERE name='):
                return self
            return self.connection.execute(sql,params)
        def fetchone(self):
            return None
    @contextmanager
    def stale_connect(*args,**kwargs):
        with real_connect(*args,**kwargs) as connection:
            yield StaleRead(connection)
    monkeypatch.setattr(projects,'connect',stale_connect)
    with pytest.raises(RefError) as caught:
        projects.create(tmp_path/'cat','shared','Stale writer')
    assert caught.value.issue['code']=='project_conflict' and caught.value.exit_code==3
    with real_connect(tmp_path/'cat') as connection:
        rows=connection.execute('SELECT id,description FROM projects').fetchall()
    assert len(rows)==1 and rows[0]['id']==other['id'] and rows[0]['description']=='First writer'


def test_revision_guard_rejects_writer_after_another_update(initialized,tmp_path,reference_path):
    first=initialized('add','--format','refs','--input',reference_path)['data']
    with connect(tmp_path/'cat') as connection:
        stale=sources.record(connection,first['id'])
    initialized('update',first['id'],'--if-revision',1,'--set','metadata.volume="2"')
    canonical={name:stale[name] for name in SourceCreate.model_fields if name in stale}
    canonical['metadata']={**canonical['metadata'],'volume':'3'}
    with pytest.raises(RefError) as caught:
        with connect(tmp_path/'cat',write=True) as connection:
            sources.store_record(connection,stale,canonical,[])
    assert caught.value.issue['code']=='stale_revision'
    current=sources.show(tmp_path/'cat',first['id'])
    assert current['revision']==2 and current['metadata']['volume']=='2'
