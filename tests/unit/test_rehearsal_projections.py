import pytest

from refs import bibliography


@pytest.mark.parametrize(('kind','metadata','extensions','expected','code'),[
    ('book',{'contributor':[{'family':'Contributor'}]}, {}, b'@book', 'contributor_omission'),
    ('book',{'collection-editor':[{'family':'Series','given':'Alex'}]}, {}, b'editor = {Series, Alex}', 'collection_editor_fallback'),
    ('chapter',{'container-title':'Collected Work','container-author':[{'family':'Book','given':'Alex'}]}, {}, b'bookauthor = {Book, Alex}', 'container_author_omission'),
    ('article-journal',{'container-title':'Journal'}, {'journal_series':'Second Series'}, b'series = {Second Series}', 'journal_series_fallback'),
    ('patent',{}, {'patent':{'assignees':[{'literal':'Research and Design'},{'family':'Holder','given':'Alex'}]}}, b'{A}ssignee: Research and Design; Alex Holder', 'assignee_in_note'),
    ('article',{}, {'identifiers':{'arxiv':'arXiv:2407.01502 [cs.AI]','oclc':'123456'}}, b'eprint = {2407.01502}', 'arxiv_fallback'),
])
def test_assessed_rehearsal_projections(kind,metadata,extensions,expected,code):
    record={'schema_version':'1.0','citation_key':'fixture','metadata':{'type':kind,'title':'Fixture Title','author':[{'family':'Author'}],'issued':{'date-parts':[[2024]]},**metadata},'extensions':extensions}
    output,warnings=bibliography.serialize([record])
    assert expected in output
    assert all(w['details']['class']!='unknown' for w in warnings)
    category = 'info' if code == 'assignee_in_note' else 'documented_fallback'
    assert any(w['code']==code and w['details']['class']==category for w in warnings)
    if metadata.get('contributor'):
        assert b'Contributor' not in output
    if kind=='patent':
        assert b'author = {Author}' in output
    if extensions.get('identifiers'):
        assert b'123456' not in output
        assert any(w['code']=='oclc_omission' for w in warnings)


def test_collection_editors_preserve_existing_editors_and_deduplicate():
    record={'schema_version':'1.0','citation_key':'book','metadata':{'type':'book','title':'Book','editor':[{'family':'Editor'}],'collection-editor':[{'family':'Editor'},{'family':'Series'}]}}
    output,_=bibliography.serialize([record])
    assert b'editor = {Editor and Series}' in output


def test_container_author_on_traditional_book_part():
    record={'schema_version':'1.0','citation_key':'part','metadata':{'type':'chapter','container-title':'Book','page':'3-7','container-author':[{'literal':'Research and Design'}]}}
    output,_=bibliography.serialize([record])
    assert output.startswith(b'@inbook{part,')
    assert b'bookauthor = {{Research and Design}}' in output
