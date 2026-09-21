# Configuration and Everyday CLI: Review Draft

**Historical proposal notice, 2026-09-21:** Examples and earlier defaults below are source rationale. Audit sections 11–12 and the revised [feature contracts](../specs/001-academic-catalog/contracts/cli.md) supersede the single-home, mode/adopt, broad vocabulary and output-profile proposals. Follow the current [plan](../specs/001-academic-catalog/plan.md) for delivery slices.

**Feature status (2026-09-20):** This document retains source rationale and earlier review proposals. Current behavior is in the [clarified academic specification](../specs/001-academic-catalog/spec.md); implementation decisions are in its [plan](../specs/001-academic-catalog/plan.md) and [contracts](../specs/001-academic-catalog/contracts/cli.md). Later clarification answers supersede conflicting older defaults below.

**Status:** Proposed defaults for review, not implemented commands or newly accepted decisions.

**Current boundary:** Collect requirements and review proposals only. The [loose requirements](requirements-review.md) retain open choices from this walkthrough; writing feature specifications is outside this discussion.

**Context:** [Academic MVP](academic-mvp.md), [accepted behavior decisions](behavior-decisions.md), and [workflow research](workflow-research.md).

## 1. One Discoverable Home

Keep user preferences and authoritative data together. Resolve the home in this order: explicit `refs --home PATH`, `REFS_HOME`, `$XDG_CONFIG_HOME/refs` when that variable is set to an absolute path, then `~/.config/refs`. Reject invalid explicit locations rather than silently fall back. A project file cannot change the catalog location.

```text
~/.config/refs/
  config.toml
  catalog.sqlite
  .gitignore
```

`refs init` creates a new home deliberately and reports its paths; repeating it preserves existing preferences and data. Ordinary commands do not create a missing catalog. Initialization creates local Git exclusions for the database and SQLite sidecars without excluding them from system backups. Any later durable artifacts must appear in the path inventory. Rebuildable caches belong outside this backup unit.

```bash
refs init
refs paths
refs config show
refs config show --sources
refs config validate
```

`paths` reports the home, configuration, database, discovered project file, and resolved resource roots. `config show` displays effective settings; `--sources` explains where each came from. Unknown settings and invalid values produce actionable errors. Help and path inspection work before initialization. Configuration inspection does not run credential helpers.

## 2. Editable Preferences

The following is a proposed TOML vocabulary. Token names and preset definitions must become documented contracts before implementation. Presets are versioned so an application upgrade does not quietly change naming behavior.

```toml
[keys]
template = "{author}-{year}-{title}"
without_creator = "{title}-{year}"
missing_year = "ND"
title_words = 2
title_case = "lowerCamel"
stopwords = ["a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "with", "your"]

[titles]
policy = "english-title-case-v1"
protected_terms = ["AI", "GPT-4", "LaTeX", "PhD", "Python", "R", "nbgrader", "pH"]

[sorting]
ignore_leading_articles = ["a", "an", "the"]

[resources.roots]
papers = "/Users/djo/Box Sync/zotero"
vault = "/Volumes/Casa/obsidian/vault"

[export]
format = "biblatex"
```

These resource paths reflect observed locations, not installation defaults; initialization must not assume they exist on another machine. References store a root name plus relative path when explicitly linked through a root. Absolute links are also supported. A missing root is a reported unresolved link, never a reason to relocate files.

`author`, `year`, and `title` are derived tokens, not executable expressions. Author/editor fallback and collision allocation follow the accepted decisions. No eligible title words should require an explicit key in the first release, rather than invent an opaque fallback. An explicit key remains subject to validity and uniqueness checks. The complete stopword list above is a proposal; only the previously reviewed examples are accepted.

Title Case minor words are separate from key stopwords. Expose the resolved preset and configurable exceptions through `config show`; specify its punctuation and language behavior in fixtures. Changing preferences affects future operations. Reprocessing existing records requires an explicit previewed operation; assigned keys and manual overrides remain stable.

Keep credential-helper settings in trusted user configuration when a provider requires authentication. Project files cannot define executable helpers. The first academic slice needs no provider configuration merely to import, search, link, or export.

## 3. Small Project Files in the MVP

Recommend supporting just project selection and export defaults initially:

```toml
# .refs.toml in a paper directory
project = "paper-x"

[export]
format = "biblatex"
output = "references.bib"
```

Precedence for permitted settings is explicit command options, selected project file, user configuration, then built-in defaults. Resolve configuration paths relative to their declaring file and command-line paths relative to the working directory; expand a leading `~`, but do not evaluate shell expressions. Command arguments override settings only for that invocation.

Discover the nearest `.refs.toml` by walking from the working directory to the nearest Git worktree root, including that root. Outside a Git worktree, inspect the working directory only. Do not merge multiple ancestor files. `--project-file PATH` selects one explicitly, and `--no-project-config` disables discovery. These two options are mutually exclusive. An invalid discovered file is an error with its path, not an excuse to ignore it. `--project NAME` selects a catalog project without discovering another project's directory.

Project files cannot override the home, resource roots, credentials, or catalog key/normalization conventions. Reject unsupported project settings. The small whitelist should remain small; broader inheritance can wait. If even this discovery proves expensive, explicit flags remain a complete first-use workflow.

## 4. Everyday Walkthrough

All commands below are illustrative proposals. Examples reuse a historical key deliberately: imported keys remain unchanged even though new keys use hyphens.

### Bring in references and find a source

```bash
refs import library.bib --dry-run
refs import library.bib
refs search "turing trap"
refs show brynjolfsson2022turin
refs list --sort title
```

Import previews show proposed normalization, preserved keys, unmapped fields, duplicate candidates, and conflicts. An unresolved identity/key conflict blocks the import transaction in the MVP; do not silently accept a partial batch. Repeating an unchanged import is a no-op. Changed matching records require explicit reconciliation, not last-write-wins. The Zotero migration adapter needs its own verified route for attachments and metadata beyond the `.bib` file.

Initial search covers keys, titles, creators, identifiers, abstracts, and available catalog context. It does not claim to search PDF contents. Results show the key, title, creator/year, and matching context. `list --sort title` uses the separate sort title; search defaults to relevance. Neither command opens an interactive picker.

### Add or correct metadata

The user has selected agent-supplied metadata as the initial new-source workflow. An agent researches a source, checks for an existing catalog entry, submits new metadata or an explicit correction, and uses the returned key in the manuscript. Native identifier lookup is deferred. The commands below remain proposals; this workflow choice is accepted. Retain the source in the catalog even when it is not ultimately cited in the current paper.

```bash
refs add --json source.json --dry-run
refs add --json source.json
refs show brynjolfsson2022turin --json
refs update brynjolfsson2022turin --patch changes.json --if-revision 7 --dry-run
refs update brynjolfsson2022turin --patch changes.json --if-revision 7
```

Define one documented creation schema and a precise patch schema in the feature contract, including clearing fields and replacing creator lists. Previews explain generated keys and derived fields. A preview does not reserve a key; actual allocation occurs transactionally and is returned to the caller. A stale revision rejects an update without changes. Human-friendly field shortcuts can follow once the structured operations are settled.

### Link and open existing resources

**Subsequent requirement:** Adding a reference with a newly acquired file should also offer moving the file into the configured document library, avoiding stranded downloads. The link-in-place examples below remain useful but no longer cover the complete intake need. Whether moving is the configured default is unresolved. Hierarchical collections, one filing collection per managed attachment, and explicit managed-file reorganization are now agreed requirements; broad bulk consolidation and bulk renaming remain deferred. See [loose requirements](requirements-review.md).

```bash
refs resource add brynjolfsson2022turin --root papers --path "TheTuringTrap-2022.pdf"
refs resource add brynjolfsson2022turin --path "/path/to/existing note.md" --role note
refs resource list brynjolfsson2022turin
refs resource primary brynjolfsson2022turin RESOURCE_ID
refs open brynjolfsson2022turin
refs resource check
```

Linking leaves files and names unchanged; spaces in existing paths remain valid. Repeating the same resolved link is a no-op. `open` uses an explicitly selected primary resource, otherwise the sole PDF, otherwise the sole non-note file. Ambiguity returns choices with resource IDs, rather than guessing or opening several files. `open --resource RESOURCE_ID` selects a particular linked resource. Checks report unresolved roots and missing files without repairing or moving anything. These examples cover linked-in-place resources. Managed placement and explicit reorganization require a separate workflow; broad bulk consolidation and bulk renaming remain deferred.

### Select a bibliography and export deliberately

```bash
refs project create paper-x
refs project add paper-x brynjolfsson2022turin
refs project cite paper-x brynjolfsson2022turin
refs export --project paper-x --format biblatex --output references.bib --dry-run
refs export --project paper-x --format biblatex --output references.bib
```

`project add` means background membership; `project cite` marks bibliography inclusion and also adds membership when necessary. Both are idempotent. `project uncite` removes citation selection but retains background membership. Export includes only explicitly selected citations, in stable key order. A local `.refs.toml` can supply project, format, and output, reducing the command to `refs export` without changing its semantics.

Proposed overwrite rule: identical output is a no-op; a different existing file requires explicit `--replace` for that invocation. Always show the resolved output path and change summary in preview. Do not add a persistent overwrite permission or hidden ownership sidecar in the MVP. Before first replacing an existing manuscript bibliography, import and reconcile it and review the export difference. Subsequent scripts may deliberately use `--replace`. Write completed output atomically so a failed export does not leave a truncated bibliography.

There are no watchers or automatic exports. A catalog edit never writes a bibliography. Export validation reports citation-relevant missing fields; export must not manufacture dates, authors, or source types to satisfy a format.

### Back up and verify recovery

```bash
refs backup --output /path/to/backups/refs-snapshot.zip
refs --home /path/to/restore-check restore /path/to/backups/refs-snapshot.zip
refs --home /path/to/restore-check resource check
```

Backup packages a consistent SQLite snapshot, configuration, schema/format information, and external-resource inventory. Attachment contents are excluded and clearly reported as external backup responsibilities. Restore requires an empty destination and validates compatibility before writing. Existing filenames and root mappings are retained, with missing paths reported on a different machine. A snapshot stored beside the live catalog is local recovery, not independent protection.

## 5. CLI Contract Before Implementation

Provide concise human output by default and consistent `--json` results for agents, including stable source IDs, keys, revisions, warnings, and machine-readable errors. Never mix progress messages into JSON stdout. Define exact result schemas and exit codes in the feature specification. Read-only commands do not mutate the catalog or initialize it. Mutating operations validate before writing; `--dry-run` does not persist changes. No prompts in structured mode; conflicts explain the required explicit action.

Offline help should include examples and input schemas. A separate protocol server, interactive TUI, shell-completion framework, general plugin manager, and broad config inheritance are not prerequisites for the first working tool.

## Review and Promotion

The main proposed choices are the home-resolution order, a small project-file whitelist in the MVP, explicit per-invocation replacement of existing bibliography output, and the everyday command vocabulary. Review these before promoting this draft into the academic feature specification. This document is a review aid; after promotion, link to the executable contract rather than maintaining two versions of it.
