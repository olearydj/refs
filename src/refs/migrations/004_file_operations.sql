UPDATE catalog_meta SET schema_version = 4;
CREATE TABLE file_operations (
    id TEXT PRIMARY KEY,
    -- Historical ID survives resource unlink; operation creation validates it.
    resource_id TEXT NOT NULL,
    old_path TEXT NOT NULL,
    new_path TEXT NOT NULL,
    old_name TEXT NOT NULL,
    new_name TEXT NOT NULL,
    staging_path TEXT NOT NULL,
    original_identity TEXT,
    destination_identity TEXT,
    staging_identity TEXT,
    digest TEXT,
    source_revision INTEGER,
    resource_revision INTEGER,
    loc TEXT,
    state TEXT NOT NULL CHECK (state IN ('staged','published','recorded','removed','failed')),
    last_state TEXT CHECK (last_state IN ('staged','published','recorded','removed')),
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
