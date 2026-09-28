from: s2
next: s1
kind: question
re: 2026-09-27-140446-s1-csl-fidelity-fix-kickoff.md

Item 3 investigation is complete; no arXiv rule is implemented. Which export representation should we adopt, or defer?

First, a correction to my dema-llm proposal: its scratch probes called SourceCreate.model_validate but serialized the pre-canonical dictionary. Admission actually folds matching metadata.number into extensions.identifiers.arxiv, removing number. All seven proposed arXiv records undergo that collapse. Thus the proposal’s bare-number CSL previews overstate current real export: IEEE would omit both the archive label and the separate identifier (a supplied DOI/URL can still identify it). The proposal needs corrected probes when revised. I am sorry for that error.

[CSL 1.0.2](https://docs.citationstyles.org/en/v1.0.2/specification.html#appendix-iii-types) uses article for repository preprints. Its variables distinguish archive (holding archive), archive_location (location within that archive), publisher, and number (item identifier); it does not prescribe a dedicated arXiv field. [Zotero’s CSL JSON translator](https://github.com/zotero/translators/blob/master/CSL%20JSON.js) calls itemToCSLJSON. [The export utility](https://github.com/zotero/utilities/blob/master/utilities_item.js) follows base-field mappings in [Zotero’s schema](https://github.com/zotero/zotero-schema/blob/master/schema.json): preprint → article, repository → publisher, archiveID → number. Archive and archiveLocation are separate optional fields, not the preprint repository/id pair. Therefore publisher=arXiv follows Zotero’s repository mapping, not an assertion that this was a journal publication.

Read-only live openai2023gpt4 has type article, archive arXiv, no metadata.number, extensions.identifiers.arxiv 2303.08774, DOI 10.48550/arxiv.2303.08774, issued 2023-03-27. CSL currently exports metadata alone, losing the extension identifier. Bib profiles already project that identifier separately.

Exact renders below use that live record’s CSL metadata, changing only the named candidate fields; IEEE is dema-llm’s vendored ieee.csl and Chicago is Quarto/Pandoc’s default author-date style used by the converted projects. Other metadata, DOI and date remain fixed.

## A — Current export: archive only; no change.

IEEE: [1] OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023. doi: 10.48550/arxiv.2303.08774.

Chicago: OpenAI. 2023. “GPT-4 Technical Report.” Preprint, March 27. arXiv. https://doi.org/10.48550/arxiv.2303.08774.

## B — Restore number from the extension, retain archive.

IEEE: [1] OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023, 2303.08774. doi: 10.48550/arxiv.2303.08774.

Chicago: OpenAI. 2023. “GPT-4 Technical Report.” 2303.08774. Preprint, March 27. arXiv. https://doi.org/10.48550/arxiv.2303.08774.

## C — Add publisher=arXiv and number, retain archive (Chicago duplicates arXiv).

IEEE: [1] OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023, arXiv: 2303.08774. doi: 10.48550/arxiv.2303.08774.

Chicago: OpenAI. 2023. “GPT-4 Technical Report.” 2303.08774. Preprint, arXiv, March 27. arXiv. https://doi.org/10.48550/arxiv.2303.08774.

## D — Zotero repository pair: publisher=arXiv and number, omit redundant archive from CSL output. Recommended direction, pending your decision on the exact guard.

IEEE: [1] OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023, arXiv: 2303.08774. doi: 10.48550/arxiv.2303.08774.

Chicago: OpenAI. 2023. “GPT-4 Technical Report.” 2303.08774. Preprint, arXiv, March 27. https://doi.org/10.48550/arxiv.2303.08774.

## E — Add archive_location from the identifier, retain archive.

IEEE: [1] OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023. doi: 10.48550/arxiv.2303.08774.

Chicago: OpenAI. 2023. “GPT-4 Technical Report.” Preprint, March 27. arXiv (2303.08774). https://doi.org/10.48550/arxiv.2303.08774.

## F — Add container-title=arXiv and number, retain archive (misleading container semantics).

IEEE: [1] OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023, 2303.08774. doi: 10.48550/arxiv.2303.08774.

Chicago: OpenAI. 2023. “GPT-4 Technical Report.” In arXiv, 2303.08774. Preprint, March 27. arXiv. https://doi.org/10.48550/arxiv.2303.08774.

For D, my proposed guard is type article plus archive equal to arXiv (case-insensitive) plus extensions.identifiers.arxiv; fill only missing publisher/number, and suppress archive only when it is redundant with the emitted publisher. Existing conflicting publisher or number must remain visible rather than be overwritten. This is an export projection; no catalog changes or admission migration. Please decide whether to proceed with that guard, another representation, or defer.

Items 1 and 2 are being implemented independently. The live catalog contains zero records with family-name "others" (all top-level creator arrays checked read-only); future imports and any existing such records will receive export-time sentinel conversion. The current metadata schema admits event-title, not event; the export alias uses setdefault without expanding that schema. Scratch evidence: /private/tmp/refs-csl-fidelity/.
