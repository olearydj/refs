# Code review: investigation, 2026-09-24

This is the reading half of the code review the owner asked for after slice 3 and then set aside while the tests pass runs: "for now, lets just treat this as a tests pass. we can come back to code review." It records what was found in `src/refs` at commit 473df8f. It decides nothing. The readers' line-level tables are in the [appendix](2026-09-24-code-review-appendix.md). The fixes wait for the test suite to be trustworthy, so that what they change is caught.

## Method

Three independent readings by module cluster, cross-checked against each other and spot-checked against the source: domain (models, naming, sources, importing, bibliography, languages, projects, collections, search); storage and files (catalog, files, moves, resources, recovery, config, the migrations); interface and adapters (cli, render, display, results, the four adapters, the two tools). The lens is the one the right-sizing page names and the project's ArjanCodes review calibrates: abstractions from actual variation; interfaces shaped by their consumer; application-owned types and errors at the boundaries; plain functions for transformations and classes only for state or lifecycle; a fix is a rule about a kind of value, not a branch on a specific one. One lens was added for the direction the owner named on 2026-09-23, an optional server database: every place SQLite leaks into domain code. Measurements were taken by script: function lengths, nesting, SQL distribution, the import graph, textual duplication.

Nothing was changed and nothing was run against the owner's data.

## Measurements

About 4,700 application lines in 27 modules, 219 functions, 23 classes. Seventeen functions exceed 40 lines. The BibTeX serializer is 282 lines with eight levels of nesting; the BibTeX parser 154 with eight; the configuration loader 76 with eight; the BibTeX partitioner nests nine deep. SQL appears in eleven modules: importing has 36 statements, projects 18, sources 17, resources 15, bibliography 13. There is no storage layer; 29 functions take a raw connection. Thirty-one imports sit inside function bodies, most breaking cycles: resources and moves import each other, sources and importing import each other, results and render import each other. Textual duplication is negligible, one repeated three-line window in the tree; the duplication that exists is semantic, the same rule written differently in several places.

## What was found

The code is sound where it must be. No traced path deletes or overwrites a file the contract says must survive; the move journal, the digest-guarded export and the identifier normalization at the validator are the three pieces every reader named as models. The problems fall into seven themes, each with a rule behind it.

### 1. Liveness and correctness at the edges of the move protocol

The protocol itself conforms to the rewritten contract step for step, including the two things the review changed: revisions are rechecked in the recorded transaction and not before deletion. What the readers found sits beside it.

- A move that fails before the recorded state keeps the source revision, resource revision and loc it captured at creation and never refreshes them. Edit the source afterwards, or unlink the resource, and every retry fails the same check forever. Because `reorg --execute` resumes unfinished operations first and stops at the first error, one stuck row blocks every unfiltered reorg, and there is no command to clear it short of SQL. Nothing is lost; both files survive. The rule: a retry of a pre-recorded operation re-plans from fresh facts rather than repeating a check that can no longer pass.
- A re-run of a completed move intake whose original is gone takes the resume branch, and if a later reorg has since moved the file, creates a new operation that moves it back to its old intake destination, unpreviewed. The rule: resume only an unfinished operation; a finished one whose path is gone returns the current resource.
- The already-recorded admission runs only for intake. Reorg will move a file that two resources record, the first move deleting the original from under the second. The owner's data has no such file today. The rule: the admission check is a property of a move, not of the intake route.
- `reorg` catches only refs's own errors, so an OS error during staging, a SQLite busy error from a plain writer, or Ctrl-C loses the accumulated old-and-new path report the contract promises for repairing outside references. The pairs remain in the journal, but nothing lists them.
- The Zotero import path catches programming errors around its writes and records the entry as invalid while the surrounding connection commits, so a partly written source with an invalid entry is possible. Latent, since it needs a bug after the write, but the catch should wrap only the adapter boundary.
- The duplicate-attachment rule from the last fix batch runs only on `resource add --copy` without a resource id. The contract's documented remedy for a partial copy, retrying `resource add --copy`, now always reports a duplicate because the linked original has identical bytes, so the link can never become a managed copy. The rule was placed on one route rather than on the kind of operation.

### 2. Boundaries: the CLI does domain work, the domain does storage work

- `add` in the CLI dispatches on format to two services, sets loc in a second transaction after creation so a crash between leaves the source without loc, decides the intake default, and validates loc itself. `resource add` repeats the intake dispatch that `capture_file` also performs. `execute and not dry_run` is written four times. Cite and uncite re-read the record only to feed the text renderer, so JSON never carries the project name or key. The contract's own docstring says services return ordinary values and the CLI reports them; the code has grown past that.
- Every domain module writes its own SQL. A change of backend today touches six domain modules. The record-to-editable-dict conversion is written five times, the pop-key-validate-reattach sequence five times, deep copy by JSON round trip six times, key allocation twice with only one validating the key. Optimistic checks rely on SQLite's database-wide write lock: the revision-guarded update never checks its row count, and key and project allocation are select-then-insert with no translation of integrity errors. Safe under `BEGIN IMMEDIATE` today; on a server at read-committed isolation, writes would be lost silently or driver errors would escape.
- Search loads every active record through the full six-query record loader and filters in Python; the plan says the boundary takes filters, limit and offset and returns identities. Over a network this is thousands of round trips per search.
- Errors from reading the user's input files are mapped to storage failures with exit 5 and the message "allow access to the selected path", because `main` catches every OS error as storage; the contract says invalid input is exit 2. Every failure envelope names the command "invocation", so a JSON consumer loses which command failed. Any exception outside the handled set prints a raw traceback. Lock detection is a substring match on "locked".

### 3. The registry is not the authority the docs say it is

The right-sizing page says mappings live in the registry table the exporter reads, not in branches of its code. The importers do read the registry's rows. The exporter does not: thesis degree strings, container targets by kind, note labels, identifier targets and publisher targets are branches in a 282-line function. Every registry row carries a `portable_projection` and an `export_class`, and nothing reads them; their values are prose such as "omit with report" and "school or institution by type", so they could not drive code as they stand. There are two sources of truth for one mapping, one of them human-readable only, and drift between them is silent. The choice is between making the column structured or declaring the code the authority and the column documentation.

### 4. Rules written as patches, and rules written more than once

Patches, by the project's own definition: the renderer rewrites a domain message for one code and sniffs `@misc` in a message to choose a description; the unparseable-Zotero-item case is a fake `itemType` sentinel; a protected-term notice keys on the letter R; limitation matching keys on message prose that another module builds; an alias conflict is classified three ways across the three import routes; the collision check in the copy planner runs early only when a label is given.

Rules written more than once with drift: path equality, NFC plus case folding, in six forms; identifier equivalence, DOI-only in one place, DOI and ISBN in another, five schemes in a third; the arXiv archive test in three places; the filename fallback condition in two; the misplacement test in two; the schema version in about twelve, including a chain in recovery that must be edited by hand for every migration or backup breaks; month tables in three modules; person-name joining in four.

### 5. Dead code and error codes

Dead: `naming.edition_display`, `catalog.migrate` (tests only, and it bypasses the lock and the safety copy), the origin-match branch in copy, a repeated version check in recovery, a one-element loop in the BibTeX adapter, project and collection revision columns that are incremented and never read, the `SourceRecord` and `Result` models that exist only to print a schema and never validate anything.

Error codes: about ninety are raised. Eight are unreachable, among them the three export blocking-loss codes for cited authors, in-text citations and protected spelling, which the test investigation also found are never emitted, and the `integrity_error` that is caught and rewrapped before it can escape. Some fifty are reachable but no test asserts them by name. One code, `integrity_error`, carries exit 3 in one module and exit 5 in two others.

### 6. What a server backend would cost today

SQLite-only SQL in domain modules: `json_extract` in joins, `INSERT OR IGNORE`, `ON CONFLICT ... excluded`, `rowid`, `instr` over a cast blob, FTS5 through a direct import. Positional inserts with no column list in six places. Row objects read past the query in importing and bibliography. Transaction boundaries chosen by domain code: an import is N plus three transactions, an export four or five. Five things are tied to the catalog being a directory: the database file, the ready marker, the lock file, staging and the safety copies; config has no notion of a connection string. None of this is wrong for SQLite. It is the list of what "optional Postgres" would have to move, and it is longer than the seam argument assumed.

### 7. The human-output renderer

The success renderer is a dictionary of one-line lambdas keyed by command name, several of them two-hundred to four-hundred characters of nested conditionals, followed by four command-specific post-processing branches. Error rendering lives in a different module, with branches on specific codes. Upgrade notices go to stdout in human mode where the contract says stderr. Warnings are carried twice in the JSON envelope. The plain-table pass in the human-output notes would replace this outright; what survives is the value formatting helpers, the warning grouping logic, the per-entry import walk and the preview prefix rule.

### The three best pieces, by consensus

The move journal and state machine, about sixty lines carrying the whole contract, publication proven by inode and deletion guarded by file facts only. `RefError` with the result envelope, one application-owned error with a validated exit code and a data field for partial results, converted in one place. Identifier normalization at the validator every route passes through, with the pinned, hash-checked tables in naming and languages beside it. Also named: the BibTeX partitioner that frames raw byte spans and refuses rather than guesses; the search adapter at 36 lines with an application-shaped result and no speculative interface; the digest-guarded export that finishes an interrupted publish on re-run.

## Contract and command surface, noted in passing

Beyond the drift the test investigation found: `import --input -` fails because that option is typed as a path; `project cite --from-import` exists and the contract does not name it; every boolean option has a generated `--no-` twin in help, including `--no-no-project-config`; typed choices are plain strings so help shows no options; and there is no help text on any command but `open`, which the help pass already owns.

## What the brief must decide

- Which of the liveness findings are fixed now and which wait for an incident: stuck operations, the intake re-run, shared originals, the lost report. All four are small; the first has no escape without SQL.
- Whether a storage layer is worth its cost now, or whether the server direction is served by narrower moves: the record and revalidate helpers, integrity-error translation and row-count checks, filters pushed into the search boundary, and no new SQLite-only SQL.
- The registry: structured projection column or code as authority.
- The CLI boundary: one domain entry per command, with loc set in the create transaction and the intake default resolved in one function.
- The dead code and unreachable codes: remove, or keep with a reason.
- How much of this joins the human-output and help passes rather than standing alone, since the renderer, the notices, the envelope duplication and the typed options all fall inside those.
