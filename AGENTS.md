# refs

refs is a personal SQLite source catalog with an agent-friendly CLI, initially focused on academic references and explicit bibliography export.

## Read Order and Authority

Read `PROJECT_CONTEXT.md`, `docs/README.md`, and the latest relevant `.ho/` note. Follow the index into task-relevant documents rather than reading every research note by default.

Explicit user decisions take precedence. `docs/vision.md` owns product intent; `docs/behavior-decisions.md` records accepted conventions. Commands and configuration in review drafts are proposals, not approved contracts. Consult the current task before progressing from requirements to specs or implementation. A Spec Kit template is not an adopted constitution.

## Operating Rules

- Keep Markdown narrative paragraphs on one physical line.
- Prefer source inspection and purpose-built tools. Ask before browser or desktop automation unless explicitly authorized for the current scope.
- Treat Zotero catalogs, manuscript bibliographies, and externally linked files as read-only during research. Use read-only SQLite connections. Do not perform migration or relocation merely to investigate it.
- Preserve assigned citation keys and existing linked filenames. New copy intake renames by the accepted convention unless --keep-name; later reorganize preserves names. Export bibliographies only on explicit invocation. Collection membership changes do not automatically move files.
- Distinguish linked-in-place resources from managed placement. Refer to accepted A2 before making assumptions about collection or file behavior.
- Use `adhoc-python` for ad hoc investigation until the project has its own managed environment; then use that environment for project work.

## Right-Sizing

The [testing convention](docs/testing-convention.md) governs test expectations, refusals, fault injection and generated cases.

refs aims for a 5 on the owner's scale (1 crude script, 10 comically over-engineered): good, well designed, professionally built and packaged, not elaborate. Calibration, reference tools, and checkpoints are in `docs/right-sizing.md`. Agents measure and ask; the owner judges.

- Slice 1 budget: about 12 commands, 7 tables, 4 runtime dependencies, 3,000 source lines. Going over is allowed only after naming the incident in the owner's workflow that it prevents and asking the owner.
- Owner's allowance (2026-09-21): slice 1 may reach a 6 (about 15 commands, 10 tables, 3,500 lines) when the extra weight is a seam: a boundary or invariant that is cheap now and hard to retrofit, such as the result envelope, revisions, per-entry originals, identity columns, schema versioning, domain and adapter separation, and an internal search boundary. Surface that is easy to add later (extra commands, tables, and machinery for cases not yet met) stays within the 5 budget or goes to a later slice.
- Governing docs shrink during revision; they do not grow. Shrink by removing content, not by compressing sentences: trimmed text must still read as plain prose to a newcomer.
- Planning is budgeted too: governing text for a slice stays near 4 words per expected source line, and planning takes less time than building. Plan what is costly to reverse; discover the rest by using working code. Ask the owner for judgment, not confirmation.
- Never cut: stable citation keys; preserved original entries; no overwrite and no delete before a verified copy; a backup that has been restored once; explicit-only export.
- A MUST needs a quoted owner decision or a visible "proposal" label.
- Use before extend: no slice 2 specification work until slice 1 has been used on one real paper.
- Before adding anything, ask which incident it prevents and which actual variation the structure serves. No answer means backlog: deferred, not dismissed.

## Context Maintenance

Keep durable decisions in the project-native docs and this bootstrap lean. Use the handoff skill for explicitly requested transient `.ho/` notes. Keep `PROJECT_CONTEXT.md` a thin source map rather than a duplicate requirements document.
