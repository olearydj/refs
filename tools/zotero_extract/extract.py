"""One-time Zotero 6 userdata-121 extractor; not a maintained SQLite adapter."""

import argparse
import json
import sqlite3
from pathlib import Path

VERSION = "1"
LINK_MODES = {0: "imported_file", 1: "imported_url", 2: "linked_file", 3: "linked_url"}


def extract(
    database: Path,
    output: Path,
    data_dir: Path,
    base_path: Path | None = None,
    legacy: Path | None = None,
):
    if output.exists():
        raise ValueError("Choose a new extraction directory")
    with sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True) as c:
        c.execute("PRAGMA query_only=ON")
        c.execute("BEGIN")
        versions = dict(c.execute("SELECT schema,version FROM version"))
        if versions.get("userdata") != 121:
            raise ValueError("Extractor requires userdata schema 121")
        settings = {
            (a, b): str(v) for a, b, v in c.execute("SELECT setting,key,value FROM settings")
        }
        user = settings.get(("account", "userID"))
        local = settings.get(("account", "localUserKey"))
        if not user and not local:
            raise ValueError("Library identity is missing")
        uri = "users/" + user if user else "users/local/" + str(local)
        libraries = [
            row[0] for row in c.execute("SELECT libraryID FROM libraries WHERE type='user'")
        ]
        if len(libraries) != 1:
            raise ValueError("Select a database with one personal library")
        if c.execute("SELECT 1 FROM items WHERE libraryID!=? LIMIT 1", (libraries[0],)).fetchone():
            raise ValueError("Nonempty additional libraries require a separately tested extractor")
        trashed = {row[0] for row in c.execute("SELECT itemID FROM deletedItems")}
        records = {
            i: dict(
                key=key,
                version=version,
                data=dict(
                    key=key, version=version, itemType=kind, dateAdded=added, dateModified=modified
                ),
            )
            for i, key, version, kind, added, modified in c.execute(
                "SELECT i.itemID,i.key,i.version,t.typeName,i.dateAdded,i.dateModified FROM items i JOIN itemTypes t USING(itemTypeID) WHERE libraryID=?",
                (libraries[0],),
            )
            if i not in trashed
        }
        for i, name, value in c.execute(
            "SELECT d.itemID,f.fieldName,v.value FROM itemData d JOIN fields f USING(fieldID) JOIN itemDataValues v USING(valueID)"
        ):
            if i in records:
                records[i]["data"][name] = value
        for i, role, last, first, literal in c.execute(
            "SELECT ic.itemID,ct.creatorType,c.lastName,c.firstName,c.fieldMode FROM itemCreators ic JOIN creators c USING(creatorID) JOIN creatorTypes ct USING(creatorTypeID) ORDER BY ic.itemID,ic.orderIndex"
        ):
            if i in records:
                name = (
                    {"name": last}
                    if literal
                    else {"lastName": last or "", "firstName": first or ""}
                )
                records[i]["data"].setdefault("creators", []).append(dict(creatorType=role, **name))
        for i, tag, kind in c.execute(
            "SELECT it.itemID,t.name,it.type FROM itemTags it JOIN tags t USING(tagID)"
        ):
            if i in records:
                records[i]["data"].setdefault("tags", []).append(dict(tag=tag, type=kind))
        collections = {
            i: dict(
                key=key,
                version=v,
                data=dict(key=key, version=v, name=name, parentCollection=parent),
            )
            for i, key, v, name, parent in c.execute(
                "SELECT collectionID,key,version,collectionName,parentCollectionID FROM collections WHERE collectionID NOT IN (SELECT collectionID FROM deletedCollections)"
            )
        }
        for value in collections.values():
            parent = value["data"]["parentCollection"]
            if parent and parent not in collections:
                raise ValueError("Missing collection parent")
            value["data"]["parentCollection"] = collections[parent]["key"] if parent else False
        for cid, i in c.execute("SELECT collectionID,itemID FROM collectionItems"):
            if i in records and cid in collections:
                records[i]["data"].setdefault("collections", []).append(collections[cid]["key"])
        for i, parent, note in c.execute("SELECT itemID,parentItemID,note FROM itemNotes"):
            if i in records:
                records[i]["data"]["note"] = note
                if parent:
                    if parent not in records:
                        raise ValueError("Missing note parent")
                    records[i]["data"]["parentItem"] = records[parent]["key"]
        for i, parent, mode, content, path in c.execute(
            "SELECT itemID,parentItemID,linkMode,contentType,path FROM itemAttachments"
        ):
            if i not in records:
                continue
            value = records[i]["data"]
            value.update(linkMode=LINK_MODES[mode], contentType=content or "")
            if parent:
                if parent not in records:
                    raise ValueError("Missing attachment parent")
                value["parentItem"] = records[parent]["key"]
            if mode in (0, 1):
                value["filename"] = (path or "").removeprefix("storage:")
            elif mode == 2:
                value["path"] = path
        annotations = 0
        for i, parent in c.execute("SELECT itemID,parentItemID FROM itemAnnotations"):
            if i in records:
                if parent not in records:
                    raise ValueError("Missing annotation parent")
                records[i]["data"]["parentItem"] = records[parent]["key"]
                annotations += 1
        for i, predicate, target in c.execute(
            "SELECT r.itemID,p.predicate,r.object FROM itemRelations r JOIN relationPredicates p USING(predicateID)"
        ):
            if i in records:
                records[i]["data"].setdefault("relations", {}).setdefault(predicate, []).append(
                    target
                )
        legacy_keys = {}
        if legacy:
            with sqlite3.connect(legacy.resolve().as_uri() + "?mode=ro", uri=True) as b:
                legacy_keys = {
                    records[i]["key"]: key
                    for i, key in b.execute("SELECT itemID,citationKey FROM citationkey")
                    if i in records
                }
        manifest = dict(
            format="refs-zotero-input",
            version=1,
            api_version=3,
            library_uri=uri,
            zotero_version="6.0.37",
            userdata_version=121,
            global_version=versions.get("global"),
            extractor_version=VERSION,
            data_directory=str(data_dir.resolve()),
            base_path=str(base_path.resolve()) if base_path else None,
            legacy_keys=legacy_keys,
            skipped=dict(trash=len(trashed), annotations=annotations),
        )
        output.mkdir(parents=True)
        (output / "items").mkdir()
        for value in records.values():
            (output / "items" / f"{value['key']}.json").write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n"
            )
        (output / "collections.json").write_text(
            json.dumps(list(collections.values()), ensure_ascii=False, indent=2) + "\n"
        )
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        return dict(items=len(records), collections=len(collections), output=str(output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("database", "output", "data-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--base-path", type=Path)
    parser.add_argument("--legacy-db", type=Path)
    args = parser.parse_args()
    try:
        result = extract(args.database, args.output, args.data_dir, args.base_path, args.legacy_db)
    except (ValueError, sqlite3.Error, OSError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
