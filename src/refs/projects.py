"""Cited-only project membership, without implicit file effects."""

from pathlib import Path
from uuid import uuid4

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
        connection.execute("INSERT INTO projects VALUES (:id, :name, :description, :revision)", project)
        changed(connection)
        return project


def cite(catalog: Path, project_ref: str, source_ref: str, *, dry_run: bool = False) -> dict:
    with connect(catalog, write=not dry_run) as connection:
        project = resolve(connection, project_ref)
        source_id = sources.resolve(connection, source_ref)
        if connection.execute("SELECT state FROM sources WHERE id=?", (source_id,)).fetchone()[0] != "active":
            raise RefError("source_removed", "Removed sources cannot be cited")
        existing = connection.execute("SELECT 1 FROM project_sources WHERE project_id=? AND source_id=?", (project["id"], source_id)).fetchone()
        if not existing and not dry_run:
            connection.execute("INSERT INTO project_sources VALUES (?, ?, 1)", (project["id"], source_id))
            connection.execute("UPDATE projects SET revision=revision+1 WHERE id=?", (project["id"],))
            changed(connection)
        return dict(project_id=project["id"], source_id=source_id, cited=True,
                    unchanged=bool(existing), dry_run=dry_run)


def show(catalog: Path, reference: str | None = None) -> dict:
    with connect(catalog) as connection:
        if reference is None:
            return dict(items=[dict(row) for row in connection.execute('SELECT * FROM projects ORDER BY name')])
        project = resolve(connection, reference)
        records = [sources.record(connection, row[0]) for row in connection.execute('SELECT source_id FROM project_sources WHERE project_id=? AND cited=1 ORDER BY source_id', (project['id'],))]
        return project | dict(sources=[record for record in records if record['state'] == 'active'],
                              removed_sources=[record for record in records if record['state'] == 'removed'])


def uncite(catalog: Path, project_ref: str, source_ref: str, *, dry_run: bool = False) -> dict:
    with connect(catalog, write=not dry_run) as connection:
        project = resolve(connection, project_ref)
        source_id = sources.resolve(connection, source_ref)
        exists = bool(connection.execute('SELECT 1 FROM project_sources WHERE project_id=? AND source_id=?', (project['id'], source_id)).fetchone())
        if exists and not dry_run:
            connection.execute('DELETE FROM project_sources WHERE project_id=? AND source_id=?', (project['id'], source_id))
            connection.execute('UPDATE projects SET revision=revision+1 WHERE id=?', (project['id'],))
            changed(connection)
        return dict(project_id=project['id'], source_id=source_id, unchanged=not exists, dry_run=dry_run)
