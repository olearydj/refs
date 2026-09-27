# arXiv CSL export projection

This follow-up to the [first two fidelity fixes](2026-09-27-csl-fidelity-fixes.md) implements the owner’s decision “q3 - D”, relayed in `comms/2026-09-27-150051-s1-arxiv-option-d.md`. It is a new commit on `s2/csl-fidelity-fixes`; the dema-llm proposal remains unapproved and unrevised.

For an article with archive arXiv (case-insensitive) and an arXiv extension identifier, CSL export fills a missing publisher with arXiv and a missing number with that identifier. It removes archive only if it repeats the emitted publisher, comparing case-insensitively. Existing publisher and number values win, including conflicting values. This changes only the exported object; source records, admission and the Bib profiles are unchanged.

Contract tests cover each required condition independently, mixed-case repository names, a versioned identifier, stored publisher/number conflicts, redundant archive removal and input preservation. Actual IEEE and default Chicago consumer tests pin these strings for the GPT-4 example:

- IEEE: [1] OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023, arXiv: 2303.08774. doi: 10.48550/arxiv.2303.08774.
- Chicago: OpenAI. 2023. “GPT-4 Technical Report.” 2303.08774. Preprint, arXiv, March 27. https://doi.org/10.48550/arxiv.2303.08774.

The historical pre-identification-note regression still compares all BibLaTeX records against its old serializer. Its CSL comparison excludes arXiv identifiers, whose output now intentionally changes and is covered by the new contract and consumer tests; it continues to check the remaining records with the previously approved event alias exception.

## Verification

The full suite with `--require-tools` passed all **1,098 tests** in 44.16 seconds. Ruff (`src tests`), source type checking (`ty check src`), and whitespace checks pass. TeX cache variables pointed to `/private/tmp/refs-csl-fidelity/tex-cache`. Logs are in `/private/tmp/refs-csl-fidelity/arxiv-full-suite.log`.

The all-project conversion walk ran without `--record`, using scratch copies and the same Quarto cache access required in the previous pass. All 295 entries match their accepted fixtures exactly: jhl-report quarto 92 and site 103; jose-danvas quarto 11 and jose 11; manufacturing HTML 39 and Elsevier 39. There are no changed entries requiring before/after transcription. The affected arXiv case is exercised directly by the consumer tests above.

The complete gate is `/private/tmp/refs-csl-fidelity/walk-arxiv/gate.json` with a Markdown counterpart. No fixtures, live export targets, catalog records or publication files were changed. Nothing is merged or recorded.
