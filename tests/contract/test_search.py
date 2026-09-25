
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



def test_creators_diacritics_and_exact_identifiers(initialized, tmp_path):
    import json

    from refs import search, sources
    raw = {'schema_version':'1.0','citation_key':'koster2012','metadata':{'type':'article-journal','title':'Synthetic Workflow','author':[{'family':'Köster','given':'Alex'},{'family':'Bazaz','given':'Sara'},{'family':'Lohtander','given':'Mika'}],'DOI':'10.5555/synthetic.workflow'}}
    source = sources.add(tmp_path/'cat',json.dumps(raw).encode(),'synthetic')
    for query in ('Köster','koster','Bazaz','Lohtander','Alex Köster'):
        found = search.retrieve(tmp_path/'cat',query)['items']
        assert len(found) == 1 and found[0]['id'] == source['id']
        assert any(match['field'] == 'metadata.author' for match in found[0]['matches'])
    for query in ('koster2012','10.5555/synthetic.workflow','https://doi.org/10.5555/SYNTHETIC.WORKFLOW'):
        result = search.retrieve(tmp_path/'cat',query)['items'][0]
        assert result['id'] == source['id'] and result['exact_match']


def test_search_resolves_full_records_only_for_page(initialized,tmp_path,monkeypatch):
    import json

    from refs import search, sources

    expected=[]
    for index in range(4):
        raw={'schema_version':'1.0','citation_key':f'common-{index}',
             'metadata':{'title':f'Common Work {index}'}}
        expected.append(sources.add(tmp_path/'cat',json.dumps(raw).encode(),f'synthetic-{index}')['id'])
    record=sources.record
    resolved=[]
    def counted(connection,source_id):
        resolved.append(source_id)
        return record(connection,source_id)
    monkeypatch.setattr(sources,'record',counted)
    result=search.retrieve(tmp_path/'cat','Common',sort='key',limit=1,offset=2)
    assert result['total']==4 and result['items'][0]['id']==expected[2]
    assert resolved==[expected[2]]
    assert result['items'][0]['revision']==1
    assert any(match['field']=='metadata.title' for match in result['items'][0]['matches'])
