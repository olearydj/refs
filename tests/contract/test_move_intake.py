from pathlib import Path

import pytest


def test_add_moves_and_resource_add_links(initialized,tmp_path,reference_path):
    original=tmp_path/'download.pdf'
    original.write_bytes(b'synthetic')
    source=initialized('add','--format','refs','--input',reference_path,'--file',original)['data']
    assert source['loc']=='unfiled' and not original.exists()
    assert len(source['resources'])==1
    assert (tmp_path/'lib'/source['resources'][0]['relative']).read_bytes()==b'synthetic'
    other=tmp_path/'other.pdf'
    other.write_bytes(b'linked')
    linked=initialized('resource','add',source['id'],'--path',other)['data']
    assert linked['path']==str(other) and other.exists()
    assert initialized('show',source['id'])['data']['loc']=='unfiled'


@pytest.mark.parametrize('flag',['--copy','--move'])
def test_intake_preserves_existing_loc(initialized,tmp_path,reference_path,flag):
    source=initialized('add','--format','refs','--input',reference_path,'--loc','Topic/Nested')['data']
    original=tmp_path/'original.pdf'
    original.write_bytes(b'synthetic')
    result=initialized('resource','add',source['id'],'--path',original,flag,'--keep-name')['data']
    assert result['relative']=='Topic/Nested/original.pdf'
    assert original.exists()==(flag=='--copy')
    shown=initialized('show',source['id'])['data']
    assert shown['loc']=='Topic/Nested' and 'loc' not in shown['corrected_fields']


def test_copy_sets_loc_and_link_leaves_it_empty(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    path=tmp_path/'first.pdf'
    path.write_bytes(b'first')
    initialized('resource','add',source['id'],'--path',path,'--link')
    assert not initialized('show',source['id'])['data'].get('loc')
    other=tmp_path/'second.pdf'
    other.write_bytes(b'second')
    initialized('resource','add',source['id'],'--path',other,'--copy')
    assert initialized('show',source['id'])['data']['loc']=='unfiled'
    assert path.exists() and other.exists()


def test_move_admission_and_preview(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    path=tmp_path/'file.pdf'
    path.write_bytes(b'synthetic')
    preview=initialized('resource','add',source['id'],'--path',path,'--move','--dry-run')['data']
    assert preview['dry_run'] and path.exists()
    assert not initialized('show',source['id'])['data'].get('loc')
    linked=initialized('resource','add',source['id'],'--path',path)['data']
    error=initialized('resource','add',source['id'],'--path',path,'--move',expected=3)
    assert error['errors'][0]['details']['resource_id']==linked['id']
    assert path.exists()


def test_move_keeps_labels_and_refuses_collision(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    for index in range(2):
        path=tmp_path/f'file{index}.pdf'
        path.write_bytes(f'synthetic {index}'.encode())
        result=initialized('resource','add',source['id'],'--path',path,'--move','--label','release',expected=0 if index==0 else 3)
        if index==0:
            assert Path(result['data']['destination']).name.endswith('-release.pdf')
        else:
            assert result['errors'][0]['code']=='destination_exists' and path.exists()


def test_add_move_preview_loc_and_text(initialized, tmp_path, reference_path):
    path = tmp_path/'download.pdf'
    path.write_bytes(b'synthetic')
    preview = initialized('add','--format','refs','--input',reference_path,'--file',path,'--loc','Papers','--dry-run')['data']
    assert preview['resources'][0]['destination'].endswith('/Papers/LearningPython-2024.pdf')
    import subprocess
    result = subprocess.run(['refs','--no-project-config','--config',str(tmp_path/'config.toml'),'--catalog',str(tmp_path/'cat'),'add','--format','refs','--input',str(reference_path),'--file',str(path)],capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    text = result.stdout
    assert text.splitlines()[1] == f"Moved {path} to {tmp_path/'lib/unfiled/LearningPython-2024.pdf'} for smith-2024-learningPython"


def test_intake_resumes_with_one_resource(initialized, tmp_path, reference_path, monkeypatch):
    from refs import moves, sources
    from refs.config import select
    settings = select(config=str(tmp_path/'config.toml'),catalog=str(tmp_path/'cat'),no_project_config=True)
    source = initialized('add','--format','refs','--input',reference_path)['data']
    path = tmp_path/'download.pdf'
    path.write_bytes(b'synthetic')
    def interrupt(point, row):
        if point == 'published':
            raise KeyboardInterrupt
    monkeypatch.setattr(moves,'checkpoint',interrupt)
    with pytest.raises(KeyboardInterrupt):
        moves.intake(settings,source['id'],path)
    before = sources.show(settings.catalog_path(),source['id'])['resources']
    assert len(before)==1 and before[0]['path']==str(path) and path.exists()
    monkeypatch.setattr(moves,'checkpoint',lambda *args:None)
    result = moves.intake(settings,source['id'],path)
    assert result['id']==before[0]['id'] and not path.exists()
    assert moves.intake(settings,source['id'],path)['id']==result['id']


def test_move_refuses_another_sources_file(initialized, tmp_path, reference_path):
    import json
    source = initialized('add','--format','refs','--input',reference_path)['data']
    path = tmp_path/'recorded.pdf'
    path.write_bytes(b'synthetic')
    resource = initialized('resource','add',source['id'],'--path',path)['data']
    other = tmp_path/'other.json'
    other.write_text(json.dumps({'schema_version':'1.0','citation_key':'other','metadata':{'title':'Other'}}))
    second = initialized('add','--format','refs','--input',other)['data']
    error = initialized('resource','add',second['id'],'--path',path,'--move',expected=3)
    assert error['errors'][0]['details']['resource_id']==resource['id']
    assert initialized('show',second['id'])['data']['resources']==[] and path.exists()


def test_move_missing_library_and_conflicting_flags(initialized, tmp_path, reference_path):
    source = initialized('add','--format','refs','--input',reference_path)['data']
    path = tmp_path/'original.pdf'
    path.write_bytes(b'synthetic')
    initialized('resource','add',source['id'],'--path',path,'--move','--copy',expected=2)
    (tmp_path/'lib').rmdir()
    result = initialized('resource','add',source['id'],'--path',path,'--move',expected=3)
    assert result['errors'][0]['code']=='library_unavailable' and path.exists()
    assert initialized('show',source['id'])['data']['resources']==[]
