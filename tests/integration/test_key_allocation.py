import json
import subprocess
from pathlib import Path

from conftest import isolated_env


def test_two_process_key_allocation(initialized, tmp_path):
    env = isolated_env(tmp_path)
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
