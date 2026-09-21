# Record and Mutation Contract v1

**Status:** Revised preimplementation contract, 2026-09-21. The envelope remains version 1.0; there is no installed API to migrate. The [registry](bibliographic-coverage.json) and [bibliography contract](bibliography.md) own the bounded bibliographic profile.

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

Dates use `date-parts`, `literal`, `season`, `circa` where supported by the pinned schema. Validate calendar values and range order; never invent January 1. Free-text Zotero dates remain in originals; API `meta.parsedDate` is an aid, not another authority. Structured dates must agree with reliable explicit components; contradictions require reconciliation. Unparseable dates remain literal with a precision warning. Bib date and year/month must agree at their overlapping precision. Month macros jan–dec are supported; other macros/inheritance need explicit preprocessing and preserved provenance. Complex uncertain/open dates remain literal until a tested target mapping exists.

Edition is one CSL-compatible string or positive integer. An unambiguous decimal edition becomes an integer; descriptive text remains text. Numeric display/filename interpretations are derived, never independently editable edition statements. Version is separate. A source type change must explicitly clear incompatible fields or fail with all conflicts; originals cannot restore them.

Name forms are either literal or personal with family/given and optional dropping-particle, non-dropping-particle, suffix and strict boolean flags. They cannot mix literal and personal properties. BibTeX's explicit von part defaults to dropping-particle with preview and override; Zotero's unsplit lastName is not split by guessing lowercase words. Such structural differences remain visible in reconciliation. A fully grouped corporate author containing “ and ” stays one literal. Native inventor/presenter/programmer map to citation author only on their corresponding types; native role survives as provenance. Key generation uses author then editor, but author arrays on patent, speech and software denote inventor/presenter/programmer and are ineligible for the author-token fallback. Those types use editor if supplied, otherwise title/year unless key_author overrides. This preserves the earlier separation between citation role projection and key-role policy, consistently for every input route. Presentation overrides such as shortauthor/sortname are not contributor roles.

## Titles and normalization

`title_protection` maps each supported title field to `{protected_terms: [nonempty strings], preserve_case: boolean}`. Terms are literal, case-sensitive whole-word/phrase matches after NFC normalization; punctuation boundaries count as word boundaries. Do not use offsets. Preserve-case bypasses title normalization for that whole field. Warn on protected terms no longer present after an edit; retain them until explicitly changed. Import distinguishes case-protection groups from accent/command arguments. The global terms list suggests per-record protection and never retroactively changes a record.

English titles use the configured Title Case rule and preserve original input. Unknown/non-English language retains spelling with a warning; export requires langid for known non-English titles. Unprotected internal capitals warn, never block. Style-specific output casing does not mutate stored text. The explicit sort-title override lives at overrides.sort_title; the explicit short title lives only at metadata.title-short. Derived values are computed from current metadata, supplied main-title structure and policy. A supplied metadata.title-short is an explicit short title; it is not duplicated in overrides. Subtitle boundaries are not inferred from colons.

Creator key policy `creator-latin-v1`: NFC then NFKD, remove combining marks only from Latin-letter sequences, use ASCII letters/digits and a table `ß→ss, æ→ae, ø→o, ł→l, đ→d, þ→th, ð→d, œ→oe, ı→i` (including uppercase forms). Reject any remaining unsupported letter, symbol, private-use or control character; allow surname hyphens, remove spaces/apostrophes. Non-Latin names require key_author; never silently drop their characters. Record policy, table and Unicode-data versions. AnyAscii is a future evaluated fallback, not a dependency. Assigned keys never regenerate automatically.

Title-token stopwords, two-word camel casing, author/editor fallback, uppercase ND and collision suffixes remain in the spec. A key must be nonempty, unique, and contain no whitespace/control characters or BibTeX delimiters `,{}()=\#%"`. Imported incompatible keys remain recorded with export errors. Case-sensitive catalog uniqueness preserves legacy keys; case-only twins block portable export. Filename preview follows the accepted short-title/edition/version/year conventions and never renames a file.

## Patches and clearing

`update REF --patch PATH --if-revision N` accepts `{schema_version:"1.0", set:{path:value}, clear:[path], provenance:[...]}`. Arrays are replaced whole. Null in set is rejected; use clear. A path cannot occur in both. IDs, keys, revisions, original evidence, resource paths and operation state are not patchable. Each changed source increments revision once; a no-op preserves it. Explicit corrections may replace earlier explicit values, but imports cannot do so silently. Clearing an override restores derivation; clearing the last recognizable title/URL/part identification fails.

Record modeled absence, explicit clearing and type supersession. Preserved originals may supply only specifically approved unmodeled passthrough facts, never modeled fields. Export always generates current modeled values, including deliberate absence. No stale original TeX can replace a later edit.

`update REF --set PATH=JSON --if-revision N` is the human shortcut and uses the same validator. Repeated set options are allowed for distinct paths; strings require JSON quoting. JSON patch remains the complete agent interface.

## Identity and reconciliation

Check all identity evidence before precedence: explicit UUID, prior origin identity and consistent persistent identifiers generate candidates. Conflicting signals, editions or versions stop that entry. A key alone proposes a match; title similarity never authorizes one. Reconciliation actions are match, create_distinct or leave_unresolved, with entry ID, target source and expected revision; every differing field needs current/incoming/clear selection. Distinct creation under an occupied key needs a new explicitly supplied key and preserves the old key as provenance.

An export projection record contains source ID/revision, destination profile fingerprint, emitted entry digest and the canonical-to-emitted field/type decisions. Re-import can retain a richer current type only when this record and matching emitted values prove an unchanged documented downgrade. Other edits are reconciled normally; current later corrections are never rolled back. A fresh catalog without projection evidence cannot reconstruct lost type information or infer identity from the key.

## Applicability

The registry explicitly lists field_applicability and extension_applicability by canonical type. A mapping applies only when its input type scope and target applicability both hold. Values outside those bounds remain preserved originals or explicit reconciliation conflicts; no silent field deletion. Source type defaults to document only when omitted for casual capture. The core type enum is restricted to the modeled types; complete upstream schemas are validation references, not a broader acceptance promise. `chapter-number` owns the traditional part identifier.

## Complete envelope and import omission rules

Allowed source-create keys are schema_version, citation_key, key_author, metadata, native_type, extensions, title_protection, title_parts, overrides, legacy_tags, context and provenance. Only schema_version and metadata are required; omitted lists/objects default empty, optional labels/overrides default absent. `legacy_tags` is a list of nonblank Unicode strings deduplicated exactly, searchable without becoming approved taxonomy. `overrides` admits only sort_title (nonblank Unicode text). `title_parts` admits only main_title: a supplied nonblank complete-word prefix of metadata.title, representing an explicitly supplied boundary, never an inferred colon split. A title change that invalidates it must clear or replace it explicitly. Short-title derivation uses that value, otherwise full title; metadata.title-short remains the sole explicit short-title override. Patches may set/clear these documented paths. key_author is a validated generation override and cannot change bibliographic names or an already assigned key.

Context entries require text and origin=user|agent|import; optional source_url and original-entry reference are allowed. Provenance entries admit origin=user|agent|import|derived, access=metadata|abstract|full_text|unknown, source_url, observed_at, original-entry reference and a source-system identity object {namespace,library_uri,item_key}. Claims remain supplied claims, not verified reading. Unknown nested keys fail at every modeled boundary; unmodeled import data remains immutable evidence rather than arbitrary envelope keys.

Incoming omission means no proposal, never deletion. Only an explicit patch clear or a reconciliation clear decision deletes a modeled value. Known howpublished text enters metadata.note as citation-note text with typed field provenance; if both howpublished and note exist, concatenate decoded howpublished then note with a newline, preserving separate field origins. This is a documented composition of note fragments, not conflicting aliases or inference of rich type/authority/event facts. Emit the resulting citation note once as note; profile-generated howpublished remains derived output. Unsupported executable/math syntax follows the unknown policy.

Projection comparison first validates identifiers and parses supported input into the portable profile's field/value representation, including ordered names, calendar precision and protection terms. Ignore field ordering, lexical enclosure and whitespace outside values, not meaningful text, creator order, case protection or unknown directives. Byte digests are a fast path; harmless syntax reformatting with identical semantic projection remains a match. Require a unique saved projection source with the same assigned key and complete matching emitted semantics, and no contradictory origin/identifier evidence. Multiple candidate source IDs require reconciliation. Matching fields retain current values even if their source revision has since advanced or they were cleared; the historical source revision identifies the emission, not permission to roll back. New/changed incoming fields follow ordinary reconciliation. A profile change cannot reuse another profile's interpretation without an explicitly compatible mapping. A fresh catalog lacking this evidence cannot infer a richer original type.
