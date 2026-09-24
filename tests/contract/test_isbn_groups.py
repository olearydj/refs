import json

import pytest
from conftest import extracted

from refs import importing, sources
from refs.catalog import connect

SHARED = b"""@book{setA,title={Player Handbook},isbn={978-1-23},edition={1}}
@book{setB,title={Monster Manual},isbn={978123},edition={1}}
@book{setC,title={Dungeon Guide},isbn={978123},edition={1}}
@incollection{chapterA,title={Chapter One},booktitle={Collected Work},isbn={978123}}
@incollection{chapterB,title={Chapter Two},booktitle={Collected Work},isbn={978123}}
@book{statsA,title={Statistics},isbn={978456},edition={1}}
@book{statsB,title={Statistics},isbn={978456},edition={2}}"""


def test_shared_isbns_in_fresh_batch_never_merge(initialized, tmp_path):
    catalog = tmp_path / "cat"
    first = importing.run(catalog, SHARED, "shared.bib")
    assert first["counts"] == dict(applied=7, unchanged=0, conflict=0, invalid=0)
    assert importing.run(catalog, SHARED, "shared.bib")["counts"]["unchanged"] == 7
    with connect(catalog) as c:
        assert c.execute("SELECT count(*) FROM sources").fetchone()[0] == 7
        assert {r[0] for r in c.execute("SELECT citation_key FROM sources")} == {
            "setA",
            "setB",
            "setC",
            "chapterA",
            "chapterB",
            "statsA",
            "statsB",
        }


@pytest.mark.parametrize("existing,incoming", [(1, 2), (2, 1), (2, 2)])
def test_ambiguous_group_blocks_every_isbn_proposal(initialized, tmp_path, existing, incoming):
    catalog = tmp_path / "cat"
    importing.run(
        catalog,
        b"\n".join(
            b"@book{old" + str(i).encode() + b",title={Old Book},isbn={978123}}"
            for i in range(existing)
        ),
        "old.bib",
    )
    raw = b"\n".join(
        b"@book{new" + str(i).encode() + b",title={New Book},isbn={978123}}"
        for i in range(incoming)
    )
    result = importing.run(catalog, raw, "new.bib")
    assert result["counts"]["conflict"] == incoming
    assert all(e["details"]["incoming_count"] == incoming for e in result["entries"])
    with connect(catalog) as c:
        assert c.execute("SELECT count(*) FROM sources").fetchone()[0] == existing
        assert (
            c.execute(
                "SELECT count(*) FROM origin_identities WHERE library_uri='new.bib'"
            ).fetchone()[0]
            == 0
        )


def test_single_capture_books_only_and_doi_unchanged(initialized, tmp_path):
    catalog = tmp_path / "cat"
    importing.run(catalog, b"@book{book,title={Whole Book},isbn={978123}}", "book.bib")
    incoming = {
        "schema_version": "1.0",
        "citation_key": "chapter",
        "metadata": {
            "type": "chapter",
            "title": "A Chapter",
            "ISBN": "978123",
            "DOI": "10.1/chapter",
        },
    }
    chapter = sources.add(catalog, json.dumps(incoming).encode(), "chapter.json")
    assert chapter["outcome"] == "created"
    incoming["citation_key"] = "doi-overlap"
    assert (
        sources.add(catalog, json.dumps(incoming).encode(), "overlap.json")["id"] == chapter["id"]
    )
    identical = {
        "schema_version": "1.0",
        "citation_key": "other-book-key",
        "metadata": {"type": "book", "title": "Whole Book", "ISBN": "978-123"},
    }
    assert (
        sources.add(catalog, json.dumps(identical).encode(), "same-book.json")["citation_key"]
        == "book"
    )


def test_zotero_shared_book_isbn_preserves_each_key(initialized, zotero_fixture, tmp_path):
    folder = tmp_path / "input"
    extracted(zotero_fixture, folder)
    base = json.loads((folder / "items/ITEM0002.json").read_bytes())
    for i in (7, 8):
        item = json.loads(json.dumps(base))
        item["key"] = item["data"]["key"] = f"ITEM{i:04}"
        item["data"]["title"] = "Another Core Book " + str(i)
        item["data"]["extra"] = "Citation Key: core" + str(i)
        (folder / "items" / f"ITEM{i:04}.json").write_text(json.dumps(item))
    first = initialized("import", "--format", "zotero", "--input", folder)["data"]
    assert first["counts"] == dict(applied=8, unchanged=0, conflict=0, invalid=0)
    assert (
        initialized("import", "--format", "zotero", "--input", folder)["data"]["counts"][
            "unchanged"
        ]
        == 8
    )
