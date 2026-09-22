CREATE TABLE catalog_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    catalog_id TEXT NOT NULL UNIQUE,
    schema_version INTEGER NOT NULL CHECK (schema_version = 1),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0)
);

CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    citation_key TEXT NOT NULL UNIQUE COLLATE BINARY,
    state TEXT NOT NULL DEFAULT 'active' CHECK (state IN ('active', 'removed')),
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL CHECK (json_valid(metadata_json)),
    details_json TEXT NOT NULL CHECK (json_valid(details_json)),
    corrected_fields_json TEXT NOT NULL DEFAULT '[]' CHECK (json_valid(corrected_fields_json)),
    key_provenance_json TEXT NOT NULL CHECK (json_valid(key_provenance_json))
);

CREATE TABLE originals (
    id TEXT PRIMARY KEY,
    source_id TEXT REFERENCES sources(id),
    raw_bytes BLOB NOT NULL,
    sha256 TEXT NOT NULL,
    byte_length INTEGER NOT NULL CHECK (byte_length = length(raw_bytes)),
    format TEXT NOT NULL,
    origin TEXT NOT NULL,
    file_digest TEXT NOT NULL,
    locator TEXT NOT NULL,
    definitions_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE (sha256, origin, locator)
);
CREATE TRIGGER originals_no_update BEFORE UPDATE ON originals BEGIN
    SELECT RAISE(ABORT, 'Original evidence is immutable');
END;
CREATE TRIGGER originals_no_delete BEFORE DELETE ON originals BEGIN
    SELECT RAISE(ABORT, 'Original evidence is immutable');
END;
CREATE TABLE origin_identities (
    namespace TEXT NOT NULL,
    library_uri TEXT NOT NULL,
    item_key TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(id),
    input_fingerprint TEXT NOT NULL,
    PRIMARY KEY (namespace, library_uri, item_key)
);

CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (length(trim(name)) > 0),
    description TEXT NOT NULL DEFAULT '',
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0)
);
CREATE TABLE project_sources (
    project_id TEXT NOT NULL REFERENCES projects(id),
    source_id TEXT NOT NULL REFERENCES sources(id),
    cited INTEGER NOT NULL DEFAULT 1 CHECK (cited IN (0, 1)),
    PRIMARY KEY (project_id, source_id)
);

CREATE TABLE export_targets (
    destination TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    profile_fingerprint TEXT NOT NULL,
    baseline_digest TEXT,
    pending_digest TEXT
);

CREATE VIRTUAL TABLE search_projection USING fts5(source_id UNINDEXED, field UNINDEXED, origin UNINDEXED, text, tokenize='unicode61');

CREATE TABLE imports (
    id TEXT PRIMARY KEY,
    origin TEXT NOT NULL,
    file_digest TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    applied INTEGER NOT NULL DEFAULT 0,
    unchanged INTEGER NOT NULL DEFAULT 0,
    conflict INTEGER NOT NULL DEFAULT 0,
    invalid INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE resources (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(id),
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
    locator TEXT NOT NULL,
    path TEXT,
    root TEXT,
    relative TEXT,
    label TEXT,
    media_type TEXT,
    digest TEXT,
    copied_from_json TEXT,
    CHECK ((path IS NOT NULL AND root IS NULL AND relative IS NULL) OR (path IS NULL AND root IS NOT NULL AND relative IS NOT NULL)),
    UNIQUE (source_id, locator)
);
