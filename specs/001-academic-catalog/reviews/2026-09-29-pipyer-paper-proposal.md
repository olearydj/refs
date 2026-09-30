# Pipyer paper conversion proposal — 2026-09-29

## Decisions for the owner

1. **Replace Kapoor's preprint citation with the published article?** **Recommend A:** create `kapoor-2025-aiAgents`, link it to retained `kapoor2024`, and switch this internal paper's citation and project membership to the May 2025 TMLR publication. The new key is refs-generated; neither existing identity nor key changes. **B:** keep citing the July 2024 preprint. The publication supports the cited cost/reproducibility claim. Its [indexed publisher PDF](https://openreview.net/pdf?id=Zy4uFzMviZ) identifies TMLR 05/2025; direct retrieval is bot-gated, so its acquisition is on the owner's fetch list. This proposal predicts A.
2. **Which Pydantic AI release should this implementation paper cite?** **Recommend A, following the guide:** with no recorded accessed date, cite current stable **2.51.0**, released **2026-09-25**, and set accessed to the execution capture date (the prediction uses 2026-09-29). **B:** explicitly except this record from the current-on-access rule and retain the implementation's **1.106.0**, released **2026-06-05**. The existing bibliography says 1.106 and Pipyer's `uv.lock` pins 1.106.0; neither supplies an accessed date. A updates a related-software citation, not Pipyer's dependency, and must not be read as a claim that Pipyer was tested against version 2. B more directly identifies the used implementation. The [PyPI release history](https://pypi.org/project/pydantic-ai/#history) verifies both release dates. The rendered prediction below uses A; choosing B requires a revised admitted candidate and render before execution approval. No historical access date is inferred from the draft date or file mtime.

Everything else below is part of the proposed conversion for approval, not a separate undecided policy: title case, retained existing keys, one current `csl-json-v1` target, source captures, and retirement of the unused `.bib` at adoption. No other owner judgment was identified. This is proposal work only; no live catalog/project mutation, import, backup, source acquisition into stores, or fixture recording has occurred.

## Backup and scope

Execution would begin with `/Volumes/Casa/refs-backups/2026-09-29-before-pipyer-paper-conversion`, validated before catalog mutation (use the actual execution date if later). The normal backup includes catalog/configuration/resource inventory, not external file contents. Proposal base: refs `315a370`, version 0.9.4. Publication: `/Volumes/Casa/pub/pipyer-paper`, clean at `de88944`; it is an internal prospective JOSS paper, not submitted, delivered or published. Internal-document version rules therefore apply.

The source tree remains byte-identical to the seven tracked files recorded in the companion JSON. No uncommitted or untracked nonignored files appeared. The ignored `.ho/`, `.quarto/`, generated `output/` PDFs and figures, and `/docs/sessions` exclusion are left alone. `AGENTS.md` and `PROJECT_CONTEXT.md` are tracked; their statements that the `.bib` is authoritative, and the latter's stale “not a Git repository” statement, need updates at adoption, staged by path. The kickoff records the owner's authorization for git initialization, already done by session 1.

## Inventory and consumers

`references.bib` is the only bibliography. Pandoc's parsed citation nodes identify 11 distinct keys, all 11 bibliography records, with no uncited entries. Both full native renders produce those 11 reference entries. There is no `.refs.toml`, sync script, custom CSL or secondary active manuscript. `_quarto.yml` selects `output/pdf` and PDF through Quarto/citeproc's default Chicago author-date style. Its current reader is `paper.qmd`; the Mermaid figure is rendered natively. Quarto 1.10.18 and bundled Pandoc 3.10 were used, with LuaLaTeX. The owner authorized Quarto's headless Mermaid renderer on disposable copies in `comms/2026-09-29-200402-s1-pipyer-mermaid-decision.md`.

The existing generated proof was inspected through extracted text; its complete extracted text is identical to the fresh full baseline render from the committed sources. The software repository `/Volumes/Casa/dev/pipyer` has no `paper.md`, `.qmd` or `.bib` consumer. README's future JOSS/Inara route is a future consumer requiring `paper.bib` with **biblatex-v1** for Pandoc/citeproc, alongside the eventual `paper.md` in the public software repository. Do not configure or generate that target now. Its venue layout and reference checker belong to the later submission preparation.

### Existing catalog and export relationship

All 11 keys are already cited in catalog project `pipyer-paper` (`b1ad93bd-65f2-4458-92a7-5f5365d4c98a`, project revision 2). Import `f90d748c-cccd-4d9e-9db6-d9038f059b82`, origin `pipyer-paper`, finished 2026-09-23T00:36:45Z with 11 applied, zero unchanged/conflict/invalid, preserving the original input digest `91ca38cd5c78cd15ca256184b1d4be2b4d2dd430fa4f99a9b74c4b4e04183146`. This is the earlier input, not the current generated file.

The current `references.bib` SHA-256 is **`cf3eeae05bfbf12f0a6f352f2034e7655100d843047d4404e947d28aa33e3cb3`**. It equals both its existing export-target baseline (pending digest null) and a fresh current `portable-bibtex-v1` export made only against a disposable catalog snapshot. Thus this is an unchanged, already-adopted export, not an unadopted legacy bibliography or a hand-edited outside change. There is no need to re-import 11 existing identities or recreate the project to establish provenance.

Under the files contract, the recommended `references.json` is a new absent destination: explicit export adopts it without `--adopt` or `--overwrite`. Do not overwrite or rebind `references.bib` as JSON. At adoption, switch the reader, check no remaining active reader needs the `.bib`, retire it in the same publication commit, and use `refs export --forget /Volumes/Casa/pub/pipyer-paper/references.bib` to retire its old target registration (forget removes registration, not the file). Git retains the old export and the catalog retains its original entries. If the owner instead keeps portable BibTeX for a real consumer, its existing unchanged binding can be exported normally; a future Inara consumer needs its own biblatex target, not an assumed reuse of portable BibTeX.

## Planned import outcomes by key

Reuse the 11 admitted identities and existing project. No repeated bulk import is proposed because the file is already their verified export. The proposed record completion has ten updates, one unchanged reuse (`khattab2024`), and one new publication (`kapoor-2025-aiAgents`). This leaves 12 relevant catalog records but **11 project members**, replacing the preprint's membership with the publication. Retain `kapoor2024` in the catalog and link the versions. If decision 1 is B, keep its membership and omit the new publication.

Every relevant record passed refs admission in scratch: ten revision-guarded update dry runs, one no-op dry run for DSPy, and a refs-JSON add dry run for the new publication. The same operations were applied only to the disposable copy to export a full proposed bibliography; canonical dry-run and applied records matched. The new publication raises the expected similar-title notice for its preprint; title similarity is not identity and the journal article stays separate. Admission warnings and complete canonical payloads are in [the companion JSON](2026-09-29-pipyer-paper-proposal.json). No refusal was bypassed. An initial local rehearsal invocation missing the patch envelope's schema_version was corrected before that invocation wrote anything; a subsequent assertion was corrected to compare the add preview's nested record, and the disposable catalog was reset before the successful rehearsal.

## Record completions by key

Existing keys and identity bindings stay fixed. Set explicit English language and title protection on the ten completed existing records; keep DSPy's already-approved record unchanged. Notes are not a workflow log. Proposed context is limited to cited arXiv revisions and the software release/date lookup. Existing originals are preserved.

| Key | Proposed completion and version choice | Primary verification |
|---|---|---|
| `ditommaso2017` | Keep published journal article, six authors, 2017, 35(4), 316–319, DOI. Protect Nextflow. No version substitution. | [Nature article](https://www.nature.com/articles/nbt.3820): title, authors, venue, pages and publication date agree. Publisher full-PDF acquisition remains owner-side. |
| `kapoor2024` | Retain as distinct preprint; retype document → article, genre Preprint, publisher arXiv, issued 2024-07-01, version-specific URL; remove redundant arXiv note; context names v1. Uncite only if A. | [arXiv v1](https://arxiv.org/abs/2407.01502v1), five authors and title verified. |
| `kapoor-2025-aiAgents` | New journal article, same five authors and title, TMLR, 2025-05, official OpenReview URL; no invented DOI, volume, issue or page range. Link preprint and cite publication under decision 1A. | [TMLR PDF](https://openreview.net/pdf?id=Zy4uFzMviZ), indexed cover identifies published 05/2025; direct endpoint challenged. |
| `khattab2024` | Reuse published ICLR 2024 identity and existing attachment/link to `khattab2023dspy`; no metadata/context edit. | [Official proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html) supports current metadata. Local proceedings PDF is marked ICLR 2024 but says Self-Improving Pipelines, Sri Vardhamanan and Thomas T. Joshi; page metadata says State-of-the-Art Pipelines, Sri Vardhamanan A and Thomas Joshi. Retain the previously accepted proceedings metadata; do not silently “correct” this shared DEMA record from its differing cover. |
| `koster2012` | Keep published article and DOI, authors, 28(19), 2520–2522. Restore the source title's em dash rather than the invented colon; protect Snakemake. | [Publisher article](https://academic.oup.com/bioinformatics/article/28/19/2520/290322): title, authors, DOI and pagination agree; online date 2012-08-20, issue October 2012. Keep existing year precision. |
| `landau2021` | Keep JOSS article, 6(57), 2959; protect `targets`, R and Make, restoring the software's lowercase name. This is an article about software, not a software-release record. | [Publisher PDF](https://joss.theoj.org/papers/10.21105/joss.02959.pdf): author, title, DOI and journal citation verified, published 2021-01-15. |
| `pydanticai2026` | Retype document → software, kind repository, corporate author unchanged, protected Pydantic AI, repository URL. Under 2A, version 2.51.0 and issued 2026-09-25; accessed/capture date current, not guessed historical. Replace the obsolete howpublished rendering with proper version/date fields. | [Repository](https://github.com/pydantic/pydantic-ai), README and MIT license at lookup commit verify product and corporate attribution; [PyPI](https://pypi.org/project/pydantic-ai/2.51.0/) supplies release date. Pipyer's local lock verifies 1.106.0 as the implementation version, not current release. |
| `qiu2026` | Keep same preprint identity and key, document → article with genre Preprint/publisher arXiv; protect LLM, set issued 2026-06-16 and v2 URL; context names cited v2. | [v2 PDF](https://arxiv.org/pdf/2508.02721v2): ten authors, title, revision and procedural-control claim verified. No journal reference or published replacement found in the current arXiv record and title search. |
| `sureshkumar2026` | Keep preprint, document → article with genre Preprint/publisher arXiv, protect R-LAM; issued 2026-01-12, v1 URL and short revision context. | [v1 PDF](https://arxiv.org/pdf/2601.09749v1): author, title, date and structured-action/provenance claim verified. No published replacement found in current arXiv record and title search. |
| `vandewater2026` | Keep published JOSS article 11(117), 9261. Protect ReciPies and ML. Change `van de` from dropping to non-dropping particle: bibliography remains Water under Chicago's demotion, but in-text citation correctly becomes van de Water. | [Publisher PDF](https://joss.theoj.org/papers/10.21105/joss.09261.pdf): Robin P. van de Water, Hendrik Schmidt, Patrick Rockenschaub; publication 2026-01-05. |
| `zaharia2018` | Keep published IEEE Data Engineering Bulletin article 41(4), 39–45 and author-hosted published PDF URL. Add omitted twelfth author **Corey Zumar**, protect MLflow. | [Author's PDF](https://people.eecs.berkeley.edu/~matei/papers/2018/ieee_mlflow.pdf): all twelve authors on cover, IEEE copyright/venue, printed pages 39–45. The added author is hidden by Chicago's et al. but belongs in the canonical record. |
| `zhang2025` | Keep ACL 2025 System Demonstrations publication, twelve authors, pages 107–117, DOI and official URL. No preprint substitution. | [ACL PDF](https://aclanthology.org/2025.acl-demo.11.pdf): title, authors, venue, page range and AGORA evaluation claim verified. |

The preprint choices are explicit: Kapoor changes to its publication under decision 1A; Qiu remains v2 and Sureshkumar remains v1 because no publication was found; DSPy and the other seven non-preprint works retain their cited editions. The bibliography's current arXiv howpublished strings are not mistaken for publication venues. Version context does not print in the candidate reference list: Qiu's visible v2 identifier becomes the dated arXiv preprint citation, while the version-specific URL and context remain in the exported/canonical data.

## Sources found, planned fetches, and owner fetch list

Local search covered the publication (including generated files), vault project `/Volumes/Casa/obsidian/vault/projects/pipyer`, `/Volumes/Casa/refs/lib`, DEVONthink exports at `/Volumes/Casa/tmp/_from2020mbp/devonthink`, and `~/Downloads`. A bounded first-page text scan of **1,511 PDFs** sought the ten unattached works' exact DOI/arXiv identifiers or distinctive title strings and found no match. This is a disclosed search boundary, not proof no differently encoded scan exists. DSPy is already attached at `/Volumes/Casa/refs/lib/unfiled/DSPyCompilingDeclarativeLanguageModelCallsIntoStateOfTheArtPipelines-2024.pdf`, SHA-256 `0592d139b3a40ba26c6669012339242b59d88ac1c2ed2bf8250429446b9d487b`; its first page was read and it is reused, not duplicated. Vault synthesis notes are project material, not source attachments.

| Record | Planned acquisition at execution | Status / edition check |
|---|---|---|
| Nextflow | [Nature PDF](https://www.nature.com/articles/nbt.3820.pdf) | **Owner fetch**: Nature identity-provider redirect blocks direct retrieval. Obtain the 2017 Nature Biotechnology 35, 316–319 article, not supplementary material. |
| Kapoor preprint | [arXiv v1 PDF](https://arxiv.org/pdf/2407.01502v1) | Retained 2024 version; fetch and attach to the preprint, even when uncited. |
| Kapoor publication | [TMLR PDF](https://openreview.net/pdf?id=Zy4uFzMviZ) | **Owner fetch**: OpenReview browser challenge. Indexed PDF cover was checked for TMLR 05/2025; final file must be verified against that edition before attachment. |
| Snakemake | [Publisher article/download](https://academic.oup.com/bioinformatics/article/28/19/2520/290322) | **Owner fetch**: article text is available but direct PDF endpoint failed; obtain published bts480, pages 2520–2522. |
| targets | [JOSS PDF](https://joss.theoj.org/papers/10.21105/joss.02959.pdf) | Direct publisher source inspected; ordinary execution fetch. |
| Pydantic AI | Default-branch README and repository API metadata | Two capture resources, both named/labeled with commit and date; see below. No ZIP/source checkout needed. |
| Qiu | [arXiv v2 PDF](https://arxiv.org/pdf/2508.02721v2) | Cover verified 16 June 2026 v2; ordinary execution fetch. |
| R-LAM | [arXiv v1 PDF](https://arxiv.org/pdf/2601.09749v1) | Cover and abstract verified; ordinary execution fetch. |
| ReciPies | [JOSS PDF](https://joss.theoj.org/papers/10.21105/joss.09261.pdf) | Published article inspected; ordinary execution fetch. |
| MLflow | [Author-hosted published PDF](https://people.eecs.berkeley.edu/~matei/papers/2018/ieee_mlflow.pdf) | Published IEEE page/author lines inspected; use this accessible source, not a later MLflow paper. |
| AGORA | [ACL PDF](https://aclanthology.org/2025.acl-demo.11.pdf) | Published proceedings cover inspected; ordinary execution fetch. |

No planned record is intentionally URL-only. For the software capture, the observed default branch is `main`, commit `768081688f17a2bcfbf9c2c40822d49e98ddac21` (2026-09-30T00:49:17Z, still September 29 locally). Read `README.md` at that commit and `https://api.github.com/repos/pydantic/pydantic-ai`; at execution resolve the then-current default-branch commit again and disclose drift. Resource names should identify README/API, commit and capture date, with URL, retrieval UTC time and SHA-256 in their capture metadata. The lookup is read-only; no source capture has been acquired for attachment yet. With no historical accessed date, use the actual capture date, and recheck the release current that day before committing metadata; a changed planned release requires reporting the difference.

## Planned attachments with final names and hashes

None added or moved during this proposal. Execution will fetch the approved sources to scratch, verify edition and hash, and use refs `resource add --move` into `unfiled` with convention-generated names. Use short labels such as `v1`, `v2`, `published`, and commit/date labels for software captures; final names/hashes belong in the execution receipt, not invented here. The retained preprint and new article get separate PDFs. Disclose every unresolved owner fetch at the gate. No own-work source file needs relocation in this pass.

## Planned targets

At adoption, create:

```toml
project = "pipyer-paper"

[[export.targets]]
output = "references.json"
profile = "csl-json-v1"
```

Use the default title-case policy; do not add a preserve override. Change `_quarto.yml` to `bibliography: references.json`, replace only `@kapoor2024` with `@kapoor-2025-aiAgents` if approved, and retire `references.bib` and its binding after checking readers. Keep all other citation keys. Add `docs/refs.md`, link it from README and tracked AGENTS, and update the tracked source map. No bibliography-copy script or future JOSS target is needed. Project prose remains unchanged; the source corrections do not authorize rewriting its argument or upgrading its software environment.

Execution will register one native PDF consumer with exact per-entry extraction. The scratch preparation changes only the bibliography path and approved Kapoor citation before rendering `quarto render paper.qmd --to pdf`; after adoption remove preparation, retain rendering and extraction. Use source citation identities and the native rendered PDF, not a standalone bibliography-only approximation. Checks of other registered consumers remain part of execution, particularly if an amended proposal changes the shared DSPy record.

## Expected export gate

Two full renders from disposable copies succeeded: current committed `.bib` baseline and proposed CSL JSON candidate, both **four pages**. The candidate came from refs admission and export against the disposable catalog; JSON was not hand-rendered around admission. The native PDF reference table predicts **2 identical, 9 expected wording changes, 0 unexplained changes**. Exact native PDF extraction is preserved below, including line-wrap spaces/hyphens. All 11 TeX citation identities resolve to bibliography identities; PDF links lead to reference pages 3 or 4. Chicago is author-date, so there are no bibliography numbers to preserve. The in-text changes are Kapoor 2024 → 2025 and Water → van de Water; the latter's bibliography remains demoted under W. No unresolved citations or render errors appeared.

All four candidate pages were visually inspected: no clipping or overlap; the existing figure's aspect ratio remains unchanged. This is a draft-layout check, not an Inara/JOSS layout claim. The existing saved proof is not overwritten. Current source hashes and clean Git status were rechecked after the renders.

### `ditommaso2017` — identical

Identical; protection/language completion does not change this reference.

Before: Di Tommaso, Paolo, Maria Chatzou, Evan W. Floden, Pablo Prieto Barja, Emilio Palumbo, and Cedric Notredame. 2017. “Nextflow Enables Reproducible Computational Workflows.” Nature Biotechnology 35 (4): 316–19. https://doi.org/10.1038/nbt.3820.

After: Di Tommaso, Paolo, Maria Chatzou, Evan W. Floden, Pablo Prieto Barja, Emilio Palumbo, and Cedric Notredame. 2017. “Nextflow Enables Reproducible Computational Workflows.” Nature Biotechnology 35 (4): 316–19. https://doi.org/10.1038/nbt.3820.

### `kapoor2024` — expected-change

Published version replaces preprint, year/venue/link and article formatting change (decision 1A).

Before: Kapoor, Sayash, Benedikt Stroebl, Zachary S. Siegel, Nitya Nadgir, and Arvind Narayanan. 2024. AI Agents That Matter. arXiv:2407.01502. https://doi.org/10.48550/arxiv.2407.01502.

After: Kapoor, Sayash, Benedikt Stroebl, Zachary S. Siegel, Nitya Nadgir, and Arvind Narayanan. 2025. “AI Agents That Matter.” Transactions on Machine Learning Research, May. https://openreview.net/forum?id=Zy4uFzMviZ.

### `khattab2024` — expected-change

Into is retained from the canonical title by CSL JSON; no shared-record edit.

Before: Khattab, Omar, Arnav Singhvi, Paridhi Maheshwari, et al. 2024. “DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines.” International Conference on Learning Representations. https://proceedi ngs.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html.

After: Khattab, Omar, Arnav Singhvi, Paridhi Maheshwari, et al. 2024. “DSPy: Compiling Declarative Language Model Calls Into State-of-the-Art Pipelines.” International Conference on Learning Representations. https://proceedi ngs.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html.

### `koster2012` — expected-change

Restore source dash; native wrapping changes with it.

Before: Köster, Johannes, and Sven Rahmann. 2012. “Snakemake: A Scalable Bioinformatics Workflow Engine.” Bioinformatics 28 (19): 2520–22. https://doi.org/10.1093/bioinformatics/bts480.

After: Köster, Johannes, and Sven Rahmann. 2012. “Snakemake—a Scalable Bioinformatics Workflow Engine.” Bioin- formatics 28 (19): 2520–22. https://doi.org/10.1093/bioinformatics/bts480.

### `landau2021` — expected-change

Protect the lowercase software name targets.

Before: Landau, William Michael. 2021. “The Targets R Package: A Dynamic Make-Like Function-Oriented Pipeline Toolkit for Reproducibility and High-Performance Computing.” Journal of Open Source Software 6 (57): 2959. https://doi.org/10.21105/joss.02959.

After: Landau, William Michael. 2021. “The targets R Package: A Dynamic Make-Like Function-Oriented Pipeline Toolkit for Reproducibility and High-Performance Computing.” Journal of Open Source Software 6 (57): 2959. https://doi.org/10.21105/joss.02959.

### `pydanticai2026` — expected-change

Software/repository, proper version and release date, repository URL (decision 2A).

Before: Pydantic Services Inc. 2026. Pydantic AI. Python software, version 1.106. https://ai.pydantic.dev/.

After: Pydantic Services Inc. 2026. Pydantic AI. Source code repository. V. 2.51.0. Released September 25. https: //github.com/pydantic/pydantic-ai.

### `qiu2026` — expected-change

Preprint type/venue/date replace legacy howpublished rendering; v2 remains explicit in canonical context and version URL.

Before: Qiu, Libin, Yuhang Ye, Zhirong Gao, et al. 2026. Blueprint First, Model Second: A Framework for Deterministic LLM Workflow. arXiv:2508.02721v2. https://doi.org/10.48550/arxiv.2508.02721.

After: Qiu, Libin, Yuhang Ye, Zhirong Gao, et al. 2026. “Blueprint First, Model Second: A Framework for Deterministic LLM Workflow.” Preprint. arXiv, June 16. https://doi.org/10.48550/arxiv.2508.02721.

### `sureshkumar2026` — expected-change

Preprint type/venue/date replace legacy howpublished rendering.

Before: Sureshkumar, Suriya. 2026. R-LAM: Reproducibility-Constrained Large Action Models for Scientific Workflow Automation. arXiv:2601.09749. https://doi.org/10.48550/arxiv.2601.09749.

After: Sureshkumar, Suriya. 2026. “R-LAM: Reproducibility-Constrained Large Action Models for Scientific Workflow Automation.” Preprint. arXiv, January 12. https://doi.org/10.48550/arxiv.2601.09749.

### `vandewater2026` — identical

Reference identical; non-dropping particle corrects its in-text citation.

Before: Water, Robin P. van de, Hendrik Schmidt, and Patrick Rockenschaub. 2026. “ReciPies: A Lightweight Data Transformation Pipeline for Reproducible ML.” Journal of Open Source Software 11 (117): 9261. https: //doi.org/10.21105/joss.09261.

After: Water, Robin P. van de, Hendrik Schmidt, and Patrick Rockenschaub. 2026. “ReciPies: A Lightweight Data Transformation Pipeline for Reproducible ML.” Journal of Open Source Software 11 (117): 9261. https: //doi.org/10.21105/joss.09261.

### `zaharia2018` — expected-change

CSL JSON retains With from canonical title. Added Corey Zumar remains behind et al.

Before: Zaharia, Matei, Andrew Chen, Aaron Davidson, et al. 2018. “Accelerating the Machine Learning Lifecycle with MLflow.” IEEE Data Engineering Bulletin 41 (4): 39–45. https://people.eecs.berkeley.edu/~matei/papers/20 18/ieee_mlflow.pdf.

After: Zaharia, Matei, Andrew Chen, Aaron Davidson, et al. 2018. “Accelerating the Machine Learning Lifecycle With MLflow.” IEEE Data Engineering Bulletin 41 (4): 39–45. https://people.eecs.berkeley.edu/~matei/papers/20 18/ieee_mlflow.pdf.

### `zhang2025` — expected-change

CSL JSON retains With from canonical title.

Before: Zhang, Qianqian, Jiajia Liao, Heting Ying, et al. 2025. “Unifying Language Agent Algorithms with Graph- Based Orchestration Engine for Reproducible Agent Research.” Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations), 107–17. https: //doi.org/10.18653/v1/2025.acl-demo.11.

After: Zhang, Qianqian, Jiajia Liao, Heting Ying, et al. 2025. “Unifying Language Agent Algorithms With Graph- Based Orchestration Engine for Reproducible Agent Research.” Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations), 107–17. https: //doi.org/10.18653/v1/2025.acl-demo.11.

## Commits and timing

Proposal branch: `s2/pipyer-paper-proposal`, off `315a370`. No publication or live catalog commits/writes. Read-only investigation and scratch admission/render work took about nine minutes on 2026-09-29; acquisition and execution time are not included. Scratch evidence is `/private/tmp/refs-pipyer-proposal`, including baseline/candidate PDFs and logs, admission receipts, local search, canonical proposals, extracted PDF links and exact gate prediction. The companion JSON preserves the review evidence independently of scratch cleanup.

## Findings for refs

No product-code change is proposed. A generated earlier export can already be adopted and current even though a publication has no `.refs.toml`; establish the existing import/target relationship before planning duplicate intake. The existing `export --forget` supports retiring its obsolete target. `howpublished` in the old BibTeX is original evidence, not a substitute for completing software/preprint canonical fields. The non-dropping particle correction affects in-text author names even when bibliography text is unchanged.

## Findings for the guide and project

No guide edit is proposed. The current-on-access software rule needs the owner's choice when an implementation paper names a historically pinned release but omits access metadata; that is decision 2, not permission to invent a date. The paper's existing broad related-work descriptions are consistent with the inspected source passages; this conversion does not certify every software claim or the stated 215-test count. The project should retain its own pre-submission recheck of related work, final JOSS artifacts and software release details. Stop after this proposal for the two choices and approval of the completed record/target/fetch plan.
