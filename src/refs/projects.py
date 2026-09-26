"""Cited-only project membership, without implicit file effects."""

import sqlite3
from pathlib import Path
from uuid import uuid4

from refs import logging as action_log
from refs import sources
from refs.catalog import changed, connect
from refs.results import RefError


def resolve(connection, reference: str) -> dict:
    rows = connection.execute("SELECT * FROM projects WHERE id=? OR name=?", (reference, reference)).fetchall()
    if len(rows) != 1:
        raise RefError("project_ambiguous" if rows else "project_missing", "Use one exact project name or ID")
    return dict(rows[0])


def create(catalog: Path, name: str, description: str, *, dry_run: bool = False) -> dict:
    if not name.strip():
        raise RefError("invalid_project", "Project name cannot be blank", 2)
    with connect(catalog, write=not dry_run) as connection:
        row = connection.execute("SELECT * FROM projects WHERE name=?", (name,)).fetchone()
        if row:
            if row["description"] != description:
                raise RefError("project_conflict", "Project exists with a different description")
            return dict(row) | {"unchanged": True}
        if dry_run:
            return dict(dry_run=True, name=name, description=description)
        project = dict(id=str(uuid4()), name=name, description=description, revision=1)
        action_log.log_mutation('project.create', {'id':project['id'],'name':name}, None, project)
        try:
            connection.execute("INSERT INTO projects VALUES (:id, :name, :description, :revision)", project)
        except sqlite3.IntegrityError as exc:
            if 'projects.name' in str(exc):
                raise RefError('project_conflict','Project name is already reserved') from exc
            raise
        changed(connection)
        return project


def cite(catalog: Path, project_ref: str, source_ref: str, *, dry_run: bool = False) -> dict:
    with connect(catalog, write=not dry_run) as connection:
        project = resolve(connection, project_ref)
        source_id = sources.resolve(connection, source_ref)
        source = connection.execute("SELECT state,citation_key FROM sources WHERE id=?", (source_id,)).fetchone()
        if source['state'] != "active":
            raise RefError("source_removed", "Removed sources cannot be cited")
        existing = connection.execute("SELECT 1 FROM project_sources WHERE project_id=? AND source_id=?", (project["id"], source_id)).fetchone()
        if not existing and not dry_run:
            action_log.log_mutation('project.cite', {'id':project['id'],'name':project['name'],'source_id':source_id},
                                    {'revision':project['revision'],'cited':False}, {'revision':project['revision']+1,'cited':True})
            connection.execute("INSERT INTO project_sources VALUES (?, ?, 1)", (project["id"], source_id))
            connection.execute("UPDATE projects SET revision=revision+1 WHERE id=?", (project["id"],))
            changed(connection)
        return dict(project_id=project["id"], project_name=project['name'], source_id=source_id, citation_key=source['citation_key'], cited=True,
                    unchanged=bool(existing), dry_run=dry_run)


def show(catalog: Path, reference: str | None = None) -> dict:
    with connect(catalog) as connection:
        if reference is None:
            return dict(items=[dict(row) for row in connection.execute('SELECT * FROM projects ORDER BY name')])
        project = resolve(connection, reference)
        records = [sources.record(connection, row[0]) for row in connection.execute('SELECT source_id FROM project_sources WHERE project_id=? AND cited=1 ORDER BY source_id', (project['id'],))]
        records.sort(key=lambda record: record['citation_key'])
        return project | dict(sources=[record for record in records if record['state'] == 'active'],
                              removed_sources=[record for record in records if record['state'] == 'removed'])


def cite_import(catalog: Path, project_ref: str, origin: str, *, dry_run=False) -> dict:
    with connect(catalog, write=not dry_run) as connection:
        project = resolve(connection, project_ref)
        if not connection.execute('SELECT 1 FROM imports WHERE origin=?', (origin,)).fetchone():
            raise RefError('import_origin_missing', 'Use the origin supplied to import, or its input path when no origin was supplied')
        # Older originals predate import_id. Creation time identifies their run;
        # a later unchanged import of the same bytes must not claim the source.
        # Two indexed paths, unioned in Python: the OR form of this join defeats every index and scales with sources times imports.
        candidates = {}
        by_batch = """SELECT s.id, s.citation_key, i.origin FROM sources s
            JOIN originals o ON o.source_id=s.id AND o.origin='import-applied'
            JOIN imports i ON i.id=json_extract(o.definitions_json,'$.import_id')
            WHERE s.state='active'"""
        by_digest = """SELECT s.id, s.citation_key, i.origin FROM sources s
            JOIN originals o ON o.source_id=s.id AND o.origin='import-applied' AND json_extract(o.definitions_json,'$.import_id') IS NULL
            JOIN imports i ON i.file_digest=o.file_digest AND i.applied>0 AND s.created_at>=i.started_at AND (i.finished_at IS NULL OR s.created_at<=i.finished_at)
            WHERE s.state='active'"""
        for statement in (by_batch, by_digest):
            for row in connection.execute(statement):
                candidates.setdefault((row['id'], row['citation_key']), set()).add(row['origin'])
        candidates = dict(sorted(candidates.items(), key=lambda item: item[0][1]))
        selected = []
        for (source_id, key), origins in candidates.items():
            if origin in origins:
                if len(origins)>1:
                    raise RefError('import_origin_ambiguous', f'Historical import runs overlap for {key}; cite that source individually')
                selected.append(source_id)
        existing = {row[0] for row in connection.execute('SELECT source_id FROM project_sources WHERE project_id=? AND cited=1', (project['id'],))}
        new = [source_id for source_id in selected if source_id not in existing]
        if new and not dry_run:
            action_log.log_mutation('project.cite', {'id':project['id'],'name':project['name']},
                                    {'revision':project['revision']}, {'revision':project['revision']+1},
                                    changes={'source_ids':{'old':[],'new':new}}, origin=origin)
            connection.executemany('INSERT INTO project_sources VALUES (?, ?, 1) ON CONFLICT(project_id,source_id) DO UPDATE SET cited=1', [(project['id'], source_id) for source_id in new])
            connection.execute('UPDATE projects SET revision=revision+1 WHERE id=?', (project['id'],))
            changed(connection)
        return dict(project_id=project['id'], project_name=project['name'], origin=origin, cited=len(new), already_cited=len(selected)-len(new), dry_run=dry_run)


def uncite(catalog: Path, project_ref: str, source_ref: str, *, dry_run: bool = False) -> dict:
    with connect(catalog, write=not dry_run) as connection:
        project = resolve(connection, project_ref)
        source_id = sources.resolve(connection, source_ref)
        citation_key = connection.execute('SELECT citation_key FROM sources WHERE id=?', (source_id,)).fetchone()[0]
        exists = bool(connection.execute('SELECT 1 FROM project_sources WHERE project_id=? AND source_id=?', (project['id'], source_id)).fetchone())
        if exists and not dry_run:
            action_log.log_mutation('project.uncite', {'id':project['id'],'name':project['name'],'source_id':source_id},
                                    {'revision':project['revision'],'cited':True}, {'revision':project['revision']+1,'cited':False})
            connection.execute('DELETE FROM project_sources WHERE project_id=? AND source_id=?', (project['id'], source_id))
            connection.execute('UPDATE projects SET revision=revision+1 WHERE id=?', (project['id'],))
            changed(connection)
        return dict(project_id=project['id'], project_name=project['name'], source_id=source_id, citation_key=citation_key, unchanged=not exists, dry_run=dry_run)
