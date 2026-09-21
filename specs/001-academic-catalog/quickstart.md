# Slice 1 Acceptance Walkthrough

**Planned checks, not executed implementation evidence.** Use disposable synthetic inputs and explicit test paths; no live Zotero/catalog/PDF/manuscript changes. The [file contract](contracts/files-and-recovery.md#snapshot-and-documented-restore) owns restore safety.

## One installed smoke workflow

1. Install the locked package in its supported Python environment. Set an explicit temporary --config and --catalog for every invocation. Initialize with a disposable library; inspect paths and config show.
2. Inspect the four schemas. Preview/add a refs record, a CSL record and a Bib entry; include incomplete metadata and protected spelling. Show the retained values/origins/key. Update using --set and a patch under revisions; prove a stale update fails.
3. Import a mixed .bib with one valid entry and one conflict. Save its report, inspect preserved originals, re-run without duplicate sources/resources and settle a value conflict using update. Nothing silently overwrites a correction.
4. Search/list the records. Create a project, cite two sources, uncite one, and show the selected set. Metadata/project changes alone produce no bibliography.
5. Link a file in place; copy another into Unfiled. Check rename-by-default and --keep-name, show/check/open selection, then unlink the association without deleting bytes. A destination collision leaves both existing files unchanged.
6. Export to a new target, repeat byte-identically, and exercise import-digest adoption of an existing file with --adopt --overwrite. Outside edits block by default. Four-class failures report all affected entries without changing target bytes; --allow-unknown-mappings does not waive known blocking losses.
7. Remove/reactivate a source under revision guards, retaining its identity/key and external bytes. Snapshot, then perform the separate-home restore below.

## Focused checks beside the smoke

Keep one two-process key-allocation test. Use focused fixtures for parser defects, type-scoped aliases, names/particles/corporate “ and ”, dates, protection, keys, current-value clearing, no-overwrite imports, copied-file metadata and source changes, crash boundaries, invalid configuration and corrupt snapshots. Test portable rendering with Pandoc citeproc, Biber and classic BibTeX/elsarticle-num, asserting meaningful authors/dates/publication/edition/spelling, not just resolved keys. Record tool/style versions and limitations.

No four-process matrix, 10,000-source performance gate, plugin proof, per-entry resume, stored waiver or saved export projection belongs to this slice.

## Separate-home restore proof

Follow the documented procedure: verify hashes/schema/integrity, restore into an empty second home with separate config, open it with list/show/project show, and compare identities, keys, original hashes, corrections, selections and resource inventory. Missing roots are reported without file changes. Try a corrupt snapshot and nonempty destination; both fail safely. Demonstrate the procedure with the installed implementation and record exact commands/results before declaring slice 1 complete.

## Owner's real-paper gate

After these checks, the owner chooses one real paper for capture-to-export use with its actual consumer. Obtain task-specific authorization before replacing a live bibliography or migrating files. Render with the catalog unavailable, and record what was missing or unused. No slice 2 specification work begins before this trial. Whole-library migration remains separate.
