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


def test_resource_copy_collision_exits_three(human, initialized, reference_path, tmp_path):
    initialized('add','--format','refs','--input',reference_path)
    source=tmp_path/'download.pdf'
    source.write_bytes(b'synthetic original')
    copied=initialized('resource','add','smith-2024-learningPython','--path',source,'--copy')['data']
    source.write_bytes(b'different file, same destination')
    text=human('resource','add','smith-2024-learningPython','--path',source,'--copy',expected=3)
    assert 'existing destination' in text
    result=initialized('resource','add','smith-2024-learningPython','--path',source,'--copy',expected=3)
    assert result['errors'][0]['code']=='destination_exists'
    from pathlib import Path
    assert Path(copied['destination']).read_bytes()==b'synthetic original'
    assert source.read_bytes()==b'different file, same destination'


def test_backup_creates_missing_parents(human, tmp_path):
    from refs.recovery import validate_snapshot
    target=tmp_path/'new'/'nested'/'snapshot'
    human('backup','--output',target,'--dry-run')
    assert not target.parent.exists()
    assert human('backup','--output',target).splitlines()[0]==f'Wrote snapshot {target} (external file bytes excluded)'
    assert validate_snapshot(target)['format']=='refs-backup'


def test_unlink_previews_without_revision_and_is_idempotent(human, initialized, reference_path, tmp_path):
    source=initialized('add','--format','refs','--input',reference_path)['data']
    path=tmp_path/'linked.pdf'
    path.write_bytes(b'untouched original')
    resource=initialized('resource','add',source['id'],'--path',path)['data']
    assert human('resource','unlink',resource['id']).startswith(f'Preview: Unlinked {path}')
    assert len(initialized('show',source['id'])['data']['resources'])==1
    assert human('resource','unlink',resource['id'],'--execute').startswith(f'Unlinked {path}')
    assert initialized('show',source['id'])['data']['resources']==[]
    assert 'already unlinked' in human('resource','unlink',resource['id'],'--execute')
    assert path.read_bytes()==b'untouched original'


def test_shared_configuration_writer_preserves_nested_values():
    import tomllib

    from refs.config import toml_text
    values={'schema_version':1, 'catalog':{'path':'/temporary/catalog'}, 'keys':{'stopwords':['a','is'], 'corporate_aliases':{'Research and Design':'rnd','Üniversity':'uni'}}}
    text=toml_text(values)
    assert text.startswith('schema_version = 1\n[catalog]\npath = ')
    assert '[keys.corporate_aliases]' in text
    assert tomllib.loads(text)==values


def test_key_prefix_search_keeps_exact_matches_first(human, initialized, tmp_path):
    path=tmp_path/'entries.bib'
    path.write_text('@book{koster2012,title={Alpha Work},author={Smith, Alex},year={2012}}\n@book{koster,title={Zebra Work},author={Smith, Alex},year={2024}}')
    initialized('import','--input',path)
    items=initialized('search','koster')['data']['items']
    assert [item['citation_key'] for item in items]==['koster','koster2012']
    assert [item['exact_match'] for item in items]==[True,False]
    assert items[1]['matches'][0]['field']=='citation_key'
    assert 'matched: citation_key' in human('search','koster').splitlines()[1]
    assert initialized('search','kost er')['data']['items']==[]


def test_cite_from_import_applied_active_only(human, initialized, tmp_path):
    path=tmp_path/'entries.bib'
    path.write_text('\n'.join('@book{'+key+',title={Study '+key+'},author={Smith, Alex},year={2024}}' for key in ('one','two','removed')))
    initialized('import','--input',path,'--origin','first')
    initialized('import','--input',path,'--origin','unchanged-only')
    initialized('remove','removed','--if-revision',1,'--execute')
    path.write_text('@book{one,title={Conflicting title},author={Smith, Alex},year={2024}}')
    initialized('import','--input',path,'--origin','conflicts-only',expected=4)
    initialized('project','create','paper')
    for origin in ('unchanged-only','conflicts-only'):
        assert human('project','cite','paper','--from-import',origin).strip()=='Cited 0 in paper (0 already cited)'
    assert human('project','cite','paper','--from-import','first','--dry-run').strip()=='Preview: Cited 2 in paper (0 already cited)'
    assert initialized('project','show','paper')['data']['sources']==[]
    initialized('project','cite','paper','one')
    assert human('project','cite','paper','--from-import','first').strip()=='Cited 1 in paper (1 already cited)'
    assert human('project','cite','paper','--from-import','first').strip()=='Cited 0 in paper (2 already cited)'
    assert [s['citation_key'] for s in initialized('project','show','paper')['data']['sources']]==['one','two']
    initialized('project','cite','paper','one','--from-import','first',expected=2)
    initialized('project','cite','paper','--from-import','missing',expected=3)


def test_cite_from_legacy_import_uses_creation_time(initialized, tmp_path):
    import sqlite3
    path=tmp_path/'entries.bib'
    path.write_text('@book{legacy,title={Old Import},author={Smith, Alex},year={2024}}')
    initialized('import','--input',path,'--origin','original')
    initialized('import','--input',path,'--origin','later')
    # Reproduce the previous on-disk evidence shape in this synthetic catalog.
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        connection.execute('DROP TRIGGER originals_no_update')
        connection.execute("UPDATE originals SET definitions_json=json_remove(definitions_json,'$.import_id')")
    initialized('project','create','paper')
    assert initialized('project','cite','paper','--from-import','later')['data']['cited']==0
    assert initialized('project','cite','paper','--from-import','original')['data']['cited']==1


def test_effective_stopwords_change_only_future_keys(human, initialized, tmp_path):
    import json

    from refs.naming import STOPWORDS
    path=tmp_path/'record.json'
    value={'schema_version':'1.0','metadata':{'title':'Is Science Useful','author':[{'family':'Smith','given':'Alex'}],'issued':{'date-parts':[[2024]]}}}
    path.write_text(json.dumps(value))
    original=initialized('add','--format','refs','--input',path)['data']
    assert original['citation_key']=='smith-2024-isScience'
    config=tmp_path/'config.toml'
    words=sorted(STOPWORDS|{'is'})
    config.write_text(config.read_text()+'\n[keys]\nstopwords = '+json.dumps(words)+'\n')
    assert f'keys.stopwords = {words} ({config})' in human('config','show')
    assert initialized('config','show')['data']['values']['keys.stopwords']==words
    value['metadata']['author'][0]['family']='Jones'
    path.write_text(json.dumps(value))
    assert initialized('add','--format','refs','--input',path)['data']['citation_key']=='jones-2024-scienceUseful'
    changed=initialized('update',original['id'],'--if-revision',1,'--set','metadata.publisher="Example Press"')['data']
    assert changed['citation_key']==original['citation_key']
    assert initialized('show',original['id'])['data']['key_provenance']==original['key_provenance']
