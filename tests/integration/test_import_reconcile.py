import pytest

from refs import importing, sources
from refs.catalog import connect
from refs.results import RefError


def conflict(catalog):
    importing.run(catalog, b"@book{a,title={First},publisher={Old},year={2020}}", "test.bib")
    return importing.run(
        catalog, b"@book{a,title={Second},publisher={New},year={2020}}", "test.bib"
    )["import_id"]


def test_preview_partial_execution_and_repeat(initialized, tmp_path):
    catalog = tmp_path / "cat"
    batch = conflict(catalog)
    before = (catalog / "catalog.sqlite").read_bytes()
    shown = initialized("import", "show", batch, "--status", "conflict")["data"]
    preview = initialized("import", "reconcile", batch, "--take-incoming", "a.metadata.title")[
        "data"
    ]
    assert preview["batch_revision"] == shown["batch_revision"]
    assert preview["entries"][0]["source_revision"] == sources.show(catalog, "a")["revision"]
    assert (catalog / "catalog.sqlite").read_bytes() == before
    result = initialized(
        "import",
        "reconcile",
        batch,
        "--take-incoming",
        "a.metadata.title",
        "--execute",
        "--if-batch-revision",
        preview["batch_revision"],
    )["data"]
    assert result["entries"][0]["remaining_conflicts"][0]["path"] == "metadata.publisher"
    current = sources.show(catalog, "a")
    assert current["metadata"]["title"] == "Second" and current["metadata"]["publisher"] == "Old"
    assert current["citation_key"] == "a" and "metadata.title" in current["corrected_fields"]
    assert any(item['origin']=='import-reconciled' for item in current['originals'])
    shown = importing.show(catalog, batch)
    assert len(shown["entries"][0]["decisions"]) == 1
    importing.reconcile(catalog, batch, ["a"], execute=True, revision=shown["batch_revision"])
    assert sources.show(catalog, "a")["metadata"]["publisher"] == "New"
    shown = importing.show(catalog, batch)
    assert shown["counts"]["applied"] == 1 and shown["counts"]["conflict"] == 0
    revision = sources.show(catalog, "a")["revision"]
    importing.reconcile(catalog, batch, ["a"], execute=True, revision=shown["batch_revision"])
    assert sources.show(catalog, "a")["revision"] == revision


def test_stale_source_and_batch_refuse_atomically(initialized, tmp_path):
    catalog = tmp_path / "cat"
    batch = conflict(catalog)
    preview = importing.reconcile(catalog, batch, ["a"])
    source = sources.show(catalog, "a")
    sources.update(
        catalog, "a", {"schema_version": "1.0", "set": {"metadata.volume": "3"}}, source["revision"]
    )
    with pytest.raises(RefError, match="changed"):
        importing.reconcile(catalog, batch, ["a"], execute=True, revision=preview["batch_revision"])
    assert sources.show(catalog, "a")["metadata"]["title"] == "First"
    preview = importing.reconcile(catalog, batch, ["a"])
    with connect(catalog, write=True) as c:
        c.execute("UPDATE imports SET revision=revision+1 WHERE id=?", (batch,))
    with pytest.raises(RefError, match="changed"):
        importing.reconcile(catalog, batch, ["a"], execute=True, revision=preview["batch_revision"])


def test_bad_selector_identity_and_missing_revision(initialized, tmp_path):
    catalog = tmp_path / "cat"
    batch = conflict(catalog)
    for selectors, code in ((["absent"], "ambiguous_selection"), (["a.metadata.not_a_field"], "invalid_selection"), ([], "invalid_selection")):
        with pytest.raises(RefError) as error:
            importing.reconcile(catalog, batch, selectors)
        assert error.value.issue['code'] == code
        assert sources.show(catalog, 'a')['metadata']['title'] == 'First'
    with pytest.raises(RefError, match="Preview"):
        importing.reconcile(catalog, batch, ["a"], execute=True)
    ambiguous = importing.run(
        catalog, b"@book{a,title={Second}}\n@book{a,title={Third}}", "duplicate.bib"
    )["import_id"]
    with pytest.raises(RefError, match="unambiguous"):
        importing.reconcile(catalog, ambiguous, ["a"])
    incompatible = importing.run(catalog, b"@article{a,title={Another}}", "type.bib")["import_id"]
    with pytest.raises(RefError, match="identity"):
        importing.reconcile(catalog, incompatible, ["a"])
