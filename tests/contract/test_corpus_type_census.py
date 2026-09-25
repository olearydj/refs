"""The census counts source types rather than first-failure import codes."""

import importlib
import json
from pathlib import Path


def test_minimized_unsupported_types_are_counted_once_with_examples(tmp_path, monkeypatch):
    root = Path(__file__).parents[1]/'fixtures/real-trial'
    monkeypatch.syspath_prepend(str(root))
    census = importlib.import_module('corpus_type_census')
    minimized = root/'minimized'
    manifest = tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'files':[
        {'path':str(minimized/'type-census.bib'), 'route':'bib'},
        {'path':str(minimized/'type-census.csl.json'), 'route':'csl'},
        {'path':str(minimized/'type-census.zotero.json'), 'route':'zotero'},
    ]}))
    result = census.census(manifest)
    assert result['files'] == 3
    assert [(row['route'], row['type'], row['count']) for row in result['rows']] == [
        ('bib', 'proceedings', 1), ('csl', 'legal_case', 1), ('zotero', 'artwork', 1)]
    assert [row['example'].split(': ')[-1] for row in result['rows']] == [
        'Etzioni:SWAgents', 'WhiteState1966', 'Hamlet nach William Shakespeare']
