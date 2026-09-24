def test_project_repeats_and_conflicts(initialized, tmp_path, reference_path):
    source = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    created = initialized("project", "create", "demo", "--description", "Synthetic project")["data"]
    assert initialized("project", "create", "demo", "--description", "Synthetic project")["data"]["id"] == created["id"]
    assert initialized("project", "create", "demo", "--description", "Different", expected=3)['errors'][0]['code']=='project_conflict'
    initialized("project", "cite", "demo", source["citation_key"])
    db = tmp_path / "cat" / "catalog.sqlite"
    before = db.read_bytes()
    assert initialized("project", "cite", created["id"], source["id"])["data"]["unchanged"]
    assert db.read_bytes() == before


def test_project_previews_and_removed_source(initialized, tmp_path, reference_path):
    db = tmp_path / "cat" / "catalog.sqlite"
    before = db.read_bytes()
    initialized("project", "create", "demo", "--dry-run")
    assert db.read_bytes() == before
    initialized("project", "create", "demo")
    source = initialized("add", "--format", "refs", "--input", reference_path)["data"]
    before = db.read_bytes()
    initialized("project", "cite", "demo", source["id"], "--dry-run")
    assert db.read_bytes() == before
    initialized("remove", source["id"], "--if-revision", source["revision"], "--execute")
    result = initialized("project", "cite", "demo", source["id"], expected=3)
    assert result["errors"][0]["code"] == "source_removed"


def test_show_uncite_and_removed_diagnostics(initialized, tmp_path, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    project = initialized('project', 'create', 'demo')['data']
    initialized('project', 'cite', 'demo', source['id'])
    assert initialized('project', 'show')['data']['items'][0]['id'] == project['id']
    assert initialized('project', 'show', 'demo')['data']['sources'][0]['id'] == source['id']
    initialized('remove', source['id'], '--if-revision', 1, '--execute')
    shown = initialized('project', 'show', 'demo')['data']
    assert shown['sources'] == []
    assert shown['removed_sources'][0]['id'] == source['id']
    initialized('project', 'uncite', 'demo', source['id'])
    db = tmp_path / 'cat/catalog.sqlite'
    before = db.read_bytes()
    assert initialized('project', 'uncite', 'demo', source['id'])['data']['unchanged']
    assert db.read_bytes() == before
