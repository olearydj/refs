import pytest

from refs import bibliography
from refs.adapters import bibtex, zotero


@pytest.mark.parametrize('series',["Annual '06","Mobile '15",'Proceedings of Synthetic Research'])
def test_conference_series_converges_and_exports(series):
    native={'key':'CONF0001','data':{'itemType':'conferencePaper','title':'Synthetic Study','proceedingsTitle':'Collected Studies','series':series,'citationKey':'conference','date':'2024'}}
    result=zotero.parse(native,{'library_uri':'users/123'})
    assert not result['limitations']
    assert result['source'].metadata.collection_title==series
    for kind in ('inproceedings','conference'):
        bib=f'@{kind}{{conference,title={{Synthetic Study}},booktitle={{Collected Studies}},series={{{series}}},year={{2024}}}}'
        source=bibtex.parse(bib.encode())['source']
        assert source.metadata.collection_title==series
    output,_=bibliography.serialize([result['source'].canonical()])
    assert ('series = {'+series+'}').encode() in output


def test_genre_status_and_other_native_fields_stay_preserved_only():
    fields={'genre':'Research','status':'Published','libraryCatalog':'Library','callNumber':'ABC','archiveLocation':'Shelf','rights':'Copyright','websiteType':'Blog'}
    source={'key':'ITEM0001','data':{'itemType':'webpage','title':'Synthetic Page',**fields}}
    result=zotero.parse(source,{'library_uri':'users/123'})
    canonical=result['source'].canonical()
    assert not canonical['metadata'].get('genre') and not canonical['metadata'].get('status')
    assert {item['field']:item['reason'] for item in result['limitations']}=={k:'Preserved from import: '+k for k in fields}
