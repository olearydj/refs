"""One read-only picture of the catalog: counts, the three hierarchies, projects and their targets."""

import json
from collections import Counter
from pathlib import Path

from refs import files, kinds, resources
from refs.bibliography import PROFILES
from refs.catalog import connect
from refs.config import Settings


def overview(settings: Settings) -> dict:
    catalog = settings.catalog_path()
    profiles = {files.digest(profile.encode()): profile for profile in PROFILES}
    with connect(catalog) as connection:
        meta = dict(connection.execute('SELECT catalog_id, schema_version, revision FROM catalog_meta').fetchone())
        active, removed, types, kind_counts, unassigned, locs = 0, 0, Counter(), Counter(), Counter(), Counter()
        for row in connection.execute('SELECT id, state, loc, metadata_json, details_json FROM sources'):
            if row['state'] != 'active':
                removed += 1
                continue
            active += 1
            metadata = json.loads(row['metadata_json'])
            record = dict(metadata=metadata, native_type=json.loads(row['details_json']).get('native_type'))
            types[metadata.get('type', 'document')] += 1
            kind = kinds.identify(record)
            if kind:
                kind_counts[kind] += 1
            elif kinds.warnings(record):
                unassigned[metadata['type']] += 1
            if row['loc']:
                locs[row['loc']] += 1
        active_ids = {row[0] for row in connection.execute("SELECT id FROM sources WHERE state='active'")}
        with_files, managed, linked, unfiled = set(), 0, 0, 0
        for row in connection.execute('SELECT source_id, root, relative FROM resources'):
            if row['source_id'] not in active_ids:
                continue
            with_files.add(row['source_id'])
            if row['root'] == 'library':
                managed += 1
                unfiled += str(row['relative']).startswith('unfiled/')
            else:
                linked += 1
        projects = []
        for project in connection.execute('SELECT id, name, description FROM projects ORDER BY name'):
            cited = connection.execute("SELECT count(*) FROM project_sources ps JOIN sources s ON s.id=ps.source_id WHERE ps.project_id=? AND ps.cited=1 AND s.state='active'", (project['id'],)).fetchone()[0]
            targets = []
            for target in connection.execute('SELECT destination, profile_fingerprint, baseline_digest FROM export_targets WHERE project_id=? ORDER BY destination', (project['id'],)):
                current = files.current_digest(Path(target['destination']))
                state = 'missing' if current is None else 'pending' if target['baseline_digest'] is None else 'current' if current == target['baseline_digest'] else 'outside_edit'
                targets.append(dict(destination=target['destination'], profile=profiles.get(target['profile_fingerprint'], 'unknown'), state=state))
            projects.append(dict(name=project['name'], description=project['description'], cited=cited, targets=targets))
        batches = connection.execute('SELECT count(*) FROM imports').fetchone()[0]
        last = connection.execute('SELECT origin, started_at, applied, unchanged, conflict, invalid FROM imports ORDER BY started_at DESC LIMIT 1').fetchone()
        open_conflicts = sum(1 for row in connection.execute("SELECT decisions_json FROM import_entries WHERE status='conflict'") if not any(d['action'] == 'dismissed' for d in json.loads(row[0] or '[]')))
        collections = [dict(path=row['path'], count=row[1]) for row in connection.execute(
            "SELECT c.path, (SELECT count(*) FROM source_collections sc JOIN sources s ON s.id=sc.source_id WHERE sc.collection_id=c.id AND s.state='active') FROM collections c ORDER BY c.path")]
    placement = resources.check(settings)['items']
    return dict(
        catalog=dict(id=meta['catalog_id'], schema_version=meta['schema_version'], revision=meta['revision'], path=str(catalog)),
        sources=dict(active=active, removed=removed, with_files=len(with_files), without_files=active - len(with_files)),
        files=dict(managed=managed, linked=linked, unfiled=unfiled,
                   missing=sum(1 for item in placement if item.get('status') == 'missing'),
                   unrecorded=sum(1 for item in placement if item.get('kind') == 'unrecorded')),
        types=dict(sorted(types.items(), key=lambda item: (-item[1], item[0]))),
        kinds=dict(assigned=dict(sorted(kind_counts.items())), unassigned=dict(sorted(unassigned.items()))),
        locs=[dict(loc=loc, count=count) for loc, count in sorted(locs.items())],
        collections=collections,
        projects=projects,
        imports=dict(batches=batches, open_conflicts=open_conflicts,
                     last=dict(origin=last['origin'], started=last['started_at'], counts={name: last[name] for name in ('applied', 'unchanged', 'conflict', 'invalid')}) if last else None),
    )
