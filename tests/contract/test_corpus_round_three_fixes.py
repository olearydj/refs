"""Owner-adopted rules from the third corpus round."""

from pathlib import Path

from refs.catalog import connect

FIXTURES = Path(__file__).parents[1] / 'fixtures/real-trial/minimized'


def test_beebe_number_ranks_before_issue_and_keeps_original(initialized, tmp_path):
    fixture = FIXTURES/'beebe-number-issue.bib'
    raw = fixture.read_bytes()
    result = initialized('import', '--format', 'bib', '--input', fixture, '--origin', 'beebe')['data']
    assert result['counts'] == dict(applied=1, unchanged=0, conflict=0, invalid=0)
    entry = result['entries'][0]
    assert entry['limitations'] == [{'field':'issue', 'reason':'Documented fallback: number takes precedence over issue for metadata.issue; original retained'}]
    assert initialized('show', 'Zapf:2001:MCD')['data']['metadata']['issue'] == '1/2'
    with connect(tmp_path/'cat') as connection:
        assert raw.rstrip() in [bytes(row[0]) for row in connection.execute("SELECT raw_bytes FROM originals WHERE format='bib'")]
    again = initialized('import', '--format', 'bib', '--input', fixture, '--origin', 'beebe')['data']
    assert again['counts'] == dict(applied=0, unchanged=1, conflict=0, invalid=0)
