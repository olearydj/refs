# Slice 1 Validation Guide

**Status:** executable acceptance design for the implementation phase; commands and fixtures below are not yet implemented. Use synthetic/public fixtures and disposable paths. Live manuscript replacement, Zotero migration and file movement need their own explicit authorization.

## Setup and first workflow

Implementation creates the package/lock and fixtures named here. Run uv sync --locked, Ruff, the exact-pinned ty, and pytest contract/integration checks. Verify SQLite capabilities and record Python, SQLite, OS/filesystem, package lock and policy versions.

```bash
refs_trial_root=$(mktemp -d)
uv run --locked refs --config "$refs_trial_root/config.toml" --catalog "$refs_trial_root/cat" --no-project-config init --library-root "$refs_trial_root/lib"
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config --json add --format refs --input tests/fixtures/public/source.json --request-id capture-example
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config project create paper-x
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config project cite paper-x smith-2024-turingTrap
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config export --project paper-x --output "$refs_trial_root/references.bib" --profile portable-bibtex-v1
```

The source fixture supplies author Smith, year 2024 and short title The Turing Trap so the shown key is deterministic. Repeat capture/export; compare IDs and output bytes. Update with a returned revision, then reject a stale revision without changes. Search exact key/identifier and text from title, creator, abstract and context. Collection filters are excluded until slice 2. A removed source can be explicitly reactivated with the same ID/key.

## Cross-route and export gates

For every promoted mapping, exercise refs' actual bibtexparser adapter, agent input and (using the synthetic extractor input adapter) Zotero mapping without requiring live migration. Compare canonical facts, preserve exact originals, edit and clear each modeled field, then export and re-import. Re-import unchanged documented fallbacks using recorded projection evidence and assert no false type conflicts or duplicate sources. Changed projected values and key-only lookalikes must reconcile. A new catalog without projection evidence must report the generic imported type honestly.

Include all 14 design-probe cases and the missing discriminators: free-text/parsedDate disagreement, partial/literal dates, both patent number kinds and priority date, assignee distinct from inventor, journal series versus collection title, numeric/descriptive editions, identifiers, corporate “ and ”, explicit particles, title-term/whole-title protection, accent-command braces, type changes and deliberate clearing. Run the parser corruption fixtures from the preserved audit through the actual adapter. Do not present Pandoc parsing as that test.

Render portable output using Pandoc/APA and IEEE, Biber, and classic BibTeX with elsarticle-num. Keep golden expectations for authors, issued dates, journal/institution, editions, source identity and protected spelling. Case-only keys must block portable export. Known fallbacks warn; actual enumerated meaning loss blocks; unknowns block unless explicitly overridden for the run. Waivers expire on loss/revision/profile changes. All blocked cases report every affected source and leave destination bytes unchanged.

Exercise new-path export, adoption of an existing reconciled bibliography, repeat no-op, external edit conflict, explicit overwrite preservation and crash recovery. No metadata or membership mutation may write a bibliography. The real-paper trial remains a separately authorized release gate.

## Copy intake and failure checks

```bash
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config --json resource intake smith-2024-turingTrap --path tests/fixtures/public/sample.pdf --intake copy --dry-run
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config --json resource intake smith-2024-turingTrap --path tests/fixtures/public/sample.pdf --intake copy --request-id copy-example
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config --json resource check --verify
```

Expect lib/Unfiled/sample.pdf, unchanged basename, matching bytes, a named-root locator and the original still present. Slice 1 move must return unsupported_in_slice. Crash at every prepared/staged/published/catalog-committed boundary. Verify no overwrite even for equal-byte unrelated destinations, source-change detection, metadata warnings, permission failures, absent roots, nonce handling and retry after config repair. A temporary local same-volume fixture does not certify real cross-volume behavior; execute a separate synthetic macOS cross-volume fixture when that storage is available.

## Snapshot and demonstrated restore

```bash
uv run --locked refs --config "$refs_trial_root/config.toml" --no-project-config backup --output "$refs_trial_root/snapshot"
uv run --locked python tools/restore_snapshot.py --input "$refs_trial_root/snapshot" --catalog "$refs_trial_root/restored-cat" --config "$refs_trial_root/restored.toml"
uv run --locked refs --config "$refs_trial_root/restored.toml" --no-project-config --json show smith-2024-turingTrap
uv run --locked refs --config "$refs_trial_root/restored.toml" --no-project-config --json resource check --verify
```

The documented slice 1 helper validates manifest/hash/schema/integrity, refuses an existing destination, creates the separate catalog and config, and marks it ready only when verified. It performs no external file effect or operation resumption. Compare all saved identities, keys, canonical metadata, originals, provenance, projections/waivers, projects/selections and resource inventory. Snapshot again with an unresolved copy operation; confirm restoration reports it without touching shared files. Missing/corrupt members and incompatible schemas must fail. The later full restore CLI/bundle format is not required for this proof.

Record explicitly that external bytes are excluded. Do not run both restored and original catalogs as active writers against shared output/library paths. Full logical export, collections, move and Zotero cutover belong to later slices.

## Readiness evidence

Record the complete slice 1 test result, consumer/style versions, corruption/interruption results, restore comparison and the 100-query/10,000-source/30,000-link performance measurement. Distinguish synthetic passing checks from actual manuscript acceptance. The metadata design examples and audit annotation evidence do not substitute for these implementation results.
