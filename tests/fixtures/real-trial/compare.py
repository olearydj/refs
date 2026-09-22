"""Assert per-entry Pandoc equality or a specifically reported change."""
import json
import subprocess
import sys
from pathlib import Path

folder = Path(sys.argv[1])



def normalized(node):
    """Compare visible plain text, not harmless Pandoc span/token boundaries."""
    import unicodedata
    def text(value):
        if isinstance(value, list):
            return ''.join(text(item) for item in value)
        if not isinstance(value, dict):
            return ''
        kind, contents = value.get('t'), value.get('c')
        if kind == 'Str':
            return contents
        if kind in ('Space', 'SoftBreak', 'LineBreak'):
            return ' '
        if kind == 'Span':
            return text(contents[1])
        if kind == 'Link':
            return text(contents[1])
        if kind == 'Quoted':
            return '“' + text(contents[1]) + '”'
        return text(contents)
    return unicodedata.normalize('NFC', ' '.join(text(node).split()))


def references(name):
    result = subprocess.run(['pandoc', '--citeproc', '--bibliography', str(folder/f'{name}.bib'), '-t', 'json'], input='---\nnocite: "@*"\n---\n', text=True, capture_output=True, check=True)
    document = json.loads(result.stdout)
    entries = {}
    def visit(node):
        if isinstance(node, dict):
            if node.get('t') == 'Div' and node['c'][0][0].startswith('ref-'):
                entries[node['c'][0][0][4:]] = normalized(node['c'][1])
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
    visit(document)
    return entries


original, exported = references('original'), references('exported')
report = json.loads((folder/'export.json').read_text())
warnings = {}
for item in report['warnings'] + report['data'].get('info', []):
    warnings.setdefault(item['details']['citation_key'], []).append(item)
differences = []
for key in sorted(original.keys() | exported.keys()):
    if original.get(key) != exported.get(key):
        notices = warnings.get(key, [])
        differences.append({'citation_key': key, 'reported_changes': notices,
                            'original': original.get(key), 'exported': exported.get(key)})
(folder/'render-differences.json').write_text(json.dumps(differences, ensure_ascii=False, indent=2)+'\n')
unexplained = [item['citation_key'] for item in differences if not item['reported_changes'] or item['original'] is None or item['exported'] is None]
print(f"  Pandoc entries: {len(original)} original, {len(exported)} exported; {len(differences)} changed; {len(unexplained)} without a report")
assert not unexplained, f'Unreported rendering differences: {unexplained}'
