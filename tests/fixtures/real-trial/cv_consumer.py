"""Scratch-only native CV rendering and reference extraction."""
import json
import re
import subprocess
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

root = Path.cwd()
assert not (root / '.git').exists(), 'CV gate refuses a live checkout'
output = root / '.refs-gate'
output.mkdir(exist_ok=True)
mode = sys.argv[1]
assert mode in ('html', 'pdf')
if mode == 'html':
    subprocess.run(['quarto', 'render', 'cv-master.qmd', '--to', 'all'], check=True)

class Entries(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.entry = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div':
            self.depth += 1
            if 'csl-entry' in attrs.get('class', '').split():
                self.entry = {'key': attrs['id'][4:], 'parts': [], 'depth': self.depth}

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.entry and self.entry['depth'] == self.depth:
                self.rows.append({'key': self.entry['key'], 'text': ' '.join(''.join(self.entry['parts']).split())})
                self.entry = None
            self.depth -= 1

    def handle_data(self, data):
        if self.entry:
            self.entry['parts'].append(data)

parser = Entries()
parser.feed((root / '_output/cv-master.html').read_text())
keys = {record['id'] for record in json.loads((root / 'refs/cv.json').read_text())}
assert len(parser.rows) == len(keys) and {row['key'] for row in parser.rows} == keys
rows = parser.rows
if mode == 'pdf':
    # HTML supplies identities, never replacement PDF content. Locate every complete
    # entry in the independently extracted native PDF and retain that PDF substring.
    text = subprocess.check_output(['pdftotext', '-layout', str(root / '_output/cv-master.pdf'), '-'], text=True)
    chars, offsets = [], []
    for index, char in enumerate(text):
        for normal in unicodedata.normalize('NFKC', char):
            if not normal.isspace() and normal != '\u00ad':
                chars.append(normal)
                offsets.append(index)
    normalized = ''.join(chars)
    def normalize(value):
        return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value)).replace('\u00ad', '')
    rows = []
    for row in parser.rows:
        query = normalize(row['text'])
        start = normalized.find(query)
        assert start >= 0, ('Native PDF reference missing or differs', row['key'])
        end = start + len(query) - 1
        actual = ' '.join(text[offsets[start]:offsets[end] + 1].split())
        assert normalize(actual) == query
        rows.append({'key': row['key'], 'text': actual})
    (output / 'cv-pdf-text.txt').write_text(text)
(output / ('cv-' + mode + '.json')).write_text(json.dumps(rows, ensure_ascii=False))
