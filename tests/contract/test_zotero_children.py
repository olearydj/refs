import json

from test_zotero_mapping import extracted

from refs.catalog import connect


def test_children_are_linked_without_touching_files(initialized, zotero_fixture, tmp_path):
    folder = tmp_path / "input"
    extracted(zotero_fixture, folder)
    before = {p: p.read_bytes() for p in zotero_fixture.parent.rglob("*.pdf")}
    result = initialized("import", "--format", "zotero", "--input", folder)["data"]
    record = initialized("show", "native1")["data"]
    assert len(record["resources"]) == 3
    paths = {r["path"] for r in record["resources"]}
    assert str(zotero_fixture.parent / "storage/FILE0012/stored.pdf") in paths
    assert str(zotero_fixture.parent / "base/relative.pdf") in paths
    assert {item["text"] for item in record["context"]} == {
        "Synthetic child note",
        "https://example.org/attachment",
    }
    assert all(item["origin"] == "import" for item in record["context"])
    assert result["preservation"] == dict(
        trash=1, annotations=1, attachment_outlines=1, standalone_children=0
    )
    again = initialized("import", "--format", "zotero", "--input", folder)["data"]
    assert again["counts"]["unchanged"] == 6
    assert initialized("show", "native1")["data"]["revision"] == record["revision"]
    with connect(tmp_path / "cat") as c:
        assert c.execute("SELECT count(*) FROM collections").fetchone()[0] == 3
        assert c.execute("SELECT count(*) FROM source_collections").fetchone()[0] == 3
        assert c.execute("SELECT count(*) FROM resources").fetchone()[0] == 3
        relation = c.execute("SELECT * FROM source_relations").fetchone()
        assert relation["target_id"] and relation["target_uri"] == "users/123/items/ITEM0002"
    assert all(p.read_bytes() == raw for p, raw in before.items())


def test_missing_base_file_and_unresolved_relation(initialized, zotero_fixture, tmp_path):
    folder = tmp_path / "input"
    extracted(zotero_fixture, folder)
    p = folder / "manifest.json"
    value = json.loads(p.read_bytes())
    value["base_path"] = None
    p.write_text(json.dumps(value))
    (zotero_fixture.parent / "linked.pdf").unlink()
    p = folder / "items/ITEM0001.json"
    value = json.loads(p.read_bytes())
    value["data"]["relations"] = {"dc:relation": ["http://zotero.org/users/123/items/ABSENT00"]}
    p.write_text(json.dumps(value))
    result = initialized("import", "--format", "zotero", "--input", folder)["data"]
    codes = {w["code"] for entry in result["entries"] for w in entry.get("warnings", [])}
    assert {"attachment_base_missing", "attachment_missing"} <= codes
    with connect(tmp_path / "cat") as c:
        assert c.execute("SELECT target_id FROM source_relations").fetchone()[0] is None
