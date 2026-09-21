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
