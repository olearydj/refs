# CSL fidelity fixes: truncated lists and legacy events

Branch: `s2/csl-fidelity-fixes`, based on `78708e1`. The owner authorized this pass through s1: “agree with the fix pass. kick that off while we review 2 and 3”. This report covers kickoff items 1 and 2. Item 3, arXiv projection, remains awaiting a decision in `comms/2026-09-27-141043-s2-arxiv-representation-question.md`.

## Rules

Export interprets an exact bare `{"family":"others"}` or `{"literal":"others"}` creator as a truncated-list sentinel. CSL emits the literal form recognized by citeproc; both Bib profiles emit unbraced `others` in the name list. Personal names with a given name and similarly named organizations retain their identities. The rule belongs at export because it handles already-stored records and each consumer needs a different spelling. No admission behavior or catalog record changes. A read-only scan of every source’s top-level creator arrays found zero records with family-name `others` in the current catalog.

CSL output adds `event` equal to `event-title`, using `setdefault` to avoid overwriting an existing value. The catalog schema currently admits only `event-title`; CSL import already translates the legacy alias and checks conflicting values. The schema is not expanded. Exported matching aliases import successfully.

Tests cover both sentinel spellings, both author/editor roles, real-name counterexamples, input preservation, presence/absence of event-title, and actual citeproc/IEEE, biber/authoryear and BibTeX/Elsevier rendering. A historical live-catalog regression now permits only the intentional event alias in its CSL comparison. The export contract shrank from 2,922 to 2,907 words while documenting both rules.

## Verification

- `uv run --locked pytest --require-tools -q`: **1,086 passed**, 35.55 seconds. `TEXMFVAR` and `TEXMFCACHE` pointed to writable scratch.
- `uv run --locked ruff check src tests`: clean.
- `uv run --locked ty check src`: clean. An initial unscoped invocation also checked archived experiments and tests and produced unrelated diagnostics; the source check is clean.
- `git diff --check`: clean.
- `uv run --locked python tests/fixtures/real-trial/conversion_check.py --all --work /private/tmp/refs-csl-fidelity/walk-complete`: exit 0, without `--record`. Quarto needed access to its existing cache after the sandboxed HTML render failed to open its cache database. All renders and exports were confined to scratch snapshots.

| Project | Consumer | Entries | Changed |
|---|---|---:|---:|
| jhl-report | quarto | 92 | 0 |
| jhl-report | site | 103 | 0 |
| jose-danvas | quarto | 11 | 0 |
| jose-danvas | jose | 11 | 0 |
| manufacturing-training-media-tradeoffs | html | 39 | 0 |
| manufacturing-training-media-tradeoffs | elsevier | 39 | 0 |

All 295 consumer entries match their accepted fixtures exactly. There are no changed entries requiring before/after transcription or attribution to either rule. The new synthetic consumer regressions exercise the affected cases that these fixtures do not expose. Full gate evidence is in `/private/tmp/refs-csl-fidelity/walk-complete/gate.json` and `gate.md`; test logs and arXiv research probes are under `/private/tmp/refs-csl-fidelity/`.

No accepted fixtures, publication files, catalog records or export targets were updated. No merge or arXiv implementation is included.
