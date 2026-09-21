# Semantic Row Review, 2026-09-21

## Status and method

Independent design review for the authoring session. This is a recommendation artifact, not an implementation certification or an amendment to governing contracts. Read audit sections 10–12 in full. Inspected every distinct native-field path in the then-current registry (preserved in the archived baseline linked below) and compared the upstream crosswalk targets. No live private catalog or manuscript was read. Corpus evidence is the preserved counts in `evidence-2026-09-20/zotero/inspect2.out`.

The registry has 54 distinct Zotero-native field names. The upstream crosswalk names targets for 51; the three others are assignee, country and seriesText. Two of the 51 targets, license and part-number, are absent from the pinned CSL input field list in this registry. Thus “51 divergences” is reproducible as crosswalk coverage, not 51 proven duplicate editable facts. Row recommendations below are independent semantic judgments, not declarations that upstream mappings are semantically exact.

Sources: the pre-revision registry member `specs/001-academic-catalog/contracts/bibliographic-coverage.json` in the [archived baseline](baseline-before-revision-2026-09-21.tar.gz), the [audit corrections and decisions](2026-09-20-independent-design-audit.md), and the pinned [Zotero schema crosswalk](https://raw.githubusercontent.com/zotero/zotero-schema/b86c79b56479cadac3288e1f122cf34ef04e8809/schema.json). The crosswalk was read through web retrieval; a shell download failed DNS, so no claim is made to have rehashed that download. The registry's pinned schema hash remains the prior audit's evidence.

## Individual dispositions for the 51 fields

Targets in this table name CSL variables, not the obsolete nested registry path. A recommendation to share a CSL variable is subject to its stated type scope. An out-of-corpus field can have a known conceptual mapping while remaining preserved-only in the delivered adapter. “Preserve only” means immutable per-entry original evidence, not a second editable extension or silent successful export.

| # | Zotero field | Zotero type scope in current registry | Crosswalk target | Disposition |
| --- | --- | --- | --- | --- |
| 01 | `applicationNumber` | patent | `call-number` | Reject alias: patent application identifier is not library shelf mark. Keep a justified patent.application_number extension when captured; do not share CSL call-number. |
| 02 | `archiveID` | preprint | `number` | Scoped alias for preprint repository identifier; pair with archive=repository. Bib eprint joins only when repository identity agrees. Never confuse with report number on another type. |
| 03 | `artworkMedium` | artwork | `medium` | Scoped medium/format alias. Map only on the declared item types; validate the input meaning and retain original wording. |
| 04 | `artworkSize` | artwork | `dimensions` | Equivalent dimensions on graphic items; outside observed corpus, preserve only until support is justified. |
| 05 | `audioFileType` | podcast | `medium` | Scoped medium/format alias. Map only on the declared item types; validate the input meaning and retain original wording. |
| 06 | `audioRecordingFormat` | audioRecording, radioBroadcast | `medium` | Scoped medium/format alias. Map only on the declared item types; validate the input meaning and retain original wording. |
| 07 | `billNumber` | bill | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 08 | `code` | bill, statute | `container-title` | Type-scoped container alias for legal publication titles; outside corpus preserve only initially. Do not conflate the code title with codeNumber. |
| 09 | `codeNumber` | statute | `volume` | Reject alias: statute code number is not necessarily container volume. Preserve only; out of corpus. |
| 10 | `committee` | hearing, standard | `section` | Reject alias: organizational committee is not a section of text. Preserve only pending demonstrated need, including on standards. |
| 11 | `court` | case | `authority` | Scoped issuing authority alias. A standards organization is authority, not automatically author or publisher. Do not manufacture a creator from it. |
| 12 | `docketNumber` | case | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 13 | `documentNumber` | hearing | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 14 | `episodeNumber` | podcast, radioBroadcast, tvBroadcast | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 15 | `extra` | artwork, audioRecording, bill, blogPost, book, bookSection, case, computerProgram, conferencePaper, dataset, dictionaryEntry, document, email, encyclopediaArticle, film, forumPost, hearing, instantMessage, interview, journalArticle, letter, magazineArticle, manuscript, map, newspaperArticle, patent, podcast, preprint, presentation, radioBroadcast, report, standard, statute, thesis, tvBroadcast, videoRecording, webpage | `note` | Reject bulk alias: mixed key directives, identifiers and prose. Extract recognized labels through type-scoped mappings; preserve the whole original and report unknown directives. Do not append Citation Key or tex directives to citation notes. |
| 16 | `format` | book, bookSection, dataset | `medium` | Scoped medium/format alias. Map only on the declared item types; validate the input meaning and retain original wording. |
| 17 | `genre` | film, preprint | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 18 | `history` | bill, case, hearing, statute | `references` | Approximate legal procedural history; preserve only, not catalog relations and not automatic citation reference text. |
| 19 | `identifier` | dataset | `number` | Dataset identifier is broader than DOI. Out of observed corpus: preserve only initially; future promotion needs identifier-scheme evidence, never duplicate DOI automatically. |
| 20 | `interviewMedium` | interview | `medium` | Scoped medium/format alias. Map only on the declared item types; validate the input meaning and retain original wording. |
| 21 | `issuingAuthority` | patent | `authority` | Scoped issuing authority alias. A standards organization is authority, not automatically author or publisher. Do not manufacture a creator from it. |
| 22 | `legislativeBody` | bill, hearing | `authority` | Scoped issuing authority alias. A standards organization is authority, not automatically author or publisher. Do not manufacture a creator from it. |
| 23 | `letterType` | letter | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 24 | `manuscriptType` | manuscript | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 25 | `mapType` | map | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 26 | `number` | manuscript, standard | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 27 | `organization` | standard | `authority` | Scoped issuing authority alias. A standards organization is authority, not automatically author or publisher. Do not manufacture a creator from it. |
| 28 | `partNumber` | journalArticle, standard | `part-number` | Crosswalk target absent from adopted CSL schema. Do not silently rename to part: prove meaning first; preserve only until a justified part-number extension is needed. |
| 29 | `partTitle` | journalArticle, standard | `part-title` | Equivalent title of a part; do not confuse a chapter title with its container title. |
| 30 | `patentNumber` | patent | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 31 | `postType` | forumPost | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 32 | `presentationType` | presentation | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 33 | `priorityDate` | patent | `original-date` | Reject automatic alias: patent priority date is not original publication date. Use patent.priority_date only when needed by a patent fixture; retain separate issued and submitted dates. |
| 34 | `priorityNumbers` | patent | `issue` | Reject alias: patent priority claims are not serial issue numbers. Preserve only pending an actual priority-number fixture; no duplicate issue value. |
| 35 | `programmingLanguage` | computerProgram | `genre` | Reject alias: programming language is not work genre. Preserve only; software is outside the measured corpus baseline. |
| 36 | `publicLawNumber` | statute | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 37 | `references` | patent | `references` | Patent reference text is a citation reference field, not catalog related-item pairs. Preserve only unless this fact is needed by the corpus fixture. |
| 38 | `reportNumber` | report | `number` | Alias by item type: identifying number of the described work. Do not map journal issue numbers here. |
| 39 | `reportType` | report | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 40 | `reporter` | case | `container-title` | Type-scoped container alias for legal publication titles; outside corpus preserve only initially. Do not conflate the code title with codeNumber. |
| 41 | `rights` | artwork, audioRecording, bill, blogPost, book, bookSection, case, computerProgram, conferencePaper, dataset, dictionaryEntry, document, email, encyclopediaArticle, film, forumPost, hearing, instantMessage, interview, journalArticle, letter, magazineArticle, manuscript, map, newspaperArticle, patent, podcast, preprint, presentation, radioBroadcast, report, standard, statute, thesis, tvBroadcast, videoRecording, webpage | `license` | Crosswalk target absent from adopted CSL schema. Preserve only initially; do not invent CSL license or silently treat it as rights metadata authority. |
| 42 | `runningTime` | audioRecording, film, podcast, radioBroadcast, tvBroadcast, videoRecording | `dimensions` | Approximate: duration is not physical dimensions. Preserve only initially; a future duration extension needs units and a fixture. |
| 43 | `scale` | map | `scale` | Equivalent map scale; outside observed corpus, preserve only until support is justified. |
| 44 | `section` | bill, journalArticle, newspaperArticle, statute | `section` | Equivalent division within an item, scoped by type. Do not map committee here. |
| 45 | `series` | journalArticle | `collection-title` | Split by type: book/report series can be collection-title; journal series is not automatically a collection. For journalArticle use a justified journal_series extension, never overwrite collection-title. |
| 46 | `session` | bill, hearing, statute | `chapter-number` | Reject alias: legislative session is not a chapter. Preserve only, since these legal item types are outside corpus. |
| 47 | `system` | computerProgram | `medium` | Reject automatic alias: supported operating system is not distribution medium. Preserve only; software outside corpus. |
| 48 | `thesisType` | thesis | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 49 | `type` | dataset, document, standard | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |
| 50 | `videoRecordingFormat` | film, tvBroadcast, videoRecording | `medium` | Scoped medium/format alias. Map only on the declared item types; validate the input meaning and retain original wording. |
| 51 | `websiteType` | blogPost, webpage | `genre` | Alias by item type: work-kind label; one CSL authority. Native item type stays a separate classification, never a duplicate genre. |

## Three remaining native fields

| Field | Disposition |
| --- | --- |
| assignee | A patent assignee is neither inventor nor publisher. A short justified patent.assignees extension is appropriate for the corpus patent case. Represent known organizations as literal names; preserve unresolved segmentation, and never split a literal organization on “ and ”. A BibLaTeX holder list can join this path after name normalization, not blind string equality. |
| country | Patent jurisdiction is not a creator address. A scoped mapping to CSL jurisdiction is plausible; require explicit normalization of country names/codes in the patent fixture. Do not assume the missing upstream crosswalk establishes non-equivalence. |
| seriesText | Preserve only until its distinction from journal series is demonstrated. It is not automatically collection-title, collection-number or a duplicate journal_series. |

## Additional true aliases outside the 51

Zotero university on thesis and institution on report are publishing/issuing institutions; use the same CSL publisher authority as traditional BibTeX school on thesis and institution on report. Do not retain publisher and institution as two editable homes for that same fact. A patent assignee and a conference organizer are different facts and must not be collapsed into publisher merely because they are organizations.

Traditional BibTeX number is type-scoped: article → issue; techreport → number; a numbered book series → collection-number. For books, absence of a series makes the interpretation uncertain and must not silently assign collection-number. Traditional journal → container-title only for articles; booktitle → container-title only for chapters and conference papers. address → publisher-place only when it describes the publisher, not an event location. Proceedings title and conference name are separate container-title and event-title facts.

Legacy year/month and BibLaTeX date converge on issued only after precision-preserving date parsing. Free-text Zotero date is never coerced to a fabricated January 1. Its original text remains evidence; meta.parsedDate is a parsing aid, not an independently editable second date. Use date-parts when reliable and a literal date when not; contradictory raw/parsed values require review. Accessed and submitted remain distinct.

## Required corpus coverage and discriminating examples

The 16 observed types are journalArticle, book, conferencePaper, preprint, bookSection, webpage, magazineArticle, thesis, blogPost, report, standard, presentation, document, patent, newspaperArticle and manuscript. Preserve these distinctions in the canonical type/native label even where portable BibTeX uses a documented fallback. Unknown types can be preserved without pretending that their export has been assessed.

| Example | Required authority and discrimination |
| --- | --- |
| Preprint | CSL article; number + archive for eprint/repository; repositoryLocation is not publisher-place by default. No parallel eprint authority. DOI remains distinct. |
| Conference paper | CSL paper-conference; container-title is proceedings, event-title is conference. Record editor separately from author. |
| Book | CSL book; edition textual meaning retained, collection-title and collection-number for series, ISBN distinct from DOI. Do not reduce revised/expanded edition to an unqualified integer. |
| Magazine and newspaper | Distinct article-magazine/article-newspaper; container-title, issued precision, volume/issue, section where applicable. |
| Standard | CSL standard; authority and number retained; corporate author remains author. Do not import as legislation because an oracle does. Portable misc is a declared projection whose actual cited-author/date output must be checked. |
| Patent | CSL patent; inventor is author; assignees extension is separate; number is patent number; application_number and priority_date cannot overwrite call-number or original-date. |
| Presentation | CSL speech; presenter is author for this type, event-title is meeting, genre is presentation type. |
| Name particle | CSL family/given and dropping/non-dropping-particle retained without guessing from every lowercase token. Compare BibTeX comma/von forms to explicit agent names. |
| Corporate “ and ” | CSL literal author; BibTeX organization is braced as a whole name. Never split literal organizations as a person list. |

Corpus roles are author, editor, seriesEditor, contributor, bookAuthor, presenter and inventor. Map seriesEditor to collection-editor, bookAuthor to container-author, and type-scoped presenter/inventor to author. This does not authorize merging an inventor and assignee or treating a contributor as author.

## Registry acceptance conditions

Every executable mapping row needs input format, input type scope, source field, canonical path, transformation, conflict rule, export projection/class and fixture ID. Type scope is mandatory even when a row lists several types. A field-name-only alias dictionary fails this review.

Agent input is the third convergence route and must pass the same canonical validator. Pandoc is a differential oracle for intended mapping and consumers; it does not exercise refs' future bibtexparser importer. Neutralize oracle title sentence-casing before comparing. Imported protection becomes per-title terms plus a whole-title flag; no Unicode offsets. Accent-command braces are not protection.

A documented portable type downgrade is idempotent only with evidence of the refs projection: match the persisted export manifest/source revision/profile and projected values, then retain the richer current type for unchanged projected facts. Citation-key equality alone is insufficient, since an external editor may intentionally change type or metadata. Changed projected values enter normal reconciliation; preserved originals must not resurrect cleared or type-incompatible fields. A fresh catalog without that manifest has only the portable entry's evidence and cannot promise recovery of its original exact type.

## Remaining semantic limits

The review does not certify an importer, resolve all preserved-only vocabulary, or establish meaning equivalence from a matching renderer result. Before declaring the corpus baseline complete, fixtures must cover the rows actually promoted, with intentional contradictions proving conflict rejection. Any preserved-only row selected for output is assessed by the four-class policy; it is never safe merely because its raw bytes survived. Extension promotion requires a named use and a fixture, not the existence of a Zotero field.
