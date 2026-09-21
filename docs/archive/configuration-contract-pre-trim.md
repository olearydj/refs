> Historical contract, superseded by the four current [contracts](../../specs/001-academic-catalog/plan.md#contracts), 2026-09-21.

# Configuration Contract v1

## Separate configuration and catalog selection

Resolve the configuration file as `--config`, then REFS_CONFIG, then ~/.config/refs/config.toml. Resolve catalog directory as `--catalog`, then REFS_CATALOG, then the selected config's catalog.path. An explicit invalid/empty value fails. There is no --home/REFS_HOME rule. `paths` and config inspection work before catalog initialization; ordinary catalog commands never create it implicitly or choose a fallback when Casa is unmounted.

The user's chosen defaults are /casa/refs/cat and /casa/refs/lib. Write their canonical forms /Volumes/Casa/refs/cat and /Volumes/Casa/refs/lib in configuration; these are distinct from the source tree /Volumes/Casa/dev/refs. Configuration lives in ~/.config/refs/config.toml. Initialization accepts explicit paths for disposable test catalogs and validates the selected volume before creation. It never creates a substitute volume mountpoint or an alternate catalog.

```toml
schema_version = 1
[catalog]
path = "/Volumes/Casa/refs/cat"
[resources]
library_root = "/Volumes/Casa/refs/lib"
intake = "copy"
[resources.roots]
library = "/Volumes/Casa/refs/lib"
[keys]
template = "{author}-{year}-{title}"
without_creator = "{title}-{year}"
missing_year = "ND"
title_words = 2
stopwords = ["a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "with", "your"]
transliteration_policy = "creator-latin-v1"
[keys.corporate_aliases]
[titles]
policy = "english-title-case-v1"
minor_words = ["a", "an", "the", "and", "but", "or", "nor", "for", "so", "yet", "as", "at", "by", "in", "of", "on", "per", "to", "up", "via"]
protected_terms = ["AI", "GPT-4", "LaTeX", "PhD", "Python", "R", "nbgrader", "pH"]
[sorting]
ignore_leading_articles = ["a", "an", "the"]
[search]
implementation = "builtin.sqlite-fts5"
[export]
profile = "portable-bibtex-v1"
```

Slice 1 supports copy and link only; move yields unsupported_in_slice, never substitutes an action. The accepted move default arrives in slice 2 with an explicit config upgrade notice; existing user choices remain intact. Root names match `[A-Za-z][A-Za-z0-9_-]*`; values are absolute local paths. library_root and roots.library must agree. Named additional roots can initially refer outside the library. Relative file-config paths resolve against the declaring file; invocation paths against the working directory. Expand leading ~ only, never shell expressions.

The agent needs write access to /Volumes/Casa/refs/cat and, for intake, /Volumes/Casa/refs/lib; ordinary config reads need no write grant. `home_not_writable` retains its stable diagnostic code but reports the catalog path and whether catalog/staging or library access failed. Configuration writes are explicit setup/editor operations, not normal capture side effects. The live catalog and staging must not be synced; only lib may be shared. Sync does not replace backup.

## Project configuration

Within a Git worktree, inspect the nearest .refs.toml from cwd through the worktree root, recognizing .git files and directories. Outside a worktree inspect cwd only. --project-file chooses one; --no-project-config disables discovery; they are mutually exclusive. Do not merge ancestors. Invalid selected configuration fails before mutation.

Allowed project keys are project, export.profile, export.output and export.consumers. Invocation overrides project values, then user values, then defaults. Project files cannot change catalog/config locations, roots, key/title policy or credential helpers.

```toml
project = "paper-x"
[export]
profile = "portable-bibtex-v1"
output = "references.bib"
consumers = ["citeproc", "biber", "bibtex:elsarticle-num"]
```

Declarations are stored with the destination profile fingerprint. Only portable is implemented in slice 1; other profiles fail explicitly. Consumer discovery is deferred and, when introduced, can suggest rather than silently set declarations. Empty/missing declarations use portable's supported baseline; exact style compatibility still requires the paper trial. Changing output paths never transfers adoption authority.

## Policies and folder mapping

Unknown keys fail with value/path/origin. Templates permit author/year/title tokens and literal separators only, with no executable expressions, duplicates or unknown tokens. without_creator cannot use author. title_words is 1 or 2. Policy lists contain nonblank strings and deduplicate case-insensitively. Corporate aliases map exact NFC literal names to explicit validated tokens. Changes affect future operations and never regenerate assigned keys.

Title Case capitalizes first/last words and words after an explicitly supplied subtitle boundary; configured minor words elsewhere stay lowercase. Hyphen parts follow their positions within the whole title. Per-title protected terms and preserve-case override normalization. Sort by casefolded sort title, numeric edition when known, issued year, then binary key; absent numeric values follow present values. Explicit sort overrides persist.

Slice 2 maps a collection's safe root-to-leaf hierarchy beneath library_root; a folder_override replaces its entire relative path. Unfiled maps to Unfiled. Reject escaping paths, unsafe components and physical collisions, including case/Unicode collisions. Renaming a collection changes intended destination only. Bulk filing assignment matches existing safe folder paths, previews ambiguities and creates requested collections only on explicit execution; it never moves a file.

## Repeat initialization and capability selection

Init against a ready compatible catalog with matching configured paths is a no-op preserving bytes and revisions. A nonempty unrecognized directory, mismatching catalog identity, incompatible schema or requested root change is init_conflict; init never overwrites/reconfigures it. An absent config can be created only by explicit init; an existing config is preserved, with conflicting requested settings reported. Partial initialization is not silently accepted as ready and needs explicit recovery or a different empty destination.

Search implementation is user-scoped and selects the built-in or an explicitly installed compatible refs.search.v1 entry point. Unknown/duplicate/incompatible providers fail. No provider is downloaded or given catalog-write authority; project config cannot select it. The independent alternative proof is required in slice 1 by the unchanged constitution.
