"""Rehearse moves on a disposable sample, never on original attachment trees."""
import argparse
import json
import runpy
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from refs import catalog, files, moves, resources
from refs.config import select, toml_text

REPO=Path(__file__).resolve().parents[3]


def contained(root, relative):
    path=root/relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(root):
        raise ValueError('Sample paths must remain inside the disposable sample')
    return path


def prepare(sample, work):
    manifest=json.loads((sample/'manifest.json').read_text())
    if any(path.is_symlink() for path in sample.rglob('*')):
        raise ValueError('Disposable samples cannot contain symlinks')
    shutil.copytree(sample,work)
    library=work/'lib'
    library.mkdir(exist_ok=True)
    # Simulate the owner's one-time rename only inside this fresh disposable home.
    old_folder,new_folder=library/'Unfiled',library/'unfiled'
    if old_folder.exists():
        if new_folder.exists() and not old_folder.samefile(new_folder):
            raise ValueError('Both intake folders exist; inspect the disposable sample')
        old_folder.rename(new_folder)
    config=work/'config.toml'
    config.write_text(toml_text(dict(schema_version=1,catalog=dict(path=str(work/'cat')),resources=dict(library_root=str(library),roots=dict(library=str(library))))))
    catalog.migrate(work/'cat')
    def remap(old):
        path=Path(old)
        for prefix,relative in sorted(manifest['roots'].items(),key=lambda pair:len(pair[0]),reverse=True):
            if path.is_relative_to(prefix):
                return contained(work,str(Path(relative)/path.relative_to(prefix)))
        raise ValueError('Unmapped attachment locator; refusing to read it')
    with sqlite3.connect(work/'cat/catalog.sqlite') as c:
        if c.execute('SELECT count(*) FROM file_operations').fetchone()[0]:
            raise ValueError('Supply a pre-move sample without operation history')
        for resource_id,path,root,relative in c.execute('SELECT id,path,root,relative FROM resources').fetchall():
            if path is not None:
                target=remap(path)
                locator=dict(path=str(target),root=None,relative=None)
            elif root=='library':
                target=contained(library,relative)
                locator=dict(path=None,root='library',relative=relative)
            else:
                raise ValueError('Unmapped named root in sample')
            if not target.is_file():
                raise ValueError('Sample attachment is missing')
            c.execute('UPDATE resources SET path=?,root=?,relative=?,locator=? WHERE id=?',(locator['path'],locator['root'],locator['relative'],json.dumps(locator,sort_keys=True),resource_id))
    settings=select(str(config),str(work/'cat'),no_project_config=True)
    assignment=runpy.run_path(str(REPO/'tools/assign_initial_loc.py'))
    proposals=assignment['preview'](settings,contained(work,manifest['box_root']))
    (work/'assignment-preview.json').write_text(json.dumps(proposals,ensure_ascii=False,indent=2))
    assignments=assignment['apply'](settings,proposals)
    (work/'assignments.json').write_text(json.dumps(assignments,ensure_ascii=False,indent=2))
    return settings


def command(settings):
    return [sys.executable,'-m','refs','--json','--no-project-config','--config',str(settings.config),'--catalog',str(settings.catalog_path()),'reorg','--execute']


def run_scenario(sample, scenario):
    work=Path(tempfile.mkdtemp(prefix='refs-move-rehearsal-')).resolve()/'home'
    settings=prepare(sample,work)
    with catalog.connect(settings.catalog_path()) as c:
        before=resources.inventory(c)
        with_files=len({item['source_id'] for item in before})
        assigned=c.execute('SELECT count(*) FROM sources WHERE loc IS NOT NULL AND id IN (SELECT source_id FROM resources)').fetchone()[0]
        fileless=c.execute('SELECT count(*) FROM sources WHERE id NOT IN (SELECT source_id FROM resources)').fetchone()[0]
        assert assigned==with_files, 'A source with files lacks loc'
        assert c.execute('SELECT count(*) FROM sources WHERE loc IS NOT NULL AND id NOT IN (SELECT source_id FROM resources)').fetchone()[0]==0, 'A file-less source received loc'
    expected={item['id']:files.hash_file(resources.resolve_path(settings,item)) for item in before}
    planned=moves.reorg(settings)
    extras={path:files.hash_file(Path(path)) for path in planned['unlinked_paths']}
    if scenario!='clean':
        worker="""import os,signal,sys
from refs import moves
from refs.config import select
def interrupt(point,row):
    if point==sys.argv[3]:
        os.kill(os.getpid(),signal.SIGKILL)
moves.checkpoint=interrupt
moves.reorg(select(sys.argv[1],sys.argv[2],no_project_config=True),execute=True)
"""
        killed=subprocess.run([sys.executable,'-c',worker,str(settings.config),str(settings.catalog_path()),scenario],capture_output=True,text=True)
        if killed.returncode!=-signal.SIGKILL:
            raise AssertionError(f'Kill boundary not reached: {killed.returncode}: {killed.stderr}')
    completed=subprocess.run(command(settings),capture_output=True,text=True)
    if completed.returncode:
        raise AssertionError(completed.stdout+completed.stderr)
    report=json.loads(completed.stdout)['data']
    (work/'move-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    with catalog.connect(settings.catalog_path()) as c:
        after=resources.inventory(c)
        operations=[dict(row) for row in c.execute('SELECT * FROM file_operations')]
    assert {item['id'] for item in after}==set(expected), 'Resource IDs or count changed'
    for item in after:
        path=resources.resolve_path(settings,item)
        assert path.is_relative_to(work), 'Locator escaped the disposable home'
        assert files.hash_file(path)==expected[item['id']], 'Attachment bytes changed'
    assert len(operations)==len(planned['moves']) and all(row['state']=='removed' for row in operations)
    assert {row['new_path'] for row in operations}=={row['new_path'] for row in planned['moves']}, 'Collision names changed on resume'
    assert all(not Path(row['old_path']).exists() for row in operations)
    assert all(files.hash_file(Path(path))==digest for path,digest in extras.items()), 'An unlinked extra changed'
    assert moves.reorg(settings,execute=True)['moves']==[], 'Completed rerun was not a no-op'
    return dict(scenario=scenario,resources=len(after),sources_with_files=with_files,sources_assigned=assigned,fileless_sources=fileless,moves=len(report['moves']),already_placed=len(after)-len(report['moves']),unlinked_files=len(extras),findings=0,home=str(work))


def run(sample):
    sample=Path(sample).expanduser().resolve()
    allowed=[Path(tempfile.gettempdir()).resolve(),Path('/private/tmp'),Path('/Volumes/Casa/tmp'),REPO/'tests/fixtures/real-trial']
    if not any(sample.is_relative_to(root) for root in allowed):
        raise ValueError('Put the disposable sample under the trial fixtures or a temporary directory')
    baseline={str(path.relative_to(sample)):files.hash_file(path) for path in sample.rglob('*') if not path.is_symlink() and path.is_file()}
    results=[run_scenario(sample,scenario) for scenario in ('clean','published_uncommitted','recorded')]
    assert baseline=={str(path.relative_to(sample)):files.hash_file(path) for path in sample.rglob('*') if not path.is_symlink() and path.is_file()}, 'Input sample changed'
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample',required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.sample),indent=2))
