# Right-Sizing refs

**Status:** Owner-approved working guardrails, 2026-09-21. The short operative form lives in [AGENTS.md](../AGENTS.md#right-sizing); this page holds the calibration behind it. Keep this page short. It is a guardrail, not a process.

## The standard

The owner's words: refs "should be good, well designed, professionally built and packaged, not elaborate." On the owner's scale, 1 is a crude hacked-together script, 10 is comically over-engineered for what it does, and 5 is exactly right-sized. The score is engineering weight relative to what the tool does, not quality. "The durable human contribution is judgment": agents measure and ask; the owner decides.

Where refs stood on 2026-09-21: the plan as first written, about 8.5; the direction after the nine recorded decisions, about 6; slice 1 as the owner scoped it, 5. Landing at 5 depends on the revision and the build, not on the decisions alone.

## Calibration against sibling tools

Scored 2026-09-21 from READMEs and measured structure, not from deep code reading or use. The owner's experience overrides these.

| Tool | Job | Source lines | Commands | Classes | Doc words per source line | Score |
| --- | --- | --- | --- | --- | --- | --- |
| git-muster | Local Git branch report | 800 | 1 | 4 | 1.5 | 5 |
| secretpath | Resolve secrets | 1,070 | 8 | 8 | 7 | 5 |
| course-courier | Publish selected course files | 1,450 | 5 | 11 | 9 | 5 |
| canvas-ledger | Personal SQLite ledger of Canvas history | 6,730 | 28 | 52 | 2.8 | 6.5 |
| danvas | Day-to-day Canvas management, with writes | 27,200 | 62 | 70 | 3.6 | 6 |
| danner | Read-only course-schedule lookup | about 6,700 hand-written | 7 | 99 | 12 | 7.5 |

Reading: git-muster and secretpath are the build-quality target (small, tested, packaged, published, deliberately unconfigurable where possible). canvas-ledger is the nearest relative in kind and a size ceiling for the whole product; slice 1 should land well under it, and without an ORM. danvas is large because it does a lot against a live system where the safety ceremony earns its keep; its structure is, if anything, under-abstracted. danner is the trajectory to avoid: a small job that accumulated layers, versioned contracts, spec features and documentation until the scaffolding outweighed the tool. Tools started since July under spec-driven, agent-heavy authoring carry 5 to 12 doc words per source line; the earlier ones carry 1.5 to 4. The drift toward 7 is a property of the process more than of any one project, which is why these guardrails attach to checkpoints.

## Budget, floor, and rules

- *Slice 1 budget:* about 12 commands, 7 tables, 4 runtime dependencies, 3,000 source lines. Exceeding a figure is allowed after naming the incident in the owner's workflow that it prevents and asking the owner.
- *Seams, not surface (owner's allowance, 2026-09-21):* "it is natural for well-architected systems to add some up-front overhead that might move us from a 5ish to a 6ish in the first slice ... a reasonable, metered, up-front investment in good design." Slice 1 may reach a 6, about 15 commands, 10 tables and 3,500 lines, when the extra is a seam: cheap now, hard to retrofit. Examples: result envelope and exit codes, schema discovery, record revisions, per-entry originals, native type and origin identity columns, a minimal human-correction marker, schema versioning with a plain migration runner, domain logic separate from Typer and SQLite, an internal search boundary, digest-guarded export. Surface waits for its slice or its first real incident: export waivers, projection records, the operations journal and recover commands before destructive moves exist, batch resume and reconcile before the large migration, the plugin entry point and proof package before a second search implementation, and convenience commands. The test: if it can be added later without a migration or a re-import, it is surface.
- *Documentation:* refs had about 44,000 words of governing text before any code. Revisions should reduce that total. Target by the end of slice 1: no more than about 4 doc words per source line.
- *Never cut:* stable citation keys; preserved original entries; no overwrite and no delete before a verified copy; a backup that has been restored once; explicit-only export. Right-sizing pushes down; this list is the floor.
- *Provenance:* a MUST needs a quoted owner decision or a visible "proposal" label. The 8.5 came from a recommendation becoming a requirement unnoticed, not from a love of structure.
- *Use before extend:* no slice 2 specification work until slice 1 has been used on one real paper.
- *Two questions before adding anything:* which incident does this prevent, and which actual variation does this structure serve? If neither has an answer, it goes to the backlog. Deferred, not dismissed.

Historical items accepted before the first checkpoint and now deferred by audit §14: export waivers scoped to loss, revision and profile; request-ID replay outside file moves; per-field provenance; batch reconcile machinery before the 562-entry migration; the multi-file library export.

## Right-sizing the planning

The guardrails above size the product. This one sizes the effort spent specifying it. By 2026-09-21 refs had about 50,000 words of governing text, 25,000 words of reviews, several agent sessions and some twenty owner judgment calls, for a first slice of about 3,500 lines and no code yet. The findings that mattered (the duplicated model, the export default that would have stripped a real manuscript, the obsolete Zotero input) came from experiments on the owner's real data and from direct questions, not from specification prose. Agents produce text at no cost, so the usual brake on documentation is missing and has to be explicit.

- *Planning budget:* governing text for a slice stays near 4 words per expected source line, and planning takes less time than building. A breach prompts the usual question: what does more planning protect against here?
- *Plan what is costly to reverse; discover the rest by use.* Key format, canonical model, data locations, export dialect, anything that can destroy a file, and migration deserve up-front thought. Which commands get used, which warnings get ignored and what is annoying are answered by working code on a real paper.
- *Lighter loop for later slices:* a one-page brief (outcome, decisions needed from the owner, what must never break), the owner's answers, a small experiment on real data where there is risk, tasks, build, use. Reserve full specification and independent audit for the risky pieces: the move-with-delete protocol and the Zotero migration.
- *The owner's attention is the scarce resource.* Ask for judgment, not confirmation.
- *Shrinking means removing content, not compressing sentences.* A trimmed document must still read as plain prose to someone new to the project: full sentences, terms defined or avoided, no slash-joined lists standing in for explanation. Review for this after any large trim.

## Checkpoints

Each is about ten minutes of measuring by an agent and one judgment by the owner. A breach prompts a question; it never blocks.

| When | Measure | Owner decides |
| --- | --- | --- |
| Revised spec returns | Commands, tables, dependencies, MUSTs without provenance, total governing words against 44,000, a 1 to 10 score | Anything over budget |
| Before task generation | Tasks cover slice 1 only; nothing from the backlog is being built | Go or trim |
| Slice 1 code-complete | Source lines, commands, classes, doc words per source line, beside git-muster and canvas-ledger | Whether it feels like a 5 in use |
| After one real paper | What was reached for and missing; what was never touched | What enters slice 2; what leaves the backlog for good |

### Slice 2 code-complete, 2026-09-22

Measured after the owner-executed Zotero cutover: about 4,130 application lines, roughly 1,000 over slice 1 against an estimate of 800; 14 tables (four added, approved); 4 runtime dependencies, unchanged; 500 tests; 23 classes, unchanged; 6 new invocations. The overrun is six rule-level fixes from rehearsing the real import against a copy of the owner's library (ISBN binding guards, identifier and language normalization, five portable projections, date ranges, the extractor's version row), each carrying a regression test from the real shape that motivated it. Score holds at 6. The rehearsal harness earned its place: the synthetic fixture passed while hiding a defect the first real run exposed in the first second.

### Slice 3 code-complete, 2026-09-24

Measured after the owner-executed cutover: about 4,700 application lines against 4,130 at slice 2, an increase of about 570 against an estimate of 700; one column and one table added; 4 runtime dependencies, unchanged; 592 tests; 23 classes, unchanged; one new command, `reorg`, plus `--loc` and the intake flags. Score holds at 6. The move protocol was specified in full, independently reviewed, rewritten once as plain prose, and rehearsed on a copy of the whole library with two kill-and-resume cases before it touched a real file. The one defect that reached the real run, a file-descriptor leak in the automatic schema upgrade added after the rehearsal, stopped the move after 31 files with nothing lost, was fixed with two regression tests that reproduced it, and the same command resumed to completion. The rehearsal earned its place again, and so did the rule that an interrupted move is finished by running the command again.

### Tests pass complete, 2026-09-24

Measured after the pass: 624 tests, split 71 unit, 158 contract, 85 integration, against 592 before, with 49 rewritten and none deleted; 87 percent combined line and branch coverage by the command recorded in the acceptance record, reported as a data point and not gated; one development dependency added, hypothesis; runtime code changed only for the protected-term warning, init's sync caution, and three rules the corpus produced. The rehearsal harness now kills the command itself at ten boundaries and cleans up after itself; the corpus harness ran 18 files and 3,949 entries in under six minutes and 409 MB, found two importer gaps and one message, and stated five limits. Score unchanged at 6; the weight went into confidence, not surface.

### Code review fix pass complete, 2026-09-25

Measured after the four batches merged: about 4,990 non-blank application lines by the method the earlier checkpoints use (the acceptance record counts every line and reports 5,712 against 5,304 at the brief), an increase of about 400 by either method; 700 tests; no new runtime dependency, one development dependency (pytest-xdist) added by the small batch beside it. Where the lines went, by batch: about 100 in four liveness rules for the move protocol, so a failed move re-plans, a finished intake does not re-run, shared originals are reported and the path report survives any exit; about 30 in logic that left the command layer for the domain, loc inside the create transaction and one intake-mode function; about 25 in adapters taking ownership of their formats and duplicated rules collapsing to one; about 115 in this pass's last batch, splitting the 282-line serializer and three other long functions by concern and replacing hand-written configuration validation with a model. Removed alongside: dead functions, one-value parameters, the tests-only migration path that bypassed the safety copy, and every error code nothing could reach. The export of the whole library is byte-identical before and after. Score holds at 6; the added weight is rules where there were omissions and names where there were paragraphs, and the owner chose to keep it rather than rework tested code to a number.

### Performance batch complete, 2026-09-25

Measured after the batch merged with corpus round three's last fixes: about 5,160 non-blank application lines against 4,990 at the fix pass, of which the batch itself is under 100 (one migration, the search side table's upkeep, a title plan, one split query, one aggregate listing) and the rest is the CSL array import route and the census; 16 tables, one added, search_rows, beside two indexes; 4 runtime dependencies, unchanged; 721 tests, seven of which pin the fixed costs by query plan and statement trace rather than by timing. Measured on a copy of the 27,781-source catalog: first-time import 356 to 6.3 ms per entry, `project cite --from-import` 12.5 s to 0.24 s, `import list` 14.5 s to 0.22 s; the corpus gate that took 153 minutes took 183 seconds with 14 workers. Score holds at 6. The weight is an index and a side table for a cost that grew with the catalog, which is the seam kind the allowance names; nothing was added for a case not yet met, and the parallel driver lives in the harness, not the product.

### Types and kinds complete, 2026-09-26

Measured after the batch merged (0f131dd, five commits, [acceptance](../specs/001-academic-catalog/reviews/2026-09-26-types-and-kinds-acceptance.md)): about 5,310 non-blank application lines against 5,160 at the performance batch, an increase of about 150, of which 70 is the kinds module and the rest is the projections, the deferred-type details and the options; 834 tests against 721; 4 runtime dependencies, unchanged; no table; one new command, `kinds`, for 29 invocable commands counting subcommands, and a `--kind` option on add, update, list and search. The registry grew from about 4,500 to 6,950 lines, all data: nine admitted types with their spellings and field applicability, ten deferred types, five kinds. Nine CSL types admitted, five spellings mapped onto existing types, and every remaining unsupported kind refuses by name with the CSL type that would admit it. Score holds at 6. The weight that matters is data in the registry that the importers read, one derived name over existing fields, and one optional guard; the exporter gained one branch, keyed on the registry's projection, and every existing export is byte-identical. The corpus rerun through the parallel driver admitted 437 more entries and changed nothing else.

## Design lens

Once there is code, apply a restrained ArjanCodes-style review, calibrated in [the project's own review](arjancodes-review.md): abstractions emerge from actual variation; interfaces are shaped by the consumer; application-owned types and errors at the boundary; plain functions for transformations and classes for state, lifecycle or invariants; replaceability proven by two real implementations. Speak up at a new abstraction, interface, hierarchy, dependency or layer, in that review's format: principle, the concrete change, the simpler alternative, evidence the boundary helps, any deliberate departure. It is a lens, not a doctrine.

## Rules, not patches

Bibliographic data does not run out of quirks: identifiers copied between records, one arXiv ID written three ways by one translator, chapters carrying their book's ISBN, class suffixes glued to values, translator overflow in Extra. Each invites a special case at the place it was found, and a few dozen of those make the importer unreadable. The test applied to every such fix, from the 2026-09-23 rehearsal onward: does it add a rule about a *kind* of value, or a branch about a *specific* value? "arXiv identifiers are normalized by stripping the prefix and class suffix, at the validator every route passes through" is a rule; "if the string contains `[cs]`" is a patch. "An identifier binds only under these evidence conditions" is a rule that covers chapters, box sets and mistyped ISBNs at once; three fixes for those three cases would be patches. Importers read the registry's mappings; the exporter currently uses its own branches. A later pass will rewrite it against a structured registry. When a fix can only be written as a branch on a value, it waits until the rule behind it is visible. The real-input rehearsal harness (`tests/fixtures/real-trial/`) is where quirks are meant to surface first, and each rule keeps the real shape that motivated it as its regression test.
