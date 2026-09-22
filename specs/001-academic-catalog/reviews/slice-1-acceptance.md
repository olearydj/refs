# Slice 1 acceptance evidence

## T032 — Snapshot restore and SQLite recovery

The documented Python blocks in `docs/restore.md` are executed directly by `tests/integration/test_restore.py`. On 2026-09-21, all five restore tests passed using temporary homes and synthetic data.

The restored catalog was opened through paths, list, show, project show and resource check. Every saved table was compared with the restored database, including original bytes, corrections, source revisions, resource associations, project citations and export target state. Corrupt bytes, symlinked members, unsupported manifest versions and a nonempty restore destination were refused. Missing resources remained recorded.

The hot-journal test terminated a separate writer after it had spilled uncommitted pages. The documented recovery commands rolled back the update and passed integrity and foreign-key checks. No real catalog, bibliography or resource file was used.

## T035 — Complete slice verification and packaging

Verified on 2026-09-21 with Python 3.14.2:

| Check | Result |
| --- | --- |
| `uv sync --locked` | Passed; lockfile and three-day cooldown retained. |
| `uv run --locked pytest -q --tb=short` | 294 passed. |
| `uv run --locked ruff check .` | No findings. |
| `uv run --locked ty check src/refs` | No diagnostics. |
| `scripts/demo.sh --smoke` | `PASS refs demo: 95 checks (US1, US2, US3, US4, US5, US6)` |
| Clean installed wheel, same demo | The same 95 checks passed. |

The demo uses temporary homes and synthetic data. Its restore section executes the documented restore block and compares every saved table. Configuration inspection works before init, forbidden project settings fail, and a missing catalog never initializes a fallback. Tests cover all 23 command invocations, with external opening mocked or requiring explicit selection rather than launching a viewer.

Built `dist/refs-0.1.0-py3-none-any.whl`, SHA-256 `ce48a9aff36cca08bd27d207750ca217ca7a006641050e7e09790a8efb7565a7`. A fresh temporary virtual environment received the exact runtime versions exported with `uv export --locked --no-dev --no-emit-project`, followed by the wheel installed with `--no-deps`. The installed module path was confirmed inside that environment's site-packages. All four offline schemas returned successfully. Archive inspection confirmed the mapping registry, registry provenance, transliteration table, model/schema code and single migration.

The first installation attempt with forced `--require-hashes` was rejected by an unrelated global, non-exact `litellm` exclusion. Installation succeeded with the exported exact pins and hashes while retaining the global constraint and cooldown; neither `--frozen` nor `--no-config` was used. The final wheel was rebuilt and reinstalled after the snapshot-schema validation improvement, then reran the full demo successfully.

Remaining boundaries: snapshots exclude all external file contents; manual restore and hot-journal recovery are documented procedures, not new commands. Copy intake retains originals and does not promise power-loss durability or native filesystem metadata preservation. Unsupported Bib constructs remain preserved with limitations. The owner checkpoint and real-paper trial have not been performed, and no real catalog, PDF or manuscript bibliography was accessed.
