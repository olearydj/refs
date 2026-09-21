"""The one installed end-to-end workflow, extended at later milestones."""

import sqlite3


def test_installed_smoke(cli, tmp_path, reference_path):
    cli("init", "--library-root", tmp_path / "lib")
    source = cli("add", "--format", "refs", "--input", reference_path)["data"]
    assert cli("show", source["citation_key"])["data"]["id"] == source["id"]
    project = cli("project", "create", "demo")["data"]
    cli("project", "cite", "demo", source["citation_key"])
    output = tmp_path / "references.bib"
    assert not output.exists()
    exported = cli("export", "--project", "demo", "--output", output)["data"]
    assert exported["count"] == 1
    expected = (
        b"@article{smith-2024-learningPython,\n"
        b"  author = {Smith, Alex},\n"
        b"  title = {Learning {Python}},\n"
        b"  journal = {Journal of Synthetic Examples},\n"
        b"  year = {2024},\n"
        b"  volume = {12},\n"
        b"  number = {2},\n"
        b"  pages = {10--20},\n"
        b"  doi = {10.5555/synthetic.2024.1},\n"
        b"}\n"
    )
    assert output.read_bytes() == expected
    cli("export", "--project", "demo", "--output", output)
    assert output.read_bytes() == expected
    unrelated = tmp_path / "unrelated.bib"
    unrelated.write_bytes(b"precious unrelated bibliography\n")
    cli("export", "--project", "demo", "--output", unrelated, expected=3)
    assert unrelated.read_bytes() == b"precious unrelated bibliography\n"
    with sqlite3.connect(tmp_path / "cat" / "catalog.sqlite") as connection:
        assert connection.execute("SELECT raw_bytes FROM originals").fetchone()[0] == reference_path.read_bytes()
        assert connection.execute("SELECT project_id, source_id, cited FROM project_sources").fetchone() == (project["id"], source["id"], 1)
        assert connection.execute("SELECT pending_digest FROM export_targets").fetchone() == (None,)
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert tables == {"catalog_meta", "sources", "originals", "origin_identities", "projects", "project_sources", "export_targets"}
