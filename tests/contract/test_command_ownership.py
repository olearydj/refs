"""Command options reach one service result and one transaction."""


def test_add_loc_is_written_in_creation_revision(initialized, reference_path, tmp_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path, '--loc', 'Papers')['data']
    assert source['loc'] == 'Papers' and source['revision'] == 1
    bib = tmp_path / 'one.bib'
    bib.write_text('@book{book2024,title={A Book}}')
    imported = initialized('add', '--format', 'bib', '--input', bib, '--loc', 'Books')['data']
    assert imported['loc'] == 'Books' and imported['revision'] == 1


def test_citation_result_has_render_names(initialized, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    initialized('project', 'create', 'Paper')
    cited = initialized('project', 'cite', 'Paper', source['id'])['data']
    uncited = initialized('project', 'uncite', 'Paper', source['id'])['data']
    assert cited['citation_key'] == uncited['citation_key'] == source['citation_key']
    assert cited['project_name'] == uncited['project_name'] == 'Paper'


def test_key_result_has_previous_key(initialized, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    renamed = initialized('key', 'set', source['id'], '--key', 'renamed-2024', '--if-revision', 1, '--execute')['data']
    assert renamed['previous_key'] == source['citation_key']
    assert renamed['citation_key'] == 'renamed-2024'


def test_export_blocked_envelope_names_output(initialized, tmp_path):
    bib = tmp_path / 'legacy.bib'
    bib.write_text('@book{legacy key,title={A Book}}')
    source = initialized('import', '--input', bib)['data']['entries'][0]['source_id']
    initialized('project', 'create', 'Paper')
    initialized('project', 'cite', 'Paper', source)
    output = tmp_path / 'output.bib'
    result = initialized('export', '--project', 'Paper', '--output', output, expected=3)
    assert result['errors'][0]['code'] == 'export_blocked'
    assert result['errors'][0]['path'] == str(output)
    assert not output.exists()


def test_both_intake_commands_reject_conflicting_modes(initialized, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    add = initialized('add', '--format', 'refs', '--input', reference_path, '--file', reference_path, '--copy', '--link', expected=2)
    resource = initialized('resource', 'add', source['id'], '--path', reference_path, '--copy', '--link', expected=2)
    assert add['errors'][0]['code'] == resource['errors'][0]['code'] == 'invalid_invocation'
    assert initialized('show', source['id'])['data']['resources'] == []


def test_add_file_action_is_in_json_result(initialized, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path, '--file', reference_path, '--link')['data']
    assert source['file_action']['path'] == str(reference_path)
    assert len(initialized('show', source['id'])['data']['resources']) == 1
