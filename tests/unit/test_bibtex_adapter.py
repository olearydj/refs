import pytest

from refs.adapters.bibtex import parse, partition
from refs.results import RefError


@pytest.mark.parametrize(('entry', 'path', 'expected'), [
    ('@article{x,title={Test},journal={Legacy Journal},number={7}}', 'issue', '7'),
    ('@techreport{x,title={Test},institution={Example School},number={R7}}', 'publisher', 'Example School'),
    ('@phdthesis{x,title={Test},school={Example School}}', 'genre', 'PhD thesis'),
    ('@inbook{x,title={Whole Book},chapter={2}}', 'container-title', 'Whole Book'),
    ('@misc{x,title={Test},howpublished={Online},note={Details}}', 'note', 'Online\nDetails'),
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
