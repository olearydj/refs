ALTER TABLE catalog_meta RENAME TO catalog_meta_v3;
CREATE TABLE catalog_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    catalog_id TEXT NOT NULL UNIQUE,
    schema_version INTEGER NOT NULL CHECK (schema_version = 4),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0)
);
INSERT INTO catalog_meta SELECT singleton, catalog_id, 4, revision FROM catalog_meta_v3;
DROP TABLE catalog_meta_v3;
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
