import json
import sqlite3


def test_outcomes_update_clear_rekey_and_tombstones(initialized, tmp_path, reference_path):
    first = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    assert first['outcome'] == 'created'
    again = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    assert again['outcome'] == 'already_present'
    key = first['citation_key']
    changed = initialized('update', key, '--if-revision', 1, '--set', 'metadata.volume="13"')['data']
    assert changed['revision'] == 2
    assert changed['id'] == first['id']
    error = initialized('update', key, '--if-revision', 1, '--set', 'metadata.volume="14"', expected=3)
    assert error['errors'][0]['code'] == 'stale_revision'
    patch = tmp_path / 'patch.json'
    patch.write_text(json.dumps({'schema_version': '1.0', 'clear': ['metadata.DOI']}))
    changed = initialized('update', key, '--if-revision', 2, '--patch', patch)['data']
    assert 'DOI' not in changed['metadata']
    assert 'metadata.DOI' in changed['corrected_fields']
    db = tmp_path / 'cat/catalog.sqlite'
    before = db.read_bytes()
    initialized('key', 'set', key, '--key', 'new-key', '--if-revision', 3)
    assert db.read_bytes() == before
    initialized('key', 'set', key, '--key', 'new-key', '--if-revision', 3, '--execute')
    initialized('remove', 'new-key', '--if-revision', 4, '--execute')
    assert initialized('show', first['id'])['data']['state'] == 'removed'
    initialized('reactivate', first['id'], '--if-revision', 5, '--execute')
    assert initialized('show', first['id'])['data']['citation_key'] == 'new-key'
    with sqlite3.connect(db) as connection:
        assert connection.execute('SELECT raw_bytes FROM originals').fetchone()[0] == reference_path.read_bytes()


def test_conflict_reports_attention(initialized, tmp_path, reference_path):
    original = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    value = json.loads(reference_path.read_text())
    value['metadata']['title'] = 'Contradictory Work'
    path = tmp_path / 'conflict.json'
    path.write_text(json.dumps(value))
    result = initialized('add', '--format', 'refs', '--input', path, expected=3)
    assert result['data']['outcome'] == 'needs_attention'
    assert original['id'] in result['errors'][0]['details']['source_ids']



def test_title_edit_retires_old_protection_but_checks_supplied_terms(initialized, tmp_path):
    import json

    from refs import sources
    raw = {'schema_version':'1.0','metadata':{'title':'An API Study'},'title_protection':{'title':{'protected_terms':['API']}}}
    source = sources.add(tmp_path/'cat',json.dumps(raw).encode(),'synthetic')
    changed = sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'metadata.title':'Different Study'}},1)
    assert changed['title_protection']['title']['protected_terms'] == []
    assert not any(w['code']=='protected_term_missing' for w in changed['warnings'])
    supplied = sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'title_protection.title.protected_terms':['Missing']}},2)
    assert any(w['code']=='protected_term_missing' for w in supplied['warnings'])
