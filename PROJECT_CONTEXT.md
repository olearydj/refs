# refs Context

refs retains sources gathered during research and agent-assisted writing in a reusable SQLite catalog. Slices 1 and 2 (capture, correction, search, cited-only projects, portable BibTeX export, linked or copied files, snapshot and restore; and the Zotero ingest, which brought 562 sources and 58 collections across on 2026-09-22) are built and in use; the owner's catalog is at `/Volumes/Casa/refs` with configuration in `~/.config/refs/config.toml`. Slice 3 (2026-09-24) organized the files: each source carries an optional `loc`, every managed file sits under `lib/<loc>`, `reorg` moves files by a verified copy-then-delete protocol with a journal, and the catalog is at schema 6 (schema 5 from slice 3; the 2026-09-25 performance batch added lookup indexes and a search side table). A tests pass (2026-09-24) established the [testing convention](docs/testing-convention.md) and the rehearsal and corpus harnesses under `tests/fixtures/real-trial/`. Human output is rendered as plain Rich tables per output class, and every mutation is logged as JSON lines at `cat/refs.log` before it takes effect. The record vocabulary is CSL's: 26 types are admitted through the registry, kinds such as `podcast` are names over type and genre (`list --kind podcast`, `add --kind`, `refs kinds`), and refusals for deferred types name the CSL type that would admit them (2026-09-26). Titles keep TeX math verbatim, non-Latin creator names fall back to a title-based key with a notice, and season words become CSL seasons (2026-09-26). Export has three profiles, each written for what its consumer prints: `csl-json-v1` for pandoc and Quarto (the identity mapping, with title protection as `nocase` spans), `portable-bibtex-v1` for classic BibTeX styles, `biblatex-v1` for pandoc and biber consumers that need a `.bib`; a project's `.refs.toml` names one target per profile its consumers need and `refs export` alone rewrites them all; a per-project title policy can preserve case; `refs summary` is the catalog at a glance. Seven projects, the owner's CV among them, are converted by the [conversion guide](docs/conversion-guide.md); sources can be linked with `update --link`, as a preprint is to its publication; refs is 0.9.4 (2026-09-29).

## Source Map

- [Docs index](docs/README.md): current scope, readiness, reading order, and open choices.
- [Vision](docs/vision.md): product purpose and enduring boundaries.
- [Accepted decisions](docs/behavior-decisions.md): scope of works, naming/title policies, initial capture, collections, and managed placement.
- [Slice 1 spec](specs/001-academic-catalog/spec.md) and [plan](specs/001-academic-catalog/plan.md): what is built, and the deferred-work ledger where the owner's use-list accumulates.
- [Conversion guide](docs/conversion-guide.md): moving a project's bibliography into the catalog and taking it back as an export; the register of converted projects; findings per project.
- [Architecture](docs/architecture.md): anticipated needs and architectural implications.
- [Workflow research](docs/workflow-research.md): local evidence with provenance and limitations.
- [Right-sizing](docs/right-sizing.md): the owner's scale, slice 1 budget, never-cut floor, and checkpoints that keep refs proportionate.

## Maintenance

Keep detailed decisions in their owning documents. Distinguish accepted requirements from recommendations and historical observations. This context file is an entry point, not a second specification or a pointer to a particular handoff.
