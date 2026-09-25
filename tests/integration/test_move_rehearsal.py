import json
import runpy
import shutil
import subprocess
from pathlib import Path

import pytest

from refs import resources
from refs.catalog import init
from refs.config import select

harness=runpy.run_path('tests/fixtures/real-trial/move_rehearsal.py')


def test_corpus_cli_passes_the_remaining_deadline_to_its_process(tmp_path,monkeypatch):
    settings=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'),no_project_config=True)
    def completed(command,**options):
        assert options['timeout']==0.25
        return subprocess.CompletedProcess(command,0,'{"status":"ok"}','')
    monkeypatch.setattr(subprocess,'run',completed)
    assert harness['phase6_cli'](settings,'paths',timeout=0.25)==(0,{'status':'ok'})


def sample(tmp_path):
    root=tmp_path/'sample'
    root.mkdir()
    config=root/'config.toml'
    settings=select(str(config),str(root/'cat'),no_project_config=True)
    init(settings,root/'lib')
    settings=select(str(config),str(root/'cat'),no_project_config=True)
    from refs import sources
    for index in range(3):
        source=sources.add(settings.catalog_path(),json.dumps({'schema_version':'1.0','citation_key':f'source{index}','metadata':{'title':f'Synthetic {index}'}}).encode(),'synthetic')
        box=root/'tree/Box/Café'/f'file{index}.pdf'
        box.parent.mkdir(parents=True,exist_ok=True)
        box.write_bytes(f'PDF {index}'.encode())
        resources.link(settings,source['id'],path=box)
        snapshot=root/f'tree/storage/{index}/snapshot.html'
        snapshot.parent.mkdir(parents=True)
        snapshot.write_bytes(f'Snapshot {index}'.encode())
        resources.link(settings,source['id'],path=snapshot)
    (root/'tree/Box/Café/extra.txt').write_bytes(b'untouched')
    (root/'manifest.json').write_text(json.dumps({'roots':{str(root/'tree'):'tree'},'box_root':'tree/Box'}))
    return root


def test_clean_and_actual_kill_resume(tmp_path):
    root=sample(tmp_path)
    results=harness['run'](root,keep=True)
    try:
        assert [row['scenario'] for row in results]==['clean','published_uncommitted','recorded']
        assert all(row['resources']==6 and row['moves']==6 and row['unlinked_files']==1 and row['findings']==0 for row in results)
        for row in results:
            folder=Path(row['home'])/'lib/Café'
            assert {path.name for path in folder.glob('*.html')}=={'snapshot.html','snapshot-b.html','snapshot-c.html'}
    finally:
        for row in results:
            shutil.rmtree(Path(row['home']).parent)


@pytest.mark.parametrize('damage',['escape','symlink'])
def test_harness_rejects_escaping_sample(tmp_path,damage):
    root=sample(tmp_path)
    if damage=='escape':
        (root/'manifest.json').write_text(json.dumps({'roots':{str(root/'tree'):'../escape'},'box_root':'tree/Box'}))
    else:
        (root/'escape').symlink_to(tmp_path)
    with pytest.raises(ValueError):
        harness['run'](root)
