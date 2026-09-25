# refs Context

refs retains sources gathered during research and agent-assisted writing in a reusable SQLite catalog. Slices 1 and 2 (capture, correction, search, cited-only projects, portable BibTeX export, linked or copied files, snapshot and restore; and the Zotero ingest, which brought 562 sources and 58 collections across on 2026-09-22) are built and in use; the owner's catalog is at `/Volumes/Casa/refs` with configuration in `~/.config/refs/config.toml`. Slice 3 (2026-09-24) organized the files: each source carries an optional `loc`, every managed file sits under `lib/<loc>`, `reorg` moves files by a verified copy-then-delete protocol with a journal, and the catalog is at schema 5. A tests pass (2026-09-24) established the [testing convention](docs/testing-convention.md) and the rehearsal and corpus harnesses under `tests/fixtures/real-trial/`. Human output is rendered as plain Rich tables per output class, and every mutation is logged as JSON lines at `cat/refs.log` before it takes effect.

## Source Map

- [Docs index](docs/README.md): current scope, readiness, reading order, and open choices.
- [Vision](docs/vision.md): product purpose and enduring boundaries.
- [Accepted decisions](docs/behavior-decisions.md): naming/title policies, initial capture, collections, and managed placement.
- [Slice 1 spec](specs/001-academic-catalog/spec.md) and [plan](specs/001-academic-catalog/plan.md): what is built, and the deferred-work ledger where the owner's use-list accumulates.
- [Architecture](docs/architecture.md): anticipated needs and architectural implications.
- [Workflow research](docs/workflow-research.md): local evidence with provenance and limitations.
- [Right-sizing](docs/right-sizing.md): the owner's scale, slice 1 budget, never-cut floor, and checkpoints that keep refs proportionate.

## Maintenance

Keep detailed decisions in their owning documents. Distinguish accepted requirements from recommendations and historical observations. This context file is an entry point, not a second specification or a pointer to a particular handoff.
