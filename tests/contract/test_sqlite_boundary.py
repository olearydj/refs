"""Existing SQLite-only domain statements are an inventory, not a pattern to extend."""

import ast
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).parents[2]/'src/refs'
SQLITE_ONLY=re.compile(r'json_extract|insert\s+or\s+ignore|on\s+conflict|\browid\b|\binstr\s*\(|\bpragma\b|\bexecutescript\b',re.I)
ALLOWED=[
    ('importing.py','INSERT OR IGNORE INTO originals (id,source_id,raw_bytes,sha256,byte_length,format,origin,file_digest,locator,definitions_json) VALUES (?,?,?,?,?,?,?,?,?,?)'),
    ('importing.py','SELECT * FROM import_entries WHERE import_id=? ORDER BY rowid'),
    ('importing.py','SELECT id,origin,started_at,revision,applied,unchanged,conflict,invalid FROM imports ORDER BY started_at DESC,rowid DESC'),
    ('importing.py','SELECT e.id, e.source_id, s.revision FROM import_entries e LEFT JOIN sources s ON s.id=e.source_id WHERE e.import_id=? ORDER BY e.rowid'),
    ('importing.py','INSERT OR IGNORE INTO source_collections VALUES (?,?)'),
    ('importing.py','INSERT OR IGNORE INTO source_relations VALUES (?,?,?,?)'),
    ('importing.py','INSERT OR IGNORE INTO origin_identities VALUES (?,?,?,?,?)'),
    ('importing.py',"SELECT id, citation_key FROM sources WHERE lower(json_extract(metadata_json,'$.title'))=lower(?)"),
    ('sources.py',"SELECT id, citation_key FROM sources WHERE lower(json_extract(metadata_json, '$.title'))=lower(?)"),
    ('bibliography.py','INSERT INTO export_targets VALUES (?,?,?,?,NULL) ON CONFLICT(destination) DO UPDATE SET project_id=excluded.project_id, profile_fingerprint=excluded.profile_fingerprint, baseline_digest=excluded.baseline_digest, pending_digest=NULL'),
    ('bibliography.py','INSERT INTO export_targets VALUES (?, ?, ?, NULL, ?) ON CONFLICT(destination) DO UPDATE SET project_id=excluded.project_id, profile_fingerprint=excluded.profile_fingerprint, baseline_digest=NULL, pending_digest=excluded.pending_digest'),
    ('bibliography.py',"INSERT OR IGNORE INTO originals (id, raw_bytes, sha256, byte_length, format, origin, file_digest, locator) VALUES (?, ?, ?, ?, 'bib', 'export-overwrite', ?, ?)"),
    ('projects.py',"SELECT s.id, s.citation_key, i.origin FROM sources s JOIN originals o ON o.source_id=s.id AND o.origin='import-applied' JOIN imports i ON i.id=json_extract(o.definitions_json,'$.import_id') WHERE s.state='active'"),
    ('projects.py',"SELECT s.id, s.citation_key, i.origin FROM sources s JOIN originals o ON o.source_id=s.id AND o.origin='import-applied' AND json_extract(o.definitions_json,'$.import_id') IS NULL JOIN imports i ON i.file_digest=o.file_digest AND i.applied>0 AND s.created_at>=i.started_at AND (i.finished_at IS NULL OR s.created_at<=i.finished_at) WHERE s.state='active'"),
    ('projects.py','INSERT INTO project_sources VALUES (?, ?, 1) ON CONFLICT(project_id,source_id) DO UPDATE SET cited=1'),
]


def test_domain_sqlite_syntax_stays_at_recorded_statements():
    found=[]
    for path in ROOT.rglob('*.py'):
        if path.name in ('catalog.py','recovery.py') or 'adapters' in path.parts:
            continue
        covered=set()
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and SQLITE_ONLY.search(node.value):
                found.append((str(path.relative_to(ROOT)),' '.join(node.value.split())))
                covered.update(range(node.lineno,node.end_lineno+1))
            if isinstance(node,ast.Attribute) and node.attr=='executescript':
                found.append((str(path.relative_to(ROOT)),'call:executescript'))
                covered.add(node.lineno)
        assert all(number in covered for number,line in enumerate(path.read_text().splitlines(),1) if SQLITE_ONLY.search(line)),path
    assert Counter(found)==Counter(ALLOWED)
