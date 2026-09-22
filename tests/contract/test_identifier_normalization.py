import json

import pytest

from refs import bibliography, importing, sources
from refs.adapters import bibtex, csl, zotero
from refs.models import SourceCreate
from refs.results import RefError


def test_validator_normalizes_all_routes_and_keeps_version(initialized,tmp_path):
    metadata={'type':'article','title':'A Preprint','archive':'arXiv','number':'arXiv:2407.01502v2 [cs.AI]','DOI':'https://doi.org/10.48550/arXiv.2407.01502v2'}
    direct=SourceCreate.model_validate({'schema_version':'1.0','metadata':metadata,'extensions':{'identifiers':{'arxiv':'ARXIV:2407.01502v2 [cs.AI]'}}}).canonical()
    csl_record=csl.parse(json.dumps(metadata).encode()).canonical()
    bib=bibtex.parse(b'@misc{x,title={A Preprint},archiveprefix={arXiv},eprint={arXiv:2407.01502v2 [cs.AI]},doi={https://doi.org/10.48550/arXiv.2407.01502v2}}')['source'].canonical()
    for value in (direct,csl_record,bib):
        assert value['metadata']['DOI']=='10.48550/arxiv.2407.01502v2'
        assert value['extensions']['identifiers']['arxiv']=='2407.01502v2'
    for format,value in [('refs',{'schema_version':'1.0','metadata':metadata}),('csljson',metadata)]:
        record=sources.add(tmp_path/'cat',json.dumps(value).encode(),format,format=format)
        current=sources.update(tmp_path/'cat',record['id'],{'schema_version':'1.0','set':{'extensions.identifiers.arxiv':'arXiv:2407.01502v2 [cs.AI]','metadata.DOI':'HTTPS://DOI.ORG/10.48550/ARXIV.2407.01502v2'}},record['revision'])
        assert current['metadata']['DOI']=='10.48550/arxiv.2407.01502v2'
        assert current['extensions']['identifiers']['arxiv']=='2407.01502v2'


def test_zotero_preprint_aliases_collapse_without_export_block():
    item={'key':'ITEM0001','data':{'itemType':'preprint','title':'A Preprint','archiveID':'arXiv:2407.01502v2 [cs.AI]','repository':'arXiv','DOI':'https://doi.org/10.48550/arXiv.2407.01502v2','extra':'arxiv: 2407.01502v2\nDOI: 10.48550/arxiv.2407.01502v2','citationKey':'preprint'}}
    source=zotero.parse(item,{'library_uri':'users/123'})['source'].canonical()
    assert 'number' not in source['metadata']
    assert source['extensions']['identifiers']['arxiv']=='2407.01502v2'
    output,warnings=bibliography.serialize([source])
    assert output.count(b'eprint = {2407.01502v2}')==1
    assert output.count(b'arXiv:2407.01502v2')==1
    assert not any(w['code']=='work_identity_changed' for w in warnings)


def test_unequal_normalized_preprint_values_still_block():
    value={'schema_version':'1.0','citation_key':'different','metadata':{'type':'article','title':'A Preprint','archive':'arXiv','number':'arXiv:2407.01502v1 [cs.AI]'},'extensions':{'identifiers':{'arxiv':'2407.01502v2'}}}
    with pytest.raises(RefError) as error:
        bibliography.serialize([value])
    assert any(loss['code']=='work_identity_changed' for loss in error.value.issue['details']['entries'])


def test_arxiv_promoted_from_bib_remains_editable_and_clearable(initialized, tmp_path):
    importing.run(tmp_path/'cat',b'@unpublished{x,title={Preprint},archiveprefix={arXiv},eprint={arXiv:2407.01502v1 [cs.AI]}}','preprint.bib')
    source=sources.show(tmp_path/'cat','x')
    updated=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'extensions.identifiers.arxiv':'arXiv:2407.01502v2 [cs.AI]'}},source['revision'])
    assert updated['extensions']['identifiers']['arxiv']=='2407.01502v2'
    cleared=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','clear':['extensions.identifiers.arxiv']},updated['revision'])
    output,_=bibliography.serialize([cleared])
    assert b'eprint =' not in output
