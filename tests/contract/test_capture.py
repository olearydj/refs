import hashlib
import json
import sqlite3
from contextlib import closing

import pytest


def test_capture_original_and_show(initialized, tmp_path, reference_path):
    data = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    shown = initialized("show", data["citation_key"])["data"]
    assert initialized("show", data["id"])["data"] == shown
    assert shown["metadata"] == json.loads(reference_path.read_text())["metadata"]
    assert shown["revision"] == 1
    assert shown["state"] == "active"
    assert shown["provenance"][0]["source_identity"]["item_key"] == "article-1"
    assert shown["corrected_fields"] == []
    assert shown["originals"][0]["sha256"] == hashlib.sha256(reference_path.read_bytes()).hexdigest()
    with closing(sqlite3.connect(tmp_path / "cat" / "catalog.sqlite")) as connection, connection:
        assert connection.execute("SELECT raw_bytes FROM originals").fetchone()[0] == reference_path.read_bytes()
        assert connection.execute("SELECT source_id FROM origin_identities").fetchone()[0] == data["id"]


def test_preview_does_not_change_catalog(initialized, tmp_path, reference_path):
    catalog = tmp_path / "cat"
    before = {p.name: p.read_bytes() for p in catalog.iterdir() if p.is_file() and p.name != 'refs.log'}
    result = initialized("add", "--format", "refs", "--input", reference_path, "--dry-run")
    assert result["data"]["dry_run"]
    assert {p.name: p.read_bytes() for p in catalog.iterdir() if p.is_file() and p.name != 'refs.log'} == before
    assert list((catalog / 'staging').iterdir()) == []
    assert [json.loads(line)['event'] for line in (catalog/'refs.log').read_text().splitlines()[-2:]] == ['command.open','command.close']


def test_repeat_is_noop_and_conflict_never_overwrites(initialized, tmp_path, reference_path):
    first = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    before = (tmp_path / "cat" / "catalog.sqlite").read_bytes()
    again = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    assert again["id"] == first["id"]
    assert (tmp_path / "cat" / "catalog.sqlite").read_bytes() == before
    incoming = json.loads(reference_path.read_text())
    incoming["metadata"]["title"] = "Different Work"
    incoming["citation_key"] = "different-2024-work"
    conflict = tmp_path / "conflict.json"
    conflict.write_text(json.dumps(incoming))
    result = initialized("add", "--format", "refs", "--input", conflict, expected=3)
    assert result["errors"][0]["code"] == "identity_conflict"
    shown = initialized("show", first["id"])["data"]
    assert shown["metadata"] == first["metadata"]
    assert any(item["origin"] == "import-capture" for item in shown["originals"])


@pytest.mark.parametrize("edit", [
    {"surprise": True},
    {"citation_key": "bad key"},
    {"metadata": {"type": "unknown-type", "title": "Unsupported Type"}},
    {"metadata": {"type": "article-journal", "title": "Test", "volume": True}},
    {"provenance": [{"origin": "agent", "access": "metadata", "identity": {}}]},
])
def test_unsupported_input_is_explicit(initialized, tmp_path, reference_path, edit):
    value = json.loads(reference_path.read_text())
    value.update(edit)
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(value))
    before = (tmp_path / "cat" / "catalog.sqlite").read_bytes()
    result = initialized("add", "--format", "refs", "--input", path, expected=2)
    assert result["errors"][0]["code"] == "invalid_record"
    assert (tmp_path / "cat" / "catalog.sqlite").read_bytes() == before


def test_partial_origin_is_preserved_without_binding(initialized, tmp_path, reference_path):
    value = json.loads(reference_path.read_text())
    value["provenance"][0]["source_identity"] = {"namespace": "synthetic"}
    value["context"][0]["original_ref"] = "upstream-note-7"
    value["provenance"][0]["original_ref"] = "upstream-entry-1"
    path = tmp_path / "partial.json"
    path.write_text(json.dumps(value))
    result = initialized("add", "--format", "refs", "--input", path)["data"]
    assert result["provenance"][0]["source_identity"] == {"namespace": "synthetic"}
    assert result["context"][0]["original_ref"] == "upstream-note-7"
    with closing(sqlite3.connect(tmp_path / "cat" / "catalog.sqlite")) as connection, connection:
        assert connection.execute("SELECT count(*) FROM origin_identities").fetchone()[0] == 0


@pytest.mark.parametrize('mode', ['link', 'copy', 'move'])
@pytest.mark.parametrize('label', [None, 'scan'])
def test_add_file_label_is_stored(initialized, tmp_path, reference_path, mode, label):
    path = tmp_path / 'scan.pdf'
    path.write_bytes(b'%PDF captured source')
    args = ['--label', label] if label else []
    added = initialized('add', '--format', 'refs', '--input', reference_path,
                        '--file', path, '--' + mode, *args)['data']
    resource = initialized('show', added['id'])['data']['resources'][0]
    assert resource['label'] == label
    assert added['resources'][0]['label'] == label
    if mode == 'link':
        assert resource['path'] == str(path)
        assert path.read_bytes() == b'%PDF captured source'


def test_add_label_without_file_refuses_before_capture(initialized, tmp_path, reference_path):
    before = (tmp_path / 'cat/catalog.sqlite').read_bytes()
    result = initialized('add', '--format', 'refs', '--input', reference_path, '--label', 'scan', expected=2)
    assert result['errors'][0]['code'] == 'invalid_invocation'
    assert (tmp_path / 'cat/catalog.sqlite').read_bytes() == before


@pytest.mark.parametrize('apostrophe', ["'", '’', 'ʼ'])
def test_generated_title_tokens_do_not_remove_stored_or_exported_apostrophes(initialized, tmp_path, apostrophe):
    title = f'Developer{apostrophe}s Playbook'
    metadata = {'type': 'book', 'title': title, 'title-short': title,
                'author': [{'family': 'Wilson'}], 'issued': {'date-parts': [[2024]]}}
    context = [{'origin': 'user', 'text': f'Owner{apostrophe}s Copy'}]
    payload = tmp_path / 'apostrophe.json'
    payload.write_text(json.dumps({'schema_version': '1.0', 'metadata': metadata, 'context': context}))
    added = initialized('add', '--format', 'refs', '--input', payload)['data']
    assert added['citation_key'] == 'wilson-2024-developersPlaybook'
    shown = initialized('show', added['id'])['data']
    assert shown['metadata'] == metadata
    assert shown['context'] == context
    initialized('project', 'create', 'apostrophe')
    initialized('project', 'cite', 'apostrophe', added['id'])
    for profile in ('csl-json-v1', 'portable-bibtex-v1', 'biblatex-v1'):
        output = tmp_path / (profile + '.txt')
        initialized('export', '--project', 'apostrophe', '--profile', profile, '--output', output)
        if profile == 'csl-json-v1':
            assert json.loads(output.read_text())[0]['title'] == title
        else:
            assert 'title = {' + title + '}' in output.read_text()
    after = initialized('show', added['id'])['data']
    assert after['metadata'] == metadata
    assert after['context'] == context
