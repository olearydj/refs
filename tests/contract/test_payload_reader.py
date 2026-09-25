"""Payload path errors stay input errors, and all payload routes accept stdin."""

import json
import sqlite3
import subprocess
import sys

import pytest
from conftest import REFS_COMMAND

from refs import cli


def test_missing_payloads_report_invalid_input_path(initialized,tmp_path,reference_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    missing=tmp_path/'missing.json'
    commands=[('add','--format','refs','--input',missing),
              ('import','--format','bib','--input',missing),
              ('update',source['id'],'--if-revision',1,'--patch',missing)]
    for command in commands:
        result=initialized(*command,expected=2)
        assert result['errors'][0]['code']=='invalid_input'
        assert result['errors'][0]['path']==str(missing)
    assert initialized('show',source['id'])['data']['revision']==1


def test_add_import_and_patch_read_stdin(initialized,cli_env,cli_cwd,reference_path):
    def run(args,payload):
        process=subprocess.run([*REFS_COMMAND,'--json',*args],input=payload,env=cli_env,cwd=cli_cwd,capture_output=True)
        assert process.returncode==0,process.stderr
        return json.loads(process.stdout)['data']
    source=run(['add','--format','refs','--input','-'],reference_path.read_bytes())
    updated=run(['update',source['id'],'--if-revision','1','--patch','-'],
                b'{"schema_version":"1.0","set":{"metadata.volume":"2"}}')
    assert updated['metadata']['volume']=='2'
    imported=run(['import','--format','bib','--input','-'],b'@book{stdin2024,title={Stdin Work}}')
    assert imported['counts']['applied']==1 and imported['input']=='stdin'


@pytest.mark.parametrize(('code','expected_code','exit_code'),[(sqlite3.SQLITE_ERROR,'storage_error',5),
                                                                (sqlite3.SQLITE_BUSY,'lock_timeout',6)])
def test_sqlite_lock_detection_uses_error_code(initialized,tmp_path,monkeypatch,capsys,code,expected_code,exit_code):
    error=sqlite3.OperationalError('database is locked' if code==sqlite3.SQLITE_ERROR else 'opaque failure')
    error.sqlite_errorcode=code
    def fail(**kwargs):
        raise error
    monkeypatch.setattr(cli,'app',fail)
    monkeypatch.setattr(sys,'argv',['refs','--json','--no-project-config','--config',str(tmp_path/'config.toml'),
                                   '--catalog',str(tmp_path/'cat'),'list'])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code==exit_code
    result=json.loads(capsys.readouterr().out)
    assert result['errors'][0]['code']==expected_code
