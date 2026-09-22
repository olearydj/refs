"""Read only the trial copies and their disposable catalogs."""
import json
import sqlite3
import sys
from pathlib import Path

import bibtexparser

root = Path(sys.argv[1])
report = json.loads((root/'out/library/import.json').read_text())
assert report['data']['counts'] == dict(applied=562, unchanged=0, conflict=0, invalid=0)
inputs = bibtexparser.parse_string((root/'inputs/zotero-bbt-export.bib').read_text()).entries
with sqlite3.connect((root/'out/library/cat/catalog.sqlite').resolve().as_uri()+'?mode=ro', uri=True) as connection:
    records = {key:json.loads(metadata) for key,metadata in connection.execute('SELECT citation_key,metadata_json FROM sources')}
    declared_authors = editors_only = unnamed = 0
    for entry in inputs:
        fields = {field.key.lower():field.value for field in entry.fields}
        value = records[entry.key]
        if fields.get('author'):
            declared_authors += 1
            assert value.get('author'), f'Input author lost: {entry.key}'
        elif fields.get('editor'):
            editors_only += 1
            assert value.get('editor'), f'Input editor lost: {entry.key}'
        else:
            unnamed += 1
            assert not value.get('author'), f'Invented author: {entry.key}'
print(f'Library creator coverage: {declared_authors} supplied author lists retained; {editors_only} editor-only; {unnamed} without supplied creators')
