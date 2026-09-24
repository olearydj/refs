"""Generated inputs exercise pure bibliographic and naming invariants."""

import unicodedata
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from refs import bibliography, naming
from refs.adapters import bibtex
from refs.models import Date, normalize_arxiv, normalize_doi, normalize_loc
from refs.moves import preserved_target
from refs.results import RefError

WORD = st.text(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=12)


@settings(max_examples=200, deadline=None)
@example(b'@book{x,title={Unclosed')
@given(st.binary(max_size=256))
def test_partition_refuses_arbitrary_bytes_only_with_its_own_error(raw):
    """Byte partitioning returns spans or its documented refusal, never an unrelated exception."""
    try:
        parts = bibtex.partition(raw)
    except RefError as error:
        assert error.issue['code'] == 'unpartitionable_input'
    else:
        assert all(part['raw'] == raw[part['start']:part['end']] for part in parts)
        assert all(0 <= part['start'] < part['end'] <= len(raw) for part in parts)


@settings(max_examples=100, deadline=None)
@example('Synthetic', 'Book', 'Smith', 2024)
@given(WORD, WORD, WORD, st.integers(min_value=1000, max_value=2100))
def test_parse_serialize_parse_preserves_supported_book_facts(first, second, family, year):
    """A generated supported book keeps its cited facts after a portable round trip."""
    original = f'@book{{fixture,title={{{first} {second}}},author={{{family}, Alex}},year={{{year}}},publisher={{Example Press}}}}'.encode()
    before = bibtex.parse(original)['source'].canonical()
    output, _ = bibliography.serialize([before])
    after = bibtex.parse(bibtex.partition(output)[0]['raw'])['source'].canonical()
    for field in ('author', 'issued', 'publisher'):
        assert after['metadata'][field] == before['metadata'][field]
    assert after['metadata']['title'].casefold() == before['metadata']['title'].casefold()


@settings(max_examples=100, deadline=None)
@example('arXiv:2407.01502v2 [cs.AI]', 'https://doi.org/10.48550/arXiv.2407.01502v2')
@given(st.text(max_size=100), st.text(max_size=100))
def test_identifier_normalization_is_idempotent(arxiv, doi):
    """Normalizing an identifier twice yields the same value as once."""
    assert normalize_arxiv(normalize_arxiv(arxiv)) == normalize_arxiv(arxiv)
    assert normalize_doi(normalize_doi(doi)) == normalize_doi(doi)


@settings(max_examples=100, deadline=None)
@example('Python', 'Guide')
@given(WORD, WORD)
def test_generated_key_has_no_unsafe_characters(first, second):
    """A title-generated key never contains syntax or whitespace forbidden to citation keys."""
    record = {'metadata': {'title': f'{first} {second}', 'issued': {'date-parts': [[2024]]}}}
    try:
        key = naming.key(record)
    except RefError as error:
        assert error.issue['code'] == 'citation_key_required'
        assert all(word.lower() in naming.STOPWORDS for word in (first, second))
        return
    assert key and not any(char.isspace() or char in '{}"%#' for char in key)


@settings(max_examples=100, deadline=None)
@example('2402.html', 8)
@given(WORD.map(lambda value: value + '.pdf'), st.integers(min_value=1, max_value=35))
def test_collision_suffix_is_unique_within_folder(name, count):
    """Repeated preserved names reserve distinct casefolded destinations in one folder."""
    with TemporaryDirectory() as directory:
        reserved = set()
        paths = [preserved_target(Path(directory), name, reserved) for _ in range(count)]
        assert len({str(path).casefold() for path in paths}) == count
        assert paths[0].name == unicodedata.normalize('NFC', name)


@settings(max_examples=100, deadline=None)
@example('Cafe\u0301')
@given(st.text(alphabet='abcABCé\u0301', min_size=1, max_size=30))
def test_loc_normalization_round_trips_through_nfc_and_casefold(raw):
    """Valid folder names normalize once and compare equally after canonical case folding."""
    value = normalize_loc(raw)
    assert value == unicodedata.normalize('NFC', raw)
    assert normalize_loc(value) == value
    assert value.casefold() == normalize_loc(raw).casefold()


@settings(max_examples=100, deadline=None)
@given(st.integers(min_value=1, max_value=9999), st.integers(min_value=1, max_value=12), st.booleans())
def test_date_validation_rejects_zero_month_or_day(year, month, zero_month):
    """A date with month zero or day zero is never admitted as a precise date."""
    parts = [year, 0] if zero_month else [year, month, 0]
    with pytest.raises(ValidationError):
        Date.model_validate({'date-parts': [parts]})


@settings(max_examples=100, deadline=None)
@example('LaTeX', 'in', 'Practice')
@given(WORD, WORD, WORD)
def test_title_case_preserves_protected_term(first, middle, last):
    """A protected whole term keeps its exact spelling while nearby words are cased."""
    title = f'{first} {middle} {last}'
    result = naming.title_case(title, {'protected_terms': [middle]})
    assert result.split()[1] == middle
    assert len(result.split()) == 3
