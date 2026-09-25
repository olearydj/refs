"""Run the real-input trial from a temporary copy with attachment locators neutralized."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

source = Path(__file__).resolve().parent
required = [source/'papers'/paper/'references.bib' for paper in (
    'pipyer-paper', '2026-jose-danvas', '2026-insight-dema-llm',
    'manufacturing-training-media-tradeoffs', 'dissertation',
)] + [source/'inputs'/name for name in ('attention.json', 'zotero-bbt-export.bib')]
missing = [str(path.relative_to(source)) for path in required if not path.is_file()]
if missing:
    print("Missing real-trial inputs: " + " ".join(missing) + "; these are the owner's files kept out of the repository.", file=sys.stderr)
    raise SystemExit(2)
root = Path(tempfile.mkdtemp(prefix='refs-trial-', dir='/private/tmp'))
if any(path.is_symlink() for path in source.rglob('*')):
    raise ValueError('Trial inputs must be copies, not symlinks')
shutil.copytree(source, root/'trial', ignore=shutil.ignore_patterns('out','__pycache__'))
for path in (root/'trial').rglob('*.bib'):
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if re.match(r'\s*file\s*=', line, re.I):
            if not re.search(r'[}"]\s*,?\s*$', line):
                raise RuntimeError('Multiline attachment field needs explicit remapping')
            lines[index] = '  file = {' + str(root/'unavailable'/f'attachment-{index}.pdf') + '},\n'
    path.write_text(''.join(lines))
protected = ['/Volumes/Casa/refs', str(Path.home()/'.config/refs'), str(Path.home()/'Box Sync'), str(Path.home()/'Zotero')]
profile = '(version 1) (allow default) (deny file-read* file-write* ' + ' '.join('(subpath '+json.dumps(p)+')' for p in protected) + ')'
with (root/'run.log').open('w') as log:
    result = subprocess.run((['sandbox-exec', '-p', profile] if shutil.which('sandbox-exec') else []) + [str(root/'trial/run.sh')], stdout=log, stderr=subprocess.STDOUT, env=dict(os.environ, REFS_TRIAL_ISOLATED='1', REFS_TRIAL_REPO=str(source.parents[2])))
print(root/'run.log', flush=True)
print((root/'run.log').read_text()[-2200:], flush=True)
raise SystemExit(result.returncode)
