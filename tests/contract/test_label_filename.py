import json

from refs import naming, sources


def test_labelled_releases_and_collision(initialized,tmp_path):
    value={'schema_version':'1.0','citation_key':'git','metadata':{'type':'book','title':'Boost Your Git DX','issued':{'date-parts':[[2023]]}}}
    sources.add(tmp_path/'cat',json.dumps(value).encode(),'fixture.json')
    incoming=tmp_path/'download.pdf'
    for label in ('r2023-06-03','r2023-10-04'):
        incoming.write_bytes(label.encode())
        result=initialized('resource','add','git','--path',incoming,'--copy','--label',label)['data']
        assert result['relative']==f'unfiled/BoostYourGitDX-2023-{label}.pdf'
    failed=initialized('resource','add','git','--path',incoming,'--copy','--label','r2023-10-04',expected=3)
    assert failed['errors'][0]['code']=='destination_exists'
    assert naming.filename(value,'download.pdf')=='BoostYourGitDX-2023.pdf'
    assert naming.filename(value,'download.pdf',' mobile / 1.2_β!')=='BoostYourGitDX-2023-mobile1.2β.pdf'
    incoming.write_bytes(b'keep original name')
    result=initialized('resource','add','git','--path',incoming,'--copy','--label','mobile','--keep-name')['data']
    assert result['relative']=='unfiled/download.pdf'
