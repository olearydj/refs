# Bibliographic Model and Standards

**Date**: 2026-09-20. **Decision status**: Recommended planning decision adopted for this feature revision under the user's instruction to proceed with research and targeted revision. This is not a claim of migration certification or a separately answered product clarification.

## Intent and recovered context

The user's original request was to retain useful Zotero conventions such as source types while replacing its application workflow. A supplied earlier discussion proposed Zotero's published model and distinguished it from the internal SQLite layout; it also considered CSL-JSON. The user highlighted Wren's Zotero-style model while declining its full GUI scope. These are evidence of intended bibliographic breadth, not proof that a particular canonical schema was already approved. CASS lexical searches recovered the original Codex session; direct native-transcript inspection was necessary because CASS expansion returned empty messages. [Original supplied discussion](/Users/djo/.codex/sessions/2026/09/20/rollout-2026-09-20T14-43-17-01a0c058-271b-7a61-84ed-af14d19baf91.jsonl:9), [Wren comparison](/Users/djo/.codex/sessions/2026/09/20/rollout-2026-09-20T14-43-17-01a0c058-271b-7a61-84ed-af14d19baf91.jsonl:105).

The later Pandoc probe lost attachment/custom fields on conversion to CSL-JSON and keywords on subsequent BibLaTeX output. [Development evidence](development.md) records the limitation; the [MVP](academic-mvp.md) requires creator roles, date precision, titles, editions, identifiers, unmapped fields, and dependable daily citation work. A narrow UI does not justify narrowing those semantics.

## Decision

Use a versioned **refs bibliographic profile** built from published vocabularies. Zotero's published schema supplies the exhaustive initial item/field/creator baseline; CSL supplies common citation semantics and a validation target; BibLaTeX supplies rich bibliography distinctions and a named export profile. refs owns identities, keys, provenance, operational state, projects, collections, and resource relationships. Its SQLite layout is an implementation choice. No normal command downloads a schema or depends on Zotero running.

The profile is not an unmodified copy of any one interchange format. Each fact has one authoritative editable representation. Shared facts use documented core fields; additional CSL facts use schema-validated citation fields; native distinctions use registered structured namespaces. Projections derive from those values. Immutable original bytes and expressions are separate evidence, never a second editable authority.

## Alternatives and consequences

| Alternative | Benefits | Why not selected as the complete catalog model |
| --- | --- | --- |
| Unmodified Zotero model | Mature types/roles, natural migration baseline, published CSL mappings | Application-specific constraints and Extra conventions do not cover every CSL/BibLaTeX distinction directly. |
| CSL-JSON alone | Shared citation input vocabulary and Pandoc compatibility | Several Zotero types collapse to one CSL type; file/collection relationships and rich native bibliography semantics exceed it. |
| BibLaTeX alone | Rich titles, dates, names, publication lists, and inheritance | TeX expressions, extensible datamodels, and bibliography processing behavior are unsuitable as the sole everyday editing contract. |
| A small independently invented schema | Simple initial implementation | Repeats the current gap: ordinary supplied data becomes opaque or unusable. |
| refs profile with published registries and explicit mappings | Retains established semantics while supporting application needs | Requires maintained mapping tables, schema pins, coverage reports, and interoperability fixtures. This cost is necessary and must remain visible. |

The Zotero schema maps podcast/TV/radio types to CSL `broadcast`, and letter/email/instant message to `personal_communication`; retain native type identity. Zotero itself documents extra citation types such as `review-book` through Extra. CSL distinguishes dropping and non-dropping particles and qualified dates. BibLaTeX distinguishes chapter, container, and multivolume titles and uses lists for publishers/locations. These are concrete reasons to avoid treating one schema as a universal ceiling. [Zotero schema](https://github.com/zotero/zotero-schema), [Zotero fields and Extra](https://www.zotero.org/support/kb/item_types_and_fields), [CSL input schema](https://github.com/citation-style-language/schema), [BibLaTeX model](https://github.com/plk/biblatex/blob/v3.22/tex/latex/biblatex/blx-dm.def).

## Boundaries and compatibility claims

A reference is a retained bibliographic source, which may identify a particular edition or version. Its PDF is a resource; a chapter's container and a later published version are relationships or distinct descriptions, not reasons to collapse identities. BIBFRAME's work/instance/item distinction is useful conceptual guidance, but adopting RDF or a full library-cataloging ontology is not required for this workflow. [BIBFRAME overview](https://www.loc.gov/bibframe/docs/bibframe2-model.html).

All published Zotero bibliographic types in the pinned baseline must be ingestible, inspectable, and editable through structured paths; notes, attachments, and annotations have their own explicitly bounded treatment. This does not promise a complete Zotero UI, sync protocol, or export compatibility for every type. CSL types outside Zotero remain valid bibliographic classifications. Initial project outputs remain BibLaTeX and traditional BibTeX; CSL-JSON is a mapped validation representation, with a public import/export command deferred until separately scoped.

Each mapping distinguishes ingestion, structured usability, indexing, target-specific export, and original preservation. An original snapshot alone satisfies only the last guarantee. Unknown fields remain recoverable and visible; known native fields cannot be hidden solely inside raw evidence. No format conversion is presumed lossless. Display/title-case policies remain separate from target-specific citation text conventions.

Imported child notes and annotation records receive stable origin/parent references and read-only structured inspection/full-library export. No editor, rendering engine, full-text indexing, or guarantee of external annotation usability is added. Attachment metadata includes URL-only and missing-file records, not just openable paths. Existing resource ownership rules remain binding. Related-source links are retained as asserted relationships without merge inference or a new relationship-management UI.

## Maintenance and acceptance

The feature's [bibliography contract](../specs/001-academic-catalog/contracts/bibliography.md) and [coverage inventory](../specs/001-academic-catalog/contracts/bibliographic-coverage.json) own exact profile paths, pins, mappings, limits, and fixture obligations. Schema vocabulary versions and Zotero database-adapter versions are separate. Upgrades require a reviewed registry diff and fixture comparison; they never regenerate keys or silently change existing records.

Two independent research agents challenged the Zotero-baseline proposal and examined mapping failures. Their conclusions are incorporated here and in [feature research](../specs/001-academic-catalog/research.md). Schema inspection and coverage enumeration were performed; adapter round trips, actual migration samples, and rendered citation validation remain implementation/release gates. No live library or manuscript was changed.
