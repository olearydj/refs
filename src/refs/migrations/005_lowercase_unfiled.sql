ALTER TABLE catalog_meta RENAME TO catalog_meta_v4;
CREATE TABLE catalog_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    catalog_id TEXT NOT NULL UNIQUE,
    schema_version INTEGER NOT NULL CHECK (schema_version = 5),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0)
);
INSERT INTO catalog_meta SELECT singleton, catalog_id, 5, revision FROM catalog_meta_v4;
DROP TABLE catalog_meta_v4;
UPDATE sources SET loc='unfiled' WHERE loc='Unfiled';
UPDATE resources
SET locator=replace(replace(locator, '"relative": "Unfiled/', '"relative": "unfiled/'),
                                     '"relative":"Unfiled/', '"relative":"unfiled/'),
    relative='unfiled/' || substr(relative,9)
WHERE root='library' AND substr(relative,1,8)='Unfiled/';
