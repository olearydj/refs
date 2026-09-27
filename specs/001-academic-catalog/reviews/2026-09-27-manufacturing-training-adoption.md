# Manufacturing training conversion — adoption, 2026-09-27

Owner acceptance: [portable identification notes gate](2026-09-27-portable-identification-notes-gate.md), after the approved [proposal](2026-09-27-manufacturing-training-proposal.md) and [intake](2026-09-27-manufacturing-training-execution.md). Adopted from refs main `3f789e4` (0.8.0). Both consumer fixtures are now recorded and a subsequent normal harness run passes.

## Backup and scope

Validated `/Volumes/Casa/refs-backups/2026-09-27-before-manufacturing-training-adoption`: manifest sizes/hashes, database integrity and identity, and resource inventory. Publication started at `4600260` with only the owner's untracked `x.md`; that note remains untouched. Only bibliography/configuration and source-workflow documentation changed. Manuscript body bytes are identical before and after. All original tracked files except the four authorized edits (`article.qmd`, `references.bib`, README and AGENTS) retain their starting hashes. The other additions are `references.json`, `.refs.toml` and `docs/refs.md`.

## Inventory and consumers

| Target | Profile | Consumer |
| --- | --- | --- |
| `references.json` | csl-json-v1 | Full Quarto HTML render of `article.qmd`, default Chicago author-date |
| `references.bib` | portable-bibtex-v1 | Full Elsevier PDF render with the submission profile, natbib/BibTeX and `elsarticle-num.bst`; retained LaTeX and the generated BibTeX remain source-bundle inputs |

Both targets contain the 39 cited records. Format-local bibliography settings replace the global header setting; no manuscript content changes. The generated BibTeX replaces the hand-kept file in place, so nothing is retired. Both targets are bound and their catalog baseline digests equal their on-disk bytes, with no pending export.

The original BibTeX SHA-256 remains `743853976ee3d25ee7e28b559cdde73567a6cf9f9c8b7690c32eea3e9d1ca3c8`, already imported during intake. The explicit `export --adopt --overwrite` succeeded for both configured targets without refusal. New SHA-256: JSON `cc3b55294e693ccefda7bee08a06f169e4883de7f0083f8ecc19ad67e10d592c`; BibTeX `749f8d8c3d7669fd92ee517c0ab2d5fe58d14c9b327a324b2d0147982609776e`.

## Import outcomes by key

No re-import. The intake report retains every initial and final key outcome: 41 entries, 39 citations, two uncited records. Kolla's historical unbound type conflict remains visible; adoption neither reconciles nor bypasses it.

## Record completions by key

No new completions. All catalog source, resource and project rows match the pre-adoption snapshot. The prior corrections, including the three news authors/outlets and the IISE ampersand, remain. The portable export reports five documented issued-precision projections, three webpage-to-misc fallbacks and two name-particle fallbacks; CSL JSON reports no warnings. No export refusal occurred.

## Sources found, fetched, and the fetch list for the owner

All 21 existing source-file hashes were verified again. Nothing was downloaded or moved during adoption. The following 20-item fetch list is handed forward unchanged from the intake report, including its access classifications and exact-edition cautions; links were not rechecked during this adoption pass. Two entries are uncited. Public-page captures and acquired PDFs still need attaching; no accessed date was advanced.

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

For Newell, obtain the cited 1981 chapter, not the 1982 technical report. For Anderson, a public manuscript is not asserted to be the final journal version. Owner-authorized downloads from gated publishers remain the owner's task. Attach source files without re-importing the bibliography.

## Attachments with final names and hashes

The [intake attachment table](2026-09-27-manufacturing-training-execution.md#attachments-with-final-names-and-hashes) supplies all 21 final paths and SHA-256 hashes; each still matches. Existing dissertation links remain, the four approved managed files stay under `unfiled`, and the IISE paper remains linked in place. No resource was relinked or renamed.

## Export gate table

The first post-adoption run matched the accepted gate entry for entry: HTML 39 identical, Elsevier 39 identical. It exited 1 only because manufacturing had no recorded fixtures yet. The owner-authorized `--record` run produced the same extractions, recorded both fixtures and the publication commit/tool versions, and likewise reported the pre-record missing-fixture status. The final normal run exits **0**, with **39 identical in each consumer**, no changed or missing entry. There is no new before/after wording to approve; the accepted review retains the prior eight changes.

| PDF entry | Citation key | HTML vs accepted gate | Elsevier vs accepted gate |
| --- | --- | --- | --- |
| 1 | `degiorgio2023adopting` | identical | identical |
| 2 | `wang2024frontier` | identical | identical |
| 3 | `fang2023hmd` | identical | identical |
| 4 | `tang2003compa` | identical | identical |
| 5 | `chu2020compa` | identical | identical |
| 6 | `vanneste2020cogni` | identical | identical |
| 7 | `funk2016interactive` | identical | identical |
| 8 | `yang2023industrial` | identical | identical |
| 9 | `caudell1992augmented` | identical | identical |
| 10 | `kaplan2021effec` | identical | identical |
| 11 | `kolla2021compa` | identical | identical |
| 12 | `gonzalez-franco2017immer` | identical | identical |
| 13 | `hoover2020measu` | identical | identical |
| 14 | `alves2022compa` | identical | identical |
| 15 | `buttner2020augme` | identical | identical |
| 16 | `wang2021role` | identical | identical |
| 17 | `marino2024assessing` | identical | identical |
| 18 | `moro2021virtu` | identical | identical |
| 19 | `chu2021experimental` | identical | identical |
| 20 | `degiorgio2022assessing` | identical | identical |
| 21 | `daling2023assemble` | identical | identical |
| 22 | `ariansyah2024learnability` | identical | identical |
| 23 | `havard2021case` | identical | identical |
| 24 | `anderson1982acqui` | identical | identical |
| 25 | `newell1981mecha` | identical | identical |
| 26 | `crossman1959theory` | identical | identical |
| 27 | `moyo2013devel` | identical | identical |
| 28 | `oleary2024augmented` | identical | identical |
| 29 | `auburn2025honda` | identical | identical |
| 30 | `auburn2022ge` | identical | identical |
| 31 | `auburn2024hartzell` | identical | identical |
| 32 | `amouzgar2025novel` | identical | identical |
| 33 | `oleary2025framework` | identical | identical |
| 34 | `azuma1994impro` | identical | identical |
| 35 | `marchand2016pose` | identical | identical |
| 36 | `nakajima1988intro` | identical | identical |
| 37 | `ngcorrales2020overa` | identical | identical |
| 38 | `conover1982analysis` | identical | identical |
| 39 | `sahoo2026laser` | identical | identical |

Scratch evidence: `/private/tmp/refs-manufacturing-adoption-check`, `/private/tmp/refs-manufacturing-adoption-record`, and `/private/tmp/refs-manufacturing-adoption-verified`, each with JSON/Markdown gate and consumer logs. The register now runs the committed configuration directly, with no scratch metadata rewrite. Fixture provenance names publication `62e7ca9`, refs `3f789e4`, the accepted review, artifact hashes and extraction hashes. Tools: Quarto 1.10.18, Pandoc 3.10, R 4.5.3, BibTeX 0.99e (TeX Live 2026), Poppler 26.09.0.

## Commits

- Publication `e7a8cad`: both generated targets, `.refs.toml`, format-local YAML routing; no content changes.
- Publication `62e7ca9`: `docs/refs.md`, README and agent-instruction links.
- This refs commit: both fixtures and register/provenance, guide register/findings, adoption report, and historical proposal/intake evidence carried from the unmerged conversion branch.

The four requested worktrees and branches (`csl-literal-text`, `portable-misc-notes`, `portable-note-capital`, `portable-identification-notes`) were each verified clean and merged into main, then removed. No other worktree was removed.

## Timing

The adoption pass used one backup, one two-target export and three full two-consumer harness passes (check, accepted recording, fixture verification). Harness tests: **19 passed** in 10.81 seconds with a writable TeX cache. No product code changed, so the full product suite was not repeated; the merged profile change's full run is recorded as 1,037 passing tests in the accepted gate review.

## Findings for refs

- Resolved in preceding approved commits: literal CSL text prevents IISE ampersand corruption; portable misc notes expose the news outlet to classic styles; leading-capital protection prevents Elsevier's lowercase outlet; identification-only notes eliminate duplicate dates/events. Both native and CSL consumers now preserve the accepted facts.
- The original Kolla import binding remains unbound after its guarded record correction. A future owner decision could define how to close that reviewed history without weakening identity checks; no force or repeated import was used.
- Multiple configured targets, explicit adoption and digest guards worked unchanged. No new product feature is required by this adoption.

## Findings for this guide

- Inspect the effective rendered style: the HTML consumer uses default Chicago despite the nearby extension stylesheet.
- Put different bibliography profiles in format-local metadata when Quarto would merge a global list, preventing both targets from reaching one consumer.
- Use the actual native BibTeX style for a production source bundle: Pandoc alone did not expose invisible misc fields or the note-capital rule.
- Distinguish generated replacement at the same path from retirement. Step 11 now names format-specific routing, and step 12 explicitly covers in-place adoption.
- Keep acquisition gaps and historical refusals visible at adoption; accepting a render does not mean every source file has been fetched. Preserve honest access dates.
