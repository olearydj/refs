# Accepted Behavior Decisions

**Current through audit §14, 2026-09-21.** Explicit owner decisions outrank earlier proposals. The [audit](../specs/001-academic-catalog/reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) separates each question/options, literal reply and auditor interpretation. The [spec Clarifications](../specs/001-academic-catalog/spec.md#clarifications) links those replies to current outcomes. [Earlier examples and proposals](archive/behavior-decisions-pre-trim.md) remain historical, not additional scope.

## Conventions

T1/E1/S1/K1–K4 are recorded acceptances from the earlier review. Their prose is the assistant's interpretation of recommendations and short answers, not verbatim owner speech. Concrete lists and algorithms in contracts are implementation proposals. Preservation of assigned keys also follows constitution I; it was not a separate user quotation.

| ID | Accepted convention |
| --- | --- |
| T1 | Conventional internal Unicode Title Case with lowercase minor words, technical spelling and deliberate exceptions. Preserve full bibliographic titles and supplied subtitle boundaries; do not split every colon. |
| E1 | Ordinary numbered editions retain numeric meaning, rendered as 2nd ed. or 2E as appropriate. Versions/variants remain distinct. Ambiguous historic P1E, 5E or v5.1-CCBY4.0 do not authorize bulk reinterpretation. |
| S1 | Ignore leading whole-word A/An/The for English sorting; keep an explicit persistent override and leave displayed titles unchanged. |
| K1 | Author, year, then two complete eligible short-title words. Existing assigned keys survive metadata and policy changes. |
| K2 | Small explicit configurable stopword list beyond articles; the reviewed examples omit your/to, giving boostGit/introModern. No model-selected tokens. |
| K3 | Fall back from author to editor, then title-year without repeating the title; uppercase ND for missing year. Explicit key/key-author overrides; collision suffix -a…-z, -aa…; no silent identity merge. |
| K4 | Lowercase creator, lowerCamel title and hyphen separators: smith-2024-turingTrap, smith-ND-turingTrap, turingTrap-ND. One eligible word suffices; no truncation. |

Short-title overrides persist; absent one, use an explicitly known main title or the full title, without invented abbreviations. Changing a short title never regenerates a key. Existing pinned keys remain unchanged, even when they do not resemble the current template. Explicit rekey warns that external citations are not rewritten.

## A1 — Filenames, revised by the owner

**Question:** When slice 1 copies a PDF into the library, should it rename at that moment? **Literal reply:** “Rename by default”. Audit §14 records all options and the separate interpretation.

**Applied interpretation:** New copy intake uses the accepted no-spaces short-title, optional edition/version and year convention unless --keep-name is supplied. Examples: PracticalVim-2E-2015.pdf, TheTuringTrap-2022.pdf, ZeroToSold-v1.2.4-2020.pdf. If a usable short title or year is unavailable, retain the original basename and report that. This reverses preserve-by-default **only for new intake**. Linked/imported files, ordinary edits and later reorganize retain names, including spaces. No standalone filename command or bulk rename is included. This owner request supplies the separately requested naming policy under constitution II; it does not authorize renaming existing library files.

## A2 — Ownership and filing

**Literal reply:** “B: Derive mode from location (Recommended)”, audit §11. **Interpretation:** A file recorded by named root within library_root is managed; other files stay linked. There is no mode flag, managed-but-elsewhere state or resource adopt command. Outside linked files cannot be moved/renamed/deleted except through explicitly invoked intake, as constitution 2.0.0 states. Assigning filing collections to files already under the root never moves them. Selected reorganize remains explicit/previewed and preserves names; membership edits never move files.

Each managed file has one effective filing collection. Slice 1 uses unfiled as the intake folder/default without collection tables. Collections, projects and tags remain distinct; collection implementation and move default wait until after real-paper use. The constitution amendment is applied, authorized by the owner's “proceed with 1-3”; it is not pending.

## C1 — Capture, and projects

Initial metadata comes from an external researching agent through the CLI or an existing .bib. Retaining references/corrections outside individual papers is the primary workflow; built-in lookup is deferred. Supplied context and access claims remain distinguishable from bibliographic facts and verified reading.

**Background membership question; literal reply:** “No, cited only for now (Recommended)”. **Interpretation:** project create/show/cite/uncite suffice. A project is its cited sources in slice 1; uncite removes that association without touching the source or other projects. Keep the cited boolean for future membership without a migration. No project add/remove/list commands.

## Other recorded decisions

| Topic | Applied decision and delivery boundary |
| --- | --- |
| Metadata | “A: What I use (Recommended)”: bounded CSL-shaped core, optional native label, justified extensions and verbatim entries; not exhaustive Zotero vocabulary. Type-scoped semantic review precedes collapsing paths. |
| Zotero notes | “B: Fold into context (Recommended)”: later migration previews child notes into searchable context, excludes annotation/outline rows, retains related pairs and an external dated Zotero archive. No supporting-items subsystem. |
| Titles | The owner's clarification says “APA etc should govern exported material” and “I just don't want to see sentence case titles in the database.” Full literal reply is in audit §12/spec. Per-title protected terms and whole-title flag; braces seed protection except accent/command grouping. Non-English language is required at export; unprotected capitals warn. |
| Profile | “A: Portable default, richer by declaration (Recommended)”: portable BibTeX only now, @misc plus howpublished for web fallbacks. Richer profiles and public CSL/Zotero output wait. Case-only key twins are export errors. |
| Names | “C: No dependency (Recommended)”: built-in normalization plus small versioned Latin table; unsupported scripts require key-author override. AnyAscii/strict filter is a future fallback, not a dependency. |
| Locations | “A, but /casa/refs/cat and /casa/refs/lib”: config stays ~/.config/refs/config.toml; data uses canonical /Volumes/Casa/refs/{cat,lib}. Only library may be synced. No fallback catalog if the volume is missing. |
| Export | Four-class report; single-run unknown override; no write when blocked. Audit §14 defers scoped waivers and saved projections. Known blocking loss stays blocked, and re-import may report a lossy difference without overwriting current values. |
| Scope of works | refs catalogs citable works: publications, and talks with a public record a reader could find (a conference or symposium program, proceedings, a posted deck or recording, an event page). Talks to a class, a club, a seminar series or an internal audience, and organizing, moderating or panels, are activities and stay in the using document's own data, even when another institution invites the talk. Accepted 2026-09-28 for the CV: "I think that works". |
| First slice | Capture-to-export, verified copy-only intake and a demonstrated second-home restore. Imports never overwrite, report conflicts and safely rerun; update settles a value conflict. |

**Trim authorization:** “I'm satisfied with changes based on my answers”, audit §14. The [plan](../specs/001-academic-catalog/plan.md#deferred-work) owns the resulting deferred ledger. No slice 2 specification work before slice 1 has been used on a real paper. Exact current interfaces live in four contracts, not parallel proposals here.
