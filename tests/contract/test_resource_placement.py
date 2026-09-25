import json

import pytest

from refs import moves, resources, sources
from refs.config import select
from refs.render import render_text


def test_five_kinds_and_filter_are_read_only(initialized,tmp_path,reference_path,monkeypatch):
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    source=initialized('add','--format','refs','--input',reference_path)['data']
    unplaced=tmp_path/'unplaced.pdf'
    unplaced.write_bytes(b'untouched')
    resources.link(settings,source['id'],path=unplaced)
    record=tmp_path/'placed.json'
    record.write_text(json.dumps({'schema_version':'1.0','citation_key':'placed','loc':'Topic','metadata':{'title':'Placed'}}))
    placed=initialized('add','--format','refs','--input',record)['data']
    for filename in ['pending.pdf','interrupted.pdf','lib/wrong.pdf']:
        path=tmp_path/filename
        path.write_bytes(filename.encode())
        resource=resources.link(settings,placed['id'],path=path)
        if filename=='interrupted.pdf':
            def kill(point,row):
                if point=='published':
                    raise KeyboardInterrupt
            monkeypatch.setattr(moves,'checkpoint',kill)
            with pytest.raises(KeyboardInterrupt):
                moves.move(settings,resource['id'],tmp_path/'lib/Topic/interrupted.pdf')
    extra=tmp_path/'lib/extra.pdf'
    extra.write_bytes(b'unrecorded')
    (tmp_path/'lib/escape').symlink_to(tmp_path,target_is_directory=True)
    before=(tmp_path/'cat/catalog.sqlite').read_bytes()
    result=initialized('resource','check')['data']
    assert {item['kind'] for item in result['items']}==set(resources.PLACEMENT_KINDS)
    assert len(result['items'])==5
    for kind in resources.PLACEMENT_KINDS:
        one=initialized('resource','check','--kind',kind)['data']
        assert len(one['items'])==1 and one['items'][0]['kind']==kind
    text=render_text('resource check',result,[])
    assert 'in the library, not recorded\t'+str(extra) in text
    assert 'Use resource add SOURCE --path' in text
    assert 'unfinished move\t'+str(tmp_path/'interrupted.pdf') in text
    assert initialized('resource','check','--source',source['id'],'--kind','unrecorded')['data']['items']==[]
    assert initialized('resource','check','--kind','bad',expected=2)['errors'][0]['code']=='invalid_kind'
    assert before==(tmp_path/'cat/catalog.sqlite').read_bytes()
    assert extra.read_bytes()==b'unrecorded' and unplaced.read_bytes()==b'untouched'


def test_correct_managed_file_keeps_health_check(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path,'--loc','Topic')['data']
    path=tmp_path/'file.pdf'
    path.write_bytes(b'synthetic')
    initialized('resource','add',source['id'],'--path',path,'--copy')
    result=initialized('resource','check','--verify')['data']
    assert result['items'][0]['kind'] is None and result['items'][0]['status']=='available'
    source=initialized('show',source['id'])['data']
    sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','clear':['loc']},source['revision'])
    assert initialized('resource','check','--kind','managed_mismatch')['data']['items']==[]


def test_kind_filter_skips_hashing_excluded_resources(initialized,tmp_path,reference_path,monkeypatch):
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    source=initialized('add','--format','refs','--input',reference_path,'--loc','Topic')['data']
    path=tmp_path/'managed.pdf'
    path.write_bytes(b'verified bytes')
    initialized('resource','add',source['id'],'--path',path,'--copy')
    def unexpected_hash(path):
        raise AssertionError(f'Filtered resource was hashed: {path}')
    monkeypatch.setattr(resources.files,'hash_file',unexpected_hash)
    assert resources.check(settings,source['id'],verify=True,kind='linked_pending')['items']==[]
    with pytest.raises(AssertionError,match='Filtered resource was hashed'):
        resources.check(settings,source['id'],verify=True)


def test_library_scan_ignores_os_metadata_but_reports_unrecorded_files(initialized,tmp_path):
    library=tmp_path/'lib'
    topic=library/'Topic'
    topic.mkdir()
    metadata={
        library/'.DS_Store':b'finder',
        topic/'._article.pdf':b'appledouble',
        topic/'Thumbs.db':b'thumbnails',
        topic/'desktop.ini':b'windows',
    }
    for path,contents in metadata.items():
        path.write_bytes(contents)
    article=topic/'article.pdf'
    article.write_bytes(b'not recorded')
    result=initialized('resource','check','--kind','unrecorded')['data']
    assert [item['resolved_path'] for item in result['items']]==[str(article)]
    assert article.read_bytes()==b'not recorded'
    assert all(path.read_bytes()==contents for path,contents in metadata.items())
