"""Configuration selection never initializes a fallback catalog."""

import json
import os
import subprocess

import pytest

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
    with pytest.raises(RefError):
        select(str(config),str(tmp_path/'cat'))


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
    assert inspected['values']['titles.minor_words']==['With']
    assert inspected['origins']['keys.template']==str(config)
    run=subprocess.run(['refs','config','show'],env=dict(os.environ,REFS_CONFIG=str(config),REFS_CATALOG=str(tmp_path/'cat')),text=True,capture_output=True)
    assert run.returncode==0 and run.stdout.startswith('Configuration:')
