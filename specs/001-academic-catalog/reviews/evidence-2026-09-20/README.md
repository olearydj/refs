# Audit Evidence, 2026-09-20

Scripts, synthetic fixtures, and raw outputs behind the [independent design audit](../2026-09-20-independent-design-audit.md), copied from the session scratch directory on 2026-09-21 before cleanup. These are audit evidence, not independently reproduced results.

| Folder | Track | Contents |
| --- | --- | --- |
| `deps/` | Dependencies (F-D01 to F-D05) | `fx/` synthetic `.bib` inputs, `exp_*.py` and `bench_parse.py`, `out/` results for bibtexparser, pylatexenc 2.10 versus 2.11, pybtex, Pandoc, Biber, transliteration, SQLite capabilities; `cli/` Typer, Click and argparse startup probes with the resolved `uv.lock` |
| `export/` | Export fidelity (F-I01, F-I05, F-I10, F-I11, F-B06, F-B08) | `fixtures/` synthetic entries, `scripts/` including `diffrender.py`, `out/` Pandoc CSL-JSON conversions and rendered citations by route and style, `natbib.txt` classic `bibtex` run with `elsarticle-num.bst`, `biber/` data-model validation, `roundtrip/`, `A-bibstats.txt` and `A-titlecase.txt` aggregate counts over the user's bibliographies |
| `fsops/` | Storage and file protocol (F-A01 to F-A08) | `exp1` to `exp5` scripts and `.out` files: link versus copy metadata preservation, `fsync` versus `F_FULLFSYNC`, SQLite concurrency, read-only homes, crash-point recovery, BLOB growth and backup cost |
| `zotero/` | Migration route (F-I06, F-B07) | Read-only inspection scripts and their count-only outputs, plus the BLOB sizing test |
| `schemas/` | Registry verification (F-B01 to F-B03) | SHA-256 of the pinned upstream files that were fetched and compared; the files themselves are reproducible from the URLs in `bibliographic-coverage.json` and `biblatex.def` at tag v3.22 |

Run pattern: `uv run --no-project --python 3.14 [--with 'package==version'] python <script>` from the script's folder. Tool versions: CPython 3.14.2, SQLite 3.50.4, uv 0.12.1, Pandoc 3.11, Quarto 1.10.18 (bundles Pandoc 3.10), Biber 2.21 with BibLaTeX 3.21, macOS 26.4.1 on APFS.

Deliberately not copied: the session-history extraction (verbatim private messages), downloaded third-party sources and documentation, virtual environments, PyPI metadata dumps, binary test files, and test databases. `A-bibstats.txt` and the Zotero outputs contain local paths and aggregate counts from private files; review them before publishing this repository.
