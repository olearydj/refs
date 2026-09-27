# dema-llm conversion — second revised proposal, 2026-09-27

**Proposal only; awaiting approval.** This rewrite incorporates the owner decisions relayed in `comms/2026-09-27-163652-s1-source-links-and-second-revision.md` and the subsequent CMMC Model Overview decision in `comms/2026-09-27-165510-s1-cmmc-model-overview.md`. It is based on refs `4af508a`, version 0.9.2, with unnamed source links merged. The plan has **37 catalog records: 35 new and two existing**, **34 cited project memberships**, one `csl-json-v1` target and four artifact gates. Three preprints remain separately identifiable, attached and linked to their publications; they are catalog records outside this project’s cited membership.

The delivered PDD remains frozen at `docs/pdd/delivered/DEMA-LLM-Overview-2026-01-18.pdf`, SHA-256 `7c0d19b66e2f71f530db212ab21ce5616db158f5a8b8f588a61131059d9d2f9d`, source tag `icams-m-mbse-t5-m3.1`. The working TDD/PDD are internal; title case and the selected published versions apply to those working documents. The owner’s other works and second INSIGHT article are deferred to the CV pass.

## Execution preconditions and backup

No backup, catalog mutation, acquisition, source capture, live export, publication edit or fixture recording has occurred. SQLite connections are read-only; generated bibliographies and rendering probes exist only in scratch. Page inspection is not a saved capture.

Publication HEAD is `8c28e25`, including the standards check from `c6c5ffb`. The owner’s dirty `.gitignore`, `docs/README.md`, `pyproject.toml` and untracked `docs/dema-data-vocabulary-alignment.md` must be settled by its session before execution, which starts from a clean supplied commit. Preserve `pre-pipyer`, delivered artifacts and manuscript prose except the authorized citation-key changes at adoption. Source links are available in refs 0.9.2; no registry expansion is needed for the selected sources.

Proposed backup: `/Volumes/Casa/refs-backups/<execution-date>-before-dema-llm-conversion`. Validate the backup before mutation and recheck bindings, citation inventory and source versions. The legacy bibliography SHA-256 is `36d0f3823a43f42e16fab530e3255f21a4e1e60808333ca017ff9d7df19d395a`.

## Consumers and adoption

`docs/references.bib` is the sole active input; no independent writer or sync script was found. Its 34 entries are all cited by the TDD. The PDD cites Sequeda, ReMatch, the three Ledford works and AI4SE. The legacy ZIP is not an active reader.

| Consumer | Current engine/configuration | Proposed route |
| --- | --- | --- |
| TDD HTML | Citeproc, `docs/tdd/_quarto.yml` | IEEE citeproc, `docs/references.json` |
| TDD PDF | Same citeproc settings, XeLaTeX layout | Same target; separate artifact gate |
| PDD DOCX | Format-local IEEE CSL in `docs/pdd/DEMA-LLM-Overview.qmd` | Same citeproc and target |
| PDD PDF | IEEE biblatex/biber, `backref=true` | Switch to IEEE citeproc and the same target |

Register project `dema-llm` and one `csl-json-v1` target in root `.refs.toml`. Every consumer reads `docs/references.json` through the appropriate relative path. Remove PDD PDF’s biblatex/backend/backref settings and ensure it selects the same `docs/csl/ieee.csl`. PDF backreferences are intentionally lost with the owner-approved engine switch; investigation of citeproc support is already in the ledger. Keep citation and bibliography hyperlinks.

At adoption, replace the following citation keys in both working documents wherever present, in the same publication commit as the bibliography switch. Sequeda occurs in both documents; the other three replacements occur in the TDD. Do not change keys before the new bibliography exists.

| Former citation | Adopted citation |
| --- | --- |
| `sequeda2023` | `sequeda-2024-benchmarkUnderstand` |
| `nussbaum2024nomic` | `nussbaum-2025-nomicEmbed` |
| `khattab2023dspy` | `khattab2024` |
| `openai2024gpt4` | `openai2023gpt4` |

Update `a6-references.qmd` and workflow documentation; retire the legacy bibliography only after all readers switch, retaining its bytes in publication history and original imported entries. Use plain `quarto render` for the TDD book to build both formats: single-format live renders can erase the other output. Adoption and complete rendering belong to the publication session after the owner’s gates.

## Intake and record plan

The fresh unfiltered BibTeX dry run still predicts 34 new records; **do not execute it unchanged**. Exclude the GPT-4 input from new intake and reuse `openai2023gpt4`, preserving its stored metadata and attachment. Retain the three original preprint entries, add new Sequeda and Nomic publication records, and reuse existing `khattab2024`. Completed canonical dry binding confirms all 37 records: 35 new and the two intended existing records, with no metadata conflicts. No existing metadata is overwritten. Append context with revision-guarded updates: simulated re-import of GPT-4’s existing plus proposed context conflicts, so this is explicit reuse, not an import merge.

Preserve assigned keys and each imported entry’s original bytes. New publication keys above come from the configured naming policy and are unbound in the current catalog; recheck collisions at execution. Normalize new English titles and retain brace protection for technical names. Clear native labels that contradict retypes. The earlier arXiv preview bug is corrected: canonical validation collapses matching number into the identifier extension, and the merged exporter projects the repository/id without duplication. Never serialize the pre-canonical dictionary.

Nine interpretation notes move verbatim to import-attributed context: Sequeda, ReMatch, the three Ledford works, both Bloor reports, Bernstein/Haas and Oracle. INSIGHT’s forthcoming note moves to historical context. Their text remains attributed input, not a newly verified research claim. All ten values survive in the proposed records.

| Record(s) | Type and completion |
| --- | --- |
| `sequeda2023` | article; retain arXiv:2311.07509v1 and the local PDF. Correct title and authors Juan F. Sequeda, Dean Allemang, Bryon Jacob; explicitly identify as preprint in context. |
| `sequeda-2024-benchmarkUnderstand` | paper-conference; separate GRADES-NDA 2024 publication, Juan Sequeda, Dean Allemang, Bryon Jacob; ACM, June 9, pp. 1–12, DOI 10.1145/3661304.3661901. Fetch the publication. |
| `nussbaum2024nomic` | article; retain arXiv:2402.01613 as preprint and fetch its PDF. |
| `nussbaum-2025-nomicEmbed` | article-journal; separate TMLR February 2025 publication, OpenReview IPmzyQSiQE; no invented volume/pages/DOI. Fetch its PDF. |
| `khattab2023dspy / khattab2024` | Retain article preprint arXiv:2310.03714; reuse the ICLR 2024 paper-conference. Fetch both versions separately. |
| `openai2023gpt4` | Reuse existing article and March 27, 2023 PDF/DOI/date, OpenAI’s requested citation. Context names the former TDD arXiv v6 (2024); no v6 record. |
| `sheetrit2024` | article; approved four authors Eitam Sheetrit, Menachem Brief, Moshik Mishaeli, Oren Elisha, arXiv:2403.01567v2; remove the hallucinated SIGMOD/ACM identity. |
| `ledford2023dissertation` | thesis; retain degree, Auburn institution/place and 2023; protect DEMA; note to context. |
| `ledford2023ieee / ledford2025syseng` | article-journal; retain journal/DOI/pages. Keep Systems Engineering issue-year 2025 despite the vault’s 2024 filename; notes to context. |
| `oleary2025ai4se` | speech; Allison B. Ledford; AI4SE & SE4AI Research and Application Workshop, September 2025. Proposed event-place Washington, DC, USA; George Washington University in context. |
| `oleary2025binary-classification` | speech; full abstract title including Comprehensive; INFORMS Annual Meeting, abstract 9229, October 28, 2025. Proposed event-place Atlanta, GA, USA; context explains the shorter printed title. |
| `howard2007bloor / howard2011bloor` | report; retain Bloor publisher, dates and genre; notes to context; primary files missing. |
| `bernsteinhaas2008` | article-journal; retain journal/DOI/pages; note to context. |
| `oracle2011migration` | report, White paper genre, Oracle publisher; retain 2012 despite key; note to context. |
| `olearyledford2026insight` | article-journal; approved INSIGHT 29(3), 37–42, DOI 10.1002/inst.70055; historical forthcoming note to context. |
| `brown2020 / wei2022` | paper-conference; retain NeurIPS volume 33/35 and pages in metadata; IEEE’s volume omission is accepted. |
| `anthropic2024claude3` | report, Model card genre; March 2024, The Claude 3 Model Family: Opus, Sonnet, Haiku, Anthropic, model-card PDF URL. |
| `touvron2023llama2 / kadavath2022` | article; arXiv:2307.09288 / 2207.05221, truncated author lists retained; pin revision on acquisition. |
| `openai2024embeddings` | webpage; current Vector Embeddings guide and canonical URL; no issued year, actual accessed date only when captured. |
| `reimers2019 / guo2017 / naeini2015 / mudgal2018 / koutras2021valentine / zhou2023ape` | paper-conference; retain cited venue/pages and publication identity, including IEEE 2021 Valentine and ICLR 2023 APE; protect BERT. |
| `christophides2021 / konda2016 / zitzler2003` | article-journal; retain journal/volume/issue/pages/DOI where supplied; Konda’s truncated authors export as et al. |
| `deb2014` | chapter; retain 2014 book/chapter/pages; a mention in another paper is not a source file. |
| `nist2020sp80053` | report; retain Revision 5, report number and DOI; one literal NIST publisher. Context records checked control-catalog release 5.2.0. |
| `fedramp2024` | report; FedRAMP Consolidated Rules for 2026, U.S. General Services Administration, release 2026.09.22.01 (September 22, 2026). Keep key. |
| `dod2020cmmc` | report; Cybersecurity Maturity Model Certification (CMMC) Model Overview, version 2.13, September 2024, DoD-CIO-00001, DoD Chief Information Officer publisher. Context names the binding regulation. Keep key. |

Use `refs update PREPRINT --link PUBLICATION --if-revision N` for each of the three version pairs, after both sources exist; refresh revisions between mutations. `show` must display each link in both directions. Attach each version to its own record. The approved links are unnamed and catalog-only; they do not affect exports.

Published identity evidence: [Sequeda’s publisher-deposited Crossref record](https://api.crossref.org/works/10.1145/3661304.3661901), [Nomic’s TMLR paper](https://openreview.net/pdf?id=IPmzyQSiQE), and [DSPy’s ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html). ReMatch’s context records s1’s verified [arXiv evidence](https://arxiv.org/abs/2403.01567): four authors, v2 revised May 30, 2024, no journal reference or DOI; a bounded search found no venue and an EMNLP 2025 industry-track paper cites it as a preprint. The correction is approved, not a pending identity choice.

Verify the Claude PDF is the March model card before attachment; the launch announcement is not that source. Current web captures gain their actual access dates at execution, so their final references will add access-date text absent from these previews.

### Standards

The approved targets follow `docs/reports/2026-09-27-standards-check.md` at publication `c6c5ffb` and the owner’s subsequent choice of the CMMC Model Overview. That report identifies partial/unsupported manuscript claims; citation correction does not establish compliance or authorize prose repair.

FedRAMP is proposed as a report because the source is a versioned official requirements document. Its exact release is both the report number (`Release 2026.09.22.01`) and version, so IEEE prints the edition. CMMC now cites the actual DoD CIO report, version 2.13, September 2024, DoD-CIO-00001. The owner selected that document instead of admitting regulation; this is a source change, not a rule mislabeled as a report. Its context names 32 CFR Part 170, final rule 89 FR 83214, published October 15, 2024, effective December 16, 2024, as the binding rule, and records that CSL regulation remains deferred. The ledger note belongs to s1.

The CIO site refused direct retrieval in the standards check. Put the PDF on the acquisition list as a possible owner-assisted fetch and verify version 2.13 before attachment. IEEE prints its report number and date but omits the separate version field; the version remains in metadata/context and must match the retained PDF. No legal-type admission or regulation-specific style edit is part of this proposal.

## Source placement and acquisition

The prior bounded search covered 4,355 PDFs in the project, DEMA vault, refs library and Downloads, including `_from2020mbp/devonthink`; it prioritized DOI and title/cover evidence, without exhaustive OCR or archive inspection. This revision rechecks the known paths and hashes. No source was downloaded or moved.

Eight source files become links in place with empty loc and preserved filenames; GPT-4 already has its selected attachment. Sequeda’s local preprint is now explicitly attached to its retained preprint record, never mislabeled as the publication.

| Key | Source path | SHA-256 |
| --- | --- | --- |
| `sequeda2023` | `/Volumes/Casa/dev/dema-llm/docs/research/references/sequeda2023-llm-text-to-sql.pdf` | 1a0cb23795bea7f11c64b7f700d9088d2d08b004f7117951030733c8b0ee45c6 |
| `sheetrit2024` | `/Volumes/Casa/dev/dema-llm/docs/research/references/sheetrit2024-rematch.pdf` | 5504fb5e12ce6c2ab6741850c9e46158e94f913519bf28e6395935823d4bd0dd |
| `ledford2023dissertation` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-dissertation.pdf` | 3a6bc4a2ca6d59e9f5d196ee445a2f36d496aa89c4c8dfe586684dc31dbc5911 |
| `ledford2023ieee` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-ieee-digital-thread.pdf` | ee87f864331b17360d25722fa8ede347956eb3d7819c1252ec12775964841fe8 |
| `ledford2025syseng` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2025-syseng.pdf` | 6883aaebae8248d4936eeb08b1cf2abb5136ae677c0c64ada6aa7c6e0ae1b13d |
| `oleary2025ai4se` | `/Volumes/Casa/pub/2025-ai4se-ai-enhanced-dema/AI4SE_AI_Enhanced_DEMA.pdf` | b2ea81187907cd0bed0f6bc4c6790acf001da2a93609e6117f41475cbecdf770 |
| `oleary2025binary-classification` | `/Volumes/Casa/pub/2025-informs-gradebot-poster/poster-oleary-informs25.pptx` | e9e3f5fb74e7235a51b8ab7459971a4d9a5a804a9336b30f78e06ee2df0ab35b |
| `olearyledford2026insight` | `/Volumes/Casa/pub/2026-insight-dema-llm/published/oleary-ledford-2026-insight-dema-llm-version-of-record.pdf` | 02567dceb4916267e82ef5f1b58bafcf340870c2215c38e037903090bc7d9af2 |
| `openai2023gpt4` | `/Volumes/Casa/refs/lib/papers/aiml/GPT4TechnicalReport-2023.pdf` | 5269ab4bab5dd064a39ecab221f79e13bbe0901f0000f8dad3416cdb493df8b4 |

The talk locations are settled; nothing moves from Downloads. The INFORMS PPTX is the owner-confirmed file sent for printing on October 28, 2025. GPT-4’s attachment is the selected 2023 edition. The local Brown file under `~/Downloads/_from2020mbp/Desktop/USB-stuff/Zotero Folder 2021-07-08/` is an arXiv v4 candidate, not a verified NeurIPS proceedings copy.

The remaining **28 keys** need acquisition, including both Nomic/DSPy versions. Use previewed convention filenames, verified-copy rules and managed `unfiled` placement. Record final destinations, versions and hashes in the execution report. Failed/denied fetches remain explicit gaps; an authorized owner-supplied copy can resolve them.

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
| `nussbaum-2025-nomicEmbed` | TMLR February 2025 paper, not the 2024 preprint | [Source](https://openreview.net/pdf?id=IPmzyQSiQE) |
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
| `fedramp2024` | Consolidated Rules for 2026, release 2026.09.22.01; capture selected release | [Source](https://www.fedramp.gov/2026/) |
| `dod2020cmmc` | Model Overview v2.13, DoD-CIO-00001; CIO retrieval refused, possible owner fetch | [Source](https://dodcio.defense.gov/Portals/0/Documents/CMMC/ModelOverviewv2.pdf) |
| `sequeda-2024-benchmarkUnderstand` | GRADES-NDA 2024 version of record; local preprint is not this source | [Source](https://doi.org/10.1145/3661304.3661901) |
| `khattab2024` | ICLR 2024 publication; attach to existing record | [Source](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html) |
| `nussbaum2024nomic` | Retained arXiv preprint, separate attachment | [Source](https://arxiv.org/abs/2402.01613) |
| `khattab2023dspy` | Retained arXiv preprint, separate attachment | [Source](https://arxiv.org/abs/2310.03714) |

## Gate predictions and proposed speech-style edit

The proposed edit belongs only in dema-llm’s vendored `docs/csl/ieee.csl`, applied by that session at adoption if approved. In the publisher macro’s final branch, replace its publisher-place text node with this fallback; keep the surrounding publisher group unchanged:

```xml
<choose>
  <if variable="publisher-place">
    <text variable="publisher-place"/>
  </if>
  <else-if type="speech">
    <text variable="event-place"/>
  </else-if>
</choose>
```

It preserves publisher-place precedence and changes only the two speech references in the 34-entry project probe. Both cities print below. Speech genre remains absent from IEEE CSL; it stays in metadata. The exact scratch diff is `ieee-proposed.diff`.

Fresh baseline citeproc reproduces the previous 34-entry baseline exactly; that baseline was checked against TDD HTML, normalized PDF and six PDD DOCX references. The candidate has all 34 project entries exported from canonically validated records. This is a bibliography preview, not an accepted full-document gate. Three retained preprints are excluded from cited membership but canonically validated. Full TDD HTML/PDF and PDD DOCX/PDF gates remain for approved execution. The PDD PDF gate compares existing biber against candidate citeproc, including layout, numbering, links and the intentional loss of backreferences.

Title case/acronym protection and equivalent DOI case normalization are expected. Apart from those, the three Ledford entries, both Bloor reports, Bernstein/Haas, Reimers, Guo, Naeini, Christophides, Mudgal, Konda, Koutras, Deb, Zitzler and Zhou retain their TDD wording; Konda’s et-al sentinel survives. All other TDD changes follow. Access-date text awaits real captures.

### `sequeda2023` → `sequeda-2024-benchmarkUnderstand`

Before CSL: J. Sequeda, D. Briggs, and D. P. Miranker, “Benchmarking the text-to-SQL capability of large language models: A comprehensive evaluation,” arXiv preprint arXiv:2311.07509, 2023, Available: https://arxiv.org/abs/2311.07509

After CSL: J. Sequeda, D. Allemang, and B. Jacob, “A Benchmark to Understand the Role of Knowledge Graphs on Large Language Model’s Accuracy for Question Answering on Enterprise SQL Databases,” in Proceedings of the 7th Joint Workshop on Graph Data Management Experiences & Systems (GRADES) and Network Data Analytics (NDA), ACM, Jun. 2024, pp. 1–12. doi: 10.1145/3661304.3661901.

### `sheetrit2024`

Before CSL: E. Sheetrit, S. Nevo, T. Mazor, N. Nadler, F. Fournier, and A. Anaby-Tavor, “ReMatch: Retrieval enhanced schema matching with LLMs,” in Proceedings of the 2024 ACM SIGMOD international conference on management of data, ACM, 2024. Available: https://arxiv.org/abs/2403.01567

After CSL: E. Sheetrit, M. Brief, M. Mishaeli, and O. Elisha, “ReMatch: Retrieval Enhanced Schema Matching With LLMs,” 2024, arXiv: 2403.01567v2. Available: https://arxiv.org/abs/2403.01567

### `oleary2025ai4se`

Before CSL: D. J. O’Leary and A. N. Ledford, “AI-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes.” The George Washington University; Workshop Presentation, AI4SE & SE4AI Research and Application Workshop, Sep. 2025.

After CSL: D. J. O’Leary and A. B. Ledford, “AI-Enhanced DEMA: Transforming Implicit System Knowledge Into Intelligent, Compliant, and Documented Processes,” presented at the AI4SE & SE4AI Research and Application Workshop, Washington, DC, USA, Sep. 2025.

### `oracle2011migration`

Before CSL: Oracle, “Put your data first or your migration will come last.” White paper, 2012. Available: https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf

After CSL: Oracle, “Put Your Data First or Your Migration Will Come Last,” Oracle, White paper, 2012. Available: https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf

### `oleary2025binary-classification`

Before CSL: D. J. O’Leary, “Beyond binary classification: A comprehensive multi-criteria assessment system for programming assignments.” Poster presentation, INFORMS Annual Meeting, October 2025, Oct. 2025.

After CSL: D. J. O’Leary, “Beyond Binary Classification: A Comprehensive Multi-Criteria Assessment System for Programming Assignments,” presented at the INFORMS Annual Meeting, Atlanta, GA, USA, Oct. 28, 2025.

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

### `nussbaum2024nomic` → `nussbaum-2025-nomicEmbed`

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

After CSL: U.S. General Services Administration, “FedRAMP Consolidated Rules for 2026,” U.S. General Services Administration, Release 2026.09.22.01, Sep. 2026. Available: https://www.fedramp.gov/2026/

### `dod2020cmmc`

Before CSL: Department of Defense, “Cybersecurity maturity model certification (CMMC) framework.” 2020.

After CSL: Department of Defense Chief Information Officer, “Cybersecurity Maturity Model Certification (CMMC) Model Overview,” Department of Defense Chief Information Officer, DoD-CIO-00001, Sep. 2024. Available: https://dodcio.defense.gov/Portals/0/Documents/CMMC/ModelOverviewv2.pdf

### PDD PDF: biber to citeproc

These are exact bibliography-only engine strings, without numeric labels. The unchanged baseline input permits reuse of the prior biber extraction. The candidate uses the same citeproc output shown above, including the proposed speech fallback. Five interpretation notes disappear, source/author corrections apply, and IEEE CSL changes punctuation, title case, DOI/URL presentation and date precision. Full-document layout still needs its gate.

**`sequeda2023`**

Before biber: J. Sequeda, D. Briggs, and D. P. Miranker, “Benchmarking the text-to-sql capability of large language models: A comprehensive evaluation,” arXiv preprint arXiv:2311.07509, 2023, Key finding: GPT-4 achieves 16% accuracy zero-shot, 54% with Knowledge Graph context. [Online]. Available: https://arxiv.org/abs/2311.07509

After citeproc: J. Sequeda, D. Allemang, and B. Jacob, “A Benchmark to Understand the Role of Knowledge Graphs on Large Language Model’s Accuracy for Question Answering on Enterprise SQL Databases,” in Proceedings of the 7th Joint Workshop on Graph Data Management Experiences & Systems (GRADES) and Network Data Analytics (NDA), ACM, Jun. 2024, pp. 1–12. doi: 10.1145/3661304.3661901.

**`sheetrit2024`**

Before biber: E. Sheetrit, S. Nevo, T. Mazor, N. Nadler, F. Fournier, and A. Anaby-Tavor, “Rematch: Retrieval enhanced schema matching with llms,” in Proceedings of the 2024 ACM SIGMOD International Conference on Management of Data, State-of-the-art LLM schema matching achieving 42-73% accuracy, ACM, 2024. [Online]. Available: https://arxiv.org/abs/2403.01567

After citeproc: E. Sheetrit, M. Brief, M. Mishaeli, and O. Elisha, “ReMatch: Retrieval Enhanced Schema Matching With LLMs,” 2024, arXiv: 2403.01567v2. Available: https://arxiv.org/abs/2403.01567

**`ledford2023dissertation`**

Before biber: A. B. Ledford, “A data element mapping and analysis (dema) approach for implementing a complete digital thread,” Establishes DEMA as a technology-agnostic methodology for systematic data element capture and mapping, Ph.D. Dissertation, Auburn University, Auburn, AL, 2023. [Online]. Available: http://etd.auburn.edu/xmlui/handle/10415/8918

After citeproc: A. B. Ledford, “A Data Element Mapping and Analysis (DEMA) Approach for Implementing a Complete Digital Thread,” Ph.D. Dissertation, Auburn University, Auburn, AL, 2023. Available: http://etd.auburn.edu/xmlui/handle/10415/8918

**`ledford2023ieee`**

Before biber: A. B. Ledford, G. Harris, and G. Purdy, “Implementing a complete digital thread: The need for data element mapping and analysis,” IEEE Open Journal of Systems Engineering, vol. 1, pp. 139–152, 2023, Proposes DEMA as tool for identifying data elements at granularity necessary to connect digital threads. DOI: 10.1109/OJSE.2023.3325189 [Online]. Available: https://ieeexplore.ieee.org/document/10286971/

After citeproc: A. B. Ledford, G. Harris, and G. Purdy, “Implementing a Complete Digital Thread: The Need for Data Element Mapping and Analysis,” IEEE Open Journal of Systems Engineering, vol. 1, pp. 139–152, 2023, doi: 10.1109/ojse.2023.3325189.

**`ledford2025syseng`**

Before biber: A. Ledford, G. Harris, S. Askew, and G. Purdy, “Application of data element mapping and analysis for system definition to enable model-based systems engineering,” Systems Engineering, vol. 28, no. 1, pp. 15–28, 2025, Demonstrates DEMA application: 1600 vessel occurrences across 79 functions in 23 storage locations. DOI: 10.1002/sys.21776 [Online]. Available: https://incose.onlinelibrary.wiley.com/doi/10.1002/sys.21776

After citeproc: A. Ledford, G. Harris, S. Askew, and G. Purdy, “Application of Data Element Mapping and Analysis for System Definition to Enable Model-Based Systems Engineering,” Systems Engineering, vol. 28, no. 1, pp. 15–28, 2025, doi: 10.1002/sys.21776.

**`oleary2025ai4se`**

Before biber: D. J. O’Leary and A. N. Ledford, Ai-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes, Workshop Presentation, AI4SE & SE4AI Research and Application Workshop, The George Washington University, Sep. 2025.

After citeproc: D. J. O’Leary and A. B. Ledford, “AI-Enhanced DEMA: Transforming Implicit System Knowledge Into Intelligent, Compliant, and Documented Processes,” presented at the AI4SE & SE4AI Research and Application Workshop, Washington, DC, USA, Sep. 2025.

## Open decisions and stop point

1. Approve the small local speech fallback and city metadata shown above.
2. Approve this complete conversion plan: 37 catalog records, 34 cited memberships, three unnamed version links, one target/four gates, eight new file links and 28 acquisitions. Accept or explicitly carry unavailable acquisitions as gaps. Semantic retypes shown above remain part of that plan review.

The selected versions, retained preprints, GPT-4 reuse, ReMatch correction, note moves, INSIGHT details, all-citeproc choice, standards targets (including the CMMC Model Overview) and unfiled placement are settled decisions, not repeated questions. Proposal approval, clean-publication readiness, later export-gate acceptance, fixture recording and adoption remain separate owner gates routed through s1.

## Verification and evidence

The merged source-links worktree was removed and this branch rebased onto refs 0.9.2. Only this proposal is edited; no code or publication changes are part of the revision. Scratch evidence is `/private/tmp/refs-dema-second-revision/`: fresh dry intake/bindings, 37 canonical records, key map, membership/acquisition lists, serializer output, exact per-key renders, proposed style/diff and verification results. The superseded CFR diagnostic remains separately labeled in scratch and is not part of the candidate. Prior `/private/tmp/refs-dema-revision/` retains baseline biber strings and current-artifact comparisons. Tools remain Quarto 1.10.18, Pandoc 3.10, biber 2.21 and XeLaTeX/TeX Live 2026.

All 963 checked input hashes match, including the live catalog, publication inputs/artifacts, delivered PDD, standards report and source files; the publication’s four dirty paths are unchanged. All ten removed note values survive with import attribution, canonical candidates are stable on revalidation, and new publication keys are unbound. The isolated style comparison changes exactly the two speeches. No unrelated product suite was rerun for this proposal-only revision.

**Stop at conversion-guide step 4:** send to s1 for owner review; do not execute intake or adoption.
