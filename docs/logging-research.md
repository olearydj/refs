# Logging research, 2026-09-23

Research done while slice 3 was building, for the logging brief named in the [plan's post-slice-3 row](../specs/001-academic-catalog/plan.md#deferred-work). It records what was found and what was discussed. It decides nothing.

## What the sibling tools do

None of the six calibration tools (git-muster, secretpath, course-courier, canvas-ledger, danvas, danner) keeps a diagnostic log file. Where a durable record of actions exists in a sibling, it was built by hand and lives beside the data: danvas writes a manifest per report run, canvas-ledger keeps ingest-run and change-log tables in its SQLite with old and new values per field, and pipyer and worldrunner keep an append-only `events.jsonl` with an fsync on every line. The smaller, older projects use the standard library with a Rich console handler and a plain file handler. A sweep of all 34 projects in the tree on 2026-09-23 found the standard library imported in 13, Rich's handler in 4 (classpub-cli, dema-llm, innovation-funding-analysis, ppt2llm), a plain file handler in 5, a rotating handler in 1 (dema-llm), python-json-logger in 1 (dema-llm), structlog only in the sk-test spike, and loguru nowhere.

Patterns worth copying: pipyer's append with a single-writer lock and an fsync per event; worldrunner's helpers that fsync the directory when a file is created; danvas's private writes with no-clobber linking and symlink refusal, which refs's copy path already mirrors; canvas-ledger's per-field old and new values; danvas's error sanitizer, which strips secrets and URLs before anything is stored.

Patterns to avoid: a rotating handler as the record of actions, since rotation discards history; log paths relative to the working directory; swallowing a failed log write; rewriting a log in place to repair a torn line; a manifest written only at the end of a run, so a crash leaves nothing.

## Candidate libraries

- Standard library, with a JSON formatter for the file. No dependency, or one if `python-json-logger` (4.2.0, no dependencies of its own) is used. Rich's `RichHandler` serves the console at no cost, since rich is already in the lockfile through typer.
- structlog (26.1.0). One dependency with nothing beneath it on Python 3.11 and later. A processor pipeline binds context such as the command, the source key and the operation id to every line; JSON rendering to file; a key-value console renderer that uses rich for exceptions when present. Integrates with the standard library. The 2026 comparisons name it the choice when structured output and bound context matter.
- loguru (0.7.3). One dependency on macOS. One `add()` call per sink with rotation, retention and JSON serialization; an intercept handler for the standard library. Thread safe, not multiprocess safe without its queue; its verbose exception mode is documented as able to leak sensitive data.

## What was discussed

The owner's need: "a second ledger of actions, changes, etc. that persists outside of what is recorded in the database", later framed as "it's logging", with a preference for something fancier than the standard library and a liking for rich. A durable record of an action wants three things a default file handler does not give: fields complete enough to reconstruct the change, a write that reaches the disk before the effect happens, and no rotation or filtering that could discard it. The move protocol's `file_operations` table already has the ordering property through SQLite.

We discussed whether one package could handle both diagnostic lines and action lines: the same logger for both, action lines carrying a fixed set of fields at their own category, and a handler for that category that fsyncs each write and never rotates, so the library choice bears only on the console and on context binding. This was discussed, not agreed.

Open for the brief: what must be reconstructable without the database; whether action lines share a file with diagnostics or have their own; which fields an action line carries; which library, against the four-dependency budget.

Sources: [Dash0, Python logging libraries in 2026](https://www.dash0.com/guides/python-logging-libraries); [Better Stack, top Python logging libraries](https://betterstack.com/community/guides/logging/best-python-logging-libraries/); [structlog console output](https://www.structlog.org/en/stable/console-output.html); [loguru overview](https://loguru.readthedocs.io/en/stable/overview.html); PyPI metadata for structlog, loguru and python-json-logger, read 2026-09-23.
