import json
import runpy
import sqlite3

import pytest

EXTRACT = runpy.run_path("tools/zotero_extract/extract.py")["extract"]
GATE = runpy.run_path("tests/fixtures/real-trial/zotero_gate.py")


def test_extraction_matches_independent_oracle(zotero_fixture, tmp_path):
    before = zotero_fixture.read_bytes()
    output = tmp_path / "extract"
    EXTRACT(
        zotero_fixture,
        output,
        zotero_fixture.parent,
        zotero_fixture.parent / "base",
        zotero_fixture.parent / "better-bibtex.sqlite",
    )
    manifest = json.loads((output / "manifest.json").read_text())
    uri, expected, collections = GATE["expected"](
        zotero_fixture, zotero_fixture.parent / "base", {6: "legacy6"}
    )
    assert manifest["library_uri"] == uri
    assert manifest["legacy_keys"]["ITEM0006"] == "legacy6"
    assert manifest["skipped"] == {"trash": 1, "annotations": 1}
    for key, e in expected.items():
        data = json.loads((output / "items" / f"{key}.json").read_text())["data"]
        assert data["itemType"] == e["native"]
        assert [
            (
                n["creatorType"],
                n.get("lastName", n.get("name", "")),
                n.get("firstName", ""),
                "name" in n,
            )
            for n in data.get("creators", [])
        ] == e["names"]
    assert len(json.loads((output / "collections.json").read_text())) == len(collections)
    assert (
        json.loads((output / "items/FILE0012.json").read_text())["data"]["filename"] == "stored.pdf"
    )
    assert not (output / "items/TRASH030.json").exists()
    assert zotero_fixture.read_bytes() == before


@pytest.mark.parametrize("damage", ["schema", "parent", "identity"])
def test_extract_refuses_unsupported_or_inconsistent_input(zotero_fixture, tmp_path, damage):
    with sqlite3.connect(zotero_fixture) as c:
        c.execute(
            {
                "schema": "UPDATE version SET version=999 WHERE schema='userdata'",
                "parent": "UPDATE itemAttachments SET parentItemID=999 WHERE itemID=10",
                "identity": "DELETE FROM settings",
            }[damage]
        )
    with pytest.raises(ValueError):
        EXTRACT(zotero_fixture, tmp_path / "output", zotero_fixture.parent)
    assert not (tmp_path / "output").exists()
