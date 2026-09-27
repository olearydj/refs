# Manufacturing training conversion — proposal, 2026-09-27

**Proposal only; not approved or executed.** Prepared from refs 0.8.0, main `63d6850`, on `codex/manufacturing-proposal`. The publication is `/Volumes/Casa/pub/manufacturing-training-media-tradeoffs`, HEAD `35ae519c2ab94e5a5c750c1935957d5884598580` with another session's staged and unstaged changes. Its current working files, not an older commit or the September 7 handoff, are the inventory authority. No catalog or publication writes, imports, backups, source downloads, moves, captures or full manuscript renders occurred. Scratch-only adapter assessments, bibliography exports and citation-engine probes support the predictions below.

There are **41 entries, 32 DOIs, 39 cited keys and two uncited keys**. Catalog prediction: **23 new, one unchanged, six existing records with non-conflicting fills, eleven value conflicts**. Sources: **21 found (16 already attached), 20 not found as the cited source**, including three URL-only news pages. A concrete CSL gate blocker is already visible: the IISE venue's ampersand becomes literal `&Amp;`. Execution requires owner approval, a clean publication tree, and resolution or an explicit new decision on that blocker.

**Approved execution addendum, 2026-09-27:** Owner approved this proposal at `3a3718b`. With the literal-CSL fix `f6dd013` merged, the gate prediction for `oleary2025framework` is **identical facts** in both consumers: the ampersand is literal and the publisher name retains its intended identity. The original failed probe below remains historical evidence. See [execution report](2026-09-27-manufacturing-training-execution.md) for the actual gates and the separate native-news-outlet blocker.

## Backup and scope

Proposed execution backup: `/Volumes/Casa/refs-backups/2026-09-27-before-manufacturing-training-conversion` (use the actual execution date if later). Validate manifest members and SQLite integrity before mutation. Nothing has been backed up or imported in this proposal phase.

Scope after approval: import the untouched bibliography once with origin `manufacturing-training-media-tradeoffs`; create that refs project; preserve all assigned keys; cite the 39 currently used keys; keep the other two catalog records uncited. Recheck citations after the other session commits its work. Complete only the record corrections below, attach verified sources, export each consumer to scratch, and compare fresh before/after renders from the same clean publication commit. Never alter prose, R analysis, frozen data, figures or the other session's edits. Bibliography metadata/configuration changes belong in a separate conversion commit. No submission or public release is proposed.

Dirty status observed (preserve all of it):

```text
 M README.md
 M REVIEW.md
 M _quarto.yml
 M article.qmd
 M data/README.md
 M submission/README.md
 M submission/author-and-release-decisions.md
 M submission/collaborator-review-invitation.md
 M submission/cover-letter.md
 M submission/prior-publication-comparison.md
D  supplement.qmd
?? x.md
```

`references.bib` SHA-256: `743853976ee3d25ee7e28b559cdde73567a6cf9f9c8b7690c32eea3e9d1ca3c8`. The latest `.ho/2026-09-07-001.md` describes an older two-document packet; current README/config fold the supplement into article appendices. Do not resurrect `supplement.qmd` or treat the old collaborator ZIP as a bibliography consumer requiring conversion.

## Inventory and consumers

Types: 25 `@article`, seven `@inproceedings`, three `@misc`, two `@phdthesis`, two `@book`, two `@incollection`. Keys use lowercase surname/organization + four-digit year + title mnemonic, with hyphenated surnames retained; the newer entries use longer mnemonics than the dissertation's truncated keys. All eighteen identity matches have exactly the incoming key, so no key alias, rekey or manuscript citation replacement is needed. DOI comparison is normalized, and title comparison ignores punctuation/spacing/diacritics for candidate discovery; title alone does not authorize binding. A fuzzy-title check found no additional credible catalog identity.

Citation counting removed executable fenced code blocks and parsed prose with Pandoc's citation extension, then cross-checked literal citation tokens against the 41 known keys. Raw QMD parsed as ordinary Markdown incorrectly absorbs prose into executable-block syntax, so that count was discarded. Quarto figure/table/section cross-references are excluded. `fitts1967human` and `gay-bellile2015appli` are the only uncited entries; all other rows below are cited. The earlier report of four uncited entries is stale.

| Consumer or artifact | Current reader and input | Proposed route |
| --- | --- | --- |
| Draft HTML, `_output/article.html` | `article.qmd`, `references.bib`, Pandoc citeproc; Elsevier extension supplies bundled `elsevier-harvard.csl` | `references.json`, `csl-json-v1`, same HTML style |
| Draft Elsevier PDF, `_output/article.pdf` | Elsevier extension 0.4.5 sets `cite-method: natbib`; `journal.cite-style: number` selects `elsarticle-num.bst`; LaTeX/BibTeX reads `references.bib` | Generated `references.bib`, `portable-bibtex-v1`; retain natbib and numbered style |
| Submission profile, `_output/submission/article.pdf` and preserved LaTeX | `_quarto-submission.yml` changes output directory and `keep-tex`; same natbib bibliography pipeline, not a separate manually maintained bibliography | Same generated BibTeX target included directly in the editable source archive with `.tex`, `.bst`, `.cls` and figures; rebuild outside the Quarto environment as a submission check |
| Existing `article.tex`, generated `.bbl`, HTML/PDF and old review ZIPs | Derived outputs; `article.tex` explicitly uses `natbib`, `elsarticle-num`, and `\bibliography{references.bib}` | Regenerate, do not edit as sources; archived review copies remain historical |
| `scripts/clean-manuscript-root.sh` | Deletes generated `.bbl` and other byproducts after drafting renders | No bibliography projection/copy to retire; R scripts prepare analysis, not references |

The requested CSL target cannot directly replace the PDF's natbib input. **Recommended interpretation for approval:** CSL JSON owns Quarto's citeproc HTML consumer; the existing numbered Quarto PDF and Elsevier source production retain classic BibTeX. Make HTML's bibliography a format-specific override, leaving PDF's bibliography on the generated `.bib`, and inspect effective Quarto metadata during execution. If “CSL JSON for the Quarto build” means changing the drafting PDF too, amend this proposal first: that needs a separately chosen numeric CSL style and a citation-engine change. Simply switching to citeproc would make the extension choose Harvard author-date, contrary to the current numbered PDF. No such style change is presumed here.

Elsevier needs an editable LaTeX source package, not only a rendered PDF for production. The project's saved September 7 JMS guide capture and `submission/jms-requirements-2026-09-07.md` say source files are requested at submission or revision and PDF is not a source format. Current [Elsevier LaTeX instructions](https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions) likewise specify a source archive including BibTeX and dependencies, even where an initial review PDF is accepted; they also require a flat upload layout. Its [Editorial Manager instructions](https://www.elsevier.support/publishing/answer/how-to-submit-a-latex-file-in-editorial-manager) describe the `.bib`/BibTeX route. A fresh direct fetch of the JMS guide returned HTTP 403; this is disclosed, not treated as a changed journal rule. Choose **portable-bibtex-v1**, because the actual production recipe is BibTeX + natbib + `.bst`, not Pandoc's BibLaTeX reader or biber. `biblatex-v1` is therefore not appropriate for this source bundle.

## Import outcomes by key

Predictions below use the actual refs BibTeX adapter and import binding assessment with `dry_run=True` over a SQLite `mode=ro` connection. No CLI invocation opened the live mutation log. Counts are not fabricated to fit three categories: refs reports six existing records as `applied` because safe fields/protection would fill; they are neither new sources nor wholly unchanged records. Conflicts can also carry compatible fills. All 41 entries parse; no admission refusal or identity collision was observed.

| Key | Cited | Canonical type planned | Predicted import | Existing match / file status |
| --- | --- | --- | --- | --- |
| `caudell1992augmented` | yes | paper-conference | new | none; not found |
| `degiorgio2023adopting` | yes | article-journal | new | none; not found |
| `fang2023hmd` | yes | article-journal | new | none; not found |
| `oleary2024augmented` | yes | thesis | new | none; found |
| `oleary2025framework` | yes | paper-conference | new | none; found |
| `funk2016interactive` | yes | paper-conference | new | none; found |
| `daling2023assemble` | yes | article-journal | new | none; not found |
| `yang2023industrial` | yes | article-journal | new | none; found |
| `kaplan2021effec` | yes | article-journal | conflict | key/DOI/title; attached |
| `buttner2020augme` | yes | paper-conference | conflict | key/DOI/title; attached |
| `vanneste2020cogni` | yes | article-journal | unchanged | key/DOI/title; attached |
| `wang2021role` | yes | article-journal | existing; fills (CLI applied) | key/DOI/title; attached |
| `wang2024frontier` | yes | article-journal | new | none; not found |
| `marino2024assessing` | yes | article-journal | new | none; not found |
| `ariansyah2024learnability` | yes | article-journal | new | none; not found |
| `sahoo2026laser` | yes | article-journal | new | none; not found |
| `nakajima1988intro` | yes | book | existing; fills (CLI applied) | key/title; not found |
| `ngcorrales2020overa` | yes | article-journal | conflict | key/DOI/title; attached |
| `moyo2013devel` | yes | thesis | conflict | key/title; attached |
| `auburn2025honda` | yes | webpage | new | none; URL-only |
| `auburn2022ge` | yes | webpage | new | none; URL-only |
| `auburn2024hartzell` | yes | webpage | new | none; URL-only |
| `crossman1959theory` | yes | article-journal | new | none; found |
| `anderson1982acqui` | yes | article-journal | new | none; not found |
| `newell1981mecha` | yes | chapter | new | none; not found |
| `fitts1967human` | **no** | book | new | none; not found |
| `conover1982analysis` | yes | article-journal | new | none; not found |
| `chu2021experimental` | yes | article-journal | new | none; not found |
| `amouzgar2025novel` | yes | article-journal | new | none; not found |
| `degiorgio2022assessing` | yes | article-journal | new | none; not found |
| `tang2003compa` | yes | paper-conference | existing; fills (CLI applied) | key/DOI/title; attached |
| `chu2020compa` | yes | article-journal | conflict | key/DOI/title; attached |
| `hoover2020measu` | yes | article-journal | existing; fills (CLI applied) | key/DOI/title; attached |
| `kolla2021compa` | yes | paper-conference | conflict | key/DOI/title; attached |
| `alves2022compa` | yes | article-journal | conflict | key/DOI/title; attached |
| `gonzalez-franco2017immer` | yes | article-journal | existing; fills (CLI applied) | key/DOI/title; attached |
| `havard2021case` | yes | article-journal | conflict | key/DOI/title; attached |
| `moro2021virtu` | yes | article-journal | conflict | key/DOI/title; attached |
| `azuma1994impro` | yes | paper-conference | conflict | key/DOI/title; attached |
| `marchand2016pose` | yes | article-journal | conflict | key/DOI/title; attached |
| `gay-bellile2015appli` | **no** | chapter | existing; fills (CLI applied) | key/title; not found |

### Conflicts, field by field

Values are **current catalog → incoming bibliography**, before any proposed completion. Preserve both originals; use explicit reconciliation/guarded updates, not blind replacement of the dissertation records. Fields not listed as conflicts remain unchanged or receive only the separately listed fills.

| Key | Field | Current → incoming | Proposed decision |
| --- | --- | --- | --- |
| `kaplan2021effec` | `metadata.container-title` | "Human Factors: The Journal of the Human Factors and Ergonomics Society" → "Human Factors" | Keep current; same fact with fuller naming or punctuation/precision. |
| `kaplan2021effec` | `metadata.page` | "706-726" → "706–726" | Keep current; same fact with fuller naming or punctuation/precision. |
| `buttner2020augme` | `metadata.title` | "Augmented Reality Training for Industrial Assembly Work - Are Projection-Based AR Assistive Systems an Appropriate Tool for Assembly Training" → "Augmented Reality Training for Industrial Assembly Work: Are Projection-Based AR Assistive Systems an Appropriate Tool for Assembly Training" | Keep current; same fact with fuller naming or punctuation/precision. |
| `ngcorrales2020overa` | `metadata.issued.date-parts` | [[2020, 1]] → [[2020]] | Neither date: published 2020-09-17 on the source PDF; correct with provenance. |
| `moyo2013devel` | `metadata.issued.date-parts` | [[2013, 12, 10]] → [[2013]] | Use 2013 only; preserve repository date 2013-12-10 and cover date 2013-12-14 in context, not as an invented publication day. |
| `moyo2013devel` | `metadata.genre` | "Dissertation" → "Doctoral dissertation" | Keep Dissertation; source is explicitly a PhD dissertation. |
| `moyo2013devel` | `metadata.URL` | "https://etd.auburn.edu//handle/10415/3972" → "https://etd.auburn.edu/handle/10415/3972" | Use incoming normalized handle URL. |
| `chu2020compa` | `metadata.title` | "Comparing Augmented Reality-Assisted Assembly Functions—a Case Study on Dougong Structure" → "Comparing Augmented Reality-Assisted Assembly Functions: A Case Study on Dougong Structure" | Keep current; same fact with fuller naming or punctuation/precision. |
| `kolla2021compa` | `metadata.type` | "article-journal" → "paper-conference" | Use conference identity from the paper header; keep authors/key; accept matching proceedings venue/publisher/protection and BibTeX native label. |
| `kolla2021compa` | `metadata.container-title` | "SSRN Electronic Journal" → "Proceedings of the 11th Conference on Learning Factories (CLF 2021)" | Use conference identity from the paper header; keep authors/key; accept matching proceedings venue/publisher/protection and BibTeX native label. |
| `kolla2021compa` | `metadata.publisher` | null → "SSRN" | Use conference identity from the paper header; keep authors/key; accept matching proceedings venue/publisher/protection and BibTeX native label. |
| `kolla2021compa` | `title_protection.title.protected_terms` | [] → ["Effectiveness", "Paper Based", "Augmented Reality Instructions", "Manual Assembly", "Training Tasks"] | Use conference identity from the paper header; keep authors/key; accept matching proceedings venue/publisher/protection and BibTeX native label. |
| `kolla2021compa` | `title_protection.container-title.protected_terms` | [] → ["CLF"] | Use conference identity from the paper header; keep authors/key; accept matching proceedings venue/publisher/protection and BibTeX native label. |
| `kolla2021compa` | `native_type.namespace` | "zotero" → "bibtex" | Use conference identity from the paper header; keep authors/key; accept matching proceedings venue/publisher/protection and BibTeX native label. |
| `kolla2021compa` | `native_type.value` | "journalArticle" → "inproceedings" | Use conference identity from the paper header; keep authors/key; accept matching proceedings venue/publisher/protection and BibTeX native label. |
| `alves2022compa` | `metadata.page` | "235-248" → "235–248" | Keep current; same fact with fuller naming or punctuation/precision. |
| `havard2021case` | `metadata.page` | "999-1014" → "999–1014" | Keep current; same fact with fuller naming or punctuation/precision. |
| `moro2021virtu` | `metadata.page` | "368-376" → "368–376" | Keep current; same fact with fuller naming or punctuation/precision. |
| `moro2021virtu` | `metadata.title` | "Virtual and Augmented Reality Enhancements to Medical and Science Student Physiology and Anatomy Test Performance: A Systematic Review and Meta‐Analysis" → "Virtual and Augmented Reality Enhancements to Medical and Science Student Physiology and Anatomy Test Performance: A Systematic Review and Meta-Analysis" | Keep current; same fact with fuller naming or punctuation/precision. |
| `azuma1994impro` | `metadata.title` | "Improving Static and Dynamic Registration in an Optical See-Through HMD Proceedings of the 21st Annual Conference on Computer Graphics and Interactive Techniques" → "Improving Static and Dynamic Registration in an Optical See-through HMD Proceedings of the 21st Annual Conference on Computer Graphics and Interactive Techniques" | Neither malformed title: correct to the source title ending “Optical See-through HMD”. |
| `marchand2016pose` | `metadata.issued.date-parts` | [[2016, 12, 1]] → [[2016, 12]] | Keep current; same fact with fuller naming or punctuation/precision. |
| `marchand2016pose` | `metadata.page` | "2633-2651" → "2633–2651" | Keep current; same fact with fuller naming or punctuation/precision. |
| `marchand2016pose` | `metadata.title` | "Pose Estimation for Augmented Reality: A Hands-on Survey" → "Pose Estimation for Augmented Reality: A Hands-On Survey" | Keep current; same fact with fuller naming or punctuation/precision. |

### Safe fills on existing records

- `buttner2020augme`: `metadata.container-title`, `metadata.page`, `title_protection.title.protected_terms`, `title_protection.container-title.protected_terms`, `title_protection.container-title.preserve_case`.
- `wang2021role`: `title_protection.title.protected_terms`.
- `nakajima1988intro`: `title_protection.title.protected_terms`.
- `tang2003compa`: `metadata.container-title`, `metadata.page`, `title_protection.container-title.protected_terms`, `title_protection.container-title.preserve_case`.
- `chu2020compa`: `title_protection.title.protected_terms`.
- `hoover2020measu`: `title_protection.title.protected_terms`.
- `gonzalez-franco2017immer`: `title_protection.title.protected_terms`.
- `havard2021case`: `title_protection.title.protected_terms`.
- `moro2021virtu`: `title_protection.title.protected_terms`.
- `azuma1994impro`: `metadata.container-title`, `title_protection.title.protected_terms`, `title_protection.container-title.protected_terms`, `title_protection.container-title.preserve_case`.
- `marchand2016pose`: `title_protection.title.protected_terms`, `title_protection.container-title.protected_terms`.
- `gay-bellile2015appli`: `metadata.DOI`, `metadata.page`, `title_protection.title.protected_terms`, `title_protection.container-title.protected_terms`.

No catalog source is merged by title alone. In particular, `gay-bellile2015appli` binds by its existing key and title even though its catalog record lacks the incoming DOI; DOI and pages are safe fills. The 1982 Newell report discussed below is not a basis for binding a 1981 chapter to another work.

## Record completions by key

Default for every row: use the canonical type shown above, retain authors/identifiers/editions and all existing title protection, add only the safe fills, and retain non-citation abstract/context/provenance. No software package or repository is cited as a source: version lookup does not apply to these 41 records, even though the manuscript discusses software and apparatus. No current registry kind applies: a proceedings **paper** is `paper-conference`, not the `proceedings` kind for a whole book; thesis/chapter/webpage have no applicable kind here.

Specific proposed completions:

- `oleary2024augmented`: thesis, genre Doctoral dissertation, Auburn University, 2024. Attach the explicitly labeled corrected `v1.1.1` PDF as a versioned resource; keep the ETD handle as identifier and explain the corrected file in context, not a false 2026 thesis date.
- `moyo2013devel`: thesis; keep recognized genre `Dissertation`, normalize the ETD URL, use publication year 2013, and move `publisher-place = Industrial and Systems Engineering` into context as department, then clear that non-place value. The PDF explicitly states Doctor of Philosophy and has a December 14 cover date; catalog December 10 is retained as prior repository metadata in context. A scratch experiment changing genre to `Doctoral dissertation` while retaining Zotero native label `thesis` caused portable `@misc` fallback and loss of printed institution/degree. That experiment was rejected; keeping the existing accurate genre yields `@phdthesis` without inventing a native label or changing product code.
- `kolla2021compa`: retype the catalog journal article as `paper-conference`, with the incoming CLF 2021 proceedings venue and SSRN publisher. The linked PDF says “11th Conference on Learning Factories, CLF2021”; retain its DOI, authors and key. This is the substantive catalog conflict, not an automatic DOI-merge decision.
- `ngcorrales2020overa`: correct catalog January 2020 to the PDF's explicit publication date, 2020-09-17. Retain the existing publisher URL and put the source of the date correction in context.
- `azuma1994impro`: correct title to `Improving Static and Dynamic Registration in an Optical See-through HMD`; the source PDF proves that the appended proceedings phrase belongs outside the title. Keep `SIGGRAPH '94` as the venue and protect `HMD`. The redundant stored event title remains a fact; portable output prints it in note, disclosed below.
- `auburn2025honda`, `auburn2022ge`, `auburn2024hartzell`: retype `@misc`/document as webpage; set container-title `Auburn Engineering News`. The primary pages identify **Carla Nelson** as author, rather than the current corporate-author string; propose that explicit correction for all three while retaining keys. Issued dates are respectively **2025-05-27**, **2022-03-03**, **2024-04-12**. Each page is linked in the fetch table. Retain the old 2026-07-27 access date in context and set accessed to the actual later capture date. The preview uses 2026-09-27; a later execution date will change that displayed value predictably. Preserve the news outlet from `howpublished` as a real bibliographic fact; it is not a research note to discard.
- `kaplan2021effec`: retain the fuller catalog journal name, `Human Factors: The Journal of the Human Factors and Ergonomics Society`. Page-range dash differences in this and other conflicts represent the same endpoints.
- `buttner2020augme`, `chu2020compa`, `moro2021virtu`, `marchand2016pose`: retain catalog title punctuation/casing and more precise issued values as assessed; preserve incoming protected terms that actually occur in the retained title. Do not reinterpret case/dash differences as lost facts. These choices and existing event metadata can change wording, as listed below.
- `newell1981mecha`: retain chapter type, year 1981, editor Anderson, publisher and cited pages 1–55 pending the actual chapter. Do not attach the 1982 technical report as if it were the cited edition. Verify chapter pagination when fetched; any correction outside this prediction is a finding for the owner.
- `fitts1967human`, `gay-bellile2015appli`: import/retain but do not cite in this project. Fetching their missing source files is still listed, explicitly lower priority than the 39 cited works.

Protection is data, not a style workaround. Keep the parsed protection below and the catalog's existing terms; do not protect every title wholesale merely to force a preferred casing. Source titles with `AR`, `VR`, `XR`, `AR/MR`, `HMD`, `Microsoft HoloLens`, `TPM`, `Industry 4.0`, `Industry 5.0`, `CHI`, `CLF`, `SIGGRAPH`, `IEEE` and `IISE` require those names to survive casing. No source has a `note` field to move wholesale. Add only factual context for source/version matching, date ambiguity, department, capture provenance and reconciliation decisions; never attach the project's review notes.

| Key | Existing imported protection to retain (title; container where present) |
| --- | --- |
| `oleary2025framework` | title: AR/MR |
| `daling2023assemble` | title: AR, VR |
| `buttner2020augme` | title: AR; container-title: CHI |
| `wang2021role` | title: AR |
| `wang2024frontier` | title: Industry 5.0, XR |
| `marino2024assessing` | title: Industry 4.0 |
| `nakajima1988intro` | title: TPM |
| `auburn2025honda` | title: Honda, Auburn |
| `auburn2022ge` | title: Tiger Motors, GE Aviation |
| `auburn2024hartzell` | title: Hartzell Engine Tech, Tiger Motors |
| `amouzgar2025novel` | title: XR, Industry |
| `tang2003compa` | container-title: Human, CHI |
| `chu2020compa` | title: Augmented Reality-Assisted Assembly Functions, A Case Study, Dougong Structure |
| `hoover2020measu` | title: Performance Impact, Using, Microsoft HoloLens, Provide Guided Assembly Work Instructions |
| `kolla2021compa` | title: Effectiveness, Paper Based, Augmented Reality Instructions, Manual Assembly, Training Tasks; container-title: CLF |
| `gonzalez-franco2017immer` | title: Mixed Reality, Manufacturing Training |
| `havard2021case` | title: AR |
| `moro2021virtu` | title: Augmented Reality Enhancements, Medical, Science Student Physiology, Anatomy Test Performance, A Systematic Review, Meta, Analysis |
| `azuma1994impro` | title: Static, Dynamic Registration, Optical See-through HMD Proceedings, Annual Conference, Computer Graphics, Interactive Techniques; container-title: SIGGRAPH |
| `marchand2016pose` | title: Estimation, Augmented Reality, A Hands-On Survey |
| `gay-bellile2015appli` | title: Augmented Reality, Automotive Industry; container-title: Wearable Computers, Augmented Reality |

## Sources found, fetched, and the fetch list for the owner

Search order: project and figures; `/Volumes/Casa/refs/lib` including dissertation folders; DEVONthink exports under `~/Downloads/_from2020mbp`; remaining `~/Downloads`. The file inventory contains 37,880 paths; 4,341 PDFs outside excluded code/cache directories were searched by filename and first-three-page text, with DOI and normalized-title matching. Non-PDF saved text, HTML, Markdown and web-location files were also searched for the nine no-DOI titles/URLs. Existing linked PDFs were verified against their catalog digests. DOI/title mentions inside dissertations, IRB appendices, this paper, bibliographies and literature-review notes were excluded as secondary mentions. “Not found” means no verified source in that bounded search; it does not assert absence inside unindexed ZIPs or image-only PDFs, and OCR was not run.

The project figures are study artifacts, not copies of the cited papers. Its own IISE prior-publication PDF is a real source. DEVONthink contains Moyo duplicates, but the library copy is already attached. No saved primary Auburn news page was found; the hits are this project's review/manuscript outputs. Nothing was fetched or captured.

### Verified files and planned placement

Existing attachments stay where they are, with their names and loc unchanged. The four new matching Downloads PDFs below may move into the library under `unfiled` through `resource add --move` after approval; the project's IISE comparison PDF stays in place and is linked with empty loc because it is project-owned material. No final renamed basename is invented before the CLI preview. Verify source and destination SHA-256 during execution.

| Key | State / planned action | Existing absolute path | SHA-256 |
| --- | --- | --- | --- |
| `oleary2024augmented` | Move to unfiled after approval | `/Users/djo/Downloads/dissertation.pdf` | `1063bd1b5e94a687eeca085a8c778b6827b73963bbcdbb492cae20eec616e06b` |
| `oleary2025framework` | Link in place, loc empty | `/Volumes/Casa/pub/manufacturing-training-media-tradeoffs/_output/submission/related-paper-iise-2025.pdf` | `9d43ade851b9d53bfaa90245d71973170218ea7d95ece7eacbb6c003e704d129` |
| `funk2016interactive` | Move to unfiled after approval | `/Users/djo/Downloads/2971648.2971706.pdf` | `8a85117c854302194763f291ac164f7100d28d2d2ce0890076daedf3533aba21` |
| `yang2023industrial` | Move to unfiled after approval | `/Users/djo/Downloads/1-s2.0-S0169814123001087-main.pdf` | `e6e64f182dd063f1dc059f868a89a0866eb1b806677a81e72ce21eb319e652a4` |
| `kaplan2021effec` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Kaplan et al. - 2021 - The Effects of Virtual Reality, Augmented Reality,.pdf` | `5001c12d8fbdb81585ce9dfde5dddae2daeceb936a9bcf7fa498ec0863805883` |
| `buttner2020augme` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Büttner et al. - 2020 - Augmented Reality Training for Industrial Assembly.pdf` | `80072351e5b855744b536094fce92f089dee872d861af55a1d748ec0bc290e4a` |
| `vanneste2020cogni` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Vanneste et al. - 2020 - Cognitive support for assembly operations by means.pdf` | `6160785722c430de3529ebe4f310dcec424f8ffe12b0d7c4ae70bc4991d12870` |
| `wang2021role` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Wang et al. - 2021 - The role of user-centered AR instruction in improv.pdf` | `86cacf31905dbdfaff71c2a6b4d594447798e4e4a2dfa139fd8f88a391b394ca` |
| `ngcorrales2020overa` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/misc/Ng Corrales et al. - 2020 - Overall Equipment Effectiveness Systematic Litera.pdf` | `d74ac4c7cc685036bd8d07f9cdad9dc4ea2738bd3506c46c297f01aac3bf7de5` |
| `moyo2013devel` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/misc/Moyo - 2013 - Developing a Multidisciplinary Best Practice Manuf.pdf` | `6fa7d8a249dfe2c96d6bbb664ae3c09ef426023b2208b19fb1687b9383c1a088` |
| `crossman1959theory` | Move to unfiled after approval | `/Users/djo/Downloads/A THEORY OF THE ACQUISITION OF SPEED-SKILL .pdf` | `10cd13c9c52586ff6fd24cde5203727260810f6a6bae9eaf7dd722924d8f8ef9` |
| `tang2003compa` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Tang et al. - 2003 - Comparative effectiveness of augmented reality in .pdf` | `489ad7808cbf0bacf403662d64de59b18e0079bffce2652d7392e7ffee08143a` |
| `chu2020compa` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Chu et al. - 2020 - Comparing Augmented Reality-Assisted Assembly Func.pdf` | `edafb2d750f2226c0b95b214915b16911be22e8fd5db839aac71a746b03ca0db` |
| `hoover2020measu` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Hoover et al. - 2020 - Measuring the Performance Impact of Using the Micr.pdf` | `bcffaaff49c20c6d27f0b8dce13df8c8f68e7379d73778213d4575de264812f0` |
| `kolla2021compa` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Kolla et al. - 2021 - Comparing Effectiveness of Paper Based and Augment.pdf` | `5bc23af3451e0fbc7a9decfd470f65378a0e6e0e6c0f686ce8c710bc7dcce51a` |
| `alves2022compa` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Alves et al. - 2022 - Comparing augmented reality visualization methods .pdf` | `d20ccab60e6b60ecc6164379c7170b07d71b3be50b4be7b79addf34b40853e2a` |
| `gonzalez-franco2017immer` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Gonzalez-Franco et al. - 2017 - Immersive Mixed Reality for Manufacturing Training.pdf` | `9e87ec5e9f97957138a055a95e83eedf48cfa1f1f1e698961a33c2f01d85adcc` |
| `havard2021case` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-manuf/Havard et al. - 2021 - A use case study comparing augmented reality (AR) .pdf` | `4fa2c48d1532dde71d6ce19733266f2f2502eec4e601f2606646470a513783ae` |
| `moro2021virtu` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/ar-metrics-med/Moro et al. - 2021 - Virtual and Augmented Reality Enhancements to Medi.pdf` | `81c00084db784ca5d43e00cf78c880bf7b4a2d24c13906106bcd77f2c5754876` |
| `azuma1994impro` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/mixed-reality/Azuma and Bishop - 1994 - Improving Static and Dynamic Registration in an Op.pdf` | `32769ecd41d64922a3b59bd68c70e587fdad52c151e6e46da2791234441e5674` |
| `marchand2016pose` | Already attached; retain | `/Volumes/Casa/refs/lib/dissertation/mixed-reality/Marchand et al. - 2016 - Pose Estimation for Augmented Reality A Hands-On .pdf` | `aae67f78dbdf23b7ed60b823b16338cd613c3f69d615b12eca4e18f227ca229c` |

Identity cautions: the library Wang PDF has garbled extracted text; its catalog DOI/key and filename identify it, and `/Users/djo/Downloads/1-s2.0-S1474034621000057-main.pdf` independently yields the correct DOI/title. Keep the existing attachment; no replacement is proposed. `/Users/djo/Downloads/dissertation.pdf` explicitly labels itself `v1.1.1 corrected release, June 28, 2026`; the several `oleary-2024-08-02*.pdf` files are older versions, not additional works to import. `/Users/djo/Downloads/msa.pdf` matches the Newell title but its cover says technical report `DRC-15-16-82`, April 1982; preserve it, do not move or attach it to the 1981 chapter. A title hit for “Human Performance” inside another article is not the Fitts/Posner book.

### Fetch/capture list (20 items)

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

The 16 attached-file names and verified hashes are in the file table. Five new attachments are only planned, and the 20 fetch/capture items have no local source hashes or final names yet. The execution report must replace these planned placements with CLI-assigned final names and verified hashes. No duplicate DEVONthink copy or raw project document is scheduled for relocation.

## Planned targets

```toml
project = "manufacturing-training-media-tradeoffs"

[[export.targets]]
output = "references.json"
profile = "csl-json-v1"

[[export.targets]]
output = "references.bib"
profile = "portable-bibtex-v1"
```

`references.bib` is **adopted as generated**, not deleted: natbib and the source bundle still read it. Its current bytes must first be imported; only after a satisfactory gate and approval may `--adopt --overwrite` replace them. Both targets contain the same 39 cited records. The two unused entries remain retrievable in the catalog. No script copies one bibliography into a second manually maintained `.bib`. The source archive should include the already generated BibTeX file and verified dependencies directly. Packaging is not permission to submit.

Register at least HTML/citeproc and PDF/natbib consumers, and verify the submission-profile source build independently with its own bibliography extraction. If default and submission PDFs are registered separately, each must pass even though they share the same natbib target. First fixtures come from same-commit before/after execution evidence and are recorded only according to the guide's gate rule; none are created here.

## Export gate table

These are **predictions from bounded bibliography-only probes**, not acceptance of a full paper render. The HTML probe uses the extension's exact `elsevier-harvard.csl` with Pandoc 3.10; the native probe runs actual BibTeX with the project's `elsarticle-num.bst`. Both probe all 41 entries to include the unused sources diagnostically. Proposed production export/render count is 39. Titles normalized by the catalog, brace nesting, punctuation, initials, DOI letter case and other purely restructured wording are disclosed without calling them lost facts. The HTML and numbered PDF styles already differ; the required comparison is each consumer against its own baseline, not cross-style byte equality.

| Key | Quarto HTML prediction | Numbered PDF / LaTeX bundle prediction |
| --- | --- | --- |
| `caudell1992augmented` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `degiorgio2023adopting` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `fang2023hmd` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `oleary2024augmented` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `oleary2025framework` | Identical facts with f6dd013: literal ampersand; publisher and restored from BibTeX name-list split. | Identical facts; brace/typography or DOI case only where present. |
| `funk2016interactive` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `daling2023assemble` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `yang2023industrial` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `kaplan2021effec` | Changed: full Human Factors journal name. | Changed: full journal name. |
| `buttner2020augme` | Identical facts; title case/typography may change. | Same facts; stored event title additionally prints in note. |
| `vanneste2020cogni` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `wang2021role` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `wang2024frontier` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `marino2024assessing` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `ariansyah2024learnability` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `sahoo2026laser` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `nakajima1988intro` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `ngcorrales2020overa` | Same visible year/volume/article facts; precise corrected date retained in data. | Changed: Issued: 2020-09-17 and existing publisher URL print. |
| `moyo2013devel` | Changed: Dissertation wording; department removed from place; publication year retained. | Same doctoral-work/institution/year facts; label becomes Dissertation. |
| `auburn2025honda` | Changed: Carla Nelson byline, webpage venue/URL/access date; exact issued day stored. | Changed: Carla Nelson byline, full issued date in note; original news outlet/URL retained. |
| `auburn2022ge` | Changed: Carla Nelson byline, webpage venue/URL/access date; exact issued day stored. | Changed: Carla Nelson byline, full issued date in note; original news outlet/URL retained. |
| `auburn2024hartzell` | Changed: Carla Nelson byline, webpage venue/URL/access date; exact issued day stored. | Changed: Carla Nelson byline, full issued date in note; original news outlet/URL retained. |
| `crossman1959theory` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `anderson1982acqui` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `newell1981mecha` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `fitts1967human` | Not rendered; remains uncited (not a missing reference). | Not rendered; remains uncited (not a missing reference). |
| `conover1982analysis` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `chu2021experimental` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `amouzgar2025novel` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `degiorgio2022assessing` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `tang2003compa` | Identical facts; title case/typography may change. | Same facts; stored event title additionally prints in note. |
| `chu2020compa` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `hoover2020measu` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `kolla2021compa` | Same paper identity as legacy bibliography; conference correction is catalog-side. | Identical facts; brace/typography or DOI case only where present. |
| `alves2022compa` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `gonzalez-franco2017immer` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `havard2021case` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `moro2021virtu` | Identical facts; title case/typography may change. | Identical facts; brace/typography or DOI case only where present. |
| `azuma1994impro` | Changed: erroneous conference suffix removed from title. | Changed: correct shorter title; stored SIGGRAPH event prints in note. |
| `marchand2016pose` | Identical facts; title case/typography may change. | Changed: retained catalog Issued: 2016-12-01 prints; title casing/DOI case also differ. |
| `gay-bellile2015appli` | Not rendered; remains uncited (not a missing reference). | Not rendered; remains uncited (not a missing reference). |

### Exact material before/after predictions

The following strings come from the HTML/citeproc probe; they identify every material wording change on that route. Date-of-access preview is conditional on capture occurring on September 27. Additional typography-only changes are not findings. DOI case normalization does not change an identifier.

**`kaplan2021effec`**

Before: Kaplan, A.D., Cruit, J., Endsley, M., Beers, S.M., Sawyer, B.D., Hancock, P.A., 2021. The effects of virtual reality, augmented reality, and mixed reality as training enhancement methods: A meta-analysis. Human Factors 63, 706–726. https://doi.org/10.1177/0018720820904229

Predicted after: Kaplan, A.D., Cruit, J., Endsley, M., Beers, S.M., Sawyer, B.D., Hancock, P.A., 2021. The Effects of Virtual Reality, Augmented Reality, and Mixed Reality as Training Enhancement Methods: A Meta-Analysis. Human Factors: The Journal of the Human Factors and Ergonomics Society 63, 706–726. https://doi.org/10.1177/0018720820904229

**`azuma1994impro`**

Before: Azuma, R.T., Bishop, G., 1994. Improving Static and Dynamic Registration in an Optical See-through HMD Proceedings of the 21st Annual Conference on Computer Graphics and Interactive Techniques, in: SIGGRAPH ’94. Association for Computing Machinery, pp. 197–204. https://doi.org/10.1145/192161.192199

Predicted after: Azuma, R.T., Bishop, G., 1994. Improving Static and Dynamic Registration in an Optical See-through HMD, in: SIGGRAPH ’94. Association for Computing Machinery, pp. 197–204. https://doi.org/10.1145/192161.192199

**`moyo2013devel`**

Before: Moyo, Y., 2013. Developing a multidisciplinary best practice manufacturing education and research laboratory for 21st century competitiveness (Doctoral dissertation). Auburn University.

Predicted after: Moyo, Y., 2013. Developing a Multidisciplinary Best Practice Manufacturing Education and Research Laboratory for 21st Century Competitiveness (Dissertation). Auburn University.

**`auburn2025honda`**

Before: Auburn University Samuel Ginn College of Engineering, 2025. Honda returns to Auburn for lean manufacturing training.

Predicted after: Nelson, C., 2025. Honda Returns to Auburn for Lean Manufacturing Training [WWW Document]. Auburn Engineering News. URL https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing-training.html (accessed 9.27.2026).

**`auburn2022ge`**

Before: Auburn University Samuel Ginn College of Engineering, 2022. Tiger Motors lab hosts GE Aviation training session.

Predicted after: Nelson, C., 2022. Tiger Motors Lab Hosts GE Aviation Training Session [WWW Document]. Auburn Engineering News. URL https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session (accessed 9.27.2026).

**`auburn2024hartzell`**

Before: Auburn University Samuel Ginn College of Engineering, 2024. Hartzell Engine Tech elevates manufacturing practices through Tiger Motors training.

Predicted after: Nelson, C., 2024. Hartzell Engine Tech Elevates Manufacturing Practices Through Tiger Motors Training [WWW Document]. Auburn Engineering News. URL https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices-through-tiger-motors-training.html (accessed 9.27.2026).

**`oleary2025framework`**

Before: O’Leary, D.J., 2025. Evaluating the effectiveness of AR/MR technologies in manufacturing training: A multi-modal assessment framework, in: Gentry, E., Ju, F., Liu, X. (Eds.), Proceedings of the IISE Annual Conference & Expo 2025. Institute of Industrial; Systems Engineers, pp. 1829–1834.

Predicted after: O’Leary, D.J., 2025. Evaluating the Effectiveness of AR/MR Technologies in Manufacturing Training: A Multi-Modal Assessment Framework, in: Gentry, E., Ju, F., Liu, X. (Eds.), Proceedings of the IISE Annual Conference &Amp; Expo 2025. Institute of Industrial and Systems Engineers, pp. 1829–1834.

The classic BibTeX probe additionally prints stored event facts for Büttner, Tang and Azuma, respectively `event: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems`, `event: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03`, and `event: SIGGRAPH ’94`. Ng Corrales gains `issued: 2020-09-17` and its existing MDPI URL; Marchand gains `issued: 2016-12-01`. The three news items gain the named author and `issued: 2025-05-27`, `issued: 2022-03-03`, `issued: 2024-04-12`. These are deliberate exposure of retained/corrected metadata, not unexplained drift. The Moyo probe retains `Auburn University` and prints `Dissertation` rather than `Doctoral dissertation`; native type is `@phdthesis`. Do not choose the rejected `@misc` result.

The IISE issue is a real altered venue, not casing preference: plain stored `Proceedings of the IISE Annual Conference & Expo 2025` becomes exported `... &amp; ...` and citeproc prints `... &Amp; ...`. It occurs with the current CSL serializer and style in the scratch probe. Report it as an export/consumer limit; do not edit the venue to spell “and,” protect a false title, suppress the citation, or silently adopt this output. This proposal includes no product fix. Execution cannot claim a clean CSL gate until a separately approved fix or target decision resolves it.

## Commits

This branch commits only this proposal. Publication and catalog have no changes from this pass: final SHA-256 checks match the initial catalog database, bibliography and all 104 inventoried publication files; the publication’s staged/unstaged status also matches the initial snapshot. After approval and a clean tree: catalog backup/import/reconciliation/intake precede scratch gates; generated targets, bibliography configuration and source-workflow documentation are committed separately from manuscript content. The refs register, verified fixtures and outcome report follow the guide, never a fabricated current fixture. No retirement of the still-consumed `.bib` is proposed.

## Timing

No intake time: nothing imported, fetched or attached. The local search covered 4,341 PDFs and the non-PDF title/URL scan; adapter and renderer probes ran only in scratch. This is a proposal/documentation task, so no unrelated full product test suite or R regression analysis was run. Scratch evidence at `/private/tmp/refs-manufacturing-proposal/` includes file inventory, PDF/text hits, predictions, matched metadata, hashes, citation keys, candidate exports, BibTeX assessments and per-key render strings.

## Findings and approval boundary

The conversion is not a blind bibliography replacement. It reuses eighteen dissertation-era identities, discloses eleven field conflicts, fills six existing records, distinguishes exact works from same-title editions, and separates two citation engines inside one Quarto project. The current manuscript changed the uncited count from four to two. Source checks justify a corrected Azuma title, Ng Corrales date, Kolla type, Moyo department/date handling, and three named news bylines. Those are proposed metadata changes with explicit gate predictions; they do not authorize manuscript edits or silent changes to unrelated shared-source facts.

Candidate changes and the incidents they prevent: a CSL entity-rendering fix prevents the observed IISE `&Amp;` venue corruption; recognized doctoral-genre handling prevents the rejected Moyo `@misc` projection from losing institution/degree; per-consumer configuration prevents feeding CSL JSON to natbib or switching the numbered PDF to Harvard without approval; source-version checking prevents attaching the 1982 report to a 1981 chapter; explicit project citation membership prevents the two unused records entering the reference list. These are findings, not product implementation authorization.

**Stop for owner approval.** Approval should explicitly cover the HTML/CSL versus PDF/natbib target interpretation, import/fill/conflict decisions, listed metadata corrections, 39 cited memberships, placement and fetch list. Execution additionally waits for a clean publication tree and resolution of the disclosed CSL venue defect. The conversion guide's step 4 requires an approved proposal before proceeding; no catalog or publication mutation is authorized by this report alone.
