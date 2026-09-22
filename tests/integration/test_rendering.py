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
