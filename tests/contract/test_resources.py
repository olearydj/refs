"""Resource associations never imply deletion or movement of linked bytes."""

import pytest

from refs import resources
from refs.config import select
from refs.results import RefError


def test_link_repeat_inventory_unlink(initialized, tmp_path, reference_path):
    source = initialized('add','--format','refs','--input',reference_path)['data']
    path = tmp_path/'linked.pdf'
    path.write_bytes(b'synthetic PDF bytes')
    first = initialized('resource','add',source['id'],'--path',path)['data']
    again = initialized('resource','add',source['id'],'--path',path)['data']
    assert first['id'] == again['id'] and again['unchanged']
    shown = initialized('show',source['id'])['data']
    assert len(shown['resources']) == 1
    initialized('resource','unlink',first['id'],'--if-revision',1,'--execute')
    assert path.read_bytes() == b'synthetic PDF bytes'
    assert not initialized('show',source['id'])['data']['resources']


def test_missing_and_named_roots(initialized, tmp_path, reference_path):
    source = initialized('add','--format','refs','--input',reference_path)['data']
    first = initialized('resource','add',source['id'],'--root','library','--relative','absent.pdf')['data']
    assert first['root'] == 'library' and first['relative'] == 'absent.pdf'
    checked = initialized('resource','check','--source',source['id'])['data']
    assert checked['items'][0]['status'] == 'missing'
    initialized('resource','add',source['id'],'--root','library','--relative','../escape.pdf',expected=3)


def test_open_selection_does_not_launch_apps(initialized, tmp_path, reference_path, monkeypatch):
    source = initialized('add','--format','refs','--input',reference_path)['data']
    settings = select(str(tmp_path/'config.toml'), str(tmp_path/'cat'))
    paths = [tmp_path/'a.pdf', tmp_path/'b.pdf']
    for path in paths:
        path.write_bytes(b'synthetic')
        resources.link(settings, source['id'], path=path)
    called = []
    monkeypatch.setattr(resources, 'launch', called.append)
    choices = resources.open_source(settings, source['id'])
    assert len(choices['choices']) == 2 and not called
    chosen = choices['choices'][0]
    resources.open_source(settings, source['id'], resource_id=chosen['id'])
    assert len(called) == 1


def test_import_file_paths_are_idempotent_links(initialized, tmp_path):
    path = tmp_path/'external.pdf'
    path.write_bytes(b'synthetic')
    bib = tmp_path/'files.bib'
    bib.write_text('@book{files,title={File Example},file={'+str(path)+'}}')
    initialized('import','--input',bib)
    initialized('import','--input',bib)
    shown = initialized('show','files')['data']
    assert len(shown['resources']) == 1
    assert path.read_bytes() == b'synthetic'


def test_unsafe_symlink_root(initialized, tmp_path, reference_path):
    source = initialized('add','--format','refs','--input',reference_path)['data']
    (tmp_path/'lib'/'escape').symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(RefError):
        resources.link(select(str(tmp_path/'config.toml'),str(tmp_path/'cat')), source['id'], root='library', relative='escape/out.pdf')
