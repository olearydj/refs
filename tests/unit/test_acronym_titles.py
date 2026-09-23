from refs import naming


def test_mixed_title_keeps_acronyms_without_warning():
    title='Exploring the MIT Mathematics and EECS Curriculum Using Large Language Models'
    record,warnings=naming.normalize({'metadata':{'type':'book','title':title}})
    assert record['metadata']['title']==title
    assert warnings==[]
    assert {'MIT','EECS'} <= set(record['title_protection']['title']['protected_terms'])


def test_shouted_title_warns():
    _,warnings=naming.normalize({'metadata':{'type':'book','title':'A STUDY OF THINGS IN CAPS'}})
    assert [warning['code'] for warning in warnings]==['unprotected_capital']


def test_acronym_that_is_a_minor_word_is_kept():
    record,warnings=naming.normalize({'metadata':{'type':'book','title':'An AS Study'}})
    assert record['metadata']['title']=='An AS Study' and not warnings
