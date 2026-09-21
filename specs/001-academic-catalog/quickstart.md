# Quickstart Validation: Academic Catalog Workflow

**Status**: Runnable acceptance guide for the implementation phase. The CLI, environment, and fixture paths below are planned deliverables, not available application code at the time of planning. Use disposable homes and synthetic/public fixtures until the user selects the real paper and migration sample.

## Prerequisites and Installation

Use macOS/Linux, Python 3.14, uv, local storage with the required filesystem primitives, and a SQLite build with FTS5. Quarto is required only for rendered-citation validation. Start from a checkout after implementation supplies `pyproject.toml`, `uv.lock`, tests, and public fixtures. All commands use project-relative fixture paths from the repository root.

```bash
uv sync --locked
uv run --locked refs --help
uv run --locked refs --json schema source-create
uv run --locked pytest tests/unit tests/contract tests/integration
uv run --locked ruff check .
uv run --locked ty check src/refs
```

Verify the project config retains `exclude-newer = "3 days"` and that a clean `uv sync --locked` succeeds. Do not use `--frozen` to bypass a mismatch. Installed-wheel acceptance is an integration test that builds once, installs into an isolated environment, and invokes the executable in subprocesses; it must not rely solely on importing modules from the working tree.

## Disposable Capture and Search

```bash
refs_trial_root=$(mktemp -d)
mkdir -p "$refs_trial_root/library"
uv run --locked refs --home "$refs_trial_root/home" --no-project-config init --library-root "$refs_trial_root/library"
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json paths
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json add --input tests/fixtures/public/source-smith.json --request-id capture-smith
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json add --input tests/fixtures/public/source-smith.json --request-id capture-smith
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json search "Turing Trap"
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json show smith-2024-turingTrap
```

The fixture follows [source creation](contracts/records.md) and has the documented Smith/2024/title values. Expect one source, stable returned identity/key, unchanged second outcome, and recognizable matching context. Capture fixtures must also include a missing-year/editor fallback, an explicit-key URL-only record, corporate names, and non-ASCII names. Check source spelling and key policy in previews; unsupported transliteration yields an override request rather than dropped letters.

## Correction and Concurrency

```bash
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json update smith-2024-turingTrap --patch tests/fixtures/public/pages-patch.json --if-revision 1
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json update smith-2024-turingTrap --patch tests/fixtures/public/pages-patch.json --if-revision 1
```

The first changed patch advances revision; the second exits 3 with a stale-revision error and no change. The key remains intact. Subprocess integration cases start four callers to test unique key allocation, duplicate request IDs, changed-request rejection, reserved resources, and bounded lock contention. Typer's in-process test runner is not used to simulate concurrent processes.

## Explicit Bibliography Export and Outside Edits

```bash
uv run --locked refs --home "$refs_trial_root/home" --no-project-config project create paper-x
uv run --locked refs --home "$refs_trial_root/home" --no-project-config project cite paper-x smith-2024-turingTrap
uv run --locked refs --home "$refs_trial_root/home" --no-project-config export --project paper-x --output "$refs_trial_root/references.bib" --format biblatex
uv run --locked refs --home "$refs_trial_root/home" --no-project-config export --project paper-x --output "$refs_trial_root/references.bib" --format biblatex
```

Expect an adopted new destination and identical repeat bytes. The integration fixture then edits the bibliography externally, verifies export exits 3 and preserves those edits, and exercises explicit overwrite and reconciliation/adoption. A catalog edit alone must not change the file. Use the public manuscript fixture with its referenced fixture bibliography to run:

```bash
cp tests/fixtures/public/citation-paper.qmd "$refs_trial_root/paper.qmd"
quarto render "$refs_trial_root/paper.qmd" --to html --output-dir "$refs_trial_root/rendered"
```

The minimal fixture cites `smith-2024-turingTrap` and declares `bibliography: references.bib`; copy it beside the bibliography just exported from the isolated catalog. Broader citation-type rendering is covered by the integration fixtures. Assert selected keys, creator roles, title protection, and absent unselected citations. The later real-paper check follows the same contract with user-selected inputs.

## Partial Imports and Migration Fidelity

```bash
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json import --format biblatex --input tests/fixtures/public/mixed-conflicts.bib --origin public-mixed --dry-run
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json import --format biblatex --input tests/fixtures/public/mixed-conflicts.bib --origin public-mixed
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json import --format biblatex --input tests/fixtures/public/mixed-conflicts.bib --origin public-mixed
```

Dry run changes no persistent state. Actual import exits 4 when the prepared fixture includes conflicts, applies every conflict-free entry, and accounts for all inputs. Repeat creates no duplicates. Use the returned batch ID with `import show`, `import reconcile --input`, and `import resume` to verify explicit decisions. Never type a placeholder UUID as if it were a real batch identity.

The Zotero fixture matrix supplies a supported synthetic snapshot with manifest/checksums, pinned keys, ordered roles, collections, absolute/root/storage attachments, notes, and annotations. Import with `--format zotero-snapshot --input tests/fixtures/public/zotero-snapshot --origin public-zotero`. Unknown schema and incomplete snapshot fixtures must fail before source writes. The live sample must be acquired with Zotero closed and inspected read-only; no current path is relocated as part of import.

## Managed Intake and Recovery

```bash
cp tests/fixtures/public/sample.pdf "$refs_trial_root/download.pdf"
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json resource intake smith-2024-turingTrap --path "$refs_trial_root/download.pdf" --dry-run
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json resource intake smith-2024-turingTrap --path "$refs_trial_root/download.pdf" --request-id intake-sample
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json resource list smith-2024-turingTrap
uv run --locked refs --home "$refs_trial_root/home" --no-project-config --json resource check
```

Expect `library/Unfiled/download.pdf`, verified bytes, original removed only after catalog commit, unchanged filename, and a complete operation. Use returned resource IDs to adopt/link/file-under and preview `reorganize`; ordinary collection/project edits must leave files in place.

Integration tests interrupt processes at every documented transfer/export boundary, then run `operations show` and `recover --execute`. Verify collision preservation, changed-source conflicts, cleanup-pending state, export-baseline recovery, and zero deletion of external attachments on source removal. Test unsupported bundle/metadata/storage cases as safe failures. No production fault-injection flag is required; test harnesses inject effects at the file-operation boundary.

## Backup, Full Export, and Restore

```bash
uv run --locked refs --home "$refs_trial_root/home" --no-project-config backup --output "$refs_trial_root/backup"
uv run --locked refs --home "$refs_trial_root/home" --no-project-config library export --output "$refs_trial_root/library-export"
uv run --locked refs --home "$refs_trial_root/restored" --no-project-config restore --input "$refs_trial_root/backup"
uv run --locked refs --home "$refs_trial_root/restored" --no-project-config --json show smith-2024-turingTrap
uv run --locked refs --home "$refs_trial_root/restored" --no-project-config --json resource check
```

Compare 100% of source IDs, keys, current metadata, provenance, overrides, collection/project relationships, unresolved imports, and resource links against the saved snapshot. Do not mutate both homes against shared external files. Verify external contents are listed as excluded, adopted outputs require current-file revalidation, corrupted bundles fail, and incomplete restores cannot be opened normally. Parse the full export without refs to check entity counts and references.

## Completion Evidence

Record the package lock, runtime/SQLite versions, OS/filesystem, fixture versions, reference-machine performance results, and commands/results for SC-001–SC-009. Search performance uses 10,000 sources, 30,000 links, and 100 fixed queries; p95 target is one second after warmup. Finish with the selected active paper, at least 30 representative migration records, and a separate-home restore. Whole-library cutover and claims about annotation portability wait for that evidence.

## Bibliographic profile acceptance

Validate packaged registry fingerprints against the [coverage inventory](contracts/bibliographic-coverage.json) and ensure every baseline type/field/role has a generated schema path and reported coverage status. This is a coverage check, not proof of conversion. Use synthetic/public cases B01–B15 from the [bibliography contract](contracts/bibliography.md) to exercise import → show → patch → export → reimport, comparing canonical values and explicit limitations. Export the complete library and verify structured native fields, supporting-item content, parent references, asserted relationships, and original bytes separately.

Include a three-level title hierarchy; two publisher/place values; corporate names containing “and”; dropping/non-dropping particles; original/issued/submitted dates; a descriptive edition; preprint and later published article; patent versus application number; programmer versus author; and native types sharing one CSL classification. Assert that editing a recognized native field changes its projection and does not resurrect old raw content. The accepted author/editor key fallback stays unchanged for inventor/programmer-only records.

Inheritance cases cover each supported parent/child pair and field transfer, child overrides, parent identifiers never copied as child identity, missing/cyclic parents, unsupported xdata, and a selected child whose parent is not cited. Include unresolved BBT override directives, unknown macros, duplicate/case-colliding fields and unsupported target types; each must report the affected field/key and block publication when citation meaning cannot be preserved.

Check imported child and standalone notes, URL-only attachments, missing attachment paths, annotations attached to attachments, and unresolved related-item targets through read-only inspection and full export. Do not mistake this for rendering/editor or PDF-annotation acceptance. Validate internal CSL projections against the pinned schema and render the supported .bib outputs through the target Quarto workflow, including title-case/protection differences. The real 30-record minimum sample must include every type/construct used by the selected paper, and must expand if 30 records do not cover them. Required unsupported cases need explicit reconciliation or a verified adapter improvement before migration acceptance.
