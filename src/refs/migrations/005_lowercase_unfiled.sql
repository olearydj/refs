UPDATE catalog_meta SET schema_version = 5;
UPDATE sources SET loc='unfiled' WHERE loc='Unfiled';
UPDATE resources
SET locator=replace(replace(locator, '"relative": "Unfiled/', '"relative": "unfiled/'),
                                     '"relative":"Unfiled/', '"relative":"unfiled/'),
    relative='unfiled/' || substr(relative,9)
WHERE root='library' AND substr(relative,1,8)='Unfiled/';
