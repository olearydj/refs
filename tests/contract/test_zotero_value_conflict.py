"""A Zotero binding conflict has the same named code as a BibTeX conflict."""

import json
import shutil
from pathlib import Path

from refs.catalog import connect


def test_zotero_value_conflict_names_code_and_keeps_current_title(initialized, tmp_path):
    existing = tmp_path/'existing.json'
    existing.write_text(json.dumps({'schema_version':'1.0', 'citation_key':'current2020',
        'metadata':{'type':'article-journal', 'title':'Current Title', 'DOI':'10.5555/zotero-value-conflict',
                    'author':[{'family':'Example','given':'Ada'}]}}))
    source_id = initialized('add', '--format', 'refs', '--input', existing)['data']['id']
    directory = tmp_path/'zotero'
    (directory/'items').mkdir(parents=True)
    fixture = Path(__file__).parents[1]/'fixtures/real-trial/minimized/zotero-value-conflict.json'
    shutil.copy2(fixture, directory/'items/CONFL001.json')
    (directory/'collections.json').write_text('[]')
    (directory/'manifest.json').write_text(json.dumps({'format':'refs-zotero-input', 'version':1, 'api_version':3,
        'library_uri':'users/local/FIXTURE', 'zotero_version':'6', 'userdata_version':1, 'global_version':1,
        'extractor_version':'test', 'data_directory':str(directory), 'base_path':str(directory)}))

    first = initialized('import', '--format', 'zotero', '--input', directory, expected=4)['data']
    entry = first['entries'][0]
    assert entry['status'] == 'conflict'
    assert entry['code'] == 'value_conflict'
    assert 'metadata.title' in entry['conflicts']
    assert entry['source_id'] == source_id
    again = initialized('import', '--format', 'zotero', '--input', directory, expected=4)['data']
    assert again['entries'][0]['code'] == 'value_conflict'
    assert again['counts']['applied'] == 0
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 1
        stored = json.loads(connection.execute('SELECT metadata_json FROM sources WHERE id=?', (source_id,)).fetchone()[0])
    assert stored['title'] == 'Current Title'
