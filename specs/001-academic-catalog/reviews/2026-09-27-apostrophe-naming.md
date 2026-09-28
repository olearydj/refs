# Apostrophes in generated title names — 2026-09-27

## Change and verification

One shared `title_tokens` rule now serves generated citation keys and conventional intake filenames. Straight U+0027, typographic U+2019 and modifier U+02BC apostrophes between letters disappear while joining the letters: `Developer's` becomes `Developers`, `Model’s` becomes `Models`, and `OʼReilly` becomes `OReilly`. Leading/trailing apostrophes and other punctuation remain separators. U+02BC needs explicit treatment because Unicode classifies it as a letter. Creator normalization, title case, title protection, existing assigned keys and existing resource paths are unchanged.

The two contract paragraphs now state that rule. Fixed unit expectations cover all three forms for possessives, a name, surrounding quotation marks, a space beside an apostrophe and ASCII and Unicode numeric boundaries; separate counterexamples cover hyphen, dot, slash, underscore and space. Targeted naming tests: 43 passed. Three additional CLI regressions verify each apostrophe form remains in the stored title/title-short and context, survives all three exported title profiles, and stays unchanged after export while the derived key joins the letters. Full suite with `TEXMFVAR` and `TEXMFCACHE` at `/private/tmp/refs-csl-tex-cache`: **1,152 passed in 43.52 seconds**. Ruff, `ty check src/refs` and whitespace checks pass. Full log: `/private/tmp/refs-apostrophe-naming/pytest-scope.log`.

## Export impact

No existing export bytes change. `bibliography.serialize` reads stored `citation_key`, and `serialize_csl` uses it as `id`; neither generates names. This patch changes only the tokenization called by new-key allocation and conventional file intake. No canonical metadata, assigned keys, file locators, creator code or export projection changes. New records can of course receive the newly correct keys. The conditional all-project conversion walk is therefore not triggered, and no fixtures were recorded.

## Read-only catalog audit

Compared baseline `072cdd5` against this patch across **760 sources and 762 registered resources**, including removed sources. No unusable-key candidate was skipped. The catalog was opened with SQLite `mode=ro`; its byte hash before and after is `17df94f940200bd5b437a8e8c6c0486e71e2b5c0344443a0d5461b99175a21d7`. Catalog revision: 4840. No keys, resource metadata or files were edited.

The [complete machine-readable audit](2026-09-27-apostrophe-naming-audit.json) includes source/resource IDs, current full paths, states, project citations and collision observations. These are counterfactual names generated from **current** canonical metadata, not a reconstruction of metadata at original intake and not a rename plan. Generated keys use saved naming settings where available; other keys use the current owner settings. Key candidates are unsuffixed; a later authorized rename would still need collision handling. No candidate key exists. Three proposed basenames resolve to the current file on this case-insensitive filesystem (Larson, Sequeda publication and Wilson); these are case-only spelling changes, not collisions with another file. No proposed path resolves to a different existing file.

### Four key candidates

Assigned legacy keys are shown separately from their old-rule generated forms. Every assigned key remains unchanged. In particular, `wilson-2024-developerS` is not cited by any project; neither is the Larson record.

| Assigned key | Old-rule generated form | New-rule generated form | Key origin | Cited projects |
| --- | --- | --- | --- | --- |
| `burt2014motor` | `burt-2014-motorcycleInnovator` | `burt-2014-motorcycleInnovators` | supplied | zotero-library |
| `larson-2024-engineeringExecutive` | `larson-2024-engineeringExecutive` | `larson-2024-engineeringExecutives` | generated | None |
| `sarkar2023shado` | `sarkar-2023-shadowsDon` | `sarkar-2023-shadowsDont` | supplied | zotero-library |
| `wilson-2024-developerS` | `wilson-2024-developerS` | `wilson-2024-developersPlaybook` | generated | None |

### Fourteen filename candidates

Thirteen resources are managed and one is linked in place. Only three current basenames exactly match the old convention (Larson, Sequeda publication and Wilson). The others have preserved imported/manual names or predate later metadata changes. For example, the CanvasAPI filename lacks the version now present in the record, so a full present-day convention would also add that version; that is not an apostrophe-only rename recommendation. Old Zotero attachment labels can themselves be long filenames, so current convention candidates include those unchanged labels. The full paths below identify the actual files; old/new conventional basenames isolate the rule comparison while all other inputs stay fixed.

| Assigned key | Mode and current full path | Old-rule conventional basename | New-rule conventional basename |
| --- | --- | --- | --- |
| `bix2020wider` | managed: `/Volumes/Casa/refs/lib/iise2025/engineering-econ/Bix - 2020 - The Wider Context of Samuelson’s MIT Textbook—Depr.pdf` | `TheWiderContextOfSamuelsonSMITTextbookDepressionEraDiscussionsAboutTheValueOfEconomicsEducationForAmericanEngineers-2020-Bix-2020-TheWiderContextofSamuelsonsMITTextbookDepr.pdf.pdf` | `TheWiderContextOfSamuelsonsMITTextbookDepressionEraDiscussionsAboutTheValueOfEconomicsEducationForAmericanEngineers-2020-Bix-2020-TheWiderContextofSamuelsonsMITTextbookDepr.pdf.pdf` |
| `bix2020wider` | managed: `/Volumes/Casa/refs/lib/iise2025/engineering-econ/The-Wider-Context-of-Samuelson-s-MIT-Textbook.html` | `TheWiderContextOfSamuelsonSMITTextbookDepressionEraDiscussionsAboutTheValueOfEconomicsEducationForAmericanEngineers-2020-Snapshot.html` | `TheWiderContextOfSamuelsonsMITTextbookDepressionEraDiscussionsAboutTheValueOfEconomicsEducationForAmericanEngineers-2020-Snapshot.html` |
| `burt2014motor` | managed: `/Volumes/Casa/refs/lib/web/pd/the-motorcycle-innovators-dilemma.html` | `TheMotorcycleInnovatorSDilemma-2014-Snapshot.html` | `TheMotorcycleInnovatorsDilemma-2014-Snapshot.html` |
| `burt2014motor` | managed: `/Volumes/Casa/refs/lib/web/pd/Burt - 2014 - The ‘Motorcycle’ Innovator’s Dilemma.pdf` | `TheMotorcycleInnovatorSDilemma-2014-Burt-2014-TheMotorcycleInnovatorsDilemma.pdf.pdf` | `TheMotorcycleInnovatorsDilemma-2014-Burt-2014-TheMotorcycleInnovatorsDilemma.pdf.pdf` |
| `larson-2024-engineeringExecutive` | managed: `/Volumes/Casa/refs/lib/unfiled/TheEngineeringExecutiveSPrimer-2024.pdf` | `TheEngineeringExecutiveSPrimer-2024.pdf` | `TheEngineeringExecutivesPrimer-2024.pdf` |
| `rico2023gener` | managed: `/Volumes/Casa/refs/lib/web/Rico - 2023 - Generative Models Aren't Databases.pdf` | `GenerativeModelsArenTDatabases-2023-Rico-2023-GenerativeModelsArentDatabases.pdf.pdf` | `GenerativeModelsArentDatabases-2023-Rico-2023-GenerativeModelsArentDatabases.pdf.pdf` |
| `rico2023gener` | managed: `/Volumes/Casa/refs/lib/web/generative-models-arent-databases.html` | `GenerativeModelsArenTDatabases-2023-Snapshot.html` | `GenerativeModelsArentDatabases-2023-Snapshot.html` |
| `sarkar2023shado` | managed: `/Volumes/Casa/refs/lib/papers/aiml/2311-c.html` | `ShadowsDonTLieAndLinesCanTBendGenerativeModelsDonTKnowProjectiveGeometryForNow-2023-arXiv.orgSnapshot.html` | `ShadowsDontLieAndLinesCantBendGenerativeModelsDontKnowProjectiveGeometryForNow-2023-arXiv.orgSnapshot.html` |
| `sarkar2023shado` | managed: `/Volumes/Casa/refs/lib/papers/aiml/Sarkar et al. - 2023 - Shadows Don't Lie and Lines Can't Bend! Generative.pdf` | `ShadowsDonTLieAndLinesCanTBendGenerativeModelsDonTKnowProjectiveGeometryForNow-2023-Sarkaretal.-2023-ShadowsDontLieandLinesCantBendGenerative.pdf.pdf` | `ShadowsDontLieAndLinesCantBendGenerativeModelsDontKnowProjectiveGeometryForNow-2023-Sarkaretal.-2023-ShadowsDontLieandLinesCantBendGenerative.pdf.pdf` |
| `sequeda-2024-benchmarkUnderstand` | managed: `/Volumes/Casa/refs/lib/unfiled/ABenchmarkToUnderstandTheRoleOfKnowledgeGraphsOnLargeLanguageModelSAccuracyForQuestionAnsweringOnEnterpriseSQLDatabases-2024.pdf` | `ABenchmarkToUnderstandTheRoleOfKnowledgeGraphsOnLargeLanguageModelSAccuracyForQuestionAnsweringOnEnterpriseSQLDatabases-2024.pdf` | `ABenchmarkToUnderstandTheRoleOfKnowledgeGraphsOnLargeLanguageModelsAccuracyForQuestionAnsweringOnEnterpriseSQLDatabases-2024.pdf` |
| `sequeda2023` | linked: `/Volumes/Casa/dev/dema-llm/docs/research/references/sequeda2023-llm-text-to-sql.pdf` | `ABenchmarkToUnderstandTheRoleOfKnowledgeGraphsOnLargeLanguageModelSAccuracyForQuestionAnsweringOnEnterpriseSQLDatabases-2023.pdf` | `ABenchmarkToUnderstandTheRoleOfKnowledgeGraphsOnLargeLanguageModelsAccuracyForQuestionAnsweringOnEnterpriseSQLDatabases-2023.pdf` |
| `skarbez2021revis` | managed: `/Volumes/Casa/refs/lib/papers/xr/Skarbez et al. - 2021 - Revisiting Milgram and Kishino's Reality-Virtualit.pdf` | `RevisitingMilgramAndKishinoSRealityVirtualityContinuum-2021-Skarbezetal.-2021-RevisitingMilgramandKishinosReality-Virtualit.pdf.pdf` | `RevisitingMilgramAndKishinosRealityVirtualityContinuum-2021-Skarbezetal.-2021-RevisitingMilgramandKishinosReality-Virtualit.pdf.pdf` |
| `ucfopen2026canvasapi` | managed: `/Volumes/Casa/refs/lib/unfiled/CanvasAPIPythonAPIWrapperForInstructureSCanvasLMS-2026-capture.json` | `CanvasAPIPythonAPIWrapperForInstructureSCanvasLMS-v3.6.0-2026-capture.json` | `CanvasAPIPythonAPIWrapperForInstructuresCanvasLMS-v3.6.0-2026-capture.json` |
| `wilson-2024-developerS` | managed: `/Volumes/Casa/refs/lib/unfiled/TheDeveloperSPlaybookForLargeLanguageModelSecurity-2024.pdf` | `TheDeveloperSPlaybookForLargeLanguageModelSecurity-2024.pdf` | `TheDevelopersPlaybookForLargeLanguageModelSecurity-2024.pdf` |

## Delivery

Branch `s2/apostrophe-naming`, based on main `072cdd5`; the change is limited to shared title tokenization, fixed behavior tests, two contract sentences and this read-only audit. No creator-key policy change, catalog migration, rekey or file rename is included. Merge and any later owner-selected renames remain separate decisions.
