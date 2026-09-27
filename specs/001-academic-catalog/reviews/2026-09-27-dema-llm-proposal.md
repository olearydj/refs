# dema-llm conversion — proposal, 2026-09-27

**Proposal only; not approved or executed.** Prepared on `s2/dema-llm-proposal` from refs main `78708e1` (0.9.0). This completes conversion-guide steps 1–4 and stops. The catalog was opened only with SQLite `mode=ro`; no import, backup, fetch of an attachment, capture, move, live export, project edit or fixture recording occurred. Local scratch contains adapter assessments and citation-engine probes, not an executed conversion.

The bibliography has **34 entries and seven distinct arXiv-linked records**, not thirteen arXiv records: thirteen bibliography lines mention arXiv. All 34 are cited by the TDD, including its explicit background-reading citations; the PDD cites six. The raw import predicts **34 new records, zero existing bindings, zero conflicts and zero refusals**. That is not an execution recommendation: GPT-4 matches an existing work under a different key/version, and DSPy has a published-version candidate already in the catalog. Identity/version decisions must precede intake.

There are **four rendered consumers and two citation engines**. Contrary to the kickoff's initial inference, PDD PDF uses IEEE biblatex/biber, not the vendored IEEE CSL. The current 0.9.0 candidate does **not** have a clean fidelity gate: three literal `others` authors, missing arXiv labels in CSL, lost speech event facts, omitted proceedings volumes and omitted webpage years are disclosed below. Do not work around them by inventing a publisher, duplicating identification text into notes, changing types to suit a style, or silently accepting a loss.

## Backup and scope

Proposed execution backup: `/Volumes/Casa/refs-backups/2026-09-27-before-dema-llm-conversion`, dated for actual execution if later. No backup was made. Validate it before any approved catalog mutation.

Publication HEAD is `267176632e5a7eb9678042b492e19e8290237a87`. Current owner edits are a precondition for execution, not conversion work to stage or discard:

```text
 M .gitignore
 M docs/README.md
 M pyproject.toml
?? docs/dema-data-vocabulary-alignment.md
```

Execution requires the publication session to settle these edits and supply a clean commit, then re-inventory citations and consumers. Preserve `pre-pipyer`, manuscript prose and all assigned keys. No conversion implementation is authorized here. Bibliography SHA-256: `36d0f3823a43f42e16fab530e3255f21a4e1e60808333ca017ff9d7df19d395a`.

The proposed refs project is `dema-llm`, with the union of 34 cited records. PDD's six references are selected by its own citations, not by deleting the other 28 catalog/project memberships. Keep source PDFs in the publication and vault where they are; the proposed external intake is described separately.

## Inventory and consumers

`docs/references.bib` is the sole current bibliography source in this repository. It is hand/agent maintained and shared by two Quarto documents; no script that writes, copies, projects or independently formats it was found. A repository-wide source search covered bibliography, citeproc, biblatex/natbib, CSL and filename references, followed by the hidden/ignored artifact inventory. `docs/legacy/tdd-quarto-1.zip` is a historical archive, not an active reader. `docs/reports/DEMA_INSIGHT_ARTICLE_LOCATION.md` points to a separate publication's bibliography; it does not consume this one. `docs/tdd/a6-references.qmd` describes the current `.bib` path and must be updated only after adoption.

Entry types: ten `article`, one `incollection`, seven `inproceedings`, twelve `misc`, one `phdthesis`, three `techreport`. Keys are lowercase surname/organization plus year and optional mnemonic/hyphens. Preserve all 34 spellings, including `oracle2011migration` even though its supplied year is 2012.

Citation inventory used Pandoc's `Cite` nodes in all top-level TDD QMDs and the PDD source, cross-checked against known keys. TDD uses all 34; PDD uses `ledford2025syseng`, `ledford2023dissertation`, `ledford2023ieee`, `sequeda2023`, `sheetrit2024`, `oleary2025ai4se`. No bibliography key is uncited across the project. Quarto cross-reference tokens are not bibliography keys.

| Consumer | Current route and artifact | Planned target/profile |
| --- | --- | --- |
| TDD HTML book | `docs/tdd/_quarto.yml`, citeproc, `../references.bib`, `../csl/ieee.csl`; `_book/a6-references.html` | `docs/references-tdd.json`, `csl-json-v1` |
| TDD PDF book | Same configuration and CSL, XeLaTeX layout; `_book/DEMA-LLM-Design-Document.pdf` | Same TDD JSON target; separate rendered gate |
| PDD DOCX | `docs/pdd/DEMA-LLM-Overview.qmd`, docx-local IEEE CSL; `DEMA-LLM-Overview.docx` | `docs/references-pdd.json`, `csl-json-v1` |
| PDD PDF | PDF-local `cite-method: biblatex`, `style=ieee`, `backend=biber`, `backref=true`; `DEMA-LLM-Overview.pdf` | `docs/references-pdd.bib`, `biblatex-v1` |

The TDD's HTML and PDF are formats of one configured reader and share one target, as the existing conversion register permits for a shared input. PDD's two engines receive distinct targets. This is three target bindings and four artifact gates. No classic BibTeX target is needed. Preserve `link-bibliography`, citation links and PDF backreferences. Plain `quarto render docs/tdd/` builds both formats; do not run a single-format render in the live project, which its instructions warn can wipe the other `_book/` output. All future renders run in scratch until adoption.

Current rendered artifacts were read, not rebuilt in place. The TDD HTML's 34 reference strings exactly match a fresh scratch citeproc rendering of the current bibliography and CSL after removing reference numbers. TDD PDF has the same facts with different citation numbering/order and line wrapping; its final Bibliography was extracted. PDD DOCX's six XML reference paragraphs match the corresponding current CSL strings. PDD PDF's six references were extracted; they additionally print annotation notes, source URLs and page backreferences. These differences are existing consumer behavior.

## Import outcomes by key

The actual BibTeX partitioner and `importing.apply_entry(..., dry_run=True)` ran over the read-only catalog with the owner's current configuration, project configuration disabled, origin `dema-llm`. All 34 entries are admitted. The five supplied DOIs (`ledford2023ieee`, `ledford2025syseng`, `bernsteinhaas2008`, `christophides2021`, `nist2020sp80053`) have no catalog match. None of the incoming keys already exists. Title comparison finds GPT-4 and the related published DSPy record; title alone does not bind either.

Every row below predicts **new/applied for the untouched input**, with no safe fills or reconciliation of existing records. The planned canonical type is the type after separately approved completion, not the raw adapter's type.

| Key | Raw import | Planned type | PDD cited |
| --- | --- | --- | --- |
| `sequeda2023` | new | article | yes |
| `sheetrit2024` | new | article | yes |
| `ledford2023dissertation` | new | thesis | yes |
| `ledford2023ieee` | new | article-journal | yes |
| `ledford2025syseng` | new | article-journal | yes |
| `oleary2025ai4se` | new | speech | yes |
| `howard2007bloor` | new | report | no |
| `howard2011bloor` | new | report | no |
| `bernsteinhaas2008` | new | article-journal | no |
| `oracle2011migration` | new | report | no |
| `oleary2025binary-classification` | new | speech | no |
| `olearyledford2026insight` | new | article-journal | no |
| `brown2020` | new | paper-conference | no |
| `wei2022` | new | paper-conference | no |
| `openai2024gpt4` | new | article | no |
| `anthropic2024claude3` | new | report | no |
| `touvron2023llama2` | new | article | no |
| `reimers2019` | new | paper-conference | no |
| `openai2024embeddings` | new | webpage | no |
| `nussbaum2024nomic` | new | article | no |
| `guo2017` | new | paper-conference | no |
| `kadavath2022` | new | article | no |
| `naeini2015` | new | paper-conference | no |
| `christophides2021` | new | article-journal | no |
| `mudgal2018` | new | paper-conference | no |
| `konda2016` | new | article-journal | no |
| `koutras2021valentine` | new | paper-conference | no |
| `deb2014` | new | chapter | no |
| `zitzler2003` | new | article-journal | no |
| `khattab2023dspy` | new | article | no |
| `zhou2023ape` | new | paper-conference | no |
| `nist2020sp80053` | new | report | no |
| `fedramp2024` | new | webpage | no |
| `dod2020cmmc` | new | document | no |

### DOI, version and key decisions before import

`openai2023gpt4` already holds DOI `10.48550/arxiv.2303.08774`, canonical type `article`, issued 2023-03-27, archive arXiv, unversioned arXiv identifier, and a March 27, 2023 PDF. The incoming `openai2024gpt4` has no DOI and describes v6 in `howpublished`, so raw import would create a second source. Adding the base DOI before intake instead matches the existing key. A second read-only bind probe reports incompatible raw types and differences in author form, date, URL, title protection and native type; it does not authorize a merge. The proposed article retype removes only the type discrepancy, not the date/key/version question. Refs exports the stored catalog key, and this inspection found no per-project alternate-key export mechanism. Neither rewriting manuscript citations nor rekeying the shared catalog is in scope. Do not add the common DOI to a new record, or omit it solely to evade binding, before the owner resolves this.

`khattab2024` is already in project `pipyer-paper`, type `paper-conference`, year 2024, ICLR, title ending “State-of-the-Art Pipelines”; it has no DOI or resource. It is a published-version candidate for `khattab2023dspy`, not an automatic title merge. The latter key names a 2023 preprint ending “Self-Improving Pipelines.” Keeping both requires an explicit version decision; choosing the existing record creates the same exported-key problem.

The newly identified INSIGHT DOI `10.1002/inst.70055` and Sequeda publication DOI `10.1145/3661304.3661901` also have no catalog match. Acquisition links below are not automatic DOI-enrichment instructions. Re-assess identity against current catalog state at execution, especially if the owner chooses published versions.

## Record completions by key

Defaults for all 34: English title-case policy, keep assigned key, original entry bytes, given creators/identifiers and all existing brace protection; set language `en` for these English works. Preserve additional technical tokens where present: DEMA, AI, LLM/LLMs, GPT-4, ReMatch, DSPy, Nomic Embed, Llama 2, SQL, BERT, FedRAMP, CMMC, INCOSE and INFORMS. No whole-title preserve policy is proposed. Keep dates at supplied precision except an explicitly selected version; reading metadata is not proof of full-text review or a capture date. Proposed types clear a mismatched native BibTeX label so it cannot force the old type on export. Kinds do not drive the semantic decisions; no repository/software kind is assigned to a paper about a model or library.

Nine interpretive notes move verbatim into context: Sequeda, Sheetrit, the three Ledford works, both Bloor reports, Bernstein/Haas and Oracle. Their claims are not verified merely by import. The INSIGHT forthcoming note becomes historical context. This deliberately removes five claim notes currently visible in PDD PDF, while CSL already omits them.

| Key | Proposed completion |
| --- | --- |
| `sequeda2023` | Correct title and coauthors from local v1; move claim note to context; preprint fields below; later published version is an owner choice. |
| `sheetrit2024` | Replace unsupported six-author/SIGMOD assertion with four authors from local v2; clear ACM/venue; move claim to context; preprint fields below. |
| `ledford2023dissertation` | Keep degree, institution, place and year; protect DEMA; move interpretation note to context. |
| `ledford2023ieee` | Keep DOI/volume/pages; move interpretation note to context. |
| `ledford2025syseng` | Keep issue-year 2025 and DOI/pages; move application summary to context; vault 2024 filename is not a year correction. |
| `oleary2025ai4se` | Workshop presentation, event-title and event-place; propose Allison B. from slide cover against bibliography/CV A. N.; retain D. J. author initials; protect AI/DEMA. |
| `howard2007bloor` | Keep report/publisher/September 2007; move survey summary to context. Primary file missing. |
| `howard2011bloor` | Keep report/publisher/year/genre; move survey/cost summary to context. Primary file missing. |
| `bernsteinhaas2008` | Keep journal/DOI/pages; move budget claim to context. |
| `oracle2011migration` | Report, genre White paper, publisher Oracle; keep 2012 and key containing 2011; move secondary-source caveat to context. |
| `oleary2025binary-classification` | Speech, genre Poster presentation, event INFORMS Annual Meeting, October 2025; candidate poster has shorter title, so attachment requires owner identity decision. |
| `olearyledford2026insight` | Use local version of record and CV: volume 29, issue 3, pages 37–42, DOI 10.1002/inst.70055; remove obsolete forthcoming note to historical context. |
| `brown2020` | Conference paper in NeurIPS volume 33, pages retained; existing truncated creator list preserved pending refs finding; local PDF is July 2020 arXiv v4, not proved proceedings copy. |
| `wei2022` | Conference paper in NeurIPS volume 35, pages retained; no new fields guessed. |
| `openai2024gpt4` | Conditional v6 preprint with supplied 2024 retained for probe; existing 2023 catalog identity blocks a final intake recommendation; see DOI analysis. |
| `anthropic2024claude3` | Conditional report/Model card/Anthropic; current URL is a launch page, not identified model-card file. Owner must select actual source before completion. |
| `touvron2023llama2` | Preprint fields below; supplied abbreviated creator list exposes literal others in CSL. |
| `reimers2019` | Keep conference/pages; protect BERT. ACL full text found online, not acquired. |
| `openai2024embeddings` | Webpage; keep supplied title/year/URL provisionally; historical page version and capture date not invented. |
| `nussbaum2024nomic` | Retain 2024 preprint for probe; protect Nomic Embed; TMLR 2025 is a separate owner choice. |
| `guo2017` | Keep conference/pages; primary PMLR acquisition link below. |
| `kadavath2022` | Preprint fields below; supplied abbreviated creator list exposes literal others in CSL. |
| `naeini2015` | Keep conference/pages; primary AAAI acquisition link below. |
| `christophides2021` | Keep journal/DOI/volume/issue/pages; no changes beyond case policy. |
| `mudgal2018` | Keep conference/pages; author-hosted paper located online; no new DOI automatically added. |
| `konda2016` | Keep PVLDB article; supplied abbreviated creator list exposes literal others in CSL. |
| `koutras2021valentine` | Keep conference/pages; acquire cited 2021 proceedings version rather than silently substitute 2020 preprint. |
| `deb2014` | Keep 2014 chapter, book and pages; reject title mention inside an unrelated Zhang PDF. |
| `zitzler2003` | Keep journal/volume/issue/pages; exact paper still to acquire. |
| `khattab2023dspy` | Retain 2023 preprint for probe; protect DSPy; published 2024 catalog identity is an owner choice. |
| `zhou2023ape` | Keep ICLR 2023 conference identity; acquisition link below. |
| `nist2020sp80053` | Keep report/number/DOI/revision 5; ensure institutional publisher is one literal string, not Pandoc’s baseline semicolon split. |
| `fedramp2024` | Webpage provisionally; keep supplied year; homepage is not verified 2024 framework capture. |
| `dod2020cmmc` | Retain document, title and 2020; specific historical framework version/file unresolved; do not substitute current CMMC. |

### Seven arXiv records and later versions

The probe retains the currently cited preprint versions pending owner choice. Each becomes CSL `article`, with `archive=arXiv`, the listed `number`, and the same value in `extensions.identifiers.arxiv`; no journal or conference container is fabricated. Keep the URL. For the two local PDFs and the explicitly named GPT-4 version, preserve v1/v2/v6. Unversioned locators remain unversioned until acquisition establishes the intended revision. No preprint DOI is newly assigned in this conditional probe. The CSL exporter carries metadata number/archive but does not serialize the identifier extension; the vendored style ignores archive. Biblatex carries the arXiv identifier in eprint fields.

Primary metadata and local covers were checked on 2026-09-27. “Not found” below means this bounded arXiv/title/publisher search found no later venue, not proof that none exists.

| Key | Number / archive | Source verification | Later version / decision |
| --- | --- | --- | --- |
| `sequeda2023` | 2311.07509v1 / arXiv | [arXiv](https://arxiv.org/abs/2311.07509); local PDF identifies Juan F. Sequeda, Dean Allemang, Bryon Jacob and the corrected title. | ACM GRADES-NDA 2024, June 9, pp. 1–12, DOI [10.1145/3661304.3661901](https://doi.org/10.1145/3661304.3661901), confirmed by publisher-deposited [Crossref metadata](https://api.crossref.org/works/10.1145/3661304.3661901). Choose preprint versus publication; do not silently replace. |
| `sheetrit2024` | 2403.01567v2 / arXiv | [arXiv](https://arxiv.org/abs/2403.01567) and local PDF agree on Eitam Sheetrit, Menachem Brief, Moshik Mishaeli, Oren Elisha. | No later venue verified. No evidence supporting the supplied SIGMOD proceedings/ACM attribution. The correction to preprint is an owner decision, not a cosmetic mapping. |
| `openai2024gpt4` | 2303.08774v6 / arXiv | [arXiv version history](https://arxiv.org/abs/2303.08774) identifies v6 dated 2024-03-04. | No separate later venue verified. Existing catalog/PDF is 2023, and the [OpenAI report](https://cdn.openai.com/papers/gpt-4.pdf) asks for OpenAI (2023). Decide version, year and key handling together. |
| `touvron2023llama2` | 2307.09288 / arXiv | [arXiv](https://arxiv.org/abs/2307.09288). | No later venue verified; retain cited preprint pending acquisition/version selection. |
| `nussbaum2024nomic` | 2402.01613 / arXiv | [arXiv](https://arxiv.org/abs/2402.01613). | TMLR February 2025, [publisher-hosted paper](https://openreview.net/pdf?id=IPmzyQSiQE), confirmed in indexed primary PDF text and [TMLR announcement](https://groups.google.com/g/tmlr-announce-weekly/c/6sK1XdkY6SM). Direct OpenReview retrieval encountered its verification page. Owner may select the journal version; not changed here. |
| `kadavath2022` | 2207.05221 / arXiv | [arXiv](https://arxiv.org/abs/2207.05221) and [Anthropic research page](https://www.anthropic.com/research/language-models-mostly-know-what-they-know). | No later venue verified; retain cited preprint. |
| `khattab2023dspy` | 2310.03714 / arXiv | [arXiv](https://arxiv.org/abs/2310.03714). | [ICLR 2024 official proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html) use the State-of-the-Art title and match catalog `khattab2024`. Owner chooses preprint versus published version; no substitution here. |

## Sources found, fetched, and the fetch list for the owner

Nothing was fetched as an attachment, captured or moved. Read-only evidence search covered the project and figures, `/Volumes/Casa/obsidian/vault/projects/dema`, `/Volumes/Casa/refs/lib`, and all of `~/Downloads`, including `_from2020mbp/devonthink`. The bounded PDF inventory contained 4,355 files. DOI matches were prioritized for identity where supplied, then normalized full-title matches in first-two-page text were reviewed. The separate DOI pass prevents a title-only miss on supplied identifiers. Filename inventory and text/HTML/Markdown searches supplemented that pass; author-publication metadata under `/Volumes/Casa/pub/cv/refs` led to the INSIGHT version of record outside those stores. ZIP contents and image-only PDFs were not exhaustively searched or OCRed. A missing file means not verified in these searches.

Seven works have verified primary files; three more have version/title candidates that cannot be called the exact cited source. Reports, dissertations and summaries that merely cite Bloor or Deb are excluded. An IP disclosure form mentioning INSIGHT is not its article. The project README's old TODO to migrate its PDFs to Zotero is superseded for this proposed workflow, but no such instruction or file was edited.

| Key | Source path | Proposed placement | SHA-256 |
| --- | --- | --- | --- |
| `sequeda2023` | `/Volumes/Casa/dev/dema-llm/docs/research/references/sequeda2023-llm-text-to-sql.pdf` | Link in place; empty loc; preserve filename | 1a0cb23795bea7f11c64b7f700d9088d2d08b004f7117951030733c8b0ee45c6 |
| `sheetrit2024` | `/Volumes/Casa/dev/dema-llm/docs/research/references/sheetrit2024-rematch.pdf` | Link in place; empty loc; preserve filename | 5504fb5e12ce6c2ab6741850c9e46158e94f913519bf28e6395935823d4bd0dd |
| `ledford2023dissertation` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-dissertation.pdf` | Link in place; empty loc; preserve filename | 3a6bc4a2ca6d59e9f5d196ee445a2f36d496aa89c4c8dfe586684dc31dbc5911 |
| `ledford2023ieee` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-ieee-digital-thread.pdf` | Link in place; empty loc; preserve filename | ee87f864331b17360d25722fa8ede347956eb3d7819c1252ec12775964841fe8 |
| `ledford2025syseng` | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2025-syseng.pdf` | Link in place; empty loc; preserve filename | 6883aaebae8248d4936eeb08b1cf2abb5136ae677c0c64ada6aa7c6e0ae1b13d |
| `oleary2025ai4se` | `/Users/djo/Downloads/OLeary_Ledford_AI_Enhanced_DEMA.pdf` | Move one selected Downloads copy to unfiled only after approval | b2ea81187907cd0bed0f6bc4c6790acf001da2a93609e6117f41475cbecdf770 |
| `olearyledford2026insight` | `/Volumes/Casa/pub/2026-insight-dema-llm/published/oleary-ledford-2026-insight-dema-llm-version-of-record.pdf` | Link in place; empty loc; preserve filename | 02567dceb4916267e82ef5f1b58bafcf340870c2215c38e037903090bc7d9af2 |

The second AI4SE download, `/Users/djo/Downloads/OLeary_Ledford_AI_Enhanced_DEMA-1.pdf`, has the same SHA-256; do not move/delete both. The SysEng vault file `/Volumes/Casa/obsidian/vault/projects/dema/docs/pubs/ledford2024-syseng.pdf` is an alternate copy to inspect only if the project copy fails; its filename does not override the issue-year metadata.

Candidates, not exact-source completion:

- `openai2024gpt4`: `/Volumes/Casa/refs/lib/papers/aiml/GPT4TechnicalReport-2023.pdf`, already attached to `openai2023gpt4`, SHA-256 `5269ab4bab5dd064a39ecab221f79e13bbe0901f0000f8dad3416cdb493df8b4`. Cover says March 27, 2023; do not attach it as v6.
- `brown2020`: `/Users/djo/Downloads/_from2020mbp/Desktop/USB-stuff/Zotero Folder 2021-07-08/Brown et al_2020_Language Models are Few-Shot Learners.pdf` is arXiv 2005.14165v4, July 22, 2020. The citation names the NeurIPS proceedings; verify version or obtain that version rather than imply the PDF is identical.
- `oleary2025binary-classification`: `/Users/djo/Downloads/poster-oleary-informs25.pptx` is a matching GradeBot poster, but its title omits “Comprehensive” and the slide text does not itself establish the INFORMS occasion. Owner confirmation is needed before attachment/title correction; the CV bibliography retains the longer title.

### Outstanding acquisition or identity list (27 keys)

These links are acquisition starting points, not claims that a download succeeded, that a homepage is the cited document, or that every source is openly licensed. Three rows have local candidates above; the other 24 have no verified primary local file. Fetch only after approval. For denied hosts, the owner supplies the authorized source. Do not invent access dates. Additional publication DOIs found during this search are not part of the base completion plan unless explicitly listed above.

| Key | Needed source / limitation | Link |
| --- | --- | --- |
| `howard2007bloor` | 2007 report; exact primary locator unresolved, not a secondary marketing quotation | [Locate](https://www.bloorresearch.com/) |
| `howard2011bloor` | 2011 report, not project market-context synthesis | [Locate](https://www.bloorresearch.com/research/data-migration-2011/) |
| `bernsteinhaas2008` | Cited journal article; access unverified | [Locate](https://doi.org/10.1145/1378727.1378745) |
| `oracle2011migration` | Supplied white-paper PDF URL; access unverified | [Locate](https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf) |
| `oleary2025binary-classification` | Owner poster identity decision; local candidate above | [Locate](https://www.informs.org/Meetings-Conferences) |
| `brown2020` | NeurIPS 2020 version needed; local preprint is only a candidate | [Locate](https://proceedings.neurips.cc/paper/2020) |
| `wei2022` | NeurIPS 2022 proceedings paper | [Locate](https://proceedings.neurips.cc/paper_files/paper/2022) |
| `openai2024gpt4` | v6 only if approved; existing attached v3-era file insufficient | [Locate](https://arxiv.org/abs/2303.08774v6) |
| `anthropic2024claude3` | Choose model card versus supplied announcement; not interchangeable | [Locate](https://www.anthropic.com/news/claude-3-family) |
| `touvron2023llama2` | Preprint; select revision at acquisition | [Locate](https://arxiv.org/abs/2307.09288) |
| `reimers2019` | ACL publisher full text available | [Locate](https://aclanthology.org/D19-1410/) |
| `openai2024embeddings` | URL-only; locate intended historical documentation or approve current capture | [Locate](https://platform.openai.com/docs/guides/embeddings) |
| `nussbaum2024nomic` | Preprint unless owner chooses TMLR version | [Locate](https://arxiv.org/abs/2402.01613) |
| `guo2017` | PMLR publisher full text available | [Locate](https://proceedings.mlr.press/v70/guo17a.html) |
| `kadavath2022` | Preprint | [Locate](https://arxiv.org/abs/2207.05221) |
| `naeini2015` | AAAI publisher full text available | [Locate](https://ojs.aaai.org/index.php/AAAI/article/download/9602/9461) |
| `christophides2021` | Cited journal article; access unverified | [Locate](https://doi.org/10.1145/3418896) |
| `mudgal2018` | Author-hosted SIGMOD paper; distinguish extended technical report | [Locate](https://pages.cs.wisc.edu/~anhai/papers1/deepmatcher-sigmod18.pdf) |
| `konda2016` | Author project publication index; exact paper still to acquire | [Locate](https://pages.cs.wisc.edu/~anhai/projects/magellan/research.html) |
| `koutras2021valentine` | Cited IEEE 2021 proceedings version | [Locate](https://ieeexplore.ieee.org/document/9458921) |
| `deb2014` | Cited 2014 chapter; exact edition required | [Locate](https://doi.org/10.1007/978-1-4614-6940-7_15) |
| `zitzler2003` | Cited 2003 journal paper; access unverified | [Locate](https://doi.org/10.1109/TEVC.2003.810758) |
| `khattab2023dspy` | Preprint unless owner chooses existing published catalog record | [Locate](https://arxiv.org/abs/2310.03714) |
| `zhou2023ape` | ICLR paper; OpenReview can present a verification page | [Locate](https://openreview.net/pdf?id=YdqwNaCLCx) |
| `nist2020sp80053` | Revision 5 as cited; do not silently use a later revision | [Locate](https://doi.org/10.6028/NIST.SP.800-53r5) |
| `fedramp2024` | URL-only; identify historical framework page/version first | [Locate](https://www.fedramp.gov/) |
| `dod2020cmmc` | 2020 framework version unresolved; current program page is a locator only | [Locate](https://business.defense.gov/Programs/Cyber-Security-Resources/Cybersecurity-Maturity-Model-Certification/) |

## Attachments with final names and hashes

No attachment was created. Source hashes above identify inputs to future approved intake, not destination verification. Project-owned PDFs retain names and empty loc when linked; proposed Downloads intake uses the CLI's filename preview and verified move protocol under `unfiled`, with original/destination hash checks before deletion. Final names and destination hashes are reported only after execution. No synthesized review note is an acceptable substitute for a missing source.

## Planned targets

An eventual root `.refs.toml` names project `dema-llm` and three explicit targets: `docs/references-tdd.json` and `docs/references-pdd.json` with `csl-json-v1`; `docs/references-pdd.bib` with `biblatex-v1`. No project file is written in this phase. TDD configuration points to the TDD JSON. PDD uses format-local bibliography routing and removes the shared top-level legacy bibliography to avoid Quarto merging both inputs. Confirm effective metadata in scratch. After owner acceptance, switch all readers together, retire `docs/references.bib` only when nothing consumes it, update its descriptive reference in a6 and add project workflow documentation. Preserve the legacy bytes as catalog originals. No `--record` or adoption is permitted by this proposal.

## Export gate table

These are predictions from hypothetical in-memory completed records passed through refs 0.9.0 serializers, not live imports or registered gates. Citeproc used Quarto 1.10.18 / Pandoc 3.10 and the actual vendored IEEE CSL. The biblatex probe used native biber 2.21 and XeLaTeX/TeX Live 2026 with `style=ieee,backend=biber,backref=true`; a minimal bibliography document isolates the reference wording. It does not certify PDD layout or backreference page numbers. Five arXiv works absent from PDD were also probed diagnostically, not inserted into its prose.

All 34 CSL entries change title casing because refs stores title case and this CSL route does not sentence-case the JSON input. That is an explicit case-policy prediction, not “identical.” DOI case normalization is identifier-equivalent. “Case only” below means those changes with all other bibliographic facts retained. Missing facts remain blockers even if the proposed retype is correct. PDD DOCX matches CSL only for its six cited keys; the other 28 are intentionally absent from both PDD outputs.

| Key | TDD HTML and PDF / CSL prediction | PDD DOCX | PDD PDF / biblatex prediction |
| --- | --- | --- | --- |
| `sequeda2023` | Changed identity metadata; correct title/coauthors and preprint number; CSL omits arXiv archive label (finding). | Same CSL wording | Changed: corrected title/authors; arXiv eprint retained; claim note removed. |
| `sheetrit2024` | Changed: correct coauthors; remove unsupported SIGMOD/ACM venue; preprint number. CSL omits archive label. | Same CSL wording | Changed: corrected authors/preprint; unsupported venue and claim note removed; arXiv eprint retained. |
| `ledford2023dissertation` | Changed: case only; other facts retained. | Same CSL wording | Changed: DEMA protected; interpretation note removed; degree/institution retained. |
| `ledford2023ieee` | Changed: case only; other facts retained. | Same CSL wording | Changed: interpretation note removed; DOI normalized; facts retained. |
| `ledford2025syseng` | Changed: case only; other facts retained. | Same CSL wording | Changed: interpretation note removed; journal/DOI/pages retained. |
| `oleary2025ai4se` | Changed author initial, but workshop/event/place vanish from CSL (finding). | Same CSL wording | Changed: Allison B.; speech wording; workshop/event/place retained by biber. |
| `howard2007bloor` | Changed: case only; other facts retained. | Not cited | Not cited |
| `howard2011bloor` | Changed: case only; other facts retained. | Not cited | Not cited |
| `bernsteinhaas2008` | Changed: case only; other facts retained. | Not cited | Not cited |
| `oracle2011migration` | Changed: report punctuation, explicit Oracle publisher and White paper genre. | Not cited | Not cited |
| `oleary2025binary-classification` | Changed retype; poster genre/INFORMS occasion vanish from CSL (finding). | Not cited | Not cited |
| `olearyledford2026insight` | Changed: published volume/issue/pages/DOI added. | Not cited | Not cited |
| `brown2020` | Changed to proceedings; volume 33 no longer printed (finding); existing author truncation remains latent. | Not cited | Not cited |
| `wei2022` | Changed to proceedings; volume 35 no longer printed (finding). | Not cited | Not cited |
| `openai2024gpt4` | Conditional: preprint number retained, archive label lost; unresolved existing identity/version. | Not cited | Not cited |
| `anthropic2024claude3` | Conditional report: Anthropic publisher and Model card genre added; source identity unresolved. | Not cited | Not cited |
| `touvron2023llama2` | Changed: preprint number; archive label omitted; et al. becomes literal and others (finding). | Not cited | Not cited |
| `reimers2019` | Changed: case only; other facts retained. | Not cited | Not cited |
| `openai2024embeddings` | Changed to webpage; year 2024 no longer printed (finding); historical page unresolved. | Not cited | Not cited |
| `nussbaum2024nomic` | Conditional 2024 preprint: number retained, archive label omitted; journal-version choice pending. | Not cited | Not cited |
| `guo2017` | Changed: case only; other facts retained. | Not cited | Not cited |
| `kadavath2022` | Changed: preprint number; archive label omitted; et al. becomes literal and others (finding). | Not cited | Not cited |
| `naeini2015` | Changed: case only; other facts retained. | Not cited | Not cited |
| `christophides2021` | Changed: case only; other facts retained. | Not cited | Not cited |
| `mudgal2018` | Changed: case only; other facts retained. | Not cited | Not cited |
| `konda2016` | Changed beyond case: et al. becomes literal and others (finding). | Not cited | Not cited |
| `koutras2021valentine` | Changed: case only; other facts retained. | Not cited | Not cited |
| `deb2014` | Changed: case only; other facts retained. | Not cited | Not cited |
| `zitzler2003` | Changed: case only; other facts retained. | Not cited | Not cited |
| `khattab2023dspy` | Conditional 2023 preprint: number retained, archive label omitted; published-version choice pending. | Not cited | Not cited |
| `zhou2023ape` | Changed: case only; other facts retained. | Not cited | Not cited |
| `nist2020sp80053` | Changed: correct literal institutional publisher replaces baseline National Institute of Standards; Technology. | Not cited | Not cited |
| `fedramp2024` | Changed to webpage; year 2024 no longer printed (finding); historical framework unresolved. | Not cited | Not cited |
| `dod2020cmmc` | Changed: case only; other facts retained. | Not cited | Not cited |

### Exact arXiv before/after wording

Reference numbers, wrapping and font emphasis are omitted. **Current CSL** is the existing TDD HTML string (also the PDD DOCX string when cited); the scratch baseline matched all 34 existing HTML strings. **Planned CSL** applies to both TDD formats and, for Sequeda/Sheetrit, PDD DOCX. **Current/planned biblatex** is native IEEE reference wording from the scratch engine; only Sequeda/Sheetrit occur in the actual PDD PDF. The remaining five are diagnostic only and remain absent from PDD. Existing PDD PDF extraction independently verifies the two cited baseline facts and notes. Page backreferences depend on the full manuscript and are outside these bibliography-only strings.

**`sequeda2023`**

Current CSL: J. Sequeda, D. Briggs, and D. P. Miranker, “Benchmarking the text-to-SQL capability of large language models: A comprehensive evaluation,” arXiv preprint arXiv:2311.07509, 2023, Available: https://arxiv.org/abs/2311.07509

Planned CSL: J. F. Sequeda, D. Allemang, and B. Jacob, “A Benchmark to Understand the Role of Knowledge Graphs on Large Language Model’s Accuracy for Question Answering on Enterprise SQL Databases,” 2023, 2311.07509v1. Available: https://arxiv.org/abs/2311.07509

Current biblatex: J. Sequeda, D. Briggs, and D. P. Miranker, “Benchmarking the text-to-sql capability of large language models: A comprehensive evaluation,” arXiv preprint arXiv:2311.07509, 2023, Key finding: GPT-4 achieves 16% accuracy zero-shot, 54% with Knowledge Graph context. [Online]. Available: https://arxiv.org/abs/2311.07509

Planned biblatex: J. F. Sequeda, D. Allemang, and B. Jacob, “A benchmark to understand the role of knowledge graphs on large language model’s accuracy for question answering on enterprise SQL databases,” 2023. arXiv: 2311.07509v1. [Online]. Available: https://arxiv.org/abs/2311.07509

**`sheetrit2024`**

Current CSL: E. Sheetrit, S. Nevo, T. Mazor, N. Nadler, F. Fournier, and A. Anaby-Tavor, “ReMatch: Retrieval enhanced schema matching with LLMs,” in Proceedings of the 2024 ACM SIGMOD international conference on management of data, ACM, 2024. Available: https://arxiv.org/abs/2403.01567

Planned CSL: E. Sheetrit, M. Brief, M. Mishaeli, and O. Elisha, “ReMatch: Retrieval Enhanced Schema Matching With LLMs,” 2024, 2403.01567v2. Available: https://arxiv.org/abs/2403.01567

Current biblatex: E. Sheetrit, S. Nevo, T. Mazor, N. Nadler, F. Fournier, and A. Anaby-Tavor, “Rematch: Retrieval enhanced schema matching with llms,” in Proceedings of the 2024 ACM SIGMOD International Conference on Management of Data, State-of-the-art LLM schema matching achieving 42-73% accuracy, ACM, 2024. [Online]. Available: https://arxiv.org/abs/2403.01567

Planned biblatex: E. Sheetrit, M. Brief, M. Mishaeli, and O. Elisha, “ReMatch: Retrieval enhanced schema matching with LLMs,” 2024. arXiv: 2403.01567v2. [Online]. Available: https://arxiv.org/abs/2403.01567

**`openai2024gpt4`**

Current CSL: OpenAI, “GPT-4 technical report.” arXiv:2303.08774v6, 2024. Available: https://arxiv.org/abs/2303.08774

Planned CSL: OpenAI, “GPT-4 Technical Report,” 2024, 2303.08774v6. Available: https://arxiv.org/abs/2303.08774

Current biblatex: OpenAI, GPT-4 technical report, arXiv:2303.08774v6, 2024. [Online]. Available: https://arxiv.org/abs/2303.08774

Planned biblatex: OpenAI, “GPT-4 technical report,” 2024. arXiv: 2303.08774v6. [Online]. Available: https://arxiv.org/abs/2303.08774

**`touvron2023llama2`**

Current CSL: H. Touvron, L. Martin, K. Stone, et al., “Llama 2: Open foundation and fine-tuned chat models.” arXiv:2307.09288, 2023. Available: https://arxiv.org/abs/2307.09288

Planned CSL: H. Touvron, L. Martin, K. Stone, and others, “Llama 2: Open Foundation and Fine-Tuned Chat Models,” 2023, 2307.09288. Available: https://arxiv.org/abs/2307.09288

Current biblatex: H. Touvron, L. Martin, K. Stone, et al., Llama 2: Open foundation and fine-tuned chat models, arXiv:2307.09288, 2023. [Online]. Available: https://arxiv.org/abs/2307.09288

Planned biblatex: H. Touvron, L. Martin, K. Stone, et al., “Llama 2: Open foundation and fine-tuned chat models,” 2023. arXiv: 2307.09288. [Online]. Available: https://arxiv.org/abs/2307.09288

**`nussbaum2024nomic`**

Current CSL: Z. Nussbaum, J. X. Morris, B. Duderstadt, and A. Mulyar, “Nomic embed: Training a reproducible long context text embedder.” arXiv:2402.01613, 2024. Available: https://arxiv.org/abs/2402.01613

Planned CSL: Z. Nussbaum, J. X. Morris, B. Duderstadt, and A. Mulyar, “Nomic Embed: Training a Reproducible Long Context Text Embedder,” 2024, 2402.01613. Available: https://arxiv.org/abs/2402.01613

Current biblatex: Z. Nussbaum, J. X. Morris, B. Duderstadt, and A. Mulyar, Nomic embed: Training a reproducible long context text embedder, arXiv:2402.01613, 2024. [Online]. Available: https://arxiv.org/abs/2402.01613

Planned biblatex: Z. Nussbaum, J. X. Morris, B. Duderstadt, and A. Mulyar, “Nomic Embed: Training a reproducible long context text embedder,” 2024. arXiv: 2402.01613. [Online]. Available: https://arxiv.org/abs/2402.01613

**`kadavath2022`**

Current CSL: S. Kadavath, T. Conerly, A. Askell, et al., “Language models (mostly) know what they know.” arXiv:2207.05221, 2022. Available: https://arxiv.org/abs/2207.05221

Planned CSL: S. Kadavath, T. Conerly, A. Askell, and others, “Language Models (Mostly) Know What They Know,” 2022, 2207.05221. Available: https://arxiv.org/abs/2207.05221

Current biblatex: S. Kadavath, T. Conerly, A. Askell, et al., Language models (mostly) know what they know, arXiv:2207.05221, 2022. [Online]. Available: https://arxiv.org/abs/2207.05221

Planned biblatex: S. Kadavath, T. Conerly, A. Askell, et al., “Language models (mostly) know what they know,” 2022. arXiv: 2207.05221. [Online]. Available: https://arxiv.org/abs/2207.05221

**`khattab2023dspy`**

Current CSL: O. Khattab et al., “DSPy: Compiling declarative language model calls into self-improving pipelines.” arXiv:2310.03714, 2023. Available: https://arxiv.org/abs/2310.03714

Planned CSL: O. Khattab et al., “DSPy: Compiling Declarative Language Model Calls Into Self-Improving Pipelines,” 2023, 2310.03714. Available: https://arxiv.org/abs/2310.03714

Current biblatex: O. Khattab et al., DSPy: Compiling declarative language model calls into self-improving pipelines, arXiv:2310.03714, 2023. [Online]. Available: https://arxiv.org/abs/2310.03714

Planned biblatex: O. Khattab et al., “DSPy: Compiling declarative language model calls into self-improving pipelines,” 2023. arXiv: 2310.03714. [Online]. Available: https://arxiv.org/abs/2310.03714

### Other material changes, exact CSL strings

The case-only rows are covered by the declared policy and full scratch before/after maps. Every other non-arXiv wording change is shown here; these strings are predictions including disclosed losses, not approved replacements.

**`oleary2025ai4se`**

Current: D. J. O’Leary and A. N. Ledford, “AI-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes.” The George Washington University; Workshop Presentation, AI4SE & SE4AI Research and Application Workshop, Sep. 2025.

Planned: D. J. O’Leary and A. B. Ledford, “AI-Enhanced DEMA: Transforming Implicit System Knowledge Into Intelligent, Compliant, and Documented Processes,” Sep. 2025.

**`oracle2011migration`**

Current: Oracle, “Put your data first or your migration will come last.” White paper, 2012. Available: https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf

Planned: Oracle, “Put Your Data First or Your Migration Will Come Last,” Oracle, White paper, 2012. Available: https://www.oracle.com/a/ocom/docs/middleware/data-integration/data-migration-wp.pdf

**`oleary2025binary-classification`**

Current: D. J. O’Leary, “Beyond binary classification: A comprehensive multi-criteria assessment system for programming assignments.” Poster presentation, INFORMS Annual Meeting, October 2025, Oct. 2025.

Planned: D. J. O’Leary, “Beyond Binary Classification: A Comprehensive Multi-Criteria Assessment System for Programming Assignments,” Oct. 2025.

**`olearyledford2026insight`**

Current: D. J. O’Leary and A. B. Ledford, “Trustworthy LLM-augmented data reconciliation for deployment-constrained environments,” INSIGHT, 2026.

Planned: D. J. O’Leary and A. B. Ledford, “Trustworthy LLM-Augmented Data Reconciliation for Deployment-Constrained Environments,” INSIGHT, vol. 29, no. 3, pp. 37–42, 2026, doi: 10.1002/inst.70055.

**`brown2020`**

Current: T. Brown et al., “Language models are few-shot learners,” Advances in Neural Information Processing Systems, vol. 33, pp. 1877–1901, 2020.

Planned: T. Brown et al., “Language Models Are Few-Shot Learners,” in Advances in Neural Information Processing Systems, 2020, pp. 1877–1901.

**`wei2022`**

Current: J. Wei et al., “Chain-of-thought prompting elicits reasoning in large language models,” Advances in Neural Information Processing Systems, vol. 35, pp. 24824–24837, 2022.

Planned: J. Wei et al., “Chain-of-Thought Prompting Elicits Reasoning in Large Language Models,” in Advances in Neural Information Processing Systems, 2022, pp. 24824–24837.

**`anthropic2024claude3`**

Current: Anthropic, “Claude 3 model card.” 2024. Available: https://www.anthropic.com/news/claude-3-family

Planned: Anthropic, “Claude 3 Model Card,” Anthropic, Model card, 2024. Available: https://www.anthropic.com/news/claude-3-family

**`openai2024embeddings`**

Current: OpenAI, “Text embedding models.” 2024. Available: https://platform.openai.com/docs/guides/embeddings

Planned: OpenAI, “Text Embedding Models.” [Online]. Available: https://platform.openai.com/docs/guides/embeddings

**`konda2016`**

Current: P. Konda, S. Das, A. Doan, et al., “Magellan: Toward building entity matching management systems,” Proceedings of the VLDB Endowment, vol. 9, no. 12, pp. 1197–1208, 2016.

Planned: P. Konda, S. Das, A. Doan, and others, “Magellan: Toward Building Entity Matching Management Systems,” Proceedings of the VLDB Endowment, vol. 9, no. 12, pp. 1197–1208, 2016.

**`nist2020sp80053`**

Current: National Institute of Standards and Technology, “Security and privacy controls for information systems and organizations,” National Institute of Standards; Technology, NIST Special Publication 800-53, Revision 5, 2020. doi: 10.6028/NIST.SP.800-53r5.

Planned: National Institute of Standards and Technology, “Security and Privacy Controls for Information Systems and Organizations,” National Institute of Standards and Technology, NIST Special Publication 800-53, Revision 5, 2020. doi: 10.6028/nist.sp.800-53r5.

**`fedramp2024`**

Current: Federal Risk and Authorization Management Program (FedRAMP), “FedRAMP security assessment framework.” 2024. Available: https://www.fedramp.gov/

Planned: Federal Risk and Authorization Management Program (FedRAMP), “FedRAMP Security Assessment Framework.” [Online]. Available: https://www.fedramp.gov/

### Remaining PDD PDF changes

The remaining four cited entries retain all ordinary identifying facts except the explicitly removed interpretation notes; the speech changes its author initial and presentation structure. The exact planned native strings are:

**`ledford2025syseng`**

Current biblatex: A. Ledford, G. Harris, S. Askew, and G. Purdy, “Application of data element mapping and analysis for system definition to enable model-based systems engineering,” Systems Engineering, vol. 28, no. 1, pp. 15–28, 2025, Demonstrates DEMA application: 1600 vessel occurrences across 79 functions in 23 storage locations. DOI: 10.1002/sys.21776 [Online]. Available: https://incose.onlinelibrary.wiley.com/doi/10.1002/sys.21776

Planned biblatex: A. Ledford, G. Harris, S. Askew, and G. Purdy, “Application of data element mapping and analysis for system definition to enable model-based systems engineering,” Systems Engineering, vol. 28, no. 1, pp. 15–28, 2025. DOI: 10.1002/sys.21776 [Online]. Available: https://incose.onlinelibrary.wiley.com/doi/10.1002/sys.21776

**`ledford2023dissertation`**

Current biblatex: A. B. Ledford, “A data element mapping and analysis (dema) approach for implementing a complete digital thread,” Establishes DEMA as a technology-agnostic methodology for systematic data element capture and mapping, Ph.D. Dissertation, Auburn University, Auburn, AL, 2023. [Online]. Available: http://etd.auburn.edu/xmlui/handle/10415/8918

Planned biblatex: A. B. Ledford, “A data element mapping and analysis (DEMA) approach for implementing a complete digital thread,” Ph.D. Dissertation, Auburn University, Auburn, AL, 2023. [Online]. Available: http://etd.auburn.edu/xmlui/handle/10415/8918

**`ledford2023ieee`**

Current biblatex: A. B. Ledford, G. Harris, and G. Purdy, “Implementing a complete digital thread: The need for data element mapping and analysis,” IEEE Open Journal of Systems Engineering, vol. 1, pp. 139–152, 2023, Proposes DEMA as tool for identifying data elements at granularity necessary to connect digital threads. DOI: 10.1109/ OJSE . 2023 . 3325189 [Online]. Available: https://ieeexplore.ieee.org/document/10286971/

Planned biblatex: A. B. Ledford, G. Harris, and G. Purdy, “Implementing a complete digital thread: The need for data element mapping and analysis,” IEEE Open Journal of Systems Engineering, vol. 1, pp. 139–152, 2023. DOI: 10.1109/ojse.2023.3325189 [Online]. Available: https://ieeexplore.ieee.org/document/10286971/

**`oleary2025ai4se`**

Current biblatex: D. J. O’Leary and A. N. Ledford, Ai-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes, Workshop Presentation, AI4SE & SE4AI Research and Application Workshop, The George Washington University, Sep. 2025.

Planned biblatex: D. J. O’Leary and A. B. Ledford, “AI-enhanced DEMA: Transforming implicit system knowledge into intelligent, compliant, and documented processes,” Workshop presentation, presented at the AI4SE & SE4AI Research and Application Workshop (The George Washington University), Sep. 2025.

## Commits

This branch contains the proposal only and is not merged. No publication commit, refs implementation change, catalog mutation, register entry or accepted fixture is created. The review session owns merge/ledger decisions; the publication session owns eventual document/configuration changes. Committing this proposal is not approval to execute it.

## Timing and verification

Final verification: all 957 hashed inputs (publication files plus catalog database) match their initial SHA-256 values, and publication staged/unstaged status is unchanged. All 34 baseline reference strings also match the current TDD PDF after whitespace/punctuation normalization. Read-only assessment and bounded source/metadata search, with scratch rendering probes. No intake or conversion execution timing is claimed. No unrelated product tests were run for a proposal-only change. Scratch evidence is `/private/tmp/refs-dema-proposal/`: `assessment.json`, `gpt4-doi-binding.json`, `citations.json`, `title-candidates.json`, `pdf-hits.json`, `doi-hits.json`, source hashes, current artifact extractions, planned records, both serializer outputs and four per-key engine maps. These are reproducible local evidence, not durable publication fixtures. Metadata retrieval fetched primary bibliographic information only, not source attachments into any store.

## Owner decisions

1. Choose the preprint or later publication separately for Sequeda (2023 arXiv versus GRADES-NDA 2024), Nomic (2024 arXiv versus TMLR 2025) and DSPy (2023 preprint versus ICLR 2024 / existing `khattab2024`). Current probe keeps the preprints. Choosing another version requires revised predictions before execution.
2. Resolve GPT-4 identity/version/year/key handling before intake: current bibliography says v6/2024 under `openai2024gpt4`; catalog holds 2023 under `openai2023gpt4` with the common DOI and earlier file. Neither duplicate creation nor changing citations/shared keys is authorized. A choice requiring an alias/export capability becomes a separate refs decision, not a conversion workaround.
3. Approve the source-supported Sequeda title/coauthors and ReMatch four-author/preprint corrections, and the INSIGHT published metadata. Approve or amend Allison B. on AI4SE: slide cover contradicts the bibliography and CV's A. N.; no external CV correction is included.
4. Decide the actual cited object for Claude 3 (model card versus launch page), the historical targets for embeddings/FedRAMP/CMMC, and whether the shorter-title GradeBot poster is the intended INFORMS source. Unresolved files stay missing; no invented dates or current-version substitution.
5. Decide how the disclosed fidelity blockers should be handled in a separate refs/style pass before this conversion can be adopted: literal `others`, CSL arXiv identification, speech event fields, proceedings volumes and webpage dates. This proposal requests no workaround and does not implement a fix.
6. Approve or amend the title-case/protection policy, the nine note-to-context moves, the obsolete forthcoming-note retirement and the semantic retypes. These cause the visible changes documented above; a style loss is not implicitly accepted by approving a type.
7. Approve three targets/four consumer gates, all 34 cited memberships, proposed file placement and the 27-key acquisition/identity list. Execution still requires a clean publication commit, revised proposal if any choice changes it, and a quoted owner decision delivered through `comms/`. Acquisition gaps may only be carried forward as explicitly disclosed missing sources. Gate acceptance, fixture recording and adoption remain later owner gates.

## Findings

### refs

- **Creator truncation is not faithfully represented in CSL JSON.** The adapter turns BibTeX `and others` into an ordinary family name. The actual IEEE CSL render prints “and others” for Touvron, Kadavath and Konda, whereas the current bibliography prints “et al.” Brown's long list masks the same representation behind the style's truncation threshold. Biber recognizes the sentinel on its own route. Do not remove that author or invent a complete list to hide the defect.
- **The preprint needs consumer-level coverage.** The canonical article can hold arXiv archive/number/identifier and biblatex prints the proper eprint, but `serialize_csl` drops identifier extensions and the vendored IEEE article layout never prints archive. It shows a bare number where the current render identifies arXiv. This is a disclosed refs/consumer-boundary finding, not justification for a fake journal or publisher.
- **Existing DOI identity plus another citation key is unresolved in this workflow.** Raw GPT-4 intake misses an existing work because the input lacks its DOI; adding that DOI binds to a different stored key/version. Export uses the stored key. The proposal cannot both promise reuse and preserve manuscript keys without an owner-selected policy/capability. DSPy's published alternative creates a similar decision.
- **Semantic retypes expose silent consumer losses.** The vendored IEEE speech macro reads legacy `event` rather than `event-title`; it loses the planned workshop/INFORMS event facts that native biber prints. IEEE conference layout omits Brown/Wei's volume numbers, and webpage layout omits the supplied embeddings/FedRAMP years. Metadata survives in JSON, so these are style/consumer limits rather than serializer erasure; they still prevent a lossless conversion claim. No style edit is authorized.
- **Original-only facts do not complete canonical records.** `howpublished` arXiv and presentation descriptions are absent from raw canonical metadata; AI4SE `organization` is explicitly preserved as unmapped input. The original bytes survive, but CSL needs honest canonical completion and a tested consumer. Retyping cannot be used merely to conceal the missing fact.

### guide

- Consumer inventory must be format-local: PDD's PDF is biber while its DOCX is citeproc, despite a shared `.bib` and an IEEE label. Count four artifacts and three target bindings; preserve current layout/backreference behavior separately from bibliography wording.
- Count distinct arXiv entries, not matching lines. The input has seven, with two incorrect author/title/venue records; “thirteen mention arXiv” was a line count. Verify cited-source identity before type conversion and before calling a same-title file a match.
- Specify version/key decisions before DOI enrichment and intake. A v6 citation must not silently become an existing v3-era resource, and a conference publication is not automatically interchangeable with its preprint. Published-version alternatives belong in the approval proposal.
- The guide still says per-project case policy and labels on `add --file` are unavailable, although 0.9.0 provides them. Its metadata-completion and attachment steps should be updated in the later help/release pass; this report changes neither guide nor ledger.
- Separate a source's own file from a report that cites it, and label historical-page or exact-version acquisition gaps. A source-link list is not evidence that the cited file exists locally or was fetched. A proposal must disclose consumer losses even when the serializer returns no blocking warning.

**Stop at step 4.** Send this proposal to the owner through session 1. No backup, import, fetch, live export, fixture recording or adoption follows from this report alone.
