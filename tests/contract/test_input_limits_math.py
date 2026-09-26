"""Math bytes survive the same parser, naming and exporter that transform surrounding text."""

import sqlite3

import pytest

from refs import bibliography, naming
from refs.adapters import bibtex


@pytest.mark.parametrize('span', [r'$\alpha$', r'$$\alpha$$', r'\(\alpha\)'])
def test_math_title_round_trip_preserves_raw_span(span):
    title = 'On ' + span + '-stable processes'
    raw = ('@article{math,title={' + title + '},author={Example, Ada},journal={Processes},year={2020}}').encode()
    before = bibtex.parse(raw)['source'].canonical()
    assert before['metadata']['title'] == title
    output, _ = bibliography.serialize([before])
    assert ('title = {' + title + '}').encode() in output
    assert span.encode() in output
    assert b'textbackslash' not in output
    after = bibtex.parse(bibtex.partition(output)[0]['raw'])['source'].canonical()
    assert after['metadata']['title'] == title


def test_two_math_spans_leave_text_between_them_decodable_and_protected():
    raw = r'On $\alpha_i$ and $$\unknown{Beta}$$ with Caf\'{e}'
    assert bibtex.decode(raw) == r'On $\alpha_i$ and $$\unknown{Beta}$$ with Café'
    normalized = naming.title_case(r'on $\alpha_i$ and $$\unknown{Beta}$$ processes', {})
    assert normalized == r'On $\alpha_i$ and $$\unknown{Beta}$$ Processes'
    # A protected term inside math must not inject braces or split an opaque span.
    assert bibliography.title(r'On $R_{i}$', {'protected_terms':['R']}) == r'On $R_{i}$'


def test_unknown_command_outside_math_keeps_its_refusal(initialized,tmp_path):
    raw = br'@article{bad,title={On $\alpha$ and \invented{text}},journal={Processes}}'
    path = tmp_path/'unknown.bib'
    path.write_bytes(raw)
    result = initialized('add','--format','bib','--input',path,expected=2)
    assert result['errors'][0]['code'] == 'invalid_bib_entry'
    assert any(item['reason'] == 'Unsupported TeX command or math; preserve and preprocess explicitly' for item in result['errors'][0]['details']['limitations'])
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0
        assert connection.execute("SELECT raw_bytes FROM originals WHERE origin='import-invalid'").fetchone()[0] == raw


def test_unbalanced_dollar_refuses_with_delimiter_reason(initialized, tmp_path):
    title_raw = br'@article{bad,title={On $\alpha-stable processes}}'
    title_path = tmp_path/'title.bib'
    title_path.write_bytes(title_raw)
    refused = initialized('import', '--format', 'bib', '--input', title_path, expected=4)['data']
    assert refused['counts'] == dict(applied=0, unchanged=0, conflict=0, invalid=1)
    assert refused['entries'][0]['code'] == 'invalid_bib_entry'
    assert {'field':'title', 'reason':'Unbalanced math delimiter: $'} in refused['entries'][0]['limitations']
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 0
        assert connection.execute("SELECT raw_bytes FROM originals WHERE origin='import-invalid'").fetchone()[0] == title_raw

    keywords_raw = br'@article{good,title={A Study},keywords={Drama,Mentally ill$$QMentally ill}}'
    keywords_path = tmp_path/'keywords.bib'
    keywords_path.write_bytes(keywords_raw)
    applied = initialized('import', '--format', 'bib', '--input', keywords_path)['data']
    assert applied['counts'] == dict(applied=1, unchanged=0, conflict=0, invalid=0)
    assert applied['entries'][0]['limitations'] == [{'field':'keywords', 'reason':'Unbalanced math delimiter: $$'}]
    record = initialized('show', 'good')['data']
    assert record['metadata']['title'] == 'A Study'
    assert record['legacy_tags'] == []
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as connection:
        assert connection.execute("SELECT raw_bytes FROM originals WHERE origin='import-applied'").fetchone()[0] == keywords_raw
