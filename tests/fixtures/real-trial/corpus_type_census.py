"""Count unsupported input types in a recorded corpus manifest without importing them."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import get_args

from refs.adapters.bibtex import partition
from refs.models import REGISTRY, Metadata

BIB_TYPES = set(REGISTRY['bib_type_aliases'])
CSL_TYPES = set(get_args(Metadata.model_fields['type'].annotation))
ZOTERO_TYPES = {row['zotero'] for row in REGISTRY['type_mappings']}
ENTRY = re.compile(br'^@\s*([^\s{(]+)\s*[{(]\s*([^,\s]*)', re.I)


def census(manifest: Path) -> dict:
    counts: Counter[tuple[str, str]] = Counter()
    examples: dict[tuple[str, str], str] = {}
    files = json.loads(manifest.read_text())['files']
    for file in files:
        path = Path(file['path'])
        route = file.get('route') or ('bib' if path.suffix.lower() == '.bib' else None)
        if route == 'bib':
            for block in partition(path.read_bytes()):
                if block['kind'] != 'entry' or not (match := ENTRY.match(block['raw'])):
                    continue
                kind = match[1].decode(errors='replace').lower()
                if kind in BIB_TYPES:
                    continue
                key = match[2].decode(errors='replace') or '<empty key>'
                counts[(route, kind)] += 1
                examples.setdefault((route, kind), f'{path.name}: {key}')
        elif route == 'csl':
            for index, item in enumerate(json.loads(path.read_bytes())):
                kind = item.get('type') if isinstance(item, dict) else None
                if not isinstance(kind, str) or kind in CSL_TYPES:
                    continue
                counts[(route, kind)] += 1
                examples.setdefault((route, kind), f"{path.name}: {item.get('id') or f'index {index}'}")
        elif route == 'zotero':
            for index, item in enumerate(json.loads(path.read_bytes())['items']):
                kind = item.get('itemType')
                if not isinstance(kind, str) or kind in ZOTERO_TYPES or not (item.get('notes') or item.get('attachments')):
                    continue
                counts[(route, kind)] += 1
                examples.setdefault((route, kind), f"{path.name}: {item.get('key') or item.get('title') or f'index {index}'}")
    return {'files':len(files), 'rows':[dict(route=route, type=kind, count=count, example=examples[(route, kind)]) for (route, kind), count in sorted(counts.items())]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    print(json.dumps(census(args.manifest), ensure_ascii=False, indent=2))
