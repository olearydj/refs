# dema-llm conversion execution — 2026-09-27

**Gate accepted and fixtures recorded.** Owner decision relayed in `comms/2026-09-27-185859-s1-dema-llm-gate-accepted.md`: “html ref nums - the change is ok for this doc, tdd is internal”, “html defect - write it up for dema-llm if that is the right place to investigate / fix it”, and “proceed”. The fresh `--record` run at `/private/tmp/refs-dema-record-01` recorded all four fixtures against clean publication `7599aee94d14a437b94b9f2f4b71de0ebb89125d`. All 80 extracted entries are byte-for-byte identical to the accepted gate. The harness reports `recorded: true`; exit 1 reflects its pre-record comparison against four absent fixtures. The register now retains each fixture's publication, tool and recording provenance. Publication adoption and branch merge remain with s1 and the publication session. Seven verified owner downloads have since been attached; the APE edition remains unresolved as described below.

## Backup and scope

Owner authorization, relayed in `comms/2026-09-27-170441-s1-dema-llm-execute.md`: “approve all / dema-llm is clean / you may fire when ready”. Approved proposal `0eed7d0` was merged at `ded1eb8`; execution uses fresh branch `s2/dema-llm-execution` from that main commit. Rechecks passed at clean publication `7599aee94d14a437b94b9f2f4b71de0ebb89125d`: unchanged bibliography SHA-256 `36d0f3823a43f42e16fab530e3255f21a4e1e60808333ca017ff9d7df19d395a`, citation inventory, consumer settings/style and all 37 catalog bindings. The owner’s README/build/vocabulary commits do not change records, keys, memberships or predicted wording.

Backup `/Volumes/Casa/refs-backups/2026-09-27-before-dema-llm-conversion` validated before intake and again afterward. Catalog `c03298ee-caee-4e20-aa0c-ddf121aafc0a`, schema 6, backup revision 4520; current revision 4738. Member hashes, byte lengths, SQLite integrity/foreign keys and saved resource inventory all pass. External file contents are not in the backup. The [execution evidence](2026-09-27-dema-llm-execution-evidence.json) retains the manifest, IDs, original-entry hashes, attachment audits and fetch outcomes.

## Inventory and consumers

One refs project, `dema-llm`, now has 34 cited memberships. The three retained preprints stay in the catalog outside that membership. One scratch export target is `docs/references.json`, profile `csl-json-v1`; all four consumers use the project’s IEEE CSL. The live readers still use their original BibTeX and the PDD PDF still uses biber until adoption.

| Consumer | Native gate | Entries | Wording | Presentation finding |
| --- | --- | --- | --- | --- |
| TDD HTML | Full Quarto book, `_book/a6-references.html` | 34 | Expected | All 34 bibliography numbers change; existing citation-number mismatch remains |
| TDD PDF | Same full book, `DEMA-LLM-Design-Document.pdf` | 34 | Expected after PDF extraction normalization | Numbering stable |
| PDD DOCX | Full Quarto PDD, Word bibliography paragraphs | 6 | Expected | Numbering stable |
| PDD PDF | Full Quarto PDD, candidate citeproc versus existing biber | 6 | Expected after PDF extraction normalization | Numbering stable; approved backreferences removed |

The harness ran without `--record` at `/private/tmp/refs-dema-gate-03`. Exit 1 is solely the four absent accepted fixtures; every consumer completed and each expected entry was extracted. The [exact gate tables](2026-09-27-dema-llm-execution-gate.md) list every changed entry before and after for each consumer, marking expected wording and unpredicted numbering. [Structured gate evidence](2026-09-27-dema-llm-execution-gate.json) includes predictions and every HTML link check.

## Import outcomes and record completions by key

The filtered import preserved 33 original BibTeX entries, omitting only the replaced GPT-4 entry: **33 applied, zero unchanged, zero conflicts, zero invalid**; import ID `0abd4709-726c-4ea2-bbb7-953bf872c6a8`. Two separate publication records were then added, giving 35 new records. Existing `openai2023gpt4` and `khattab2024` were reused with revision-guarded context appends; their bibliographic metadata remained unchanged. Every completion and relationship mutation used the normal CLI and log path. All 33 imported per-entry byte strings match the original input exactly.

The table records every source’s final type and intake outcome. The approved per-key field changes, ten verbatim interpretation/historical notes and version identities are in the proposal; a post-execution field comparison verifies all 37 bibliographic records against those canonical candidates. Only the two planned `accessed=2026-09-27` values differ. No failed fetch received an access date. Existing keys were preserved; the two publication keys were generated as approved.

| Key | Intake | Final type | Cited | Resource state |
| --- | --- | --- | --- | --- |
| `sequeda2023` | import + completion | article | no; retained preprint | linked in place |
| `sheetrit2024` | import + completion | article | yes | linked in place |
| `ledford2023dissertation` | import + completion | thesis | yes | linked in place |
| `ledford2023ieee` | import + completion | article-journal | yes | linked in place |
| `ledford2025syseng` | import + completion | article-journal | yes | linked in place |
| `oleary2025ai4se` | import + completion | speech | yes | linked in place |
| `howard2007bloor` | import + completion | report | yes | owner fetch gap |
| `howard2011bloor` | import + completion | report | yes | owner fetch gap |
| `bernsteinhaas2008` | import + completion | article-journal | yes | owner download attached |
| `oracle2011migration` | import + completion | report | yes | acquired |
| `oleary2025binary-classification` | import + completion | speech | yes | linked in place |
| `olearyledford2026insight` | import + completion | article-journal | yes | linked in place |
| `brown2020` | import + completion | paper-conference | yes | acquired |
| `wei2022` | import + completion | paper-conference | yes | acquired |
| `anthropic2024claude3` | import + completion | report | yes | acquired |
| `touvron2023llama2` | import + completion | article | yes | acquired |
| `reimers2019` | import + completion | paper-conference | yes | acquired |
| `openai2024embeddings` | import + completion | webpage | yes | acquired |
| `nussbaum2024nomic` | import + completion | article | no; retained preprint | acquired |
| `guo2017` | import + completion | paper-conference | yes | acquired |
| `kadavath2022` | import + completion | article | yes | acquired |
| `naeini2015` | import + completion | paper-conference | yes | acquired |
| `christophides2021` | import + completion | article-journal | yes | owner download attached |
| `mudgal2018` | import + completion | paper-conference | yes | acquired |
| `konda2016` | import + completion | article-journal | yes | acquired |
| `koutras2021valentine` | import + completion | paper-conference | yes | owner download attached |
| `deb2014` | import + completion | chapter | yes | owner fetch gap |
| `zitzler2003` | import + completion | article-journal | yes | owner download attached |
| `khattab2023dspy` | import + completion | article | no; retained preprint | acquired |
| `zhou2023ape` | import + completion | paper-conference | yes | owner fetch gap |
| `nist2020sp80053` | import + completion | report | yes | acquired |
| `fedramp2024` | import + completion | report | yes | acquired |
| `sequeda-2024-benchmarkUnderstand` | new publication | paper-conference | yes | owner download attached |
| `nussbaum-2025-nomicEmbed` | new publication | article-journal | yes | owner download attached |
| `khattab2024` | reuse + context | paper-conference | yes | acquired |
| `openai2023gpt4` | reuse + context | article | yes | existing PDF |
| `dod2020cmmc` | import + completion | report | yes | owner download attached |

All three unnamed links are visible in both directions: `sequeda2023` ↔ `sequeda-2024-benchmarkUnderstand`, `nussbaum2024nomic` ↔ `nussbaum-2025-nomicEmbed`, and `khattab2023dspy` ↔ `khattab2024`. They remain catalog-only. Retained preprint PDFs belong to the preprint records, not their publications.

## Sources found, fetched and remaining owner fetches

Eight approved local files were linked in place with empty loc; none moved. Fifteen verified PDFs and two single-file captures were moved into managed `unfiled` placement through `resource add --move`, using the CLI’s previewed names. The pre-existing GPT-4 PDF makes 26 attached resources across the 37 relevant records. All final file hashes match the approved local or acquired source bytes; all 17 scratch inputs were deleted only by verified CLI moves.

The Claude card is the March edition (PDF creation/modification metadata March 4, 2024). Attached preprint revisions are Llama 2 v2 (July 19, 2023), Kadavath v4 (November 21, 2022), Nomic v1 (February 2, 2024) and DSPy v1 (October 5, 2023); acquisition context pins them without changing the approved reference strings. The ICLR DSPy PDF is linked by the official proceedings and marked ICLR 2024, but its cover says “Self-Improving Pipelines” while the page and existing record say “State-of-the-Art Pipelines”. That difference is recorded in context; no unapproved metadata correction was made.

The embeddings JSON capture contains the full retrieved HTML response, URL, time and hash; remote assets and linked pages were not crawled. FedRAMP’s JSON capture contains the complete official Markdown/JSON sources at `2026-markdown` commit `2f81e380a6615d48927a72c5007df785c038f891` (289 files) and `rules` commit `58487bda77d76d9ce334304ec2e779ece7cc7d54` (11 files), plus commit metadata and archive hashes. Its changelog confirms content release `2026.09.22.01`; underlying rules data remains `2026.09.13.02`, consistent with the later content/build-only update. Both captures carry actual September 27 access dates. No browser automation was used.

At the initial gate, eleven records were missing their selected source; seven have since been filled below. Four gaps remain: Deb, both Bloor reports, and the unverified APE edition. Refusals were not bypassed. The 2007 Bloor homepage and Springer landing page were not attached as substitutes for the requested report/chapter.

| Key | Fetch result | Owner locator |
| --- | --- | --- |
| `bernsteinhaas2008` | ACM PDF refused, HTTP 403 | [Source](https://doi.org/10.1145/1378727.1378745) |
| `christophides2021` | ACM PDF refused, HTTP 403 | [Source](https://doi.org/10.1145/3418896) |
| `deb2014` | PDF URL redirects to HTML chapter landing page; no chapter PDF | [Source](https://doi.org/10.1007/978-1-4614-6940-7_15) |
| `dod2020cmmc` | DoD CIO refused, HTTP 403; need Model Overview v2.13 | [Source](https://dodcio.defense.gov/Portals/0/Documents/CMMC/ModelOverviewv2.pdf) |
| `howard2007bloor` | Exact 2007 primary report unresolved; homepage only | [Source](https://www.bloorresearch.com/) |
| `howard2011bloor` | Supplied report URL returns 404 | [Source](https://www.bloorresearch.com/research/data-migration-2011/) |
| `koutras2021valentine` | IEEE refused, HTTP 418 | [Source](https://ieeexplore.ieee.org/document/9458921) |
| `nussbaum-2025-nomicEmbed` | OpenReview PDF refused, HTTP 403 | [Source](https://openreview.net/pdf?id=IPmzyQSiQE) |
| `sequeda-2024-benchmarkUnderstand` | ACM PDF refused, HTTP 403; preprint is separately attached | [Source](https://doi.org/10.1145/3661304.3661901) |
| `zhou2023ape` | OpenReview PDF refused, HTTP 403 | [Source](https://openreview.net/pdf?id=YdqwNaCLCx) |
| `zitzler2003` | IEEE refused, HTTP 418 | [Source](https://doi.org/10.1109/TEVC.2003.810758) |

## Owner-download follow-up

Authorized by `comms/2026-09-27-190551-s1-dema-llm-owner-fetches.md` and `comms/2026-09-27-192440-s1-bloor-deb-gaps.md`. Seven owner downloads dated September 27 were verified against their selected publication identities and moved through `resource add --move` into managed unfiled placement. Each final file hash matches its input, each moved Downloads input is absent, and each record retains user-attributed provenance naming the original download and hash. The catalog now has 33 attached resources across these 37 records. All 37 approved bibliographic records and the three version links still pass the canonical comparison; no new access dates were added.

The supplied APE file `43_large_language_models_are_huma.pdf` remains untouched in Downloads: it lacks an ICLR 2023 header and has November 3, 2022 PDF dates. The earlier fetch locator `YdqwNaCLCx` appears to identify a 2022 workshop version. The official ICLR PDF at https://openreview.net/pdf?id=92gvk82DE- explicitly identifies ICLR 2023 in its indexed primary text, but direct download returns HTTP 403. A correct-edition download request is pending with s1; the earlier file was not attached as the publication.

Deb and both Bloor records now include import-attributed research notes supplied by the owner/session 1, preserving the owner’s availability statements. The notes distinguish the archived 2011 report listing, secondary statistics not verified against the report, the different September 2007 whitepaper, and the Oracle quotation. No metadata was changed. Deb and Bloor remain acknowledged gaps unless an author request succeeds.

The [owner-download evidence](2026-09-27-dema-llm-owner-downloads.json) retains original and final paths, identity checks, hashes, move results and appended context.

| Key | Managed filename | SHA-256 |
| --- | --- | --- |
| `bernsteinhaas2008` | `InformationIntegrationInTheEnterprise-2008.pdf` | `9e136e810b0a933619fd1152c94c15ec2ffa9bddb9f7ba6f8a57682b2613f151` |
| `christophides2021` | `AnOverviewOfEndToEndEntityResolutionForBigData-2021.pdf` | `dabe687fb9e0f0935572bb45c4954efb8cec69d5fc67b21d7706a9fa4eecf03a` |
| `sequeda-2024-benchmarkUnderstand` | `ABenchmarkToUnderstandTheRoleOfKnowledgeGraphsOnLargeLanguageModelSAccuracyForQuestionAnsweringOnEnterpriseSQLDatabases-2024.pdf` | `cff60b1f9da2950c511bdf6c74871e0d757ddfa8f2f064edf25e48d3c6a84866` |
| `nussbaum-2025-nomicEmbed` | `NomicEmbedTrainingAReproducibleLongContextTextEmbedder-2025.pdf` | `e7a2ec2906b7b48540e92945c771394017d00f6499a0a9ca1eb1dba50e3813fb` |
| `dod2020cmmc` | `CybersecurityMaturityModelCertificationCMMCModelOverview-v2.13-2024.pdf` | `3521adb262f431433bc0be3a3f7f717b0b05c61f1e5eb127c38c81d2979f4a00` |
| `zitzler2003` | `PerformanceAssessmentOfMultiobjectiveOptimizersAnAnalysisAndReview-2003.pdf` | `76d6f579eee9fe7bddffbab999c6541e0bdd12e402fa1ed37350e01210c0f046` |
| `koutras2021valentine` | `ValentineEvaluatingMatchingTechniquesForDatasetDiscovery-2021.pdf` | `3a7446976f18abecff45cb543c34ccc085f154cd0c38d93b51d03d9b40ef96fd` |

## Initial attachments with final names and hashes

All paths below were rehashed after intake. Linked resources retain their original filenames. Managed resources use the convention under `/Volumes/Casa/refs/lib/unfiled/`. The existing GPT-4 resource is included for completeness.

| Key | Mode | Final path | SHA-256 |
| --- | --- | --- | --- |
| `anthropic2024claude3` | move | `/Volumes/Casa/refs/lib/unfiled/TheClaude3ModelFamilyOpusSonnetHaiku-2024.pdf` | a96214e5d495dec76f6120891233aa97a73386b35b065a6709840b07588ed118 |
| `brown2020` | move | `/Volumes/Casa/refs/lib/unfiled/LanguageModelsAreFewShotLearners-2020.pdf` | 5fb1e3b8062688f5023ee63a9641d39c8c86922f2bca98535dcba084af7f719e |
| `fedramp2024` | move | `/Volumes/Casa/refs/lib/unfiled/FedRAMPConsolidatedRulesFor2026-v2026.09.22.01-2026-capture.json` | 817431e9bf2553c3739357bc197a79f426b54324b437c3f55a1f6241eb6b7443 |
| `guo2017` | move | `/Volumes/Casa/refs/lib/unfiled/OnCalibrationOfModernNeuralNetworks-2017.pdf` | df7c93f97204f8a3c2b10f6d5bf5265baac25f00c1ae3b473a3e1dbc102dacb2 |
| `kadavath2022` | move | `/Volumes/Casa/refs/lib/unfiled/LanguageModelsMostlyKnowWhatTheyKnow-2022.pdf` | 1d861f7732f65769703cb2731dc085f3c9e69771b1b6196d074646d1473c3fbf |
| `khattab2023dspy` | move | `/Volumes/Casa/refs/lib/unfiled/DSPyCompilingDeclarativeLanguageModelCallsIntoSelfImprovingPipelines-2023.pdf` | 5309836325c3a580b6c176242f49f21ca40e413b0acd514e74b67e16bb1b56bc |
| `khattab2024` | move | `/Volumes/Casa/refs/lib/unfiled/DSPyCompilingDeclarativeLanguageModelCallsIntoStateOfTheArtPipelines-2024.pdf` | 0592d139b3a40ba26c6669012339242b59d88ac1c2ed2bf8250429446b9d487b |
| `konda2016` | move | `/Volumes/Casa/refs/lib/unfiled/MagellanTowardBuildingEntityMatchingManagementSystems-2016.pdf` | c8cd4abd17917e60bcd3bb7b7b968f66b679590c501631cd68105afbf606c959 |
| `ledford2023dissertation` | link | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-dissertation.pdf` | 3a6bc4a2ca6d59e9f5d196ee445a2f36d496aa89c4c8dfe586684dc31dbc5911 |
| `ledford2023ieee` | link | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2023-ieee-digital-thread.pdf` | ee87f864331b17360d25722fa8ede347956eb3d7819c1252ec12775964841fe8 |
| `ledford2025syseng` | link | `/Volumes/Casa/dev/dema-llm/docs/research/references/ledford2025-syseng.pdf` | 6883aaebae8248d4936eeb08b1cf2abb5136ae677c0c64ada6aa7c6e0ae1b13d |
| `mudgal2018` | move | `/Volumes/Casa/refs/lib/unfiled/DeepLearningForEntityMatchingADesignSpaceExploration-2018.pdf` | 30c191e5326ccaeee2d6efd01aa36799c806e28e620e9ef74eb6e0bb8410f829 |
| `naeini2015` | move | `/Volumes/Casa/refs/lib/unfiled/ObtainingWellCalibratedProbabilitiesUsingBayesianBinning-2015.pdf` | c1688bddfa3c43d3755e2a43dd68d72c45544211734ee2ff369d78ce22d22acb |
| `nist2020sp80053` | move | `/Volumes/Casa/refs/lib/unfiled/SecurityAndPrivacyControlsForInformationSystemsAndOrganizations-2020.pdf` | fc63bcd61715d0181dd8e85998b1e6201ae3515fc6626102101cab1841e11ec6 |
| `nussbaum2024nomic` | move | `/Volumes/Casa/refs/lib/unfiled/NomicEmbedTrainingAReproducibleLongContextTextEmbedder-2024.pdf` | c82d1ba2fbb03747bc6665821edfd07895cd162dc06cecb067898f33d24380b3 |
| `oleary2025ai4se` | link | `/Volumes/Casa/pub/2025-ai4se-ai-enhanced-dema/AI4SE_AI_Enhanced_DEMA.pdf` | b2ea81187907cd0bed0f6bc4c6790acf001da2a93609e6117f41475cbecdf770 |
| `oleary2025binary-classification` | link | `/Volumes/Casa/pub/2025-informs-gradebot-poster/poster-oleary-informs25.pptx` | e9e3f5fb74e7235a51b8ab7459971a4d9a5a804a9336b30f78e06ee2df0ab35b |
| `olearyledford2026insight` | link | `/Volumes/Casa/pub/2026-insight-dema-llm/published/oleary-ledford-2026-insight-dema-llm-version-of-record.pdf` | 02567dceb4916267e82ef5f1b58bafcf340870c2215c38e037903090bc7d9af2 |
| `openai2023gpt4` | existing | `/Volumes/Casa/refs/lib/papers/aiml/GPT4TechnicalReport-2023.pdf` | 5269ab4bab5dd064a39ecab221f79e13bbe0901f0000f8dad3416cdb493df8b4 |
| `openai2024embeddings` | move | `/Volumes/Casa/refs/lib/unfiled/openai2024embeddings-capture.json` | 19dffcda4fb9341b53b391bddddd6c6bea810a4d28cac1137db746e624eaa3df |
| `oracle2011migration` | move | `/Volumes/Casa/refs/lib/unfiled/PutYourDataFirstOrYourMigrationWillComeLast-2012.pdf` | 80aab7a9b13085214b05050f0cbb5c4293841f19ef5ab42af2e6a7fc743e12b8 |
| `reimers2019` | move | `/Volumes/Casa/refs/lib/unfiled/SentenceBERTSentenceEmbeddingsUsingSiameseBERTNetworks-2019.pdf` | e2703128039850ba7e098bfc6c7d9f3f3e75e6318815c5dd90af71085b1d384e |
| `sequeda2023` | link | `/Volumes/Casa/dev/dema-llm/docs/research/references/sequeda2023-llm-text-to-sql.pdf` | 1a0cb23795bea7f11c64b7f700d9088d2d08b004f7117951030733c8b0ee45c6 |
| `sheetrit2024` | link | `/Volumes/Casa/dev/dema-llm/docs/research/references/sheetrit2024-rematch.pdf` | 5504fb5e12ce6c2ab6741850c9e46158e94f913519bf28e6395935823d4bd0dd |
| `touvron2023llama2` | move | `/Volumes/Casa/refs/lib/unfiled/Llama2OpenFoundationAndFineTunedChatModels-2023.pdf` | 1df284ce95f783002074bfe8f21d47c646b396ceb1736ea3ec0ea212fc070d91 |
| `wei2022` | move | `/Volumes/Casa/refs/lib/unfiled/ChainOfThoughtPromptingElicitsReasoningInLargeLanguageModels-2022.pdf` | 880df0b46e8b4f77248d92a639dca69b96e57cad626e6fad0b4f5d746b930bd5 |

## Gate preparation and findings

The register’s first consumer writes a helper only into `.refs-gate/` inside the harness copy; that helper refuses a directory containing `.git`. It replaces the four approved citation keys only in copied TDD/PDD `.qmd` files, points copied consumer settings at `../references.json`, switches copied PDD PDF settings from biblatex/backend/backref to citeproc, and applies exactly the approved event-place fallback to the copied CSL publisher macro. Its `scratch-transformations.json` records the touched files. The helper renders both book formats together; the third consumer renders both PDD formats together. The remaining consumers extract the resulting PDFs. Bibliography extraction uses HTML reference elements, Word Bibliography paragraphs, and numbered PDF entries ending before the following TDD callout. Footer detection preserves numeric-only URL continuation lines.

Two extraction checks caught and corrected a following-callout leak and a wrapped numeric URL line mistaken for a page footer. Fresh scratch reruns verified the corrected register; they did not change source metadata or publication content. Final gate artifacts and logs are under `/private/tmp/refs-dema-gate-03`; the earlier two runs are diagnostic only.

**Expected wording:** all 80 entries match. HTML/DOCX strings compare exactly after removing numeric labels; PDFs match after Unicode and punctuation/whitespace normalization, which accounts for line-break hyphens and ligatures. The only planned post-capture wording additions are `Accessed: Sep. 27, 2026` for embeddings and FedRAMP, with IEEE’s accompanying Online label. PDD PDF differences include the approved engine switch, source/author corrections, note removal and loss of backreferences. Its six exact before/after rows are in the gate appendix.

**Unpredicted TDD HTML numbering:** exported records are ordered by citation key, so the reference appendix changes all 34 numbers. For example, Sequeda changes `[1]` → `[29]` and ReMatch `[2]` → `[30]`. The PDF’s first-citation ordering and both PDD outputs keep their numbering. This presentation change was absent from the bibliography-only proposal previews; every affected row is flagged in the gate.

**Pre-existing HTML number mismatch:** all 43 in-text citation anchors reach an existing, correct source key, but their displayed number disagrees with the destination appendix number in both the original and candidate books. Example: the first Howard citation displays `[1]`; its original appendix entry is `[7]`, candidate `[9]`. The conversion does not introduce the mismatch, but the full gate exposes it. No fix or acceptance is implied. The owner should decide the HTML gate with this evidence; changing the publication’s numbering behavior is outside this execution.

## Commits, timing and verification

Execution work is isolated on `s2/dema-llm-execution`, based on `ded1eb8`; the register, this report and its evidence are the branch changes. The proposal worktree remains separate. Main’s untracked `worktrees/` is local workspace state, not a claim of a clean main tree. The publication remains clean at `7599aee`; no source, style, configuration, generated artifact, delivered PDD, `pre-pipyer` state or filename was changed there. Four accepted fixtures were subsequently recorded as described above; no export targeted the publication.

The run began after the 17:04 owner authorization. Verification covers the validated backup, 33 exact imported originals, 37 approved canonical records, 34 memberships, three symmetric links, 26 final file hashes and all four native artifact gates. Quarto 1.10.18, Pandoc 3.10, XeLaTeX/TeX Live 2026 and Poppler 26.09.0 were used. The original PDD is the existing biber artifact; its bibliography-only baseline extraction also remains in the prior proposal evidence. No product code changed, so verification uses the actual conversion rather than an unrelated full product suite.

## Findings for refs and the conversion guide

For refs: no new product feature is proposed by this pass. Preserve the separately approved deferred-regulation ledger note. A source’s publisher landing-page title can differ from its own PDF cover; keeping that evidence in context avoids silently rewriting an approved existing record.

For the guide: full book gates need a check that displayed citation numbers agree with their hyperlink destinations, as bibliography-only previews do not expose that mismatch. Record-order changes can renumber an HTML appendix independently of PDF first-citation order. PDF footer removal must not discard a numeric URL continuation, and bibliography extraction must stop before following callouts. The pre-adoption register helper must be retired when the live publication adopts the switches; its assertions deliberately expect legacy input settings.

**Next:** s1 coordinates publication adoption. Await the correct APE edition and publication-adoption result; do not merge this branch or edit the publication.
