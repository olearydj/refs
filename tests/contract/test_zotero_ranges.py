import pytest

from refs.adapters import zotero


@pytest.mark.parametrize(('raw','parsed','expected'),[
    ('19-23 March 2011','2011-03-19',[[2011,3,19],[2011,3,23]]),
    ('08–13 Sep 2022','2022-09-08',[[2022,9,8],[2022,9,13]]),
    ('2019/2020','2019-00-00',[[2019],[2020]]),
    ('2011-03-19 19-23 March 2011',None,[[2011,3,19],[2011,3,23]]),
    ('2019-12-30/2020-01-02','2019-12-30',[[2019,12,30],[2020,1,2]]),
])
def test_ranges_keep_both_endpoints(raw,parsed,expected):
    assert zotero.date(raw,parsed)=={'date-parts':expected}


@pytest.mark.parametrize('raw',['Late 2019–early 2020','19 March to 23 April 2011','March 19–23, 2011','31-32 February 2011','2020/2019','2019/unknown','19-23 Marching 2011'])
def test_unparsed_ranges_never_collapse_to_parsed_start(raw):
    item={'key':'RANGE001','meta':{'parsedDate':'2019-01-01'},'data':{'itemType':'conferencePaper','title':'Synthetic Range','date':raw}}
    result=zotero.parse(item,{'library_uri':'users/123'})
    assert result['source'].metadata.issued.literal==raw
    assert result['source'].metadata.issued.date_parts is None
    assert result['limitations'][0]['field']=='date'


@pytest.mark.parametrize(('raw','parsed','parts'),[
    ('2019-12-30','2019-12-30',[[2019,12,30]]),
    ('2019/12/30','2019-12-30',[[2019,12,30]]),
    ('12/2019','2019-12-00',[[2019,12]]),
    ('2/2/24','2024-02-02',[[2024,2,2]]),
    ('2019-12-30T12:00:00Z','2019-12-30',[[2019,12,30]]),
])
def test_single_dates_are_not_ranges(raw,parsed,parts):
    assert zotero.date(raw,parsed)=={'date-parts':parts}


@pytest.mark.parametrize(('parts','month'),[
    ([[2011,3,19],[2011,3,23]],b'month = mar'),
    ([[2022,9,8],[2022,9,13]],b'month = sep'),
    ([[2019],[2020]],None),
    ([[2019,12,30],[2020,1,2]],None),
])
def test_portable_range_projects_year_and_shared_month_without_note(parts,month):
    from refs import bibliography
    record={'schema_version':'1.0','citation_key':'range','metadata':{'type':'paper-conference','title':'Synthetic Range','issued':{'date-parts':parts}}}
    output,warnings=bibliography.serialize([record])
    assert f'year = {{{parts[0][0]}}}'.encode() in output
    assert (month in output) if month else b'month =' not in output
    assert b'note =' not in output and b'date =' not in output
    assert record['metadata']['issued']['date-parts']==parts
    notice=next(w for w in warnings if w['code']=='date_range_projected')
    assert notice['details']['class']=='documented_fallback'
    assert notice['details']['citation_key']=='range'
