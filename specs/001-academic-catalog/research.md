# Research and Design Rationale

**2026-09-21.** This is an evidence index, not a second requirements document. [Audit §§10–14](reviews/2026-09-20-independent-design-audit.md#10-addendum-2026-09-21-corrections-after-review-by-the-authoring-session) correct earlier findings and record owner decisions. Historical findings/counts remain unchanged; the approved trim supersedes earlier machinery recommendations.

## Model and bibliography

The [semantic row review](reviews/semantic-row-review-2026-09-21.md) distinguishes actual shared meanings from approximate Zotero/CSL mappings. [Fourteen synthetic probes](reviews/model-examples-2026-09-21/README.md) compare candidate mappings, agent input and Pandoc as a differential oracle; they do not execute refs' importer. Type-scoped aliases are essential: article number and report number are different facts. Patent assignee/application/priority and journal series justify bounded extensions. Zotero-shaped authority remains coherent for full Zotero breadth, which the owner did not choose.

Actual writing uses Pandoc, Biber and classic BibTeX/elsarticle-num. Portable output therefore retains year/journal/address/school and classic types. The standard fixture shows why resolving a key is insufficient: a wrong type can remove the author in rendered output. Preserve corporate “ and ” names, title protection, issued precision and explicit distinctions through tested mappings. Parser corruption counterexamples and raw output are in [audit evidence](reviews/evidence-2026-09-20/README.md); use guarded bibtexparser and pinned one-way decoding rather than inventing a parser.

## Architecture and weight

[Dependency research](../../docs/archive/dependency-audit.md) documents sibling packages and the owner's Typer preference; current versions are in plan.md. Latin-only normalization/table was explicitly chosen over a transliteration dependency. No new dependency or current-version claim is made here.

Slice 1 has no destructive file intake. Retaining sources and refusing collision makes a complete unregistered copy safe to inspect after interruption, without durable journals. Export uses digest authorization and atomic publication; a crash before baseline commit causes conservative conflict on retry. Backup uses SQLite's snapshot API and a demonstrated separate-home restore. These narrow guarantees replace the earlier journal/replay surface, not the preservation floor.

Constitution 2.0.0 moves plugin selection and replacement proof to the second implementation. The internal search boundary stays. Correction markers and originals replace a provenance table; cited-only projects keep the cited column as a cheap future seam. Projection history, stored waivers and batch reconciliation wait for a real incident. Consequently, lossy re-import can report a conflict without overwriting, and known meaning-changing loss stays blocked.

## Limits

The audited library/annotation counts are historical observations, not new permission to access or move private data. Later Zotero migration retains its existing note/archive decisions and the one malformed-annotation viewer check; it is outside slice 1. No live migration, consumer certification or restored implementation has run. First-paper use and the right-sizing checkpoint remain explicit gates.
