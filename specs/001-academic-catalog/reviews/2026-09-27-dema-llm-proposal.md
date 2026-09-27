# dema-llm conversion — revised proposal, 2026-09-27

**Proposal only; still awaiting approval.** This revision incorporates the owner decisions relayed in `comms/2026-09-27-153211-s1-dema-llm-revision-request.md`. The branch is rebased onto refs main `dbebb38`, version 0.9.1. It proposes 32 new records and reuse of two existing records, giving 34 project memberships. All 34 remain cited by the TDD; the PDD cites six. The plan has three export targets and four rendered gates.

The delivered PDD is frozen at `docs/pdd/delivered/DEMA-LLM-Overview-2026-01-18.pdf`, SHA-256 `7c0d19b66e2f71f530db212ab21ce5616db158f5a8b8f588a61131059d9d2f9d`; its README identifies source tag `icams-m-mbse-t5-m3.1`. That delivered file and tag remain untouched. Both working documents are now internal. Published versions therefore replace the selected preprints, and internal title case is the standing policy. The owner’s rule still forbids retroactive changes to published works without specific direction.

The first proposal’s arXiv probes were wrong: they validated records but serialized the noncanonical dictionaries. This revision uses the actual canonical results and the merged exporter. The et-al sentinel, legacy event alias and arXiv repository/id rules are now implemented in refs; conference-paper volumes and webpage years are accepted IEEE style behavior. A remaining speech-style omission is disclosed below rather than treated as fixed.

## Execution preconditions and backup

No backup, import, source acquisition, capture, attachment, live export, publication edit or fixture recording has occurred. All catalog connections use SQLite `mode=ro`; generated bibliography files and engine probes exist only in scratch. Metadata/page inspection is not a saved source capture.

The revision began at publication `46fda2a`; during the read-only checks its own session committed `c6c5ffb`, adding cited-standards instructions and an initial review. Bibliography, citation sources and consumer configuration remain unchanged. The owner’s uncommitted `.gitignore`, `docs/README.md`, `pyproject.toml` and `docs/dema-data-vocabulary-alignment.md` remain a precondition: the publication session must settle them and supply a clean commit before execution. Preserve `pre-pipyer`, the delivered PDD and manuscript prose. The two authorized TDD citation-key replacements occur only at adoption, in the same commit as the refs bibliography switch.

Proposed backup: `/Volumes/Casa/refs-backups/<execution-date>-before-dema-llm-conversion`. Validate that backup before catalog mutation. Recheck catalog bindings, citation inventory and source versions against the clean publication commit. The current legacy bibliography SHA-256 is `36d0f3823a43f42e16fab530e3255f21a4e1e60808333ca017ff9d7df19d395a`.

## Consumers and targets

`docs/references.bib` is the sole active bibliography source, shared by both documents. No independent writer or synchronization script was found. Its 34 entries comprise ten article, one incollection, seven inproceedings, twelve misc, one phdthesis and three techreport entries. Seven distinct records mention arXiv. The historical ZIP under `docs/legacy/` is not an active reader.

| Consumer | Current route | Proposed target/profile |
| --- | --- | --- |
| TDD HTML | `docs/tdd/_quarto.yml`, citeproc, `../csl/ieee.csl` | `docs/references-tdd.json`, `csl-json-v1` |
| TDD PDF | Same bibliography/CSL; XeLaTeX layout | Same TDD JSON; separate artifact gate |
| PDD DOCX | Format-local IEEE CSL in `docs/pdd/DEMA-LLM-Overview.qmd` | `docs/references-pdd.json`, `csl-json-v1` |
| PDD PDF | Format-local IEEE biblatex/biber, `backref=true` | `docs/references-pdd.bib`, `biblatex-v1` |

The proposed refs project is `dema-llm`. All targets export its 34 memberships; each document selects references through its citations. The PDD cites Sequeda, ReMatch, the three Ledford works and AI4SE. Its other 28 members remain available without appearing in the PDD bibliography.

At adoption, a root `.refs.toml` registers the targets. PDD routing becomes format-local and its shared legacy bibliography setting is removed, avoiding merged inputs. TDD changes `openai2024gpt4` to `openai2023gpt4` and `khattab2023dspy` to `khattab2024` in the same commit that switches its bibliography. The current BibTeX file lacks the new keys, so those changes must not precede adoption. Update `a6-references.qmd` and workflow documentation, and retire the legacy file only after every reader switches. Keep its complete bytes in publication history and preserve imported entry originals. Retain citation links, bibliography links and PDF backreferences. Use plain `quarto render` for the book, which builds both formats; a single-format live render can erase the other output.

## Intake and completion plan

A fresh dry run of the untouched BibTeX still predicts 34 new records. **Do not execute that unfiltered import.** Exclude the two replaced preprint entries from intake and cite the existing GPT-4 and DSPy records. Dry binding of the completed canonical candidates confirms 32 unbound new records and the two intended existing IDs, with no metadata conflicts. Add replacement context through guarded updates that preserve existing context. A simulated re-import of GPT-4 plus that context reports a context conflict; this is why the plan reuses and updates the record rather than importing it again. DSPy’s absent context would be a safe fill, but use the same explicit reuse workflow.

For new records, preserve assigned keys and original entry bytes, use English title case, retain existing brace protection, and protect technical names such as DEMA, AI, LLM/LLMs, GPT-4, ReMatch, DSPy, Nomic Embed, Llama 2, SQL, BERT, FedRAMP, CMMC, INCOSE and INFORMS. No whole-title preservation is proposed. Clear native labels that contradict an approved retype. Existing GPT-4 and DSPy metadata stays as stored; their replacement context and project membership are the planned changes.

Nine interpretation notes move verbatim into context: Sequeda, ReMatch, the three Ledford works, both Bloor reports, Bernstein/Haas and Oracle. These remain attributed input claims, not newly verified research conclusions. The INSIGHT forthcoming note moves to historical context separately. Five removed interpretation notes currently print in the PDD PDF; their disappearance is intentional if this proposal is approved.

| Input key → membership when changed | Planned type | Completion |
| --- | --- | --- |
| `sequeda2023` | paper-conference | GRADES-NDA 2024 publication; corrected title and Juan Sequeda, Dean Allemang, Bryon Jacob; ACM, June 9, pp. 1–12, DOI 10.1145/3661304.3661901. Context names replaced arXiv:2311.07509v1. |
| `sheetrit2024` | article | Proposed four-author preprint correction: Eitam Sheetrit, Menachem Brief, Moshik Mishaeli, Oren Elisha; remove unsupported SIGMOD/ACM; arXiv:2403.01567v2. |
| `ledford2023dissertation` | thesis | Retain degree, Auburn institution/place and 2023; protect DEMA; note to context. |
| `ledford2023ieee` | article-journal | Retain journal, DOI, volume/pages and 2023; note to context. |
| `ledford2025syseng` | article-journal | Retain issue-year 2025, DOI and pages; the vault’s 2024 filename does not change the year; note to context. |
| `oleary2025ai4se` | speech | Allison B. Ledford, supported by the slide cover, dissertation and IEEE paper; workshop speech with event and place; link relocated PDF. |
| `howard2007bloor` | report | Retain Bloor report, publisher and September 2007; note to context; primary file missing. |
| `howard2011bloor` | report | Retain Bloor report, publisher/year/genre; note to context; primary file missing. |
| `bernsteinhaas2008` | article-journal | Retain journal/DOI/pages; note to context. |
| `oracle2011migration` | report | Proposed report retype, White paper genre and Oracle publisher; retain 2012 despite key; note to context. |
| `oleary2025binary-classification` | speech | Full abstract title, INFORMS 2025 abstract 9229, October 28, Atlanta; poster speech; context explains that printed poster omits “Comprehensive”. |
| `olearyledford2026insight` | article-journal | Proposed published metadata: INSIGHT 29(3), 37–42, DOI 10.1002/inst.70055; obsolete forthcoming note to context. |
| `brown2020` | paper-conference | Proposed conference-paper retype; retain NeurIPS volume 33 and pages in metadata; IEEE volume omission accepted. |
| `wei2022` | paper-conference | Proposed conference-paper retype; retain NeurIPS volume 35 and pages in metadata; IEEE volume omission accepted. |
| `openai2024gpt4` → `openai2023gpt4` | article | Reuse openai2023gpt4 and its 2023 PDF/DOI/date; context names replaced arXiv:2303.08774v6 (2024); no new record or rekey. |
| `anthropic2024claude3` | report | March 2024 model card: The Claude 3 Model Family: Opus, Sonnet, Haiku; Anthropic report, Model card genre, PDF URL; fetch at execution. |
| `touvron2023llama2` | article | Preprint arXiv:2307.09288; retain truncated authors; select exact revision on acquisition. |
| `reimers2019` | paper-conference | Retain conference/pages; protect BERT. |
| `openai2024embeddings` | webpage | Current Vector Embeddings guide; canonical current URL; no issued year; capture and record actual accessed date at execution. |
| `nussbaum2024nomic` | article-journal | TMLR February 2025 publication under existing key; no invented volume/pages/DOI; context names replaced arXiv:2402.01613 (2024). |
| `guo2017` | paper-conference | Retain ICML/PMLR conference and pages. |
| `kadavath2022` | article | Preprint arXiv:2207.05221; retain truncated authors; select exact revision on acquisition. |
| `naeini2015` | paper-conference | Retain AAAI conference and pages. |
| `christophides2021` | article-journal | Retain journal/DOI/volume/issue/pages. |
| `mudgal2018` | paper-conference | Retain SIGMOD paper and pages; acquire cited proceedings version. |
| `konda2016` | article-journal | Retain PVLDB article and truncated authors; merged export prints et al. |
| `koutras2021valentine` | paper-conference | Retain ICDE 2021 proceedings identity, not the 2020 preprint. |
| `deb2014` | chapter | Retain 2014 chapter, book and pages; a mention in another paper is not a source file. |
| `zitzler2003` | article-journal | Retain journal/volume/issue/pages. |
| `khattab2023dspy` → `khattab2024` | paper-conference | Reuse khattab2024, ICLR 2024, State-of-the-Art Pipelines title; context names replaced arXiv:2310.03714 (2023); no new record. |
| `zhou2023ape` | paper-conference | Retain ICLR 2023 proceedings identity. |
| `nist2020sp80053` | report | Retain revision 5, report number and DOI; publisher is one literal institution, not a semicolon-separated list. |
| `fedramp2024` | webpage | Conditional: historical webpage versus a claims-supported current official document; see both outcomes below. |
| `dod2020cmmc` | document | Conditional: historical 2020 document versus a claims-supported current official document; see both outcomes below. |

Published Sequeda metadata comes from the publisher-deposited [Crossref record](https://api.crossref.org/works/10.1145/3661304.3661901), including its online publication date; the supplied 2023 key stays fixed. The [TMLR paper](https://openreview.net/pdf?id=IPmzyQSiQE) identifies February 2025. The [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html) match existing `khattab2024`. Each switched record’s context names the preprint it replaces.

ReMatch’s four authors and arXiv v2 identity are supported by the project PDF and [arXiv](https://arxiv.org/abs/2403.01567). No later venue was verified. The INSIGHT version of record supports its proposed volume/issue/pages and DOI. Those two metadata corrections still await approval.

The Claude 3 plan cites the March 2024 model card, not the [launch announcement](https://www.anthropic.com/news/claude-3-family); verify the fetched PDF is that edition before attachment. The [current OpenAI guide](https://developers.openai.com/api/docs/guides/embeddings) now calls itself Vector Embeddings. Its actual capture date belongs in accessed, never in issued. The preview deliberately omits accessed until the capture exists, so its final reference will gain the real access-date text.

### FedRAMP and CMMC: both pending outcomes

The dema-llm session is checking whether the TDD claims hold under current official documents. This proposal does not choose or invent those documents in advance.

| Key | If the claims support a current document | If they do not |
| --- | --- | --- |
| `fedramp2024` | Keep the key; use the named official document’s actual title, type, version/date and URL; capture/fetch at execution and record actual access. Re-probe its wording once identified. | Retain the supplied historical framework identity and year, proposed webpage type; acquire the intended historical page/version. A current homepage capture is not historical evidence. |
| `dod2020cmmc` | Keep the key; use the named official CMMC document’s actual title, type, version/date and URL; capture/fetch at execution and re-probe. | Retain the supplied 2020 framework/document identity; identify that historical version. A current program page is only a locator. |

The gate previews below show the historical branches. The current-document branches remain conditional and cannot be called rendered or approved until s1 forwards the claims check and concrete metadata. No live substitution is authorized by this revision.

## Source placement and acquisition

The earlier bounded search covered the project, DEMA vault, refs library and Downloads, including `_from2020mbp/devonthink`: 4,355 PDFs, prioritized by DOI then title/cover evidence. It did not exhaustively OCR image-only PDFs or inspect every archive. This revision rechecks the changed locations and recorded source hashes; it does not repeat an unrelated whole-disk search. No source was fetched or moved.

Seven source files are proposed as new links in place, with empty loc and their filenames retained. GPT-4 already has its selected source attached. The old Sequeda project PDF is the replaced preprint, so it stays where it is and is not represented as the ACM publication.

| Key | Source path | SHA-256 |
| --- | --- | --- |
| `sheetrit2024` | `/Volumes/Casa/dev/dema-llm/docs/research/references/sheetrit2024-rematch.pdf` | 5504fb5e12ce6c2ab6741850c9e46158e94f913519bf28e6395935823d4bd0dd |
| `ledford2023dissertation` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-dissertation.pdf` | 3a6bc4a2ca6d59e9f5d196ee445a2f36d496aa89c4c8dfe586684dc31dbc5911 |
| `ledford2023ieee` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-ieee-digital-thread.pdf` | ee87f864331b17360d25722fa8ede347956eb3d7819c1252ec12775964841fe8 |
| `ledford2025syseng` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2025-syseng.pdf` | 6883aaebae8248d4936eeb08b1cf2abb5136ae677c0c64ada6aa7c6e0ae1b13d |
| `oleary2025ai4se` | `/Volumes/Casa/pub/2025-ai4se-ai-enhanced-dema/AI4SE_AI_Enhanced_DEMA.pdf` | b2ea81187907cd0bed0f6bc4c6790acf001da2a93609e6117f41475cbecdf770 |
| `oleary2025binary-classification` | `/Volumes/Casa/pub/2025-informs-gradebot-poster/poster-oleary-informs25.pptx` | e9e3f5fb74e7235a51b8ab7459971a4d9a5a804a9336b30f78e06ee2df0ab35b |
| `olearyledford2026insight` | `/Volumes/Casa/pub/2026-insight-dema-llm/published/oleary-ledford-2026-insight-dema-llm-version-of-record.pdf` | 02567dceb4916267e82ef5f1b58bafcf340870c2215c38e037903090bc7d9af2 |
| `openai2023gpt4` | `/Volumes/Casa/refs/lib/papers/aiml/GPT4TechnicalReport-2023.pdf` | 5269ab4bab5dd064a39ecab221f79e13bbe0901f0000f8dad3416cdb493df8b4 |

The talk placement is settled: link the relocated files under `/Volumes/Casa/pub/`; do not move anything from Downloads. The INFORMS PPTX is the file sent for printing on 2025-10-28, confirmed by the owner’s decision. The selected GPT-4 source is March 27, 2023, matching the reused record, not a v6 attachment.

A local Brown candidate in `~/Downloads/_from2020mbp/Desktop/USB-stuff/Zotero Folder 2021-07-08/Brown et al_2020_Language Models are Few-Shot Learners.pdf` is arXiv v4, not a verified NeurIPS proceedings copy. It remains a candidate. The fetched-source plan below therefore has 26 outstanding keys, including the reused DSPy record, which has no attachment. A failed or denied fetch stays an explicit gap; the owner can supply an authorized copy. For new managed copies, use the CLI’s previewed filename and verified-copy rules under `unfiled`. Final destination names and hashes belong in the execution report; none exists yet.

| Key | Needed source | Locator |
| --- | --- | --- |
| `howard2007bloor` | 2007 report; exact primary locator unresolved, not a secondary marketing quotation | [Source](https://www.bloorresearch.com/) |
| `howard2011bloor` | 2011 report, not project market-context synthesis | [Source](https://www.bloorresearch.com/research/data-migration-2011/) |
| `bernsteinhaas2008` | Cited journal article; access unverified | [Source](https://doi.org/10.1145/1378727.1378745) |
| `oracle2011migration` | Supplied white-paper PDF URL; access unverified | [Source](https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf) |
| `brown2020` | NeurIPS 2020 version needed; local preprint is only a candidate | [Source](https://proceedings.neurips.cc/paper/2020) |
| `wei2022` | NeurIPS 2022 proceedings paper | [Source](https://proceedings.neurips.cc/paper_files/paper/2022) |
| `anthropic2024claude3` | March 2024 model card PDF; verify edition on acquisition | [Source](https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf) |
| `touvron2023llama2` | Preprint; select revision at acquisition | [Source](https://arxiv.org/abs/2307.09288) |
| `reimers2019` | ACL publisher full text available | [Source](https://aclanthology.org/D19-1410/) |
| `openai2024embeddings` | Capture current guide at execution, with actual accessed date | [Source](https://developers.openai.com/api/docs/guides/embeddings) |
| `nussbaum2024nomic` | TMLR February 2025 paper, not the 2024 preprint | [Source](https://openreview.net/pdf?id=IPmzyQSiQE) |
| `guo2017` | PMLR publisher full text available | [Source](https://proceedings.mlr.press/v70/guo17a.html) |
| `kadavath2022` | Preprint | [Source](https://arxiv.org/abs/2207.05221) |
| `naeini2015` | AAAI publisher full text available | [Source](https://ojs.aaai.org/index.php/AAAI/article/download/9602/9461) |
| `christophides2021` | Cited journal article; access unverified | [Source](https://doi.org/10.1145/3418896) |
| `mudgal2018` | Author-hosted SIGMOD paper; distinguish extended technical report | [Source](https://pages.cs.wisc.edu/~anhai/papers1/deepmatcher-sigmod18.pdf) |
| `konda2016` | Author project publication index; exact paper still to acquire | [Source](https://pages.cs.wisc.edu/~anhai/projects/magellan/research.html) |
| `koutras2021valentine` | Cited IEEE 2021 proceedings version | [Source](https://ieeexplore.ieee.org/document/9458921) |
| `deb2014` | Cited 2014 chapter; exact edition required | [Source](https://doi.org/10.1007/978-1-4614-6940-7_15) |
| `zitzler2003` | Cited 2003 journal paper; access unverified | [Source](https://doi.org/10.1109/TEVC.2003.810758) |
| `zhou2023ape` | ICLR paper; OpenReview can present a verification page | [Source](https://openreview.net/pdf?id=YdqwNaCLCx) |
| `nist2020sp80053` | Revision 5 as cited; do not silently use a later revision | [Source](https://doi.org/10.6028/NIST.SP.800-53r5) |
| `fedramp2024` | Historical source or claims-supported current official document; pending | [Source](https://www.fedramp.gov/) |
| `dod2020cmmc` | Historical 2020 document or claims-supported current document; pending | [Source](https://business.defense.gov/Programs/Cyber-Security-Resources/Cybersecurity-Maturity-Model-Certification/) |
| `sequeda2023` | GRADES-NDA 2024 version of record; local preprint is not this source | [Source](https://doi.org/10.1145/3661304.3661901) |
| `khattab2024` | ICLR 2024 publication; attach to existing record | [Source](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html) |

## Gate predictions

These are canonical-record previews, not accepted conversion gates. The revised pipeline runs the real BibTeX adapter and dry admission against the read-only catalog, applies the proposed completions, then uses `SourceCreate.canonical()`, the configured naming policy and a final canonical validation before export through refs 0.9.1. Existing records come from the catalog and retain their metadata. Matching arXiv numbers collapse into the identifier extension; the merged CSL exporter projects them back as number plus publisher without duplicating archive.

Fresh baseline citeproc output matches all 34 current TDD HTML entries and the six PDD DOCX reference paragraphs exactly. All 34 baseline strings also match the current TDD PDF after punctuation/whitespace normalization. Both baseline and candidate have 34 entries in the actual IEEE citeproc and native IEEE biber probes. Tools: Quarto 1.10.18, Pandoc 3.10, biber 2.21 and XeLaTeX/TeX Live 2026. Bibliography-only biber probes isolate wording; they do not certify full-document layout or backreference page numbers. The four complete artifact gates still run in scratch after approved execution.

Title case and acronym protection are expected policy changes, not findings. DOI case normalization is equivalent identity. Apart from those, the case-only TDD entries are the three Ledford works, both Bloor reports, Bernstein/Haas, Reimers, Guo, Naeini, Christophides, Mudgal, Konda, Koutras, Deb, Zitzler and Zhou. Konda’s et-al wording is now preserved. Every other TDD change is transcribed below; the same CSL wording applies to PDD DOCX for its six cited keys.

The remaining speech-style limit is explicit: IEEE CSL prints the event name after the fix, but not genre or event-place. Thus AI4SE’s workshop survives, while its George Washington University place and “Workshop presentation” genre are absent from CSL; biber retains them. INFORMS prints the event and full date but not “Poster presentation” or Atlanta. Accepting the retypes must include review of that presentation, not an assumption that every field prints. No further style or refs change is proposed here.

### `sequeda2023`

Before CSL: J. Sequeda, D. Briggs, and D. P. Miranker, “Benchmarking the text-to-SQL capability of large language models: A comprehensive evaluation,” arXiv preprint arXiv:2311.07509, 2023, Available: https://arxiv.org/abs/2311.07509

After CSL: J. Sequeda, D. Allemang, and B. Jacob, “A Benchmark to Understand the Role of Knowledge Graphs on Large Language Model’s Accuracy for Question Answering on Enterprise SQL Databases,” in Proceedings of the 7th Joint Workshop on Graph Data Management Experiences & Systems (GRADES) and Network Data Analytics (NDA), ACM, Jun. 2024, pp. 1–12. doi: 10.1145/3661304.3661901.

### `sheetrit2024`

Before CSL: E. Sheetrit, S. Nevo, T. Mazor, N. Nadler, F. Fournier, and A. Anaby-Tavor, “ReMatch: Retrieval enhanced schema matching with LLMs,” in Proceedings of the 2024 ACM SIGMOD international conference on management of data, ACM, 2024. Available: https://arxiv.org/abs/2403.01567

After CSL: E. Sheetrit, M. Brief, M. Mishaeli, and O. Elisha, “ReMatch: Retrieval Enhanced Schema Matching With LLMs,” 2024, arXiv: 2403.01567v2. Available: https://arxiv.org/abs/2403.01567

### `oleary2025ai4se`

Before CSL: D. J. O’Leary and A. N. Ledford, “AI-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes.” The George Washington University; Workshop Presentation, AI4SE & SE4AI Research and Application Workshop, Sep. 2025.

After CSL: D. J. O’Leary and A. B. Ledford, “AI-Enhanced DEMA: Transforming Implicit System Knowledge Into Intelligent, Compliant, and Documented Processes,” presented at the AI4SE & SE4AI Research and Application Workshop, Sep. 2025.

### `oracle2011migration`

Before CSL: Oracle, “Put your data first or your migration will come last.” White paper, 2012. Available: https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf

After CSL: Oracle, “Put Your Data First or Your Migration Will Come Last,” Oracle, White paper, 2012. Available: https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf

### `oleary2025binary-classification`

Before CSL: D. J. O’Leary, “Beyond binary classification: A comprehensive multi-criteria assessment system for programming assignments.” Poster presentation, INFORMS Annual Meeting, October 2025, Oct. 2025.

After CSL: D. J. O’Leary, “Beyond Binary Classification: A Comprehensive Multi-Criteria Assessment System for Programming Assignments,” presented at the INFORMS Annual Meeting, Oct. 28, 2025.

### `olearyledford2026insight`

Before CSL: D. J. O’Leary and A. B. Ledford, “Trustworthy LLM-augmented data reconciliation for deployment-constrained environments,” INSIGHT, 2026.

After CSL: D. J. O’Leary and A. B. Ledford, “Trustworthy LLM-Augmented Data Reconciliation for Deployment-Constrained Environments,” INSIGHT, vol. 29, no. 3, pp. 37–42, 2026, doi: 10.1002/inst.70055.

### `brown2020`

Before CSL: T. Brown et al., “Language models are few-shot learners,” Advances in Neural Information Processing Systems, vol. 33, pp. 1877–1901, 2020.

After CSL: T. Brown et al., “Language Models Are Few-Shot Learners,” in Advances in Neural Information Processing Systems, 2020, pp. 1877–1901.

### `wei2022`

Before CSL: J. Wei et al., “Chain-of-thought prompting elicits reasoning in large language models,” Advances in Neural Information Processing Systems, vol. 35, pp. 24824–24837, 2022.

After CSL: J. Wei et al., “Chain-of-Thought Prompting Elicits Reasoning in Large Language Models,” in Advances in Neural Information Processing Systems, 2022, pp. 24824–24837.

### `openai2024gpt4` → `openai2023gpt4`

Before CSL: OpenAI, “GPT-4 technical report.” arXiv:2303.08774v6, 2024. Available: https://arxiv.org/abs/2303.08774

After CSL: OpenAI, “GPT-4 Technical Report,” Mar. 27, 2023, arXiv: 2303.08774. doi: 10.48550/arxiv.2303.08774.

### `anthropic2024claude3`

Before CSL: Anthropic, “Claude 3 model card.” 2024. Available: https://www.anthropic.com/news/claude-3-family

After CSL: Anthropic, “The Claude 3 Model Family: Opus, Sonnet, Haiku,” Anthropic, Model card, Mar. 2024. Available: https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf

### `touvron2023llama2`

Before CSL: H. Touvron, L. Martin, K. Stone, et al., “Llama 2: Open foundation and fine-tuned chat models.” arXiv:2307.09288, 2023. Available: https://arxiv.org/abs/2307.09288

After CSL: H. Touvron, L. Martin, K. Stone, et al., “Llama 2: Open Foundation and Fine-Tuned Chat Models,” 2023, arXiv: 2307.09288. Available: https://arxiv.org/abs/2307.09288

### `openai2024embeddings`

Before CSL: OpenAI, “Text embedding models.” 2024. Available: https://platform.openai.com/docs/guides/embeddings

After CSL: OpenAI, “Vector Embeddings.” [Online]. Available: https://developers.openai.com/api/docs/guides/embeddings

### `nussbaum2024nomic`

Before CSL: Z. Nussbaum, J. X. Morris, B. Duderstadt, and A. Mulyar, “Nomic embed: Training a reproducible long context text embedder.” arXiv:2402.01613, 2024. Available: https://arxiv.org/abs/2402.01613

After CSL: Z. Nussbaum, J. X. Morris, B. Duderstadt, and A. Mulyar, “Nomic Embed: Training a Reproducible Long Context Text Embedder,” Transactions on Machine Learning Research, Feb. 2025, Available: https://openreview.net/forum?id=IPmzyQSiQE

### `kadavath2022`

Before CSL: S. Kadavath, T. Conerly, A. Askell, et al., “Language models (mostly) know what they know.” arXiv:2207.05221, 2022. Available: https://arxiv.org/abs/2207.05221

After CSL: S. Kadavath, T. Conerly, A. Askell, et al., “Language Models (Mostly) Know What They Know,” 2022, arXiv: 2207.05221. Available: https://arxiv.org/abs/2207.05221

### `khattab2023dspy` → `khattab2024`

Before CSL: O. Khattab et al., “DSPy: Compiling declarative language model calls into self-improving pipelines.” arXiv:2310.03714, 2023. Available: https://arxiv.org/abs/2310.03714

After CSL: O. Khattab et al., “DSPy: Compiling Declarative Language Model Calls Into State-of-the-Art Pipelines,” in International Conference on Learning Representations, 2024. Available: https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html

### `nist2020sp80053`

Before CSL: National Institute of Standards and Technology, “Security and privacy controls for information systems and organizations,” National Institute of Standards; Technology, NIST Special Publication 800-53, Revision 5, 2020. doi: 10.6028/NIST.SP.800-53r5.

After CSL: National Institute of Standards and Technology, “Security and Privacy Controls for Information Systems and Organizations,” National Institute of Standards and Technology, NIST Special Publication 800-53, Revision 5, 2020. doi: 10.6028/nist.sp.800-53r5.

### `fedramp2024`

Before CSL: Federal Risk and Authorization Management Program (FedRAMP), “FedRAMP security assessment framework.” 2024. Available: https://www.fedramp.gov/

After CSL: Federal Risk and Authorization Management Program (FedRAMP), “FedRAMP Security Assessment Framework.” [Online]. Available: https://www.fedramp.gov/

### `dod2020cmmc`

Before CSL: Department of Defense, “Cybersecurity maturity model certification (CMMC) framework.” 2020.

After CSL: Department of Defense, “Cybersecurity Maturity Model Certification (CMMC) Framework.” 2020.

### PDD PDF: six native biber comparisons

These six changes include the approved version/author choices and the still-proposed metadata corrections and note removals. The engine controls sentence case; protected technical names survive. Line wrapping and bibliography labels are omitted. Full-document backreferences remain an adoption check.

**`sequeda2023`**

Before biber: J. Sequeda, D. Briggs, and D. P. Miranker, “Benchmarking the text-to-sql capability of large language models: A comprehensive evaluation,” arXiv preprint arXiv:2311.07509, 2023, Key finding: GPT-4 achieves 16% accuracy zero-shot, 54% with Knowledge Graph context. [Online]. Available: https://arxiv.org/abs/2311.07509

After biber: J. Sequeda, D. Allemang, and B. Jacob, “A benchmark to understand the role of knowledge graphs on large language model’s accuracy for question answering on enterprise SQL databases,” in Proceedings of the 7th Joint Workshop on Graph Data Management Experiences & Systems (GRADES) and Network Data Analytics (NDA), ACM, Jun. 9, 2024, pp. 1–12. DOI: 10.1145/3661304.3661901 [Online]. Available: https://doi.org/10.1145/3661304.3661901

**`sheetrit2024`**

Before biber: E. Sheetrit, S. Nevo, T. Mazor, N. Nadler, F. Fournier, and A. Anaby-Tavor, “Rematch: Retrieval enhanced schema matching with llms,” in Proceedings of the 2024 ACM SIGMOD International Conference on Management of Data, State-of-the-art LLM schema matching achieving 42-73% accuracy, ACM, 2024. [Online]. Available: https://arxiv.org/abs/2403.01567

After biber: E. Sheetrit, M. Brief, M. Mishaeli, and O. Elisha, “ReMatch: Retrieval enhanced schema matching with LLMs,” 2024. arXiv: 2403.01567v2. [Online]. Available: https://arxiv.org/abs/2403.01567

**`ledford2023dissertation`**

Before biber: A. B. Ledford, “A data element mapping and analysis (dema) approach for implementing a complete digital thread,” Establishes DEMA as a technology-agnostic methodology for systematic data element capture and mapping, Ph.D. Dissertation, Auburn University, Auburn, AL, 2023. [Online]. Available: http://etd.auburn.edu/xmlui/handle/10415/8918

After biber: A. B. Ledford, “A data element mapping and analysis (DEMA) approach for implementing a complete digital thread,” Ph.D. Dissertation, Auburn University, Auburn, AL, 2023. [Online]. Available: http://etd.auburn.edu/xmlui/handle/10415/8918

**`ledford2023ieee`**

Before biber: A. B. Ledford, G. Harris, and G. Purdy, “Implementing a complete digital thread: The need for data element mapping and analysis,” IEEE Open Journal of Systems Engineering, vol. 1, pp. 139–152, 2023, Proposes DEMA as tool for identifying data elements at granularity necessary to connect digital threads. DOI: 10.1109/OJSE.2023.3325189 [Online]. Available: https://ieeexplore.ieee.org/document/10286971/

After biber: A. B. Ledford, G. Harris, and G. Purdy, “Implementing a complete digital thread: The need for data element mapping and analysis,” IEEE Open Journal of Systems Engineering, vol. 1, pp. 139–152, 2023. DOI: 10.1109/ojse.2023.3325189 [Online]. Available: https://ieeexplore.ieee.org/document/10286971/

**`ledford2025syseng`**

Before biber: A. Ledford, G. Harris, S. Askew, and G. Purdy, “Application of data element mapping and analysis for system definition to enable model-based systems engineering,” Systems Engineering, vol. 28, no. 1, pp. 15–28, 2025, Demonstrates DEMA application: 1600 vessel occurrences across 79 functions in 23 storage locations. DOI: 10.1002/sys.21776 [Online]. Available: https://incose.onlinelibrary.wiley.com/doi/10.1002/sys.21776

After biber: A. Ledford, G. Harris, S. Askew, and G. Purdy, “Application of data element mapping and analysis for system definition to enable model-based systems engineering,” Systems Engineering, vol. 28, no. 1, pp. 15–28, 2025. DOI: 10.1002/sys.21776 [Online]. Available: https://incose.onlinelibrary.wiley.com/doi/10.1002/sys.21776

**`oleary2025ai4se`**

Before biber: D. J. O’Leary and A. N. Ledford, Ai-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes, Workshop Presentation, AI4SE & SE4AI Research and Application Workshop, The George Washington University, Sep. 2025.

After biber: D. J. O’Leary and A. B. Ledford, “AI-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes,” Workshop presentation, presented at the AI4SE & SE4AI Research and Application Workshop (The George Washington University), Sep. 2025.

## Open decisions and stop point

1. Approve the source-supported ReMatch four-author/preprint correction and the INSIGHT published metadata.
2. Approve the nine interpretation-note moves, separate retirement of INSIGHT’s forthcoming note, and remaining semantic retypes. Review the disclosed IEEE speech genre/place omissions as part of those retypes. Brown/Wei volume omissions and webpage year behavior are already accepted.
3. Resolve the two conditional FedRAMP/CMMC source choices when s1 forwards the claims check. If current documents qualify, their concrete metadata and new render strings must replace the conditional branch before execution.
4. Approve the three targets, four artifact gates, 34 memberships (32 new plus two existing), seven new links in place and the 26-key acquisition list. Explicitly carry any remaining unavailable sources as gaps. The two talk locations are already settled.

The version choices, internal title case, Allison B. Ledford, full INFORMS title, talk placement, Claude model-card identity and current embeddings capture are decisions incorporated into the plan, not questions being asked again. Proposal approval, clean-publication readiness, later export-gate acceptance, fixture recording and adoption remain separate gates owned by the review session and owner.

## Verification and evidence

The merged fix worktree was removed; `s2/dema-llm-proposal` is the remaining isolated worktree for this report. No code or publication changes are part of the branch. Scratch evidence in `/private/tmp/refs-dema-revision/` contains fresh `assessment.json`, `planned-binding.json`, canonical `planned-records.json`, serializer outputs, four per-key engine maps, citation inventory, current-artifact extractions and source hashes. The two existing-record context outcomes are disclosed above rather than counted as silent merges. No unrelated product suite was run for this proposal-only revision.

Final verification: 960 of the 962 initial input hashes match, including the catalog database, all citation inputs and rendered artifacts, the delivered PDD and relocated talks. The only changed initial files are AGENTS.md and CLAUDE.md in the publication session’s `c6c5ffb` commit; this session wrote neither. Publication dirty status is unchanged. All ten removed note values survive in proposed context, including the separate INSIGHT note, and the canonical records are stable on revalidation.

This revision replaces the original report rather than appending another plan. **Stop at conversion-guide step 4:** send it to s1 for the owner’s approval; do not execute intake or adoption.
