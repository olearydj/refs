# Record and Mutation Contract v1

**Status:** Implementation proposal for trimmed slice 1, 2026-09-21. The envelope remains version 1.0; there is no installed API to migrate. The [registry](bibliographic-coverage.json) and [bibliography contract](bibliography.md) own the bounded bibliographic profile.

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

Unknown envelope keys and wrong primitive types fail; no general string-to-number coercion. Creation needs a nonblank title or absolute HTTP(S) URL, or a container-title plus page or chapter-number identification for a traditional title-less part. It needs no tags, project or file. Generic casually captured records may use type document; unknown explicitly supplied types remain unapplied originals with a diagnostic. Generated keys require usable title tokens or an explicit key. URLs are not invented into titles.

`metadata` is the sole authority for the registry's CSL-shaped fields. No parallel creators, identifiers, publication object, citation_fields or editable native-fields namespace exists. Creator arrays use CSL roles and ordered personal/literal names. Standard identifiers occupy DOI/ISBN/ISSN/PMID/PMCID; normalized lookup indexes are derived. Additional scheme/value identifiers can be preserved in originals until a justified extension is registered. Native type is optional `{namespace,value}`, validated against the type crosswalk; it cannot contradict the canonical type. Origin-system identity belongs to provenance, not this label.

Dates use `date-parts`, `literal`, `season`, `circa` where supported by the pinned schema. Validate calendar values and range order; never invent January 1. Free-text Zotero dates remain in originals; API `meta.parsedDate` is an aid, not another authority. Structured dates must agree with reliable explicit components; contradictions are reported without applying the entry. Unparseable dates remain literal with a precision warning. Bib date and year/month must agree at their overlapping precision. Month macros jan–dec are supported; other macros/inheritance need explicit preprocessing and preserved provenance. Complex uncertain/open dates remain literal until a tested target mapping exists.

Edition is one CSL-compatible string or positive integer. An unambiguous decimal edition becomes an integer; descriptive text remains text. Numeric display/filename interpretations are derived, never independently editable edition statements. Version is separate. A source type change must explicitly clear incompatible fields or fail with all conflicts; originals cannot restore them.

Name forms are either literal or personal with family/given and optional dropping-particle, non-dropping-particle, suffix and strict boolean flags. They cannot mix literal and personal properties. BibTeX's explicit von part defaults to dropping-particle with preview and override; Zotero's unsplit lastName is not split by guessing lowercase words. Such structural differences remain visible as import conflicts. A fully grouped corporate author containing “ and ” stays one literal. Native inventor/presenter/programmer map to citation author only on their corresponding types; native role survives as provenance. Key generation uses the first name in the source's author list, then the first editor, then the title and year, for every type. key_author still overrides. Native roles such as inventor, presenter and programmer remain provenance and do not affect keys. Presentation overrides such as shortauthor/sortname are not contributor roles.

## Titles and normalization

`title_protection` maps each supported title field to `{protected_terms: [nonempty strings], preserve_case: boolean}`. Terms are literal, case-sensitive whole-word/phrase matches after NFC normalization; punctuation boundaries count as word boundaries. Do not use offsets. Preserve-case bypasses title normalization for that whole field. Warn on protected terms no longer present after an edit; retain them until explicitly changed. Import distinguishes case-protection groups from accent/command arguments. The global terms list suggests per-record protection and never retroactively changes a record.

English titles use the configured Title Case rule and preserve original input. Unknown/non-English language retains spelling with a warning; export requires langid for known non-English titles. Unprotected internal capitals warn, never block. Style-specific output casing does not mutate stored text. The explicit sort-title override lives at overrides.sort_title; the explicit short title lives only at metadata.title-short. Derived values are computed from current metadata, supplied main-title structure and policy. A supplied metadata.title-short is an explicit short title; it is not duplicated in overrides. Subtitle boundaries are not inferred from colons.

Creator key policy `creator-latin-v1`: NFC then NFKD, remove combining marks only from Latin-letter sequences, use ASCII letters/digits and a table `ß→ss, æ→ae, ø→o, ł→l, đ→d, þ→th, ð→d, œ→oe, ı→i` (including uppercase forms). Reject any remaining unsupported letter, symbol, private-use or control character; allow surname hyphens, remove spaces/apostrophes. Non-Latin names require key_author; never silently drop their characters. Record policy, table and Unicode-data versions. Their members in key_provenance are named policy, table_version and unicode_version; the table digest is named table_sha256, and the provenance kind is named origin. AnyAscii is a future evaluated fallback, not a dependency. Assigned keys never regenerate automatically.

Title-token stopwords are in the CLI/configuration contract. Select eligible words left-to-right; punctuation separates words, letters/digits stay together. Lowercase the first selected word and capitalize only the initial of the second. Use author/editor fallback, uppercase ND and collision suffixes as specified. A key must be nonempty, unique, and contain no whitespace/control characters or BibTeX delimiters `,{}()=\#%"`. Imported incompatible keys remain recorded with export errors. Case-sensitive catalog uniqueness preserves legacy keys; case-only twins block portable export. Copy preview shows the conventional filename and any keep-name/fallback decision; no standalone filename command exists.

## Patches and clearing

`update REF --patch PATH --if-revision N` accepts `{schema_version:"1.0", set:{path:value}, clear:[path], provenance:[...]}`. Arrays are replaced whole. Null in set is rejected; use clear. A path cannot occur in both. IDs, keys, revisions, original evidence, resource paths and internal state are not patchable. Each changed source increments revision once; a no-op preserves it. Explicit corrections may replace earlier explicit values, but imports cannot do so silently. Clearing an override restores derivation; clearing the last recognizable title/URL/part identification fails.

Record explicit sets, clearing and type supersession in the source-row corrected_fields marker; do not add a field_provenance table. Preserved originals may supply only specifically approved unmodeled passthrough facts, never modeled fields. Export always generates current modeled values, including deliberate absence. No stale original TeX can replace a later edit.

`update REF --set PATH=JSON --if-revision N` is the human shortcut and uses the same validator. Repeated set options are allowed for distinct paths; strings require JSON quoting. JSON patch remains the complete agent interface.

## Identity and non-overwriting import

Check all identity evidence: explicit UUID, prior origin binding and consistent persistent identifiers. Contradictory signals, editions or versions stop that entry. A key alone proposes a match; title similarity never authorizes one. Exact previously applied entry evidence or a unique consistent identity permits a repeat, not replacement of current values. New entries commit source/evidence/identity together. Repeats never duplicate sources/resources; differences are reported without overwriting, including previously empty or deliberately cleared fields.

Plain update settles value conflicts and records corrected paths. If the source retains a deliberate different value, later imports may report the conflict again. There is no batch reconcile command or per-entry status table. Identity collisions require inspection and, where appropriate, ordinary add with a distinct key; no automatic merge or rekey. Removed-source matches report source_removed.

There is no saved export projection in slice 1. Re-importing a documented lossy output may report a type/value conflict while preserving the richer record. It cannot infer a richer original type in a fresh catalog. Safe re-run means no duplicates or overwritten decisions, not guaranteed conflict suppression.

## Applicability

The registry explicitly lists field_applicability and extension_applicability by canonical type. A mapping applies only when its input type scope and target applicability both hold. Values outside those bounds remain preserved originals or explicit reconciliation conflicts; no silent field deletion. Source type defaults to document only when omitted for casual capture. The core type enum is restricted to the modeled types; complete upstream schemas are validation references, not a broader acceptance promise. `chapter-number` owns the traditional part identifier.

## Complete envelope and import omission rules

Allowed source-create keys are schema_version, citation_key, key_author, metadata, native_type, extensions, title_protection, title_parts, overrides, legacy_tags, context and provenance. Only schema_version and metadata are required; omitted lists/objects default empty, optional labels/overrides default absent. `legacy_tags` is a list of nonblank Unicode strings deduplicated exactly, searchable without becoming approved taxonomy. `overrides` admits only sort_title (nonblank Unicode text). `title_parts` admits only main_title: a supplied nonblank complete-word prefix of metadata.title, representing an explicitly supplied boundary, never an inferred colon split. A title change that invalidates it must clear or replace it explicitly. Short-title derivation uses that value, otherwise full title; metadata.title-short remains the sole explicit short-title override. Patches may set/clear these documented paths. key_author is a validated generation override and cannot change bibliographic names or an already assigned key.

Context entries require text and origin=user|agent|import; optional source_url and original_ref (an original-entry reference) are allowed. Provenance entries admit origin=user|agent|import|derived, access=metadata|abstract|full_text|unknown, source_url, observed_at, original_ref (an original-entry reference) and source_identity (a source-system identity object whose optional keys are namespace, library_uri and item_key). Claims remain supplied claims, not verified reading. Unknown nested keys fail at every modeled boundary; unmodeled import data remains immutable evidence rather than arbitrary envelope keys.

Incoming omission means no proposal, never deletion. Only an explicit patch clear deletes a modeled value. Known howpublished text enters metadata.note as citation-note text with imported origin and retained raw field evidence; if both howpublished and note exist, concatenate decoded howpublished then note with a newline, preserving the raw fields in the original entry. This is a documented composition of note fragments, not conflicting aliases or inference of rich type/authority/event facts. Emit the resulting citation note once as note; profile-generated howpublished remains derived output. Unsupported executable/math syntax follows the unknown policy.


## Input adapters and run accounting

Add accepts one refs JSON, CSL JSON or Bib entry; import accepts a .bib file with supported BibTeX and BibLaTeX aliases per entry. CSL id is external origin evidence, not an assigned refs UUID. Both routes use the same bounded validator. Native type and source-system identity remain optional for casual capture. Source-record output includes stable id/key/state/revision, the canonical create fields, corrected_fields/key provenance, original references and resources; result wraps it under data. Internal identity, revision and correction-marker fields cannot be supplied as arbitrary create/patch mutations.

Use bibtexparser==2.0.1 only as a guarded block splitter. Preserve each entry's exact bytes, file digest/byte offsets and necessary comments/definitions, including failed blocks. Retain the exact .bib input once in originals for adoption inspection; entry slices remain independently addressable. Guard the audit's duplicate/case-colliding fields, missing-equals absorption and embedded-entry-marker cases; truncated parser raw text is not the original. Unpartitionable input cannot produce source writes. No custom general parser is justified by these guard cases.

Decode supported non-verbatim text with pylatexenc==2.11 on a working copy. Never generically decode DOI/URL/file values. Preserve original TeX/protection; unknown commands/math produce limitations rather than silent text corruption. Only jan–dec macros are resolved natively; custom strings, concatenation, crossref/xdata and inheritance remain preserved/unresolved. Explicit external preprocessing needs original and flattened bytes plus tool/version provenance.

Each finished import emits per-entry outcomes and records one imports row with exact file digest and aggregate counts. Conflicts and invalid entries preserve original evidence, not a persisted per-entry workflow. Counts commit alongside entry application; an interrupted run remains incomplete and can be rerun. A finished run with every block accounted for proves that digest was imported for adoption even if conflicts were reported; a truncated/unpartitionable run does not. Import does not write input files or acquire attachments.

Resource JSON names the absolute locator `path`, or the named-root pair `root` and `relative`. The verified content hash is `digest`; descriptive members are `label` and `media_type`. Inspection adds `resolved_path` when resolution succeeds and `status` for availability.

Import result fields are named `import_id`, `input`, `file_digest`, `counts` and `entries`. Each entry uses `outcome`, byte offsets `start` and `end`, and the status fields `preserved`, `editable`, `searchable` and `exportable`. Pending file paths are `resource_proposals`; preserved-only mapping issues are `limitations`, with `field` and `reason` members. Copy previews name the planned output path `destination`.

Generated key provenance names its captured key-generation settings `naming_settings`. Import entry results name their classification `status`, alongside the existing `outcome` member.
