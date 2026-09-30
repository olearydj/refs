# Pipyer adoption package — 2026-09-29

The owner selected “Accept and adopt (Recommended)” as quoted in `comms/2026-09-29-204346-s1-pipyer-gate-accepted.md`. The pre-adoption fixture is now recorded against clean publication commit `de8894483ea107068ef0529e81de28d2f18328ed`. All 11 extracted entries exactly equal the accepted gate; first recording exits 3 because the fixture was absent at the start. Fixture SHA-256: `f9c8b4f208faad5a35e32241e1f10f9d509f5bc1808ca085352b8927e85b8887`.

## Exact inputs

Apply [the patch](2026-09-29-pipyer-paper-adoption.patch) against that commit. It changes only the bibliography path in `_quarto.yml` and the Kapoor citation key in `paper.qmd`. Copy [the configuration file](2026-09-29-pipyer-paper-adoption.refs.toml) byte-for-byte to the publication's `.refs.toml` (UTF-8, LF, final newline):

```toml
project = "pipyer-paper"

[[export.targets]]
output = "references.json"
profile = "csl-json-v1"
```

Expected `references.json` SHA-256: **`69a894fcd277a1fbbab6bb32a1311f7d76651be46b47800d2dc10ca02d244e31`**. The fresh recorded scratch export has 11 records and these exact bytes. The old `references.bib` SHA-256 before retirement is `cf3eeae05bfbf12f0a6f352f2034e7655100d843047d4404e947d28aa33e3cb3`.

## Adoption sequence for session 1's subagent

Confirm the paper is still clean at the stated commit and `references.json` and `.refs.toml` do not exist. Apply the patch and copy the configuration. Run the following refs commands in this order from `/Volumes/Casa/dev/refs/worktrees/pipyer-paper-execution`; explicit selection avoids relying on the caller's current project configuration:

```sh
uv run --locked refs --json --no-project-config export --project pipyer-paper --profile csl-json-v1 --output /Volumes/Casa/pub/pipyer-paper/references.json --dry-run
uv run --locked refs --json --no-project-config export --project pipyer-paper --profile csl-json-v1 --output /Volumes/Casa/pub/pipyer-paper/references.json
shasum -a 256 /Volumes/Casa/pub/pipyer-paper/references.json
uv run --locked refs --json --no-project-config export --forget /Volumes/Casa/pub/pipyer-paper/references.bib --dry-run
uv run --locked refs --json --no-project-config export --forget /Volumes/Casa/pub/pipyer-paper/references.bib
```

Stop if the exported hash differs from the expected hash above, before forgetting the old binding. `--forget` removes only the old target binding and leaves the file unchanged. After confirming the new export hash and successful forgetting, retire the tracked old file with `git -C /Volumes/Casa/pub/pipyer-paper rm references.bib`; git history preserves it. Commit `_quarto.yml`, `paper.qmd`, `.refs.toml`, `references.json`, and the `references.bib` deletion together as the adoption, without other content changes. No `--overwrite` or `--adopt` is needed for the new JSON destination.

Send the adoption commit to session 2. The owner has authorized removing the scratch substitutions, pointing the register at that commit, and running the individual and all-project checks without `--record`. Only if all 11 Pipyer entries and all 423 existing entries are identical may session 2 re-record at the adoption commit. Session 1 performs the eventual merge.
