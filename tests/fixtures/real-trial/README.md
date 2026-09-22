# Real-input trial harness

`run.sh` exercises refs against copies of the owner's real bibliographies in throwaway homes. It is not part of the pytest suite and the private inputs are not committed.

Before running, populate the sibling directories (all git-ignored):

- `papers/<name>/references.bib` plus that paper's `_quarto.yml` and main `.qmd`, copied from `/Volumes/Casa/pub/<name>/` for: `pipyer-paper`, `2026-jose-danvas`, `2026-insight-dema-llm`, `manufacturing-training-media-tradeoffs`, `dissertation`
- `inputs/zotero-bbt-export.bib` copied from `/Volumes/Casa/au/!Research/bib/zotero.bib`
- `inputs/attention.json` fetched with `curl -sL -H 'Accept: application/vnd.citationstyles.csl+json' https://doi.org/10.48550/arXiv.1706.03762`
- `downloads/*.pdf`: any three PDFs

Then `tests/fixtures/real-trial/run.sh`. Output lands in `out/`; findings are echoed and appended to `out/findings.txt`. Every home is created under `out/`; nothing touches `~/.config/refs`, `/Volumes/Casa/refs`, or the source files.
