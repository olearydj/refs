import json

import pytest

from refs.results import RefError, emit


def test_usage_failure_is_json(cli):
    result = cli("not-a-command", expected=2)
    assert result["status"] == "error"
    assert result["errors"][0]["code"] == "invalid_invocation"
    assert set(result) == {"schema_version", "command", "status", "data", "warnings", "errors"}


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
