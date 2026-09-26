UPDATE catalog_meta SET schema_version = 6;
CREATE INDEX originals_source_id ON originals(source_id);
CREATE INDEX project_sources_source_id ON project_sources(source_id);
CREATE TABLE search_rows (
    rowid INTEGER PRIMARY KEY,
    source_id TEXT NOT NULL
);
CREATE INDEX search_rows_source_id ON search_rows(source_id);
INSERT INTO search_rows (rowid, source_id) SELECT rowid, source_id FROM search_projection;
