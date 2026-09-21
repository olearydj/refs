# Cross-route Model Examples, 2026-09-21

## Status and method

Synthetic redesign evidence following audit sections 10–12, not a refs importer certification. [check.py](check.py) contains 14 corpus-shaped synthetic cases, explicit candidate Zotero mappings, a validating identity route for agent CSL-shaped input, expected values, and actual Pandoc BibLaTeX-reader results. [results.json](results.json) retains every input/projection/difference. The agent validator covers only exercised shapes, not the final complete schema. Pandoc is a differential oracle, not refs' future bibtexparser adapter.

Run `adhoc-python specs/001-academic-catalog/reviews/model-examples-2026-09-21/check.py`. Pandoc 3.11 was executed. No private library/manuscript/PDF was read or changed, and no project dependencies were installed. The same source identifiers are synthetic labels, not evidence of automatic identity matching.

The original five-case report treated reader title casing as a model limitation. That is superseded: comparisons now neutralize casing/nocase markup for title fields, retaining unmodified reader output. Pandoc's deprecated event property is compared to event-title. refs will preserve internal Title Case. Protected terms and the whole-title flag supersede the earlier offset-spans suggestion.

## Results and decisions

| Case | Observed evidence | Design consequence |
| --- | --- | --- |
| Thesis | university/school agree on publisher; explicit degree labels agree on genre. | One authority, aliases scoped to thesis. Do not infer arbitrary degree labels. |
| Report | institution agrees on publisher; reportNumber/number agree on number. | No separate mutable institution namespace. |
| Article | journal/publicationTitle, issue/number and legacy year/month converge. | Number must be scoped by type. |
| Chapter | Book/container, publisher/place and pages converge. | Does not settle traditional title-less inbook; preserve its separate rule. |
| Web | Portable misc loses exact webpage type. | Accepted documented fallback, warn/record. Persist projection evidence for idempotent re-import. |
| Preprint | Zotero archiveID/repository and explicit agent number/archive agree; Pandoc yields manuscript and derives an arXiv URL without preserving those two structured fields. | Use type-scoped number/archive, preserve original repository identity, and test refs' actual importer rather than delegating semantics to Pandoc. |
| Conference | Proceedings and conference names remain distinct; Pandoc returns deprecated event. | Normalize the alias, not the two facts. |
| Book | Edition, ISBN and series agree after neutralizing oracle casing. | Preserve edition meaning and collection title; no duplicated statement authority. |
| Magazine | Pandoc reads article as journal article. | Documented portable subtype downgrade; projection-aware re-import. |
| Standard | Pandoc reads standard as legislation. | Reject that canonical mapping; use explicit portable misc projection. Separate rendering probe below verifies the author/date consequence. |
| Patent | Inventor/name/number agree; the Zotero assignee has a separate expected extension while Pandoc omits holder. | Assignee is not inventor. The prototype checks Zotero's extension but does not certify BibTeX holder conversion. |
| Presentation | Misc loses speech type and does not return a separate event field. | Record documented fallback and event text; do not pretend generic input can reconstruct the richer type. |
| Particle | Zotero's unsplit lastName differs structurally from BibTeX's explicit dropping-particle. | Do not guess from casing. Preview and permit explicit name interpretation. This example deliberately does not assert exact convergence. |
| Corporate “ and ” | Fully grouped author and institution remain one literal each. | Serializer/parser fixtures must preserve grouping. |

All 14 agent-route records equal their candidate Zotero canonical values. Independent BibTeX results retain the differences above. These are small executed design probes, not a claim that all 140 registry rows have passed or that names/dates/extensions are fully implemented. Competing aliases targeting publisher are rejected. The six original approximate aliases are excluded from the candidate dictionary. The [independent row review](../semantic-row-review-2026-09-21.md) evaluates all 51 disputed fields and identifies further approximations.

## Standard rendering probe

[render-standard.py](render-standard.py) runs the preserved APA style through Pandoc 3.11 with intended CSL standard input, native @standard and portable @misc. [standard-render-results.json](standard-render-results.json) retains inputs, rendered HTML and diagnostics. The intended CSL and portable routes cite Research and Standards Council (2024); native @standard instead cites the title and formats a public-law number. Portable output retains the corporate author and date while formatting the standard number differently. This supports a documented fallback for this fixture and demonstrates why the native legislation conversion is a blocking authorship/citation change. It does not certify every style or standard record.

## Remaining implementation evidence

The selected model is one CSL-shaped authority with type-scoped aliases and four justified extensions, as documented in docs/bibliographic-model.md and the contracts. Required implementation fixtures still include free-text Zotero dates with meta.parsedDate and contradictions, unknown dates, explicit clearing/type changes, the actual guarded parser, every promoted extension, term protection versus accent-command braces, and fallback re-import. The registry explicitly labels these as obligations rather than passing probes.

The nine product decisions are settled. The constitution's conflicting adopt sentence remains a separately proposed amendment until explicitly authorized; no example grants that approval. Task generation follows the revised documents and independent checklist reassessment.
