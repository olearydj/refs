# Research and Revised Decisions

**Revised 2026-09-21.** The [independent audit](reviews/2026-09-20-independent-design-audit.md), particularly corrected sections 10–12, supersedes the earlier recommendations. The [baseline archive](reviews/baseline-before-revision-2026-09-21.tar.gz) preserves those documents. Audit experiments are preserved under reviews/evidence-2026-09-20; they were performed by the auditor, not reproduced wholesale here.

## R1. Model and scope

Select the demand-driven CSL-shaped core, optional native type and four bounded extensions. This follows the user's breadth choice and the individual [semantic row review](reviews/semantic-row-review-2026-09-21.md), not an assumption that CSL guarantees convergence. Fourteen [new probes](reviews/model-examples-2026-09-21/README.md) explicitly exercise candidate Zotero mappings and agent input, with Pandoc as a separate BibTeX oracle. They do not execute refs' future importer. Type-scoped aliases are mandatory; patent priority/application/assignee and journal series cannot be blindly collapsed. Zotero-shaped authority remains the coherent alternative if full Zotero vocabulary becomes a requirement.

## R2. Runtime and dependencies

Retain Python 3.14 as support policy, Typer by explicit user preference, strict Pydantic boundaries and SQLite. Audit dependency evidence supports Typer >=0.27.2 for public exception handling; own the JSON envelope and schema discovery. Pin bibtexparser==2.0.1 and pylatexenc==2.11. Use the former narrowly for raw syntax, with malformed-input guards; never use its writer as authority. Use the latter only for supported one-way non-verbatim decoding. Neither package establishes semantic or round-trip fidelity. A custom parser remains a higher-maintenance alternative to justify only through failed concrete gates.

Remove Unidecode. The user's observed non-ASCII surnames are Latin; select built-in Unicode normalization plus an explicit table and unsupported-name override. Record Unicode-data and policy versions; no silently dropped letters. AnyAscii with a strict refs filter is the named future fallback. The audit's count of 31 non-ASCII surnames and 13 first-creator occurrences is historical evidence, not a future script guarantee.

Use uv with the required portable three-day cooldown and locked checks. Exact runtime/dev dependency resolutions belong in the implementation lockfile. Exactly pin the evaluated ty version; a floating beta tool must not alter diagnostics in unchanged CI. The [dependency audit](dependency-audit.md) retains sibling-project observations, with its older package selections superseded here.

## R3. Output consumers and losses

Slice 1 implements portable BibTeX only because real destinations include Pandoc, Biber and classic BibTeX/elsarticle-num. Use year/journal/address/school and classic names, not a default BibLaTeX dialect. Web, standard, patent, presentation and software fallbacks are explicit rows, not arbitrary misc escapes. Standard must not become legislation: the audit and new probe show Pandoc's @standard classification differs from the intended source semantics. A correct bibliography can still lose authors/years while resolving every citation key, so rendering gates inspect fields and in-text output.

Four classes govern export. Stored waivers bind exact loss, revision and destination profile; unknown mapping overrides last one run. Structural errors remain unwaivable. Persist successful projections so re-import of an unchanged downgraded type is idempotent; citation key alone is not enough. Current corrections and deliberate deletion override originals. Fresh catalogs cannot recover richer types from lossy output without the projection evidence.

## R4. Titles, names and dates

Store Title Case Unicode with protected-term lists and a whole-title flag. Citation style governs export. Terms supersede offset spans. Protect corporate and institutional literals containing “ and ”. Pandoc reader title casing is neutralized in comparisons and its deprecated event alias is recorded, not interpreted as refs' own importer behavior. Name particle differences between unsplit Zotero names and BibTeX von parts require explicit preview/override rather than guessing equivalence.

Zotero free-text date and API meta.parsedDate are two pieces of evidence for one canonical date. Preserve both originals, validate precision and contradictions, and retain literal-only uncertainty when needed. Native month macros are enough initially; arbitrary inheritance/strings require explicit external preprocessing. The corpus contains legacy BibTeX date and publication aliases, so these are first-class input rows.

## R5. File effects and locations

Config remains ~/.config/refs/config.toml; cat/lib are visible siblings on Casa. Only lib may be synced. Agent access includes canonical catalog and library paths. Missing Casa fails explicitly with no alternate initialization. Downloads intake is cross-volume: build copy/verify/no-overwrite publication first; the source-link route is an optional slice 2 optimization. Stage in cat to avoid syncing partial files. Creation-date preservation across volumes is not promised. Metadata-aware native copy and identity-safe quarantined cleanup need destructive synthetic fixtures before move ships.

Only link creation is atomic; file effects and SQLite commit remain separate. Same-inode hard links are never backups. Process-death recovery is required; power-loss protection is best effort with fullfsync where supported. Digest equality alone cannot prove that an existing destination was created by the operation. Captured staging/source identity and a per-attempt nonce address this. Native platform behavior must be validated on actual supported filesystems, not inferred from pathlib names.

## R6. Migration and retained evidence

Use a one-time read-only extractor into a published JSON contract, versioned separately from the runtime. Certify the observed Zotero 6.0.37/BBT 7 route; do not require a legacy BBT SQLite file for all versions. Preserve per-entry originals in refs and a dated whole Zotero archive externally. Child notes become previewed imported context; no supporting_items subsystem. Keep simple related pairs. The authorized nine-PDF check found 239/240 matching annotations and all three comments embedded, but one malformed object needs a viewer check before retirement. This is presence/position evidence only.

A stale June BBT bibliography is a possible seed after explicit regeneration; it is not migration certification. Files may initially retain a named root outside lib, later relocated as an intact tree only when the user authorizes it. Root remapping plus checks and bulk filing assignment then require no per-file movement. Five vault notes with eleven old-path references are the measured external-link impact, not a reason to preempt the user's location choice.

## R7. Storage, recovery and complexity

Keep rollback journaling and short BEGIN IMMEDIATE writes. Close read snapshots before file intent writes. Read-only commands report required hot-journal recovery rather than silently mutating the database. Requests fingerprint payload/targets, recording settings separately so repair does not masquerade as a different request; captured effects still cannot be retargeted silently.

Snapshot unresolved operations as well as normal state. Demonstrate restore into a second catalog in slice 1. Full bundle/restore CLI and logical export remain later; inventories never claim file-byte backup. A minimal explicit reactivation preserves tombstone identity/key without a general undo system. Independent revision review corrected the proposed search deferral: constitution IV/V require a selectable entry-point boundary and an independently installed alternative proof as search is delivered. Keep that bounded slice 1 obligation; no general plugin manager is added.

## Evidence boundaries

The registry stores immutable schema URLs/hashes inherited from the audited baseline. The semantic reviewer consulted the pinned Zotero crosswalk but did not rehash it; no fresh certification is implied. The new probes are synthetic. No production database, manuscript, PDF or folder was mutated, and no runtime package was installed. Implementation gates in plan.md and quickstart.md remain to be executed.
