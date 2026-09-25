import json

import pytest

from refs.results import RefError, emit


def test_usage_failure_is_json(cli):
    result = cli("not-a-command", expected=2)
    assert result["status"] == "error"
    assert result["errors"][0]["code"] == "invalid_invocation"
    assert set(result) == {"schema_version", "command", "status", "data", "warnings", "errors"}


def test_failure_envelopes_name_leaf_commands(initialized):
    assert initialized('show','missing',expected=3)['command']=='show'
    assert initialized('project','cite','missing','source',expected=3)['command']=='project cite'
    assert initialized('resource','add','missing','--path','/missing',expected=3)['command']=='resource add'


def test_bare_group_has_one_json_envelope_and_help_on_stderr(initialized,cli_env,cli_cwd):
    import subprocess

    from conftest import REFS_COMMAND

    result=subprocess.run([*REFS_COMMAND,'--json','project'],env=cli_env,cwd=cli_cwd,capture_output=True,text=True)
    assert result.returncode==2
    envelope=json.loads(result.stdout)
    assert envelope['command']=='project' and envelope['errors'][0]['code']=='invalid_invocation'
    assert 'Usage' in result.stderr and 'Usage' not in result.stdout


def test_unexpected_service_error_has_envelope_without_traceback(initialized,tmp_path,monkeypatch,capsys):
    import sys

    from refs import cli

    def fail(*args):
        raise KeyError('synthetic fault')
    monkeypatch.setattr(cli.resources,'inspect_source',fail)
    monkeypatch.setattr(sys,'argv',['refs','--json','--no-project-config','--config',str(tmp_path/'config.toml'),
                                   '--catalog',str(tmp_path/'cat'),'show','missing'])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    assert caught.value.code==5
    result=json.loads(capsys.readouterr().out)
    assert result['command']=='show' and result['errors'][0]['code']=='internal_error'
    assert 'synthetic fault' not in json.dumps(result)


def test_integrity_error_exits_five_with_command(initialized,tmp_path,monkeypatch,capsys):
    import sys

    from refs import cli

    def fail(*args):
        raise RefError('integrity_error', 'Published bytes differ')
    monkeypatch.setattr(cli.resources, 'inspect_source', fail)
    monkeypatch.setattr(sys, 'argv', ['refs', '--json', '--no-project-config', '--config', str(tmp_path/'config.toml'),
                                     '--catalog', str(tmp_path/'cat'), 'show', 'source'])
    with pytest.raises(SystemExit) as caught:
        cli.main()
    result = json.loads(capsys.readouterr().out)
    assert caught.value.code == 5
    assert result['command'] == 'show' and result['errors'][0]['code'] == 'integrity_error'


@pytest.mark.parametrize("exit_code", [2, 3, 4, 5, 6])
def test_error_envelope(exit_code, capsys):
    error = RefError("example", "An explanation", exit_code, path="/temporary", retryable=exit_code == 6)
    emit("example", error=error, json_output=True)
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == ("partial" if exit_code == 4 else "error")
    assert result["errors"] == [{"code": "example", "message": "An explanation", "path": "/temporary", "details": {}, "retryable": exit_code == 6}]


def test_human_output(capsys):
    emit("project create", {"name": "café"})
    assert "café" in capsys.readouterr().out



def test_export_block_names_the_citation_key(capsys):
    from refs.results import RefError, emit
    error = RefError('export_blocked','Correct the date',path='synthetic.bib',details={'entries':[{'citation_key':'smith-2024','message':'Issued range cannot be projected'}]})
    emit('export',error=error)
    assert 'smith-2024: Issued range cannot be projected' in capsys.readouterr().err
