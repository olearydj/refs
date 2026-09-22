import pytest

from refs import naming
from refs.results import RefError


def record(kind='book', **metadata):
    return {'metadata': {'type': kind, 'title': 'The Turing Trap', 'language': 'en', 'author': [{'family': 'Smith'}], 'issued': {'date-parts': [[2024]]}, **metadata}}


@pytest.mark.parametrize('kind', ['book', 'patent', 'speech', 'software'])
def test_author_rule_is_uniform(kind):
    assert naming.key(record(kind)) == 'smith-2024-turingTrap'


def test_fallbacks_overrides_and_suffixes():
    assert naming.key(record(author=[], editor=[{'family': 'Jones'}])) == 'jones-2024-turingTrap'
    assert naming.key(record(author=[], issued={})) == 'turingTrap-ND'
    assert naming.key(record() | {'key_author': 'chosen'}) == 'chosen-2024-turingTrap'
    assert naming.key(record(**{'title-short': 'Python'})) == 'smith-2024-python'
    assert [naming.suffix(i) for i in [0, 1, 26, 27, 52, 53]] == ['', '-a', '-z', '-aa', '-az', '-ba']


def test_latin_and_unsupported_script():
    assert naming.creator_token('García Østergård') == 'garciaostergard'
    assert naming.creator_token('Straße') == 'strasse'
    with pytest.raises(RefError):
        naming.creator_token('王')
    assert naming.key(record(author=[{'family': '王'}]) | {'key_author': 'wang'}) == 'wang-2024-turingTrap'


def test_titles_and_filenames():
    assert naming.title_case('learning with Python', {'protected_terms': ['Python']}) == 'Learning with Python'
    assert naming.title_case('pH in context', {'protected_terms': ['pH']}) == 'pH in Context'
    assert naming.title_case('deliberate lower case', {'preserve_case': True}) == 'deliberate lower case'
    value = record(title='Practical Vim', edition=2, issued={'date-parts': [[2015]]})
    assert naming.filename(value, 'download.pdf') == 'PracticalVim-2E-2015.pdf'
    assert naming.filename(record(title='Zero to Sold', version='1.2.4', issued={'date-parts': [[2020]]}), 'download.pdf') == 'ZeroToSold-v1.2.4-2020.pdf'
    assert naming.filename(record(issued={}), 'download.pdf') == 'download.pdf'
    assert naming.short_title(record(title='Main Title: Subtitle') | {'title_parts': {'main_title': 'Main Title'}}) == 'Main Title'
    assert naming.sort_title(record()) == 'turing trap'
    assert naming.sort_title(record() | {'overrides': {'sort_title': 'Chosen'}}) == 'chosen'
    assert naming.edition_display(2) == '2nd ed.'
