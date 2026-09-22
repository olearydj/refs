# Slice 1 Acceptance Walkthrough

T001–T020 are implemented. The US1 and US2 demonstration uses synthetic inputs and a fresh temporary configuration, catalog and library. It does not access the owner's catalog, Zotero data, PDFs or manuscript bibliographies.

## Run the demonstration

The walkthrough lives in [scripts/demo.sh](../../scripts/demo.sh). It is also the single installed end-to-end test, so its examples and assertions run together. From the repository root:

```sh
scripts/demo.sh
```

Use `scripts/demo.sh --help` for its execution modes. The script narrates capture, correction, retrieval, project selection and explicit bibliography export. It checks stale revisions, retained originals, removal and reactivation, repeat export, outside-edit refusal, a documented export fallback and a blocking loss. Every expected failure has an asserted exit code and JSON diagnostic.

## Verification

```sh
uv sync --locked
uv run --locked pytest
uv run --locked ruff check .
uv run --locked ty check src/refs
scripts/demo.sh --smoke
```

Focused tests cover strict records, naming, one two-process key-allocation case, transactionally updated search, correction markers, case-sensitive keys, export assessment and interrupted publication. The database has eight logical tables, including the derived search projection; SQLite's FTS shadow tables are internal. There is one initial migration, exercised only in disposable catalogs.

## Rendering evidence, 2026-09-21

All three consumers ran against `tests/fixtures/rendering/sources.json` through the actual serializer. The fixtures are a journal article, a second-edition book, a corporate-authored standard and a doctoral thesis. Assertions inspect rendered authors, issued years, journal, publisher, edition, institution, standard number and protected Python spelling. These checks establish those fixture results, not exhaustive style equivalence for every supported type and value. Unassessed mappings still block unless explicitly overridden for that invocation.

| Consumer | Style | Result |
| --- | --- | --- |
| Pandoc 3.11 with citeproc | Preserved APA Style 7th edition CSL | Passed |
| Biber 2.21 with LaTeX | biblatex 3.21, authoryear, dated 2025/07/10 | Passed |
| BibTeX 0.99e, TeX Live 2026, with LaTeX | elsarticle-num 2.1, dated 2025-01-09; numeric natbib mode | Passed |

The classic style is copied from the preserved audit evidence into each temporary rendering directory. No style or package is installed by the tests. An unavailable consumer produces an explicit warning and a named skipped test; none was unavailable in this run.

## Remaining slice 1 acceptance

Import, file intake, backup and the demonstrated restore into a second home remain pending. The [file contract](contracts/files-and-recovery.md#snapshot-and-documented-restore) owns restore safety. The owner selects a real paper only after the remaining slice 1 work is complete. No whole-library migration or slice 2 work is authorized by this demonstration.
