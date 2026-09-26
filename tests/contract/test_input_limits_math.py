"""Math bytes survive the same parser, naming and exporter that transform surrounding text."""

import sqlite3

import pytest

from refs import bibliography, naming
from refs.adapters import bibtex
from refs.results import RefError


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


def test_unbalanced_dollar_refuses_with_delimiter_reason():
    with pytest.raises(RefError) as caught:
        bibtex.parse(br'@article{bad,title={On $\alpha-stable processes}}')
    assert caught.value.exit_code == 2
    assert caught.value.issue['code'] == 'invalid_bib_entry'
    assert caught.value.issue['message'] == 'Unbalanced math delimiter: $'
