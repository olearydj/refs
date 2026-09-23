ALTER TABLE catalog_meta RENAME TO catalog_meta_v2;
CREATE TABLE catalog_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    catalog_id TEXT NOT NULL UNIQUE,
    schema_version INTEGER NOT NULL CHECK (schema_version = 3),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0)
);
INSERT INTO catalog_meta SELECT singleton, catalog_id, 3, revision FROM catalog_meta_v2;
DROP TABLE catalog_meta_v2;
ALTER TABLE sources ADD COLUMN loc TEXT;
