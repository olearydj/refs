"""Season words canonicalize to CSL numbers without replacing date parts with a literal."""

import sqlite3
from pathlib import Path

import pytest

from refs import bibliography
from refs.adapters import bibtex

FIXTURES = Path(__file__).parents[1] / 'fixtures/real-trial/minimized'


@pytest.mark.parametrize(('word', 'season', 'canonical'), [
    ('spring', 1, 'spring'), ('summer', 2, 'summer'), ('autumn', 3, 'autumn'),
    ('fall', 3, 'autumn'), ('winter', 4, 'winter'),
])
@pytest.mark.parametrize('case', [str.lower, str.upper, str.title], ids=['lower', 'upper', 'title'])
def test_season_word_imports_and_round_trips_at_csl_level(initialized, tmp_path, word, season, canonical, case):
    raw = (FIXTURES/'season-month.bib').read_bytes().replace(b'Spring', case(word).encode())
    path = tmp_path/'input.bib'
    path.write_bytes(raw)
    result = initialized('import', '--format', 'bib', '--input', path)['data']
    assert result['counts'] == dict(applied=1, unchanged=0, conflict=0, invalid=0)
    record = initialized('show', 'season')['data']
    assert record['metadata']['issued'] == {'date-parts': [[2024]], 'season': season}
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        assert raw.rstrip() in [bytes(row[0]) for row in connection.execute("SELECT raw_bytes FROM originals WHERE format='bib'")]
    output, _ = bibliography.serialize([record])
    assert f'month = {{{canonical}}}'.encode() in output
    assert b'year = {2024}' in output
    after = bibtex.parse(bibtex.partition(output)[0]['raw'])['source'].canonical()
    assert after['metadata']['issued'] == {'date-parts': [[2024]], 'season': season}
    again = initialized('import', '--format', 'bib', '--input', path)['data']
    assert again['counts'] == dict(applied=0, unchanged=1, conflict=0, invalid=0)


@pytest.mark.parametrize('date', ['2024', '2024-09-12'])
def test_season_beside_explicit_date_preserves_its_precision(date):
    raw = ('@book{season,title={Season Study},month={Fall},date={' + date + '}}').encode()
    record = bibtex.parse(raw)['source'].canonical()
    expected = {'date-parts': [[2024]] if date == '2024' else [[2024, 9, 12]], 'season': 3}
    assert record['metadata']['issued'] == expected
    output, _ = bibliography.serialize([record])
    assert bibtex.parse(bibtex.partition(output)[0]['raw'])['source'].canonical()['metadata']['issued'] == expected


@pytest.mark.parametrize('word', ['????', 'monsoon', '31'])
def test_nonmonth_still_refuses_without_a_source(initialized, tmp_path, word):
    raw = (FIXTURES/'invalid-month.bib').read_bytes().replace(b'{31}', ('{' + word + '}').encode())
    path = tmp_path/'invalid.bib'
    path.write_bytes(raw)
    result = initialized('import', '--format', 'bib', '--input', path, expected=4)['data']
    assert result['counts'] == dict(applied=0, unchanged=0, conflict=0, invalid=1)
    assert result['entries'][0]['code'] == 'invalid_bib_entry'
    assert result['entries'][0]['message'] == f'Invalid month: {word}'
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0
        assert connection.execute("SELECT raw_bytes FROM originals WHERE origin='import-invalid'").fetchone()[0] == bibtex.partition(raw)[0]['raw']
