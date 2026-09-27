"""Configuration selection never initializes a fallback catalog."""

import json
import os
import subprocess

import pytest
from conftest import REFS_COMMAND

from refs.config import select
from refs.results import RefError


def test_precedence_and_before_init(tmp_path,monkeypatch):
    config=tmp_path/'user.toml'
    config.write_text('schema_version=1\n[catalog]\npath="configured"\n')
    monkeypatch.setenv('REFS_CONFIG',str(config))
    monkeypatch.setenv('REFS_CATALOG',str(tmp_path/'environment'))
    assert select(None,None).catalog==tmp_path/'environment'
    assert select(None,str(tmp_path/'flag')).catalog==tmp_path/'flag'
    selected=select(None,None)
    assert selected.inspect()['values']['keys.title_words']==2
    assert not selected.catalog.exists()


def test_nearest_project_worktree_and_disable(tmp_path,monkeypatch):
    config=tmp_path/'user.toml'
    config.write_text('schema_version=1\n')
    root=tmp_path/'worktree'
    root.mkdir()
    (root/'.git').write_text('gitdir: elsewhere')
    (root/'.refs.toml').write_text('project="root"\n')
    nested=root/'paper'
    nested.mkdir()
    (nested/'.refs.toml').write_text('project="paper"\n[export]\noutput="paper.bib"\n')
    child=nested/'section'
    child.mkdir()
    monkeypatch.chdir(child)
    selected=select(str(config),str(tmp_path/'cat'))
    assert selected.values['project']=='paper'
    assert selected.values['export']['output']==str(nested/'paper.bib')
    assert selected.inspect()['origins']['project']==str(nested/'.refs.toml')
    assert select(str(config),str(tmp_path/'cat'),no_project_config=True).values.get('project') is None
    assert select(str(config),str(tmp_path/'cat'),project_file=str(root/'.refs.toml')).values['project']=='root'


@pytest.mark.parametrize('text',[
    '[catalog]\npath="forbidden"',
    '[keys]\ntitle_words=1',
    '[export]\nprofile="rich"',
    'project=5',
    '[export]\nconsumers="pandoc"',
])
def test_invalid_project_settings(tmp_path,text):
    config=tmp_path/'user.toml'
    config.write_text('schema_version=1\n')
    project=tmp_path/'project.toml'
    project.write_text(text)
    with pytest.raises(RefError) as error:
        select(str(config),str(tmp_path/'cat'),project_file=str(project))
    assert error.value.issue['code'] == 'invalid_config'
    assert error.value.issue['path']==str(project)
    assert not (tmp_path/'cat').exists()


@pytest.mark.parametrize('text',[
    '[keys]\ntemplate="{unknown}"',
    '[keys]\nwithout_creator="{author}-{title}"',
    '[keys]\ntitle_words=3',
    '[keys]\nstopwords=[""]',
    '[titles]\npolicy="unsupported"',
    '[resources.roots]\nmissing=42',
])
def test_invalid_user_values(tmp_path,text):
    config=tmp_path/'user.toml'
    config.write_text('schema_version=1\n'+text)
    with pytest.raises(RefError) as error:
        select(str(config),str(tmp_path/'cat'))
    assert error.value.issue['code'] == 'invalid_config'
    assert not (tmp_path/'cat').exists()


def test_missing_and_unwritable_catalog(initialized,tmp_path):
    result=initialized('--catalog',tmp_path/'missing','list',expected=3)
    assert result['errors'][0]['code']=='catalog_missing'
    catalog=tmp_path/'cat'
    catalog.chmod(0o500)
    try:
        result=initialized('project','create','cannot-write',expected=5)
        assert result['errors'][0]['code']=='home_not_writable'
    finally:
        catalog.chmod(0o700)


def test_inspection_and_policy_overrides(initialized,tmp_path):
    config=tmp_path/'config.toml'
    config.write_text(config.read_text()+'\n[keys]\ntitle_words=1\ntemplate="{year}_{author}_{title}"\n[keys.corporate_aliases]\n"Research and Design"="rnd"\n[titles]\nminor_words=["With","with"]\nprotected_terms=["PyTest"]\n')
    record=tmp_path/'record.json'
    record.write_text(json.dumps({'schema_version':'1.0','metadata':{'title':'Work with PyTest','author':[{'literal':'Research and Design'}],'issued':{'date-parts':[[2024]]}}}))
    result=initialized('add','--format','refs','--input',record)['data']
    assert result['citation_key']=='2024_rnd_work'
    inspected=initialized('config','show')['data']
    assert inspected['values']['titles.minor_words']==['a','an','and','as','at','but','by','for','in','nor','of','on','or','per','so','the','to','up','via','yet','With']
    assert inspected['origins']['keys.template']==str(config)
    run=subprocess.run([*REFS_COMMAND,'config','show'],env=dict(os.environ,REFS_CONFIG=str(config),REFS_CATALOG=str(tmp_path/'cat')),text=True,capture_output=True)
    assert run.returncode==0 and run.stdout.startswith('Configuration:')


def test_project_export_defaults_and_invocation_override(initialized,tmp_path):
    import sys
    record=tmp_path/'record.json'
    record.write_text(json.dumps({'schema_version':'1.0','citation_key':'one','metadata':{'title':'Example'}}))
    initialized('add','--format','refs','--input',record)
    initialized('project','create','one')
    initialized('project','create','two')
    initialized('project','cite','one','one')
    selected=tmp_path/'paper.toml'
    selected.write_text('project="one"\n[export]\noutput="default.bib"\n')
    def configured(*args, expected=0):
        result=subprocess.run([sys.executable,'-m','refs','--json','--project-file',str(selected),*map(str,args)],env=dict(os.environ,REFS_CONFIG=str(tmp_path/'config.toml'),REFS_CATALOG=str(tmp_path/'cat')),cwd=tmp_path,capture_output=True,text=True)
        assert result.returncode==expected, result.stdout+result.stderr
        assert result.stderr==''
        return json.loads(result.stdout)
    result=configured('export')['data']
    assert result['count']==1 and result['output']==str(tmp_path/'default.bib')
    result=configured('export','--project','two','--output',tmp_path/'other.bib')['data']
    assert result['count']==0
    configured('--no-project-config','paths',expected=2)


def test_changed_policy_does_not_rewrite_existing_correction(initialized,tmp_path,reference_path):
    record=initialized('add','--format','refs','--input',reference_path)['data']
    before=record['metadata']['title']
    config=tmp_path/'config.toml'
    config.write_text(config.read_text()+'\n[titles]\nminor_words=["python"]\nprotected_terms=[]\n')
    changed=initialized('update',record['id'],'--if-revision',1,'--set','metadata.volume="42"')['data']
    assert changed['metadata']['title']==before and changed['citation_key']==record['citation_key']
    original=config.read_bytes()
    initialized('init','--library-root',tmp_path/'lib')
    assert config.read_bytes()==original


@pytest.mark.parametrize(('policy', 'protection', 'expected'), [
    ('preserve', None, 'a sentence about training'),
    (None, None, 'A Sentence About Training'),
    ('english-title-case-v1', None, 'A Sentence About Training'),
    ('preserve', {'preserve_case': False, 'protected_terms': []}, 'A Sentence About Training'),
    ('english-title-case-v1', {'preserve_case': True, 'protected_terms': []}, 'a sentence about training'),
])
def test_project_title_policy_and_record_override(initialized, tmp_path, cli_env, policy, protection, expected):
    import sys
    project = tmp_path / '.refs.toml'
    project.write_text('[titles]\npolicy="' + policy + '"\n' if policy else '')
    record = {'schema_version': '1.0', 'metadata': {'title': 'a sentence about training'}}
    if protection is not None:
        record['title_protection'] = {'title': protection}
    source = tmp_path / 'source.json'
    source.write_text(json.dumps(record))
    result = subprocess.run([sys.executable, '-m', 'refs', '--json', '--project-file', str(project),
                             'add', '--format', 'refs', '--input', str(source)], env=cli_env, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    added = json.loads(result.stdout)['data']
    stored = initialized('show', added['citation_key'])['data']
    assert stored['metadata']['title'] == expected
    if policy == 'preserve' and protection is None:
        assert stored['title_protection'] == {}
