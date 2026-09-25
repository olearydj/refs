from refs.adapters.search_sqlite import exact_matches


def test_exact_matches_are_pure_and_preserve_identifier_priority():
    record = {'citation_key': 'smith-2024-work', 'metadata': {'DOI': '10.1000/EXAMPLE'}, 'extensions': {'identifiers': {'arxiv': '2401.01234'}}}
    original = {'citation_key': record['citation_key'], 'metadata': dict(record['metadata']), 'extensions': {'identifiers': dict(record['extensions']['identifiers'])}}
    doi, exact = exact_matches(record, 'https://doi.org/10.1000/example')
    assert exact is True and doi == [{'field': 'metadata.DOI', 'origin': 'metadata', 'text': '10.1000/EXAMPLE'}]
    prefix, exact = exact_matches(record, 'smith-2024')
    assert exact is False and prefix == [{'field': 'citation_key', 'origin': 'catalog', 'text': 'smith-2024-work'}]
    arxiv, exact = exact_matches(record, 'arXiv:2401.01234')
    assert exact is True and arxiv[0]['field'] == 'extensions.identifiers.arxiv'
    assert record == original
