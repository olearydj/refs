"""Independent values cross actual adapters; upstream probes are not importers."""

import json
from pathlib import Path

import pytest

from refs import bibliography, naming, sources
from refs.adapters import bibtex, csl
from refs.models import REGISTRY, SourceCreate, parse
from refs.results import RefError

CASES = json.loads((Path(__file__).parents[1]/'fixtures/mappings/bib-rows.json').read_text())


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['type']+'-'+case['field'])
def test_bib_refs_csl_convergence_and_clear(initialized, tmp_path, case):
    proposal = bibtex.parse(case['bib'].encode())['source'].canonical()
    if case['field'] == 'howpublished':
        assert 'note' not in proposal['metadata']
        assert case['expected'] in case['bib']  # Preserved-only; actual export is tested with original bytes.
        return
    if case['field'] == 'eprint':
        assert proposal['extensions']['identifiers']['arxiv'] == case['expected']
        assert 'number' not in proposal['metadata']
        return
    assert proposal['metadata'][case['path']] == case['expected']
    expected = proposal['metadata']
    assert csl.parse(json.dumps(expected).encode()).canonical()['metadata'] == expected
    assert parse(json.dumps({'schema_version':'1.0','metadata':expected}).encode()).canonical()['metadata'] == expected
    # Every input remains editable, and original Bib values never restore clears.
    proposal['metadata']['URL'] = 'https://example.org/recognizable'
    created = sources.add(tmp_path/'cat', json.dumps(proposal).encode(), 'fixture.json')
    field = 'metadata.'+case['path']
    replacement = {'date-parts': [[2025]]} if isinstance(case['expected'], dict) else [{'family':'Changed'}] if isinstance(case['expected'], list) else 3 if isinstance(case['expected'], int) else 'https://example.org/changed' if case['path']=='URL' else 'de' if case['path']=='language' else '10.1000/changed' if case['path']=='DOI' else 'Changed Value'
    edited = sources.update(tmp_path/'cat', created['id'], {'schema_version':'1.0','set':{field:replacement}}, created['revision'])
    assert edited['metadata'][case['path']] == replacement
    created = edited
    current = sources.update(tmp_path/'cat', created['id'], {'schema_version':'1.0','clear':[field]}, created['revision'])
    assert case['path'] not in current['metadata']
    output, _ = bibliography.serialize([current])
    assert b'{fixture,' in output
    assert case['path'] not in current['metadata']


@pytest.mark.parametrize('fields', [
    'journal={First},journaltitle={Second}',
    'issue={1},number={2}',
    'language={en},langid={de}',
])
def test_alias_conflicts_are_not_route_priority(fields):
    with pytest.raises(RefError) as error:
        bibtex.parse(('@article{x,title={Test},'+fields+'}').encode())
    assert error.value.issue['code'] == 'invalid_bib_entry'
    assert error.value.issue['message'].startswith('Conflicting aliases for metadata.')


def test_extensions_remain_distinct_and_assessed():
    source = SourceCreate.model_validate({'schema_version':'1.0','citation_key':'patent','metadata':{'type':'patent','title':'Synthetic Patent','author':[{'family':'Inventor'}], 'number':'GRANT-1', 'issued':{'date-parts':[[2024]]}}, 'extensions':{'patent':{'assignees':[{'literal':'Research and Design'}], 'application_number':'APP-2','priority_date':{'date-parts':[[2020]]}}}})
    assert bibtex.parse(b'@patent{x,title={Synthetic Patent},author={Inventor},holder={{Research and Design}},number={GRANT-1}}')['source'].extensions.patent.assignees == source.extensions.patent.assignees
    with pytest.raises(RefError) as error:
        bibliography.serialize([source.canonical()])
    assert error.value.issue['code'] == 'export_blocked'
    for kind, extensions in [('patent',source.extensions.model_dump(by_alias=True, exclude_none=True)), ('article-journal',{'journal_series':'Journal Series'})]:
        canonical = {'schema_version':'1.0','citation_key':'fixture','metadata':{'type':kind,'title':'Fixture Title'},'extensions':extensions}
        assert parse(json.dumps(canonical).encode()).extensions.model_dump(by_alias=True, exclude_none=True) == extensions


def test_title_and_person_details():
    proposal = bibtex.parse(br'@book{x,title={Using {Python} and {NASA}},author={de Vries, Alex and {Research and Design}},edition={2},series={Series},number={4}}')['source'].canonical()
    normalized, _ = naming.normalize(proposal)
    assert normalized['title_protection']['title']['protected_terms'] == ['Python','NASA']
    assert normalized['metadata']['author'][1] == {'literal':'Research and Design'}


@pytest.mark.parametrize('kind', REGISTRY['core_fields']['type']['schema']['enum'])
def test_observed_type_families(kind):
    canonical = {'schema_version':'1.0','citation_key':'fixture','metadata':{'type':kind,'title':'Fixture Title','author':[{'family':'Smith'}], 'issued':{'date-parts':[[2024]]}, 'language':'en'}}
    refs = parse(json.dumps(canonical).encode()).canonical()
    assert csl.parse(json.dumps(canonical['metadata']).encode()).canonical()['metadata'] == refs['metadata']
    output, warnings = bibliography.serialize([refs])
    incoming = bibtex.parse(bibtex.partition(output)[0]['raw'])['source'].canonical()
    assert incoming['metadata']['author'] == refs['metadata']['author']
    assert incoming['metadata']['issued'] == refs['metadata']['issued']
    if incoming['metadata']['type'] != kind:
        assert any(warning['details']['class']=='documented_fallback' for warning in warnings)


CSL_ONLY = json.loads((Path(__file__).parents[1]/'fixtures/mappings/csl-only-rows.json').read_text())


@pytest.mark.parametrize('case', CSL_ONLY, ids=lambda case: case['field'])
def test_remaining_csl_rows_edit_clear_and_assessment(initialized,tmp_path,case):
    metadata={'type':case['type'],'title':'Fixture Title',case['field']:case['expected']}
    proposal=csl.parse(json.dumps(metadata).encode()).canonical()
    assert parse(json.dumps(proposal).encode()).metadata.model_dump(by_alias=True,exclude_none=True) == metadata
    source=sources.add(tmp_path/'cat',json.dumps(metadata).encode(),'csl.json',format='csljson')
    path='metadata.'+case['field']
    replacement={'date-parts':[[2025]]} if isinstance(case['expected'],dict) else [{'family':'Changed'}] if isinstance(case['expected'],list) else 'Changed Value'
    changed=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{path:replacement}},source['revision'])
    assert changed['metadata'][case['field']]==replacement
    if case['field'] in {'submitted','original-date','event-date'}:
        with pytest.raises(RefError) as error:
            bibliography.serialize([changed])
        assert error.value.issue['code']=='export_blocked'
        assert any(entry['code']=='unassessed_mapping' and entry['path']=='metadata.'+case['field'] for entry in error.value.issue['details']['entries'])
    else:
        output,_=bibliography.serialize([changed])
        assert b'{' + changed['citation_key'].encode() + b',' in output
    cleared=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','clear':[path]},changed['revision'])
    assert case['field'] not in cleared['metadata']


@pytest.mark.parametrize(('kind','extension','value','replacement'),[
    ('patent','patent.assignees',[{'literal':'Research and Design'}],[{'literal':'Other Institution'}]),
    ('patent','patent.application_number','APP-1','APP-2'),
    ('patent','patent.priority_date',{'date-parts':[[2020]]},{'date-parts':[[2021]]}),
    ('article-journal','journal_series','Series One','Series Two'),
])
def test_extension_edits_and_clears(initialized,tmp_path,kind,extension,value,replacement):
    canonical={'schema_version':'1.0','metadata':{'type':kind,'title':'Fixture Title','number':'GRANT-1'} if kind=='patent' else {'type':kind,'title':'Fixture Title'},'extensions':{}}
    node=canonical['extensions']
    parts=extension.split('.')
    for part in parts[:-1]:
        node=node.setdefault(part,{})
    node[parts[-1]]=value
    source=sources.add(tmp_path/'cat',json.dumps(canonical).encode(),'extension.json')
    path='extensions.'+extension
    changed=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{path:replacement}},source['revision'])
    if extension in ('patent.assignees','journal_series'):
        output,_=bibliography.serialize([changed])
        assert b'{'+changed['citation_key'].encode()+b',' in output
    else:
        with pytest.raises(RefError) as error:
            bibliography.serialize([changed])
        assert error.value.issue['code']=='export_blocked'
        assert {item['code'] for item in error.value.issue['details']['entries']} & {'unassessed_extension','unsupported_record'}
    cleared=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','clear':[path]},changed['revision'])
    assert path in cleared['corrected_fields']
    if kind=='patent':
        assert cleared['metadata']['number']=='GRANT-1'
