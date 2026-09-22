# One-time Zotero extractor

This migration script supports the observed Zotero 6.0.37 userdata schema 121 only. It is not part of the installed refs package and does not promise compatibility with other layouts. It reads a consistent SQLite snapshot in a read-only transaction and never edits the database or attachments.

```sh
uv run --locked python tools/zotero_extract/extract.py --database "$SNAPSHOT" --output "$NEW_DIRECTORY" --data-dir "$ORIGINAL_DATA_DIRECTORY" --base-path "$LINKED_ATTACHMENT_BASE" --legacy-db "$LEGACY_BBT_DATABASE"
```

Use a closed, consistent database or Zotero's maintained `.bak`. The original data directory controls stored attachment resolution; do not substitute an archive path. Base path and legacy database are optional; native and Extra keys take precedence later. Missing identity, unsupported schemas and nonempty additional libraries fail explicitly. Output must not exist. A failed output is incomplete until manifest.json exists; retain it for inspection and retry into another new directory. Archive the full Zotero data directory separately before real cutover. Only T051 authorizes that real operation.

The schema-121 multipart date prefix is emitted as `meta.parsedDate`, while the user-facing text remains in `data.date`, matching [Zotero 6 item serialization](https://github.com/zotero/zotero/blob/6.0.37/chrome/content/zotero/xpcom/data/item.js) and its [pinned date utility](https://github.com/zotero/utilities/blob/cccf1235a318c259345fc623d5e9d6770ba19df7/date.js). Zero month/day components retain partial precision; the importer does not supply January 1. The archived database retains the internal storage string.
