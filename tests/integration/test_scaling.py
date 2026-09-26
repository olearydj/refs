"""Costs that must not grow with the catalog: each test pins the rule with a query plan or a trace, and a loose timing as a smoke check.

The catalog is built once per module by copying one real record into 3,000 sources through SQL, which is the shape the
2026-09-25 performance investigation measured (reviews/2026-09-25-performance-investigation.md). The trace and plan
assertions are the guards; the timing bounds are generous so the suite stays honest on slow machines.
"""

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

import pytest

from refs import importing, projects, sources
from refs.adapters import search_sqlite
from refs.catalog import connect
from refs.config import select

SOURCES = 3000


@contextmanager
def traced(connection):
    statements = []
    connection.set_trace_callback(statements.append)
    try:
        yield statements
    finally:
        connection.set_trace_callback(None)


@pytest.fixture(scope='module')
def big_catalog(tmp_path_factory):
    """An initialized catalog with one real record and 2,999 copies of it under distinct keys and titles."""
    import os
    import subprocess
    import sys

    home = tmp_path_factory.mktemp('scaling')
    env = dict(os.environ, REFS_CONFIG=str(home / 'config.toml'), REFS_CATALOG=str(home / 'cat'))
    command = [sys.executable, '-m', 'refs', '--json', '--no-project-config']
    subprocess.run(command + ['init', '--library-root', str(home / 'lib')], env=env, check=True, capture_output=True)
    reference = Path(__file__).parents[1] / 'fixtures' / 'reference.json'
    subprocess.run(command + ['add', '--format', 'refs', '--input', str(reference)], env=env, check=True, capture_output=True)
    with sqlite3.connect(home / 'cat' / 'catalog.sqlite') as c:
        row = dict(zip([d[0] for d in c.execute('SELECT * FROM sources').description], c.execute('SELECT * FROM sources').fetchone()))
        columns = [key for key in row]
        rows = []
        for index in range(1, SOURCES):
            copy = dict(row)
            copy['id'] = str(uuid.uuid4())
            copy['citation_key'] = f'{row["citation_key"]}-{index}'
            metadata = json.loads(copy['metadata_json'])
            metadata['title'] = f'{metadata["title"]} number {index}'
            metadata.pop('DOI', None)
            copy['metadata_json'] = json.dumps(metadata)
            rows.append(tuple(copy[key] for key in columns))
        c.executemany(f'INSERT INTO sources ({",".join(columns)}) VALUES ({",".join("?" * len(columns))})', rows)
        # every source carries an original, so the originals table has the shape the record loader scans
        c.executemany("INSERT INTO originals (id, source_id, raw_bytes, sha256, byte_length, format, origin, file_digest, locator) VALUES (?,?,?,?,?,?,?,?,?)",
                      [(str(uuid.uuid4()), r[columns.index('id')], b'@misc{x, title={t}}', uuid.uuid4().hex * 2, len(b'@misc{x, title={t}}'), 'bib', 'import-applied', uuid.uuid4().hex * 2, f'seed#{i}') for i, r in enumerate(rows)])
    settings = select(str(home / 'config.toml'), str(home / 'cat'), no_project_config=True)
    with connect(settings.catalog_path(), write=True) as c:
        for source_id, in c.execute('SELECT id FROM sources').fetchall():
            search_sqlite.refresh(c, sources.record(c, source_id))
    return settings


def test_record_loader_uses_indexes_not_scans(big_catalog):
    with connect(big_catalog.catalog_path()) as c:
        source_id = c.execute('SELECT id FROM sources ORDER BY rowid DESC LIMIT 1').fetchone()[0]
        with traced(c) as statements:
            started = time.perf_counter()
            sources.record(c, source_id)
            elapsed = time.perf_counter() - started
        for statement in statements:
            if 'FROM originals' in statement or 'FROM project_sources' in statement:
                plan = ' '.join(row[3] for row in c.execute('EXPLAIN QUERY PLAN ' + statement))
                assert 'SCAN originals' not in plan and 'SCAN project_sources' not in plan, (statement, plan)
    assert elapsed < 0.05


def test_search_refresh_never_scans_the_fts_table(big_catalog):
    with connect(big_catalog.catalog_path(), write=True) as c:
        source_id = c.execute('SELECT id FROM sources ORDER BY rowid DESC LIMIT 1').fetchone()[0]
        record = sources.record(c, source_id)
        with traced(c) as statements:
            started = time.perf_counter()
            search_sqlite.refresh(c, record)
            elapsed = time.perf_counter() - started
        assert not any('DELETE FROM search_projection WHERE source_id' in s for s in statements)
        assert any('search_rows' in s for s in statements)
        found = search_sqlite.matches(c, record['metadata']['title'])
        assert source_id in found
        rows = c.execute('SELECT count(*) FROM search_rows WHERE source_id=?', (source_id,)).fetchone()[0]
        assert rows == c.execute('SELECT count(*) FROM search_projection WHERE source_id=?', (source_id,)).fetchone()[0] > 0
        c.rollback()
    assert elapsed < 0.05


def test_bibliography_import_builds_the_title_plan_once(big_catalog, tmp_path):
    raw = b'\n\n'.join(f'@article{{scale{i}, title={{Scaling title {i}}}, author={{Example, Ada}}, year={{2021}}, journal={{J}}}}'.encode() for i in range(20))
    statements = []
    real_connect = importing.connect

    @contextmanager
    def tracing_connect(*args, **kwargs):
        with real_connect(*args, **kwargs) as connection:
            connection.set_trace_callback(statements.append)
            yield connection

    importing.connect = tracing_connect
    try:
        started = time.perf_counter()
        result = importing.run(big_catalog.catalog_path(), raw, str(tmp_path / 'scale.bib'), settings=big_catalog, origin='scale')
        elapsed = time.perf_counter() - started
    finally:
        importing.connect = real_connect
    assert result['counts'] == dict(applied=20, unchanged=0, conflict=0, invalid=0)
    title_scans = [s for s in statements if "json_extract(metadata_json,'$.title')" in s or "json_extract(metadata_json, '$.title')" in s]
    assert title_scans == [], title_scans
    plan_reads = [s for s in statements if s.strip().startswith('SELECT id,citation_key,metadata_json FROM sources')]
    assert len(plan_reads) == 1
    assert elapsed / 20 < 0.05


def test_import_list_reads_aggregates_not_records(big_catalog, tmp_path, monkeypatch):
    for index in range(30):
        raw = f'@article{{batch{index}, title={{Batch {index}}}, author={{Example, Ada}}, year={{2020}}, journal={{J}}}}'.encode()
        importing.run(big_catalog.catalog_path(), raw, str(tmp_path / f'b{index}.bib'), settings=big_catalog, origin=f'batch-{index}')

    def never(*_):
        raise AssertionError('import list loaded a full record')

    monkeypatch.setattr(sources, 'record', never)
    started = time.perf_counter()
    listed = importing.list_batches(big_catalog.catalog_path())
    elapsed = time.perf_counter() - started
    assert len(listed['items']) >= 30
    monkeypatch.undo()
    shown = importing.show(big_catalog.catalog_path(), listed['items'][0]['import_id'])
    assert shown['batch_revision'] == listed['items'][0]['batch_revision']
    assert shown['counts'] == listed['items'][0]['counts']
    assert elapsed < 0.5


def test_cite_from_import_uses_two_indexed_paths(big_catalog, tmp_path):
    catalog = big_catalog.catalog_path()
    raw = b'@article{cited1, title={Cited one}, author={Example, Ada}, year={2020}, journal={J}}\n@article{cited2, title={Cited two}, author={Example, Ada}, year={2020}, journal={J}}'
    importing.run(catalog, raw, str(tmp_path / 'cited.bib'), settings=big_catalog, origin='cited-origin')
    with connect(catalog, write=True) as c:
        # a legacy original: applied by this origin's batch but predating the import_id link, matched by digest and time window
        legacy_source = c.execute("SELECT id FROM sources WHERE citation_key='cited2'").fetchone()[0]
        digest = c.execute("SELECT file_digest FROM imports WHERE origin='cited-origin'").fetchone()[0]
        c.execute("INSERT INTO originals (id, source_id, raw_bytes, sha256, byte_length, format, origin, file_digest, locator, definitions_json) VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (str(uuid.uuid4()), legacy_source, b'@article{cited2, title={Cited two}}', uuid.uuid4().hex * 2, len(b'@article{cited2, title={Cited two}}'), 'bib', 'import-applied', digest, 'legacy#1', '{}'))
    projects.create(catalog, 'scaled', 'scaling test')
    started = time.perf_counter()
    result = projects.cite_import(catalog, 'scaled', 'cited-origin')
    elapsed = time.perf_counter() - started
    assert result['cited'] == 2
    with connect(catalog) as c:
        keys = sorted(row[0] for row in c.execute("SELECT s.citation_key FROM project_sources ps JOIN sources s ON s.id=ps.source_id JOIN projects p ON p.id=ps.project_id WHERE p.name='scaled'"))
    assert keys == ['cited1', 'cited2']
    assert elapsed < 0.5
