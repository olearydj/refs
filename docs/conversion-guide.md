# Converting a project to refs

How an existing writing project moves its bibliography into the catalog and takes its reference list back as an export. Written from the family-document pilot and the inventory of 2026-09-26, before the first academic conversion; the findings section at the end grows by one entry per project. Governing rules are in the contracts; this page is the working order.

## When a project qualifies

It has a bibliography file it builds from, kept by hand or by an agent, and the file is not an export from Zotero already in the catalog. The inventory review lists the candidates. A project in the middle of a submission still qualifies, because nothing here changes the project until the export is proven identical in meaning.

## The order

The order has two halves and a stop between them. The first half is read-only and ends in a proposal; nothing in the catalog or the project changes until the owner approves it. The second half executes the approved proposal and stops again only at the export gate. This is so the retypes, versions, unlinks and attachments are decided once, before anything runs, rather than discovered after a gate and redone.

### Propose, read-only

1. **Inventory the project.** Name every bibliography file, who writes it, and every consumer: a Quarto or pandoc build, a LaTeX build with biber or natbib, a venue that demands a `.bib`, a site build, a sync script. Note the citation-key style, since keys must not change. Record which entries the prose cites, so the export can be cited-only later without dropping anything the text uses.

2. **Find the sources.** Read-only in this half: search the stores listed in the attach step below, match by DOI first and then by title, and list what was found with paths, what needs a fetch with the link, and what is URL-only. Nothing is downloaded or moved yet.

3. **Plan the records.** From the bibliography and the sources found, decide per record what the completion step will do: the type the thing is, the kind, protected names, the software version and release date from the rule below, which notes move to context, and what file will be attached from where. Decide the export targets and profiles per consumer and the expected gate outcome per entry, identical or changed with the expected wording.

4. **Stop for approval.** Write the proposal in the report template's first sections: backup name, inventory and consumers, planned import, planned record completions by key, sources found and the fetch list, planned targets and the expected gate outcomes. The owner approves, amends or declines. Only an approved proposal proceeds; an amended one is rewritten and approved again.

### Execute the approved proposal

5. **Backup.** `refs backup --output /Volumes/Casa/refs-backups/<date>-before-<project>-<pass>`, one per pass of a project, named by the pass. Check the manifest validates.

6. **Import.** `refs import --format bib --input references.bib` (or `--format csljson`) with the project named as origin. Read every outcome: applied is new, unchanged is already there, conflict means the catalog holds a different value for a bound source and both are kept for `import reconcile`, invalid names a limit and preserves the entry. Nothing is guessed; a refusal is recorded, not worked around. Where a DOI binds an entry to a source the Zotero import created, the conflict list is the interesting part: it shows where the agent's hand-written entry and the library disagree.

7. **Create and cite the project.** `refs project create <name>` and `refs project cite <name> KEY` for every entry the prose cites, plus the ones the bibliography carries uncited if the owner wants them kept. The export is cited-only, so this list is the reference list.

8. **Complete the records** exactly as approved: One pass over every record before any export gate, so the gate runs once. Is the type what the thing is: a software project cited by its repository is `software`, not `webpage`; documentation is a `webpage` with the site as container title; a scanned order is a `document`. Does a kind apply: `repository` for source code repositories, `podcast`, `lecture` and the rest as the registry lists them. Are software and product names protected in the title, so styles do not recapitalize them. For software, version and date follow the rule below. Notes hold facts meant for the page; capture provenance and caveats go to context.

9. **Attach the sources** exactly as approved. Every record should end up connected to the thing it describes. Look first in the project folder and its figures, the vault project if there is one, the library at `/Volumes/Casa/refs/lib`, then DEVONthink exports and `~/Downloads`; match by DOI first, then by title. Then by kind of source: an article is fetched by DOI, and open-access publishers have stable PDF locations (JOSE and JOSS by DOI path, PLoS by article id, DOI content negotiation where offered); paywalled and bot-gated hosts, Elsevier and the bepress repositories among them, refuse scripted downloads as a rule and are a browser download by the owner through the university VPN. A software record gets the README at the default branch's current commit and the repository's API metadata, both named with the commit and the date. A web page gets a single-file capture at the accessed date. Files move into the library by `resource add --move`, which names them by the convention and files them under `unfiled` until the loc taxonomy exists; a project's own raw material, such as a vault's scans, stays where it is and is linked in place with loc empty. The owner's fetches from the approved list are attached the same way; the pass is not complete until every item on the list is attached or disclosed as missing.

10. **Export per consumer, to scratch.** Never over the project's file. A pandoc or Quarto consumer takes `--profile csl-json-v1`, the identity mapping; a LaTeX build or a venue that wants BibTeX takes `--profile portable-bibtex-v1`. CSL JSON titles may carry CSL's own markup, `nocase` spans for protected case and the `i`, `b`, `sup`, `sub` and `sc` tags; citeproc renders them, and any consumer that formats titles itself from the export, such as a site build, must render or strip them too. Render the project from the scratch export with its own configuration and diff its reference list against the current render, entry by entry. The gate has three outcomes: identical; wording changed by a deliberate type or field correction from step 5, listed per entry with the exact before and after; or a fact lost or altered, which stops the pass until the record or a refs limit explains it. The owner decides adoption once, from the per-entry list; an outcome the proposal did not predict is reported as such.

11. **Adopt.** Export to the project's path, change the one bibliography line in the build configuration, write `.refs.toml` with the project and target, and commit those together, separately from any content change. Refs remembers the bytes of the last export it published to a target; if that export is later discarded through git, the next export refuses with "Destination differs from recorded export bytes" and needs `--overwrite` after confirming the file on disk matches the commit, and the replaced bytes are kept in the catalog's originals. When the gate passes, the exported file and the rendered reference-list text become that project's fixture, and the project joins the register below with the refs version and the pandoc and Quarto versions it was verified against.

12. **Retire the hand-kept file** once nothing reads it, in the same commit as the reader's switch, never before.

13. **Document in the project.** A short `docs/refs.md` in the project: the catalog is the master, the export is generated and never edited, how to add and cite a source, how to re-export, and the checks after every export. Point to it from the project's README and agent instructions.

14. **Report and record.** Write the pass report in the template below, add the findings to this page, and complete the register row. Feature decisions go to the plan's ledger, not to this page.

## Rules the steps rely on

A record links only the source's own file: its PDF, its capture, its scan. A project's synthesis or review note is a project document; a fact from it about one source goes into that record's context.

A software record's version is the release current on the record's accessed date, and its issued date is that release's date, both from PyPI or GitHub release history and recorded as a lookup in context, never guessed. Without them Chicago prints "released." with nothing after it.

## Report template

Every pass report uses the same headings, so reports diff against each other: backup and scope; inventory and consumers; import outcomes by key; record completions by key; sources found, fetched, and the fetch list for the owner; attachments with final names and hashes; the export gate table with exact before and after per changed entry; commits; timing; findings. Session reports live under `specs/001-academic-catalog/reviews/` named `<date>-<project>-<pass>.md`.

## Checks

The catalog backup validates; the import's counts sum to the file's entry count and every invalid entry has a named reason; the project's cited count equals the reference list the prose needs; each linked or copied file's hash matches the original; the rendered reference list from the scratch export loses no fact; the build passes after the switch; the project's docs name the export and the re-export command.

After any change in refs to an export profile or a projection, every project in the register is re-exported from the real catalog read-only, re-rendered by every consumer in its row, the style and any hand-rolled formatter alike, and each reference-list text diffed against the last verified render; every difference is listed and explained before the change merges. The suite tests refs's reading of its own exports and the corpus never renders, so the register is the only check that sees what a style prints. The real-trial harness automates this walk and stores each project's verified text as a fixture pinned to the tool versions that produced it.

## Boundaries

Prose is never edited for a conversion. Citation keys never change. Nothing under a project's own source store is moved. A refusal is disclosed, not patched around. A conversion adds no feature to refs; it produces evidence.

## Converted projects

One row per project whose bibliography is an export of the catalog. The row is the regression check's worklist: what to export, with which profile, what renders it, and what it was last verified against.

| Project | refs project | Export target and profile | Consumer and style | Last verified |
| --- | --- | --- | --- | --- |
| `/Volumes/Casa/pub/2026-james-harvey-long` | `jhl-report` | `references.json`, csl-json-v1, read by the Quarto report and the site build | Quarto 1.10 with pandoc 3.10, the project's own `ieee.csl` with genre added for documents and web pages; the site build `site/scripts/build_data.py` is a second consumer that formats its own Sources list from the same file and must handle CSL title markup | 2026-09-26, refs 0.7.0 at 105803c (title protection as `nocase` spans), publication commits 94445e5 (site formatter renders CSL title markup) and 25257f8 (re-export); 101 entries, report text identical to a fresh pre-export render, site sources identical to baseline, site version 7 |
| `/Volumes/Casa/pub/2026-jose-danvas` | `jose-danvas` | `references.json`, csl-json-v1; JOSE's `paper.bib` remains a legacy sync output, not a refs target | Quarto 1.10.18 with bundled Pandoc 3.10, default Chicago Manual of Style 18th edition (author-date) | 2026-09-26, refs 0.7.0 at 26b56cb (repository kind); publication adoption ba418b7, docs af6ce45, sources pass 2573802; 11 entries, all with files in the library under unfiled (six papers, five page captures); the four repositories cite version and release date current on the accessed date; render clean, only the five related-software entries changed wording |

## Findings by project

### 2026-jose-danvas — 2026-09-26, adopted after the case-protection fix

All eleven entries are cited in the current prose. One `jose-danvas` batch applied eleven new records, with no existing DOI bindings, conflicts or refusals. The six article PDFs were not found in the searched local stores; the five online records link to the project's shared literature-review note, with loc unset, but have no saved primary pages. Backup and linked-note hashes verified. Intake through both scratch exports took about three minutes; render and catalog verification took another three.

The initial CSL JSON render changed four protected software names: `canvaslms`, `nbgrader`, `Org-mode` and `canvas-cli`. The catalog retained their protection, but the identity exporter emitted metadata without it and reported no warning. The portable BibTeX comparison preserved the rendered facts, with five disclosed webpage-to-misc fallbacks. No workaround was applied; the first attempt stopped before changing the publication.

Candidates, not feature decisions: carrying case protection through CSL JSON prevents the four observed name changes; transferring ownership of JOSE's second export target prevents the sync script from overwriting a refs export. Multiple explicit destinations already work; the latter needs a script/workflow change and guarded adoption, not a new export engine. The [conversion report](../specs/001-academic-catalog/reviews/2026-09-26-jose-danvas-conversion.md) records every key, the comparisons, hashes and resumption boundary. The family document's earlier four passes remain in its own [pilot report](/Volumes/Casa/pub/2026-james-harvey-long/docs/refs-pilot-report.md) and the plan's ledger.

Resumed outcome: with title protection merged, both scratch comparisons pass for all eleven entries and the four names render unchanged. The Quarto paper's complete text differs only by `S0149` becoming `s0149` in one DOI; the portable BibTeX comparison adds only the five disclosed web-entry formatting differences. The adopted build matches the scratch candidate. `ba418b7` adds the generated JSON, bibliography-line switch and `.refs.toml`; `af6ce45` adds the source workflow and README/agent-instruction links. Nothing was re-imported or retired, and `paper.qmd` was unchanged. JOSE's `paper.bib` still comes byte-for-byte from `references.bib`; replacing the sync script's bibliography half remains a separate decision. The accepted export and rendered References are now fixtures linked in the register.

Sources pass (2026-09-26): the six article PDFs were already attached under `unfiled`; the five shared-review links are now removed and replaced with five primary captures, giving eleven verified attachments. Each repository capture bundles its commit-pinned README and GitHub metadata; Instructure has the API index HTML. All four repositories are software with kind `repository`, publisher GitHub, and version unset because the historical comparison names none. Source context retains relevant review facts and former accessed dates; current accessed dates are 2026-09-26. Backup validates, authors and titles are unchanged, and no catalog command refused. The scratch Chicago render changes the four software references and also adds Instructure’s requested container title; the other six references and the paper body are unchanged. The style’s bare “released” is disclosed. The [sources report](../specs/001-academic-catalog/reviews/2026-09-26-jose-danvas-sources.md) gives exact before/after wording and every final filename/hash. These changes remain catalog-only pending the owner’s pre-review timing decision; the project export, accepted fixture, prose, legacy bibliography and sync script are unchanged. No source is retired.

Sources pass, the same day (reviews/2026-09-26-jose-danvas-sources.md; publication commit 2573802): all six article PDFs fetched and moved into the library under `unfiled` by convention name, two of them through the owner's library access and one by hand because the host refuses scripted downloads; the four repositories retyped as software with the new `repository` kind, version and release date taken from PyPI and GitHub release history as of the accessed date rather than guessed; the project's literature-review note unlinked from the five web records, replaced by page captures at the current commit; the export re-adopted with the five related-software entries reading as software citations. Findings: a project's review note is not a source file; software citations need a version to render sensibly under Chicago, and the release current on the accessed date is a fact, not a guess; hosts that block scripted downloads are the norm for publishers, so step 3 is partly by hand.
