import json
import os
import subprocess
from pathlib import Path


def test_two_process_key_allocation(initialized, tmp_path):
    env = dict(os.environ, REFS_CONFIG=str(tmp_path/'config.toml'), REFS_CATALOG=str(tmp_path/'cat'))
    children = []
    for last_word in ['Alpha', 'Beta']:
        path = tmp_path / f'{last_word}.json'
        path.write_text(json.dumps({'schema_version': '1.0', 'metadata': {'type': 'book', 'title': f'Synthetic Study {last_word}', 'language': 'en', 'author': [{'family': 'Smith'}], 'issued': {'date-parts': [[2024]]}}}))
        children.append(subprocess.Popen([str(Path('.venv/bin/refs').resolve()), '--json', 'add', '--format', 'refs', '--input', str(path)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
    keys = []
    for process in children:
        out, err = process.communicate(timeout=20)
        assert process.returncode == 0, (out, err)
        keys.append(json.loads(out)['data']['citation_key'])
    assert set(keys) == {'smith-2024-syntheticStudy', 'smith-2024-syntheticStudy-a'}
