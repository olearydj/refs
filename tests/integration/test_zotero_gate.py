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
        "author",
        "editor",
        "translator",
        "contributor",
    ]
    assert len(items["ITEM0001"]["notes"]) == 1


def test_empty_catalog_gate(initialized, tmp_path, zotero_fixture):
    result = GATE["compare"](tmp_path / "cat", zotero_fixture, zotero_fixture.parent / "base")
    assert result["summary"]["missing_items"] == 6
    assert result["summary"]["findings"] == 8


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
        c.executemany("INSERT INTO collections (id,library_uri,item_key,parent,name,path) VALUES (?,?,?,?,?,?)", [('Research',uri,'COLL0001',None,'Research','Research'),('Research/Methods',uri,'COLL0002','Research','Methods','Research/Methods'),('Empty',uri,'COLL0003',None,'Empty','Empty')])
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
            | ({"issued": e["issued"]} if e["issued"] else {})
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
    with sqlite3.connect(tmp_path/'cat/catalog.sqlite') as c:
        bindings=dict(c.execute("SELECT item_key,source_id FROM origin_identities WHERE namespace='zotero'"))
        for key,e in items.items():
            for target in e['relations']:
                c.execute('INSERT INTO source_relations VALUES (?,?,?,?)',(bindings[key],target,bindings.get(target.rsplit('/',1)[-1]),uri))
    return tmp_path / "cat"


def test_gate_negative_controls(initialized, tmp_path, zotero_fixture):
    catalog = populated(initialized, tmp_path, zotero_fixture)

    def check():
        return GATE["compare"](catalog, zotero_fixture, zotero_fixture.parent / "base")

    assert check()["summary"]["findings"] == 0
    cases = [
        ("UPDATE sources SET metadata_json=json_remove(metadata_json,'$.issued') WHERE citation_key='native1'", "issued"),
        (
            "UPDATE origin_identities SET library_uri='users/999' WHERE item_key='ITEM0001'",
            "missing_item",
        ),
        ("DELETE FROM collections WHERE path='Empty'", "collection_inventory"),
        ("UPDATE resources SET path='/nonexistent/synthetic' WHERE path LIKE '%linked.pdf'", "files"),
        ("UPDATE resources SET path='/nonexistent/synthetic' WHERE path LIKE '%relative.pdf'", "files"),
        ("UPDATE collections SET parent=NULL WHERE item_key='COLL0002'", "collection_structure"),
        ("DELETE FROM source_relations", "relations"),
        ("UPDATE sources SET metadata_json=json_set(metadata_json,'$.author',json_array(json_extract(metadata_json,'$.author[1]'),json_extract(metadata_json,'$.author[0]'))) WHERE citation_key='native1'", "creators_author"),
        ("UPDATE source_relations SET target_id=NULL", "related_endpoint"),
        ("UPDATE sources SET metadata_json=json_remove(metadata_json,'$.editor') WHERE citation_key='native1'", "creators_editor"),
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


def test_complete_extractor_importer_gate(initialized,tmp_path,zotero_fixture):
    from refs import importing
    from refs.config import select

    folder=tmp_path/'input'
    runpy.run_path('tools/zotero_extract/extract.py')['extract'](zotero_fixture,folder,zotero_fixture.parent,zotero_fixture.parent/'base',zotero_fixture.parent/'better-bibtex.sqlite')
    before={path:path.read_bytes() for path in zotero_fixture.parent.rglob('*') if path.is_file()}
    selected=select(str(tmp_path/'config.toml'),str(tmp_path/'cat'))
    result=importing.run_zotero(tmp_path/'cat',folder,settings=selected)
    assert result['counts']==dict(applied=6,unchanged=0,conflict=0,invalid=0)
    gate=GATE['compare'](tmp_path/'cat',zotero_fixture,zotero_fixture.parent/'base',{6:'legacy6'})
    assert gate['summary']['findings']==0,gate
    assert all(path.read_bytes()==raw for path,raw in before.items())
    repeated=importing.run_zotero(tmp_path/'cat',folder,settings=selected)
    assert repeated['counts']==dict(applied=0,unchanged=6,conflict=0,invalid=0)
    print(gate)


def test_gate_normalization_preserves_version_and_identity(initialized,tmp_path,zotero_fixture):
    with sqlite3.connect(zotero_fixture) as c:
        row=c.execute("SELECT d.valueID,v.value FROM itemData d JOIN fields f USING(fieldID) JOIN itemDataValues v USING(valueID) WHERE d.itemID=1 AND f.fieldName='extra'").fetchone()
        lines=[line for line in row[1].splitlines() if not line.lower().startswith(('arxiv:','doi:'))]
        c.execute('UPDATE itemDataValues SET value=? WHERE valueID=?',('\n'.join(lines+['arxiv: arXiv:2407.01502v2 [cs.AI]','doi: https://doi.org/10.1234/Mixed']),row[0]))
    catalog=populated(initialized,tmp_path,zotero_fixture)
    def check():
        return GATE['compare'](catalog,zotero_fixture,zotero_fixture.parent/'base')
    assert check()['summary']['findings']==0
    with sqlite3.connect(catalog/'catalog.sqlite') as c:
        c.execute("UPDATE sources SET details_json=json_set(details_json,'$.extensions.identifiers.arxiv','2407.01502') WHERE citation_key='native1'")
    assert 'identifier_arxiv' in {item['kind'] for item in check()['findings']}
    with sqlite3.connect(catalog/'catalog.sqlite') as c:
        c.execute("UPDATE sources SET metadata_json=json_set(metadata_json,'$.DOI','10.1234/different') WHERE citation_key='native1'")
    assert 'identifier_doi' in {item['kind'] for item in check()['findings']}


def test_gate_range_oracle_and_start_only_negative_control(initialized,tmp_path,zotero_fixture):
    for raw,expected in [('2011-03-19 19-23 March 2011',[[2011,3,19],[2011,3,23]]),('2022-09-08 08–13 Sep 2022',[[2022,9,8],[2022,9,13]]),('2019-00-00 2019/2020',[[2019],[2020]])]:
        assert GATE['expected_issued'](raw)=={'date-parts':expected}
    with sqlite3.connect(zotero_fixture) as c:
        c.execute("INSERT INTO itemDataValues (value) VALUES ('2011-03-19 19-23 March 2011')")
        c.execute("UPDATE itemData SET valueID=(SELECT valueID FROM itemDataValues WHERE value='2011-03-19 19-23 March 2011') WHERE itemID=1 AND fieldID=(SELECT fieldID FROM fields WHERE fieldName='date')")
    catalog=populated(initialized,tmp_path,zotero_fixture)
    assert GATE['compare'](catalog,zotero_fixture,zotero_fixture.parent/'base')['summary']['findings']==0
    with sqlite3.connect(catalog/'catalog.sqlite') as c:
        c.execute("UPDATE sources SET metadata_json=json_remove(metadata_json,'$.issued.date-parts[1]') WHERE citation_key='native1'")
    assert 'issued' in {item['kind'] for item in GATE['compare'](catalog,zotero_fixture,zotero_fixture.parent/'base')['findings']}
