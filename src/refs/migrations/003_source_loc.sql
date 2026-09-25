UPDATE catalog_meta SET schema_version = 3;
ALTER TABLE sources ADD COLUMN loc TEXT;
