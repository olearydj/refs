"""Cross-boundary guards from investigation lines 69-73."""

import hashlib
import json
import subprocess
import sys
import time

import pytest

from refs import moves, resources, sources
from refs.catalog import connect
from refs.config import select
from refs.results import RefError


def test_remove_managed_cited_source_preserves_file_and_export(initialized, tmp_path, reference_path):
    original = tmp_path / "download.pdf"
    original.write_bytes(b"synthetic paper bytes")
    source = initialized("add", "--format", "refs", "--input", reference_path, "--file", original, "--copy")["data"]
    initialized("project", "create", "paper")
    initialized("project", "cite", "paper", source["id"])
    bibliography = tmp_path / "paper.bib"
    initialized("export", "--project", "paper", "--output", bibliography)
    before_bib = bibliography.read_bytes()
    managed = tmp_path / "lib" / source["resources"][0]["relative"]
    before_file = managed.read_bytes()
    revision = initialized("show", source["id"])["data"]["revision"]
    initialized("remove", source["id"], "--if-revision", revision, "--execute")
    assert managed.read_bytes() == before_file
    assert bibliography.read_bytes() == before_bib
    assert initialized("show", source["id"])["data"]["state"] == "removed"
    initialized("reactivate", source["id"], "--execute")
    assert initialized("show", source["id"])["data"]["state"] == "active"
    assert initialized("export", "--project", "paper", "--output", bibliography)["data"]["count"] == 1
    assert bibliography.read_bytes() == before_bib


def test_foreign_destination_after_publication_cannot_be_adopted(initialized, tmp_path, reference_path, monkeypatch):
    source = initialized("add", "--format", "refs", "--input", reference_path, "--loc", "Topic")["data"]
    original = tmp_path / "download.pdf"
    original.write_bytes(b"original PDF")
    settings = select(str(tmp_path / "config.toml"), str(tmp_path / "cat"), no_project_config=True)
    resource = resources.link(settings, source["id"], path=original)
    target = tmp_path / "lib/Topic/download.pdf"

    def interrupt(point, row):
        if point == "published":
            raise KeyboardInterrupt

    monkeypatch.setattr(moves, "checkpoint", interrupt)
    with pytest.raises(KeyboardInterrupt):
        moves.move(settings, resource["id"], target)
    original_target = target.stat()
    target.unlink()
    target.write_bytes(b"foreign PDF")
    assert target.stat().st_ino != original_target.st_ino
    monkeypatch.setattr(moves, "checkpoint", lambda *args: None)
    with pytest.raises(RefError) as caught:
        moves.move(settings, resource["id"], target)
    assert caught.value.issue["code"] == "move_incomplete"
    assert "Published file changed" in caught.value.issue["details"]["cause"]
    assert original.read_bytes() == b"original PDF"
    assert target.read_bytes() == b"foreign PDF"
    assert sources.show(settings.catalog_path(), source["id"])["resources"][0]["path"] == str(original)
    with connect(settings.catalog_path()) as connection:
        assert tuple(connection.execute("SELECT state,last_state FROM file_operations").fetchone()) == ("failed", "published")


def test_two_process_file_lock_times_out_after_five_seconds(initialized, tmp_path):
    catalog = tmp_path / "cat"
    holder_code = """import sys,time
from pathlib import Path
from refs.files import file_lock
with file_lock(Path(sys.argv[1])):
 print('locked',flush=True)
 time.sleep(8)
"""
    contender_code = """import sys
from pathlib import Path
from refs.files import file_lock
from refs.results import RefError
try:
 with file_lock(Path(sys.argv[1])): pass
except RefError as error:
 print(error.issue['code'],flush=True)
 raise SystemExit(error.exit_code)
"""
    holder = subprocess.Popen([sys.executable, "-c", holder_code, str(catalog)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "locked"
        started = time.monotonic()
        contender = subprocess.run([sys.executable, "-c", contender_code, str(catalog)], capture_output=True, text=True, timeout=9)
        elapsed = time.monotonic() - started
        assert contender.returncode == 6, contender.stderr
        assert contender.stdout.strip() == "lock_timeout"
        assert 5 <= elapsed < 8
        assert (catalog / "files.lock").is_file()
    finally:
        holder.terminate()
        holder.communicate(timeout=3)


def test_remove_preview_leaves_catalog_bytes_unchanged(initialized, tmp_path, reference_path):
    source = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    catalog_file = tmp_path / "cat/catalog.sqlite"
    before = catalog_file.read_bytes()
    preview = initialized("remove", source["id"], "--if-revision", source["revision"])["data"]
    assert preview["dry_run"] is True
    assert catalog_file.read_bytes() == before
    with connect(tmp_path / "cat") as connection:
        assert connection.execute("SELECT state FROM sources WHERE id=?", (source["id"],)).fetchone()[0] == "active"


def test_title_edit_drops_stale_protection_once(initialized, reference_path):
    source = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    result = initialized("update", source["id"], "--if-revision", source["revision"], "--set", 'metadata.title="Learning Rust"')
    assert result["data"]["title_protection"]["title"]["protected_terms"] == []
    notices = [item for item in result["warnings"] if item["code"] == "protected_terms_dropped"]
    assert len(notices) == 1
    assert notices[0]["details"]["terms"] == [{"field": "title", "term": "Python"}]
    assert not [item for item in result["warnings"] if item["code"] == "protected_term_missing"]
    assert initialized("show", source["id"])["data"]["title_protection"]["title"]["protected_terms"] == []


def test_init_help_cautions_about_synchronized_catalog(tmp_path):
    result = subprocess.run([sys.executable, "-m", "refs", "init", "--help"], cwd=tmp_path, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "outside folders synchronized by a file-copy service" in " ".join(result.stdout.split())


@pytest.mark.parametrize(("loss_code", "patch"), [
    ("issued_date_lost_or_changed", {'metadata.issued': {'date-parts': [[2024]], 'circa': True}}),
    ("work_identity_changed", {'metadata.type': 'article', 'metadata.archive': 'arXiv', 'metadata.number': '2407.01502', 'extensions.identifiers.arxiv': '2407.01503'}),
])
def test_real_export_loss_blocks_without_touching_target(initialized, tmp_path, reference_path, loss_code, patch):
    source = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    initialized("project", "create", "paper")
    initialized("project", "cite", "paper", source["id"])
    target = tmp_path / "paper.bib"
    initialized("export", "--project", "paper", "--output", target)
    before = target.read_bytes()
    with connect(tmp_path / "cat") as connection:
        baseline = connection.execute("SELECT baseline_digest, pending_digest FROM export_targets").fetchone()
        assert tuple(baseline) == (hashlib.sha256(before).hexdigest(), None)
    args = ["update", source["id"], "--if-revision", source["revision"]]
    for path, value in patch.items():
        args.extend(("--set", f"{path}={json.dumps(value)}"))
    initialized(*args)
    result = initialized("export", "--project", "paper", "--output", target, expected=3)
    assert result["errors"][0]["code"] == "export_blocked"
    assert any(item["code"] == loss_code for item in result["errors"][0]["details"]["entries"])
    assert target.read_bytes() == before
    assert not list(tmp_path.glob(".refs-*.tmp"))
    with connect(tmp_path / "cat") as connection:
        assert tuple(connection.execute("SELECT baseline_digest, pending_digest FROM export_targets").fetchone()) == tuple(baseline)
