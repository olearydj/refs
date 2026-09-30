# Pipyer paper conversion execution — 2026-09-29

**Status: execution complete; awaiting owner gate acceptance.** The native gate matches all 11 approved predictions. All 423 entries from previously converted projects remain identical. Nothing is recorded or adopted in the live paper yet. All required source attachments are now present; recording and adoption remain separate owner gates.

## Backup and scope

Execution follows the owner's “Approve, 1A + 2B (Recommended)” in `comms/2026-09-29-201409-s1-pipyer-proposal-decision.md`, on `s2/pipyer-paper-execution` based on merged proposal `ebb845f`. Before mutation, the live project records/membership exactly matched the proposal snapshot, and all tracked publication bytes and clean commit `de88944` matched. The requested backup `/Volumes/Casa/refs-backups/2026-09-29-before-pipyer-paper-conversion` was created and validated before record mutation. It includes catalog/configuration/resource inventory, not external file contents.

## Inventory and consumers

One current consumer: `paper.qmd` to native Quarto PDF using default Chicago author-date through citeproc/LuaLaTeX, including the native Mermaid figure. One planned target: `references.json`, csl-json-v1. The new register row prepares only the bibliography-path switch and approved Kapoor citation switch inside scratch; its readable helper is `tests/fixtures/real-trial/pipyer_consumer.py`. The future Inara `.bib` target remains unconfigured. Publication source, old `.bib`, `.refs.toml` absence, and all live export-target bindings remain unchanged until adoption.

## Import outcomes by key

No repeated import or project creation: the existing 11-record project and adopted portable export were already proven. Applied ten approved record updates, reused `khattab2024` unchanged, and added `kapoor-2025-aiAgents` through refs-JSON admission. Each update/add was dry-run first and checked against the approved canonical payload; the same operations were rehearsed on a disposable catalog. The new article's expected similar-title warning names its distinct preprint, not an identity collision. Linked publication and preprint bidirectionally, uncited `kapoor2024` only from this project, and cited the new publication. Membership remains 11; the preprint and its originals remain in the catalog.

## Record completions by key

All completions follow the proposal: Nextflow protection/language; retained Kapoor preprint completion and new TMLR identity; Snakemake's source dash; lowercase targets protection; Pydantic AI software/repository retype; Qiu v2 and R-LAM v1 preprint types/dates; ReciPies/ML protection and non-dropping van de particle; Corey Zumar restored to MLflow's author list with name protection; and AGORA's English title policy. DSPy's entire shared record, attachment and existing links are unchanged. Complete canonical records and per-operation receipts are in [the evidence JSON](2026-09-29-pipyer-paper-execution.json).

The owner's sole amendment was re-predicted before proceeding: `pydanticai2026` is software, kind repository, version **1.106.0**, issued **2026-06-05**, repository URL, and **no accessed date**. Its single context sentence records that Pipyer's lock pins this release and the owner's dated exception to the current-on-access rule. PyPI upload history and GitHub's published release both verify June 5. The native entry is:

> Pydantic Services Inc. 2026. Pydantic AI. Source code repository. V. 1.106.0. Released June 5. https://github.com/pydantic/pydantic-ai.

The other ten entries remained identical to the original proposal prediction. Therefore the conditional authorization to continue was satisfied. The README and API captures use **v1.106.0 commit `1b42945de65b2816fed3cffa371671a2ac759241`**, not the default branch; the API capture is the immutable Git commit endpoint. Each wrapper contains the original content, source URL, full commit, release tag, retrieval UTC time and content hash. Managed labels contain the commit prefix and local capture date, 2026-09-29; UTC retrieval was September 30.

## Sources found, fetched, and the fetch list for the owner

Seven approved PDFs were acquired and checked at their first page: Kapoor arXiv v1, targets JOSS, Qiu arXiv v2, R-LAM arXiv v1, ReciPies JOSS, MLflow's published author-hosted IEEE PDF, and the ACL AGORA paper. Edition identifiers, bylines and publication lines agree with the proposed records. Both release-pinned software captures were acquired and checked. Existing DSPy is reused.

The owner supplied the three remaining PDFs after the initial search found none. Each edition was independently checked before attachment: Nextflow's published Nature Biotechnology 35(4), April 2017, pages 316–319, with the six-author byline; AI Agents That Matter's TMLR 05/2025 publication with its five authors and OpenReview identity Zy4uFzMviZ; and Snakemake's Bioinformatics 28(19), 2012, pages 2520–2522, with both authors and DOI bts480. Nextflow's four-page journal extract includes adjacent correspondence and is preserved intact. All source gaps are closed. The evidence retains the earlier unsuccessful search as history and adds the owner-file verification receipts.

## Attachments with final names and hashes

All twelve new resources (ten PDFs and two software captures) were admitted with `resource add --move` after dry runs. Every managed destination was rehashed against the supplied original, and each intake source was confirmed removed only after the verified move. Receipts retain the move journal operation and final destination. No file under the live paper was moved.

| Key / label | Managed relative path | SHA-256 |
|---|---|---|
| `kapoor2024` / `v1` | `unfiled/AIAgentsThatMatter-2024-v1.pdf` | `1681013e0421f9d193ca5bb556b566f50d1e5eaa43d7a9700a31ca3dd0e2ff7a` |
| `landau2021` / `published` | `unfiled/TheTargetsRPackageADynamicMakeLikeFunctionOrientedPipelineToolkitForReproducibilityAndHighPerformanceComputing-2021-published.pdf` | `7cede44db66fcc5399dc725cb4ffd1cc6bac634b5ac527eb3b7b46102e4259bb` |
| `qiu2026` / `v2` | `unfiled/BlueprintFirstModelSecondAFrameworkForDeterministicLLMWorkflow-2026-v2.pdf` | `939f7bf23e9349756efda23cbadf08d92ce5e5d4ed5ac8704bafba892d14b587` |
| `sureshkumar2026` / `v1` | `unfiled/RLAMReproducibilityConstrainedLargeActionModelsForScientificWorkflowAutomation-2026-v1.pdf` | `2b30e54f43ba6f3e69b2559816424f756bc3c8f9ec8c443a197c2f9a01b23d8d` |
| `vandewater2026` / `published` | `unfiled/ReciPiesALightweightDataTransformationPipelineForReproducibleML-2026-published.pdf` | `b095f79b3d5d7b8f74d4dc1525ea97588f1285d4de92f279a44658f0734ff702` |
| `zaharia2018` / `published` | `unfiled/AcceleratingTheMachineLearningLifecycleWithMLflow-2018-published.pdf` | `24fe5860c8a91f0b3294d58607e18ed7641e54c0e2b0ef450d87eeb32f7ac636` |
| `zhang2025` / `published` | `unfiled/UnifyingLanguageAgentAlgorithmsWithGraphBasedOrchestrationEngineForReproducibleAgentResearch-2025-published.pdf` | `3825a1f24615e649b28ed1b1e9c5bb9c743df9078f322497968fc35d1a29239c` |
| `pydanticai2026` / `readme-1b42945-2026-09-29` | `unfiled/PydanticAI-v1.106.0-2026-readme-1b42945-2026-09-29.json` | `ea8c9292789c9cebc0b4220504c3b29f489e7658a3f4c0eb88ceae4dc9e7c09a` |
| `pydanticai2026` / `api-1b42945-2026-09-29` | `unfiled/PydanticAI-v1.106.0-2026-api-1b42945-2026-09-29.json` | `441107d2feb0a044e6bbc2552b216371477f003602820abcc172f6bc528155ee` |
| `ditommaso2017` / `published` | `unfiled/NextflowEnablesReproducibleComputationalWorkflows-2017-published.pdf` | `b9812621325d28becd34bb58ad192340f1ae70fb33eec38ddf9a4d3df5c48739` |
| `kapoor-2025-aiAgents` / `published` | `unfiled/AIAgentsThatMatter-2025-published.pdf` | `18038b6c27700657711c6ec00e345355bf9ab68e4ad87104ce4985f0f0139750` |
| `koster2012` / `published` | `unfiled/SnakemakeAScalableBioinformaticsWorkflowEngine-2012-published.pdf` | `d33c43ef89792abcb07955f3a5c728e9966135b44e6f27752ada7450194d63dd` |

## Export gate table

The register renders the whole native paper, reads bibliography identities and citation targets from its generated TeX, and extracts actual PDF reference paragraphs. It checks entry count, first-author prefix and DOI/URL against the corresponding exported identity; all cited identities resolve. Both the revised prediction and live-catalog gate render four pages. The changed software-reference page was visually checked after the 1.106.0 amendment; no clipping or overlap was introduced.

The new unrecorded fixture makes the generic harness mark entries changed and exit **3**. Against the approved revised prediction, **all 11 are expected-identical**. Against the live paper's old bibliography, the two identical and nine deliberate changes remain those reported in the proposal, with the owner's revised software release replacing the proposed 2.51.0. No unexpected difference occurred. Exact native PDF text follows; spaces introduced by line wrapping are retained.

| Key | Old live paper → approved result | Gate vs approved |
|---|---|---|
| `ditommaso2017` | Identical | Identical |
| `kapoor-2025-aiAgents` | Expected change | Identical |
| `khattab2024` | Expected change | Identical |
| `koster2012` | Expected change | Identical |
| `landau2021` | Expected change | Identical |
| `pydanticai2026` | Expected change | Identical |
| `qiu2026` | Expected change | Identical |
| `sureshkumar2026` | Expected change | Identical |
| `vandewater2026` | Identical | Identical |
| `zaharia2018` | Expected change | Identical |
| `zhang2025` | Expected change | Identical |

### `kapoor-2025-aiAgents`

Before: Kapoor, Sayash, Benedikt Stroebl, Zachary S. Siegel, Nitya Nadgir, and Arvind Narayanan. 2024. AI Agents That Matter. arXiv:2407.01502. https://doi.org/10.48550/arxiv.2407.01502.

After: Kapoor, Sayash, Benedikt Stroebl, Zachary S. Siegel, Nitya Nadgir, and Arvind Narayanan. 2025. “AI Agents That Matter.” Transactions on Machine Learning Research, May. https://openreview.net/forum?id=Zy4uFzMviZ.

### `khattab2024`

Before: Khattab, Omar, Arnav Singhvi, Paridhi Maheshwari, et al. 2024. “DSPy: Compiling Declarative Language Model Calls into State-of-the-Art Pipelines.” International Conference on Learning Representations. https://proceedi ngs.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html.

After: Khattab, Omar, Arnav Singhvi, Paridhi Maheshwari, et al. 2024. “DSPy: Compiling Declarative Language Model Calls Into State-of-the-Art Pipelines.” International Conference on Learning Representations. https://proceedi ngs.iclr.cc/paper_files/paper/2024/hash/f1cf02ce09757f57c3b93c0db83181e0-Abstract-Conference.html.

### `koster2012`

Before: Köster, Johannes, and Sven Rahmann. 2012. “Snakemake: A Scalable Bioinformatics Workflow Engine.” Bioinformatics 28 (19): 2520–22. https://doi.org/10.1093/bioinformatics/bts480.

After: Köster, Johannes, and Sven Rahmann. 2012. “Snakemake—a Scalable Bioinformatics Workflow Engine.” Bioin- formatics 28 (19): 2520–22. https://doi.org/10.1093/bioinformatics/bts480.

### `landau2021`

Before: Landau, William Michael. 2021. “The Targets R Package: A Dynamic Make-Like Function-Oriented Pipeline Toolkit for Reproducibility and High-Performance Computing.” Journal of Open Source Software 6 (57): 2959. https://doi.org/10.21105/joss.02959.

After: Landau, William Michael. 2021. “The targets R Package: A Dynamic Make-Like Function-Oriented Pipeline Toolkit for Reproducibility and High-Performance Computing.” Journal of Open Source Software 6 (57): 2959. https://doi.org/10.21105/joss.02959.

### `pydanticai2026`

Before: Pydantic Services Inc. 2026. Pydantic AI. Python software, version 1.106. https://ai.pydantic.dev/.

After: Pydantic Services Inc. 2026. Pydantic AI. Source code repository. V. 1.106.0. Released June 5. https: //github.com/pydantic/pydantic-ai.

### `qiu2026`

Before: Qiu, Libin, Yuhang Ye, Zhirong Gao, et al. 2026. Blueprint First, Model Second: A Framework for Deterministic LLM Workflow. arXiv:2508.02721v2. https://doi.org/10.48550/arxiv.2508.02721.

After: Qiu, Libin, Yuhang Ye, Zhirong Gao, et al. 2026. “Blueprint First, Model Second: A Framework for Deterministic LLM Workflow.” Preprint. arXiv, June 16. https://doi.org/10.48550/arxiv.2508.02721.

### `sureshkumar2026`

Before: Sureshkumar, Suriya. 2026. R-LAM: Reproducibility-Constrained Large Action Models for Scientific Workflow Automation. arXiv:2601.09749. https://doi.org/10.48550/arxiv.2601.09749.

After: Sureshkumar, Suriya. 2026. “R-LAM: Reproducibility-Constrained Large Action Models for Scientific Workflow Automation.” Preprint. arXiv, January 12. https://doi.org/10.48550/arxiv.2601.09749.

### `zaharia2018`

Before: Zaharia, Matei, Andrew Chen, Aaron Davidson, et al. 2018. “Accelerating the Machine Learning Lifecycle with MLflow.” IEEE Data Engineering Bulletin 41 (4): 39–45. https://people.eecs.berkeley.edu/~matei/papers/20 18/ieee_mlflow.pdf.

After: Zaharia, Matei, Andrew Chen, Aaron Davidson, et al. 2018. “Accelerating the Machine Learning Lifecycle With MLflow.” IEEE Data Engineering Bulletin 41 (4): 39–45. https://people.eecs.berkeley.edu/~matei/papers/20 18/ieee_mlflow.pdf.

### `zhang2025`

Before: Zhang, Qianqian, Jiajia Liao, Heting Ying, et al. 2025. “Unifying Language Agent Algorithms with Graph- Based Orchestration Engine for Reproducible Agent Research.” Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations), 107–17. https: //doi.org/10.18653/v1/2025.acl-demo.11.

After: Zhang, Qianqian, Jiajia Liao, Heting Ying, et al. 2025. “Unifying Language Agent Algorithms With Graph- Based Orchestration Engine for Reproducible Agent Research.” Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations), 107–17. https: //doi.org/10.18653/v1/2025.acl-demo.11.

The all-project gate confirms **423 existing entries identical**: JHL 195, danvas 22, manufacturing 78, DEMA 80, NEO 4, CV 44. The additional 11 Pipyer entries match the revised prediction exactly; individual and all-project extractions agree. Exit 3 is solely Pipyer's missing unrecorded fixture. No `--record` was used.

## Commits and verification

Execution changes are confined to the register, readable scratch consumer, and this report/evidence on `s2/pipyer-paper-execution`. Full suite: **1,207 passed in 42.30 seconds**. Ruff, source ty and diff checks passed. Publication remains clean at `de88944`, with every tracked hash equal to preflight. Existing export-target rows equal the backup, and the shared DSPy record is unchanged. After the final three attachments, comparison with the gate-time state confirmed that only resources, revisions and update timestamps changed for those three records; membership and all bibliographic metadata remain identical. The existing render results therefore still apply; no code changed and the full suite was not repeated for attachment-only work. Native checks and receipts are retained under `/private/tmp/refs-pipyer-execution` (`gate`, `all-gate`, revised prediction and intake/attachment evidence).

## Timing and next step

Work began after the 20:14 CDT decision on 2026-09-29. The initial execution completed catalog work and render checks, then paused for three owner PDFs. Those files have now been verified and attached on the same branch without repeating intake. Next action belongs to s1 and the owner: accept the completed export gate. Recording and live adoption remain separate steps after acceptance. No live export, paper edit/commit or merge has occurred.

## Findings for refs

No product change is needed. Existing adopted-export provenance avoids duplicate import; no target binding changes before adoption. The explicit software version/date fields print correctly through CSL JSON, without inventing an accessed date.

## Findings for the guide

The owner's exception identifies the actually used software release and pins its captures to that tag. No guide edit is proposed. The attachment requirement is now satisfied, including the retained preprint and distinct publication.
