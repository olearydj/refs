"""Guarded parsing and non-overwriting import against disposable SQLite catalogs."""

import hashlib
import json
from pathlib import Path

import pytest

from refs import importing, sources
from refs.adapters import bibtex
from refs.catalog import connect
from refs.results import RefError

FIXTURES = Path(__file__).parents[1] / 'fixtures/bibliography'
GOOD = b'@article{x,title={A Python Example},author={Smith, Alex},year={2024},doi={10.1000/example}}'


@pytest.mark.parametrize('raw', [
    b'@article{x,title={First},title={Second}}',
    b'@article{x,title={First},TITLE={Second}}',
    b'@article{x,title {First},year={2024}}',
    b'@article{x,title={First}, broken, year={2024}}',
    b'@article{x,title={First @book{y,title={Second}}}}',
])
def test_parser_corruption_is_not_applied(initialized, tmp_path, raw):
    result = importing.run(tmp_path/'cat', raw, 'synthetic.bib')
    assert result['counts'] == dict(applied=0, unchanged=0, conflict=0, invalid=1)
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0
        originals = [bytes(row[0]) for row in connection.execute('SELECT raw_bytes FROM originals')]
        assert raw in originals


def test_offsets_are_original_utf8_bytes():
    raw = '% café\n'.encode() + GOOD + b'\r\n'
    entries = bibtex.partition(raw)
    entry = next(item for item in entries if item['kind'] == 'entry')
    assert raw[entry['start']:entry['end']] == GOOD == entry['raw']


def test_partial_batch_and_rerun_preserve_bytes(initialized, tmp_path):
    raw = (FIXTURES/'mixed.bib').read_bytes()
    first = importing.run(tmp_path/'cat', raw, str(FIXTURES/'mixed.bib'))
    assert first['counts'] == dict(applied=2, unchanged=0, conflict=0, invalid=1)
    second = importing.run(tmp_path/'cat', raw, str(FIXTURES/'mixed.bib'))
    assert second['counts'] == dict(applied=0, unchanged=2, conflict=0, invalid=1)
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 2
        assert connection.execute('SELECT count(*) FROM imports WHERE finished_at IS NOT NULL').fetchone()[0] == 2
        assert connection.execute('SELECT raw_bytes FROM originals WHERE format=?', ('bib-file',)).fetchone()[0] == raw


def test_import_conflict_clear_and_removed(initialized, tmp_path):
    catalog = tmp_path/'cat'
    importing.run(catalog, GOOD, 'input.bib')
    source = sources.show(catalog, 'x')
    sources.update(catalog, 'x', {'schema_version':'1.0', 'clear':['metadata.DOI']}, source['revision'])
    result = importing.run(catalog, GOOD, 'input.bib')
    assert result['counts']['conflict'] == 1
    assert 'DOI' not in sources.show(catalog, 'x')['metadata']
    source = sources.show(catalog, 'x')
    sources.change_identity(catalog, 'x', source['revision'], state='removed', execute=True)
    result = importing.run(catalog, GOOD, 'input.bib')
    assert result['entries'][0]['code'] == 'source_removed'


def test_key_only_and_conflicting_identifiers(initialized, tmp_path):
    catalog = tmp_path/'cat'
    importing.run(catalog, GOOD, 'input.bib')
    changed = GOOD.replace(b'10.1000/example', b'10.1000/other')
    assert importing.run(catalog, changed, 'other.bib')['counts']['conflict'] == 1
    assert sources.show(catalog, 'x')['metadata']['DOI'] == '10.1000/example'


def test_lossy_reimport_keeps_richer_record(initialized, tmp_path):
    raw = json.dumps({'schema_version':'1.0', 'citation_key':'web', 'metadata':{'type':'webpage','title':'Example Page','URL':'https://example.org'}}).encode()
    sources.add(tmp_path/'cat', raw, 'agent.json')
    result = importing.run(tmp_path/'cat', b'@misc{web,title={Example Page},url={https://example.org}}', 'out.bib')
    assert result['counts']['conflict'] == 1
    assert sources.show(tmp_path/'cat', 'web')['metadata']['type'] == 'webpage'


@pytest.mark.parametrize('extra', [b'crossref={parent}', b'xdata={parent}', b'title=custom', b'title={A} # {B}', br'title={A \unknown{word}}'])
def test_unsupported_constructs_are_explicit(initialized, tmp_path, extra):
    result = importing.run(tmp_path/'cat', b'@book{x,title={Base},'+extra+b'}', 'input.bib')
    assert result['entries'][0].get('limitations') or result['counts']['invalid']


def test_unpartitionable_file_makes_no_sources(initialized, tmp_path):
    with pytest.raises(RefError, match='partition'):
        importing.run(tmp_path/'cat', GOOD + b'\n@book{broken,title={unfinished', 'input.bib')
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0
        assert connection.execute('SELECT count(*) FROM imports WHERE finished_at IS NULL').fetchone()[0] == 1


def test_interrupted_run_reruns_without_duplicate(initialized, tmp_path, monkeypatch):
    raw = GOOD + b'\n@book{other,title={Other Work}}'
    original = importing.apply_entry
    calls = 0

    def interrupt(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt
        return original(*args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(importing, 'apply_entry', interrupt)
        with pytest.raises(KeyboardInterrupt):
            importing.run(tmp_path/'cat', raw, 'input.bib')
    with connect(tmp_path/'cat') as connection:
        row = connection.execute('SELECT * FROM imports').fetchone()
        assert row['finished_at'] is None and row['applied'] == 1
        assert row['file_digest'] == hashlib.sha256(raw).hexdigest()
    assert importing.run(tmp_path/'cat', raw, 'input.bib')['counts']['unchanged'] == 1
