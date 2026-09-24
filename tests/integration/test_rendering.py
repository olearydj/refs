"""Real consumer checks; absent tools are reported explicitly."""

import json
import re
import shutil
import subprocess
import warnings
from pathlib import Path

import pytest

from refs.bibliography import serialize

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'specs/001-academic-catalog/reviews/evidence-2026-09-20/export'


def tool(name, pytestconfig):
    path = shutil.which(name)
    if path is None:
        if pytestconfig._refs_require_tools:
            pytest.fail(f'Rendering consumer unavailable: {name}')
        warnings.warn(f'Rendering consumer unavailable: {name}', stacklevel=2)
        pytest.skip(f'Rendering consumer unavailable: {name}')
    return path


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=90)
    if result.returncode and Path(args[0]).name == 'biber':
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout[-6000:] + result.stderr[-2000:]
    return result.stdout


def expected_facts(text):
    normalized = ' '.join(text.split())
    for fact in ['Smith', '2024', 'Python', 'Synthetic Journal', 'Jones', '2023', 'Example Press', 'Research and Development', '2022', 'STD-7', 'Doe', '2021', 'Example University']:
        assert fact in normalized, (fact, normalized)
    assert re.search(r'(?:2nd|2|second)\s*(?:ed|edition)', normalized, re.I), normalized


def render_with_consumer(consumer, bib, tmp_path, record_property, pytestconfig):
    executable = tool(consumer, pytestconfig)
    version = run([executable, '--version'], tmp_path).splitlines()[0]
    record_property('consumer_version', version)
    (tmp_path/'references.bib').write_bytes(bib)
    if consumer == 'pandoc':
        (tmp_path/'paper.md').write_text('---\nnocite: "@*"\n---\n\n# References\n')
        text = run([executable, 'paper.md', '--citeproc', '--bibliography', 'references.bib', '--csl', str(EVIDENCE/'csl/apa.csl'), '-t', 'plain'], tmp_path)
    else:
        latex, extract = tool('pdflatex', pytestconfig), tool('pdftotext', pytestconfig)
        if consumer == 'biber':
            body = r'\usepackage[backend=biber,style=authoryear]{biblatex}\addbibresource{references.bib}\begin{document}\nocite{*}\printbibliography\end{document}'
        else:
            style = EVIDENCE/'fixtures/natbib/elsarticle-num.bst'
            shutil.copyfile(style, tmp_path/'elsarticle-num.bst')
            body = r'\usepackage[numbers]{natbib}\begin{document}\nocite{*}\bibliographystyle{elsarticle-num}\bibliography{references}\end{document}'
        (tmp_path/'paper.tex').write_text(r'\documentclass{article}' + body)
        run([latex, '-interaction=nonstopmode', '-halt-on-error', 'paper.tex'], tmp_path)
        run([executable, 'paper'], tmp_path)
        run([latex, '-interaction=nonstopmode', '-halt-on-error', 'paper.tex'], tmp_path)
        run([latex, '-interaction=nonstopmode', '-halt-on-error', 'paper.tex'], tmp_path)
        text = run([extract, 'paper.pdf', '-'], tmp_path)
    (tmp_path/'rendered.txt').write_text(text)
    return text


@pytest.mark.parametrize('consumer', ['pandoc', 'biber', 'bibtex'])
def test_actual_rendering(consumer, tmp_path, record_property, pytestconfig):
    records = json.loads((ROOT/'tests/fixtures/rendering/sources.json').read_text())
    bib, _ = serialize(records)
    expected_facts(render_with_consumer(consumer, bib, tmp_path, record_property, pytestconfig))


@pytest.mark.parametrize('howpublished', ['arXiv:2407.01502', 'Python software, version 1.106', None])
def test_misc_render_keeps_supplied_howpublished(initialized, tmp_path, howpublished, pytestconfig):
    from refs import bibliography, importing, projects
    raw = '@misc{example,author={Smith, Alex},title={A Study},year={2024}'
    if howpublished:
        raw += ',howpublished={' + howpublished + '}'
    raw += '}'
    original = tmp_path/'original.bib'
    original.write_text(raw)
    importing.run(tmp_path/'cat', raw.encode(), str(original))
    projects.create(tmp_path/'cat','paper','')
    projects.cite(tmp_path/'cat','paper','example')
    output = tmp_path/'output.bib'
    bibliography.export(tmp_path/'cat','paper',output)
    if howpublished:
        assert 'howpublished = {' + howpublished + '}' in output.read_text()
        assert 'note =' not in output.read_text()
    else:
        assert 'howpublished' not in output.read_text()
    document = tmp_path/'paper.md'
    document.write_text('---\nnocite: "@*"\n---\n')
    renders = [run([tool('pandoc', pytestconfig), str(document), '--citeproc', '--bibliography', str(bib), '-t','plain'], tmp_path) for bib in (original,output)]
    assert renders[0] == renders[1]


@pytest.mark.parametrize('family, expected', [(r"Garc{\'i}a", False), (r"Garc{\'i}a{\relax}", True), (r"Test{\u \i}", True)])
def test_tex_notice_only_for_observed_rendering_changes(initialized, tmp_path, family, expected):
    from refs import bibliography, importing, projects
    raw = ('@book{x,title={Study},year={2024},author={'+family+', Alex}}').encode()
    importing.run(tmp_path/'cat',raw,'synthetic.bib')
    projects.create(tmp_path/'cat','paper','')
    projects.cite(tmp_path/'cat','paper','x')
    report = bibliography.export(tmp_path/'cat','paper',tmp_path/'out.bib')
    assert any(w['code']=='tex_decoded' for w in report['warnings']) == expected


def test_added_protection_and_publisher_grouping_are_reported(initialized, tmp_path):
    from refs import bibliography, importing, projects
    raw = b'@book{x,title={The R Package},publisher={Research and Design Institute},year={2024},author={Smith, Alex}}'
    importing.run(tmp_path/'cat',raw,'synthetic.bib')
    importing.run(tmp_path/'cat',raw,'synthetic.bib')
    projects.create(tmp_path/'cat','paper','')
    projects.cite(tmp_path/'cat','paper','x')
    result = bibliography.export(tmp_path/'cat','paper',tmp_path/'out.bib')
    codes = [item['code'] for item in result['warnings']]
    assert [item['code'] for item in result['info']].count('title_protection_added') == 1
    assert 'title_protection_added' not in codes
    assert 'literal_publisher' not in codes
    assert [item['code'] for item in result['info']].count('literal_publisher') == 1


def test_online_documentation_reports_portable_quotation_change(initialized, tmp_path, pytestconfig):
    from refs import bibliography, importing, projects
    raw = b'@online{docs,author={{Example, Inc.}},title={Service API Documentation},year={2026},url={https://example.org/docs}}'
    original = tmp_path/'original.bib'
    original.write_bytes(raw)
    importing.run(tmp_path/'cat',raw,str(original))
    projects.create(tmp_path/'cat','web','')
    projects.cite(tmp_path/'cat','web','docs')
    exported = tmp_path/'exported.bib'
    report = bibliography.export(tmp_path/'cat','web',exported)
    document = tmp_path/'paper.md'
    document.write_text('---\nnocite: "@*"\n---\n')
    texts = [run([tool('pandoc', pytestconfig),str(document),'--citeproc','--bibliography',str(path),'-t','plain'],tmp_path) for path in (original,exported)]
    assert '“Service API Documentation.”' in texts[0]
    assert 'Service API Documentation.' in texts[1]
    assert any('quotation marks' in warning['message'] for warning in report['warnings'])
    assert 'Web page' not in texts[1]


@pytest.mark.parametrize('consumer', ['pandoc', 'biber', 'bibtex'])
@pytest.mark.parametrize('route', ['bib', 'csl'])
@pytest.mark.parametrize('particle', ['dropping-particle', 'non-dropping-particle'])
def test_particle_names_export_and_render(consumer, route, particle, tmp_path, record_property, pytestconfig):
    from refs.adapters import bibtex, csl
    if route == 'bib':
        flag = 'true' if particle == 'non-dropping-particle' else 'false'
        raw = ('@article{particle,title={Synthetic Particle Study},journal={Synthetic Journal},year={2020},author={family=Lopik, given=Katherine, prefix=van, useprefix='+flag+' and Smith, Alex}}').encode()
        record = bibtex.parse(raw)['source'].canonical()
    else:
        record = csl.parse(json.dumps({'type':'article-journal','title':'Synthetic Particle Study','container-title':'Synthetic Journal','issued':{'date-parts':[[2020]]},'author':[{'family':'Lopik','given':'Katherine',particle:'van'},{'family':'Smith','given':'Alex'}]}).encode()).canonical()
        record['citation_key'] = 'particle'
    assert record['metadata']['author'][0][particle] == 'van'
    bib, notices = serialize([record])
    assert b'author = {van Lopik, Katherine and Smith, Alex}' in bib
    assert not any(w['details']['class']=='unknown' for w in notices)
    assert [w['code'] for w in notices if w['code'].startswith('name_')] == ['name_particle_fallback']
    text = render_with_consumer(consumer, bib, tmp_path, record_property, pytestconfig)
    line = ' '.join(text.split())
    assert re.search(r'(?:[Vv]an Lopik|Lopik, (?:Katherine|K[.]) van)', line), line
    record_property('rendered_particle_line', line)


@pytest.mark.parametrize('consumer', ['pandoc','biber','bibtex'])
def test_arxiv_identifier_extension_render(consumer,tmp_path,record_property,pytestconfig):
    record={'schema_version':'1.0','citation_key':'arxiv','metadata':{'type':'document','title':'Synthetic Preprint','author':[{'family':'Smith','given':'Alex'}],'issued':{'date-parts':[[2024]]}},'extensions':{'identifiers':{'arxiv':'2407.01502','oclc':'456'}}}
    bib,warnings=serialize([record])
    assert b'eprint = {2407.01502}' in bib and b'eprinttype = {arxiv}' in bib
    assert b'oclc' not in bib
    assert {'arxiv_fallback','oclc_omission'} <= {w['code'] for w in warnings}
    text=render_with_consumer(consumer,bib,tmp_path,record_property,pytestconfig)
    assert '2407.01502' in text
    assert 'Smith' in text and '2024' in text


@pytest.mark.parametrize('consumer', ['pandoc','biber','bibtex'])
def test_language_aliases_and_valid_mislabel_render(consumer,tmp_path,record_property,pytestconfig):
    from refs.models import SourceCreate
    records=[]
    for index,language in enumerate(('English','eng','en','en-US','Uncatalogued Language','bn')):
        records.append(SourceCreate.model_validate({'schema_version':'1.0','citation_key':f'language{index}','metadata':{'type':'book','title':f'Synthetic Language Example {index}','author':[{'family':'Smith','given':'Alex'}],'issued':{'date-parts':[[2020+index]]},'publisher':'Example Press','language':language}}).canonical())
    output,warnings=serialize(records)
    assert any(w['code']=='language_unrecognized' for w in warnings)
    assert any(w['code']=='title_language_review' for w in warnings)
    text=render_with_consumer(consumer,output,tmp_path,record_property,pytestconfig)
    for year in range(2020,2026):
        assert str(year) in text
    assert 'Smith' in text


@pytest.mark.parametrize('consumer',['pandoc','biber','bibtex'])
@pytest.mark.parametrize(('raw','iso','parts'),[
    ('19-23 March 2011','2011-03-19/2011-03-23',[[2011,3,19],[2011,3,23]]),
    ('08–13 Sep 2022','2022-09-08/2022-09-13',[[2022,9,8],[2022,9,13]]),
])
def test_range_year_matches_bbt_render(consumer,raw,iso,parts,tmp_path,record_property,pytestconfig):
    from refs.adapters import zotero
    original=f'@inproceedings{{range,title={{Synthetic Range Study}},author={{Smith, Alex}},booktitle={{Synthetic Proceedings}},date={{{iso}}}}}'
    (tmp_path/'bbt.bib').write_text(original)
    (tmp_path/'compare.md').write_text('---\nnocite: "@*"\n---\n')
    baseline=run([tool('pandoc', pytestconfig),'compare.md','--citeproc','--bibliography','bbt.bib','-t','plain'],tmp_path)
    value=zotero.parse({'key':'RANGE001','meta':{'parsedDate':iso.split('/')[0]},'data':{'itemType':'conferencePaper','citationKey':'range','title':'Synthetic Range Study','proceedingsTitle':'Synthetic Proceedings','date':raw,'creators':[{'creatorType':'author','lastName':'Smith','firstName':'Alex'}]}},{'library_uri':'users/123'})['source'].canonical()
    assert value['metadata']['issued']['date-parts']==parts
    output,warnings=serialize([value])
    assert b'note =' not in output
    rendered=render_with_consumer(consumer,output,tmp_path,record_property,pytestconfig)
    year=str(parts[0][0])
    assert year in baseline and year in rendered
    assert any(w['code']=='date_range_projected' for w in warnings)
