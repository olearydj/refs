# Test review: investigation, 2026-09-24

This is the investigation half of the test review the owner asked for after slice 3: "make sure they are all valid and well designed, actually meaningful tests ... look at coverage, consider what other kinds of tests should be added / expanded (integration, e2e, etc.), revisit the demo / smoke, do another expanded pass of rehearsal style testing". It records what was found. The brief that decides what to do about it is separate.

## Method

Three independent readings, cross-checked against each other and spot-checked against the source before anything was written here. One reader took every file under `tests/contract` (48 files, 209 functions, 432 cases) and asked of each test what would have to break for it to fail. A second took `tests/integration`, `tests/unit`, the demo script and the real-trial harness with the same question, with particular attention to the interruption tests that guard the move protocol. A third mapped every MUST, refusal, exit code and error code in the contracts, and every functional requirement in the spec, to the tests that would fail if it broke. Coverage was measured twice: once in-process, which reported 79 percent and showed the command layer at zero because every CLI test runs `refs` as a subprocess, and once with coverage started inside each child process, which is the real figure.

Nothing was changed. The full suite passed, 592 tests in about two and a half minutes.

## Measurements

Coverage with branches, collected across subprocesses: 90 percent of lines. Modules below 85 percent: `adapters/csl.py` 67, `files.py` 81, `adapters/bibtex.py` 84, `catalog.py` 84, `display.py` 86, `recovery.py` 86, `resources.py` 87. Nothing is below two thirds. The uncovered lines are mostly refusal branches and error paths: the external opener failing, a cloud placeholder that cannot supply bytes, the staging-volume mismatch, the lock timeout, a hot journal on a read-only open.

The pyramid, by what a test actually exercises rather than by directory:

| Kind | Count | Notes |
| --- | --- | --- |
| Unit, pure functions and models | about 67 | `tests/unit`, plus about 15 files in `tests/contract` that never touch the CLI and belong here |
| Contract, through the command as a subprocess | about 430 cases | `tests/contract`; about 40 files use the shared `cli` fixture, 13 build their own subprocess call |
| Integration in process, real filesystem and SQLite | about 51 | moves, copy, restore, the Zotero gate |
| Integration across processes or with a real crash | 6 | descriptor limit, key allocation race, the move rehearsal |
| Integration with external tools | 35 | rendering through pandoc, biber, bibtex; skipped when a tool is missing |
| End to end | 1 | `test_smoke` runs `scripts/demo.sh --smoke`, 121 checks, against the editable install |

Kinds that do not exist: a test of the built wheel installed into a clean environment; a real kill of the `refs` command itself rather than of a Python worker; property-based tests for the parsers, dates, naming and collision suffixes; concurrency beyond two processes; scale, which lives only in the manual harness; a case-sensitive filesystem; fault injection for disk full, permission denied, or a cloud placeholder; resuming an unfinished move after a restore.

## What was found

The suite is better than most: no sleeps, no skipped or expected-failure tests, no broad exception handlers, nothing writes outside its temporary directory, and there are tests in it that would be worth copying anywhere. The problems are of four kinds, and each has a rule behind it rather than a list of patches.

### Tests that pass for the wrong reason

About twenty tests cannot fail, or cannot fail for the reason their name gives. The shapes recur.

- Either outcome passes. `test_mapping_convergence.py` wraps serialization in a try that accepts success with any warning class or a refusal with one code, so a mapping that starts blocking, or stops, is not noticed. `test_import.py:87` asserts `limitations or invalid`, so a construct that flips from preserved to rejected passes.
- The expectation is computed by the code under test. `test_default_output.py:25` takes the expected warning count from a prior JSON export by the same code. `test_languages.py:28` compares the implementation to itself. Three files build expected policy lists from `naming.GLOBAL_TERMS` and friends, so a wrong default travels into the expectation.
- Any change passes. `test_export.py:136` and two places in `test_skeleton_export.py` assert only that the output differs from before, which garbage would satisfy.
- Trivially true. `b'@' in output` for any BibTeX; `'2024' in stdout` for a record dated 2024; `if code:` on rows that all have a code; a `findings == 0` that the harness hard-codes; a check that a fixture file contains its own text.
- The race is not forced. `test_key_allocation.py` starts two processes with no barrier, so if they happen to run in sequence the test passes without exercising the race.

The rule these break: a test must assert a value the code under test did not produce, and the assertion must distinguish the defect the test is named for from the absence of a crash.

### Refusals checked without their reason

Twenty-eight `pytest.raises(RefError)` calls carry no code or message, and about fifteen CLI calls assert exit 2 or 3 without the error code. Exit 2 is also Typer's generic usage error, so a renamed option passes those. Bare raises are worst where the wrong refusal is easy: the symlink cases in `test_resources.py:64` and `test_skeleton_export.py:108` would pass on a missing-source error, and the adoption test at `test_export.py:124` would pass on an empty project. Thirty-seven error codes defined in the source are never asserted by any test; another thirty are reached only by exit code or message substring, so a wrong code passes.

The rule: every refusal test pins the exit code, the error code, and the absence of side effects, which is exactly what the best test in the suite, `test_capture.py::test_unsupported_input_is_explicit`, already does.

### The wrong layer

About fifteen files in `tests/contract` never invoke the command: they call `importing.run`, `sources.add`, `bibliography.serialize` and so on. They are unit tests filed as contract tests, and the flag parsing, exit codes and envelopes for those paths, such as reconcile with both `--keep-current` and `--take-incoming`, are untested at the command level. Several human-output checks call the renderer in process rather than reading what `refs` prints, so a command that bypassed the renderer would not be caught. One integration test counts calls to the hash function, which breaks on a harmless refactor.

### Fixtures and the harness the tests stand on

- The `cli` fixture runs whichever `refs` is first on `PATH`. Under `uv run` that is the checkout; from a bare shell it is the tool install in `~/.local/bin`. Both are editable installs today, so the code is the same, but the environments are not, and the suite has no way to know which it tested.
- The fixture never passes `--no-project-config` and inherits the working directory, so every CLI test depends on no `.refs.toml` being discoverable from wherever pytest runs. About ten files construct settings the same way. Six files use paths relative to the repository root and fail at collection elsewhere.
- Ten files copy the same three-line environment setup; the `human` fixture lives in one test file; a helper is imported across test modules by relying on the rootdir being on `sys.path`.
- The fixture asserts the schema version on every call but never that stderr is empty, so human text could leak into JSON mode unseen.
- State is built by raw SQL in about ten places, including `state='removed'` where `refs remove` exists, and in one case a trigger is dropped to do it. Magic numbers for the schema version and table count appear in six places and change with every migration.
- The Zotero fixture and `reference.json` are clean: one ASCII author, one date, valid everything. All human rendering of `show`, `list` and `search` is checked only against that shape. Move and copy tests use files of a few dozen bytes: no zero-byte file, nothing larger than a buffer, no NFD name on disk, nothing read-only.
- The rendering tests skip when pandoc or TeX is missing, so on a machine without them about 32 tests vanish silently; on this machine biber failed to unpack itself in one run and passed in the next, so the file is also flaky. The smoke test needs `jq` and fails rather than skips without it.
- The move rehearsal never removes its temporary homes. Eighty-six had accumulated, 31 GB, six of them full copies of the library from the real-sample runs; the owner deleted them during this investigation.

### What is not tested at all

The mapping found the following, ordered by what a regression would cost.

1. Removing a source that has managed files. Every `remove` in the suite runs with `--execute` on a source with no file. Nothing asserts that files survive removal or that an exported bibliography is untouched. Since intake now moves by default, a regression here would destroy the only copy of a PDF.
2. A retry after publication when the destination's identity differs. Only the matching case is tested; the case where a foreign file occupies the destination, which must stop, is not.
3. Three of the five blocking-loss codes for export, the ones about cited authors, in-text citations and protected spelling, are only ever fed to the enforcement function as synthetic lists. Nothing proves the detector emits them.
4. The catalog file lock: its five-second timeout, exit 6 and `lock_timeout` have no test, and nothing runs two writers against file effects.
5. `remove` without `--execute`, its default preview, is never run.

Also untested: changing a named root never moves a file; a missing previously adopted bibliography remains a conflict; the recorded state's recheck of the resource revision and loc; the staging-volume mismatch; the lock; the cloud placeholder; search over abstracts and imported tags; list ordering by title; every `--dry-run` on update, key set, remove, reactivate, uncite and unlink; `export --profile`; `open --resource` through the command; the mutually exclusive option pairs.

### Contract drift found on the way

The mapping turned up three places where a test asserts the opposite of the contract, and one requirement with no code.

- `cli.md` says `resource unlink` and `reactivate` take `--if-revision`; the command does not, or makes it optional, and tests lock that in.
- `records.md` says protected terms no longer present after a title edit are warned about and retained until explicitly changed; `test_sources.py::test_title_edit_retires_old_protection` asserts they are dropped without a warning.
- `cli.md` says help and version are the textual exceptions to JSON output; `refs --version` does not exist. Typer also generates a `--no-no-project-config` flag in the help.
- FR-044, that the catalog is never placed in a folder a sync service copies, has no code and no test.

Which side of each drift is right is the owner's call; the tests should then follow the contract, not the other way round.

### The demo and the real-trial harness

The demo's 121 checks are 65 exit-code-and-envelope checks, 49 value checks through jq, and 7 byte comparisons. It would catch wrong answers, not only crashes, and it is the only end-to-end test. Its weak spots: two list assertions pass on an empty list; a few checks are `> 0` or `!= null`; the interrupted copy is simulated by patching; the restore runs inside the demo's own Python rather than as a process; it runs only the editable install; and the smoke test asserts the `PASS` line but not the count, so a deleted section goes unnoticed.

The real-trial harness proves the things that have mattered: five real bibliographies import clean, the whole library imports, rendering matches or reports its differences, creators are not invented, export notices classify correctly. It only exercises, without counting failures, the show step, title normalization, search and backup; `set -e` is off and the import exit code is printed but not asserted; its files section still lists `lib/Unfiled`, so that check prints nothing. The move rehearsal is the strongest test in the project: a real SIGKILL at two boundaries and digest-level assertions after resume. It covers only two of the six boundaries, and never the windows inside the copy, inside the record transaction, or after the unlink; the in-suite move tests cover all six but by raising an exception, which unwinds locks and context managers as a real kill would not.

### Patterns worth keeping

Three tests should be the model for the rest. `test_duplicate_attachment.py` asserts no effect at every level and then flips one variable to prove the discriminator is content, not name. `test_skeleton_export.py::test_interrupted_publication_recovers` injects a fault at a named boundary and asserts on persisted state, not return values. `test_capture.py::test_unsupported_input_is_explicit` pins exit code, error code and an unchanged catalog for each of five bad inputs. Also worth naming: the Zotero gate as an independent SQL oracle with negative controls, and the walkthrough test that compares two commands' outputs to each other instead of to a hand-written expectation.

## What the brief must decide

- The bar: whether a test that cannot fail is deleted or rewritten, and whether the rule "pin code, exit and side effects" becomes a stated convention in the repository.
- The three contract drifts and FR-044: which side stands.
- The harness: pin the binary, isolate from the working directory, share fixtures, clean up temp homes, and whether external-tool tests skip, fail, or run only in a marked job.
- The missing kinds: which of wheel install, real kill of the command, property-based parsers, concurrency, and post-restore resume are worth building now, against the right-sizing budget.
- The second rehearsal round the owner asked for: what it runs against and what it must prove beyond the first.
