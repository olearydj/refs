"""The census counts source types rather than first-failure import codes."""

import importlib
import json
from pathlib import Path


def test_minimized_unsupported_types_are_counted_once_with_examples(tmp_path, monkeypatch):
    root = Path(__file__).parents[1]/'fixtures/real-trial'
    monkeypatch.syspath_prepend(str(root))
    census = importlib.import_module('corpus_type_census')
    minimized = root/'minimized'
    bib = tmp_path/'types.bib'
    bib.write_text((minimized/'type-census.bib').read_text().replace('@proceedings', '@legislation'))
    zotero = tmp_path/'types.json'
    zotero.write_text((minimized/'type-census.zotero.json').read_text().replace('artwork', 'case'))
    manifest = tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'files':[
        {'path':str(bib), 'route':'bib'},
        {'path':str(minimized/'type-census.csl.json'), 'route':'csl'},
        {'path':str(zotero), 'route':'zotero'},
    ]}))
    result = census.census(manifest)
    assert result['files'] == 3
    assert [(row['route'], row['type'], row['count']) for row in result['rows']] == [
        ('bib', 'legislation', 1), ('csl', 'legal_case', 1), ('zotero', 'case', 1)]
    assert [row['example'].split(': ')[-1] for row in result['rows']] == [
        'Etzioni:SWAgents', 'WhiteState1966', 'Hamlet nach William Shakespeare']


def test_zotero_type_census_includes_parents_without_children(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1]/'fixtures/real-trial'))
    census = importlib.import_module('corpus_type_census')
    source = tmp_path/'parents.json'
    source.write_text(json.dumps({'items':[
        {'itemType':'case', 'title':'Without children'},
        {'itemType':'case', 'title':'With children', 'notes':['A note']},
        {'itemType':'note', 'title':'Standalone note'},
        {'itemType':'attachment', 'title':'Standalone attachment'},
    ]}))
    manifest = tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'files':[{'path':str(source), 'route':'zotero'}]}))
    assert census.census(manifest)['rows'] == [
        {'route':'zotero', 'type':'case', 'count':2, 'example':'parents.json: Without children'}]
