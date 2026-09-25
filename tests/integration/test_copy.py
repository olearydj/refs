"""Real disposable files, injected failures, no original deletion in any outcome."""

import pytest

from refs import files, resources, sources
from refs.config import select
from refs.results import RefError


def prepare(initialized, tmp_path, reference_path):
    source = initialized('add','--format','refs','--input',reference_path)['data']
    path = tmp_path/'download.pdf'
    path.write_bytes(b'synthetic PDF content')
    return select(str(tmp_path/'config.toml'),str(tmp_path/'cat')), source, path


def test_copy_retargets_one_resource(initialized, tmp_path, reference_path):
    settings, source, path = prepare(initialized,tmp_path,reference_path)
    linked = resources.link(settings, source['id'], path=path)
    copied = resources.copy(settings, source['id'], path, resource_id=linked['id'])
    assert copied['id'] == linked['id']
    assert copied['copied_from']['path'] == str(path)
    assert copied['root'] == 'library'
    assert copied['relative'].startswith('unfiled/')
    assert path.read_bytes() == (settings.library/copied['relative']).read_bytes()
    assert len(sources.show(settings.catalog_path(),source['id'])['resources']) == 1


@pytest.mark.parametrize('failure', ['before', 'after', 'changed'])
def test_copy_failure_retains_original_and_published_copy(initialized, tmp_path, reference_path, monkeypatch, failure):
    settings, source, path = prepare(initialized,tmp_path,reference_path)
    linked = resources.link(settings, source['id'], path=path)
    if failure == 'before':
        monkeypatch.setattr(files, 'publish', lambda *args: (_ for _ in ()).throw(OSError('synthetic interruption')))
    elif failure == 'after':
        monkeypatch.setattr(resources, 'register_copy', lambda *args, **kwargs: (_ for _ in ()).throw(OSError('synthetic interruption')))
    else:
        original = files.hash_file
        def change(target):
            result = original(target)
            if target == path:
                path.write_bytes(b'changed externally')
            return result
        monkeypatch.setattr(files,'hash_file',change)
    with pytest.raises(RefError) as error:
        resources.copy(settings, source['id'], path, resource_id=linked['id'])
    assert error.value.issue['code'] == {'before':'copy_failed','after':'copy_published_unregistered','changed':'source_changed'}[failure]
    assert path.exists()
    copies = list((settings.library/'unfiled').glob('*')) if (settings.library/'unfiled').exists() else []
    assert len(copies) == (1 if failure == 'after' else 0)
    assert sources.show(settings.catalog_path(),source['id'])['resources'][0]['path'] == str(path)


def test_collision_keep_name_and_preview(initialized, tmp_path, reference_path):
    settings, source, path = prepare(initialized,tmp_path,reference_path)
    preview = resources.copy(settings, source['id'],path,keep_name=True,dry_run=True)
    assert preview['dry_run'] and not (settings.library/'unfiled').exists()
    copied = resources.copy(settings,source['id'],path,keep_name=True)
    assert copied['relative'] == 'unfiled/download.pdf'
    path.write_bytes(b'different content, same destination')
    with pytest.raises(RefError) as error:
        resources.copy(settings,source['id'],path,keep_name=True)
    assert error.value.issue['code'] == 'destination_exists'
    assert (settings.library/'unfiled/download.pdf').read_bytes() == b'synthetic PDF content'
    assert path.exists()


def test_unavailable_library_bundle_and_symlink(initialized,tmp_path,reference_path):
    settings, source, path = prepare(initialized,tmp_path,reference_path)
    bundle=tmp_path/'bundle.app'
    bundle.mkdir()
    for candidate in [bundle]:
        with pytest.raises(RefError) as error:
            resources.copy(settings,source['id'],candidate)
        assert error.value.issue['code'] == 'unsafe_copy_source'
    symlink=tmp_path/'symlink.pdf'
    symlink.symlink_to(path)
    with pytest.raises(RefError) as error:
        resources.copy(settings,source['id'],symlink)
    assert error.value.issue['code'] == 'unsafe_copy_source'
    settings.library.rmdir()
    with pytest.raises(RefError) as error:
        resources.copy(settings,source['id'],path)
    assert error.value.issue['code'] == 'library_unavailable'
    assert path.exists()


def test_add_defaults_and_partial_copy(initialized,tmp_path,reference_path):
    path=tmp_path/'new.pdf'
    path.write_bytes(b'synthetic')
    result=initialized('add','--format','refs','--input',reference_path,'--file',path,'--copy')['data']
    assert len(result['resources']) == 1
    assert result['resources'][0]['root'] == 'library'
    assert result['resources'][0]['copied_from']['path'] == str(path)
    assert path.exists()


def test_link_flag_keep_name_and_failed_add(initialized,tmp_path,reference_path):
    path=tmp_path/'original.pdf'
    path.write_bytes(b'synthetic')
    linked=initialized('add','--format','refs','--input',reference_path,'--file',path,'--link')['data']
    assert linked['resources'][0]['path'] == str(path)
    assert not (tmp_path/'lib'/'unfiled').exists()
    copied=initialized('resource','add',linked['id'],'--path',path,'--copy','--keep-name')['data']
    assert copied['copied'] is False
    assert copied['duplicate_resource_id'] == linked['resources'][0]['id']
    assert len(initialized('show',linked['id'])['data']['resources']) == 1
    other=tmp_path/'other.pdf'
    other.write_bytes(b'other')
    failed=initialized('add','--format','refs','--input',reference_path,'--file',other,'--copy','--keep-name')['data']
    assert len(failed['resources']) == 2
    assert path.exists() and other.exists()
    result=initialized('add','--format','refs','--input',reference_path,'--file',other,'--copy','--keep-name',expected=4)
    assert result['data']['id'] == linked['id']
    assert result['errors'][0]['code'] == 'file_action_incomplete'
    assert other.read_bytes() == b'other'


def test_preview_does_not_capture_or_stage(initialized,tmp_path,reference_path):
    path=tmp_path/'original.pdf'
    path.write_bytes(b'synthetic')
    data=initialized('add','--format','refs','--input',reference_path,'--file',path,'--copy','--dry-run')['data']
    assert data['resources'][0]['destination'].endswith('/unfiled/LearningPython-2024.pdf')
    assert initialized('list')['data']['total'] == 0
    assert list((tmp_path/'cat'/'staging').iterdir()) == []
    assert not (tmp_path/'lib'/'unfiled').exists()


def test_revision_change_after_publication_preserves_copy(initialized,tmp_path,reference_path,monkeypatch):
    settings, source, path = prepare(initialized,tmp_path,reference_path)
    original=resources.register_copy
    def change(*args,**kwargs):
        sources.update(settings.catalog_path(),source['id'],{'schema_version':'1.0','set':{'metadata.volume':'Changed'}},source['revision'])
        return original(*args,**kwargs)
    monkeypatch.setattr(resources,'register_copy',change)
    with pytest.raises(RefError) as error:
        resources.copy(settings,source['id'],path)
    assert error.value.exit_code == 4
    assert error.value.issue['code'] == 'copy_published_unregistered'
    assert list((settings.library/'unfiled').iterdir())
    assert not sources.show(settings.catalog_path(),source['id'])['resources']
    assert path.exists()


def test_filename_fallback_is_explicit(initialized,tmp_path):
    import json
    path=tmp_path/'undated.pdf'
    path.write_bytes(b'synthetic')
    record=tmp_path/'undated.json'
    record.write_text(json.dumps({'schema_version':'1.0','citation_key':'undated','metadata':{'title':'Undated Work'}}))
    result=initialized('add','--format','refs','--input',record,'--file',path,'--copy')
    data=result['data']
    assert data['resources'][0]['relative'] == 'unfiled/undated.pdf'
    assert any(item['code']=='filename_unavailable' for item in result['warnings'])
    assert 'warnings' not in data


def test_staging_volume_mismatch_refuses_before_copy(initialized,tmp_path,reference_path,monkeypatch):
    import os
    from pathlib import Path

    settings, source, path = prepare(initialized,tmp_path,reference_path)
    stat = Path.stat
    def different_device(self,*args,**kwargs):
        result = stat(self,*args,**kwargs)
        if self == settings.catalog_path():
            fields = list(result)
            fields[2] += 1
            return os.stat_result(fields)
        return result
    monkeypatch.setattr(Path,'stat',different_device)
    with pytest.raises(RefError) as error:
        resources.copy(settings,source['id'],path)
    assert error.value.issue['code'] == 'staging_volume_mismatch'
    assert path.read_bytes() == b'synthetic PDF content'
    assert not (settings.library/'unfiled').exists()
