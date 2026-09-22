"""The Zotero gate has an independent source oracle and negative controls."""

import runpy
import sqlite3
from pathlib import Path

GATE = runpy.run_path(str(Path(__file__).parents[1] / "fixtures/real-trial/zotero_gate.py"))


def test_expected_fixture(zotero_fixture):
    uri, items, collections = GATE["expected"](
        zotero_fixture, zotero_fixture.parent / "base", {6: "legacy6"}
    )
    assert uri == "users/123"
    assert len(items) == 6 and collections == {"Research", "Research/Methods", "Empty"}
    assert items["ITEM0001"]["key"] == "native1"
    assert items["ITEM0006"]["key"] == "legacy6"
    assert len(items["ITEM0001"]["files"]) == 3
    assert len(items["ITEM0001"]["ids"]) == 6
    assert [name[0] for name in items["ITEM0001"]["names"]] == [
        "author",
        "editor",
        "translator",
        "contributor",
    ]
    assert len(items["ITEM0001"]["notes"]) == 1


def test_empty_catalog_gate(initialized, tmp_path, zotero_fixture):
    result = GATE["compare"](tmp_path / "cat", zotero_fixture, zotero_fixture.parent / "base")
    assert result["summary"]["missing_items"] == 6
    assert result["summary"]["findings"] == 7


def test_local_identity(zotero_fixture):
    with sqlite3.connect(zotero_fixture) as c:
        c.execute("UPDATE settings SET key='localUserKey',value='LOCAL123'")
    assert (
        GATE["expected"](zotero_fixture, zotero_fixture.parent / "base")[0]
        == "users/local/LOCAL123"
    )


def populated(initialized, tmp_path, zotero_fixture):
    import json

    from refs import sources

    uri, items, collections = GATE["expected"](zotero_fixture, zotero_fixture.parent / "base")
    with sqlite3.connect(tmp_path / "cat/catalog.sqlite") as c:
        c.execute("CREATE TABLE IF NOT EXISTS collections (id TEXT,library_uri TEXT,path TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS source_collections (source_id TEXT,collection_id TEXT)")
        c.executemany("INSERT INTO collections (id,library_uri,item_key,name,path) VALUES (?,?,?,?,?)", [(p, uri, p, p, p) for p in collections])
    for key, e in items.items():
        value = {
            "schema_version": "1.0",
            "citation_key": e["key"] or "generated",
            "metadata": {"title": key},
        }
        record = sources.add(tmp_path / "cat", json.dumps(value).encode(), "synthetic")
        names = {}
        for role, last, first, literal in e["names"]:
            names.setdefault(GATE["ROLES"][role], []).append(
                {"literal": last}
                if literal
                else {k: v for k, v in [("family", last), ("given", first)] if v}
            )
        metadata = (
            record["metadata"]
            | names
            | {k.upper(): v for k, v in e["ids"] if k not in ("arxiv", "oclc")}
        )
        details = {
            "native_type": {"namespace": "zotero", "value": e["native"]},
            "legacy_tags": list(e["tags"]),
            "context": [
                {"origin": "import", "text": "Synthetic child note"},
                *[{"origin": "import", "text": url} for url in e["urls"]],
            ],
            "extensions": {"identifiers": {k: v for k, v in e["ids"] if k in ("arxiv", "oclc")}},
        }
        with sqlite3.connect(tmp_path / "cat/catalog.sqlite") as c:
            c.execute(
                "UPDATE sources SET metadata_json=?,details_json=? WHERE id=?",
                (json.dumps(metadata), json.dumps(details), record["id"]),
            )
            c.execute(
                "INSERT INTO origin_identities VALUES (?,?,?,?,?)",
                ("zotero", uri, key, record["id"], "synthetic"),
            )
            c.executemany(
                "INSERT INTO source_collections VALUES (?,?)",
                [(record["id"], p) for p in e["collections"]],
            )
            for path in e["files"]:
                c.execute(
                    "INSERT INTO resources (id,source_id,locator,path) VALUES (?,?,?,?)",
                    (path, record["id"], path, path),
                )
    return tmp_path / "cat"


def test_gate_negative_controls(initialized, tmp_path, zotero_fixture):
    catalog = populated(initialized, tmp_path, zotero_fixture)

    def check():
        return GATE["compare"](catalog, zotero_fixture, zotero_fixture.parent / "base")

    assert check()["summary"]["findings"] == 0
    cases = [
        (
            "UPDATE origin_identities SET library_uri='users/999' WHERE item_key='ITEM0001'",
            "missing_item",
        ),
        ("DELETE FROM collections WHERE path='Empty'", "collection_inventory"),
        (
            "UPDATE resources SET path='/nonexistent/synthetic' WHERE path LIKE '%stored.pdf'",
            "files",
        ),
        (
            "UPDATE sources SET metadata_json=json_set(metadata_json,'$.author[0].family','Wrong') WHERE citation_key='native1'",
            "creators_author",
        ),
        (
            "UPDATE sources SET details_json=json_set(details_json,'$.context',json('[]')) WHERE citation_key='native1'",
            "child_note",
        ),
        (
            "UPDATE sources SET details_json=json_set(details_json,'$.extensions.identifiers.arxiv','wrong') WHERE citation_key='native1'",
            "identifier_arxiv",
        ),
    ]
    baseline = (catalog / "catalog.sqlite").read_bytes()
    for sql, kind in cases:
        (catalog / "catalog.sqlite").write_bytes(baseline)
        with sqlite3.connect(catalog / "catalog.sqlite") as c:
            c.execute(sql)
        assert kind in {f["kind"] for f in check()["findings"]}
