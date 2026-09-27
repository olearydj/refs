"""Unnamed catalog links are symmetric, guarded and absent from exports."""

import json
import sqlite3
from copy import deepcopy

import pytest

from refs import bibliography, sources
from refs import logging as action_log
from refs.results import RefError


@pytest.fixture
def pair(initialized, tmp_path):
    records = []
    for key in ('left', 'right'):
        path = tmp_path / (key + '.json')
        path.write_text(json.dumps({'schema_version': '1.0', 'citation_key': key,
                                    'metadata': {'type': 'book', 'title': key.title() + ' Work'}}))
        records.append(initialized('add', '--format', 'refs', '--input', path)['data'])
    return records


def link_events(tmp_path):
    return [json.loads(line) for line in (tmp_path/'cat/refs.log').read_text().splitlines()
            if json.loads(line)['event'] in ('source.link', 'source.unlink')]


def test_link_and_unlink_are_visible_from_either_endpoint(initialized, pair, human):
    left, right = pair
    linked = initialized('update', 'left', '--link', right['id'], '--if-revision', 1)['data']
    assert linked['links'] == [{'id': right['id'], 'citation_key': 'right', 'title': 'Right Work', 'state': 'active'}]
    reverse = initialized('show', 'right')['data']
    assert reverse['links'] == [{'id': left['id'], 'citation_key': 'left', 'title': 'Left Work', 'state': 'active'}]
    assert linked['revision'] == reverse['revision'] == 2
    assert 'left: Left Work' in human('show', 'right')
    unlinked = initialized('update', right['id'], '--unlink', 'left', '--if-revision', 2)['data']
    assert unlinked['links'] == initialized('show', 'left')['data']['links'] == []
    assert unlinked['revision'] == initialized('show', 'left')['data']['revision'] == 3


def test_duplicate_and_absent_links_are_byte_preserving_noops(initialized, pair, tmp_path):
    initialized('update', 'left', '--link', 'right')
    db = tmp_path/'cat/catalog.sqlite'
    before = db.read_bytes()
    events = link_events(tmp_path)
    assert initialized('update', 'right', '--link', 'left')['data']['unchanged']
    assert db.read_bytes() == before and link_events(tmp_path) == events
    initialized('update', 'right', '--unlink', 'left')
    before = db.read_bytes()
    events = link_events(tmp_path)
    assert initialized('update', 'left', '--unlink', 'right')['data']['unchanged']
    assert db.read_bytes() == before and link_events(tmp_path) == events


@pytest.mark.parametrize('unlink', [False, True])
def test_link_preview_never_changes_either_record(initialized, pair, tmp_path, unlink):
    if unlink:
        initialized('update', 'left', '--link', 'right')
    db = tmp_path/'cat/catalog.sqlite'
    before, events = db.read_bytes(), link_events(tmp_path)
    result = initialized('update', 'right', '--unlink' if unlink else '--link', 'left', '--dry-run')['data']
    assert result['dry_run'] and bool(result['links']) != unlink
    assert db.read_bytes() == before and link_events(tmp_path) == events


def test_link_changes_invalidate_both_endpoint_revision_guards(initialized, pair, tmp_path):
    initialized('update', 'left', '--link', 'right', '--if-revision', 1)
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    for key, other in [('left', 'right'), ('right', 'left')]:
        error = initialized('update', key, '--unlink', other, '--if-revision', 1, expected=3)
        assert error['errors'][0]['code'] == 'stale_revision'
        assert error['errors'][0]['details'] == {'expected': 1, 'actual': 2}
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before


@pytest.mark.parametrize('args,code,exit_code', [
    (['--link', 'left'], 'invalid_link', 2),
    (['--unlink', 'left'], 'invalid_link', 2),
    (['--link', 'missing'], 'source_missing', 3),
    (['--unlink', 'missing'], 'source_missing', 3),
    (['--link', 'right', '--unlink', 'right'], 'invalid_invocation', 2),
    (['--link', 'right', '--set', 'metadata.title="Changed"'], 'invalid_invocation', 2),
    (['--link', 'right', '--patch', 'not-read.json'], 'invalid_invocation', 2),
    (['--link', 'right', '--kind', 'repository'], 'invalid_invocation', 2),
])
def test_invalid_link_invocations_preserve_catalog(initialized, pair, tmp_path, args, code, exit_code):
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    result = initialized('update', 'left', *args, expected=exit_code)
    assert result['errors'][0]['code'] == code
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before
    assert link_events(tmp_path) == []


def test_link_log_records_both_revisions_and_the_relationship(initialized, pair, tmp_path):
    left, right = pair
    initialized('update', 'left', '--link', 'right')
    event = link_events(tmp_path)[-1]
    assert event['event'] == 'source.link'
    assert event['target'] == {'id': left['id'], 'citation_key': 'left', 'other_id': right['id']}
    assert event['before'] == {'revisions': {left['id']: 1, right['id']: 1}}
    assert event['after'] == {'revisions': {left['id']: 2, right['id']: 2}}
    assert event['changes'] == {'linked': {'old': False, 'new': True}}
    initialized('update', 'left', '--unlink', 'right')
    assert link_events(tmp_path)[-1]['event'] == 'source.unlink'
    assert link_events(tmp_path)[-1]['changes'] == {'linked': {'old': True, 'new': False}}


def test_unwritable_link_log_refuses_before_catalog_mutation(initialized, pair, tmp_path, monkeypatch):
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    def fail(*args, **kwargs):
        raise RefError('log_unwritable', 'Injected durable log failure', 5)
    monkeypatch.setattr(action_log, 'log_mutation', fail)
    with pytest.raises(RefError) as caught:
        sources.change_link(tmp_path/'cat', 'left', 'right', 1)
    assert caught.value.issue['code'] == 'log_unwritable' and caught.value.exit_code == 5
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before


def test_endpoint_failure_rolls_back_link_and_both_revisions(initialized, pair, tmp_path):
    right = pair[1]
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as db:
        db.execute(f"CREATE TRIGGER refuse_right BEFORE UPDATE ON sources WHEN NEW.id='{right['id']}' BEGIN SELECT RAISE(ABORT, 'injected endpoint failure'); END")
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    with pytest.raises(sqlite3.IntegrityError, match='injected endpoint failure'):
        sources.change_link(tmp_path/'cat', 'left', 'right', 1)
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before


def test_zotero_links_are_symmetric_deduplicated_and_unlinked_together(initialized, pair, tmp_path):
    left, right = pair
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as db:
        db.executemany('INSERT INTO source_relations VALUES (?,?,?,?)', [
            (left['id'], 'users/1/items/RIGHT', right['id'], 'users/1'),
            (right['id'], 'users/1/items/LEFT', left['id'], 'users/1'),
            (left['id'], 'users/1/items/UNKNOWN', None, 'users/1')])
    assert len(initialized('show', 'left')['data']['links']) == 1
    assert len(initialized('show', 'right')['data']['links']) == 1
    assert initialized('update', 'right', '--link', 'left')['data']['unchanged']
    initialized('update', 'right', '--unlink', 'left')
    assert initialized('show', 'left')['data']['links'] == []
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as db:
        assert db.execute('SELECT target_uri FROM source_relations').fetchall() == [('users/1/items/UNKNOWN',)]


def test_links_follow_rekeys_and_survive_removal(initialized, pair, human):
    initialized('update', 'left', '--link', 'right')
    initialized('key', 'set', 'right', '--key', 'renamed', '--if-revision', 2, '--execute')
    initialized('remove', 'renamed', '--if-revision', 3, '--execute')
    links = initialized('show', 'left')['data']['links']
    assert len(links) == 1 and links[0]['citation_key'] == 'renamed' and links[0]['state'] == 'removed'
    assert '[removed]' in human('show', 'left')
    assert initialized('show', 'renamed')['data']['links'][0]['citation_key'] == 'left'


@pytest.mark.parametrize('profile', bibliography.PROFILES)
def test_links_never_enter_bibliography_output(initialized, pair, profile):
    before = deepcopy(pair)
    initialized('update', 'left', '--link', 'right')
    after = [initialized('show', key)['data'] for key in ('left', 'right')]
    if profile == 'csl-json-v1':
        assert bibliography.serialize_csl(before) == bibliography.serialize_csl(after)
    else:
        assert bibliography.serialize(before, profile=profile) == bibliography.serialize(after, profile=profile)
