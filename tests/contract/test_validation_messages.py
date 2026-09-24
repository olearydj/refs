import json
import subprocess

from conftest import REFS_COMMAND, isolated_env


def test_context_type_error_has_path_and_reason(initialized,tmp_path):
    path=tmp_path/'invalid.json'
    path.write_text(json.dumps({'schema_version':'1.0','metadata':{'type':'book','title':'Synthetic Book'},'context':'not a list'}))
    result=initialized('add','--format','refs','--input',path,expected=2)
    issue=result['errors'][0]['details']['issues'][0]
    assert issue['loc']==['context'] and issue['msg']=='Input should be a valid array'
    env=isolated_env(tmp_path)
    human=subprocess.run([*REFS_COMMAND,'add','--format','refs','--input',str(path)],env=env,capture_output=True,text=True)
    assert human.returncode==2
    assert human.stderr.startswith('context: Input should be a valid array;')
    assert len(human.stderr.splitlines())==1


def test_csl_validation_details_use_metadata_path(initialized,tmp_path):
    path=tmp_path/'invalid.json'
    path.write_text(json.dumps({'type':'book','title':'Synthetic Book','author':'not a list'}))
    result=initialized('add','--format','csljson','--input',path,expected=2)
    issue=result['errors'][0]['details']['issues'][0]
    assert issue['loc']==['metadata','author'] and 'valid list' in issue['msg']
