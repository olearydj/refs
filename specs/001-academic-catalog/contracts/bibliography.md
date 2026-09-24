# Bibliographic Mapping and Export Contract v1

**Profile:** refs-bibliography-v1. **Status:** implementation proposal for trimmed slice 1, not executed importer certification. [Registry](bibliographic-coverage.json), [semantic row review](../reviews/semantic-row-review-2026-09-21.md), and [examples](../reviews/model-examples-2026-09-21/README.md) are complementary.

## Authority and bounded coverage

The registry contains type-scoped input aliases and the CSL variable vocabulary. Each promoted row must name input format, input type scope, source field, canonical path, transformation, conflict handling, portable projection/class and fixture. A generic field-name dictionary is forbidden: article number means issue, report number identifies the report, and book number needs series evidence. All paths must validate against the core/extension schemas; ambiguous aliases produce conflicts before mutation. The schema pins describe vocabulary, not a requirement to implement it exhaustively.

The 16 observed Zotero types plus software for the stated capture workflow are modeled. Unknown types remain verbatim originals with explicit limitations. Unmodeled CSL producer properties remain in originals; accepted variables are independent of source type. Search covers title, creators, abstract, context and legacy tags, not arbitrary originals. Each import report separately states preserved, editable, searchable and exportable status. Every promoted mapping needs positive, contradictory and edit/clear fixtures before release; no registry enumeration can certify itself.

Preprint archiveID/eprint uses metadata.number for other repositories; normalized arXiv aliases converge on extensions.identifiers.arxiv, as specified in records.md. Proceedings title is container-title, conference name is event-title. Thesis university/school and report institution converge on publisher. Publisher is a literal string in the core; multiple structured publisher lists require explicit reconciliation before flattening. Preserve the original list. Shortauthor/sortname are original presentation instructions, not additional authors.

The original four extensions are patent.assignees (ordered personal/literal names), patent.application_number (text), patent.priority_date (Date), and journal_series (text). Assignees are distinct from inventors, application numbers from granted numbers, priority dates from publication dates, and journal series from book/report series. The patent and journal-series fixture families must prove these distinctions; they are implementation obligations, not claims that the current probe exercises every extension. The fifth registered extension is extensions.identifiers with schemes arxiv and oclc, both supporting exact-value search. arXiv emits eprint={ID} and eprinttype={arxiv}; for misc or unpublished only, add note={arXiv:ID} when howpublished does not already carry it, retaining any supplied note. This is a documented fallback. OCLC is a documented omission. Journal series emits series. Patent assignees emit an Assignee note, never replacing inventors. Collection editors join editor on books with a documented role fallback; container authors emit bookauthor on book parts with a warning that classic styles may omit it. Other type scopes use documented omissions for these two roles. Contributors are omitted with a documented omission. Remaining approximate mappings are preserved-only. No unsupported extension is safe to emit merely because it has a registered path.

## Portable output in slice 1

`portable-bibtex-v1` is the only implemented slice 1 profile. It uses UTF-8, classic names and types, year/month, journal, address, school/institution, and doi/url/urldate when supplied. Recognized language tags emit langid; unknown literal values stay in the catalog with a documented omission and never block export. Text emits current Unicode values through a deterministic tested TeX serializer; verbatim URI fields are handled separately. Preserve corporate names and publisher/institution strings containing “ and ” by grouping the entire literal. Never execute or pass through arbitrary TeX from originals.

| Canonical type | Portable entry and decisions |
| --- | --- |
| article-journal | article; container-title→journal, issue→number, page→pages. An article identifier occupying pages needs a declared tested rule, not a guess. |
| article-magazine, article-newspaper | article; documented subtype downgrade; retain publication and issued precision, section in note when present. |
| book | book; publisher/address, edition, series and series number. |
| chapter | incollection when separately titled; traditional inbook with container title plus pages/chapter only preserves that form and does not invent a part title. |
| paper-conference | inproceedings; proceedings→booktitle, conference name retained separately in note. |
| thesis | phdthesis/mastersthesis only from a known supplied degree or preserved native subtype; otherwise misc with supplied genre/institution in howpublished. No degree guessing. |
| report | techreport; publisher→institution, genre→type, number→number. |
| article with preprint evidence, manuscript | unpublished; genre/repository and locator in note, eprint/archiveprefix when present. Preserve supplied URL; derive an arXiv URL only from validated arXiv identity and report derivation. |
| webpage, post-weblog, document | misc; URL and exactly supplied howpublished, re-emitted unchanged. Nothing moves into or is synthesized from note; emit note only when supplied, apart from the explicit arXiv fallback. No invented author/date. Ordinary misc is a known generic document, not automatically an unknown mapping. |
| standard | misc; number and authority in howpublished, supplied corporate author retained. Never project to legislation. |
| patent | misc; inventor as citation author, patent number/jurisdiction in howpublished. Supplied assignees/application/priority facts require an assessed projection or an unknown-mapping report, never inventor substitution. |
| speech | misc; presenter as author and event/genre in howpublished. |
| software | misc; programmer as author, version/publisher in howpublished and supplied locator. Programming language is not genre. |

Known subtype downgrades warn and are itemized in the export report; no projection-history table is stored. They are not unknown mappings. Richer profiles may later be selected only when a destination declares compatible consumers; unsupported profile requests fail rather than silently falling back. Quarto configuration detection may suggest declarations only. Portable output is tested with Pandoc citeproc, Biber and classic BibTeX/elsarticle-num. Compare rendered authors, issued dates, journal/institution, edition and protected spelling, not merely resolved keys. Golden outputs identify tool/style versions; schema validity and rendering are distinct evidence.

## Four-class policy

| Class | Outcome |
| --- | --- |
| Faithful but incomplete | Warn about missing citation facts; never invent values. Abstracts, context and tags retained in the catalog produce no report. Missing language warns only for titles containing non-ASCII letters. |
| Documented fallback | Warn with mapping ID and describe the fallback or documented omission, including preserved unmapped import fields, in this run's report. |
| Enumerated meaning-changing loss | Block. Stored waivers and export waive are backlog. |
| Unknown or unassessed | Block by default; `--allow-unknown-mappings` is a single-run override, listed per entry/loss in the report. |

Closed blocking-loss codes are `issued_date_lost_or_changed` and `work_identity_changed` (source/container/edition/version/identifying locator altered). The list grows only with a detector and a test. Omitting an access date is not equivalent to dropping issued date. Merely unprotected capitalization warns under the explicit user decision. A type downgrade alone is documented fallback; an observed consequence in this list upgrades it to blocking. A type or field mapping without a registry assessment belongs to unknown. Preserving an unmapped input field verbatim is an assessed omission, not an unknown transformation.

Structural errors cannot be overridden: invalid/unserializable key/value, case-insensitive duplicate portable keys, malformed output, or unsafe target. The command reports every affected entry in one pass. Blocked exports create no target/staging file and do not advance adoption. There is no stored loss waiver in slice 1. Unknown overrides cannot waive a known blocking loss; correct the record, change project selection explicitly, or leave the export blocked. The earlier scoped-waiver design is deferred, not silently replaced with a blanket override.

## Titles, dates and originals

Internal titles stay Title Case. Export adds braces for per-title protected terms and the whole-title flag. CSL-JSON output is deferred; an internal CSL projection for tests derives sentence case without rewriting storage. Comparison against Pandoc neutralizes its reader casing and deprecated event alias, while preserving raw oracle output. Original brace syntax remains evidence; accent or command arguments are not protection by default.

Dates preserve known precision. Portable year/month is faithful only for the mapped precision; ranges project to the start year and a month only when shared by both endpoints, with a per-entry date_range_projected documented-fallback warning. The full range remains in issued.date-parts; no range is emitted into note. Other unsupported uncertainty is reported under the appropriate loss class, never silently reduced. Missing fields warn; supplied issued facts dropped by projection block. Literal editions remain literal. A title-less inbook remains a part description, not a fabricated standalone chapter.

Only month macros are resolved natively in slice 1. crossref/xdata, arbitrary string concatenation and custom datamodels remain preserved and unresolved; an explicitly requested external flattening step must preserve original and flattened inputs with tool/version provenance. No custom inheritance subset is asserted to match BibLaTeX. BBT Extra is parsed only for registered keys/identifiers and scoped known fields; residual prose and directives remain evidence with limitations.

## Value-dependent assessment

Registry export_class is value-dependent; assessment_rule supplies the positive, loss and unknown branches. It is not an unconditional claim that a field is faithful. Single calendar dates may emit supplementary date in addition to legacy year/month to retain supplied day precision; the declared-consumer golden fixtures govern that mapping. The explicit range projection above is a documented precision fallback. Other supplied issued facts lost by projection are classified issued_date_lost_or_changed. Role omission must be assessed for the actual type and cited authors; translator is an assessed, documented omission in the portable profile. Core property fragments are not standalone JSON Schema: package and hash-check complete upstream definitions, then narrow with the profile enum/applicability.

## Traditional part records and remaining input dispositions

The traditional inbook branch runs before generic title mapping: if booktitle is present, title is the part title and booktitle the container. If booktitle is absent and chapter/pages is present, title becomes container-title, chapter becomes chapter-number, and no source title is fabricated. An explicit supplied citation key is required if no eligible source-title token exists. Reverse portable output uses inbook with title=container-title and chapter/pages. An inbook with neither container evidence nor part identification remains unresolved. The generic title row is explicitly excluded from this branch.

Zotero websiteTitle/blogTitle supply container-title for web/blog types; presentationType/manuscriptType supply genre on their types; company/versionNumber supply software publisher/version; bookSection series/seriesNumber supply collection-title/collection-number; patent filingDate supplies submitted. Bib issue supplies issue for article, keywords supply legacy_tags without taxonomy promotion, and file supplies resource-link proposals with parse limitations and no acquisition. Unsupported file expressions remain original evidence and a resource warning, not permission to copy or a bibliographic loss. Website/container, event and series omissions must be assessed explicitly for the target; absence of a row is never a safe default. Generic howpublished handling and composition with note are defined in records.md.
