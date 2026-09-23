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
