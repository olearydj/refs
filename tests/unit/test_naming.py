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
    assert naming.title_case('learning with Python', {'protected_terms': ['Python']}) == 'Learning With Python'
    assert naming.title_case('pH in context', {'protected_terms': ['pH']}) == 'pH in Context'
    assert naming.title_case('deliberate lower case', {'preserve_case': True}) == 'deliberate lower case'
    value = record(title='Practical Vim', edition=2, issued={'date-parts': [[2015]]})
    assert naming.filename(value, 'download.pdf') == 'PracticalVim-2E-2015.pdf'
    assert naming.filename(record(title='Zero to Sold', version='1.2.4', issued={'date-parts': [[2020]]}), 'download.pdf') == 'ZeroToSold-v1.2.4-2020.pdf'
    assert naming.filename(record(issued={}), 'download.pdf') == 'download.pdf'
    assert naming.short_title(record(title='Main Title: Subtitle') | {'title_parts': {'main_title': 'Main Title'}}) == 'Main Title'
    assert naming.sort_title(record()) == 'turing trap'
    assert naming.sort_title(record() | {'overrides': {'sort_title': 'Chosen'}}) == 'chosen'
    assert naming.filename(record(title='Practical Vim', edition=3, issued={'date-parts': [[2015]]}), 'download.pdf') == 'PracticalVim-3E-2015.pdf'


def test_filename_reports_its_own_fallback():
    assert naming.filename(record(issued={}), 'download.pdf', report_fallback=True) == ('download.pdf', True)
    assert naming.filename(record(title='Practical Vim', issued={'date-parts': [[2015]]}), 'download.pdf', report_fallback=True) == ('PracticalVim-2015.pdf', False)


@pytest.mark.parametrize('text, language, expected, warns', [
    ('learning from examples', None, 'Learning From Examples', False),
    ('études françaises', None, 'études françaises', True),
    ('études françaises', 'fr', 'études françaises', False),
    ('learning Python', 'en', 'Learning Python', False),
])
def test_title_language_warning_requires_unknown_nonascii_letters(text, language, expected, warns):
    metadata = {'title': text}
    if language is not None:
        metadata['language'] = language
    normalized, warnings = naming.normalize({'metadata': metadata})
    assert normalized['metadata']['title'] == expected
    assert any(item['code'] == 'title_language_unknown_or_nonenglish' for item in warnings) == warns
    assert normalized['metadata'].get('language') == language


@pytest.mark.parametrize('raw, expected', [
    ('Workflow: a Scalable Engine', 'Workflow: A Scalable Engine'),
    ('A Dynamic Make-like Function-oriented Toolkit', 'A Dynamic Make-Like Function-Oriented Toolkit'),
    ('Recipes: a Lightweight Pipeline', 'Recipes: A Lightweight Pipeline'),
    ('Compiler: calls into State-of-the-Art Pipelines', 'Compiler: Calls Into State-of-the-Art Pipelines'),
    ('Blueprint First, Model Second: a Framework', 'Blueprint First, Model Second: A Framework'),
])
def test_subtitles_and_hyphenated_words(raw, expected):
    from refs.naming import title_case
    assert title_case(raw, {}) == expected


@pytest.mark.parametrize('apostrophe', ["'", '’', 'ʼ'])
@pytest.mark.parametrize(('title', 'key_title', 'file_title'), [
    ("The Developer{a}s Playbook", 'developersPlaybook', 'TheDevelopersPlaybook'),
    ("Model{a}s Accuracy", 'modelsAccuracy', 'ModelsAccuracy'),
    ("O{a}Reilly Guide", 'oreillyGuide', 'OReillyGuide'),
    ("{a}Quoted{a} Words", 'quotedWords', 'QuotedWords'),
    ("Developer{a} s Guide", 'developerS', 'DeveloperSGuide'),
    ("Model{a}2 Guide", 'model2', 'Model2Guide'),
    ("Model²{a}s Guide", 'model²S', 'Model²SGuide'),
])
def test_title_apostrophes_join_only_between_letters(apostrophe, title, key_title, file_title):
    value = record(title=title.format(a=apostrophe))
    assert naming.key(value) == 'smith-2024-' + key_title
    assert naming.filename(value, 'download.pdf') == file_title + '-2024.pdf'


@pytest.mark.parametrize('separator', ['-', '.', '/', '_', ' '])
def test_other_title_punctuation_still_separates_words(separator):
    value = record(title='Model' + separator + 'based Guide')
    assert naming.key(value) == 'smith-2024-modelBased'
    assert naming.filename(value, 'download.pdf') == 'ModelBasedGuide-2024.pdf'


@pytest.mark.parametrize('label', [
    'transcription', 'scan', 'capture', 'PDF', 'r2023-06-03', 'mobile', 'figure-ruby-photo-1',
])
def test_single_token_label_filename_is_unchanged(label):
    assert naming.filename(record(), 'download.pdf', label) == f'TheTuringTrap-2024-{label}.pdf'


@pytest.mark.parametrize(('label', 'segment'), [
    ('Author-hosted full text (journal article)', 'Author-hosted-full-text-journal-article'),
    ('  scan\t\n copy\u00a0 text  ', 'scan-copy-text'),
    ('--scan--- - copy--', 'scan-copy'),
    ('scan-()-copy', 'scan-copy'),
    ('r2023.06.03 PDF', 'r2023.06.03-PDF'),
    ('café 日本語', 'café-日本語'),
    ('!!! / () _', ''),
    ('---', ''),
    ('', ''),
    (None, ''),
])
def test_label_filename_segment_normalizes_whitespace_and_hyphens(label, segment):
    expected = 'TheTuringTrap-2024' + ('-' + segment if segment else '') + '.pdf'
    assert naming.filename(record(), 'download.pdf', label) == expected
