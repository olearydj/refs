"""CSL arrays use the persisted import batch and preserve each element as evidence."""

from pathlib import Path

from refs.catalog import connect

FIXTURE = Path(__file__).parents[1] / 'fixtures/real-trial/minimized/csl-batch-three.json'


def test_csl_array_accounts_for_duplicate_and_invalid_element(initialized, tmp_path):
    raw = FIXTURE.read_bytes()
    expected_slices = [line.strip().rstrip(b',') for line in raw.splitlines()[1:4]]
    first = initialized('import', '--format', 'csljson', '--input', FIXTURE, '--origin', 'csl-batch', expected=4)
    assert first['command'] == 'import'
    assert first['status'] == 'partial'
    assert first['errors'][0]['code'] == 'import_partial'
    assert first['data']['counts'] == dict(applied=1, unchanged=1, conflict=0, invalid=1)
    assert [entry['status'] for entry in first['data']['entries']] == ['applied', 'unchanged', 'invalid']
    assert first['data']['entries'][2]['code'] == 'invalid_record'
    assert first['data']['entries'][0]['source_id'] == first['data']['entries'][1]['source_id']
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM imports').fetchone()[0] == 1
        assert connection.execute('SELECT count(*) FROM import_entries').fetchone()[0] == 3
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 1
        slices = [bytes(row[0]) for row in connection.execute("SELECT raw_bytes FROM originals WHERE format='csljson' AND origin LIKE 'import-%'")]
        assert sorted(slices) == sorted(expected_slices)
        assert connection.execute("SELECT source_id FROM originals WHERE origin='import-invalid'").fetchone()[0] is None
    again = initialized('import', '--format', 'csljson', '--input', FIXTURE, '--origin', 'csl-batch', expected=4)
    assert again['data']['counts'] == dict(applied=0, unchanged=2, conflict=0, invalid=1)
    assert again['status'] == first['status']
    assert again['errors'] == first['errors']
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM imports').fetchone()[0] == 2
        assert connection.execute('SELECT count(*) FROM import_entries').fetchone()[0] == 6
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 1


def test_csl_single_object_is_one_import_entry(initialized, tmp_path):
    source = FIXTURE.read_bytes().splitlines()[1].strip().rstrip(b',')
    path = tmp_path/'one.json'
    path.write_bytes(source)
    result = initialized('import', '--format', 'csljson', '--input', path)
    assert result['status'] == 'ok'
    assert result['data']['counts'] == dict(applied=1, unchanged=0, conflict=0, invalid=0)
    with connect(tmp_path/'cat') as connection:
        assert connection.execute('SELECT count(*) FROM imports').fetchone()[0] == 1
        assert connection.execute('SELECT count(*) FROM import_entries').fetchone()[0] == 1
        assert bytes(connection.execute("SELECT raw_bytes FROM originals WHERE origin='import-applied'").fetchone()[0]) == source


def test_csl_partial_envelope_matches_bib_import(initialized, tmp_path):
    csl = initialized('import', '--format', 'csljson', '--input', FIXTURE, expected=4)
    bib = initialized('import', '--format', 'bib', '--input', Path(__file__).parents[1]/'fixtures/bibliography/mixed.bib', expected=4)
    assert (csl['command'], csl['status'], csl['errors'][0]['code']) == (bib['command'], bib['status'], bib['errors'][0]['code'])
    assert set(csl['data']) == set(bib['data'])
