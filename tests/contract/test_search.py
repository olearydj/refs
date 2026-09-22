
def test_search_fields_filters_and_empty_results(initialized, reference_path):
    assert initialized('list')['data']['total'] == 0
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    for query, field in [('Learning', 'metadata.title'), ('Smith', 'metadata.author'), ('walking', 'context'), ('smith-2024-learningPython', 'citation_key')]:
        found = initialized('search', query)['data']
        assert found['total'] == 1
        assert found['items'][0]['id'] == source['id']
        assert any(match['field'] == field for match in found['items'][0]['matches'])
    assert initialized('search', 'no-matches-at-all')['data']['total'] == 0
    initialized('project', 'create', 'empty')
    assert initialized('list', '--project', 'empty')['data']['total'] == 0
    initialized('project', 'cite', 'empty', source['id'])
    assert initialized('list', '--project', 'empty')['data']['total'] == 1
    initialized('update', source['id'], '--if-revision', 1, '--set', 'metadata.title="Revised Metadata"')
    assert initialized('search', 'Learning')['data']['total'] == 0
    assert initialized('search', 'Revised')['data']['items'][0]['revision'] == 2
    initialized('remove', source['id'], '--if-revision', 2, '--execute')
    assert initialized('list')['data']['total'] == 0
