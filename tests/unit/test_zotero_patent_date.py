import pytest

from refs import bibliography
from refs.adapters import zotero
from refs.results import RefError


def test_native_patent_issue_date_is_admitted_and_exported():
    item={'key':'PATENT01','data':{'itemType':'patent','title':'Synthetic Viewing Apparatus','citationKey':'patent1960','issueDate':'1960-00-00 1960'}}
    result=zotero.parse(item,{'library_uri':'users/123'})
    assert result['source'].metadata.issued.date_parts==[[1960]]
    assert not result['limitations']
    output,warnings=bibliography.serialize([result['source'].canonical()])
    assert b'year = {1960}' in output
    assert not any(w['code']=='missing_issued' for w in warnings)
    item['data']['date']='1961'
    with pytest.raises(RefError,match='Competing values'):
        zotero.parse(item,{'library_uri':'users/123'})


def test_unparsed_patent_date_is_preserved_literally():
    item={'key':'PATENT01','data':{'itemType':'patent','title':'Synthetic Patent','issueDate':'Undetermined date'}}
    result=zotero.parse(item,{'library_uri':'users/123'})
    assert result['source'].metadata.issued.literal=='Undetermined date'
    assert result['limitations'][0]['field']=='issueDate'
