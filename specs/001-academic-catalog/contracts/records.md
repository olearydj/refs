# Record and Mutation Contract v1

This contract owns structured input semantics. CLI names and error envelopes are in [CLI](cli.md). Runtime models will emit JSON Schema through `refs schema`; the tables below are the design source until implementation creates those models.

## Bibliographic profile

The [bibliographic profile](bibliography.md) and [coverage registry](bibliographic-coverage.json) define the complete vocabulary, native namespaces, richer names/dates, and target mappings. This record envelope remains version 1.0 because it is a preimplementation revision, not a change to an installed API. `metadata.profile` defaults to `refs-bibliography-v1`; supplied unknown profiles are rejected. Profile identifiers and schema fingerprints are returned in complete records.

## Source Creation

```json
{
  "schema_version": "1.0",
  "citation_key": null,
  "key_author": null,
  "metadata": {
    "type": "article-journal",
    "title": "The Turing Trap",
    "language": "en",
    "creators": [{"role": "author", "family": "Smith", "given": "Alex"}],
    "issued": {"date_parts": [[2024]]},
    "identifiers": [],
    "legacy_tags": []
  },
  "context": [{"text": "Background for the paper", "origin": "user"}],
  "provenance": [{"origin": "agent", "source_url": "https://example.org/paper", "access": "metadata"}],
  "extra": {}
}
```

Unknown top-level keys and wrong primitive types are errors; no string-to-integer coercion. `schema_version` must be `1.0`. `metadata` is required with a nonblank title or nonblank absolute original URL; the documented traditional inbook case may instead supply container_title and chapter/pages with its native subtype. `citation_key` and `key_author` are optional strings or null; null means omitted at creation. Empty/unsupported generated title tokens require an explicit key; a bare URL is not fabricated into a bibliographic title. Structured input does not implicitly execute file or export operations; attachments enter through explicit CLI acquisition/link commands.

| Field | Type and validation |
| --- | --- |
| `metadata.type` | A pinned CSL source type; all types in the coverage registry are valid catalog classifications. `metadata.native_types` preserves narrower registered Zotero/BibLaTeX types as structured metadata. Unknown namespaced types are retained with explicit unsupported-output status. Shared `article` alone does not establish preprint status. |
| `title`, `main_title`, `subtitle`, `short_title`, `sort_title` | Unicode strings; title may be absent with original URL or the explicit traditional inbook part-record exception. Supplied short/sort titles are explicit overrides. Main/subtitle boundaries are supplied facts, never inferred from every colon. |
| `language` | Optional language tag; English normalization only for `en` or `en-*`. Absent/other tags preserve original casing and produce a normalization warning where relevant. |
| `original_url` | Optional absolute URI with `http` or `https` scheme; preserved without fetching. URL query/fragment are not stripped for identity. |
| `creators` | Ordered array. Each has role and optional registered role namespace, plus either nonempty literal or personal family/given with at least one nonempty component. Personal fields include dropping_particle, non_dropping_particle, suffix, comma_suffix, static_ordering, parse_names. Name-form mixing is invalid. All roles in the registered Zotero, CSL, and BibLaTeX vocabularies are representable. Core aliases author/editor/translator/book-author/series-editor/contributor remain valid. Unclassified prefix is not silently assigned a particle kind. |
| `issued`, `accessed`, `event_date`, `original_date`, `submitted`, `available_date` | Date object with optional date_parts (one or two year/month/day arrays), literal/raw text, season, circa. Validate supplied calendar values and range order; missing components are absent. Literal-only uncertainty is valid. A usable first issued year drives keys; otherwise ND. Source-specific dates retain their native role in registered extension fields. |
| `edition` | Optional positive integer interpretation of authoritative edition_statement text. Numeric-only input supplies the equivalent statement. Conflicting supplied interpretations fail. Literal editions such as “Revised and expanded” are valid; version and variant remain separate. Clearing/changing the statement clears a stale numeric interpretation. |
| `publication` | Optional textual container_title/container_subtitle/container_title_addon, multivolume_title/multivolume_subtitle/multivolume_title_addon, volume, issue, pages, article_number, series, series_number, number_of_pages, number_of_volumes, genre, jurisdiction, number, status; ordered string arrays publishers, publisher_places, original_publishers, original_publisher_places, institutions, organizations. Other recognized facts use citation_fields or registered native extension paths. No invented page range, hierarchy, or publication status. |
| `citation_fields`, `extensions` | Schema-validated recognized CSL fields and registered native namespace fields as defined in the coverage registry. Core-field duplicates are rejected. These fields support creation, inspection, patching and full export; target bibliography support is separately reported. |
| `identifiers` | Array of `{scheme,value}` strings. Preserve raw form. Normalize DOI prefix/case, ISBN separator/checksum representation, and PMID decimal form. ISBN-10/13 equivalence requires validated conversion; DOI/ISBN disagreement with known edition/type is a conflict. Unrecognized schemes use exact trimmed value with no guessed semantics. |
| `abstract` | Optional Unicode text; stored separately from authored context. |
| `legacy_tags` | Array of nonblank strings, deduplicated exactly; preserved metadata, not approved taxonomy. |
| `protected_terms` | Optional array of literal terms that take precedence over casing. |
| `native_fields` | Import-adapter-owned object with source format, original type, field expressions, protected groups, and unresolved dependencies. Ordinary creation may supply it only through explicit supported format ingestion; avoid treating arbitrary TeX as trusted executable content. |
| `context` | Array of `{text,origin}` with optional source URL; origin is user/agent/import. Does not establish full-text review. |
| `provenance` | Array of origin records with optional URL, observed time, source-system identity, and `access=metadata|abstract|full_text|unknown`. Preserve supplied claim; refs does not independently certify it. |
| `extra` | JSON object preserving explicitly namespaced extension fields. Never used to override core fields. |

Input strings preserve source spelling. Generated citation keys must be nonempty, have no whitespace/control characters or BibTeX delimiters `,{}()=\\#%"`, and be serializable without reinterpretation. Preserve imported assigned keys byte-for-byte as decoded text; incompatible export keys remain cataloged with an explicit error requiring user decision. Uniqueness is case-sensitive to preserve legacy distinctions; report a case-only collision warning because external tools may handle it differently.

## Patch Semantics

```json
{
  "schema_version": "1.0",
  "set": {"metadata.publication.pages": "12-19", "metadata.short_title": "Turing Trap"},
  "clear": ["metadata.sort_title"],
  "provenance": [{"origin": "user", "access": "metadata"}]
}
```

`update` requires `--if-revision N`. `set` maps documented mutable field paths to complete replacement values; arrays such as creators, identifiers, and tags are replaced as units. `clear` lists fields to remove. A path cannot be in both. Null in `set` is rejected; use `clear`. Paths cannot address IDs, revisions, citation keys, file paths, operation state, immutable import evidence, or array elements. Registered native type/field and citation-field paths are mutable under their profile validators. Setting type/native_types must keep their classifications consistent; no update silently deletes now-inapplicable metadata. Clearing a short/sort-title override restores derivation. Clearing the last recognizable title/URL or valid container-and-part identification is invalid. Provenance for changed fields is retained. No changed values yields unchanged revision and outcome.

`key set` and resource/project operations are separate from metadata patching. An explicit correction may replace a previously explicit field; an import or derived update cannot silently do so. The command always rechecks the expected revision at commit.

## Matching and Reconciliation

All evidence is checked before applying the precedence order. An explicit source UUID, prior origin identity, or consistent persistent identifier produces a candidate. If two signals identify different sources or conflict with type/edition facts, return all candidates and apply nothing to that entry. A citation key alone is a candidate for explicit matching; a title alone is never a merge instruction. DOI equality is not permission to overwrite a record.

```json
{
  "schema_version": "1.0",
  "decisions": [{
    "entry_id": "83a6e01b-d9d6-40d0-9fb0-e67c153f7051",
    "action": "match",
    "source_id": "a5b4de9b-2a59-440e-bc61-40a9b016d33c",
    "if_revision": 2,
    "fields": {"metadata.publication.pages": "incoming", "metadata.title": "current"}
  }]
}
```

Actions are `match`, `create_distinct`, or `leave_unresolved`. Match requires source ID, revision, and a decision for every conflicting field; unspecified nonconflicting fields can be retained but not silently replace different current values. `create_distinct` accepts a `citation_key` string, required and validated by the explicit-key grammar when the imported key is occupied, and must preserve the original key as provenance. Shared identifiers remain reported. `leave_unresolved` records the decision without discarding the entry and blocks initial bibliography adoption for that batch. Invalid decisions do not roll back unrelated valid entries; the report accounts for every decision. New unmatched records preserve supplied keys; missing keys use the generation policy.

## Key, Title, and Filename Transformations

The spec's accepted component order, literal author/editor role fallback, `ND`, camel case, and collision sequence are binding. Configuration lists and presets are in [configuration](configuration.md). Normalize creator input to NFC, apply explicit creator override/alias first, then strict pinned transliteration and lowercase/punctuation rules. Reject control/symbol or unmapped letter input and empty tokens. Show original and transformed name with policy ID; a mapping warning does not assert a person's canonical romanization. Transliteration never affects identity matching.

Title word selection uses Unicode letter/digit runs, excludes configured words case-insensitively, and takes the first two remaining words without truncation. Lowercase the first word; capitalize only the initial of the second and lowercase its rest. Unicode title words remain Unicode if the output format permits them; unsupported export cases require an explicit key. This name-transliteration decision does not authorize inventing an English title.

Generated filenames join whitespace-separated short-title words preserving their existing spelling, then optional edition/version, then available issued year, using hyphens between components and the requested extension. Missing year uses `ND`; no edition/version adds no empty component. Reject path separators, control characters, empty basename, or unsafe resulting names rather than silently sanitize. Filename preview never renames an attachment. Both numbering and version labels cannot be compressed into one token without an explicit selected label; report ambiguity.
