# Record and Mutation Contract v1

**Status:** Slice 1 record contract with slice 2 import additions. The result envelope remains version 1.0. The [registry](bibliographic-coverage.json) and [bibliography contract](bibliography.md) own the bounded bibliographic profile.

## Creation and canonical ownership

```json
{
  "schema_version": "1.0",
  "citation_key": null,
  "key_author": null,
  "metadata": {
    "type": "article-journal",
    "title": "Learning With Python",
    "author": [{"family": "Example", "given": "Alex"}],
    "issued": {"date-parts": [[2024]]},
    "language": "en"
  },
  "title_protection": {"title": {"protected_terms": ["Python"], "preserve_case": false}},
  "native_type": null,
  "extensions": {},
  "context": [{"text": "Background for the paper", "origin": "agent"}],
  "provenance": [{"origin": "agent", "access": "metadata", "source_url": "https://example.org/paper"}]
}
```

Unknown envelope keys and wrong primitive types fail; no general string-to-number coercion. Creation needs a nonblank title or absolute HTTP(S) URL, or a container-title plus page or chapter-number identification for a traditional title-less part. It needs no tags, project or file. Generic casually captured records may use type document; unknown explicitly supplied types remain unapplied originals with a diagnostic. Generated keys require usable title tokens or an explicit key. URLs are not invented into titles. During Bib import, an invalid or relative URL remains in the original with a limitation; other usable metadata is applied.

`metadata` is the sole authority for bibliographic variables in the pinned CSL schema. No parallel creators, identifiers, publication object, citation_fields or editable native-fields namespace exists. Creator arrays use CSL roles and ordered personal/literal names. Standard identifiers occupy DOI/ISBN/ISSN/PMID/PMCID; normalized lookup indexes are derived. The fifth registered extension, `extensions.identifiers`, stores schemes `arxiv` and `oclc`; exact-value search supports both. Other schemes remain original evidence unless already modeled. Native type is optional `{namespace,value}`, validated against the type crosswalk; it cannot contradict the canonical type. Origin-system identity belongs to provenance, not this label.

Dates use `date-parts`, `literal`, `season`, `circa` where supported by the pinned schema. Validate calendar values and range order; never invent January 1. Free-text Zotero dates remain in originals; API `meta.parsedDate` is an aid, not another authority. Structured dates must agree with reliable explicit components; contradictions are reported without applying the entry. Unparseable dates remain literal with a precision warning. Bib date and year/month must agree at their overlapping precision. Month macros jan–dec are supported; other macros/inheritance need explicit preprocessing and preserved provenance. Complex uncertain/open dates remain literal until a tested target mapping exists.

Edition is one CSL-compatible string or positive integer. An unambiguous decimal edition becomes an integer; descriptive text remains text. Numeric display/filename interpretations are derived, never independently editable edition statements. Version is separate. CSL variables remain valid when the source type changes. Type-specific extensions and native labels must remain compatible; originals cannot restore cleared values.

Name forms are either literal or personal with family/given and optional dropping-particle, non-dropping-particle, suffix and strict boolean flags. They cannot mix literal and personal properties. BibTeX's explicit von part defaults to dropping-particle with preview and override; Zotero's unsplit lastName is not split by guessing lowercase words. Such structural differences remain visible as import conflicts. A fully grouped corporate author containing “ and ” stays one literal. Native inventor/presenter/programmer map to citation author only on their corresponding types; native role survives as provenance. Key generation uses the first name in the source's author list, then the first editor, then the title and year, for every type. key_author still overrides. Native roles such as inventor, presenter and programmer remain provenance and do not affect keys. Presentation overrides such as shortauthor/sortname are not contributor roles.

A kind is a registry name for a rule over the record's type, genre or native label, derived on read and assigned by setting its defining fields. Import assigns it when the origin determines it; otherwise an entry whose type has kinds warns with their names in the preview and saved import record. `add --kind` and `update --kind` refuse differing defining values and show both; `list --kind` and `search --kind` filter, `--kind unassigned` selects types with kinds and none assigned, and `kinds` prints the definitions. Source JSON includes the derived kind beside its bibliographic metadata.

## Titles and normalization

`title_protection` maps each supported title field to `{protected_terms: [nonempty strings], preserve_case: boolean}`. Terms are literal, case-sensitive whole-word/phrase matches after NFC normalization; punctuation boundaries count as word boundaries. Do not use offsets. Preserve-case bypasses title normalization for that whole field. A title edit drops terms no longer present and warns once, naming them. An explicitly supplied absent term also warns. Import distinguishes case-protection groups from accent/command arguments. The global terms list suggests per-record protection and never retroactively changes a record.

English titles use the configured Title Case rule and preserve original input. The shared validator normalizes ISO 639-2/B and 639-2/T codes and common English language names to language tags; supplied tags such as en-US retain their form. Unknown values remain literal with a record limitation and use the missing-language title warning rule. Non-English tags retain title spelling; export preserves the tag and warns about an ASCII title without guessing a correction. Unprotected internal capitals warn, never block. Style-specific output casing does not mutate stored text. The explicit sort-title override lives at overrides.sort_title; the explicit short title lives only at metadata.title-short. Derived values are computed from current metadata, supplied main-title structure and policy. A supplied metadata.title-short is an explicit short title; it is not duplicated in overrides. Subtitle boundaries are not inferred from colons.

Creator key policy `creator-latin-v1`: NFC then NFKD, remove combining marks only from Latin-letter sequences, use ASCII letters/digits and a table `ß→ss, æ→ae, ø→o, ł→l, đ→d, þ→th, ð→d, œ→oe, ı→i` (including uppercase forms). Reject any remaining unsupported letter, symbol, private-use or control character; allow surname hyphens, remove spaces/apostrophes. Non-Latin names require key_author; never silently drop their characters. Record policy, table and Unicode-data versions. Their members in key_provenance are named policy, table_version and unicode_version; the table digest is named table_sha256, and the provenance kind is named origin. AnyAscii is a future evaluated fallback, not a dependency. Assigned keys never regenerate automatically.

Title-token stopwords are in the CLI/configuration contract. Select eligible words left-to-right; punctuation separates words, letters/digits stay together. Lowercase the first selected word and capitalize only the initial of the second. Use author/editor fallback, uppercase ND and collision suffixes as specified. A key must be nonempty, unique, and contain no whitespace/control characters or BibTeX delimiters `,{}()=\#%"`. Imported incompatible keys remain recorded with export errors. Case-sensitive catalog uniqueness preserves legacy keys; case-only twins block portable export. Copy preview shows the conventional filename and any keep-name/fallback decision; no standalone filename command exists.

## Patches and clearing

`update REF --patch PATH --if-revision N` accepts `{schema_version:"1.0", set:{path:value}, clear:[path], provenance:[...]}`. Arrays are replaced whole. Null in set is rejected; use clear. A path cannot occur in both. IDs, keys, revisions, original evidence, resource paths and internal state are not patchable. Each changed source increments revision once and reports it; a no-op preserves it, an omitted --if-revision applies to the current revision, and a supplied guard refuses a stale revision. Explicit corrections may replace earlier explicit values, but imports cannot do so silently. Clearing an override restores derivation; clearing the last recognizable title/URL/part identification fails. Any metadata path the record profile accepts can be set or cleared, and bind-time fills follow the same rule; export assesses fields separately.

Record explicit sets, clearing and type supersession in the source-row corrected_fields marker; do not add a field_provenance table. Preserved originals may supply only specifically approved unmodeled passthrough facts, never modeled fields. Export always generates current modeled values, including deliberate absence. No stale original TeX can replace a later edit.

`update REF --set PATH=JSON --if-revision N` is the human shortcut and uses the same validator. Repeated set options are allowed for distinct paths; strings require JSON quoting. JSON patch remains the complete agent interface.

## Identity and non-overwriting import

**Slice 2, all import formats.** Check prior origin bindings and normalized identifiers together. A unique DOI match binds when type and edition do not contradict. ISBN is a fallback for books only, with exactly one incoming book and one existing book in its group; ambiguous groups do not bind. Batch ISBN candidates are the sources present before the batch, so a fresh library import keeps distinct books sharing an ISBN. Existing key and origin identities support unchanged reruns; contradictory signals and removed-source matches require inspection. Keep the catalog key and record the incoming key in provenance. Report every bind. Title similarity produces a warning on a separate source, never a merge or block.

A bound entry fills absent fields with origin `import`; deliberate clears and incompatible fields stay absent. Incoming omissions propose nothing. Differing values remain in originals and appear side by side in the persisted report. Source creation, safe fills, evidence and bindings commit with the entry's accounting. Reruns do not duplicate sources, resources, notes, memberships or relations, or undo corrections.

`import reconcile BATCH --take-incoming KEY[.field]...` previews selected incoming entries by batch citation key. KEY accepts differing values; KEY.field selects a canonical path, such as KEY.metadata.title. Resolve a complete key first, then its suffix; ambiguous selectors fail. Preview is read-only and includes `batch_revision` and each entry's current source revision. Execution requires `--execute --if-batch-revision N`; atomically recheck the batch and every touched source revision, returning stale_revision on any change. Explicit acceptance records corrections, retains the catalog key and leaves unselected differences current. Identity conflicts require inspection, not metadata overwrites. `--keep-current KEY[.field]` uses the same selectors and revision guard. It records the current and incoming values as a decision for that import origin without changing the source. Resolved differences leave the conflict list; later imports suppress that same comparison. A changed current or incoming value is reviewed again. Ordinary update remains available.

### Zotero Extra — slice 2

Parse labels case-insensitively. `Citation Key:` participates in the [input contract's precedence](interchange.md). Map `doi`, `pmid`, `pmcid` and `issn` to their CSL variables; map `arxiv` and `oclc` to `extensions.identifiers`. All routes normalize DOI by stripping its resolver prefix and lowercasing it. arXiv identifiers lose the `arXiv:` prefix and trailing subject class, retaining the version suffix. Equivalent arXiv archive numbers, Extra values and arXiv DOI identifiers share one extension value; the DOI remains available for DOI binding. Unequal normalized values are reported. These identifiers are searchable; D3 binding still requires consistent identity evidence, not an ISSN shared by different articles. Conflicting values are reported, never silently selected. Every other line remains only in the complete original Extra, not metadata or context. `show` reports `Preserved from import: extra` when such lines exist.

There is no saved export projection in slice 1. Re-importing a documented lossy output may report a type/value conflict while preserving the richer record. It cannot infer a richer original type in a fresh catalog. Safe re-run means no duplicates or overwritten decisions, not guaranteed conflict suppression.

## Applicability

The registry explicitly lists field_applicability and extension_applicability by canonical type. An input mapping applies within its type scope. Any pinned CSL variable is accepted on any supported type during capture, editing and import. Applicability is assessed only on export: a fact without a portable slot is a documented omission. Source type defaults to document only when omitted for casual capture. The core type enum is restricted to the modeled types; the pinned CSL schema supplies the accepted variable vocabulary. `chapter-number` owns the traditional part identifier.

## Complete envelope and import omission rules

Allowed source-create keys are schema_version, citation_key, key_author, metadata, native_type, extensions, title_protection, title_parts, overrides, legacy_tags, context and provenance. Only schema_version and metadata are required; omitted lists/objects default empty, optional labels/overrides default absent. `legacy_tags` is a list of nonblank Unicode strings deduplicated exactly, searchable without becoming approved taxonomy. `overrides` admits only sort_title (nonblank Unicode text). `title_parts` admits only main_title: a supplied nonblank complete-word prefix of metadata.title, representing an explicitly supplied boundary, never an inferred colon split. A title change that invalidates it must clear or replace it explicitly. Short-title derivation uses that value, otherwise full title; metadata.title-short remains the sole explicit short-title override. Patches may set/clear these documented paths. key_author is a validated generation override and cannot change bibliographic names or an already assigned key.

Context entries require text and origin=user|agent|import; optional source_url and original_ref (an original-entry reference) are allowed. Provenance entries admit origin=user|agent|import|derived, access=metadata|abstract|full_text|unknown, source_url, observed_at, original_ref (an original-entry reference) and source_identity (a source-system identity object whose optional keys are namespace, library_uri and item_key). Claims remain supplied claims, not verified reading. Unknown nested keys fail at every modeled boundary; unmodeled import data remains immutable evidence rather than arbitrary envelope keys.

Incoming omission means no proposal, never deletion. Only explicit clearing deletes a modeled value. `howpublished` is preserved exactly as supplied and re-emitted unchanged; nothing is moved into or synthesized from `note`. A source's own note is emitted as note. The arXiv fallback specified in the bibliography contract is the explicit exception for identifier compatibility, not generic howpublished synthesis.



## Input adapters and run accounting

Add accepts one refs JSON, CSL JSON or Bib entry. Import accepts Bib files and, in slice 2, the [Zotero directory](interchange.md). CSL-JSON import accepts one object or an array, saving one batch and each element's exact bytes as original evidence. CSL id is external origin evidence, not an assigned refs UUID. Both routes validate the accepted CSL variables. CSL producer properties outside that vocabulary remain in the preserved original and are ignored by capture. Native type and source-system identity remain optional for casual capture. Source-record output includes stable id/key/state/revision, the canonical create fields, corrected_fields/key provenance, original references and resources; result wraps it under data. Internal identity, revision and correction-marker fields cannot be supplied as arbitrary create/patch mutations.

Use bibtexparser==2.0.1 only as a guarded block splitter. Preserve each entry's exact bytes, file digest/byte offsets and necessary comments/definitions, including failed blocks. Retain the exact .bib input once in originals for adoption inspection; entry slices remain independently addressable. Guard the audit's duplicate/case-colliding fields, missing-equals absorption and embedded-entry-marker cases; truncated parser raw text is not the original. Unpartitionable input cannot produce source writes. No custom general parser is justified by these guard cases.

Decode supported non-verbatim text with pylatexenc==2.11 on a working copy. Never generically decode DOI/URL/file values. Preserve original TeX/protection; unknown commands/math produce limitations rather than silent text corruption. BibTeX month values accept integers 1–12, three-letter abbreviations and full English month names without case sensitivity; other values refuse. Custom strings, concatenation, crossref/xdata and inheritance remain preserved/unresolved. Explicit external preprocessing needs original and flattened bytes plus tool/version provenance.

The corpus confirms the boundary: entries without a usable title, URL or book part; unsupported entry types; unsupported TeX or math forms; malformed creator forms; BibTeX field names with punctuation such as `+`; and URLs containing TeX escapes retain their original bytes even when admission or export refuses them. Calendar-invalid and unsupported month values also refuse, while natural-language access dates are retained but have no assessed portable projection. Export refuses control characters in field values and case-colliding citation keys. These remain explicit limits until a concrete source shape justifies a new mapping or correction rule.

Each run records its input digest and aggregate counts. **Slice 2:** `import_entries` persists outcomes, candidates, conflicting values and source associations for `import show` and reconciliation. Counts and entry state commit with each application; interrupted runs remain incomplete and can be rerun. A finished Bib run accounts for every block and proves its digest was imported for adoption, even with conflicts; an unpartitionable run does not. Import never writes its input or acquires file bytes.

Resource JSON names the absolute locator `path`, or the named-root pair `root` and `relative`. The verified content hash is `digest`; descriptive members are `label` and `media_type`. Inspection adds `resolved_path` when resolution succeeds and `status` for availability.

Import result fields are named `import_id`, `input`, `file_digest`, `counts` and `entries`. Each entry includes `citation_key` and uses `outcome`, byte offsets `start` and `end`, and the status fields `preserved`, `editable`, `searchable` and `exportable`. Pending file paths are `resource_proposals`; preserved-only mapping issues are `limitations`, with `field` and `reason` members. Copy previews name the planned output path `destination`.

Generated key provenance names its captured key-generation settings `naming_settings`. Import entry results name their classification `status`, alongside the existing `outcome` member.
