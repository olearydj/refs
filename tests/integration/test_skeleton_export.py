import hashlib
import json
import sqlite3
from contextlib import closing

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
        with closing(sqlite3.connect(catalog / "catalog.sqlite")) as connection, connection:
            connection.execute("UPDATE sources SET metadata_json=json_set(metadata_json, '$.volume', '13')")
    original = bibliography.finish_export

    def interrupted(*args):
        raise OSError("Synthetic interruption after publication")

    monkeypatch.setattr(bibliography, "finish_export", interrupted)
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, "demo", output)
    assert error.value.exit_code == 4
    published = output.read_bytes()
    with closing(sqlite3.connect(catalog / "catalog.sqlite")) as connection, connection:
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
    with closing(sqlite3.connect(catalog / "catalog.sqlite")) as connection, connection:
        assert connection.execute("SELECT baseline_digest, pending_digest FROM export_targets").fetchone() == (hashlib.sha256(published).hexdigest(), None)


def test_failure_before_publication_preserves_baseline(cited, monkeypatch):
    catalog, output = cited
    bibliography.export(catalog, "demo", output)
    before = output.read_bytes()
    with closing(sqlite3.connect(catalog / "catalog.sqlite")) as connection, connection:
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
    assert b'volume = {13}' in output.read_bytes()
    assert b'volume = {13}' not in before


def test_post_publication_digest_failure_reports_recoverable_output(cited, monkeypatch):
    catalog, output = cited
    published = False
    publish = files.publish
    current_digest = files.current_digest

    def mark_publication(*args):
        nonlocal published
        publish(*args)
        published = True

    def changed_digest(path):
        return '0' * 64 if published and path == output else current_digest(path)

    monkeypatch.setattr(files, 'publish', mark_publication)
    monkeypatch.setattr(files, 'current_digest', changed_digest)
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, 'demo', output)
    assert error.value.issue['code'] == 'export_published_unrecorded'
    assert error.value.exit_code == 4
    assert output.is_file() and current_digest(output) != '0' * 64
    with closing(sqlite3.connect(catalog / 'catalog.sqlite')) as connection:
        assert connection.execute('SELECT pending_digest FROM export_targets').fetchone()[0] == current_digest(output)


def test_unknown_stored_field_blocks_before_staging(cited):
    catalog, output = cited
    with closing(sqlite3.connect(catalog / "catalog.sqlite")) as connection, connection:
        connection.execute("UPDATE sources SET metadata_json=json_set(metadata_json, '$.unexpected', 'retained')")
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, "demo", output)
    assert error.value.issue["code"] == "export_blocked"
    assert not output.exists()
    assert not list(output.parent.glob(".refs-*.tmp"))
    with closing(sqlite3.connect(catalog / "catalog.sqlite")) as connection, connection:
        assert connection.execute("SELECT count(*) FROM export_targets").fetchone()[0] == 0


def test_changed_binding_and_symlink_are_rejected(initialized, cited):
    catalog, output = cited
    bibliography.export(catalog, "demo", output)
    initialized("project", "create", "other")
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, "other", output)
    assert error.value.issue['code'] == 'target_binding_conflict'
    before = output.read_bytes()
    link = output.parent / "symlink.bib"
    link.symlink_to(output)
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, "demo", link)
    assert error.value.issue['code'] == 'unsafe_target'
    assert output.read_bytes() == before


def test_protection_and_tex_are_not_executable(cited):
    catalog, output = cited
    with closing(sqlite3.connect(catalog / "catalog.sqlite")) as connection, connection:
        metadata = json.loads(connection.execute("SELECT metadata_json FROM sources").fetchone()[0])
        metadata["title"] = r"Python & Pythonic: \input{unsafe}"
        metadata["author"] = [{"literal": "Research and Development"}]
        connection.execute("UPDATE sources SET metadata_json=?", (json.dumps(metadata),))
    bibliography.export(catalog, "demo", output)
    text = output.read_text()
    assert "{Python} \\& Pythonic" in text
    assert r"\textbackslash{}input\{unsafe\}" in text
    assert "author = {{Research and Development}}" in text


def test_explicit_overwrite_preserves_outside_bytes_and_cannot_adopt(initialized, cited):
    catalog, output = cited
    bibliography.export(catalog, 'demo', output)
    outside = b'% Synthetic outside edit\n'
    output.write_bytes(outside)
    initialized('export', '--project', 'demo', '--output', output, '--overwrite')
    assert output.read_bytes().startswith(b'@article{smith-2024-learningPython,')
    assert b'journal = {Journal' in output.read_bytes()
    with closing(sqlite3.connect(catalog/'catalog.sqlite')) as connection, connection:
        assert connection.execute("SELECT raw_bytes FROM originals WHERE origin='export-overwrite'").fetchone()[0] == outside
    unrelated = output.parent/'unowned.bib'
    unrelated.write_bytes(outside)
    initialized('export', '--project', 'demo', '--output', unrelated, '--overwrite', expected=3)
    assert unrelated.read_bytes() == outside
