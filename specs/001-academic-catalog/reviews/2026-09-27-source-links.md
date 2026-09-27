# Unnamed source links

The owner approved an unnamed link between a preprint and its publication, with named relationships deferred. This branch exposes the existing `source_relations` table through `update REF --link OTHER` and `update REF --unlink OTHER`, plus linked-source display in `show`. It adds no command, table, migration, dependency or export field.

The options accept an exact ID or citation key and stand alone from metadata edits. They use update’s existing optional `--if-revision` guard for REF and `--dry-run` preview. A link is symmetric: show returns each linked catalog source once, with ID, key, title and state, even if Zotero supplied reciprocal rows. Human output prints the key and title and marks removed sources. Unresolved external Zotero endpoints remain stored; they are not yet catalog sources to display.

A real link/unlink logs `source.link` or `source.unlink` before changing the catalog, recording both endpoint revisions and the old/new relationship state. Both source revisions advance in one transaction, so a stale guard on either endpoint catches a subsequent edit. Duplicate links, including reverse-direction repeats, and absent unlinks are no-ops. Self-links and mixed metadata/link invocations refuse. Unlink removes all stored rows connecting the pair, including reciprocal imported rows, without touching other relations. Tombstoning retains links, and rekeying changes only the displayed key.

This is deliberately an update option because it edits an existing source’s catalog relationships. A separate command group or relationship taxonomy would add surface without serving this incident. Link data is read-only in the public source-record envelope and excluded from source-create, patches and all bibliography profiles.

## Verification

The focused CLI tests exercise symmetric display, human output, no-op bytes, both dry-run paths, stale revisions at either endpoint, invalid invocations, durable mutation logs, log-failure refusal, transaction rollback after an injected second-endpoint failure, reciprocal Zotero rows, retained unresolved rows, removal/rekeying and byte-identical exports in all three profiles.

The full suite with required rendering tools passed all **1,119 tests** in 40.65 seconds. Ruff on src/tests, source type checking and whitespace checks pass. The full-suite log is `/private/tmp/refs-source-links-full-final.log`. Initial integration failures identified the missing public-envelope field and a SQLite-specific domain query; both were corrected without weakening the existing tests or adding SQLite syntax allowances.

A direct read-only check of the owner’s catalog found six Zotero relation rows representing three pairs across five sources. Every pair appeared from both endpoints without duplicates, and the catalog database hash remained unchanged. Details are in `/private/tmp/refs-source-links-live-check.json`. All mutation tests used disposable catalogs. No live relation was added or removed, no export changed, and nothing is merged.
