# Search Capability Contract v1

This is the first bounded capability-replacement contract. It does not introduce a general plugin manager, remote provider, or background indexing service.

## Selection and Authority

User configuration `search.implementation` defaults to `builtin.sqlite-fts5`. Explicitly selected installed packages may register an entry point in `refs.search.v1`; discovery uses package metadata and loads only the selected implementation. Duplicate names, unsupported contract versions, missing dependencies, or incompatible capabilities produce a configuration error. A project cannot override provider selection. No packages are downloaded automatically.

External packages are explicitly installed trusted local code, not sandboxed untrusted code. The interface grants no catalog-write API, network requirement, credential helper, or file relocation permission. Runtime catalog invariants still validate all returned source IDs/revisions. New provider installation/configuration may require restarting the command process; no hot-swapping is promised.

## Application-Owned Interface

`SearchProviderV1` declares `name`, `version`, `contract_version="1"`, and supported operations. Its bounded operations are `search(query, projection_reader, limit, offset)` and optional explicit `rebuild(projection_reader)`. A projection reader exposes immutable source ID/revision, title, creator text, abstracts, context, legacy tags, and eligible source IDs derived from catalog-owned project/collection filters. It does not expose SQL write connections or external PDF contents.

The application resolves exact source keys/identifiers and validates filters before provider search. The default provider uses the FTS5 projection maintained by catalog transactions; external providers can read the same projection through bounded iteration. Each result has source ID, source revision, matching field, excerpt, and optional provider score. Scores are not probabilities and need not be comparable across implementations. Unknown IDs, stale revisions, or evidence outside permitted fields are discarded with an explicit warning/error rather than presented as current evidence.

Queries are literal user text, not raw SQL or FTS expressions. The built-in default uses quoted token matching with AND semantics; case folding and accent-insensitive lexical behavior are documented in its tokenizer profile. Quotes in user input do not become executable syntax. Empty input is an error for `search`; `list` supplies browsing. Provider results must respect the eligible set, then stable tie-breaking by source key. A provider missing a required operation/filter cannot silently weaken the query; catalog filtering is always enforced.

## Replacement Proof

Implementation creates a small separate distribution under `tests/fixtures/search_plugin/` that registers a literal lexical implementation over the same read-only projection. Its test corpus contains matching and nonmatching sources, project/collection exclusions, and no-tag records. Install it in an isolated test environment, select it, run the same contract cases, and verify identities, manual corrections, associations, and source data remain unchanged. This proves adding/selecting an implementation without modifying the built core wheel. No second production engine or benchmark-equivalence claim is required.

Import/export adapters similarly translate external values into application-owned records/errors and preserve provenance. Their installation/discovery mechanisms remain internal until a real external alternative is introduced. The deferred search/model capabilities will require their own evidence and contracts; this feature does not force them through a generic text-generation interface.
