"""Deterministic consumer of a real refs export for the conversion gate tests."""
import json
from pathlib import Path

records = json.loads(Path('references.json').read_text())
Path('rendered.json').write_text(json.dumps({'sources': [
    {'id': r['id'], 'title': r['title']} for r in records
]}))
