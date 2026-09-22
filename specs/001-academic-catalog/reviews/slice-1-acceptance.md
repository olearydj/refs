# Slice 1 acceptance evidence

## T032 — Snapshot restore and SQLite recovery

The documented Python blocks in `docs/restore.md` are executed directly by `tests/integration/test_restore.py`. On 2026-09-21, all five restore tests passed using temporary homes and synthetic data.

The restored catalog was opened through paths, list, show, project show and resource check. Every saved table was compared with the restored database, including original bytes, corrections, source revisions, resource associations, project citations and export target state. Corrupt bytes, symlinked members, unsupported manifest versions and a nonempty restore destination were refused. Missing resources remained recorded.

The hot-journal test terminated a separate writer after it had spilled uncommitted pages. The documented recovery commands rolled back the update and passed integrity and foreign-key checks. No real catalog, bibliography or resource file was used.
