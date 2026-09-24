"""Read-only Zotero fidelity gate. All paths are explicit; no private defaults."""

import argparse
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

ROLES = {
    "author": "author",
    "editor": "editor",
    "translator": "translator",
    "contributor": "contributor",
    "bookAuthor": "container-author",
    "seriesEditor": "collection-editor",
    "inventor": "author",
    "presenter": "author",
    "programmer": "author",
}
SCHEMES = {"arxiv", "doi", "pmid", "pmcid", "oclc", "issn"}


def ro(path):
    return closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True))


def normalized_identifier(scheme, value):
    # Independent gate oracle for the owner's normalization decision.
    if scheme == 'doi':
        return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value.strip(), flags=re.I).lower()
    if scheme == 'arxiv':
        value = re.sub(r'^arxiv:\s*', '', value.strip(), flags=re.I)
        return re.sub(r'\s*\[[^]]+\]$', '', value).strip()
    return value


def expected_issued(stored):
    """Independent SQL-date oracle; no refs adapters or models are imported."""
    if not stored:
        return None
    native = re.fullmatch(r'(\d{4}-\d{2}-\d{2}) (.+)', stored)
    raw, parsed = (native[2],native[1]) if native and not re.fullmatch(r'\d{2}:\d{2}(?::\d{2})?',native[2]) else (stored,None)
    interval = None
    if match := re.fullmatch(r'(\d{4})\s*[-–—/]\s*(\d{4})',raw):
        interval = [[int(year)] for year in match.groups()]
    elif match := re.fullmatch(r'(\d{1,2})[-–—](\d{1,2})\s+([A-Za-z]+)\.?\s+(\d{4})',raw):
        from datetime import datetime
        try:
            interval = []
            for day in match.groups()[:2]:
                format = '%d %b %Y' if len(match[3])==3 else '%d %B %Y'
                endpoint=datetime.strptime(f'{day} {match[3]} {match[4]}',format)
                interval.append([endpoint.year,endpoint.month,endpoint.day])
        except ValueError:
            return {'literal':raw}
    elif match := re.fullmatch(r'(\d{4}(?:-\d{1,2}){0,2})\s*(?:/|–|—| to | - )\s*(\d{4}(?:-\d{1,2}){0,2})',raw):
        interval = [[int(n) for n in endpoint.split('-')] for endpoint in match.groups()]
    if interval:
        if interval[0]>interval[1] or any(not valid_parts(part) for part in interval):
            return {'literal':raw}
        return {'date-parts':interval}
    simple = re.fullmatch(r'\d{4}(?:-\d{1,2}){0,2}(?:[ T]\d{2}:\d{2}.*)?|\d{4}/\d{1,2}(?:/\d{1,2})?|\d{1,2}/\d{4}|\d{1,2}/\d{1,2}/\d{2,4}',raw)
    if (not simple and re.search(r'[-–—/]|\b(?:to|through|until)\b',raw,re.I)) or re.search(r'\b(?:circa|about|before|after)\b|[?~]',raw,re.I):
        return {'literal':raw}
    explicit = re.fullmatch(r'\d{4}(?:-\d{2}){0,2}',raw)
    candidate = raw if explicit else parsed or raw
    candidate = re.sub(r'[ T]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?$','',candidate)
    if re.fullmatch(r'\d{4}(?:-\d{2}){0,2}',candidate):
        parts = [int(n) for n in candidate.split('-')]
        while len(parts)>1 and parts[-1]==0:
            parts.pop()
        if valid_parts(parts):
            return {'date-parts':[parts]}
    return {'literal':raw}


def valid_parts(parts):
    from datetime import date
    try:
        date(*(parts+[1]*(3-len(parts))))
        return True
    except ValueError:
        return False


def expected(database, base_path=None, legacy=None):
    with ro(database) as c:
        settings = {
            (a, b): str(v) for a, b, v in c.execute("SELECT setting,key,value FROM settings")
        }
        user = settings.get(("account", "userID"))
        local = settings.get(("account", "localUserKey"))
        if not user and not local:
            raise ValueError("Zotero library identity is missing")
        uri = "users/" + user if user else "users/local/" + str(local)
        fields = {}
        for i, k, v in c.execute(
            "SELECT d.itemID,f.fieldName,v.value FROM itemData d JOIN fields f USING(fieldID) JOIN itemDataValues v USING(valueID)"
        ):
            fields.setdefault(i, {})[k] = v
        collections = {
            i: (key, name, parent)
            for i, key, name, parent in c.execute(
                "SELECT collectionID,key,collectionName,parentCollectionID FROM collections WHERE collectionID NOT IN (SELECT collectionID FROM deletedCollections)"
            )
        }

        def path(i, seen=()):
            if i in seen:
                raise ValueError("Collection cycle")
            _, name, parent = collections[i]
            return path(parent, (*seen, i)) + "/" + name if parent else name

        paths = {i: path(i) for i in collections}
        result = {}
        for i, key, kind in c.execute(
            "SELECT i.itemID,i.key,t.typeName FROM items i JOIN itemTypes t USING(itemTypeID) WHERE i.libraryID IN (SELECT libraryID FROM libraries WHERE type='user') AND i.itemID NOT IN (SELECT itemID FROM deletedItems) AND t.typeName NOT IN ('note','annotation','attachment')"
        ):
            f = fields.get(i, {})
            extra = {}
            for line in f.get("extra", "").splitlines():
                if ":" in line:
                    label, value = line.split(":", 1)
                    extra[label.strip().lower()] = value.strip()
            names = []
            for role, last, first, literal in c.execute(
                "SELECT ct.creatorType,cr.lastName,cr.firstName,cr.fieldMode FROM itemCreators ic JOIN creators cr USING(creatorID) JOIN creatorTypes ct USING(creatorTypeID) WHERE ic.itemID=? ORDER BY ic.orderIndex",
                (i,),
            ):
                names.append((role, last or "", first or "", bool(literal)))
            files = []
            urls = []
            for child, childkey, mode, locator in c.execute(
                "SELECT a.itemID,i.key,a.linkMode,a.path FROM itemAttachments a JOIN items i USING(itemID) WHERE a.parentItemID=? AND a.itemID NOT IN (SELECT itemID FROM deletedItems)",
                (i,),
            ):
                if mode == 3:
                    urls.append(fields.get(child, {}).get("url", ""))
                    continue
                if locator.startswith("storage:"):
                    resolved = Path(database).parent / "storage" / childkey / locator[8:]
                elif locator.startswith("attachments:"):
                    if base_path is None:
                        raise ValueError("Supply --base-path for relative attachments")
                    resolved = Path(base_path) / locator[12:]
                else:
                    resolved = Path(locator)
                files.append(str(resolved.resolve()))
            notes = [
                n
                for (n,) in c.execute(
                    "SELECT n.note FROM itemNotes n JOIN items i USING(itemID) JOIN itemTypes t USING(itemTypeID) WHERE n.parentItemID=? AND t.typeName='note'",
                    (i,),
                )
            ]
            result[key] = dict(
                key=f.get("citationKey") or extra.get("citation key") or (legacy or {}).get(i),
                native=kind,
                issued=expected_issued(f.get('issueDate') if kind=='patent' and f.get('issueDate') else f.get('date')),
                names=names,
                relations={target.removeprefix('http://zotero.org/').removeprefix('https://zotero.org/') for (target,) in c.execute("SELECT r.object FROM itemRelations r JOIN relationPredicates p USING(predicateID) WHERE r.itemID=? AND p.predicate='dc:relation'", (i,))},
                tags={
                    r[0]
                    for r in c.execute(
                        "SELECT t.name FROM itemTags it JOIN tags t USING(tagID) WHERE it.itemID=?",
                        (i,),
                    )
                },
                collections={
                    paths[r[0]]
                    for r in c.execute(
                        "SELECT collectionID FROM collectionItems WHERE itemID=?", (i,)
                    )
                    if r[0] in paths
                },
                files=set(files),
                urls=urls,
                notes=notes,
                ids={(k, normalized_identifier(k,v)) for k, v in extra.items() if k in SCHEMES},
            )
        return uri, result, set(paths.values())


def compare(catalog, database, base_path=None, legacy=None):
    uri, wanted, collections = expected(database, base_path, legacy)
    findings = []
    with ro(database) as z:
        structure = set(z.execute("SELECT c.key,c.collectionName,p.key FROM collections c LEFT JOIN collections p ON p.collectionID=c.parentCollectionID WHERE c.collectionID NOT IN (SELECT collectionID FROM deletedCollections)"))
        skipped = dict(trash=z.execute('SELECT count(*) FROM deletedItems').fetchone()[0],annotations=z.execute('SELECT count(*) FROM itemAnnotations').fetchone()[0],attachment_outlines=z.execute('SELECT count(*) FROM itemNotes n JOIN itemAttachments a USING(itemID) WHERE length(n.note)>0').fetchone()[0])
    with ro(Path(catalog) / "catalog.sqlite") as c:
        bindings = {
            key: sid
            for key, sid in c.execute(
                "SELECT item_key,source_id FROM origin_identities WHERE namespace='zotero' AND library_uri=?",
                (uri,),
            )
        }
        tables = {row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        actual_collections = (
            {
                row[0]
                for row in c.execute("SELECT path FROM collections WHERE library_uri=?", (uri,))
            }
            if "collections" in tables
            else set()
        )
        actual_structure = set(c.execute('SELECT v.item_key,v.name,p.item_key FROM collections v LEFT JOIN collections p ON p.id=v.parent WHERE v.library_uri=?',(uri,))) if 'collections' in tables else set()
        if actual_structure != structure:
            findings.append(dict(kind='collection_structure'))
        if actual_collections != collections:
            findings.append(
                dict(
                    kind="collection_inventory",
                    missing=sorted(collections - actual_collections),
                    extra=sorted(actual_collections - collections),
                )
            )
        if set(bindings)-set(wanted):
            findings.append(dict(kind='unexpected_bindings',keys=sorted(set(bindings)-set(wanted))))
        for key, e in wanted.items():
            if key not in bindings:
                findings.append(dict(kind="missing_item", key=key))
                continue
            sid = bindings[key]
            ckey, meta, details, state = c.execute(
                "SELECT citation_key,metadata_json,details_json,state FROM sources WHERE id=?",
                (sid,),
            ).fetchone()
            m, d = json.loads(meta), json.loads(details)

            def check(kind, valid):
                if not valid:
                    findings.append(dict(kind=kind, key=key))

            check("citation_key", not e["key"] or ckey == e["key"])
            check("native_type", d.get("native_type", {}).get("value") == e["native"])
            check("active", state == "active")
            check("issued", m.get("issued") == e["issued"])
            expected_names = {}
            for role, last, first, literal in e["names"]:
                expected_names.setdefault(ROLES.get(role, role), []).append(
                    {"literal": last}
                    if literal
                    else {k: v for k, v in [("family", last), ("given", first)] if v}
                )
            for role, names in expected_names.items():
                check("creators_" + role, m.get(role) == names)
            related = {row[0] for row in c.execute('SELECT target_uri FROM source_relations WHERE source_id=?',(sid,))} if 'source_relations' in tables else set()
            check('relations',related == e['relations'])
            for target, target_id in c.execute('SELECT target_uri,target_id FROM source_relations WHERE source_id=?',(sid,)) if 'source_relations' in tables else []:
                target_uri, _, target_key = target.rpartition('/items/')
                expected_id = bindings.get(target_key) if target_uri == uri else None
                if expected_id:
                    check('related_endpoint',target_id == expected_id)
            check("tags", set(d.get("legacy_tags", [])) == e["tags"])
            membership = (
                {
                    r[0]
                    for r in c.execute(
                        "SELECT c.path FROM source_collections sc JOIN collections c ON c.id=sc.collection_id WHERE sc.source_id=?",
                        (sid,),
                    )
                }
                if "source_collections" in tables
                else set()
            )
            check("memberships", membership == e["collections"])
            actual_files = {
                r[0] for r in c.execute("SELECT path FROM resources WHERE source_id=?", (sid,))
            }
            check(
                "files", actual_files == e["files"] and all(Path(p).is_file() for p in e["files"])
            )
            contexts = d.get("context", [])
            for note in e["notes"]:
                import html
                import re

                text = html.unescape(re.sub("<[^>]+>", " ", note))
                check(
                    "child_note",
                    any(
                        " ".join(x["text"].split()) == " ".join(text.split())
                        and x["origin"] == "import"
                        for x in contexts
                    ),
                )
            for url in e["urls"]:
                check("url_context", any(url in x["text"] for x in contexts))
            ids = {k.lower(): v for k, v in m.items() if k in ("DOI", "PMID", "PMCID", "ISSN")}
            ids.update(d.get("extensions", {}).get("identifiers", {}))
            for scheme, value in e["ids"]:
                check("identifier_" + scheme, ids.get(scheme) == value)
        summary = dict(
            zotero_items=len(wanted),
            zotero_collections=len(collections),
            refs_bound_to_zotero=len(bindings),
            missing_items=len(set(wanted) - bindings.keys()),
            findings=len(findings),
            skipped=skipped,
        )
    return dict(summary=summary, findings=findings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog")
    parser.add_argument("--zotero", required=True)
    parser.add_argument("--base-path")
    parser.add_argument("--legacy")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    keys = {}
    if args.legacy:
        with ro(args.legacy) as c:
            keys = dict(c.execute("SELECT itemID,citationKey FROM citationkey"))
    result = compare(args.catalog, args.zotero, args.base_path, keys)
    print(
        json.dumps(result, indent=2)
        if args.json
        else "\n".join(f"{k}: {v}" for k, v in result["summary"].items())
    )
    return bool(result["findings"])


if __name__ == "__main__":
    raise SystemExit(main())
