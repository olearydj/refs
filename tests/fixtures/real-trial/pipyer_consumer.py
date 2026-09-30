"""Native Pipyer draft PDF gate in a disposable project copy."""
import json
import re
import subprocess
from pathlib import Path

root = Path.cwd()
assert not (root / '.git').exists(), 'Pipyer gate refuses a live checkout'
out = root / '.refs-gate'
out.mkdir(exist_ok=True)
# Execution-only adoption preparation; remove after the project adopts.
config = root / '_quarto.yml'
assert 'bibliography: references.bib' in config.read_text()
config.write_text(config.read_text().replace('bibliography: references.bib', 'bibliography: references.json'))
paper = root / 'paper.qmd'
assert '@kapoor2024' in paper.read_text()
paper.write_text(paper.read_text().replace('@kapoor2024', '@kapoor-2025-aiAgents'))
subprocess.run(['quarto', 'render', 'paper.qmd', '--to', 'pdf', '-M', 'keep-tex:true'], check=True)
text = subprocess.check_output(['pdftotext', '-layout', str(root / 'output/pdf/paper.pdf'), '-'], text=True)
(out / 'pdf-text.txt').write_text(text)
tex = (root / 'paper.tex').read_text()
keys = re.findall(r'\\bibitem\[\\citeproctext\]\{ref-([^}]+)\}', tex)
records = {r['id']: r for r in json.loads((root / 'references.json').read_text())}
cites = re.findall(r'\\citeproc\{ref-([^}]+)\}', tex)
assert len(keys) == len(records) and set(keys) == set(records) == set(cites)
references = text.rsplit('\nReferences\n', 1)[1]
references = re.sub(r'^\s*\d+\s*$', '', references, flags=re.M).replace('\f', '')
entries = [' '.join(part.split()) for part in re.split(r'\n\s*\n', references) if part.strip()]
assert len(entries) == len(keys), 'Native PDF entry boundaries differ from bibliography identities'
rows = []
for key, entry in zip(keys, entries, strict=True):
    author = records[key]['author'][0]
    assert entry.startswith(author.get('literal') or author['family'] + ','), (key, entry)
    locator = records[key].get('DOI') or records[key].get('URL')
    assert locator and re.sub(r'\s+', '', locator) in re.sub(r'\s+', '', entry), (key, locator)
    rows.append({'key': key, 'text': entry})
(out / 'pdf.json').write_text(json.dumps(rows, ensure_ascii=False))
(out / 'citations.json').write_text(json.dumps(cites))
