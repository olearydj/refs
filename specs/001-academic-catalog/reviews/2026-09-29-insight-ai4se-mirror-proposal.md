# INSIGHT and AI4SE bibliography mirror proposal — 2026-09-29

**Proposal only.** Create two cited-work projects, reuse five catalog records, add two verified works, and defer the uncited technical report. INSIGHT cites **six** works, although its starter `.bib` contains seven; the submitted AI4SE abstract cites **four**, although its `.bib` contains five. Each paper retains its own bibliography and delivered text. No catalog or publication changes, backups, attachment intake, exports, register rows, conversion checks, or renders were performed.

This follows the owner's instruction to mirror the papers “in spirit” while making refs entries as correct as the sources allow. The branch is `s2/insight-ai4se-mirror-proposal`, based on `f75d9d7`. The owner decides this proposal before execution.

## What the papers actually cite

INSIGHT's `article.qmd` has six distinct citation keys. All six identities appear in the body and the reference list on printed page 42 of `published/oleary-ledford-2026-insight-dema-llm-version-of-record.pdf` (six PDF pages, printed pages 37–42). `oleary2025techreport` is not cited or listed. The bottom of page 42 also contains references continued from another article on page 36; those are not this paper's sources. The repository's instructions correctly distinguish its pre-review Quarto/BibTeX sources from the delivered manuscript and version of record. The published PDF, rather than the starter `.bib`, controls this mirror's membership.

AI4SE's `proposal/abstract.qmd` cites four identities in “Background: From a Point Solution to a General Capability.” The existing submitted `proposal/abstract.pdf` has the same four citations and a four-entry reference list on PDF page 3. `ledford2023dissertation` is unused. The rejected submission remains archived as submitted; no new render was needed.

| Paper key | Proposed catalog key | INSIGHT membership | AI4SE membership | Identity evidence |
|---|---|---|---|---|
| `ledford2023dissertation` | Same, existing | Cited | Not cited; `.bib` only | Allison B. Ledford's 2023 Auburn dissertation; exact title, author, thesis title page, and [Auburn ETD handle 10415/8918](https://etd.auburn.edu/handle/10415/8918). |
| `ledford2023ieee` | Same, existing | Cited | Cited | Exact title and three authors; DOI `10.1109/OJSE.2023.3325189` on the existing published PDF, volume 1, pages 139–152. |
| `ledford2025syseng` | Same, existing | Cited | Cited | Exact title and four authors; DOI `10.1002/sys.21776`, [publisher record](https://incose.onlinelibrary.wiley.com/doi/full/10.1002/sys.21776), volume 28(1), pages 15–28. |
| `ledford2024mbe` | Same, new | Cited | Absent | Public 2024 MBE Summit program and NIST-hosted presentation, detailed below. |
| `ledford2024patent` | Same, new | Cited | Absent | US 12,131,134 B1, granted 2024-10-29; official document and Google Patents, detailed below. |
| `oleary2025ai4se` | Same, existing | Cited | Cited | Exact title, both presenters, existing deck and [organizer's public workshop record](https://sercuarc.org/event/ai4se-se4ai-workshop-2025/). |
| `oleary2026insight` | `olearyledford2026insight`, existing | This paper itself, not a reference | Cited | Exact title and two authors; delivered INSIGHT PDF and DOI `10.1002/inst.70055`, volume 29(3), pages 37–42. |
| `oleary2025techreport` | No addition proposed | Not cited; `.bib` only | Absent | Local report exists; public publication status unverified. See decision 1. |

Catalog search by patent number and distinguishing titles found no existing copy of either proposed new work. The five existing records were read through `refs show`, and their linked primary PDFs were checked. The catalog's `gadzey2026dema-digital-thread` is a different 2026 poster with six authors despite sharing the dissertation title; it is not used for either mirror. Neither proposed project name already exists.

## Record accuracy and differences from the papers

Reuse the five existing records and preserve their keys and attachments. No correction to those existing records is required by the identity review. Every O'Leary author remains **Danny J. O'Leary**, including when the 2025 slide deck prints “Dan O’Leary.” No extra author-name normalization is proposed for the other contributors.

The AI4SE `.bib` abbreviates or omits metadata that refs already has: the IEEE DOI, volume and pages; the Systems Engineering DOI, volume, issue and pages, full Susan Askew name, and correct journal title; the published INSIGHT DOI, volume, issue and pages in place of “In press.” AI4SE uses Gregory A. Harris and Allison B. Ledford where the two journal articles' bylines and corresponding catalog records use Gregory Harris and, for Systems Engineering, Allison Ledford. These are the same people and works. The 2025 Systems Engineering issue year remains 2025 even though its publisher reports first online publication in July 2024.

The existing workshop record also supplies September 2025, Washington, DC, and the speech/workshop-presentation type. The organizer confirms the September 17–18 event, but the catalog's month-only date is not incorrect; no exact presentation day is inferred from the two-day event. These differences are information for the mirror, not corrections to either paper. The patent's more substantial title and name corrections are specified below.

## The three candidate additions

### 1. `ledford2024mbe`: eligible; add

Use type `speech`, genre `Conference presentation`, language `en`; author Allison B. Ledford; title **Data Element Mapping and Analysis (DEMA): A Systematic Method to Implement a Complete Digital Thread**; issued **2024-04-17**; event **MBE & QIF Summit 2024**; event place **MxD, Chicago, IL, USA**; URL **https://www.nist.gov/system/files/documents/2024/04/24/Ledford_Data_Element_Mapping_and_Analysis.pdf**. Protect `DEMA` in the title. Preserve the paper-assigned key `ledford2024mbe`.

The [NIST deck](https://www.nist.gov/system/files/documents/2024/04/24/Ledford_Data_Element_Mapping_and_Analysis.pdf) and existing local 14-page PDF agree on title and Allison B. Ledford's authorship. The [DMSC public agenda](https://qifstandards.org/mbe-qif-summit-2024/) schedules her talk on April 17 at 09:00; [NIST's event record](https://www.nist.gov/news-events/news/2024/04/mbe-qif-summit-2024) independently links the deck and identifies MxD in Chicago. This meets the accepted “Scope of works” rule for a talk with a discoverable public record. The `.bib` has only Allison Ledford and the year; refs can retain the fuller byline and exact date. The deck title uses “and”; the agenda's ampersand is not a different work.

### 2. `ledford2024patent`: eligible; add with corrected metadata

Use type `patent`, language `en`; title **Physical Components Using Data Element Mapping and Analysis**; inventors in source order **Allison Brown Ledford, Gregory Allen Harris, Haley Patterson, Phillip Farrington**; issued **2024-10-29**; number **US 12,131,134 B1**; jurisdiction **US**; authority **United States Patent and Trademark Office**; URL **https://patents.google.com/patent/US12131134B1/en**. Preserve key `ledford2024patent`; the printed shorthand title does not determine the catalog title. There is no acronym in the official title to protect.

The [Google Patents record](https://patents.google.com/patent/US12131134B1/en) and [public patent facsimile](https://patentimages.storage.googleapis.com/a6/1b/47/7b3d5b1b928a4b/US12131134.pdf) identify the same number, date, title and inventors. I inspected page 1 of the local 27-page image-only facsimile as a static image. It prints “Phillip Farrington”; retain that byline rather than infer a different spelling from assignment-event text. The patent application number, filing and priority dates are distinct from the granted patent's number and issue date. No legal-status or current-ownership claim is proposed.

INSIGHT prints the shorthand “Data Element Mapping and Analysis (DEMA)” and abbreviates the inventors as Allison B. Ledford, Gregory Harris, H. Patterson and P. Farrington. The exact patent number and issue date settle identity despite those differences. Refs should hold the official title and full inventor names; the paper remains untouched.

### 3. `oleary2025techreport`: defer; not cited and eligibility unverified

`/Volumes/Casa/dev/dema-llm/docs/reports/dema_llm_technical_report.md` exists with the heading **DEMA-LLM Technical Development Report**, subtitle **AI-Enhanced Data Element Reconciliation System**, ICAMS Research Laboratory/Auburn University, and September 2025. Its title block says “Technical Director” rather than naming an author; the paper's unused `.bib` attributes it to Danny J. O'Leary. The local file has later git edits and is not established as a fixed September 2025 release.

Exact-title and DEMA-LLM/report web searches found no public publication record. The local DEMA publications index lists the talk and patent with public links but not this report; the implementation repository has no configured remote. This is bounded negative evidence, not proof that no published copy exists. Under the kickoff's request to verify scope eligibility, defer addition pending a discoverable publication record or an explicit owner decision about this internal report. If admitted later, use `report`, the complete title above, author Danny J. O'Leary once confirmed, publisher ICAMS Research Laboratory, Auburn University, and the verified release date/version. It would remain outside both cited-only projects.

## Proposed attachments and owner fetch list

Link the two existing reference copies in place during approved execution. These files belong to the DEMA documentation repository; do not move, rename or replace them. Existing catalog resource links remain unchanged.

| New key / proposed label | Existing source | SHA-256 |
|---|---|---|
| `ledford2024mbe` / `slides` | `/Volumes/Casa/dev/dema-docs/publications/files/ledford-2024-mbe-summit-dema.pdf` | `930acdb69fbe6afb84730886abce7bb14c44985dbe641789d60949dc9f72c7d6` |
| `ledford2024patent` / `published` | `/Volumes/Casa/dev/dema-docs/publications/files/us-12131134-b1-dema-patent.pdf` | `d9ad6b2042ef734a249eadda41a65160b12d5d8ef4172eb1960768cb7ddf465b` |

Execution would use `refs resource add <key> --link --path <existing-path> --label <label>`, with dry runs first. Public recovery URLs are supplied above. No owner PDF fetch is needed for either eligible addition. For the deferred report, the only open source request is a public release/record and identified version if the owner wants catalog consideration; the local Markdown file is already available and need not be fetched.

## Projects and exact description notes

Create `insight-dema-llm` with exactly the six INSIGHT keys in the table. Its `--description` text:

> Bibliography mirror of the published INSIGHT DEMA-LLM article. The paper keeps its own references.bib and frozen published references; refs mirrors only the six works it cites. Refs records are kept as correct as possible and may be more correct than the paper's printed entries. This is intentional; refs does not supply or rewrite the paper's bibliography.

Create `ai4se-pipyer-proposal` with exactly `oleary2025ai4se`, `olearyledford2026insight`, `ledford2023ieee`, and `ledford2025syseng`. Its `--description` text:

> Bibliography mirror of the rejected AI4SE/SE4AI 2026 Pipyer abstract, archived as submitted. The paper keeps proposal/references.bib and its frozen submitted references; refs mirrors only the four works it cites. Refs records are kept as correct as possible and may be more correct than the submitted entries. This is intentional; refs does not supply or rewrite the paper's bibliography.

Project descriptions and the following documentation provide the requested configuration. No `.refs.toml`, export target or conversion-register entry is proposed. Project creation and each `project cite` will be previewed before execution; neither entire `.bib` should be bulk-cited. Preserve the two new records' source entries as originals when admitting their corrected metadata, so the papers' original spelling/title claims remain inspectable.

## Exact `docs/refs.md` drafts for session 1's subagent

### `/Volumes/Casa/pub/2026-insight-dema-llm/docs/refs.md`

```markdown
# Bibliography mirror in refs

This published paper keeps its own `references.bib`; refs is not the source of its bibliography. The local Quarto and BibTeX files are pre-review sources. The delivered manuscript and published version of record retain their frozen references.

The refs project `insight-dema-llm` mirrors the six works cited in the published paper. Refs records are kept as correct as possible and may be more correct than the paper's printed entries. That is intentional and does not change the paper. The unused technical-report entry in `references.bib` is not project membership.

Inspect the catalog mirror with `refs project show insight-dema-llm`. Do not export a refs bibliography into this publication or rewrite its citations as part of mirror maintenance.
```

### `/Volumes/Casa/pub/rejected/2026-ai4se-pipyer/docs/refs.md`

```markdown
# Bibliography mirror in refs

This rejected abstract is archived as submitted. It keeps `proposal/references.bib` as its own bibliography source; refs does not supply or rewrite it. The submitted text and references remain frozen.

The refs project `ai4se-pipyer-proposal` mirrors the four works cited in the submitted abstract. Refs records are kept as correct as possible and may be more correct than the submitted entries. That is intentional and does not change the paper. The paper's key `oleary2026insight` maps to catalog key `olearyledford2026insight`; the unused dissertation entry is not project membership.

Inspect the catalog mirror with `refs project show ai4se-pipyer-proposal`. Do not export a refs bibliography into this archive or rewrite its citations as part of mirror maintenance.
```

Session 1's subagent should stage and commit **only `docs/refs.md`** in each paper after approval. INSIGHT is at `521e994`; its actual preflight status includes modified `.gitignore` and `README.md`, plus untracked `AGENTS.md`, `PROJECT_CONTEXT.md`, `admin/`, `published/`, and `revisions/`. AI4SE has the reported modified `.gitignore` and untracked `REJECTED.md`. Preserve all of them, including the publication PDFs currently untracked in INSIGHT. No pointer edits to README/AGENTS/PROJECT_CONTEXT are proposed.

## Owner decision

1. **Technical report scope:** **A — defer it (recommended)** and approve the two verified additions plus the six/four cited-work mirrors. The report is uncited and lacks an established public release; no mirror is incomplete by leaving it out. **B — supply a public publication record/version** and revisit its catalog eligibility as a separate, uncited record before execution. An internal-only exception would require an explicit owner scope decision rather than treating the unused `.bib` entry as proof of publication.

No other substantive judgment is needed. The six/four counts follow the delivered evidence, and the corrected patent identity is verified. Approval of this proposal also approves the proposed project names, descriptions, two in-place attachments, and two documentation files; it does not authorize export or conversion.

## Verification record

The delivered INSIGHT PDF SHA-256 is `02567dceb4916267e82ef5f1b58bafcf340870c2215c38e037903090bc7d9af2`; submitted AI4SE PDF SHA-256 is `cc5b19b0b0b5405d8e2de0da7e35d955a0651b1eee6279d6e05331ca7058fd2f`. Scratch evidence in `/private/tmp/refs-insight-ai4se-mirror` contains text extractions, catalog reads, citation-key inventory and preflight hashes/status. Both papers' tracked bytes and dirty status were rechecked unchanged. This documentation-only proposal requires no code tests. No public/private record was uploaded to a search service; searches used bibliographic titles and public identifiers.
