"""Command options reach the CLI and preserve state when previewed."""

import pytest


@pytest.mark.parametrize('action', ['update', 'key set', 'remove', 'reactivate', 'uncite', 'unlink'])
def test_dry_run_options_leave_catalog_unchanged(initialized, tmp_path, reference_path, action):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    key = source['citation_key']
    initialized('project', 'create', 'paper')
    initialized('project', 'cite', 'paper', key)
    resource = initialized('resource', 'add', key, '--path', tmp_path/'linked.pdf')['data']
    source = initialized('show', key)['data']
    if action == 'reactivate':
        initialized('remove', key, '--if-revision', source['revision'], '--execute')
        source = initialized('show', key)['data']
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    options = {
        'update': ('update', key, '--if-revision', source['revision'], '--set', 'metadata.publisher="Other"', '--dry-run'),
        'key set': ('key', 'set', key, '--key', 'replacement', '--if-revision', source['revision'], '--execute', '--dry-run'),
        'remove': ('remove', key, '--if-revision', source['revision'], '--execute', '--dry-run'),
        'reactivate': ('reactivate', key, '--execute', '--dry-run'),
        'uncite': ('project', 'uncite', 'paper', key, '--dry-run'),
        'unlink': ('resource', 'unlink', resource['id'], '--execute', '--dry-run'),
    }[action]
    result = initialized(*options)
    assert result['status'] == 'ok'
    assert result['data']['dry_run'] is True
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before


def test_export_profile_option_refuses_before_write(initialized, tmp_path, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    initialized('project', 'create', 'paper')
    initialized('project', 'cite', 'paper', source['citation_key'])
    target = tmp_path/'paper.bib'
    result = initialized('export', '--project', 'paper', '--output', target, '--profile', 'unsupported', expected=2)
    assert result['errors'][0]['code'] == 'unsupported_profile'
    assert not target.exists()


def test_open_resource_option_selects_without_launching(initialized, tmp_path, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    path = tmp_path/'linked.pdf'
    path.write_bytes(b'synthetic')
    initialized('resource', 'add', source['citation_key'], '--path', path)
    result = initialized('open', source['citation_key'], '--resource', 'missing', expected=3)
    assert result['errors'][0]['code'] == 'resource_unavailable'
    assert path.read_bytes() == b'synthetic'


@pytest.mark.parametrize('options', [('--link', '--copy'), ('--link', '--move'), ('--copy', '--move')])
def test_intake_modes_are_mutually_exclusive(initialized, tmp_path, reference_path, options):
    path = tmp_path/'incoming.pdf'
    path.write_bytes(b'synthetic')
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    result = initialized('add', '--format', 'refs', '--input', reference_path, '--file', path, *options, expected=2)
    assert result['errors'][0]['code'] == 'invalid_invocation'
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before
    assert path.read_bytes() == b'synthetic'


def test_resource_intake_modes_are_mutually_exclusive(initialized, tmp_path, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    path = tmp_path/'incoming.pdf'
    path.write_bytes(b'synthetic')
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    result = initialized('resource', 'add', source['citation_key'], '--path', path, '--copy', '--move', expected=2)
    assert result['errors'][0]['code'] == 'invalid_invocation'
    assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before
    assert path.read_bytes() == b'synthetic'


def test_update_requires_exactly_one_patch_form(initialized, tmp_path, reference_path):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    patch = tmp_path/'patch.json'
    patch.write_text('{"schema_version":"1.0","set":{"metadata.publisher":"Other"}}')
    before = (tmp_path/'cat/catalog.sqlite').read_bytes()
    for extra in ((), ('--patch', patch, '--set', 'metadata.publisher="Other"')):
        result = initialized('update', source['citation_key'], '--if-revision', source['revision'], *extra, expected=2)
        assert result['errors'][0]['code'] == 'invalid_invocation'
        assert (tmp_path/'cat/catalog.sqlite').read_bytes() == before
