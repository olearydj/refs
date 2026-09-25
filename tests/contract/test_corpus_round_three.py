"""The mixed corpus gate must preserve fixture facts and account for every CSL element."""

import importlib
import json
from pathlib import Path

from refs.adapters import zotero


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
