"""Slice 2 acceptance gate: compare a refs catalog with the Zotero library it was imported from.

Read-only against every input. Reports counts and keys, never note or abstract text.

Usage:
  uv run --locked python tests/fixtures/real-trial/zotero_gate.py CATALOG_DIR [--zotero ~/Zotero/zotero.sqlite] [--json]

Against an empty catalog it reports every Zotero item as missing; that is the baseline
the importer must drive to zero. Expected differences (D2 outlines skipped, annotations
not imported, URL-only attachments not resources) are not counted as failures.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

EXTRA_IDENTIFIERS = {"arxiv", "doi", "pmid", "pmcid", "oclc", "issn"}


def ro(path):
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def zotero_expected(z):
    q = lambda sql, *a: z.execute(sql, a).fetchall()
    items = {}
    for item_id, key, type_name in q(
        "SELECT i.itemID, i.key, t.typeName FROM items i JOIN itemTypes t USING(itemTypeID) "
        "WHERE t.typeName NOT IN ('attachment','note','annotation') AND i.itemID NOT IN (SELECT itemID FROM deletedItems)"
    ):
        items[item_id] = dict(item_key=key, type=type_name, creators=[], tags=set(), collections=set(),
                              files=set(), child_notes=0, citation_key=None, extra_ids=set())
    for item_id, ctype, last, first in q(
        "SELECT ic.itemID, ct.creatorType, c.lastName, c.firstName FROM itemCreators ic "
        "JOIN creators c USING(creatorID) JOIN creatorTypes ct USING(creatorTypeID) ORDER BY ic.itemID, ic.orderIndex"
    ):
        if item_id in items:
            items[item_id]["creators"].append((ctype, last or "", first or ""))
    for item_id, name in q("SELECT it.itemID, t.name FROM itemTags it JOIN tags t USING(tagID)"):
        if item_id in items:
            items[item_id]["tags"].add(name)
    coll_names = {cid: (name, parent) for cid, name, parent in q("SELECT collectionID, collectionName, parentCollectionID FROM collections")}

    def coll_path(cid):
        name, parent = coll_names[cid]
        return (coll_path(parent) + "/" if parent else "") + name

    for cid, item_id in q("SELECT collectionID, itemID FROM collectionItems"):
        if item_id in items:
            items[item_id]["collections"].add(coll_path(cid))
    for parent, path in q("SELECT parentItemID, path FROM itemAttachments WHERE parentItemID IS NOT NULL"):
        if parent in items and path:
            items[parent]["files"].add(path)
    for parent, in q("SELECT n.parentItemID FROM itemNotes n JOIN items i USING(itemID) JOIN itemTypes t USING(itemTypeID) WHERE t.typeName='note' AND n.parentItemID IS NOT NULL"):
        if parent in items:
            items[parent]["child_notes"] += 1
    for item_id, value in q(
        "SELECT d.itemID, v.value FROM itemData d JOIN fields f USING(fieldID) JOIN itemDataValues v USING(valueID) WHERE f.fieldName='extra'"
    ):
        if item_id not in items:
            continue
        for line in value.split("\n"):
            m = re.match(r"^\s*([A-Za-z][\w .-]*?):\s*(.+?)\s*$", line)
            if not m:
                continue
            label = m.group(1).strip().lower()
            if label == "citation key":
                items[item_id]["citation_key"] = m.group(2)
            elif label in EXTRA_IDENTIFIERS:
                items[item_id]["extra_ids"].add((label, m.group(2)))
    for item_id, value in q(
        "SELECT d.itemID, v.value FROM itemData d JOIN fields f USING(fieldID) JOIN itemDataValues v USING(valueID) WHERE f.fieldName='citationKey'"
    ):
        if item_id in items:
            items[item_id]["citation_key"] = value  # native field wins over Extra
    collections = {coll_path(cid) for cid in coll_names}
    return items, collections


def refs_actual(c):
    q = lambda sql, *a: c.execute(sql, a).fetchall()
    by_item_key = {}
    for item_key, source_id in q("SELECT item_key, source_id FROM origin_identities WHERE namespace='zotero'"):
        by_item_key[item_key] = source_id
    sources = {}
    for sid, ckey, meta, details, state in q("SELECT id, citation_key, metadata_json, details_json, state FROM sources"):
        m = json.loads(meta)
        d = json.loads(details or "{}")
        nt = d.get("native_type") or {}
        ext = d.get("extensions") or {}
        creators = [(role, n.get("family") or n.get("literal") or "", n.get("given") or "")
                    for role in ("author", "editor", "translator", "container-author", "collection-editor")
                    for n in m.get(role, [])]
        ids = {(k.lower(), v) for k, v in m.items() if k in ("DOI", "PMID", "PMCID", "ISSN")}
        for k, v in (ext.get("identifiers") or {}).items():
            ids.add((k.lower(), v))
        sources[sid] = dict(citation_key=ckey, type=m.get("type"), native=nt.get("value"), creators=creators,
                            tags=set(d.get("legacy_tags") or []), files=set(), collections=set(), state=state, ids=ids)
    tables = {r[0] for r in q("SELECT name FROM sqlite_master WHERE type='table'")}
    if "source_collections" in tables:
        for sid, path in q(
            "SELECT sc.source_id, c.path FROM source_collections sc JOIN collections c ON c.id=sc.collection_id"
        ):
            if sid in sources:
                sources[sid]["collections"].add(path)
    for sid, path, root, relative in q("SELECT source_id, path, root, relative FROM resources"):
        if sid in sources:
            sources[sid]["files"].add(path or f"{root}:{relative}")
    return by_item_key, sources


def compare(expected, by_item_key, sources):
    findings = []
    missing = [e["item_key"] for e in expected.values() if e["item_key"] not in by_item_key]
    if missing:
        findings.append(("missing_items", len(missing), missing[:10]))
    for e in expected.values():
        sid = by_item_key.get(e["item_key"])
        if not sid:
            continue
        s = sources[sid]
        if e["citation_key"] and s["citation_key"] != e["citation_key"]:
            findings.append(("key_changed", e["item_key"], e["citation_key"], s["citation_key"]))
        if s["native"] != e["type"]:
            findings.append(("native_type", e["item_key"], e["type"], s["native"]))
        ez = [(c[1], c[2]) for c in e["creators"]]
        sz = [(c[1], c[2]) for c in s["creators"]]
        if ez != sz:
            findings.append(("creators", e["item_key"], len(ez), len(sz)))
        if e["tags"] != s["tags"]:
            findings.append(("tags", e["item_key"], sorted(e["tags"] - s["tags"])[:3], sorted(s["tags"] - e["tags"])[:3]))
        if e["collections"] != s["collections"]:
            findings.append(("collections", e["item_key"], sorted(e["collections"] - s["collections"]), sorted(s["collections"] - e["collections"])))
        want = set()
        for p in e["files"]:
            if p.startswith("storage:"):
                want.add("storage")  # resolved beneath zotero storage/<itemKey>; presence checked loosely
            elif p.startswith("/"):
                want.add(p)
        have_abs = {f for f in s["files"] if f.startswith("/")}
        if (want - {"storage"}) - have_abs:
            findings.append(("files_missing", e["item_key"], sorted((want - {"storage"}) - have_abs)[:3]))
        if "storage" in want and not any("storage" in f for f in s["files"]) and not have_abs:
            findings.append(("stored_file_missing", e["item_key"]))
        for label, value in e["extra_ids"]:
            if (label, value) not in s["ids"]:
                findings.append(("extra_identifier_missing", e["item_key"], label))
        if s["state"] != "active":
            findings.append(("not_active", e["item_key"], s["state"]))
    extra_sources = len(sources) - len(by_item_key)
    return findings, missing, extra_sources


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catalog")
    ap.add_argument("--zotero", default=os.path.expanduser("~/Zotero/zotero.sqlite"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    z = ro(a.zotero)
    c = ro(Path(a.catalog) / "catalog.sqlite")
    expected, expected_colls = zotero_expected(z)
    by_item_key, sources = refs_actual(c)
    findings, missing, extra = compare(expected, by_item_key, sources)
    summary = dict(
        zotero_items=len(expected), zotero_collections=len(expected_colls),
        refs_sources=len(sources), refs_bound_to_zotero=len(by_item_key), refs_sources_not_from_zotero=extra,
        missing_items=len(missing), findings=len(findings),
        by_kind={k: sum(1 for f in findings if f[0] == k) for k in {f[0] for f in findings}},
    )
    if a.json:
        print(json.dumps(dict(summary=summary, findings=findings[:200]), indent=1, default=list))
    else:
        for k, v in summary.items():
            print(f"{k}: {v}")
        for f in findings[:40]:
            print("  ", *f)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
