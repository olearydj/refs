"""The richer profile is tested against Pandoc, not against its own mapping code."""

import json
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest

from refs import bibliography
from refs.adapters.bibtex import parse, partition
from refs.models import REGISTRY, SourceCreate

# Independent, measured Pandoc 3.10 expectations; differences are explicit limits.
TYPES = {
    'article': ('unpublished', 'manuscript'), 'article-journal': ('article', 'article-journal'),
    'article-magazine': ('article', 'article-magazine'), 'article-newspaper': ('article', 'article-newspaper'),
    'book': ('book', 'book'), 'chapter': ('incollection', 'chapter'),
    'paper-conference': ('inproceedings', 'paper-conference'), 'webpage': ('online', 'webpage'),
    'post-weblog': ('online', 'webpage'), 'post': ('online', 'webpage'),
    'thesis': ('thesis', 'thesis'), 'report': ('report', 'report'),
    'standard': ('standard', 'legislation'), 'speech': ('unpublished', 'manuscript'),
    'document': ('misc', ''), 'patent': ('patent', 'patent'), 'manuscript': ('unpublished', 'manuscript'),
    'software': ('software', 'software'), 'periodical': ('periodical', 'article-journal'),
    'entry-encyclopedia': ('inreference', 'entry-encyclopedia'), 'map': ('image', 'graphic'),
    'graphic': ('image', 'graphic'), 'motion_picture': ('video', 'motion_picture'),
    'song': ('audio', 'song'), 'broadcast': ('audio', 'song'), 'dataset': ('dataset', 'dataset'),
}
IMPORT_LIMITS = {'article': 'manuscript', 'post-weblog': 'webpage', 'post': 'webpage',
                 'speech': 'manuscript', 'map': 'graphic', 'broadcast': 'song'}


def record(kind, **extra):
    return SourceCreate.model_validate({'schema_version': '1.0', 'citation_key': kind,
        'metadata': {'type': kind, 'title': 'Recorded Work', 'author': [{'family': 'Example'}],
                     'issued': {'date-parts': [[2026, 9, 17]]}, 'version': '6.21',
                     'page': '11–19', 'publisher-place': 'Auburn', **extra}}).canonical()


@pytest.fixture
def pandoc(request):
    tool = shutil.which('pandoc')
    if not tool:
        if request.config._refs_require_tools:
            pytest.fail('Rendering consumer unavailable: pandoc')
        pytest.skip('Rendering consumer unavailable: pandoc')
    return tool


def test_registry_covers_each_canonical_type_once():
    assert set(TYPES) == {r['canonical'] for r in REGISTRY['type_mappings']} == set(REGISTRY['biblatex_types'])
    for kind, (spelling, read_type) in TYPES.items():
        assert REGISTRY['biblatex_types'][kind]['entry_type'] == spelling
        assert REGISTRY['biblatex_types'][kind]['pandoc_type'] == read_type
        assert spelling in REGISTRY['bib_type_aliases']


@pytest.mark.slow
@pytest.mark.parametrize('kind', TYPES)
def test_pandoc_reads_type_date_version_pages_and_place(kind, pandoc):
    spelling, read_type = TYPES[kind]
    raw, warnings = bibliography.serialize([record(kind)], profile='biblatex-v1')
    assert raw.startswith(('@' + spelling + '{').encode())
    assert b'year =' not in raw and b'month =' not in raw and b'Issued:' not in raw and b'csltype' not in raw
    parsed = json.loads(subprocess.check_output([pandoc, '-f', 'biblatex', '-t', 'csljson'], input=raw))[0]
    assert parsed['type'] == read_type
    assert parsed['issued'] == {'date-parts': [[2026, 9, 17]]}
    assert parsed['version'] == '6.21' and parsed['page'] == '11-19' and parsed['publisher-place'] == 'Auburn'
    limits = [w for w in warnings if w['code'] == 'biblatex_consumer_type']
    assert bool(limits) == (read_type != kind)
    if limits:
        assert limits[0]['details']['class'] == 'documented_fallback'
        assert (read_type or 'unspecified CSL type') in limits[0]['message']
    assert not any(w['code'] == 'type_fallback' for w in warnings)


@pytest.mark.slow
@pytest.mark.parametrize(('medium', 'spelling', 'read_type'), [('radio', 'audio', 'song'), ('TV broadcast', 'video', 'motion_picture')])
def test_broadcast_medium_selects_reader_type_and_remains_in_note(pandoc, medium, spelling, read_type):
    raw, warnings = bibliography.serialize([record('broadcast', medium=medium)], profile='biblatex-v1')
    assert raw.startswith(('@' + spelling).encode()) and ('Medium: ' + medium).encode() in raw
    assert json.loads(subprocess.check_output([pandoc, '-f', 'biblatex', '-t', 'csljson'], input=raw))[0]['type'] == read_type
    assert any(read_type in w['message'] for w in warnings if w['code'] == 'biblatex_consumer_type')


def test_import_round_trip_keeps_faithful_records_and_reports_type_limits(initialized, tmp_path):
    before = {}
    values = []
    for kind, (spelling, _) in TYPES.items():
        value = record(kind)
        if kind not in IMPORT_LIMITS:
            value['native_type'] = {'namespace': 'bibtex', 'value': spelling}
        payload = tmp_path / (kind + '.json')
        payload.write_text(json.dumps(value))
        before[kind] = initialized('add', '--format', 'refs', '--input', payload)['data']
        values.append(value)
    output = tmp_path / 'all.bib'
    output.write_bytes(bibliography.serialize(values, profile='biblatex-v1')[0])
    result = initialized('import', '--format', 'bib', '--input', output, expected=4)['data']
    assert result['counts'] == {'applied': 0, 'unchanged': 20, 'conflict': 6, 'invalid': 0}
    for entry in result['entries']:
        kind = entry['citation_key']
        assert entry['outcome'] == ('conflict' if kind in IMPORT_LIMITS else 'unchanged')
        if kind in IMPORT_LIMITS:
            assert 'metadata.type' in entry['conflicts']
        after = initialized('show', kind)['data']
        assert after['metadata'] == before[kind]['metadata']
        assert after['title_protection'] == before[kind]['title_protection']


def test_biblatex_fields_replace_portable_notes_and_keep_title_protection():
    value = record('software', title='The canvaslms Package', genre='Source code repository',
                   **{'event-title': 'Meeting', 'event-place': 'Paris', 'status': 'forthcoming',
                      'number-of-pages': '100', 'number-of-volumes': '2'})
    value['title_protection'] = {'title': {'protected_terms': ['canvaslms'], 'preserve_case': False}}
    raw, warnings = bibliography.serialize([value], profile='biblatex-v1')
    assert b'{canvaslms}' in raw and b'version = {6.21}' in raw
    assert b'eventtitle = {Meeting}' in raw and b'venue = {Paris}' in raw and b'pubstate = {forthcoming}' in raw
    assert b'pagetotal = {100}' in raw and b'volumes = {2}' in raw and b'note =' not in raw
    incoming = parse(partition(raw)[0]['raw'])['source'].canonical()
    assert incoming['metadata'] == value['metadata']
    assert incoming['title_protection']['title']['protected_terms'] == ['canvaslms']


@pytest.mark.slow
def test_jose_software_versions_and_release_dates_render_under_chicago(pandoc, tmp_path):
    path = Path(__file__).parents[1] / 'fixtures/real-trial/converted/jose-danvas/repositories.json'
    values = [SourceCreate.model_validate(r).canonical() for r in json.loads(path.read_text())]
    output = tmp_path / 'references.bib'
    output.write_bytes(bibliography.serialize(values, profile='biblatex-v1')[0])
    rendered = subprocess.check_output([pandoc, '--citeproc', '--bibliography', str(output), '-t', 'plain', '--wrap=none'], input=b'---\nnocite: "@*"\n---\n').decode()
    for expected in ['V. 6.21. GitHub, released September 17.', 'V. 3.6.0. GitHub, released April 16.',
                     'V. 1.15.0. GitHub, released September 25.', 'V. 0.4.1. GitHub, released September 21.']:
        assert expected in rendered
    assert 'canvaslms:' in rendered and 'canvas-cli:' in rendered


def test_new_profile_keeps_target_binding_guard(initialized, tmp_path):
    payload = tmp_path / 'record.json'
    payload.write_text(json.dumps(record('software')))
    initialized('add', '--format', 'refs', '--input', payload)
    initialized('project', 'create', 'demo')
    initialized('project', 'cite', 'demo', 'software')
    output = tmp_path / 'refs.bib'
    args = ('export', '--project', 'demo', '--output', output)
    initialized(*args, '--profile', 'biblatex-v1')
    before = output.read_bytes(), (tmp_path / 'cat/catalog.sqlite').read_bytes()
    result = initialized(*args, '--profile', 'portable-bibtex-v1', expected=3)
    assert result['errors'][0]['code'] == 'target_binding_conflict'
    assert (output.read_bytes(), (tmp_path / 'cat/catalog.sqlite').read_bytes()) == before
    with sqlite3.connect(tmp_path / 'cat/catalog.sqlite') as db:
        assert db.execute('SELECT count(*) FROM export_targets').fetchone()[0] == 1


@pytest.mark.parametrize(('issued', 'iso'), [([[2026]], '2026'), ([[2026, 9]], '2026-09'), ([[2025, 1, 2], [2026, 9, 17]], '2025-01-02/2026-09-17')])
def test_iso_dates_keep_precision_without_year_month_or_note(issued, iso):
    value = record('software', issued={'date-parts': issued})
    raw, _ = bibliography.serialize([value], profile='biblatex-v1')
    assert ('date = {' + iso + '}').encode() in raw
    assert b'year =' not in raw and b'month =' not in raw and b'note =' not in raw
    assert parse(partition(raw)[0]['raw'])['source'].canonical()['metadata']['issued'] == {'date-parts': issued}


def test_unrepresentable_iso_date_refuses_without_dropping_precision():
    from refs.results import RefError
    with pytest.raises(RefError) as error:
        bibliography.serialize([record('software', issued={'date-parts': [[2026]], 'circa': True})], profile='biblatex-v1', allow_unknown=True)
    assert error.value.issue['code'] == 'export_blocked'
    assert error.value.issue['details']['entries'][0]['code'] == 'issued_date_lost_or_changed'


def test_native_patent_holder_is_a_field_not_a_note():
    value = record('patent', number='US123')
    value['extensions'] = {'patent': {'assignees': [{'literal': 'Research & Development'}]}}
    raw, _ = bibliography.serialize([value], profile='biblatex-v1')
    assert b'holder = {{Research \\& Development}}' in raw and b'note =' not in raw
    assert parse(partition(raw)[0]['raw'])['source'].canonical()['extensions'] == value['extensions']


@pytest.mark.slow
def test_existing_profiles_match_pre_biblatex_serializer_on_owner_catalog():
    import html
    import types
    from contextlib import closing

    from refs import math_text, sources

    catalog = Path('/Volumes/Casa/refs/cat/catalog.sqlite')
    if not catalog.exists():
        pytest.skip('Owner real catalog unavailable')
    root = Path(__file__).parents[2]
    previous = subprocess.run(['git', 'show', 'e4cff52:src/refs/bibliography.py'], cwd=root, text=True, capture_output=True)
    if previous.returncode:
        pytest.skip('Pinned pre-profile checkout unavailable')
    baseline = types.ModuleType('pre_biblatex')
    exec(compile(previous.stdout, 'pre-biblatex-bibliography.py', 'exec'), baseline.__dict__)
    with closing(sqlite3.connect(catalog.as_uri() + '?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        values = [sources.record(db, row[0]) for row in db.execute("SELECT id FROM sources WHERE state='active' ORDER BY citation_key")]
        for value in values:
            value.update(bibliography.preserved_bib_fields(db, value))
    assert bibliography.serialize(values)[0] == baseline.serialize(values)[0]
    # The later literal-CSL rule intentionally removes the old HTML escaping.
    # Keep the historical comparison for every other field and title detail.
    expected = json.loads(baseline.serialize_csl(values)[0])
    for entry in expected:
        for field in ('title', 'container-title'):
            if field in entry:
                entry[field] = math_text.transform(entry[field], html.unescape)
    assert json.loads(bibliography.serialize_csl(values)[0]) == expected
