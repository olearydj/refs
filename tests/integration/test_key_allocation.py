import json
import sqlite3
import subprocess
import sys
from contextlib import closing

from conftest import isolated_env


def test_two_process_key_allocation(initialized, tmp_path):
    env = isolated_env(tmp_path)
    wrapper = """import runpy, sys
from refs import catalog
original = catalog.connect
def announced(*args, **kwargs):
    if kwargs.get('write'):
        print('WRITE_ATTEMPT', file=sys.stderr, flush=True)
    return original(*args, **kwargs)
catalog.connect = announced
sys.argv = ['refs', '--json', '--no-project-config', *sys.argv[1:]]
runpy.run_module('refs', run_name='__main__')
"""
    children = []
    with closing(sqlite3.connect(tmp_path/'cat/catalog.sqlite')) as connection:
        connection.execute('BEGIN IMMEDIATE')
        try:
            for last_word in ['Alpha', 'Beta']:
                path = tmp_path / f'{last_word}.json'
                path.write_text(json.dumps({'schema_version': '1.0', 'metadata': {'type': 'book', 'title': f'Synthetic Study {last_word}', 'language': 'en', 'author': [{'family': 'Smith'}], 'issued': {'date-parts': [[2024]]}}}))
                children.append(subprocess.Popen([sys.executable, '-c', wrapper, 'add', '--format', 'refs', '--input', str(path)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
            assert [process.stderr.readline().strip() for process in children] == ['WRITE_ATTEMPT', 'WRITE_ATTEMPT']
            assert all(process.poll() is None for process in children)
        finally:
            connection.rollback()
    keys = []
    for process in children:
        out, err = process.communicate(timeout=20)
        assert process.returncode == 0 and not err, (out, err)
        keys.append(json.loads(out)['data']['citation_key'])
    assert set(keys) == {'smith-2024-syntheticStudy', 'smith-2024-syntheticStudy-a'}
