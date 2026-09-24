# Real-input trial harness

`run.sh` exercises refs against copies of the owner's real bibliographies in throwaway homes. It is not part of the pytest suite and the private inputs are not committed.

Before running, populate the sibling directories (all git-ignored):

- `papers/<name>/references.bib` plus that paper's `_quarto.yml` and main `.qmd`, copied from `/Volumes/Casa/pub/<name>/` for: `pipyer-paper`, `2026-jose-danvas`, `2026-insight-dema-llm`, `manufacturing-training-media-tradeoffs`, `dissertation`
- `inputs/zotero-bbt-export.bib` copied from `/Volumes/Casa/au/!Research/bib/zotero.bib`
- `inputs/attention.json` fetched with `curl -sL -H 'Accept: application/vnd.citationstyles.csl+json' https://doi.org/10.48550/arXiv.1706.03762`
- `downloads/*.pdf`: any three PDFs

Then `tests/fixtures/real-trial/run.sh`. It copies the fixtures to a fresh `/private/tmp/refs-trial-*/trial` directory and remaps BibTeX attachment fields to unavailable temporary paths before import. This prevents duplicate-file checks from reading absolute links into the owner's trees. On macOS the subprocess also denies reads and writes to the real refs, Box and Zotero locations. The printed log path retains full output; homes and findings are under that temporary copy's `out/`. Private input copies and existing repository output remain untouched.

## Slice 3 move rehearsal

Run `uv run --locked python tests/fixtures/real-trial/move_rehearsal.py --sample "$SAMPLE"` against an owner-provided disposable sample under this fixture directory or a temporary directory. The sample contains `cat/` (a closed catalog copy with no move operations), copied attachment trees, and `manifest.json`:

```json
{"roots": {"/original/Box/root": "tree/Box", "/original/storage": "tree/storage"}, "box_root": "tree/Box"}
```

The original-root strings are used only to rewrite catalog locators. They are never opened. Every resource must map to a file inside the sample. Symlinks, missing files, escaping paths and unrecognized named roots are refused. Configuration from the sample is replaced with explicit temporary paths.

The harness makes three fresh temporary homes, applies loc assignments, and runs a clean move and two real SIGKILL cases: after publication before registration, and after registration before deletion. Each interrupted command is repeated. Assertions cover resource IDs, digests, collision names, completed states, no-op reruns, unchanged input samples and untouched extras. The JSON report names the retained homes. Synthetic tests exercise the harness separately; they are not evidence of a real cutover.

## Tests pass rehearsal on the owner's copy

Use a closed copy of `cat/` and `lib/` under `/Volumes/Casa/tmp`, and create a separate empty work directory there. The phase 6 move mode APFS-clones the copy into a fresh working home for each of six protocol checkpoints and four interior windows. It kills the refs CLI process at the selected point, runs a new command to resume, verifies the final digest and state, and deletes only that working home. `--daily` clones the same copy, starts by removing a cited source with a managed file, checks that the file and an already exported bibliography have identical hashes, reactivates the source, exercises read commands, and validates a backup. Both modes report elapsed time and peak physical temporary disk use.

```bash
uv run --locked python tests/fixtures/real-trial/move_rehearsal.py --sample "$SAMPLE" --phase6-work "$WORK"
uv run --locked python tests/fixtures/real-trial/move_rehearsal.py --sample "$SAMPLE" --phase6-work "$WORK" --daily
```

Keep the corpus manifest and fetched Better BibTeX fixture checkout outside the repository. The manifest has `ceilings` for files, entries, seconds and temporary bytes, and a `files` array of objects with `source` and absolute `path`. The corpus mode classifies all files before writing, refuses to start above a ceiling, imports into a clone, accounts for every entry, repeats every import, exports and renders when possible, checks resources, then backs up and restores. Refusal codes and examples stay in the JSON report. Its refs and Pandoc subprocesses deny access to the real refs catalog, Box tree, Zotero directory and default config path.

```bash
tests/fixtures/real-trial/run.sh --corpus --sample "$SAMPLE" --phase6-work "$WORK" --corpus-manifest "$WORK/corpus-manifest.json"
```
