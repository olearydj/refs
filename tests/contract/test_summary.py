"""summary is one read-only picture of the catalog; list and search say when more pages exist."""

import json


def variant(reference_path, key, **metadata):
    payload = json.loads(reference_path.read_text()) | {'citation_key': key}
    payload['metadata'] = {name: value for name, value in payload['metadata'].items() if name not in ('DOI', 'ISBN', 'URL')} | metadata
    payload['provenance'] = [{'origin': 'agent', 'access': 'metadata'}]  # no identity: each variant is its own source
    return payload


def test_summary_counts_sources_files_kinds_projects_and_targets(initialized, human, tmp_path, reference_path):
    empty = initialized('summary')['data']
    assert empty['sources'] == dict(active=0, removed=0, with_files=0, without_files=0)
    assert empty['projects'] == [] and empty['imports']['last'] is None and empty['types'] == {}
    created = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    (tmp_path / 'podcast.json').write_text(json.dumps(variant(reference_path, 'podcast-one', type='song', genre='Audio podcast', title='An episode')))
    initialized('add', '--format', 'refs', '--input', tmp_path / 'podcast.json')
    (tmp_path / 'tool.json').write_text(json.dumps(variant(reference_path, 'tool-one', type='software', title='A tool')))
    initialized('add', '--format', 'refs', '--input', tmp_path / 'tool.json')
    attachment = tmp_path / 'paper.pdf'
    attachment.write_bytes(b'%PDF-1.4 minimal')
    initialized('resource', 'add', created['citation_key'], '--path', attachment, '--copy')
    initialized('project', 'create', 'demo', '--description', 'summary demo')
    initialized('project', 'cite', 'demo', created['citation_key'])
    target = tmp_path / 'demo.json'
    initialized('export', '--project', 'demo', '--output', target, '--profile', 'csl-json-v1')
    data = initialized('summary')['data']
    assert data['sources'] == dict(active=3, removed=0, with_files=1, without_files=2)
    assert data['files']['managed'] == 1 and data['files']['unfiled'] == 1 and data['files']['linked'] == 0
    assert data['files']['missing'] == 0 and data['files']['unrecorded'] == 0
    assert data['types'][created['metadata']['type']] == 1 and data['types']['song'] == 1 and data['types']['software'] == 1
    assert data['kinds'] == dict(assigned={'podcast': 1}, unassigned={'software': 1})
    assert data['projects'] == [dict(name='demo', description='summary demo', cited=1,
                                     targets=[dict(destination=str(target), profile='csl-json-v1', state='current')])]
    target.write_text('edited outside refs\n')
    assert initialized('summary')['data']['projects'][0]['targets'][0]['state'] == 'outside_edit'
    target.unlink()
    assert initialized('summary')['data']['projects'][0]['targets'][0]['state'] == 'missing'
    assert data['catalog']['schema_version'] >= 6 and data['locs'] == [dict(loc='unfiled', count=1)] and data['collections'] == []
    text = human('summary')
    for heading in ('Catalog', 'Sources by type', 'Kinds', 'Locations', 'Collections', 'Projects'):
        assert heading in text
    assert '3 active, 0 removed; 1 with files, 2 without' in text
    assert 'unassigned software\t1' in text and 'demo\t1 cited' in text


def test_list_and_search_footers_name_the_next_page(initialized, human, tmp_path, reference_path):
    for index in range(3):
        (tmp_path / f'p{index}.json').write_text(json.dumps(variant(reference_path, f'paged-{index}', title=f'Paged title {index}')))
        initialized('add', '--format', 'refs', '--input', tmp_path / f'p{index}.json')
    assert initialized('list', '--limit', 2)['data']['total'] == 3
    assert human('list', '--limit', 2).rstrip().endswith('2 of 3 sources shown; --offset 2 for the next page, --limit 1000 for up to 1000 at once')
    assert human('list', '--limit', 2, '--offset', 2).rstrip().endswith('1 source')
    assert human('list').rstrip().endswith('3 sources')
    assert human('search', 'Paged', '--limit', 1).rstrip().endswith('1 of 3 sources shown; --offset 1 for the next page, --limit 1000 for up to 1000 at once')
