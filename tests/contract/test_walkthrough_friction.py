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



def test_show_reports_preserved_howpublished(human, initialized, tmp_path):
    path=tmp_path/'entry.bib'
    path.write_text('@misc{example,title={Study},howpublished={arXiv:2407.01502},year={2024},author={Smith, Alex}}')
    initialized('import','--input',path)
    text=human('show','example')
    assert 'Limitations:\n  Preserved from import: howpublished' in text
    initialized('project','create','paper')
    initialized('project','cite','paper','example')
    report=initialized('export','--project','paper','--output',tmp_path/'out.bib')
    assert 'howpublished = {arXiv:2407.01502}' in (tmp_path/'out.bib').read_text()
    assert not any(w['code']=='unassessed_import' for w in report['warnings'])



def test_project_show_uses_key_sorted_list_rows(human, initialized, tmp_path, reference_path):
    initialized('add','--format','refs','--input',reference_path)
    path=tmp_path/'other.bib'
    path.write_text('@book{alpha,title={Zebra Study},author={Jones, Alex},year={2025}}')
    initialized('import','--input',path)
    initialized('project','create','paper')
    for key in ('smith-2024-learningPython','alpha'):
        initialized('project','cite','paper',key)
    assert human('project','show','paper').splitlines()[1:] == human('list','--sort','key').splitlines()
    assert human('project','show','paper').splitlines()[1].startswith('alpha | Alex Jones | 2025 | Zebra Study')
