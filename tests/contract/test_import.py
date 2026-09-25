"""Guarded parsing and non-overwriting import against disposable SQLite catalogs."""

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from conftest import REFS_COMMAND, isolated_env

from refs import importing, sources
from refs.adapters import bibtex
from refs.catalog import connect
from refs.results import RefError

FIXTURES = Path(__file__).parents[1] / 'fixtures/bibliography'
GOOD = b'@article{x,title={A Python Example},author={Smith, Alex},year={2024},doi={10.1000/example}}'


def test_empty_key_fixture_names_entry_position_and_preserves_bytes(initialized, tmp_path):
    fixture = Path(__file__).parents[1] / 'fixtures/real-trial/minimized/empty-key.bib'
    raw = fixture.read_bytes()
    report = importing.run(tmp_path / 'cat', raw, str(fixture))
    assert report['counts'] == dict(applied=0, unchanged=0, conflict=0, invalid=1)
    entry = report['entries'][0]
    assert entry['code'] == 'invalid_bib_entry'
    assert entry['start'] == 0
    assert entry['message'] == 'Entry at byte 0: citation key is empty'
    with connect(tmp_path / 'cat') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0
        assert raw in [bytes(row[0]) for row in connection.execute('SELECT raw_bytes FROM originals')]


def test_malformed_entry_diagnostic_stays_in_json_envelope(initialized, tmp_path, cli):
    fixture = Path(__file__).parents[1] / 'fixtures/real-trial/minimized/missing-key-comma.bib'
    result = cli('import', '--format', 'bib', '--input', fixture, '--origin', 'synthetic', expected=4)
    assert result['data']['counts'] == dict(applied=0, unchanged=0, conflict=0, invalid=1)
    assert result['data']['entries'][0]['code'] == 'invalid_bib_entry'
    assert result['data']['entries'][0]['preserved'] is True
    assert result['errors'][0]['code'] == 'import_partial'
    with connect(tmp_path / 'cat') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0


def test_no_doi_proposal_never_reads_every_stored_metadata_row(initialized, tmp_path):
    fixture = Path(__file__).parents[1] / 'fixtures/real-trial/minimized/no-doi-scan.bib'
    blocks = [block for block in bibtex.partition(fixture.read_bytes()) if block['kind'] == 'entry']
    report = importing.run(tmp_path / 'cat', b'\n'.join(block['raw'] for block in blocks[:2]), str(fixture))
    assert report['counts']['applied'] == 2
    proposed = bibtex.parse(blocks[2]['raw'])['source']
    with connect(tmp_path / 'cat') as connection:
        def forbid_full_metadata_read(action, table, column, *_):
            if action == sqlite3.SQLITE_READ and table == 'sources' and column == 'metadata_json':
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        connection.set_authorizer(forbid_full_metadata_read)
        assert importing.match(connection, proposed, hashlib.sha256(blocks[2]['raw']).hexdigest()) == (None, [])
    full = importing.run(tmp_path / 'cat', fixture.read_bytes(), str(fixture))
    assert full['counts'] == dict(applied=1, unchanged=2, conflict=0, invalid=0)
    assert importing.run(tmp_path / 'cat', fixture.read_bytes(), str(fixture))['counts']['applied'] == 0


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


@pytest.mark.parametrize(('extra', 'status', 'field'), [
    (b'crossref={parent}', 'applied', 'crossref'),
    (b'xdata={parent}', 'applied', 'xdata'),
    (b'title=custom', 'invalid', None),
    (b'title={A} # {B}', 'invalid', None),
    (br'title={A \unknown{word}}', 'invalid', None),
])
def test_unsupported_constructs_are_explicit(initialized, tmp_path, extra, status, field):
    result = importing.run(tmp_path/'cat', b'@book{x,title={Base},'+extra+b'}', 'input.bib')
    assert result['entries'][0]['status'] == status
    assert result['counts'][status] == 1
    if field:
        assert result['entries'][0]['limitations'] == [{'field': field, 'reason': 'Unmapped field preserved verbatim'}]
        assert sources.show(tmp_path/'cat', 'x')['metadata']['title'] == 'Base'
    else:
        with connect(tmp_path/'cat') as connection:
            assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0


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


def test_cli_formats_and_partial_result(initialized, tmp_path):
    result = initialized('import', '--format', 'bib', '--input', FIXTURES/'mixed.bib', '--origin', 'synthetic test', expected=4)
    assert result['status'] == 'partial' and result['data']['counts']['applied'] == 2
    path = tmp_path/'single.bib'
    path.write_bytes(GOOD.replace(b'A Python Example', b'A Distinct Example'))
    result = initialized('add', '--format', 'bib', '--input', path)
    assert result['data']['outcome'] == 'created'
    assert initialized('add', '--format', 'bib', '--input', path)['data']['outcome'] == 'already_present'


def test_legacy_key_remains_editable_but_blocks_export(initialized,tmp_path):
    from refs import bibliography
    from refs.models import SourceRecord
    importing.run(tmp_path/'cat',b'@book{legacy key,title={Original Title}}','legacy.bib')
    record=sources.show(tmp_path/'cat','legacy key')
    SourceRecord.model_validate(record)
    edited=sources.update(tmp_path/'cat','legacy key',{'schema_version':'1.0','set':{'metadata.title':'Corrected Title'}},record['revision'])
    assert edited['citation_key']=='legacy key'
    with pytest.raises(RefError) as error:
        bibliography.serialize([edited])
    assert error.value.issue['code'] == 'export_blocked'


def test_import_entry_status_and_human_order(initialized,tmp_path):
    import subprocess
    path=tmp_path/'mixed.bib'
    path.write_bytes((FIXTURES/'mixed.bib').read_bytes())
    result=initialized('import','--input',path,expected=4)
    assert [entry['status'] for entry in result['data']['entries']]==['applied','applied','invalid']
    run=subprocess.run([*REFS_COMMAND,'import','--input',str(path)],env=isolated_env(tmp_path),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    assert run.returncode==4
    assert run.stdout.splitlines()[0].startswith('Imported 0, unchanged 2, conflicts 0, invalid 1')
    assert 'Inspect reported entries' in run.stdout
    assert run.stdout.index('Imported ') < run.stdout.index('Inspect reported entries')



def test_report_keys_title_similarity_and_relative_url(initialized, tmp_path):
    from refs import importing, sources
    raw = b'@book{one,title={Same Study},author={Smith, Alex},url={relative/book}}\n@book{two,title={Same Study},author={Jones, Lee}}\n@book{bad,title={Bad},broken,year={2024}}'
    result = importing.run(tmp_path/'cat',raw,'synthetic.bib')
    assert result['counts'] == dict(applied=2,unchanged=0,conflict=0,invalid=1)
    assert [e['citation_key'] for e in result['entries']] == ['one','two','bad']
    assert any(w['code']=='likely_match' for w in result['entries'][1]['warnings'])
    stored = sources.show(tmp_path/'cat','one')
    assert 'URL' not in stored['metadata']
    assert stored['limitations'][0]['field'] == 'url'
    again = importing.run(tmp_path/'cat',raw,'synthetic.bib')
    assert again['counts'] == dict(applied=0,unchanged=2,conflict=0,invalid=1)
