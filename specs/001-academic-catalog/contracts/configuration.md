# Configuration Contract v1

## Home and Project Selection

Resolve home in order: `--home`, `REFS_HOME`, absolute `$XDG_CONFIG_HOME/refs`, then `~/.config/refs`. Explicit empty/invalid values fail; they do not fall back. Relative invocation paths resolve against the working directory. A configured XDG root must be absolute. Resolve a leading `~` but do not evaluate shell expressions. Project configuration cannot change the home.

Within a Git worktree, discover the nearest `.refs.toml` while walking from the working directory through the worktree root inclusive. Recognize both a `.git` directory and worktree `.git` file. Outside a worktree, inspect only the working directory. `--project-file` selects one file explicitly; `--no-project-config` disables discovery. Do not merge ancestor files. Invalid selected files fail with their path.

For allowed project values: invocation > selected project file > user config > builtin defaults. Paths declared in files resolve relative to those files. The project whitelist is `project`, `export.format`, `export.output`. All other project keys fail. Environment changes only home selection in v1. Inspection reports each resolved value and its origin.

## User Configuration

```toml
schema_version = 1

[keys]
template = "{author}-{year}-{title}"
without_creator = "{title}-{year}"
missing_year = "ND"
title_words = 2
stopwords = ["a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "with", "your"]
transliteration_policy = "creator-unidecode-1.4.0-v1"

[keys.corporate_aliases]

[titles]
policy = "english-title-case-v1"
minor_words = ["a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as", "at", "by", "in", "of", "on", "per", "to", "up", "via"]
protected_terms = ["AI", "GPT-4", "LaTeX", "PhD", "Python", "R", "nbgrader", "pH"]

[sorting]
ignore_leading_articles = ["a", "an", "the"]

[resources]
intake = "move"

[resources.roots]

[export]
format = "biblatex"

[search]
implementation = "builtin.sqlite-fts5"
```

`resources.library_root` is an optional absolute/local path added by explicit setup or editing. No example personal path is installed as a default. Managed intake requires a usable root; metadata capture and link-in-place do not. `resources.intake` is `move|copy|link`; the accepted shipped default is move, and per-invocation selection wins. Root names are nonempty identifiers matching `[A-Za-z][A-Za-z0-9_-]*` with absolute path values. Corporate aliases map exact normalized literal creator names to explicit token strings.

Templates accept only the literal tokens `{author}`, `{year}`, `{title}` and literal separators; no attribute access, indexing, calls, conversions, format specifications, or executable expressions. Reject unknown/duplicate tokens and templates unable to produce a usable unique key. Missing-creator template cannot reference author. V1 supports `title_words=1|2`; the accepted default is two. Collision suffixing remains mandatory independently of template choices.

Unknown settings are errors. Lists are validated for nonempty strings and deduplicated case-insensitively; inspection returns the effective list. User-level policy lists are editable; assigned keys and explicit record overrides do not change. A changed preset implementation requires a new preset ID; config cannot silently select an unknown version. No credential-helper execution is defined for this provider-free feature.

## Project File

```toml
project = "paper-x"

[export]
format = "biblatex"
output = "references.bib"
```

A default does not itself export or create a project. Selected project must exist for project-dependent operations. Changing `export.output` does not transfer adoption authority to a new existing file.

## Collection Mapping and Files

A collection's safe path defaults to its root-to-leaf hierarchy beneath `resources.library_root`. A relative `folder_override` stored with that collection replaces the entire derived relative path for that collection, not other collections. `Unfiled` maps to literal `Unfiled`; no filing decision is required at acquisition.

Reject absolute overrides, `.`/`..`, empty components, NUL/control characters, separators inside a component, and any symlink traversal outside the root. Case/Unicode-equivalent destinations on the actual filesystem are treated as conflicts. Existing unsafe imported names remain valid catalog descriptions; require an explicit safe override only before managed placement. Two collections mapping to the same physical directory are rejected to keep filing unambiguous. Renaming/reparenting changes intended destinations only; explicit reorganization moves selected files.

Setup creates the home with private default permissions and excludes `catalog.sqlite`, sidecars, locks, staging data, and runtime artifacts from any local Git tracking. It does not modify a parent dotfiles repository's rules. Preferences can be deliberately tracked; Git exclusion is separate from backup responsibility. Config writes, if later added, must preserve deliberate comments or document their behavior; v1 edits are through the user's text editor and inspection validates them.
