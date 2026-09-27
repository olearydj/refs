"""CSL identity output shares the export target protocol without portable mappings."""

import hashlib
import json
import sqlite3
from contextlib import closing
from copy import deepcopy
from pathlib import Path

import pytest

from refs import bibliography
from refs.adapters import csl
from refs.results import RefError

FIXTURES = Path(__file__).resolve().parents[1] / 'fixtures'
PROFILE = 'csl-json-v1'


@pytest.fixture
def csl_project(initialized, tmp_path):
    payloads = [
        {'schema_version': '1.0', 'citation_key': 'zulu', 'loc': 'Family/Test',
         'metadata': {'type': 'document', 'title': 'Second Work', 'genre': 'Original wartime document',
                      'medium': 'scanned copy', 'source': 'Capture database'},
         'context': [{'text': 'Private capture', 'origin': 'agent'}],
         'provenance': [{'origin': 'agent', 'access': 'metadata'}],
         'native_type': {'namespace': 'bibtex', 'value': 'misc'}},
        {'schema_version': '1.0', 'citation_key': 'alpha',
         'metadata': {'type': 'book', 'title': 'Café', 'language': 'fr'}},
    ]
    initialized('project', 'create', 'demo')
    for payload in payloads:
        path = tmp_path / (payload['citation_key'] + '.json')
        path.write_text(json.dumps(payload, ensure_ascii=False))
        source = initialized('add', '--format', 'refs', '--input', path)['data']
        initialized('project', 'cite', 'demo', source['id'])
    return tmp_path / 'cat', tmp_path / 'references.json'


def export(initialized, output, *args, expected=0):
    return initialized('export', '--project', 'demo', '--output', output,
                       '--profile', PROFILE, *args, expected=expected)


def test_csl_fixed_project_bytes_are_stable_and_metadata_only(initialized, csl_project):
    catalog, output = csl_project
    expected = '''[
  {
    "id": "alpha",
    "language": "fr",
    "title": "Café",
    "type": "book"
  },
  {
    "genre": "Original wartime document",
    "id": "zulu",
    "medium": "scanned copy",
    "source": "Capture database",
    "title": "Second Work",
    "type": "document"
  }
]
'''.encode()
    preview_before = (catalog / 'catalog.sqlite').read_bytes()
    preview = export(initialized, output, '--dry-run')
    assert preview['command'] == 'export' and preview['status'] == 'ok'
    assert preview['data']['profile'] == PROFILE
    assert preview['data']['keys'] == ['alpha', 'zulu']
    assert preview['data']['sha256'] == hashlib.sha256(expected).hexdigest()
    assert preview['data']['info'] == [] and preview['warnings'] == []
    assert not output.exists()
    assert (catalog / 'catalog.sqlite').read_bytes() == preview_before
    assert not list(output.parent.glob('.refs-*.tmp'))
    first = export(initialized, output)
    assert output.read_bytes() == expected
    assert first['data']['count'] == 2
    before = (catalog / 'catalog.sqlite').read_bytes()
    again = export(initialized, output)
    assert again['data']['unchanged'] is True
    assert again['data']['sha256'] == first['data']['sha256']
    assert output.read_bytes() == expected
    assert (catalog / 'catalog.sqlite').read_bytes() == before
    with closing(sqlite3.connect(catalog / 'catalog.sqlite')) as connection:
        assert connection.execute('SELECT profile_fingerprint, baseline_digest, pending_digest FROM export_targets').fetchone() == (hashlib.sha256(PROFILE.encode()).hexdigest(), first['data']['sha256'], None)


def test_importing_csl_export_leaves_every_source_unchanged(initialized, csl_project):
    catalog, output = csl_project
    for key, protection in [('alpha', {'protected_terms': ['Café']}),
                            ('zulu', {'preserve_case': True})]:
        initialized('update', key, '--set', 'title_protection.title=' + json.dumps(protection))
    export(initialized, output)
    before = {key: initialized('show', key)['data'] for key in ['alpha', 'zulu']}
    imported = initialized('import', '--format', 'csljson', '--input', output)
    assert imported['data']['counts'] == dict(applied=0, unchanged=2, conflict=0, invalid=0)
    assert [entry['citation_key'] for entry in imported['data']['entries']] == ['alpha', 'zulu']
    for key in before:
        current = initialized('show', key)['data']
        for field in ['metadata', 'context', 'native_type', 'loc', 'title_protection']:
            assert current.get(field) == before[key].get(field)
    with closing(sqlite3.connect(catalog / 'catalog.sqlite')) as connection:
        assert connection.execute('SELECT count(*) FROM sources').fetchone()[0] == 2


@pytest.mark.parametrize('field', ['title', 'container-title'])
@pytest.mark.parametrize('value, protection, csl_value, bib_value', [
    ('canvas-cli canvas canvaslms café $x$',
     {'protected_terms': ['canvas', 'canvas-cli', 'cafe\u0301', 'x']},
     '<span class="nocase">canvas-cli</span> <span class="nocase">canvas</span> canvaslms <span class="nocase">café</span> $x$',
     '{canvas-cli} {canvas} canvaslms {café} $x$'),
    ('the canvas-cli & its <API>', {'preserve_case': True, 'protected_terms': ['canvas-cli']},
     '<span class="nocase">the canvas-cli &amp; its &lt;API&gt;</span>',
     r'{the canvas-cli \& its <API>}'),
])
def test_csl_protection_preserves_plain_metadata_and_bibtex(field, value, protection, csl_value, bib_value):
    record = {'schema_version': '1.0', 'citation_key': 'protected',
              'metadata': {'type': 'article-journal', 'title': 'Example', field: value},
              'title_protection': {field: protection}}
    before = deepcopy(record)
    output, warnings = bibliography.serialize_csl([record])
    entry = json.loads(output)[0]
    assert entry[field] == csl_value
    assert warnings == []
    assert record == before
    restored = csl.parse(output).canonical()
    assert restored['metadata'][field] == value
    recovered = restored['title_protection'][field]
    if protection.get('preserve_case'):
        assert recovered['preserve_case'] is True
    else:
        assert recovered == {'protected_terms': ['canvas-cli', 'canvas', 'café'], 'preserve_case': False}
    bib, _ = bibliography.serialize([record])
    bib_field = 'title' if field == 'title' else 'journal'
    assert f'  {bib_field} = {{{bib_value}}},\n'.encode() in bib


def test_jose_protection_keeps_bibtex_profile_bytes():
    fixture = FIXTURES / 'real-trial/minimized/jose-title-protection.json'
    output, _ = bibliography.serialize(json.loads(fixture.read_text()))
    assert output == fixture.with_suffix('.bib').read_bytes()


def test_csl_outside_edit_refuses_and_overwrite_preserves_original(initialized, csl_project):
    catalog, output = csl_project
    export(initialized, output)
    candidate = output.read_bytes()
    outside = b'[{"id":"outside","type":"document","title":"Outside edit"}]\n'
    output.write_bytes(outside)
    before = (catalog / 'catalog.sqlite').read_bytes()
    refused = export(initialized, output, expected=3)
    assert refused['errors'][0]['code'] == 'outside_edit'
    assert output.read_bytes() == outside
    assert (catalog / 'catalog.sqlite').read_bytes() == before
    export(initialized, output, '--overwrite')
    assert output.read_bytes() == candidate
    with closing(sqlite3.connect(catalog / 'catalog.sqlite')) as connection:
        assert connection.execute("SELECT raw_bytes, format FROM originals WHERE origin='export-overwrite'").fetchone() == (outside, 'csljson')


def test_csl_adoption_requires_import_of_current_bytes(initialized, csl_project):
    catalog, output = csl_project
    raw = '[{"id":"alpha","type":"book","title":"Café","language":"fr"}]\n'.encode()
    output.write_bytes(raw)
    for flags, code in [((), 'unadopted_target'), (('--adopt', '--overwrite'), 'adoption_requires_import')]:
        before = (catalog / 'catalog.sqlite').read_bytes()
        result = export(initialized, output, *flags, expected=3)
        assert result['errors'][0]['code'] == code
        assert output.read_bytes() == raw
        assert (catalog / 'catalog.sqlite').read_bytes() == before
    imported = initialized('import', '--format', 'csljson', '--input', output)
    assert imported['data']['counts'] == dict(applied=0, unchanged=1, conflict=0, invalid=0)
    before = (catalog / 'catalog.sqlite').read_bytes()
    refused = export(initialized, output, '--adopt', expected=3)
    assert refused['errors'][0]['code'] == 'adoption_requires_overwrite'
    assert output.read_bytes() == raw
    assert (catalog / 'catalog.sqlite').read_bytes() == before
    preview = export(initialized, output, '--adopt', '--overwrite', '--dry-run')
    assert preview['data']['import_conflicts'] == []
    assert output.read_bytes() == raw
    assert (catalog / 'catalog.sqlite').read_bytes() == before
    result = export(initialized, output, '--adopt', '--overwrite')
    assert result['data']['import_conflicts'] == []
    assert [entry['id'] for entry in json.loads(output.read_bytes())] == ['alpha', 'zulu']


def test_csl_exact_bytes_adopt_without_rewriting(initialized, csl_project):
    catalog, output = csl_project
    export(initialized, output)
    unbound = output.with_name('imported.json')
    unbound.write_bytes(output.read_bytes())
    initialized('import', '--format', 'csljson', '--input', unbound)
    before = unbound.read_bytes()
    result = export(initialized, unbound, '--adopt')
    assert result['data']['unchanged'] is True
    assert result['data']['import_conflicts'] == []
    assert unbound.read_bytes() == before
    with closing(sqlite3.connect(catalog / 'catalog.sqlite')) as connection:
        assert connection.execute('SELECT count(*) FROM export_targets').fetchone()[0] == 2


@pytest.mark.parametrize('bound_profile', ['portable-bibtex-v1', PROFILE])
@pytest.mark.parametrize('flags', [(), ('--overwrite',), ('--adopt', '--overwrite')])
def test_destination_cannot_switch_export_profile(initialized, tmp_path, reference_path, bound_profile, flags):
    source = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    initialized('project', 'create', 'demo')
    initialized('project', 'cite', 'demo', source['id'])
    output = tmp_path / 'bound-output'
    initialized('export', '--project', 'demo', '--output', output, '--profile', bound_profile)
    other = PROFILE if bound_profile == 'portable-bibtex-v1' else 'portable-bibtex-v1'
    before_file = output.read_bytes()
    before_catalog = (tmp_path / 'cat/catalog.sqlite').read_bytes()
    result = initialized('export', '--project', 'demo', '--output', output, '--profile', other, *flags, expected=3)
    assert result['errors'][0]['code'] == 'target_binding_conflict'
    assert output.read_bytes() == before_file
    assert (tmp_path / 'cat/catalog.sqlite').read_bytes() == before_catalog


def test_csl_destination_cannot_switch_project(initialized, csl_project):
    catalog, output = csl_project
    export(initialized, output)
    initialized('project', 'create', 'other')
    before = output.read_bytes(), (catalog / 'catalog.sqlite').read_bytes()
    result = initialized('export', '--project', 'other', '--output', output, '--profile', PROFILE, expected=3)
    assert result['errors'][0]['code'] == 'target_binding_conflict'
    assert (output.read_bytes(), (catalog / 'catalog.sqlite').read_bytes()) == before


def test_csl_empty_selection_requires_overwrite(initialized, csl_project):
    catalog, output = csl_project
    export(initialized, output)
    for key in ['alpha', 'zulu']:
        initialized('project', 'uncite', 'demo', key)
    before = output.read_bytes(), (catalog / 'catalog.sqlite').read_bytes()
    result = export(initialized, output, expected=3)
    assert result['errors'][0]['code'] == 'outside_edit'
    assert (output.read_bytes(), (catalog / 'catalog.sqlite').read_bytes()) == before
    result = export(initialized, output, '--overwrite')
    assert output.read_bytes() == b'[]\n'
    assert result['data']['count'] == 0 and result['warnings'][0]['code'] == 'empty_selection'


def test_csl_revalidation_refuses_before_staging(initialized, csl_project):
    catalog, output = csl_project
    with closing(sqlite3.connect(catalog / 'catalog.sqlite')) as connection, connection:
        connection.execute("UPDATE sources SET metadata_json=json_set(metadata_json,'$.unexpected','retained') WHERE citation_key='zulu'")
    before = (catalog / 'catalog.sqlite').read_bytes()
    result = export(initialized, output, '--allow-unknown-mappings', expected=3)
    error = result['errors'][0]
    assert error['code'] == 'export_blocked' and error['path'] == str(output)
    assert error['details']['entries'][0]['code'] == 'unsupported_record'
    assert error['details']['entries'][0]['citation_key'] == 'zulu'
    assert not output.exists() and not list(output.parent.glob('.refs-*.tmp'))
    assert (catalog / 'catalog.sqlite').read_bytes() == before


def test_csl_interrupted_publication_recovers_shared_intent(csl_project, monkeypatch):
    catalog, output = csl_project
    original = bibliography.finish_export
    def interrupted(*args):
        raise OSError('Synthetic interruption after CSL publication')
    monkeypatch.setattr(bibliography, 'finish_export', interrupted)
    with pytest.raises(RefError) as error:
        bibliography.export(catalog, 'demo', output, profile=PROFILE)
    assert error.value.exit_code == 4
    assert error.value.issue['code'] == 'export_published_unrecorded'
    published = output.read_bytes()
    before = (catalog / 'catalog.sqlite').read_bytes()
    assert bibliography.export(catalog, 'demo', output, profile=PROFILE, dry_run=True)['recoverable'] is True
    assert (catalog / 'catalog.sqlite').read_bytes() == before
    monkeypatch.setattr(bibliography, 'finish_export', original)
    result = bibliography.export(catalog, 'demo', output, profile=PROFILE)
    assert result['recovered'] is True
    assert output.read_bytes() == published
    with closing(sqlite3.connect(catalog / 'catalog.sqlite')) as connection:
        assert connection.execute('SELECT baseline_digest, pending_digest FROM export_targets').fetchone() == (hashlib.sha256(published).hexdigest(), None)


def test_unsupported_profile_names_both_supported_choices(initialized, csl_project):
    catalog, output = csl_project
    before = (catalog / 'catalog.sqlite').read_bytes()
    result = initialized('export', '--project', 'demo', '--output', output, '--profile', 'unrecognized', expected=2)
    assert result['errors'][0]['code'] == 'unsupported_profile'
    assert 'portable-bibtex-v1' in result['errors'][0]['message']
    assert PROFILE in result['errors'][0]['message']
    assert not output.exists() and (catalog / 'catalog.sqlite').read_bytes() == before


def test_csl_existing_id_still_reports_different_values(initialized, csl_project):
    catalog, output = csl_project
    raw = {'id': 'zulu', 'type': 'document', 'title': 'Different Work'}
    output.write_text(json.dumps(raw))
    before = (catalog / 'catalog.sqlite').read_bytes()
    result = initialized('import', '--format', 'csljson', '--input', output, '--dry-run', expected=4)
    assert result['data']['counts'] == dict(applied=0, unchanged=0, conflict=1, invalid=0)
    entry = result['data']['entries'][0]
    assert entry['code'] == 'value_conflict' and entry['citation_key'] == 'zulu'
    assert 'metadata.title' in entry['conflicts']
    assert (catalog / 'catalog.sqlite').read_bytes() == before


def test_csl_unrelated_external_id_keeps_generated_key(initialized, csl_project):
    _, output = csl_project
    output.write_text(json.dumps({'id': 'external-id', 'type': 'document', 'title': 'Other Work'}))
    result = initialized('import', '--format', 'csljson', '--input', output)
    assert result['data']['counts'] == dict(applied=1, unchanged=0, conflict=0, invalid=0)
    assert result['data']['entries'][0]['citation_key'] == 'otherWork-ND'
    again = initialized('import', '--format', 'csljson', '--input', output)
    assert again['data']['counts'] == dict(applied=0, unchanged=1, conflict=0, invalid=0)


def test_csl_key_and_doi_disagreement_remains_identity_conflict(initialized, csl_project, reference_path):
    catalog, output = csl_project
    other = initialized('add', '--format', 'refs', '--input', reference_path)['data']
    output.write_text(json.dumps(other['metadata'] | {'id': 'zulu'}))
    before = (catalog / 'catalog.sqlite').read_bytes()
    result = initialized('import', '--format', 'csljson', '--input', output, '--dry-run', expected=4)
    entry = result['data']['entries'][0]
    assert entry['code'] == 'identity_conflict'
    assert set(entry['details']['source_ids']) == {other['id'], initialized('show', 'zulu')['data']['id']}
    assert (catalog / 'catalog.sqlite').read_bytes() == before


def test_csl_adoption_reports_invalid_import_entries(initialized, csl_project):
    catalog, output = csl_project
    raw = b'[{"id":"invalid","type":"made-up","title":"Invalid entry"}]\n'
    output.write_bytes(raw)
    imported = initialized('import', '--format', 'csljson', '--input', output, expected=4)
    assert imported['data']['counts'] == dict(applied=0, unchanged=0, conflict=0, invalid=1)
    before = (catalog / 'catalog.sqlite').read_bytes()
    result = export(initialized, output, '--adopt', '--overwrite', '--dry-run')
    assert result['data']['import_conflicts'][0]['code'] == 'invalid_record'
    assert output.read_bytes() == raw
    assert (catalog / 'catalog.sqlite').read_bytes() == before
