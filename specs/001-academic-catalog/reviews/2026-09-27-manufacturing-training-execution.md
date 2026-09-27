# Manufacturing training conversion — execution, 2026-09-27

**Stopped at the export gate; publication not adopted.** Owner approval: proposal `3a3718b`, with `oleary2025framework` revised to identical facts after literal-CSL fix `f6dd013`. Execution branch starts at refs `0abfff9` (0.8.0). Publication baseline is clean commit `46002603b9fecd8971f51f800c5f7a45d3c22d8a`, apart from owner-owned untracked `x.md`, which was excluded from scratch copies and left unchanged.

## Backup and scope

Backup: `/Volumes/Casa/refs-backups/2026-09-27-before-manufacturing-training-conversion`. `refs.recovery.validate_snapshot` passed: manifest member sizes/hashes, database integrity and identity, and resource inventory. Catalog revision at backup: 4142; external file contents are excluded by the backup format. The approved four moves independently verified their source hashes before intake and destination hashes afterward. No source file was deleted before the CLI's verified move.

Completed: one import, the project and 39 citations, approved record completions, 21 source attachments, scratch exports and full consumer renders. No download/capture, publication edit, export adoption, fixture recording, submission or public release occurred. The guide's step 10 says “a fact lost or altered, which stops the pass until the record or a refs limit explains it.” The three news outlets disappear under native BibTeX; that limit needs a separate resolution and a new gate before adoption.

## Inventory and consumers

The unchanged original `references.bib` has 41 entries (25 article, seven inproceedings, three misc, two phdthesis, two book, two incollection), 32 DOIs; SHA-256 `743853976ee3d25ee7e28b559cdde73567a6cf9f9c8b7690c32eea3e9d1ca3c8`. Recount on the clean publication confirms 39 cited keys; `fitts1967human` and `gay-bellile2015appli` remain uncited catalog records. Citation keys and manuscript prose are untouched.

| Consumer | Current/approved input | Actual pipeline and gate |
| --- | --- | --- |
| Quarto HTML | Legacy BibTeX → planned `references.json`, csl-json-v1 | Full `article.qmd` render; actual HTML style is Pandoc default Chicago author-date. The proposal's explicit Harvard probe was not the effective HTML configuration. Existing Chicago is preserved. References extracted by HTML `ref-KEY` divs into JSON for the harness. |
| Elsevier numbered PDF and LaTeX submission source | Legacy → generated `references.bib`, portable-bibtex-v1 | Full `quarto render article.qmd --to elsevier-pdf --profile submission`, natbib/BibTeX with the project's `elsarticle-num.bst`; PDF References extracted by printed number. Submission profile retains LaTeX. Default drafting PDF shares this engine/style. |

There is no bibliography-copy script or second hand-kept bibliography. Elsevier source production still needs the `.bib`, so it is to be adopted as generated, never retired. Both targets contain the same 39 cited records. The effective bibliography must be set per format inside `article.qmd`'s YAML header: a project-level HTML override appended JSON to the document-level BibTeX list rather than replacing it. The corrected scratch candidate removes the global header bibliography and specifies JSON under `html`, BibTeX under `elsevier-pdf`; manuscript prose remains byte-identical.

The pending entry in `tests/fixtures/real-trial/converted/register.json` stages that approved header-only routing inside the disposable copy, runs both consumers, and records actual tool versions. It is explicitly `pending-adoption`, with no accepted fixtures; a normal harness run therefore exits 1 for missing fixtures even though both renders succeed. That is intentional and must not be mistaken for an adopted project. Remove the staging preamble when the same configuration is committed in the publication. R packages are read from the publication's existing managed R 4.5 library; its obsolete local library symlinks, generated outputs, owner note, and `docs/sessions` symlink are excluded from copies. No R restoration or analysis changes were made.

## Import outcomes by key

Batch `88568e29-ad40-4e30-848f-62159423fa9a`, origin `manufacturing-training-media-tradeoffs`: **29 applied = 23 new + six safe fills; one unchanged; 11 conflicts; zero invalid**, total 41. Every initial conflict value exactly matched the approved proposal's field-by-field list. The import's exit 4 reports those conflicts, not a failed batch.

Ten bound conflicts were reconciled with a batch revision guard. Kolla's type mismatch makes its binding `bound:false`; `import reconcile` refused with `identity_conflict`. The all-entry preview made no reconciliation writes. A second preview/execution excluded Kolla and reconciled the ten bound entries. Kolla's separately approved correction was applied to the existing, DOI/key-identified source with `update --if-revision`; no identity was forced, no history edited, and no re-import was used to clear the refusal. Final import status: 39 applied, one unchanged, one unresolved historical Kolla conflict. Its catalog record is correctly `paper-conference` and exports once.

| Key | Initial outcome | Final handling |
| --- | --- | --- |
| `caudell1992augmented` | new | completed |
| `degiorgio2023adopting` | new | completed |
| `fang2023hmd` | new | completed |
| `oleary2024augmented` | new | completed |
| `oleary2025framework` | new | completed |
| `funk2016interactive` | new | completed |
| `daling2023assemble` | new | completed |
| `yang2023industrial` | new | completed |
| `kaplan2021effec` | conflict | reconciled, current values kept as approved |
| `buttner2020augme` | conflict | reconciled, current values kept as approved |
| `vanneste2020cogni` | unchanged | completed |
| `wang2021role` | safe fills | completed |
| `wang2024frontier` | new | completed |
| `marino2024assessing` | new | completed |
| `ariansyah2024learnability` | new | completed |
| `sahoo2026laser` | new | completed |
| `nakajima1988intro` | safe fills | completed |
| `ngcorrales2020overa` | conflict | reconciled, current values kept as approved |
| `moyo2013devel` | conflict | reconciled, current values kept as approved |
| `auburn2025honda` | new | completed |
| `auburn2022ge` | new | completed |
| `auburn2024hartzell` | new | completed |
| `crossman1959theory` | new | completed |
| `anderson1982acqui` | new | completed |
| `newell1981mecha` | new | completed |
| `fitts1967human` | new | completed |
| `conover1982analysis` | new | completed |
| `chu2021experimental` | new | completed |
| `amouzgar2025novel` | new | completed |
| `degiorgio2022assessing` | new | completed |
| `tang2003compa` | safe fills | completed |
| `chu2020compa` | conflict | reconciled, current values kept as approved |
| `hoover2020measu` | safe fills | completed |
| `kolla2021compa` | conflict | record corrected by guarded update; original batch conflict remains unbound |
| `alves2022compa` | conflict | reconciled, current values kept as approved |
| `gonzalez-franco2017immer` | safe fills | completed |
| `havard2021case` | conflict | reconciled, current values kept as approved |
| `moro2021virtu` | conflict | reconciled, current values kept as approved |
| `azuma1994impro` | conflict | reconciled, current values kept as approved |
| `marchand2016pose` | conflict | reconciled, current values kept as approved |
| `gay-bellile2015appli` | safe fills | completed |

## Record completions by key

- `oleary2024augmented`: thesis remains 2024; context identifies the attached corrected v1.1.1 PDF (June 28, 2026).
- `moyo2013devel`: retained recognized `Dissertation`, normalized ETD URL, kept publication year 2013; cleared department from publisher place and retained the department and conflicting December 10/14 dates in context.
- `kolla2021compa`: conference-paper type, CLF 2021 venue, SSRN publisher and incoming protection/native label applied by guarded update. Original batch refusal remains visible.
- `ngcorrales2020overa`: corrected issued date to the PDF's explicit 2020-09-17; source of correction in context.
- `azuma1994impro`: title now ends `Optical See-through HMD`; protected HMD; venue/event retained; correction source recorded.
- `auburn2022ge`, `auburn2024hartzell`, `auburn2025honda`: webpage, container-title `Auburn Engineering News`, Carla Nelson author, issued 2022-03-03, 2024-04-12 and 2025-05-27 respectively. Since the owner has not supplied captures, accessed remains 2026-07-27; the proposal's September 27 date was explicitly conditional on capture. No fictitious capture date was set. Their original `misc` native label was cleared when retyping, as required by native/canonical compatibility.
- `kaplan2021effec`: kept full catalog venue. Büttner, Chu, Moro and Marchand keep catalog punctuation and date precision; compatible title protections/fills retained. All remaining source facts follow the proposal. No software/version or kind assignment applies.

The native-news gate revealed that preserved `howpublished` is selected only when the original BibTeX entry type matches the current native label. A guarded attempt to restore the actual original `bibtex/misc` label on the first webpage (`auburn2022ge`) refused `invalid_patch`: “Native label contradicts the canonical type or uses an unknown namespace.” No record changed in that attempt; the other two were not retried. No synthetic note, false native type, manual `.bib` edit or serializer change was introduced. The correct outlet remains in all three catalog records, but `journal` on exported `@misc` does not print under `elsarticle-num.bst`. This is the adoption blocker.

## Sources found, fetched, and the fetch list for the owner

All 21 approved local source files are attached and hash-verified: 16 retained, four Downloads PDFs moved to managed `unfiled`, and the project-owned IISE paper linked in place with loc empty. Nothing was downloaded. The 20 entries below remain file-less; two are uncited. The exact edition cautions from the proposal still apply, especially the 1981 Newell chapter versus the 1982 technical report. Owner-supplied PDFs/captures should be attached after this report; do not re-import the bibliography.

One acquisition link per missing item follows. **OA** marks a publisher/repository open full text verified by the linked primary source; **public page** means capture the webpage, not an OA journal-license claim. **Access unverified** means no claim that it is closed or open: use the owner's library/VPN if needed and disclose any refusal. No browser automation, login or source download was used in this pass.

| Key | Access / needed source | Link |
| --- | --- | --- |
| `caudell1992augmented` | Public university-hosted paper; OA license unverified | [Acquire/capture](https://www.mona.uwi.edu/halls/sites/default/files/halls/00183317.pdf) |
| `degiorgio2023adopting` | OA, CC BY publisher copy at KTH | [Acquire/capture](https://kth.diva-portal.org/smash/get/diva2%3A1816503/FULLTEXT01.pdf) |
| `fang2023hmd` | Access unverified; exact cited edition | [Acquire/capture](https://doi.org/10.1016/j.rcim.2023.102567) |
| `daling2023assemble` | OA, publisher CC license | [Acquire/capture](https://www.sciencedirect.com/science/article/pii/S0003687023000595) |
| `wang2024frontier` | Access unverified; exact cited edition | [Acquire/capture](https://doi.org/10.1016/j.jmsy.2024.05.002) |
| `marino2024assessing` | OA, publisher CC license | [Acquire/capture](https://www.sciencedirect.com/science/article/pii/S0166361524000137) |
| `ariansyah2024learnability` | Open institutional full text; license not asserted | [Acquire/capture](https://dspace.lib.cranfield.ac.uk/bitstream/1826/21128/1/Augmented_reality_training-2023.pdf) |
| `sahoo2026laser` | Access unverified; exact cited edition | [Acquire/capture](https://doi.org/10.1016/j.apergo.2025.104662) |
| `nakajima1988intro` | Access unverified; 1988 book, ISBN 9780915299232 | [Acquire/capture](https://search.worldcat.org/search?q=bn%3A9780915299232) |
| `auburn2025honda` | Public page; capture needed | [Acquire/capture](https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing-training.html) |
| `auburn2022ge` | Public page; capture needed | [Acquire/capture](https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session) |
| `auburn2024hartzell` | Public page; capture needed | [Acquire/capture](https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices-through-tiger-motors-training.html) |
| `anderson1982acqui` | Access unverified; exact cited edition | [Acquire/capture](https://doi.org/10.1037/0033-295x.89.4.369) |
| `newell1981mecha` | Access unverified; obtain chapter, not 1982 report | [Acquire/capture](https://www.taylorfrancis.com/chapters/edit/10.4324/9780203728178-1/mechanisms-skill-acquisition-law-practice-allen-newell-paul-rosenbloom) |
| `fitts1967human` | Access unverified; 1967 Brooks/Cole book; uncited | [Acquire/capture](https://search.worldcat.org/search?q=ti%3AHuman+Performance+au%3AFitts+yr%3A1967) |
| `conover1982analysis` | Access unverified; exact cited edition | [Acquire/capture](https://doi.org/10.2307/2530051) |
| `chu2021experimental` | Access unverified; exact cited edition | [Acquire/capture](https://doi.org/10.1016/j.jmsy.2021.04.003) |
| `amouzgar2025novel` | OA, CC BY publisher copy at Uppsala | [Acquire/capture](https://uu.diva-portal.org/smash/get/diva2%3A1979089/FULLTEXT01.pdf) |
| `degiorgio2022assessing` | OA, CC BY publisher copy at Politecnico | [Acquire/capture](https://re.public.polimi.it/retrieve/e0c31c12-2f65-4599-e053-1705fe0aef77/Assessing%20the%20influence%20of%20expert%20video%20aid%20on%20assembly%20learning%20curves.pdf) |
| `gay-bellile2015appli` | Access unverified; exact cited edition; uncited | [Acquire/capture](https://doi.org/10.1201/b18703-22) |

For Anderson, a public CMU manuscript was discovered online but is not asserted to be the final journal version; the DOI above is the requested published work. For blocked publisher downloads, the owner supplies the authorized PDF. On execution, fetched papers and page captures move under `unfiled`; missing items remain file-less and disclosed, never attached to a citing paper as a substitute.

## Attachments with final names and hashes

| Key | Action / loc | Final path | Verified SHA-256 |
| --- | --- | --- | --- |
| `alves2022compa` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Alves et al. - 2022 - Comparing augmented reality visualization methods .pdf` | `d20ccab60e6b60ecc6164379c7170b07d71b3be50b4be7b79addf34b40853e2a` |
| `azuma1994impro` | retained; dissertation/mixed-reality | `/Volumes/Casa/refs/lib/dissertation/mixed-reality/Azuma and Bishop - 1994 - Improving Static and Dynamic Registration in an Op.pdf` | `32769ecd41d64922a3b59bd68c70e587fdad52c151e6e46da2791234441e5674` |
| `buttner2020augme` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Büttner et al. - 2020 - Augmented Reality Training for Industrial Assembly.pdf` | `80072351e5b855744b536094fce92f089dee872d861af55a1d748ec0bc290e4a` |
| `chu2020compa` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Chu et al. - 2020 - Comparing Augmented Reality-Assisted Assembly Func.pdf` | `edafb2d750f2226c0b95b214915b16911be22e8fd5db839aac71a746b03ca0db` |
| `crossman1959theory` | moved; unfiled | `/Volumes/Casa/refs/lib/unfiled/ATheoryOfTheAcquisitionOfSpeedSkill-1959-PDF.pdf` | `10cd13c9c52586ff6fd24cde5203727260810f6a6bae9eaf7dd722924d8f8ef9` |
| `funk2016interactive` | moved; unfiled | `/Volumes/Casa/refs/lib/unfiled/InteractiveWorkerAssistanceComparingTheEffectsOfInSituProjectionHeadMountedDisplaysTabletAndPaperInstructions-2016-PDF.pdf` | `8a85117c854302194763f291ac164f7100d28d2d2ce0890076daedf3533aba21` |
| `gonzalez-franco2017immer` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Gonzalez-Franco et al. - 2017 - Immersive Mixed Reality for Manufacturing Training.pdf` | `9e87ec5e9f97957138a055a95e83eedf48cfa1f1f1e698961a33c2f01d85adcc` |
| `havard2021case` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Havard et al. - 2021 - A use case study comparing augmented reality (AR) .pdf` | `4fa2c48d1532dde71d6ce19733266f2f2502eec4e601f2606646470a513783ae` |
| `hoover2020measu` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Hoover et al. - 2020 - Measuring the Performance Impact of Using the Micr.pdf` | `bcffaaff49c20c6d27f0b8dce13df8c8f68e7379d73778213d4575de264812f0` |
| `kaplan2021effec` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Kaplan et al. - 2021 - The Effects of Virtual Reality, Augmented Reality,.pdf` | `5001c12d8fbdb81585ce9dfde5dddae2daeceb936a9bcf7fa498ec0863805883` |
| `kolla2021compa` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Kolla et al. - 2021 - Comparing Effectiveness of Paper Based and Augment.pdf` | `5bc23af3451e0fbc7a9decfd470f65378a0e6e0e6c0f686ce8c710bc7dcce51a` |
| `marchand2016pose` | retained; dissertation/mixed-reality | `/Volumes/Casa/refs/lib/dissertation/mixed-reality/Marchand et al. - 2016 - Pose Estimation for Augmented Reality A Hands-On .pdf` | `aae67f78dbdf23b7ed60b823b16338cd613c3f69d615b12eca4e18f227ca229c` |
| `moro2021virtu` | retained; dissertation/ar-metrics-med | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-med/Moro et al. - 2021 - Virtual and Augmented Reality Enhancements to Medi.pdf` | `81c00084db784ca5d43e00cf78c880bf7b4a2d24c13906106bcd77f2c5754876` |
| `moyo2013devel` | retained; dissertation/misc | `/Volumes/Casa/refs/lib/dissertation/misc/Moyo - 2013 - Developing a Multidisciplinary Best Practice Manuf.pdf` | `6fa7d8a249dfe2c96d6bbb664ae3c09ef426023b2208b19fb1687b9383c1a088` |
| `ngcorrales2020overa` | retained; dissertation/misc | `/Volumes/Casa/refs/lib/dissertation/misc/Ng Corrales et al. - 2020 - Overall Equipment Effectiveness Systematic Litera.pdf` | `d74ac4c7cc685036bd8d07f9cdad9dc4ea2738bd3506c46c297f01aac3bf7de5` |
| `oleary2024augmented` | moved; unfiled | `/Volumes/Casa/refs/lib/unfiled/AugmentedVsTraditionalInstructionInManufacturingAssemblyAnAffordanceBasedMultiModalAssessmentOfLearningRecallAndRetention-2024-PDF.pdf` | `1063bd1b5e94a687eeca085a8c778b6827b73963bbcdbb492cae20eec616e06b` |
| `oleary2025framework` | linked; empty | `/Volumes/Casa/pub/manufacturing-training-media-tradeoffs/_output/submission/related-paper-iise-2025.pdf` | `9d43ade851b9d53bfaa90245d71973170218ea7d95ece7eacbb6c003e704d129` |
| `tang2003compa` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Tang et al. - 2003 - Comparative effectiveness of augmented reality in .pdf` | `489ad7808cbf0bacf403662d64de59b18e0079bffce2652d7392e7ffee08143a` |
| `vanneste2020cogni` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Vanneste et al. - 2020 - Cognitive support for assembly operations by means.pdf` | `6160785722c430de3529ebe4f310dcec424f8ffe12b0d7c4ae70bc4991d12870` |
| `wang2021role` | retained; dissertation/ar-metrics-manuf | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Wang et al. - 2021 - The role of user-centered AR instruction in improv.pdf` | `86cacf31905dbdfaff71c2a6b4d594447798e4e4a2dfa139fd8f88a391b394ca` |
| `yang2023industrial` | moved; unfiled | `/Volumes/Casa/refs/lib/unfiled/DoesAugmentedRealityHelpInIndustrialTrainingAComprehensiveEvaluationBasedOnNaturalHumanBehaviorAndKnowledgeRetention-2023-PDF.pdf` | `e6e64f182dd063f1dc059f868a89a0866eb1b806677a81e72ce21eb319e652a4` |

The IISE linked resource intentionally has no stored digest under link-in-place semantics; this pass independently hashed its bytes and matched the approved SHA-256. All four moved originals are absent only after their matching library destination verified. Existing 16 resource names/paths/digests are unchanged.

## Export gate table with exact before and after per changed entry

Both consumers render all **39** cited references, with zero missing. Fresh before/after renders use the same clean publication commit and R data. Tool versions: Quarto 1.10.18, bundled Pandoc 3.10, R 4.5.3, BibTeX 0.99e (TeX Live 2026), Poppler 26.09.0. Full tool output is recorded in the register. The first harness attempt had no fixtures, as expected for a first conversion; the comparison below uses freshly rendered legacy bibliography extractions, not invented accepted fixtures. The committed evidence JSON stores all 39 before/after outcomes per consumer; no `--record` ran.

| Consumer | Mechanical outcomes | Meaning / adoption decision |
| --- | --- | --- |
| HTML / CSL JSON | 25 identical, 14 changed, zero missing | No fact loss found. Approved author/type/date/title/venue changes, DOI case normalization, punctuation/casing and the IISE publisher's `and` restored from Pandoc's prior name-list split. Actual Chicago wording differs from the proposal's Harvard strings, so this is disclosed as a prediction correction rather than silently called byte-identical. |
| Elsevier / portable BibTeX | 25 identical, 14 changed, zero missing | **Blocked**: entries 29–31 lose the news outlet. Other changes are the disclosed corrections and retained event/date/URL notes, punctuation and DOI normalization. |

`oleary2025framework` now has **identical facts** in both consumers: the IISE `&` survives literally; the native reference is text-identical. HTML changes only `Institute of Industrial; Systems Engineers` to `Institute of Industrial and Systems Engineers`. The title and venue are correct. No `&Amp;` remains.

### html

| Key / printed entry | Before | After |
| --- | --- | --- |
| anderson1982acqui | Anderson, John R. 1982. “Acquisition of Cognitive Skill.” Psychological Review 89 (4): 369–406. https://doi.org/10.1037/0033-295X.89.4.369. | Anderson, John R. 1982. “Acquisition of Cognitive Skill.” Psychological Review 89 (4): 369–406. https://doi.org/10.1037/0033-295x.89.4.369. |
| auburn2022ge | Auburn University Samuel Ginn College of Engineering. 2022. Tiger Motors Lab Hosts GE Aviation Training Session. Auburn Engineering News. https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session. | Nelson, Carla. 2022. “Tiger Motors Lab Hosts GE Aviation Training Session.” Auburn Engineering News, March 3. https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session. |
| auburn2024hartzell | Auburn University Samuel Ginn College of Engineering. 2024. Hartzell Engine Tech Elevates Manufacturing Practices Through Tiger Motors Training. Auburn Engineering News. https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices-through-tiger-motors-training.html. | Nelson, Carla. 2024. “Hartzell Engine Tech Elevates Manufacturing Practices Through Tiger Motors Training.” Auburn Engineering News, April 12. https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices-through-tiger-motors-training.html. |
| auburn2025honda | Auburn University Samuel Ginn College of Engineering. 2025. Honda Returns to Auburn for Lean Manufacturing Training. Auburn Engineering News. https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing-training.html. | Nelson, Carla. 2025. “Honda Returns to Auburn for Lean Manufacturing Training.” Auburn Engineering News, May 27. https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing-training.html. |
| azuma1994impro | Azuma, Ronald T., and Gary Bishop. 1994. “Improving Static and Dynamic Registration in an Optical See-through HMD Proceedings of the 21st Annual Conference on Computer Graphics and Interactive Techniques.” SIGGRAPH ’94, 197–204. https://doi.org/10.1145/192161.192199. | Azuma, Ronald T., and Gary Bishop. 1994. “Improving Static and Dynamic Registration in an Optical See-Through HMD.” SIGGRAPH ’94, 197–204. https://doi.org/10.1145/192161.192199. |
| buttner2020augme | Büttner, Sebastian, Michael Prilla, and Carsten Röcker. 2020. “Augmented Reality Training for Industrial Assembly Work: Are Projection-Based AR Assistive Systems an Appropriate Tool for Assembly Training.” Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, 1–12. https://doi.org/10.1145/3313831.3376720. | Büttner, Sebastian, Michael Prilla, and Carsten Röcker. 2020. “Augmented Reality Training for Industrial Assembly Work - Are Projection-Based AR Assistive Systems an Appropriate Tool for Assembly Training.” Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, 1–12. https://doi.org/10.1145/3313831.3376720. |
| caudell1992augmented | Caudell, Thomas P., and David W. Mizell. 1992. “Augmented Reality: An Application of Heads-up Display Technology to Manual Manufacturing Processes.” Proceedings of the Twenty-Fifth Hawaii International Conference on System Sciences 2: 659–69. https://doi.org/10.1109/HICSS.1992.183317. | Caudell, Thomas P., and David W. Mizell. 1992. “Augmented Reality: An Application of Heads-up Display Technology to Manual Manufacturing Processes.” Proceedings of the Twenty-Fifth Hawaii International Conference on System Sciences 2: 659–69. https://doi.org/10.1109/hicss.1992.183317. |
| chu2021experimental | Chu, Chih-Hsing, and Ching-Hung Ko. 2021. “An Experimental Study on Augmented Reality Assisted Manual Assembly with Occluded Components.” Journal of Manufacturing Systems 61: 685–95. https://doi.org/10.1016/j.jmsy.2021.04.003. | Chu, Chih-Hsing, and Ching-Hung Ko. 2021. “An Experimental Study on Augmented Reality Assisted Manual Assembly With Occluded Components.” Journal of Manufacturing Systems 61: 685–95. https://doi.org/10.1016/j.jmsy.2021.04.003. |
| chu2020compa | Chu, Chih-Hsing, Chien-Jung Liao, and Shu-Chiang Lin. 2020. “Comparing Augmented Reality-Assisted Assembly Functions: A Case Study on Dougong Structure.” Applied Sciences 10 (10): 3383. https://doi.org/10.3390/app10103383. | Chu, Chih-Hsing, Chien-Jung Liao, and Shu-Chiang Lin. 2020. “Comparing Augmented Reality-Assisted Assembly Functions—a Case Study on Dougong Structure.” Applied Sciences 10 (10): 3383. https://doi.org/10.3390/app10103383. |
| kaplan2021effec | Kaplan, Alexandra D., Jessica Cruit, Mica Endsley, Suzanne M. Beers, Ben D. Sawyer, and P. A. Hancock. 2021. “The Effects of Virtual Reality, Augmented Reality, and Mixed Reality as Training Enhancement Methods: A Meta-Analysis.” Human Factors 63 (4): 706–26. https://doi.org/10.1177/0018720820904229. | Kaplan, Alexandra D., Jessica Cruit, Mica Endsley, Suzanne M. Beers, Ben D. Sawyer, and P. A. Hancock. 2021. “The Effects of Virtual Reality, Augmented Reality, and Mixed Reality as Training Enhancement Methods: A Meta-Analysis.” Human Factors: The Journal of the Human Factors and Ergonomics Society 63 (4): 706–26. https://doi.org/10.1177/0018720820904229. |
| marchand2016pose | Marchand, Eric, Hideaki Uchiyama, and Fabien Spindler. 2016. “Pose Estimation for Augmented Reality: A Hands-On Survey.” IEEE Transactions on Visualization and Computer Graphics 22 (12): 2633–51. https://doi.org/10.1109/TVCG.2015.2513408. | Marchand, Eric, Hideaki Uchiyama, and Fabien Spindler. 2016. “Pose Estimation for Augmented Reality: A Hands-on Survey.” IEEE Transactions on Visualization and Computer Graphics 22 (12): 2633–51. https://doi.org/10.1109/tvcg.2015.2513408. |
| moro2021virtu | Moro, Christian, James Birt, Zane Stromberga, et al. 2021. “Virtual and Augmented Reality Enhancements to Medical and Science Student Physiology and Anatomy Test Performance: A Systematic Review and Meta-Analysis.” Anatomical Sciences Education 14 (3): 368–76. https://doi.org/10.1002/ase.2049. | Moro, Christian, James Birt, Zane Stromberga, et al. 2021. “Virtual and Augmented Reality Enhancements to Medical and Science Student Physiology and Anatomy Test Performance: A Systematic Review and Meta‐Analysis.” Anatomical Sciences Education 14 (3): 368–76. https://doi.org/10.1002/ase.2049. |
| moyo2013devel | Moyo, Yamkelani. 2013. “Developing a Multidisciplinary Best Practice Manufacturing Education and Research Laboratory for 21st Century Competitiveness.” Doctoral dissertation, Auburn University. https://etd.auburn.edu/handle/10415/3972. | Moyo, Yamkelani. 2013. “Developing a Multidisciplinary Best Practice Manufacturing Education and Research Laboratory for 21st Century Competitiveness.” Dissertation, Auburn University. https://etd.auburn.edu/handle/10415/3972. |
| oleary2025framework | O’Leary, Danny J. 2025. “Evaluating the Effectiveness of AR/MR Technologies in Manufacturing Training: A Multi-Modal Assessment Framework.” In Proceedings of the IISE Annual Conference & Expo 2025, edited by E. Gentry, F. Ju, and X. Liu. Institute of Industrial; Systems Engineers. | O’Leary, Danny J. 2025. “Evaluating the Effectiveness of AR/MR Technologies in Manufacturing Training: A Multi-Modal Assessment Framework.” In Proceedings of the IISE Annual Conference & Expo 2025, edited by E. Gentry, F. Ju, and X. Liu. Institute of Industrial and Systems Engineers. |
### elsevier

| Key / printed entry | Before | After |
| --- | --- | --- |
| 4 | [4] A. Tang, C. Owen, F. Biocca, W. Mou, Comparative effectiveness of augmented reality in object assembly, in: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03, ACM Press, 2003, pp. 73–80. doi:10.1145/642611.642626. | [4] A. Tang, C. Owen, F. Biocca, W. Mou, Comparative effectiveness of augmented reality in object assembly, in: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03, ACM Press, 2003, pp. 73–80, event: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03. doi:10.1145/642611.642626. |
| 5 | [5] C.-H. Chu, C.-J. Liao, S.-C. Lin, Comparing Augmented Reality-Assisted Assembly Functions: A Case Study on Dougong Structure, Applied Sciences 10 (10) (2020) 3383. doi:10.3390/app10103383. | [5] C.-H. Chu, C.-J. Liao, S.-C. Lin, Comparing Augmented Reality-Assisted Assembly Functions—a case study on Dougong Structure, Applied Sciences 10 (10) (2020) 3383. doi:10.3390/app10103383. |
| 9 | [9] T. P. Caudell, D. W. Mizell, Augmented reality: An application of heads-up display technology to manual manufacturing processes, in: Proceedings of the Twenty-Fifth Hawaii International Conference on System Sciences, Vol. 2, IEEE, 1992, pp. 659–669. doi:10.1109/HICSS.1992.183317. | [9] T. P. Caudell, D. W. Mizell, Augmented reality: An application of heads-up display technology to manual manufacturing processes, in: Proceedings of the Twenty-Fifth Hawaii International Conference on System Sciences, Vol. 2, IEEE, 1992, pp. 659–669. doi:10.1109/hicss.1992.183317. |
| 10 | [10] A. D. Kaplan, J. Cruit, M. Endsley, S. M. Beers, B. D. Sawyer, P. A. Hancock, The effects of virtual reality, augmented reality, and mixed reality as training enhancement methods: A meta-analysis, Human Factors 63 (4) (2021) 706–726. doi:10.1177/0018720820904229. | [10] A. D. Kaplan, J. Cruit, M. Endsley, S. M. Beers, B. D. Sawyer, P. A. Hancock, The effects of virtual reality, augmented reality, and mixed reality as training enhancement methods: A meta-analysis, Human Factors: The Journal of the Human Factors and Ergonomics Society 63 (4) (2021) 706–726. doi:10.1177/0018720820904229. |
| 15 | [15] S. Büttner, M. Prilla, C. Röcker, Augmented reality training for industrial assembly work: Are projection-based AR assistive systems an appropriate tool for assembly training, in: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, ACM, 2020, pp. 1–12. doi: 10.1145/3313831.3376720. | [15] S. Büttner, M. Prilla, C. Röcker, Augmented reality training for industrial assembly work - are projection- based AR assistive systems an appropriate tool for assembly training, in: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, ACM, 2020, pp. 1–12, event: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems. doi:10.1145/3313831.3376720. |
| 18 | [18] C. Moro, J. Birt, Z. Stromberga, C. Phelps, J. Clark, P. Glasziou, A. M. Scott, Virtual and Augmented Reality Enhancements to Medical and Science Student Physiology and Anatomy Test Performance: A Systematic Review and Meta-Analysis, Anatomical Sciences Education 14 (3) (2021) 368–376. doi:10.1002/ase.2049. | [18] C. Moro, J. Birt, Z. Stromberga, C. Phelps, J. Clark, P. Glasziou, A. M. Scott, Virtual and Augmented Reality Enhancements to Medical and Science Student Physiology and Anatomy Test Performance: A Systematic Review and Meta‐Analysis, Anatomical Sciences Education 14 (3) (2021) 368–376. doi:10.1002/ase.2049. |
| 24 | [24] J. R. Anderson, Acquisition of cognitive skill, Psychological Review 89 (4) (1982) 369–406. doi: 10.1037/0033-295X.89.4.369. | [24] J. R. Anderson, Acquisition of cognitive skill, Psychological Review 89 (4) (1982) 369–406. doi: 10.1037/0033-295x.89.4.369. |
| 27 | [27] Y. Moyo, Developing a multidisciplinary best practice manufacturing education and research laboratory for 21st century competitiveness, Doctoral dissertation, Auburn University (2013). URL https://etd.auburn.edu/handle/10415/3972 | [27] Y. Moyo, Developing a multidisciplinary best practice manufacturing education and research laboratory for 21st century competitiveness, Dissertation, Auburn University (2013). URL https://etd.auburn.edu/handle/10415/3972 |
| 29 | [29] Auburn University Samuel Ginn College of Engineering, Honda returns to Auburn for lean manufacturing training, Auburn Engineering News (May 2025). URL https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing- training.html | [29] C. Nelson, Honda returns to Auburn for lean manufacturing training, issued: 2025-05-27 (May 2025). URL https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing- training.html |
| 30 | [30] Auburn University Samuel Ginn College of Engineering, Tiger Motors lab hosts GE Aviation training session, Auburn Engineering News (Mar. 2022). URL https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session | [30] C. Nelson, Tiger Motors lab hosts GE Aviation training session, issued: 2022-03-03 (Mar. 2022). URL https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session |
| 31 | [31] Auburn University Samuel Ginn College of Engineering, Hartzell Engine Tech elevates manufacturing practices through Tiger Motors training, Auburn Engineering News (Apr. 2024). URL https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices- through-tiger-motors-training.html | [31] C. Nelson, Hartzell Engine Tech elevates manufacturing practices through Tiger Motors training, issued: 2024-04-12 (Apr. 2024). URL https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices- through-tiger-motors-training.html |
| 34 | [34] R. T. Azuma, G. Bishop, Improving Static and Dynamic Registration in an Optical See-through HMD Proceedings of the 21st Annual Conference on Computer Graphics and Interactive Techniques, in: SIGGRAPH ’94, Association for Computing Machinery, 1994, pp. 197–204. doi:10.1145/192161.192 199. | [34] R. T. Azuma, G. Bishop, Improving static and dynamic registration in an optical see-through HMD, in: SIGGRAPH ’94, Association for Computing Machinery, 1994, pp. 197–204, event: SIGGRAPH ’94. doi:10.1145/192161.192199. |
| 35 | [35] E. Marchand, H. Uchiyama, F. Spindler, Pose Estimation for Augmented Reality: A Hands-On Survey, IEEE Transactions on Visualization and Computer Graphics 22 (12) (2016) 2633–2651. doi: 10.1109/TVCG.2015.2513408. | [35] E. Marchand, H. Uchiyama, F. Spindler, Pose Estimation for Augmented Reality: A hands-on survey, IEEE Transactions on Visualization and Computer Graphics 22 (12) (2016) 2633–2651, issued: 2016-12-01. doi:10.1109/tvcg.2015.2513408. |
| 37 | [37] L. d. C. Ng Corrales, M. P. Lambán, M. E. Hernandez Korner, J. Royo, Overall equipment effectiveness: Systematic literature review and overview of different approaches, Applied Sciences 10 (18) (2020) 6469. doi:10.3390/app10186469. | [37] L. d. C. Ng Corrales, M. P. Lambán, M. E. Hernandez Korner, J. Royo, Overall equipment effectiveness: Systematic literature review and overview of different approaches, Applied Sciences 10 (18) (2020) 6469, issued: 2020-09-17. doi:10.3390/app10186469. URL https://www.mdpi.com/2076-3417/10/18/6469 |

## Commits

This refs branch carries the approved proposal with its revised IISE prediction, the pending register entry, this execution report, and complete fresh-gate evidence. **No publication commit exists:** adoption, generated targets, `.refs.toml`, the YAML switch and project workflow documentation remain unexecuted because the native gate loses facts. `references.bib` remains the unchanged publication input and is not retired. No manuscript-content commit was made. No accepted fixture was created or changed.

## Timing

Approximately 12 minutes from backup validation through intake, full baseline/candidate renders and report preparation. The import and citation/reconciliation commands completed in seconds; full renders and investigation of the native consumer occupied most of the pass. Harness tests: **19 passed**. No product code changed, so the unrelated full product suite was not rerun.

## Findings

- The literal-CSL fix resolves the proposal's IISE ampersand defect. No further CSL workaround is needed.
- The proposal over-inferred HTML style from an extension file; a full render shows Chicago. Inspect effective format metadata, not merely nearby stylesheets, before predicting exact wording.
- Quarto merged the proposed project-level bibliography list with document metadata. Format-local document metadata in the scratch copy reliably isolates the two consumers; no prose changes are required.
- A canonical webpage cannot retain the incompatible `misc` native label, but the portable export then omits preserved `howpublished`. Its `journal` field does not satisfy the actual native style. A separately approved projection decision must retain the real news outlet in a slot that this consumer prints; this pass implements no product change. That candidate prevents the observed loss of three source outlets.
- Reconciliation cannot accept a type-conflict entry whose import binding is false even after the approved catalog correction. The refusal remains visible; it was not cleared by force or repeat import. A future decision may clarify how such reviewed corrections close import history.
- Captures remain an owner fetch task; accessed dates must not imply captures that never occurred.

Verification: every one of the 95 inventoried tracked/source publication files, including `x.md`, retains its starting hash; publication status remains only `?? x.md`. All 669 pre-existing catalog records outside the 41-key scope are unchanged. A concurrent session added unrelated keys `mr-0624` and `so39`; this pass neither created nor changed them. The approved 23 additions account for this conversion's catalog growth. All 21 attached-file hashes verified. No R analysis, derived data or manuscript prose was changed.

**Resume boundary:** resolve the three missing native news outlets, then rerun both registered consumers and compare against this fresh baseline. Present the corrected gate and actual Chicago wording to the owner before adoption. On acceptance, record fixtures, adopt both generated targets (the exact legacy bytes are already imported), commit bibliography routing/configuration separately from prose, add the project source-workflow documentation, and update the pending register entry. Do not repeat import, citation creation, file moves or record completions.
