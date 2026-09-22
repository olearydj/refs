# Zotero Input Contract

## Zotero input (slice 2)

`tools/zotero_extract/` is a versioned, one-time migration script outside the installed package. It reads Zotero SQLite read-only, preferably the maintained `.bak`, and accepts userdata schema 121. The observed route is Zotero 6.0.37, global schema 28 and Better BibTeX 7.0.0. Unsupported layouts require another tested extractor. Archive a dated, consistent Zotero data directory outside the catalog before cutover; whole databases are never stored in refs.

The directory contains UTF-8 `items/<itemKey>.json` files in published Zotero API v3 item shape, `collections.json` as an array of API v3 collection objects, and `manifest.json`. The manifest records input format/version, API version 3, Zotero version, userdata/global schema versions, extractor version, original data directory and linked-attachment base path. Its `library_uri` is derived from the source identity as `users/<id>` or `users/local/<key>`, never from the extraction directory. Legacy table keys, when available, are recorded by item key in manifest `legacy_keys`.

Admission validates the manifest, item keys, library identity, parents and collection references before applying dependent records. Unsupported versions, malformed records and unresolved references receive explicit diagnostics. Non-deleted regular items become sources; children attach only to identified parents. Trash is reported, never resurrected. Standalone children remain preserved with an association diagnostic. Preserve exact per-item JSON and collection/manifest evidence; report skipped content separately from usable records.

Identity is the pair of library URI and item key under namespace `zotero`. Key precedence is native `citationKey`, Extra `Citation Key:`, then manifest legacy keys. Preserve all evidence. The [records contract](records.md) governs Extra, binding and corrections.

Absolute linked-file paths remain absolute. Base-relative `attachments:` paths resolve against the manifest base path. Stored `storage:` paths resolve beneath the original data directory's `storage/<attachmentItemKey>/`, never the extraction or archive directory. Missing bases/files are reported without guessed paths or movement. URL-only attachments become context, not resources. Child notes become inert searchable context with origin `import`; annotations and attachment outlines are skipped under FR-023. Related endpoints retain their Zotero identity; their pairs are stored without a general relationship editor.
