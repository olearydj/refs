# Converting a project to refs

How an existing writing project moves its bibliography into the catalog and takes its reference list back as an export. Written from the family-document pilot and the inventory of 2026-09-26, before the first academic conversion; the findings section at the end grows by one entry per project. Governing rules are in the contracts; this page is the working order.

## When a project qualifies

It has a bibliography file it builds from, kept by hand or by an agent, and the file is not an export from Zotero already in the catalog. The inventory review lists the candidates. A project in the middle of a submission still qualifies, because nothing here changes the project until the export is proven identical in meaning.

## The order

1. **Backup.** `refs backup --output /Volumes/Casa/refs-backups/<date>-before-<project>`. Check the manifest validates.

2. **Inventory the project.** Name every bibliography file, who writes it, and every consumer: a Quarto or pandoc build, a LaTeX build with biber or natbib, a venue that demands a `.bib`, a site build, a sync script. Note the citation-key style, since keys must not change. Record which entries the prose cites, so the export can be cited-only later without dropping anything the text uses.

3. **Find the sources.** Every record should end up connected to the thing it describes: the PDF of a paper, the saved page, the scan, the note. Look in the project folder and its figures, the vault project if there is one, the Zotero archive library at `/Volumes/Casa/refs/lib` for papers already in the catalog, DEVONthink exports and `~/Downloads` for papers read but never filed. Match by DOI first, then by title. List what was found, what was not, and what is only a URL, and treat a missing file as a fact to record, not a reason to stop.

4. **Import.** `refs import --format bib --input references.bib` (or `--format csljson`) with the project named as origin. Read every outcome: applied is new, unchanged is already there, conflict means the catalog holds a different value for a bound source and both are kept for `import reconcile`, invalid names a limit and preserves the entry. Nothing is guessed; a refusal is recorded, not worked around. Where a DOI binds an entry to a source the Zotero import created, the conflict list is the interesting part: it shows where the agent's hand-written entry and the library disagree.

5. **Create and cite the project.** `refs project create <name>` and `refs project cite <name> KEY` for every entry the prose cites, plus the ones the bibliography carries uncited if the owner wants them kept. The export is cited-only, so this list is the reference list.

6. **Files.** The library is for the owner's copies of published work: a paper's PDF is copied in, `add --file --copy` or `resource add --copy`, under a loc the owner names, and the original stays where it was. Raw research material that belongs to a project's own store, such as the vault's scans and captures, stays there and is linked in place with loc left empty; the family document is the example. A source with a scan and a transcription gets two resources with labels.

7. **Export per consumer.** Export to a scratch path first, never over the project's file. A pandoc or Quarto consumer takes `--profile csl-json-v1`, the identity mapping; a LaTeX build or a venue that wants BibTeX takes `--profile portable-bibtex-v1`. Render the project from the scratch export and diff its reference list against the current render, entry by entry. Restructured wording is not a finding; a lost or altered fact is, and it is fixed in the catalog record or reported as a limit before anything is switched. Only then: export to the project's path, change the one bibliography line in the build configuration, write `.refs.toml` with the project and target, and commit those together, separately from any content change.

8. **Retire the hand-kept file** once nothing reads it, in the same commit as the reader's switch, never before.

9. **Document in the project.** A short `docs/refs.md` in the project: the catalog is the master, the export is generated and never edited, how to add and cite a source, how to re-export, and the checks after every export. Point to it from the project's README and agent instructions.

10. **Record findings here.** What refused, what mapped lossily, what needed a workaround, what surprised, and which incident each candidate change would prevent, in the section below. Feature decisions go to the plan's ledger, not to this page.

## Checks

The catalog backup validates; the import's counts sum to the file's entry count and every invalid entry has a named reason; the project's cited count equals the reference list the prose needs; each linked or copied file's hash matches the original; the rendered reference list from the scratch export loses no fact; the build passes after the switch; the project's docs name the export and the re-export command.

## Boundaries

Prose is never edited for a conversion. Citation keys never change. Nothing under a project's own source store is moved. A refusal is disclosed, not patched around. A conversion adds no feature to refs; it produces evidence.

## Findings by project

None yet. The family document's four passes are recorded in its own [pilot report](/Volumes/Casa/pub/2026-james-harvey-long/docs/refs-pilot-report.md) and in the plan's ledger.
