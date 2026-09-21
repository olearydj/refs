# Feature Specification: Academic Catalog, Slice 1

Created 2026-09-20. Rewritten in plain language 2026-09-21; scope unchanged from the owner-approved trim in commit b10db29. Branch: main. Status: design only. No tasks and no application code exist yet.

## What slice 1 delivers

refs is a personal, offline catalog of references with a command-line interface that coding agents and the owner both use. Slice 1 is the first usable version. With it the owner can:

- save a reference that an agent has researched, and correct it later;
- find a saved reference by key, identifier, or words;
- mark references as cited in a paper and export that paper's bibliography as a `.bib` file, only when asked;
- import a paper's existing `.bib` file without losing or overwriting anything;
- link a PDF where it already sits, or copy it into the library folder with a tidy name;
- take a snapshot of the catalog and prove that it restores.

This document covers slice 1 only. The [plan](plan.md) lists what comes later without designing it. No specification work for slice 2 starts until slice 1 has been used on one real paper.

## Authority

The [constitution, version 2.0.0](../../.specify/memory/constitution.md), the [accepted conventions](../../docs/behavior-decisions.md), and the owner's recorded decisions decide what refs must do. The four contracts linked from the plan are implementation proposals: they make these requirements testable, and their exact syntax and algorithms are not owner decisions. Requirement numbers are the ones this feature has always used, so history in Git stays traceable. Numbers that belong to later slices are listed near the end.

## Words used here

- Source: one saved reference, such as an article, a book, or a web page. It has a permanent internal ID.
- Citation key: the short name used to cite a source in a manuscript, for example `smith-2024-turingTrap`.
- Original entry: the exact text or JSON that a source was imported or submitted from, kept unchanged as evidence.
- Revision: a counter on each source that goes up with every change. An edit must say which revision it was based on, so two agents cannot silently overwrite each other.
- Library: the folder `/Volumes/Casa/refs/lib`, where refs keeps copies of files it has been asked to take in. `Unfiled` is the folder inside it where new copies go in this slice.
- Managed and linked: a file stored inside the library is managed by refs. A file anywhere else is linked: refs records where it is and never moves, renames, or deletes it.
- Catalog: the SQLite database in `/Volumes/Casa/refs/cat`. Configuration lives separately in `~/.config/refs/config.toml`.
- Project: a paper or other piece of writing. In this slice a project is simply the set of sources cited in it.
- Portable bibliography: a `.bib` file written in the traditional BibTeX dialect, which Pandoc, Biber, and classic BibTeX can all read.

## Clarifications

The [audit sections 11–14](reviews/2026-09-20-independent-design-audit.md#11-addendum-2026-09-21-user-decisions-on-the-open-items) preserve questions, options, literal replies and interpretations separately. In particular:

| Question/topic | Literal owner reply | Interpretation applied here |
| --- | --- | --- |
| Metadata breadth | “A: What I use (Recommended)” | Bounded CSL-shaped authority, justified extensions and verbatim originals. |
| Notes | “B: Fold into context (Recommended)” | Later Zotero migration imports child notes into context, not a supporting-item subsystem. |
| Export failure | “A: Block, with override (Recommended)” | Four classes; unknown override retained, stored loss waivers deferred by the trim. |
| First slice | “B: Core + copy-only intake (Recommended)” | Core, non-destructive copy, demonstrated restore. |
| Ownership | “B: Derive mode from location (Recommended)” | Named library-root files are managed; others linked. |
| Title case | “A, with a clarification. APA etc should govern exported material. My prefs for internal representation do not superceed that. I just don't want to see sentence case titles in the database. They are an abomination.” | Internal Title Case, protected terms, style-governed output. |
| Profile | “A: Portable default, richer by declaration (Recommended)” | Only portable BibTeX ships now. |
| Transliteration | “C: No dependency (Recommended)” | Built-in Latin normalization/table, otherwise explicit override. |
| Locations | “A, but /casa/refs/cat and /casa/refs/lib” | Separate configuration, catalog and library. Full clarification is in audit §12. |
| Constitution | “proceed with 1-3” | Applied v2.0.0; no pending amendment gate. |
| Background project membership | “No, cited only for now (Recommended)” | A project's sources are its citations; keep a cited column as a future seam. |
| Rename on intake | “Rename by default” | New copy intake renames by convention unless --keep-name; linked files and later reorganize keep names. |
| Trim | “I'm satisfied with changes based on my answers” | The keep/fold/defer list in audit §14 supersedes earlier delivery commitments. |

In the first clarification session the owner answered five multiple-choice questions with the letters `b`, `a`, `a`, `b`, and the sentence `a - use a library / package if something small and proven exists and is beneficial. seems like this could be more problematic than it seems on face`. Those letters chose: move a newly downloaded file into the library by default; put it in `Unfiled` when no collection is chosen; import the entries that have no conflicts and report the rest; let an explicit export replace a bibliography that refs wrote earlier and that nobody has edited since; and handle accented names with care. Moving files arrives in slice 2; until then the closest safe equivalent, copying, is used. The later no-dependency decision settled name handling. Keeping existing citation keys unchanged comes from constitution principle I, not from a quoted owner statement.

## User stories and acceptance

| Story | Priority | How to tell it works, on its own |
| --- | --- | --- |
| US1 Keep and find references | P1 | Starting with an empty catalog, add one complete and one incomplete reference, correct a field, search for both, and read back their keys, with no project and no network service. A correction based on an out-of-date revision is refused. |
| US2 Use a bibliography in one paper | P1 | Create a project, cite and uncite sources, export, and render the paper while the catalog is unavailable. Editing the catalog afterwards leaves the exported file untouched until the next export. |
| US3 Import an existing bibliography | P2 | Import a prepared `.bib` file that contains clean entries, a conflict, and a malformed entry. Every original is kept, the conflict and the malformed entry are reported, importing again creates no duplicates, and an ordinary update settles the conflict. The input file is never changed. |
| US4 Keep research files | P2 | Link one file without touching it. Copy another into `Unfiled` and see it renamed by the convention. Try the keep-name option, a name collision, a source file that changes during the copy, and an interrupted copy. The original file survives every case. |
| US5 Recover the catalog | P2 | Take a snapshot, restore it into a second, empty location, open it, and compare IDs, keys, corrections, projects, and the list of files. The snapshot says plainly that the PDFs themselves are not inside it. |
| US6 See the settings in force | P2 | Show the configuration, catalog, and library locations and every effective setting, even before the catalog exists. An invalid project setting is rejected. If the Casa volume is not mounted, refs reports that and does not create a catalog somewhere else. |

## Functional requirements

### Saving references and naming them

- FR-001: An agent or the owner can create a source, read it back, and correct it. Input may be refs' own JSON, CSL-JSON, or a single BibTeX entry. A source needs only a recognizable title, a web address, or the title of the book or journal it is part of plus a chapter or page reference. Tags, files, projects, and complete metadata are optional.
- FR-002: refs keeps what it is given: the type of work, contributors in order with their roles, organizations as authors, title and subtitle, dates exactly as precise as supplied, edition and version, identifiers such as DOI and ISBN, publication details, abstract, and keywords from imports. Anything refs has no field for stays readable in the original entry. refs never fills in a fact that was not supplied.
- FR-003: Every source has a permanent ID and a unique citation key. Every command that creates or changes a source says whether it was created, was already present, or needs attention, and returns the ID and key. When a new submission looks like an existing source, refs reports the likely match instead of creating a duplicate or merging the two.
- FR-004: A citation key never changes because of an edit, an import, or a changed preference, and neither does the name of a linked file. Changing a key is a separate, explicit command that first shows the old and new key and warns that manuscripts citing the old key are not updated.
- FR-005: refs can tell apart a value that came from an import, a value it derived (such as a sort title), and a value a person corrected on purpose. It also records what the supplier of a reference actually saw: only the metadata, the abstract, or the full text. Complete metadata never implies that anyone read the work.
- FR-006: A new citation key is the first author's family name in lower case, the year, and the first two meaningful words of the short title in lower camel case, joined by hyphens: `smith-2024-turingTrap`. With no author the first editor is used. With neither, the title words come first and the year second: `turingTrap-2024`. A missing year is written `ND`. One meaningful title word is enough.
- FR-007: Small words on a configurable list are skipped when choosing title words. If a new key already exists, the new source gets the next free suffix, `-a` to `-z`, then `-aa` and so on; existing keys never change. The owner can always supply a key, or a name to use for the author part. Accents are removed using Python's built-in Unicode handling plus a short refs-owned table for letters such as `ß`, `ø`, and `ł`. A name in any other script is not guessed at; refs asks for an override. Two different names that produce the same key part are still two different sources. Changing these rules later never alters a key already assigned.
- FR-008: Titles are stored in Title Case as ordinary text. Each title can carry a list of terms whose capitalization must be kept, such as `Python` or `Alabama`, and a flag meaning "keep this whole title exactly as written". On import both are taken from the braces BibTeX uses to protect capitals; braces that only wrap an accent or a LaTeX command are not treated as protection. The citation style decides how titles look in a rendered paper; refs only writes the `.bib` file so that the style can do that correctly. A title that is not in English needs its language recorded before export. A capitalized word in the middle of a title that is not protected produces a warning.
- FR-009: A short title that was supplied is kept. Otherwise refs uses the main title when the split between title and subtitle was given explicitly, and the full title when it was not. It never splits at a colon on its own and never invents an abbreviation.
- FR-010: An ordinary numbered edition is stored as a number and shown as `2nd ed.`, or `2E` in a filename. Version labels such as `v1.2.4` and unclear shorthand such as `P1E` are kept exactly as written and are never reinterpreted.
- FR-011: Lists sorted by title ignore a leading `A`, `An`, or `The`. The title as shown and cited is unchanged. A sort title set by hand stays until it is cleared.
- FR-012: When refs copies a file into the library it names the copy from the short title, the edition or version if any, and the year, with no spaces: `PracticalVim-2E-2015.pdf`. The `--keep-name` option keeps the original name. If the source has no short title or no year, the original name is kept and refs says so. Linked files are never renamed.

### Working with agents

- FR-013: Every operation is a command that prints readable text by default and one JSON object when asked. Commands never stop to ask a question. Errors say what went wrong and what to do next. `refs schema` prints the JSON Schema for the input and output formats, with no network access.
- FR-014: Input is checked before anything is changed. `--dry-run` shows what would happen and changes nothing. An edit based on an out-of-date revision is refused. When a command completes only part of its work, for example the reference was saved and the file copy failed, the result says exactly which part succeeded.
- FR-015: A source can be found by its exact key or identifier, or by words in its title, contributors, abstract, saved notes, or imported keywords. Each result shows the key, enough description to recognize the source, and which field matched.
- FR-016: Sources can be listed for one project and ordered by title or by key.
- FR-017: Everything in this slice works with no network, no model service, and no credentials. Commands that only read never create or change a catalog.

### Importing a bibliography

- FR-018: refs imports `.bib` files, whether they use traditional BibTeX field names (`journal`, `year`, `address`, `school`) or BibLaTeX ones. The exact text of every entry is kept as its original entry. The imported file is never modified.
- FR-019: Importing with `--dry-run` shows, entry by entry, the key that will be kept, how the title will be normalized, possible matches with existing sources, conflicts, and anything refs cannot represent. A type of entry that refs does not support is reported as such and is not quietly turned into a different type.
- FR-020: refs decides that an incoming entry is an existing source only from real evidence, such as the same DOI or ISBN. A similar title is never enough. If the evidence is contradictory, for example the same key with a different DOI, that entry is not applied and the report explains the decision the owner needs to make.
- FR-021: Importing the same file again creates no duplicate sources or file links. An import never overwrites a value already in the catalog, including a value a person corrected or deliberately cleared. To accept an incoming value, the owner runs an ordinary update. If a bibliography that refs itself exported is imported again, an entry that was simplified on the way out, such as a web page written as `@misc`, may be reported as a conflict; the catalog's richer value is kept.
- FR-022: Keywords in an imported entry are kept as imported tags. File paths in an entry become links to those files where they are. An import never assigns sources to a project.
- FR-024: Entries without conflicts are imported straight away. Entries with conflicts and malformed entries are kept as originals, reported with reasons, and left unapplied. The report accounts for every entry in the file, and a partly applied import is reported as partial, not as success. refs records each import run with the file's digest and the counts. After an interruption, importing the same file again is safe.

### Files

- FR-025: A source can have several files of any type, each with a label. A file's location is recorded either as a full path or as a named folder plus a relative path, so that a whole folder can be relocated later by changing one setting.
- FR-026: refs shows where each file is and whether it can currently be found. Removing a file's link removes only the catalog record. A missing file or folder is reported and nothing is moved or deleted in response.
- FR-027: `refs open` opens a source's only file, or a file chosen explicitly. When there are several and none was chosen, it lists them instead of guessing. Files are opened in their usual application and never modified.
- FR-030: In this slice every copy goes into the library's `Unfiled` folder, with no filing decision required.
- FR-031: A file is either linked where it is or copied into the library. A file supplied together with a new reference is copied into the library by default, which is the slice 1 form of the owner's choice to bring new downloads into the library; an option links it in place instead. Adding a file to an existing source links it by default, and an option copies it in. Before a copy, refs shows the destination and the new name. If the library is not set up or cannot be reached, the command fails and the original file is untouched.
- FR-032: A file inside the library is managed. A file anywhere else is linked, and refs never moves, renames, or deletes it. Changing where a named folder points never moves a file.
- FR-033: A copy is checked against the original before it counts. refs never overwrites an existing file, and if the original changes while it is being copied the copy is abandoned. The original is kept in every case. If refs is interrupted after a copy is complete and before the catalog records it, the finished copy stays in place; refs reports it and never deletes it, and the owner can link it to the source.
- FR-034: Something made of several files, such as a saved web page with its folder of images, is linked where it is and not copied in this slice.
- FR-035: Removing a source first shows what is attached to it and requires explicit confirmation on the command line. Removal never deletes a file and never changes an exported bibliography. The removed source's key stays reserved. `refs reactivate` brings a removed source back with the same ID and key. An import never brings a removed source back on its own.

### Projects, export, and recovery

- FR-036: The project commands are create, show, cite, and uncite. `project show` with no name lists all projects. Citing a source twice, or unciting one that is not cited, changes nothing. The catalog keeps room for a "related but not cited" kind of membership later without any change to existing data.
- FR-037: An export contains every source cited in the project exactly once, under its assigned key, in the portable dialect. The same catalog contents and settings always produce the same bytes. The file works on its own; the manuscript does not need the catalog.
- FR-038: refs writes a bibliography only when the export command is run, by the owner, a script, or an agent. Nothing else ever triggers a write. A file refs has not written before is replaced only if that exact file was imported first, its conflicts have been shown, and the owner passes both `--adopt` and `--overwrite`. After that, an export replaces the file without extra options as long as nobody has edited it outside refs. If somebody has, the export stops and says so; `--overwrite` replaces it anyway, and refs keeps a copy of the text it replaced. A failed or blocked export leaves the existing file exactly as it was.
- FR-039: Before writing, an export reports every entry that does not map cleanly, in four classes. A reference with facts missing, written faithfully: warning. A documented simplification, such as a web page written as `@misc`: warning, and the report records it. A change on a fixed list of changes that alter what a citation says, such as losing an author or the publication date: the export is blocked. A mapping nobody has assessed: blocked, unless `--allow-unknown-mappings` is passed for that one run. That option never overrides a blocking change or an invalid file. Two keys that differ only in upper and lower case are an error, because classic BibTeX treats them as the same key.
- FR-040: `refs backup` writes a consistent snapshot of the catalog, the configuration, and a list of every file the catalog refers to. The snapshot states that the files themselves are not inside it. A backup of links is not a backup of files.
- FR-041: Slice 1 is accepted only after a snapshot has been restored into a second, empty location by the documented procedure and opened there. A damaged snapshot, an unsupported catalog version, and a destination that is not empty are all refused. A file that cannot be found after a restore is reported, and nothing is moved or deleted.
- FR-043: `refs paths` and `refs config show` display the configuration file, the catalog, the library, and every effective setting with where it came from. Both work before the catalog exists, and `config show` reports invalid settings.
- FR-044: Setting up a catalog is an explicit command, and running it again never overwrites anything. If the chosen catalog location is missing, for example because the volume is not mounted, refs reports that and never starts a catalog elsewhere. If the location cannot be written to, which is normal for a sandboxed agent, the error names the exact path that needs write access. The catalog and its working files are never placed in a folder that a sync service copies.
- FR-045: A small `.refs.toml` file in a paper's folder may name the project and the export's output file and options. It cannot change the catalog location, the library, or the naming rules.
- FR-046: An unknown or invalid setting is reported, with the file it came from, before anything is changed. Changed preferences apply from then on; keys, filenames, and hand-made corrections already in the catalog stay as they are.
- FR-047: Every bibliographic fact has exactly one place where it is stored and edited, in a structure shaped like CSL-JSON, whichever route it arrived by. A source may also carry a label with its more specific original type, such as a Zotero or BibLaTeX type. Four extra fields exist because CSL has no place for them: a patent's assignees, its application number, its priority date, and a journal's series. Everything else from an import remains readable in the original entry.
- FR-048: Each supported field mapping states which input format and which type of entry it applies to, the field it reads, how the value is transformed, what happens on a conflict, how it is written in the portable bibliography, and the test that proves it. The same reference entered by different routes must end up as the same record. A correction or a deliberately cleared field always wins over the original entry.

## Deferred identifiers

These requirement numbers belong to later slices and are not part of slice 1: FR-023 and FR-049 (Zotero migration, including notes and related items), FR-028 and FR-029 (collections), FR-042 (a complete export of the library in an open format), and the parts of FR-018, FR-022, FR-030 to FR-034, FR-040, and FR-041 that concern Zotero, collections, moving files, and a restore command. Their earlier text is in Git commit 4209e5d. The [plan](plan.md#deferred-work) keeps the list of deferred work.

## Success criteria

- SC-001: On one active paper chosen by the owner, the whole loop works without opening Zotero: save, find, correct, open a file, cite, and export.
- SC-002: A representative `.bib` test file is imported with every key kept, every supplied field either stored or readable in its original entry, and every entry accounted for in the report.
- SC-003: Importing the same file twice creates no duplicates and overwrites nothing. Every deliberate conflict in the test file is reported. Malformed entries that are known to confuse the parser are reported and do no damage.
- SC-004: Every agreed example of key, title, edition, and filename behavior produces its stated result, including missing authors and years, protected terms, accented names, names needing an override, and collisions. Two agents adding sources at the same moment receive different keys.
- SC-005: A prepared set of lookups by key, identifier, title, contributor, abstract, and saved note each finds the intended source and shows which field matched.
- SC-006: The exported test bibliography is rendered through Pandoc, Biber, and classic BibTeX with the `elsarticle-num` style, and each shows the right authors, dates, journal or institution, edition, and protected spelling. It contains no source that was not cited, is identical byte for byte when exported twice, and renders without the catalog. A blocked export and a file edited outside refs are both left intact.
- SC-007: In the collision, changed-source, and interrupted-copy tests the original file always survives and no existing file is overwritten. Links that succeeded resolve. Editing metadata, changing projects, and removing sources change no file.
- SC-008: A snapshot restored into a second location has the same IDs, keys, original entries, corrections, project citations, and file links as the catalog it came from.
- SC-009: Every slice 1 command works offline. Invalid settings and out-of-date edits fail with a message that says what to do, and nothing is changed.
- SC-010: Every supported mapping passes tests that would fail if the mapping were wrong: an input that distinguishes it from its neighbours, two inputs that disagree, an edit, a cleared field, and the exported result. Agent-submitted JSON is one of the routes compared. A list of field names, or a file that merely parses, is never accepted as proof.

## Assumptions and limits

- A-04: How the configuration file, the catalog location, and a project's `.refs.toml` take precedence over one another is defined in the [CLI and configuration contract](contracts/cli.md).
- A-12: Agents may submit CSL-JSON now. Writing CSL-JSON, and writing Zotero's JSON format, are on the backlog.

This is a design, not software that has passed these criteria. Nothing here authorizes migrating the real Zotero library, moving or renaming real files, or replacing a real manuscript's bibliography. The owner chooses the paper for the first trial. refs is designed to survive being interrupted or killed at any moment on a local disk; protection against sudden power loss is best effort and its limits are stated in the [files and recovery contract](contracts/files-and-recovery.md).
