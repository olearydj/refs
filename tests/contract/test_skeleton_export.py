import hashlib
import json
import sqlite3

import pytest

from refs import bibliography, files
from refs.results import RefError


@pytest.fixture
def cited(initialized, reference_path, tmp_path):
    source = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    initialized("project", "create", "demo")
    initialized("project", "cite", "demo", source["id"])
    return tmp_path / "cat", tmp_path / "references.bib"


def test_preview_and_outside_edit(initialized, cited):
    catalog, output = cited
    before = (catalog / "catalog.sqlite").read_bytes()
    initialized("export", "--project", "demo", "--output", output, "--dry-run")
    assert not output.exists()
    assert (catalog / "catalog.sqlite").read_bytes() == before
    initialized("export", "--project", "demo", "--output", output)
    output.write_text("External changes\n")
    result = initialized("export", "--project", "demo", "--output", output, expected=3)
    assert result["errors"][0]["code"] == "outside_edit"
    assert output.read_text() == "External changes\n"


@pytest.mark.parametrize("prior_export", [False, True])
def test_interrupted_publication_recovers(cited, monkeypatch, prior_export):
    catalog, output = cited
    if prior_export:
        bibliography.export(catalog, "demo", output)
        # Synthetic edit makes a different candidate without implementing update.
        with sqlite3.connect(catalog / "catalog.sqlite") as connection:
            connection.execute("UPDATE sources SET metadata_json=json_set(metadata_json, '$.volume', '13')")
    original = bibliography.finish_export

    def interrupted(*args):
        raise OSError("Synthetic interruption after publication")

    monkeypatch.setattr(bibliography, "finish_export", interrupted)
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, "demo", output)
    assert error.value.exit_code == 4
    published = output.read_bytes()
    with sqlite3.connect(catalog / "catalog.sqlite") as connection:
        baseline, pending = connection.execute("SELECT baseline_digest, pending_digest FROM export_targets").fetchone()
        assert pending == hashlib.sha256(published).hexdigest()
        assert baseline != pending
    before = (catalog / "catalog.sqlite").read_bytes()
    assert bibliography.export(catalog, "demo", output, dry_run=True)["recoverable"]
    assert (catalog / "catalog.sqlite").read_bytes() == before
    monkeypatch.setattr(bibliography, "finish_export", original)
    result = bibliography.export(catalog, "demo", output)
    assert result["recovered"]
    assert output.read_bytes() == published
    with sqlite3.connect(catalog / "catalog.sqlite") as connection:
        assert connection.execute("SELECT baseline_digest, pending_digest FROM export_targets").fetchone() == (hashlib.sha256(published).hexdigest(), None)


def test_failure_before_publication_preserves_baseline(cited, monkeypatch):
    catalog, output = cited
    bibliography.export(catalog, "demo", output)
    before = output.read_bytes()
    with sqlite3.connect(catalog / "catalog.sqlite") as connection:
        connection.execute("UPDATE sources SET metadata_json=json_set(metadata_json, '$.volume', '13')")
    real_publish = files.publish

    def failed(*args):
        raise OSError("Synthetic publication failure")

    monkeypatch.setattr(files, "publish", failed)
    with pytest.raises(OSError):
        bibliography.export(catalog, "demo", output)
    assert output.read_bytes() == before
    assert not list(output.parent.glob(".refs-*.tmp"))
    monkeypatch.setattr(files, "publish", real_publish)
    bibliography.export(catalog, "demo", output)
    assert output.read_bytes() != before


def test_unknown_stored_field_blocks_before_staging(cited):
    catalog, output = cited
    with sqlite3.connect(catalog / "catalog.sqlite") as connection:
        connection.execute("UPDATE sources SET metadata_json=json_set(metadata_json, '$.unexpected', 'retained')")
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, "demo", output)
    assert error.value.issue["code"] == "export_blocked"
    assert not output.exists()
    assert not list(output.parent.glob(".refs-*.tmp"))
    with sqlite3.connect(catalog / "catalog.sqlite") as connection:
        assert connection.execute("SELECT count(*) FROM export_targets").fetchone()[0] == 0


def test_changed_binding_and_symlink_are_rejected(initialized, cited):
    catalog, output = cited
    bibliography.export(catalog, "demo", output)
    initialized("project", "create", "other")
    with pytest.raises(RefError):
        bibliography.export(catalog, "other", output)
    link = output.parent / "symlink.bib"
    link.symlink_to(output)
    with pytest.raises(RefError):
        bibliography.export(catalog, "demo", link)


def test_protection_and_tex_are_not_executable(cited):
    catalog, output = cited
    with sqlite3.connect(catalog / "catalog.sqlite") as connection:
        metadata = json.loads(connection.execute("SELECT metadata_json FROM sources").fetchone()[0])
        metadata["title"] = r"Python & Pythonic: \input{unsafe}"
        metadata["author"] = [{"literal": "Research and Development"}]
        connection.execute("UPDATE sources SET metadata_json=?", (json.dumps(metadata),))
    bibliography.export(catalog, "demo", output)
    text = output.read_text()
    assert "{Python} \\& Pythonic" in text
    assert r"\textbackslash{}input\{unsafe\}" in text
    assert "author = {{Research and Development}}" in text
