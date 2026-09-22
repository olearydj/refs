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


def tool(name):
    path = shutil.which(name)
    if path is None:
        warnings.warn(f'Rendering consumer unavailable: {name}', stacklevel=2)
        pytest.skip(f'Rendering consumer unavailable: {name}')
    return path


def run(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout[-6000:] + result.stderr[-2000:]
    return result.stdout


def expected_facts(text):
    normalized = ' '.join(text.split())
    for fact in ['Smith', '2024', 'Python', 'Synthetic Journal', 'Jones', '2023', 'Example Press', 'Research and Development', '2022', 'STD-7', 'Doe', '2021', 'Example University']:
        assert fact in normalized, (fact, normalized)
    assert re.search(r'(?:2nd|2|second)\s*(?:ed|edition)', normalized, re.I), normalized


@pytest.mark.parametrize('consumer', ['pandoc', 'biber', 'bibtex'])
def test_actual_rendering(consumer, tmp_path, record_property):
    executable = tool(consumer)
    version = run([executable, '--version'], tmp_path).splitlines()[0]
    record_property('consumer_version', version)
    records = json.loads((ROOT/'tests/fixtures/rendering/sources.json').read_text())
    bib, _ = serialize(records)
    (tmp_path/'references.bib').write_bytes(bib)
    if consumer == 'pandoc':
        (tmp_path/'paper.md').write_text('---\nnocite: "@*"\n---\n\n# References\n')
        text = run([executable, 'paper.md', '--citeproc', '--bibliography', 'references.bib', '--csl', str(EVIDENCE/'csl/apa.csl'), '-t', 'plain'], tmp_path)
    else:
        latex, extract = tool('pdflatex'), tool('pdftotext')
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
    expected_facts(text)


@pytest.mark.parametrize('howpublished', ['arXiv:2407.01502', 'Python software, version 1.106', None])
def test_misc_render_keeps_supplied_howpublished(initialized, tmp_path, howpublished):
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
    renders = [run([tool('pandoc'), str(document), '--citeproc', '--bibliography', str(bib), '-t','plain'], tmp_path) for bib in (original,output)]
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
    assert codes.count('title_protection_added') == 1
    assert codes.count('literal_publisher') == 1


def test_online_documentation_reports_portable_quotation_change(initialized, tmp_path):
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
    texts = [run([tool('pandoc'),str(document),'--citeproc','--bibliography',str(path),'-t','plain'],tmp_path) for path in (original,exported)]
    assert '“Service API Documentation.”' in texts[0]
    assert 'Service API Documentation.' in texts[1]
    assert any('quotation marks' in warning['message'] for warning in report['warnings'])
    assert 'Web page' not in texts[1]
