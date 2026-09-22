import json
import runpy

import pytest

from refs import bibliography, search, sources
from refs.adapters import bibtex, csl, zotero
from refs.results import RefError


def extracted(database, output):
    runpy.run_path("tools/zotero_extract/extract.py")["extract"](
        database,
        output,
        database.parent,
        database.parent / "base",
        database.parent / "better-bibtex.sqlite",
    )
    return zotero.read(output)


def test_fixture_mapping(zotero_fixture, tmp_path):
    bundle = extracted(zotero_fixture, tmp_path / "input")
    regular = [
        entry for entry in bundle["items"] if entry["data"]["itemType"] not in zotero.CHILDREN
    ]
    parsed = [zotero.parse(entry["item"], bundle["manifest"]) for entry in regular]
    assert [p["source"].citation_key for p in parsed] == [
        "native1",
        "extra2",
        "extra3",
        "extra4",
        "extra5",
        "legacy6",
    ]
    source = parsed[0]["source"].canonical()
    assert source["extensions"]["identifiers"] == {"arxiv": "2407.01502", "oclc": "456"}
    assert source["metadata"]["contributor"] == [{"literal": "Research and Design"}]
    assert source["metadata"]["author"][0]["family"] == "van Example"
    assert source["metadata"]["issued"] == {"date-parts": [[2020, 5, 4]]}
    assert parsed[0]["limitations"] == [
        {"field": "extra", "reason": "Preserved from import: extra"}
    ]
    assert all(p["source"].native_type.namespace == "zotero" for p in parsed)
    assert parsed[3]["source"].metadata.author[0].family == "Inventor"


def test_route_convergence_dates_and_aliases():
    manifest = {"library_uri": "users/local/LOCALKEY"}
    item = {
        "key": "ITEM0001",
        "data": {
            "itemType": "book",
            "title": "A Book",
            "date": "2020",
            "publisher": "Press",
            "edition": "2",
            "creators": [{"creatorType": "author", "lastName": "Smith", "firstName": "Alex"}],
        },
    }
    mapped = zotero.parse(item, manifest)["source"].canonical()["metadata"]
    bib = bibtex.parse(
        b"@book{x,title={A Book},year={2020},publisher={Press},edition={2},author={Smith, Alex}}"
    )["source"].canonical()["metadata"]
    assert mapped == bib == csl.parse(json.dumps(mapped).encode()).canonical()["metadata"]
    item["data"]["date"] = "Spring 2020"
    assert zotero.parse(item, manifest)["source"].metadata.issued.literal == "Spring 2020"
    item["meta"] = {"parsedDate": "2020-03"}
    assert zotero.parse(item, manifest)["source"].metadata.issued.date_parts == [[2020, 3]]
    item["data"].update(DOI="10.1/one", extra="DOI: 10.1/two")
    with pytest.raises(RefError, match="Competing"):
        zotero.parse(item, manifest)
    item["data"]["itemType"] = "unknown"
    with pytest.raises(RefError, match="No assessed"):
        zotero.parse(item, manifest)


@pytest.mark.parametrize("damage", ["parent", "collection", "uri", "version", "filename"])
def test_directory_admission(zotero_fixture, tmp_path, damage):
    folder = tmp_path / "input"
    extracted(zotero_fixture, folder)
    path = (
        folder / "manifest.json" if damage in ("uri", "version") else folder / "items/ITEM0001.json"
    )
    value = json.loads(path.read_bytes())
    if damage == "uri":
        value["library_uri"] = "invented"
    elif damage == "version":
        value["api_version"] = 9
    elif damage == "parent":
        value["data"]["parentItem"] = "NOITEM00"
    elif damage == "collection":
        value["data"]["collections"] = ["NOITEM00"]
    else:
        value["key"] = "../wrong"
    path.write_text(json.dumps(value))
    with pytest.raises(RefError):
        zotero.read(folder)


def test_identifier_search_and_portable_fallback(initialized, tmp_path):
    raw = {
        "schema_version": "1.0",
        "citation_key": "arxiv-test",
        "metadata": {
            "type": "document",
            "title": "A Study",
            "author": [{"family": "Smith"}],
            "issued": {"date-parts": [[2024]]},
            "note": "Supplied",
        },
        "extensions": {"identifiers": {"arxiv": "2407.01502", "oclc": "456"}},
    }
    record = sources.add(tmp_path / "cat", json.dumps(raw).encode(), "synthetic.json")
    for query in ("2407.01502", "456"):
        assert search.retrieve(tmp_path / "cat", query)["items"][0]["exact_match"]
    output, warnings = bibliography.serialize([record])
    assert b"eprint = {2407.01502}" in output and b"eprinttype = {arxiv}" in output
    assert b"note = {Supplied; arXiv:2407.01502}" in output
    assert all(w["details"]["class"] != "unknown" for w in warnings)
    output, _ = bibliography.serialize([record | {"_howpublished": "arXiv:2407.01502"}])
    assert b"note = {Supplied}" in output and b"howpublished = {arXiv:2407.01502}" in output
    raw["metadata"]["type"] = "article-journal"
    output, _ = bibliography.serialize([raw])
    assert b"note = {Supplied}" in output
