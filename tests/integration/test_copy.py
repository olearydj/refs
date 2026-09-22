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
    assert copied['relative'].startswith('Unfiled/')
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
    with pytest.raises(RefError):
        resources.copy(settings, source['id'], path, resource_id=linked['id'])
    assert path.exists()
    copies = list((settings.library/'Unfiled').glob('*')) if (settings.library/'Unfiled').exists() else []
    assert len(copies) == (1 if failure == 'after' else 0)
    assert sources.show(settings.catalog_path(),source['id'])['resources'][0]['path'] == str(path)


def test_collision_keep_name_and_preview(initialized, tmp_path, reference_path):
    settings, source, path = prepare(initialized,tmp_path,reference_path)
    preview = resources.copy(settings, source['id'],path,keep_name=True,dry_run=True)
    assert preview['dry_run'] and not (settings.library/'Unfiled').exists()
    copied = resources.copy(settings,source['id'],path,keep_name=True)
    assert copied['relative'] == 'Unfiled/download.pdf'
    with pytest.raises(RefError):
        resources.copy(settings,source['id'],path,keep_name=True)
    assert path.exists()


def test_unavailable_library_bundle_and_symlink(initialized,tmp_path,reference_path):
    settings, source, path = prepare(initialized,tmp_path,reference_path)
    bundle=tmp_path/'bundle.app';bundle.mkdir()
    for candidate in [bundle]:
        with pytest.raises(RefError):
            resources.copy(settings,source['id'],candidate)
    symlink=tmp_path/'symlink.pdf';symlink.symlink_to(path)
    with pytest.raises(RefError):
        resources.copy(settings,source['id'],symlink)
    settings.library.rmdir()
    with pytest.raises(RefError):
        resources.copy(settings,source['id'],path)
    assert path.exists()


def test_add_defaults_and_partial_copy(initialized,tmp_path,reference_path):
    path=tmp_path/'new.pdf';path.write_bytes(b'synthetic')
    result=initialized('add','--format','refs','--input',reference_path,'--file',path)['data']
    assert len(result['resources']) == 1
    assert result['resources'][0]['root'] == 'library'
    assert result['resources'][0]['copied_from']['path'] == str(path)
    assert path.exists()
