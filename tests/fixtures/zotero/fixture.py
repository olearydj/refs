"""Synthetic rows inserted into the unmodified Zotero 6.0.37 schema."""

import sqlite3
from pathlib import Path


def build(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    database = folder / "zotero.sqlite.bak"
    with sqlite3.connect(database) as c:
        c.executescript(Path(__file__).with_name("userdata.sql").read_text())
        c.executemany("INSERT INTO version VALUES (?,?)", [("userdata", 121), ("global", 28)])
        c.execute("INSERT INTO settings VALUES ('account','userID','123')")
        c.execute(
            "INSERT INTO libraries (libraryID,type,editable,filesEditable) VALUES (1,'user',1,1)"
        )
        types = [
            "journalArticle",
            "book",
            "bookSection",
            "patent",
            "presentation",
            "computerProgram",
            "attachment",
            "note",
            "annotation",
        ]
        c.executemany(
            "INSERT INTO itemTypes (itemTypeID,typeName) VALUES (?,?)", enumerate(types, 1)
        )
        fields = ["title", "date", "DOI", "ISBN", "extra", "citationKey", "publicationTitle", "url"]
        c.executemany("INSERT INTO fields (fieldID,fieldName) VALUES (?,?)", enumerate(fields, 1))
        roles = [
            "author",
            "editor",
            "translator",
            "contributor",
            "bookAuthor",
            "inventor",
            "presenter",
            "programmer",
            "seriesEditor",
        ]
        c.executemany("INSERT INTO creatorTypes VALUES (?,?)", enumerate(roles, 1))

        def item(i, kind, key):
            c.execute(
                "INSERT INTO items (itemID,itemTypeID,libraryID,key) VALUES (?,?,1,?)",
                (i, types.index(kind) + 1, key),
            )

        def field(i, name, value):
            c.execute("INSERT OR IGNORE INTO itemDataValues (value) VALUES (?)", (value,))
            c.execute(
                "INSERT INTO itemData VALUES (?,?,(SELECT valueID FROM itemDataValues WHERE value=?))",
                (i, fields.index(name) + 1, value),
            )

        for i, kind in enumerate(types[:6], 1):
            item(i, kind, f"ITEM{i:04}")
            field(i, "title", f"Synthetic {kind} Study")
            field(i, "date", "2020-05-04 May 4, 2020")
            field(i, "extra", f"Citation Key: extra{i}\n")
        field(1, "citationKey", "native1")
        field(1, "DOI", "10.5555/synthetic")
        field(1, "publicationTitle", "Synthetic Journal")
        c.execute(
            "UPDATE itemDataValues SET value=? WHERE value=?",
            (
                "Citation Key: extra1\narxiv: 2407.01502\ndoi: 10.5555/synthetic\npmid: 123\npmcid: PMC123\noclc: 456\nissn: 1234-5678\npublisher: Unmodeled Press",
                "Citation Key: extra1\n",
            ),
        )
        c.execute("DELETE FROM itemData WHERE itemID=6 AND fieldID=5")
        field(2, "ISBN", "978-0-123456-47-2")
        for n, (item_id, role, last, first, mode) in enumerate(
            [
                (1, "author", "van Example", "Alex", 0),
                (1, "author", "Second", "Zoe", 0),
                (2, "seriesEditor", "Series", "Sid", 0),
                (1, "editor", "Editor", "Eve", 0),
                (1, "translator", "Translator", "Tess", 0),
                (1, "contributor", "Research and Design", "", 1),
                (3, "bookAuthor", "Bookauthor", "Bea", 0),
                (4, "inventor", "Inventor", "Ira", 0),
                (5, "presenter", "Presenter", "Pat", 0),
                (6, "programmer", "Programmer", "Sam", 0),
            ],
            1,
        ):
            c.execute("INSERT INTO creators VALUES (?,?,?,?)", (n, first, last, mode))
            c.execute(
                "INSERT INTO itemCreators VALUES (?,?,?,?)", (item_id, n, roles.index(role) + 1, n)
            )
        for cid, name, parent, key in [
            (1, "Research", None, "COLL0001"),
            (2, "Methods", 1, "COLL0002"),
            (3, "Empty", None, "COLL0003"),
        ]:
            c.execute(
                "INSERT INTO collections (collectionID,collectionName,parentCollectionID,libraryID,key) VALUES (?,?,?,1,?)",
                (cid, name, parent, key),
            )
        c.executemany("INSERT INTO collectionItems VALUES (?,?,0)", [(1, 1), (2, 1), (2, 2)])
        c.execute("INSERT INTO tags VALUES (1,'legacy tag')")
        c.execute("INSERT INTO itemTags VALUES (1,1,0)")
        paths = [
            (10, 2, str(folder / "linked.pdf")),
            (11, 2, "attachments:relative.pdf"),
            (12, 0, "storage:stored.pdf"),
            (13, 3, ""),
        ]
        (folder / "linked.pdf").write_bytes(b"synthetic linked")
        (folder / "base").mkdir()
        (folder / "base/relative.pdf").write_bytes(b"synthetic relative")
        (folder / "storage/FILE0012").mkdir(parents=True)
        (folder / "storage/FILE0012/stored.pdf").write_bytes(b"synthetic stored")
        for i, mode, path in paths:
            item(i, "attachment", f"FILE{i:04}")
            c.execute(
                "INSERT INTO itemAttachments (itemID,parentItemID,linkMode,contentType,path) VALUES (?,1,?,?,?)",
                (i, mode, "application/pdf", path),
            )
            if mode == 3:
                field(i, "url", "https://example.org/attachment")
        item(20, "note", "NOTE0020")
        c.execute("INSERT INTO itemNotes VALUES (20,1,'<p>Synthetic child note</p>','')")
        c.execute(
            "INSERT INTO itemNotes VALUES (10,1,'<h1>Contents</h1><ul><li>outline</li></ul>','')"
        )
        item(21, "annotation", "ANNO0021")
        c.execute(
            "INSERT INTO itemAnnotations (itemID,parentItemID,type,sortIndex,position,isExternal) VALUES (21,10,1,'0','{}',1)"
        )
        c.execute("INSERT INTO relationPredicates VALUES (1,'dc:relation')")
        c.execute(
            "INSERT INTO itemRelations VALUES (1,1,'http://zotero.org/users/123/items/ITEM0002')"
        )
        item(30, "book", "TRASH030")
        c.execute("INSERT INTO deletedItems (itemID) VALUES (30)")
    with sqlite3.connect(folder / "better-bibtex.sqlite") as bbt:
        bbt.execute("CREATE TABLE citationkey (itemID INTEGER, citationKey TEXT)")
        bbt.executemany("INSERT INTO citationkey VALUES (?,?)", [(1, "legacy1"), (6, "legacy6")])
    return database
