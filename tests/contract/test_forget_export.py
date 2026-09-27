"""Forgetting a binding cannot remove or silently adopt a publication file."""


def test_forget_target_preserves_file_and_allows_fresh_binding(initialized, tmp_path, reference_path, human):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    initialized('project', 'create', 'paper')
    initialized('project', 'cite', 'paper', source['id'])
    path = tmp_path / 'references.bib'
    initialized('export', '--project', 'paper', '--output', path)
    before = path.read_bytes()
    preview = initialized('export', '--forget', path, '--dry-run')['data']
    assert preview['dry_run'] and not preview['forgotten']
    assert len(initialized('summary')['data']['projects'][0]['targets']) == 1
    assert 'file unchanged' in human('export', '--forget', path)
    assert path.read_bytes() == before
    assert initialized('summary')['data']['projects'][0]['targets'] == []
    refused = initialized('export', '--project', 'paper', '--output', path, expected=3)
    assert refused['errors'][0]['code'] == 'unadopted_target'
    assert path.read_bytes() == before
    # The owner archives the old file; a different profile can now bind fresh.
    path.rename(tmp_path / 'archived.bib')
    initialized('export', '--project', 'paper', '--output', path, '--profile', 'biblatex-v1')
    targets = initialized('summary')['data']['projects'][0]['targets']
    assert targets == [dict(destination=str(path), profile='biblatex-v1', state='current')]
    assert (tmp_path / 'archived.bib').read_bytes() == before


def test_forget_unknown_target_refuses_without_changes(initialized, tmp_path):
    path = tmp_path / 'unregistered.bib'
    path.write_bytes(b'owner file')
    before = (tmp_path / 'cat/catalog.sqlite').read_bytes()
    result = initialized('export', '--forget', path, expected=3)
    assert result['errors'][0]['code'] == 'target_missing'
    assert result['errors'][0]['path'] == str(path)
    assert path.read_bytes() == b'owner file'
    assert (tmp_path / 'cat/catalog.sqlite').read_bytes() == before
