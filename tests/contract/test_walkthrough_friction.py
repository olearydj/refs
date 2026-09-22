"""Regressions from the owner's slice 1 walkthrough, in isolated homes."""
import os
import subprocess

import pytest


@pytest.fixture
def human(initialized, tmp_path):
    def run(*args, expected=0):
        result = subprocess.run(['refs', '--no-project-config', *map(str,args)], env=dict(os.environ, REFS_CONFIG=str(tmp_path/'config.toml'), REFS_CATALOG=str(tmp_path/'cat')), capture_output=True, text=True)
        assert result.returncode == expected, result.stdout + result.stderr
        return result.stdout + result.stderr
    return run


def test_add_file_confirms_copy(human, reference_path, tmp_path):
    path = tmp_path/'download.pdf'
    path.write_bytes(b'synthetic file')
    text = human('add','--format','refs','--input',reference_path,'--file',path)
    assert text.splitlines()[:2] == ['Created smith-2024-learningPython', f"Copied {path} to {tmp_path/'lib/Unfiled/LearningPython-2024.pdf'} for smith-2024-learningPython"]
    assert path.read_bytes() == b'synthetic file'



def test_show_exposes_all_populated_metadata(human, initialized, reference_path):
    initialized('add','--format','refs','--input',reference_path)
    initialized('update','smith-2024-learningPython','--if-revision',1,'--set','metadata.publisher="Example Press"','--set','metadata.edition=2','--set','metadata.genre="Tutorial"','--set','metadata.event-title="Annual Meeting"')
    text = human('show','smith-2024-learningPython')
    lines = text.splitlines()
    assert lines[:5] == ['Key: smith-2024-learningPython','Type: article-journal','Authors: Alex Smith','Year: 2024','Title: Learning Python']
    for field,value in [('publisher','Example Press'),('edition','2'),('genre','Tutorial'),('event-title','Annual Meeting'),('language','en'),('issued','2024')]:
        assert f'{field}: {value}' in lines
    labels=[line.split(':')[0] for line in lines[5:lines.index('Files: (none)')]]
    assert labels == sorted(labels)
