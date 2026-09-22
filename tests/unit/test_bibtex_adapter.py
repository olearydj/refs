import pytest

from refs.adapters.bibtex import parse, partition
from refs.results import RefError


@pytest.mark.parametrize(('entry', 'path', 'expected'), [
    ('@article{x,title={Test},journal={Legacy Journal},number={7}}', 'issue', '7'),
    ('@techreport{x,title={Test},institution={Example School},number={R7}}', 'publisher', 'Example School'),
    ('@phdthesis{x,title={Test},school={Example School}}', 'genre', 'PhD thesis'),
    ('@inbook{x,title={Whole Book},chapter={2}}', 'container-title', 'Whole Book'),
    ('@misc{x,title={Test},howpublished={Online},note={Details}}', 'note', 'Details'),
    ('@book{x,title={Test},year={2024},month=jan,date={2024-01-02}}', 'issued', {'date-parts':[[2024,1,2]]}),
    ('@book{x,title={Test},author={{Research and Design}}}', 'author', [{'literal':'Research and Design'}]),
    ('@book{x,title={Test},author={de Vries, Alex}}', 'author', [{'given':'Alex','family':'Vries','dropping-particle':'de'}]),
])
def test_supported_bibtex(entry, path, expected):
    assert parse(entry.encode())['source'].canonical()['metadata'][path] == expected


@pytest.mark.parametrize('entry', [
    '@article{x,title={A},number={1},issue={2}}',
    '@book{x,title={A},year={2024},date={2023-01}}',
    '@article{x,title={A},TITLE={B}}',
    '@article{x,title={A},broken,year={2024}}',
])
def test_guards(entry):
    with pytest.raises(RefError):
        parse(entry.encode())


def test_partition_and_original_protection():
    raw = b'% synthetic\n@book{x,title={A {Python} Example}}\n'
    block = partition(raw)[0]
    assert block['raw'] == raw[block['start']:block['end']]
    source = parse(block['raw'])['source']
    assert source.title_protection['title'].protected_terms == ['Python']


def test_uppercase_fields_and_accents_do_not_create_protection():
    source = parse(br'@BOOK{X,TITLE={An {NASA} Example with Caf\'{e}},AUTHOR={Smith, Alex}}')['source']
    assert source.metadata.title == 'An NASA Example with Café'
    assert source.title_protection['title'].protected_terms == ['NASA']


def test_date_aliases_compare_overlapping_precision():
    source = parse(b'@book{x,title={Test},year={2024},month=jan,date={2024}}')['source']
    assert source.metadata.issued.date_parts == [[2024,1]]
    with pytest.raises(RefError):
        parse(b'@book{x,title={Test},month=feb,date={2024-01}}')


@pytest.mark.parametrize('flag, particle', [('true','non-dropping-particle'), ('false','dropping-particle')])
def test_extended_biblatex_names(flag, particle):
    raw = ('@book{x,title={Study},author={family=Lopik, given=Katherine, prefix=van, suffix=Jr, useprefix='+flag+' and Smith, Alex}}').encode()
    names = parse(raw)['source'].canonical()['metadata']['author']
    assert names == [{'family':'Lopik','given':'Katherine','suffix':'Jr',particle:'van'}, {'given':'Alex','family':'Smith'}]


@pytest.mark.parametrize('name', ['', 'family=, given=', 'family=Smith, useprefix=maybe', r'\unknown{Smith}'])
def test_unparsed_creator_is_invalid(name):
    with pytest.raises(RefError):
        parse(('@book{x,title={Study},author={'+name+'}}').encode())


def test_show_surfaces_import_limitations():
    from refs.display import readable
    value = parse(b'@book{x,title={Study},organization={Institute}}')
    record = value['source'].canonical() | {'limitations':value['limitations']}
    assert 'Limitations:\n  organization:' in readable('show', record)


def test_relax_in_accented_creator_is_not_a_lost_name():
    source = parse(br"@article{x,title={Study},author={Garc{\'i}a{\relax}, Alex}}")['source']
    assert source.metadata.author[0].family == 'García'


def test_literal_year_survives_import_and_export_with_a_warning():
    from refs import bibliography
    parsed = parse(b'@book{artifact,title={A Study},year={/05/04 2015},author={Smith, Alex}}')
    value = parsed['source'].canonical()
    assert value['metadata']['issued'] == {'literal':'/05/04 2015'}
    assert any(item['field']=='year' for item in parsed['limitations'])
    output, warnings = bibliography.serialize([value])
    assert b'year = {/05/04 2015}' in output
    assert any(w['code']=='literal_issued_year' for w in warnings)
