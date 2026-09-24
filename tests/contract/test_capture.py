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
    before = {p.name: p.read_bytes() for p in catalog.iterdir()}
    result = initialized("add", "--format", "refs", "--input", reference_path, "--dry-run")
    assert result["data"]["dry_run"]
    assert {p.name: p.read_bytes() for p in catalog.iterdir()} == before


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
