"""Folder policy is captured on records; exporting needs no folder policy."""

import json
import subprocess
import sys

import pytest


@pytest.mark.parametrize('route', ['add', 'bib', 'csljson'])
def test_preserve_policy_carries_titles_through_policy_free_exports(initialized, tmp_path, cli_env, route):
    project = tmp_path / '.refs.toml'
    project.write_text('[titles]\npolicy = "preserve"\n')
    metadata = [
        {'type': 'article-journal', 'title': 'a sentence about AR', 'container-title': 'a journal of training'},
        {'type': 'article-journal', 'title': 'another sentence', 'container-title': 'another journal'},
    ]
    path = tmp_path / 'input'
    if route == 'add':
        path.write_text(json.dumps({'schema_version': '1.0', 'citation_key': 'one', 'metadata': metadata[0]}))
        args = ['add', '--format', 'refs']
    elif route == 'bib':
        path.write_text('@article{one,title={a sentence about AR},journal={a journal of training}}\n'
                        '@article{two,title={another sentence},journal={another journal}}')
        args = ['import', '--format', 'bib']
    else:
        path.write_text(json.dumps(metadata))
        args = ['import', '--format', 'csljson']
    result = subprocess.run([sys.executable, '-m', 'refs', '--json', '--project-file', str(project),
                             *args, '--input', str(path)], env=cli_env, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)['data']
    ids = [data['id']] if route == 'add' else [entry['source_id'] for entry in data['entries']]
    assert len(ids) == (1 if route == 'add' else 2)
    initialized('project', 'create', 'paper')
    for source_id, expected in zip(ids, metadata, strict=route != 'add'):
        stored = initialized('show', source_id)['data']
        for field in ('title', 'container-title'):
            assert stored['metadata'][field] == expected[field]
            assert stored['title_protection'][field] == {'protected_terms': [], 'preserve_case': True}
        initialized('project', 'cite', 'paper', source_id)
    # Delete the folder policy: both exporters must use the saved record alone.
    project.unlink()
    csl = tmp_path / 'export.json'
    bib = tmp_path / 'export.bib'
    initialized('export', '--project', 'paper', '--output', csl, '--profile', 'csl-json-v1')
    initialized('export', '--project', 'paper', '--output', bib, '--profile', 'portable-bibtex-v1')
    csl_records = json.loads(csl.read_text())
    assert len(csl_records) == len(ids)
    for expected in metadata[:len(ids)]:
        assert any(entry['title'] == '<span class="nocase">' + expected['title'] + '</span>'
                   and entry['container-title'] == '<span class="nocase">' + expected['container-title'] + '</span>'
                   for entry in csl_records)
        assert '  title = {{' + expected['title'] + '}},' in bib.read_text()
        assert '  journal = {{' + expected['container-title'] + '}},' in bib.read_text()
