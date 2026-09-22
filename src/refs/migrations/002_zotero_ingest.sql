ALTER TABLE catalog_meta RENAME TO catalog_meta_v1;
CREATE TABLE catalog_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    catalog_id TEXT NOT NULL UNIQUE,
    schema_version INTEGER NOT NULL CHECK (schema_version = 2),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0)
);
INSERT INTO catalog_meta SELECT singleton, catalog_id, 2, revision FROM catalog_meta_v1;
DROP TABLE catalog_meta_v1;
ALTER TABLE imports ADD COLUMN revision INTEGER NOT NULL DEFAULT 1;
CREATE TABLE import_entries (
    id TEXT PRIMARY KEY,
    import_id TEXT NOT NULL REFERENCES imports(id),
    locator TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('applied','unchanged','conflict','invalid')),
    candidates_json TEXT NOT NULL DEFAULT '[]',
    conflicts_json TEXT NOT NULL DEFAULT '[]',
    source_id TEXT REFERENCES sources(id),
    source_revision INTEGER,
    payload_json TEXT NOT NULL,
    decisions_json TEXT NOT NULL DEFAULT '[]',
    UNIQUE (import_id, locator)
);
CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    library_uri TEXT NOT NULL,
    item_key TEXT NOT NULL,
    parent TEXT REFERENCES collections(id),
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
    UNIQUE (library_uri, item_key)
);
CREATE TABLE source_collections (
    source_id TEXT NOT NULL REFERENCES sources(id),
    collection_id TEXT NOT NULL REFERENCES collections(id),
    PRIMARY KEY (source_id, collection_id)
);
CREATE TABLE source_relations (
    source_id TEXT NOT NULL REFERENCES sources(id),
    target_uri TEXT NOT NULL,
    target_id TEXT REFERENCES sources(id),
    origin TEXT NOT NULL,
    PRIMARY KEY (source_id, target_uri)
);
