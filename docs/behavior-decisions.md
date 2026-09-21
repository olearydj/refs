# Academic MVP Behavior Decisions

**Feature status (2026-09-20):** This document retains source rationale and earlier review proposals. Current behavior is in the [clarified academic specification](../specs/001-academic-catalog/spec.md); implementation decisions are in its [plan](../specs/001-academic-catalog/plan.md) and [contracts](../specs/001-academic-catalog/contracts/cli.md). Later clarification answers supersede conflicting older defaults below.

**Status:** Partially reviewed: T1, E1, S1, K1, K2, K3, K4, A1, A2, and C1 accepted on 2026-09-20; remaining recommendations await review.
**Date:** 2026-09-20
**Scope:** Titles, editions, sorting, and citation keys first; concise proposals for adjacent workflows.
**Context:** [Academic MVP](academic-mvp.md), [workflow research](workflow-research.md).

## How to Review

**Agreed** records explicit user direction. **Proposed** means a recommended default that can be changed before specification. **Decision** identifies a consequential unresolved choice. Examples marked **catalog** were read from the current Zotero database; **synthetic** examples illustrate behavior and do not assert corrected bibliographic facts.

The purpose is to standardize routine work without requiring repeated editorial decisions. Preserve original imported values, apply predictable conventions, and make exceptions explicit. Approval of this sheet should precede executable contracts and implementation. No catalog changes have been made.

## 1. Titles and Short Titles

**Agreed:** Normalize titles to Title Case, preserve meaningful technical spelling, and keep displayed/cited titles separate from sorting. Make conventions configurable.

**Proposed:** Use a documented English Title Case policy: capitalize first/last words and the first word after a subtitle separator; otherwise lowercase a configured set of minor words. Preserve acronyms, formulas, names, and protected spans. Seed exceptions include `AI`, `GPT-4`, `LaTeX`, `PhD`, `Python`, `R`, `nbgrader`, and `pH`. Explicit user corrections take precedence. Non-English titles need language-appropriate handling rather than forced English rules; retain uncertain spelling for review.

| Input | Proposed result | Evidence |
| --- | --- | --- |
| `Sparks of Artificial General Intelligence: Early experiments with GPT-4` | `Sparks of Artificial General Intelligence: Early Experiments with GPT-4` | Catalog title; capitalization proposal only. |
| `An Introduction to Statistical Learning: with Applications in Python` | `An Introduction to Statistical Learning: With Applications in Python` | Catalog title. |
| `LaTeX for Complete Novices` | Unchanged. | Catalog title. |
| `measuring pH with Python` | `Measuring pH with Python` | Synthetic; protected mixed case. |

Preserve the full bibliographic title as the source-facing title. Retain a subtitle separately when supplied or explicitly identified, but do not destructively split every colon. The catalog's `LaTeX: A Document Preparation System: User's Guide and Reference Manual` illustrates why a colon alone is insufficient evidence of structure.

**Proposed short-title behavior:** Preserve existing short titles. When missing, derive a short title from the main title if its boundary is known; otherwise use the full title. Do not silently invent abbreviations. Allow an explicit short-title override for display and filename templates. Record derived versus user-specified status so later corrections do not erase intentional choices.

**Accepted T1:** Conventional Title Case with lowercase minor words and protected technical spelling. Accepted following the three-choice review. The finite minor-word list, hyphenation rules, and punctuation fixtures remain to be specified; this does not approve every proposed transformation automatically.

## 2. Editions, Versions, and Variants

**Agreed:** Standardize these conventions so the user need not remember how to enter or format them. Preserve distinctions between sources and editions.

**Proposed:** Treat numbered editions, descriptive edition statements, version labels, and variants as distinct concepts. Their physical schema remains undecided. Normalize equivalent unambiguous inputs, then render them through templates. Do not turn every number or suffix into an ordinal edition.

| Input | Proposed interpretation and output | Evidence |
| --- | --- | --- |
| `2`, `2nd`, `Second Edition` | Numbered edition `2`; display `2nd ed.`; filename token `2E`. | Synthetic equivalent inputs. |
| `Practical Vim…`, edition `2E` | Propose numbered edition `2`; retain short title `Practical Vim`; display `Practical Vim — 2nd ed.` | Catalog values; migration interpretation to approve. |
| `Programming in Lua, Fourth Edition`, edition `4E` | Propose title `Programming in Lua` and numbered edition `4`; avoid displaying the edition twice. | Catalog values; explicit migration preview before removing title text. |
| `LaTeX for Complete Novices`, edition `1.4` | Preserve `1.4`; propose a version label only after confirming its meaning. Never infer “14th edition.” | Catalog values. |
| `Zero to Sold…`, edition `v1.2.4` | Preserve the version label, including its meaningful components. | Catalog values. |
| Statistical Learning books with `P1E` and `R2E` | Preserve both values; propose Python/R variants and edition numbers only after confirming the shorthand. | Catalog values; no automatic split. |
| `Dungeon Master's Guide`, edition `5E` | Preserve `5E` until its meaning as a rules-system edition versus a book edition is settled. | Catalog values. |
| `Systems Reference Document`, edition `v5.1-CCBY4.0` | Preserve the complete value; confirm version/license separation before normalization. | Catalog values. |
| `Revised and Expanded Edition` | Preserve a descriptive edition statement; do not invent an edition number. | Synthetic. |

For new input, an explicit structured edition/version value avoids inference. Imports that embed an edition in the title should propose a correction when corroborating metadata exists, rather than remove potentially meaningful title text automatically. First editions may remain recorded even when a display/export format omits the label.

**Accepted E1:** Store ordinary numbered editions numerically and render them through templates, initially `2nd ed.` for display and `2E` for filenames. Keep versions and variants distinct. Existing ambiguous shorthand still needs interpretation before migration; approval of the convention does not approve bulk conversion of those values.

## 3. Sort Titles

**Agreed:** Fill a separate sort title automatically, ignore leading “The” when sorting, and permit a manual override without changing the displayed title.

**Proposed:** For English titles, remove one leading `A`, `An`, or `The` as a whole word, after ignoring enclosing opening quotation marks for comparison. Preserve the rest of the readable sort title. Compare case-insensitively; do not remove embedded articles or letters within words. Unicode collation details belong in implementation fixtures.

| Title | Derived sort title | Evidence |
| --- | --- | --- |
| `The Turing Trap: The Promise & Peril of Human-Like Artificial Intelligence` | `Turing Trap: The Promise & Peril of Human-Like Artificial Intelligence` | Catalog. |
| `An Introduction to Statistical Learning: With Applications in Python` | `Introduction to Statistical Learning: With Applications in Python` | Catalog, with proposed Title Case normalization. |
| `A New Kind of Science` | `New Kind of Science` | Catalog. |
| `Theoretical Statistics` | `Theoretical Statistics` | Synthetic; no partial-word stripping. |

Derived values update when their source title changes. Manual overrides persist until explicitly cleared. Changing the sort policy offers a previewed rebuild of derived values only. Missing sort titles can fall back to a derived comparison value rather than make records unfindable.

**Proposed ordering:** Sort title, then numeric edition when available, then publication year, then citation key as a stable tie-breaker. Descriptive/version-only editions need a documented fallback rather than being coerced to numbers. The default sort uses the full title, so subtitle distinctions remain visible.

**Accepted S1:** Ignore leading `A`, `An`, and `The` for English title sorting, with persistent manual overrides. Secondary ordering and language-specific collation remain proposals. Sorting by a supplied short title can be a separate explicit option.

## 4. Citation Keys

**Agreed:** Preserve existing keys. Make the generation template configurable. Title corrections, edition edits, and preference changes must not silently regenerate assigned keys.

**Observed:** Better BibTeX currently has `auth.lower+year+title.lower.substring(1,5)` configured. Stored keys include `johnson2023boost`, `brynjolfsson2022turin`, `wotc2014dunge`, and exceptions such as `montgomery2019`. All 562 stored keys are pinned. The formula alone does not establish its exact tokenization or abbreviation semantics.

**Accepted K1:** Author first, followed by year, followed by two complete words from the short title, ignoring articles. This preserves author-prefix completion, uses the year as a visual separator, and favors readable words over arbitrary truncation. Existing keys remain unchanged. The template remains configurable. Exact stopword scope and token formatting are separate decisions below.

**Accepted K4 — rendering:** Lowercase the author token and use lower camel case for the title fragment, with hyphens between components, as in `brynjolfsson-2022-turingTrap`. Separate a collision suffix with another hyphen, as in `brynjolfsson-2022-turingTrap-a`. Do not truncate the two selected words. If only one eligible word exists, use it without padding. Use the maintained short title, including a user override; when it is absent, use the short-title derivation policy rather than the sort-title override. Once a key is assigned, later short-title edits do not change it.

### Examples of Stopword Handling

The following use actual catalog short titles. New-key previews illustrate the accepted rendering and do not authorize changes to historical keys.

| Short title | Existing key: preserved | Ignore only articles (`a`, `an`, `the`) | Also ignore selected minor words |
| --- | --- | --- | --- |
| `The Turing Trap` | `brynjolfsson2022turin` | `brynjolfsson-2022-turingTrap` | Same. |
| `Boost Your Git DX` | `johnson2023boost` | `johnson-2023-boostYour` | `johnson-2023-boostGit` if `your` is excluded. |
| `Intro To Modern Stats` | `cetinkaya-rundel2021intro` | `cetinkaya-rundel-2021-introTo` | `cetinkaya-rundel-2021-introModern` if `to` is excluded. |
| `Little Book Of Deep Learning` | `fleuretlittl` | `fleuret-2023-littleBook` | Same with `of` excluded. |
| `GPT4 Technical Report` | `openai2023gpt4` | `openai-2023-gpt4Technical` | Same. |

**Accepted K2 — stopwords:** Use a small, explicit, configurable exclusion list beyond articles so the selected words usually convey subject matter. The reviewed examples exclude `your` and `to`, producing `boostGit` and `introModern`. Specify the complete default list in the behavior contract and expose it in configuration and key previews; do not let a model choose words during generation. This list is distinct from the minor-word list used for Title Case. Changing it does not regenerate assigned keys.

### Fallbacks and Collisions for Review

| Situation | Proposed behavior |
| --- | --- |
| Personal author | First author in source order; use their family name, lowercase, transliterate accents, preserve surname hyphens, remove spaces/apostrophes. Keep original spelling in metadata. |
| Corporate author | Configured alias if present; otherwise normalized literal name. Never invent an acronym silently. |
| No author | Use the first editor when available. With neither author nor editor, use the same two selected short-title words followed by year, with no repeated title fragment. Explain the fallback in preview. |
| No year | Use uppercase `ND` as the visible separator; do not invent a publication year. With no author/editor, append `ND` after the selected title words. |
| Explicit key-author override | Takes precedence for generation without changing bibliographic authorship. |
| No eligible title words | Request an explicit key or use a stable-ID fallback to be specified. |
| Same source imported again | Retain its key and report metadata differences. |
| Distinct new sources generate the same key | Next free suffix `-a`–`-z`, then `-aa`, `-ab`, etc.; leave prior keys unchanged. Check and allocate transactionally. |
| Different sources import the same existing key | Report a conflict rather than overwrite or silently rename. |
| Explicit key regeneration | Preview the change; consider retaining the previous key as a resolvable alias. External documents are not rewritten automatically. |

The catalog's `wotc2014dunge` has editors Mike Mearls and Jeremy Crawford, rather than a corporate author named WotC. Preserve that key as-is. An explicit key-author override could support this convention for new entries without manufacturing a corporate author.

**Accepted K3 — fallbacks, collisions, and overrides:** Use author, falling back to editor. When neither exists, replace the author-led structure with the selected short-title words followed by year; do not repeat the title words after the year. Use uppercase `ND` for a missing year. Append collision suffixes without changing earlier keys. Always allow an explicit key override. The lowercase `anon` and `nd` proposals are superseded.

| Available metadata (synthetic) | Key shape | Example using the accepted rendering |
| --- | --- | --- |
| Smith, 2024, short title `The Turing Trap` | author + year + title words | `smith-2024-turingTrap` |
| No author, editor Smith, 2024 | editor + year + title words | `smith-2024-turingTrap` |
| Neither author nor editor, 2024 | title words + year | `turingTrap-2024` |
| Smith, no year | author + `ND` + title words | `smith-ND-turingTrap` |
| Neither author nor editor nor year | title words + `ND` | `turingTrap-ND` |
| Distinct source collides with the first example | new key + next free suffix | `smith-2024-turingTrap-a` |

Uppercase `ND` marks an unavailable year; hyphens provide consistent component boundaries whether the year is present or missing. An override bypasses generation, but still requires key validity and uniqueness checks; it cannot overwrite another source's identity. Punctuation, hyphenated title words, transliteration, and acronym rendering still need fixtures. Same normalized DOI is an identity signal requiring reconciliation, not permission to overwrite; the same title alone does not establish identity.

## 5. Adjacent Workflow Defaults for Later Review

These complete the first draft without requiring every detail to be settled in the first interview. The [configuration and CLI review draft](configuration-and-cli.md) now develops these proposals into concrete defaults and an everyday walkthrough; its new choices remain unaccepted.

| Area | Agreed | Proposed default / remaining decision |
| --- | --- | --- |
| Attachment location | Any type; scattered files supported; optional move into the document library when adding a reference. Bulk collection remains later work. | Intake default is unresolved following the Downloads-retention concern. Keep link-in-place available; separate moving and renaming. Prefer an explicitly designated primary resource, otherwise the sole PDF; multiple PDFs require selection. |
| Attachment names | Preserve existing filenames. Generated filenames use no spaces: short title + optional edition/version + year, separated by hyphens. | Bulk renaming remains deferred. Managed placement and reorganization are now early requirements under A2; moving does not imply renaming. |
| User configuration | Editable preferences; backup-friendly home; credential helpers. | `~/.config/refs/config.toml` beside the database, with path inspection and validation. |
| Project configuration | Local overrides supported, possibly deferred. | `.refs.toml`; invocation options override project settings, which override user defaults, for permitted keys. Catalog-wide normalization/key rules remain user-level. Explicit home selection remains separate from project discovery. |
| Bibliography export | Explicit invocation only; no change-triggered regeneration. | Export command callable from build scripts or skills; refuse accidental overwrite of an unadopted existing bibliography, with an explicit adoption/overwrite path. |
| Inspection and editing | Agent-friendly structured operations. | Preview transformations as field-level before/after values with reasons; make ordinary record editing direct, with transactions and revision checks. |

**Accepted A1 — attachment filenames and scope:** Preserve existing filenames, including existing spaces. When explicitly generating a new filename, use the reviewed no-spaces style: `PracticalVim-2E-2015.pdf`, `TheTuringTrap-2022.pdf`, and `ZeroToSold-v1.2.4-2020.pdf`. Do not enforce that convention by renaming imported or linked files. Shared-folder collection and bulk renaming are later-version possibilities, not MVP requirements. If collection is added, preserve names by default and make renaming a separate explicit option. These naming choices do not settle attachment-role or primary-selection proposals.

**Accepted A2 — collections and managed placement:** Support hierarchical collections distinct from projects and subject tags. A source may belong to multiple collections; a managed attachment has one designated filing collection determining its physical placement beneath a configured document-library root. Linked-in-place files remain untouched by collection changes. Managed placement permits explicit, previewed reorganization that moves files and updates catalog links; membership edits do not automatically move files. Existing Zotero links may be explicitly adopted into managed placement without an immediate move. Reorganization must handle conflicts, interrupted transfers, and reporting of potentially broken external links; it does not promise to repair Obsidian links automatically. Preserve filenames during placement changes. This brings a small collection hierarchy, intake, and managed reorganization into early requirements, refining A1's earlier blanket deferral of collection operations. Broad bulk consolidation and bulk renaming remain later possibilities. The new-file intake default, folder mapping details, and handling of an unfiled source remain open.

## Review Sequence

**Accepted C1 — initial source capture:** An external agent obtains bibliographic information and submits it through the CLI. The user already constructs ad hoc bibliographies this way outside Zotero; retaining those references in a reusable catalog is a primary motivation. Built-in identifier lookup is deferred. Existing project bibliographies are also reconciliation inputs, not proof that Zotero already holds all relevant sources and corrections. See the [recovered session evidence](workflow-research.md#agent-supplied-references-in-the-manufacturing-paper). Command syntax, submission schemas, and conflict-resolution details remain proposals.

T1, E1, S1, K1, K2, K3, and K4 are accepted. The component separators and basic camel-case rendering are settled; detailed punctuation, acronym, and transliteration fixtures remain. A1 establishes filename conventions; A2 refines its scope by bringing collections, managed intake, and explicit reorganization into early requirements while deferring bulk renaming. C1 establishes agent-supplied metadata as the initial capture path. Project configuration, the daily workflow, and ambiguous historical edition labels remain review topics, collected in [loose requirements](requirements-review.md). The current discussion stops at requirements collection, before feature specifications.

Record accepted choices here before promoting them into the feature specification; unanswered recommendations remain proposals. After promotion, the specification owns executable behavior and this sheet should link to it rather than evolve as a parallel contract.
