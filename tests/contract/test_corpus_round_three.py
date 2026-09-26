"""The mixed corpus gate must preserve fixture facts and account for every CSL element."""

import importlib
import json
import sqlite3
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from refs.adapters import zotero
from refs.catalog import connect
from refs.config import select, toml_text


def harness(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / 'fixtures' / 'real-trial'))
    return importlib.import_module('corpus_round_three')


def test_bbt_native_wrapper_keeps_items_and_children_inside_disposable_directory(tmp_path, monkeypatch):
    corpus = harness(monkeypatch)
    fixture = tmp_path/'source.json'
    fixture.write_text(json.dumps({'items':[{'itemType':'book', 'title':'Fixture book', 'itemID':17,
        'extra':['First line: one','Second line: two'],
        'attachments':[{'itemType':'attachment', 'path':'/external/not-read.pdf', 'linkMode':'linked_file'}],
        'notes':['<p>Fixture note</p>']}],
        'collections':{'coll:1':{'name':'Fixture collection'}}}))
    original = fixture.read_bytes()
    directory = tmp_path/'extracted'
    assert corpus.materialize_zotero(fixture,directory) == 1
    bundle = zotero.read(directory)
    assert fixture.read_bytes() == original
    assert sorted(item['data']['itemType'] for item in bundle['items']) == ['attachment','book','note']
    parent = next(item for item in bundle['items'] if item['data']['itemType'] == 'book')
    attachment = next(item for item in bundle['items'] if item['data']['itemType'] == 'attachment')
    note = next(item for item in bundle['items'] if item['data']['itemType'] == 'note')
    assert parent['data']['title'] == 'Fixture book'
    assert parent['data']['extra'] == 'First line: one\nSecond line: two'
    assert attachment['data']['parentItem'] == parent['key']
    assert Path(attachment['data']['path']).is_relative_to(directory)
    assert zotero.context(note['item']) == 'Fixture note'
    assert bundle['collections'][0]['data']['name'] == 'Fixture collection'


def test_csl_array_worker_counts_each_add_and_readd(initialized, tmp_path, monkeypatch):
    harness(monkeypatch)
    worker = importlib.import_module('corpus_csl_worker')
    source = tmp_path/'array.json'
    book = {'id':'fixture-book', 'type':'book', 'title':'A Fixture Book', 'author':[{'family':'Example','given':'Ada'}], 'issued':{'date-parts':[[2020]]}}
    source.write_text(json.dumps([book, book, {'type':'not-a-csl-type', 'title':'Invalid'}]))
    result = worker.run(tmp_path/'config.toml', tmp_path/'cat', source, 'array-fixture')
    assert result['outcomes'] == {'created':1, 'already_present':1, 'invalid':1}
    assert result['reimport'] == {'already_present':2, 'invalid':1}
    assert result['cited_sources'] == 1
    assert result['source_rows_added'] == 1
    assert result['entry_codes']['invalid_record'] == 1


def test_csl_large_array_uses_import_and_small_array_keeps_add(initialized, tmp_path, monkeypatch):
    corpus = harness(monkeypatch)
    monkeypatch.setattr(importlib.import_module('move_rehearsal'), 'sandboxed', lambda command: command)
    monkeypatch.setattr(corpus, 'sandboxed', lambda command: command)
    settings = select(str(tmp_path/'config.toml'), str(tmp_path/'cat'), no_project_config=True)
    monkeypatch.setattr(corpus, 'render_export', lambda *args: dict(export=dict(skipped='focused route test')))
    item = {'id':'batch-book', 'type':'book', 'title':'A Batch Book', 'author':[{'family':'Example','given':'Ada'}], 'issued':{'date-parts':[[2020]]}}
    large = tmp_path/'large.json'
    large.write_text(json.dumps([item]*50))
    result = corpus.gate_file(settings, tmp_path, 0, dict(path=str(large), kind='csl_array', entries=50), lambda: 30)
    assert result['outcomes'] == {'applied':1, 'unchanged':49, 'conflict':0, 'invalid':0}
    assert result['reimport'] == {'applied':0, 'unchanged':50, 'conflict':0, 'invalid':0}
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM import_entries').fetchone()[0] == 100
    small = tmp_path/'small.json'
    small.write_text(json.dumps([item]))
    result = corpus.gate_file(settings, tmp_path, 1, dict(path=str(small), kind='csl_array', entries=1), lambda: 30)
    assert result['outcomes'] == {'already_present':1}
    assert result['reimport'] == {'already_present':1}
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM import_entries').fetchone()[0] == 100


def test_json_gate_resumes_after_file_deadline_without_replaying_completed_file(tmp_path, monkeypatch):
    corpus = harness(monkeypatch)
    sample, work = tmp_path/'sample', tmp_path/'work'
    sample.mkdir()
    work.mkdir()
    files = [tmp_path/f'{index}.json' for index in range(2)]
    for path in files:
        path.write_text('{"id":0,"result":{}}')
    manifest = work/'manifest.json'
    manifest.write_text(json.dumps(dict(ceilings=dict(files=2, entries=0, seconds=120, temporary_bytes=1_000_000_000),
                                        files=[dict(path=str(path), source='fixture', route='inapplicable') for path in files])))
    monkeypatch.setattr(corpus, 'phase6_paths', lambda *args: None)
    settings = SimpleNamespace(config=work/'corpus/config.toml', catalog_path=lambda: work/'corpus/cat')
    clones = []

    def clone(_sample, home):
        clones.append(home)
        (home/'cat').mkdir(parents=True)
        (home/'config.toml').write_text('')
        with sqlite3.connect(home/'cat/catalog.sqlite') as connection:
            connection.execute('CREATE TABLE markers (file_number INTEGER)')
        return settings

    monkeypatch.setattr(corpus, 'clone_owner_copy', clone)
    monkeypatch.setattr('refs.config.select', lambda *args, **kwargs: settings)
    monkeypatch.setattr(corpus, 'phase6_cli', lambda _settings, *args, **kwargs: (0, {'status':'ok', 'data':{'items':[]}}))
    monkeypatch.setattr(corpus, 'phase6_restore', lambda *args, **kwargs: dict(rows_match=True))
    attempts = []
    clock = [0]
    monkeypatch.setattr(corpus.time, 'monotonic', lambda: clock[0])

    def gate(_settings, home, index, row, _remaining):
        clock[0] += 17
        with sqlite3.connect(home/'cat/catalog.sqlite') as connection:
            before = connection.execute('SELECT count(*) FROM markers').fetchone()[0]
            attempts.append((index, before))
            connection.execute('INSERT INTO markers VALUES (?)', (index,))
        if index == 1 and attempts.count((1, 1)) == 1:
            raise subprocess.TimeoutExpired('fixture gate', 1)
        return row | dict(inapplicable='fixture')

    monkeypatch.setattr(corpus, 'gate_file', gate)
    with pytest.raises(subprocess.TimeoutExpired):
        corpus.run(sample, work, manifest)
    state = json.loads((work/'corpus-progress.json').read_text())
    assert len(state['results']) == 1
    assert state['active_index'] == 1
    report = corpus.run(sample, work, manifest)
    assert len(report['results']) == 2
    assert [row['wall_seconds'] for row in report['results']] == [17, 17]
    assert attempts == [(0, 0), (1, 1), (1, 1)]
    assert len(clones) == 1
    assert report['run_seconds'] and len(report['run_seconds']) == 2
    assert corpus.run(sample, work, manifest) == report


def test_bib_gate_resumes_after_file_deadline_without_replaying_completed_file(initialized, tmp_path, monkeypatch):
    harness(monkeypatch)
    rehearsal = importlib.import_module('move_rehearsal')
    monkeypatch.setattr(rehearsal, 'phase6_paths', lambda *args: None)
    monkeypatch.setattr(rehearsal, 'sandboxed', lambda command: command)
    monkeypatch.setattr(rehearsal.shutil, 'which', lambda name: None if name == 'pandoc' else '/usr/bin/true')
    work = tmp_path/'bib-work'
    work.mkdir()
    files = [tmp_path/f'{index}.bib' for index in range(2)]
    for index, path in enumerate(files):
        path.write_text(f'@book{{bib{index},title={{Fixture {index}}},author={{Example, Ada}},year={{2024}}}}')
    manifest = work/'manifest.json'
    manifest.write_text(json.dumps(dict(ceilings=dict(files=2, entries=2, seconds=120, temporary_bytes=1_000_000_000),
                                        files=[dict(path=str(path), source='fixture') for path in files])))
    clones = []

    def clone(_sample, home):
        clones.append(home)
        rehearsal.shutil.copytree(tmp_path/'cat', home/'cat')
        (home/'lib').mkdir()
        (home/'config.toml').write_text(toml_text(dict(schema_version=1, catalog=dict(path=str(home/'cat')),
                                                      resources=dict(library_root=str(home/'lib'), roots=dict(library=str(home/'lib'))))))
        return select(str(home/'config.toml'), str(home/'cat'), no_project_config=True)

    monkeypatch.setattr(rehearsal, 'clone_owner_copy', clone)
    actual_cli = rehearsal.phase6_cli
    attempts = []

    def call(settings, *args, timeout=None):
        if args[:2] == ('resource', 'check'):
            return 0, {'status':'ok', 'data':{'items':[]}}
        if args[0] == 'backup':
            return 0, {'status':'ok'}
        if args[0] == 'import' and 'phase6-1' in args:
            attempts.append('second')
            if len(attempts) == 1:
                actual_cli(settings, *args, timeout=timeout)
                raise subprocess.TimeoutExpired('fixture gate', 1)
        return actual_cli(settings, *args, timeout=timeout)

    monkeypatch.setattr(rehearsal, 'phase6_cli', call)
    monkeypatch.setattr(rehearsal, 'phase6_restore', lambda *args, **kwargs: dict(rows_match=True))
    with pytest.raises(subprocess.TimeoutExpired):
        rehearsal.phase6_corpus(tmp_path, work, manifest)
    state = json.loads((work/'bib-corpus-progress.json').read_text())
    assert len(state['results']) == 1
    assert state['active_index'] == 1
    report = rehearsal.phase6_corpus(tmp_path, work, manifest)
    assert report['outcomes'] == {'applied':2}
    assert len(report['results']) == 2
    assert len(clones) == 1
    assert len(report['run_seconds']) == 2
    assert rehearsal.phase6_corpus(tmp_path, work, manifest) == report
