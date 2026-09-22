
import pytest

from refs import bibliography
from refs.models import SourceCreate
from refs.results import RefError


def record(kind='article-journal', **metadata):
    return SourceCreate.model_validate({'schema_version': '1.0', 'citation_key': 'example-2024-work', 'metadata': {'type': kind, 'title': 'Synthetic Work', 'language': 'en', 'author': [{'family': 'Smith'}], 'issued': {'date-parts': [[2024]]}, **metadata}}).canonical()


def test_four_classes_and_unknown_override():
    value = record('webpage', author=[], issued={'date-parts': [[2024]]}, URL='https://example.org/work')
    data, warnings = bibliography.serialize([value])
    assert b'@misc{' in data
    assert {'faithful_incomplete', 'documented_fallback'} <= {item['details']['class'] for item in warnings}
    value['metadata']['contributor'] = [{'family': 'Jones'}]
    with pytest.raises(RefError):
        bibliography.serialize([value])
    data, warnings = bibliography.serialize([value], allow_unknown=True)
    assert any(item['details'].get('override') for item in warnings)
    assert b'Synthetic Work' in data
    value['metadata']['issued'] = {'date-parts': [[2020], [2024]]}
    with pytest.raises(RefError) as error:
        bibliography.serialize([value], allow_unknown=True)
    assert any(item['code'] == 'issued_date_lost_or_changed' for item in error.value.issue['details']['entries'])


@pytest.mark.parametrize('code', ['cited_authors_changed', 'issued_date_lost_or_changed', 'work_identity_changed', 'in_text_citation_changed', 'protected_spelling_changed'])
def test_known_losses_cannot_be_waived(code):
    with pytest.raises(RefError):
        bibliography.enforce_losses([{'code': code, 'class': 'blocking', 'citation_key': 'example'}], allow_unknown=True)


def test_structural_conflicts_and_all_affected_entries():
    first = record()
    second = record()
    second['citation_key'] = first['citation_key'].upper()
    with pytest.raises(RefError):
        bibliography.serialize([first, second], allow_unknown=True)
    first['metadata']['issued'] = {'literal': 'Uncertain Date'}
    second['citation_key'] = 'another-key'
    second['metadata']['issued'] = {'date-parts': [[2020], [2024]]}
    with pytest.raises(RefError) as error:
        bibliography.serialize([first, second])
    assert {row['citation_key'] for row in error.value.issue['details']['entries']} == {'example-2024-work', 'another-key'}


def test_dates_corporate_names_and_protection():
    value = record(author=[{'literal': 'Research and Development'}], issued={'date-parts': [[2024, 2, 29]]})
    value['title_protection'] = {'title': {'protected_terms': ['Synthetic'], 'preserve_case': False}}
    data, _ = bibliography.serialize([value])
    assert b'author = {{Research and Development}}' in data
    assert b'{Synthetic} Work' in data
    assert b'2024-02-29' in data
    assert b'month = feb' in data


@pytest.mark.parametrize('kind', ['article', 'article-journal', 'article-magazine', 'article-newspaper', 'book', 'chapter', 'document', 'manuscript', 'paper-conference', 'patent', 'post-weblog', 'report', 'software', 'speech', 'standard', 'thesis', 'webpage'])
def test_supported_type_projection(kind):
    data, _ = bibliography.serialize([record(kind)])
    expected = {'article': 'unpublished', 'article-journal': 'article', 'article-magazine': 'article', 'article-newspaper': 'article', 'book': 'book', 'chapter': 'incollection', 'paper-conference': 'inproceedings', 'report': 'techreport', 'manuscript': 'unpublished'}.get(kind, 'misc')
    assert data.startswith(('@' + expected + '{').encode())
    assert b'example-2024-work' in data
    assert b'Smith' in data
    assert b'2024' in data


def test_type_scoped_numbers_and_traditional_part():
    article, _ = bibliography.serialize([record(issue='7')])
    report, _ = bibliography.serialize([record('report', number='R-42', publisher='Institute')])
    assert b'number = {7}' in article
    assert b'number = {R-42}' in report and b'institution = {Institute}' in report
    part = record('chapter', **{'container-title': 'Whole Book', 'chapter-number': 3})
    del part['metadata']['title']
    part['citation_key'] = 'explicit-part-key'
    output, _ = bibliography.serialize([part])
    assert b'@inbook{' in output and b'title = {Whole Book}' in output and b'chapter = {3}' in output


def test_extensions_are_explicit_unknowns():
    value = record('patent')
    value['extensions'] = {'patent': {'assignees': [{'literal': 'Owner Company'}], 'application_number': 'APP1', 'priority_date': {'date-parts': [[2020]]}}}
    with pytest.raises(RefError) as error:
        bibliography.serialize([value])
    assert len([item for item in error.value.issue['details']['entries'] if item['class'] == 'unknown']) == 3


def test_empty_and_cleared_values():
    assert bibliography.serialize([])[0] == b''
    value = record(DOI='10.5555/test')
    del value['metadata']['DOI']
    output, _ = bibliography.serialize([value])
    assert b'doi =' not in output
    assert bibliography.serialize([value])[0] == output


def test_nonenglish_language_and_unassessed_language():
    data, _ = bibliography.serialize([record(language='fr')])
    assert b'langid = {french}' in data
    with pytest.raises(RefError):
        bibliography.serialize([record(language='zz')], allow_unknown=True)
