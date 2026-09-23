import json
import unicodedata

import pytest

from refs.catalog import connect
from refs.display import readable


def test_loc_capture_edit_clear_and_filter(initialized, tmp_path, reference_path):
    cli = initialized
    loc = unicodedata.normalize('NFD', 'Papers/Café')
    item = cli('add', '--format', 'refs', '--input', reference_path, '--loc', loc)['data']
    assert item['loc'] == 'Papers/Café'
    assert 'loc: Papers/Café' in readable('show', item)
    assert cli('list', '--loc', 'papers/café')['data']['total'] == 1
    assert cli('search', item['citation_key'], '--loc', 'PAPERS/CAFÉ')['data']['total'] == 1
    assert cli('list', '--loc', 'papers')['data']['total'] == 0
    changed = cli('update', item['id'], '--if-revision', item['revision'], '--set', 'loc="Other"')['data']
    assert changed['loc'] == 'Other' and 'loc' not in changed['corrected_fields']
    cli('update', item['id'], '--if-revision', item['revision'], '--set', 'loc="Stale"', expected=3)
    patch = tmp_path/'clear.json'
    patch.write_text(json.dumps({'schema_version':'1.0', 'clear':['loc']}))
    cleared = cli('update', item['id'], '--if-revision', changed['revision'], '--patch', patch)['data']
    assert cleared.get('loc') is None and 'loc' not in cleared['corrected_fields']
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT loc FROM sources').fetchone()[0] is None


@pytest.mark.parametrize('loc', ['/absolute', '../up', 'a/../b', 'a//b', '.', 'a/./b'])
def test_invalid_loc_does_not_create(initialized, reference_path, loc):
    initialized('add', '--format', 'refs', '--input', reference_path, '--loc', loc, expected=2)
    assert initialized('list')['data']['total'] == 0


def test_loc_preview_and_unplaced(initialized, reference_path):
    preview = initialized('add', '--format', 'refs', '--input', reference_path, '--loc', 'Topic', '--dry-run')['data']
    assert preview.get('loc', preview.get('record', {}).get('loc')) == 'Topic'
    assert initialized('list')['data']['total'] == 0
    item = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    assert item.get('loc') is None


def test_loc_does_not_change_repeat_capture(initialized, reference_path):
    first = initialized('add', '--format', 'refs', '--input', reference_path, '--loc', 'Topic')['data']
    repeat = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    assert repeat['id'] == first['id']
    assert repeat['loc'] == 'Topic' and repeat['revision'] == first['revision']
    assert repeat['outcome'] == 'already_present'
