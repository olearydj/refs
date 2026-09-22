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



def test_export_warning_keys_groups_and_info(human, initialized, tmp_path):
    path=tmp_path/'entries.bib'
    path.write_text('\n'.join('@misc{'+key+',title={The R Package '+key+'},author={Smith, Alex},year={2024}}' for key in ('four','one','three','two')))
    initialized('import','--input',path)
    initialized('project','create','paper')
    for key in ('four','one','three','two'):
        initialized('project','cite','paper',key)
    text=human('export','--project','paper','--output',tmp_path/'out.bib')
    assert text.splitlines()[1:] == ['Warning: 4 entries use the portable @misc fallback (four, one, three, two)']
    data=initialized('export','--project','paper','--output',tmp_path/'out.bib')
    assert len(data['warnings']) == 4
    assert len(data['data']['info']) == 4
    assert all(item['details']['class']=='info' for item in data['data']['info'])
    initialized('project','create','single')
    initialized('project','cite','single','one')
    assert 'Warning: one: document is projected as @misc' in human('export','--project','single','--output',tmp_path/'single.bib')


def test_paths_and_config_keep_their_distinct_formats(human, tmp_path):
    assert human('paths').splitlines() == [f'Configuration: {tmp_path/"config.toml"}', f'Catalog: {tmp_path/"cat"}', f'Library: {tmp_path/"lib"}']
    text = human('config', 'show')
    assert text.startswith(f'Configuration: {tmp_path/"config.toml"}\n')
    assert f'catalog.path = {tmp_path/"cat"} (REFS_CATALOG)' in text
    assert f'resources.library_root = {tmp_path/"lib"} ({tmp_path/"config.toml"})' in text


def test_empty_export_warns_and_requires_overwrite(human, initialized, reference_path, tmp_path):
    initialized('project','create','paper')
    output=tmp_path/'empty.bib'
    result=initialized('export','--project','paper','--output',output)
    assert result['warnings'][0]['code']=='empty_selection'
    assert output.read_bytes()==b''
    assert f'Wrote {output} (0 entries)' in human('export','--project','paper','--output',output)
    initialized('add','--format','refs','--input',reference_path)
    initialized('project','cite','paper','smith-2024-learningPython')
    initialized('export','--project','paper','--output',output)
    original=output.read_bytes()
    initialized('project','uncite','paper','smith-2024-learningPython')
    for options in ([], ['--dry-run']):
        refused=initialized('export','--project','paper','--output',output,*options,expected=3)
        assert refused['errors'][0]['code']=='outside_edit'
        assert output.read_bytes()==original
    initialized('export','--project','paper','--output',output,'--overwrite')
    assert output.read_bytes()==b''
