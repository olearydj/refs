from refs.adapters.bibtex import original_facts


def test_original_facts_preserve_howpublished_and_tex_evidence():
    raw = br'@misc{sample,title={R},howpublished={Archive copy},author={Smith, \relax Alex},journal={journal of tests}}'
    facts = original_facts(raw)
    assert len(facts) == 1
    assert facts[0]['type'] == 'misc'
    assert facts[0]['howpublished'] == ['Archive copy']
    assert facts[0]['containers'] == [('journal', 'journal of tests')]
    assert facts[0]['titles'] == ['R']
    assert [(notice['code'], notice['path']) for notice in facts[0]['tex_notices']] == [('tex_decoded', 'author')]
