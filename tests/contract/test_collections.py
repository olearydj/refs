import json

from test_zotero_mapping import extracted

from refs import sources
from refs.catalog import connect


def test_hierarchy_counts_filters_and_no_writes(initialized, zotero_fixture, tmp_path):
    directory = tmp_path / "input"
    extracted(zotero_fixture, directory)
    path = directory / "collections.json"
    value = json.loads(path.read_bytes())
    value[0]["data"]["name"] = "Résearch"
    path.write_text(json.dumps(value))
    initialized("import", "--format", "zotero", "--input", directory)
    initialized("project", "create", "paper")
    initialized("project", "cite", "paper", "extra2")
    before = (tmp_path / "cat/catalog.sqlite").read_bytes()
    listed = initialized("collection", "list")["data"]
    assert {r["path"]: r["count"] for r in listed["items"]} == {
        "Résearch": 1,
        "Résearch/Methods": 2,
        "Empty": 0,
    }
    rows = initialized(
        "list", "--collection", "Résearch/Methods", "--sort", "key", "--limit", 1, "--offset", 1
    )["data"]
    assert rows["total"] == 2 and rows["items"][0]["citation_key"] == "native1"
    rows = initialized(
        "search", "Synthetic", "--collection", "Résearch/Methods", "--project", "paper"
    )["data"]
    assert rows["total"] == 1 and rows["items"][0]["citation_key"] == "extra2"
    assert rows["items"][0]["matches"]
    assert initialized("list", "--collection", "Empty")["data"]["total"] == 0
    assert (tmp_path / "cat/catalog.sqlite").read_bytes() == before
    record = sources.show(tmp_path / "cat", "extra2")
    sources.change_identity(
        tmp_path / "cat", "extra2", record["revision"], state="removed", execute=True
    )
    assert initialized("list", "--collection", "Résearch/Methods")["data"]["total"] == 1
    assert (
        next(
            r
            for r in initialized("collection", "list")["data"]["items"]
            if r["path"] == "Résearch/Methods"
        )["count"]
        == 1
    )


def test_ambiguous_and_missing_paths(initialized, tmp_path):
    with connect(tmp_path / "cat", write=True) as c:
        for i in range(2):
            c.execute(
                "INSERT INTO collections (id,library_uri,item_key,name,path) VALUES (?,?,?,?,?)",
                (str(i), "users/" + str(i), "COLL0001", "Same", "Same"),
            )
    assert (
        initialized("list", "--collection", "Same", expected=3)["errors"][0]["code"]
        == "collection_ambiguous"
    )
    assert (
        initialized("search", "word", "--collection", "absent", expected=3)["errors"][0]["code"]
        == "collection_missing"
    )
