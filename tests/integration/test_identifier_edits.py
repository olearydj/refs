import json

from refs import bibliography, importing, sources


def test_identifier_edits_normalize_all_routes(initialized,tmp_path):
    metadata={'type':'article','title':'A Preprint','archive':'arXiv','number':'arXiv:2407.01502v2 [cs.AI]','DOI':'https://doi.org/10.48550/arXiv.2407.01502v2'}
    for format,value in [('refs',{'schema_version':'1.0','metadata':metadata}),('csljson',metadata)]:
        record=sources.add(tmp_path/'cat',json.dumps(value).encode(),format,format=format)
        current=sources.update(tmp_path/'cat',record['id'],{'schema_version':'1.0','set':{'extensions.identifiers.arxiv':'arXiv:2407.01502v2 [cs.AI]','metadata.DOI':'HTTPS://DOI.ORG/10.48550/ARXIV.2407.01502v2'}},record['revision'])
        assert current['metadata']['DOI']=='10.48550/arxiv.2407.01502v2'
        assert current['extensions']['identifiers']['arxiv']=='2407.01502v2'


def test_arxiv_promoted_from_bib_remains_editable_and_clearable(initialized, tmp_path):
    importing.run(tmp_path/'cat',b'@unpublished{x,title={Preprint},archiveprefix={arXiv},eprint={arXiv:2407.01502v1 [cs.AI]}}','preprint.bib')
    source=sources.show(tmp_path/'cat','x')
    updated=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','set':{'extensions.identifiers.arxiv':'arXiv:2407.01502v2 [cs.AI]'}},source['revision'])
    assert updated['extensions']['identifiers']['arxiv']=='2407.01502v2'
    cleared=sources.update(tmp_path/'cat',source['id'],{'schema_version':'1.0','clear':['extensions.identifiers.arxiv']},updated['revision'])
    output,_=bibliography.serialize([cleared])
    assert b'eprint =' not in output
