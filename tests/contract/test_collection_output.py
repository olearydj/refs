import os
import subprocess

from conftest import extracted


def test_plain_hierarchy_and_filtered_sources(initialized,zotero_fixture,tmp_path):
    folder=tmp_path/'input'
    extracted(zotero_fixture,folder)
    initialized('import','--format','zotero','--input',folder)
    env=dict(os.environ,REFS_CONFIG=str(tmp_path/'config.toml'),REFS_CATALOG=str(tmp_path/'cat'))
    result=subprocess.run(['refs','collection','list'],env=env,text=True,capture_output=True)
    assert result.returncode==0
    assert result.stdout.splitlines()[0]=='Empty (0 active sources) [users/123]'
    assert 'Research/Methods (2 active sources)' in result.stdout
    result=subprocess.run(['refs','list','--collection','Research/Methods','--sort','key'],env=env,text=True,capture_output=True)
    assert result.returncode==0 and len(result.stdout.splitlines())==2
    assert result.stdout.splitlines()[0].startswith('extra2')
    assert initialized('collection','list')['schema_version']=='1.0'
