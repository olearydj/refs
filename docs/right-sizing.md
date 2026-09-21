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

## Design lens

Once there is code, apply a restrained ArjanCodes-style review, calibrated in [the project's own review](arjancodes-review.md): abstractions emerge from actual variation; interfaces are shaped by the consumer; application-owned types and errors at the boundary; plain functions for transformations and classes for state, lifecycle or invariants; replaceability proven by two real implementations. Speak up at a new abstraction, interface, hierarchy, dependency or layer, in that review's format: principle, the concrete change, the simpler alternative, evidence the boundary helps, any deliberate departure. It is a lens, not a doctrine.
