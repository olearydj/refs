# Near-Earth Object Monitor conversion execution — 2026-09-27

**All four entries match the approved proposal exactly.** Both native PDF consumers rendered successfully, and all six in-text author-date citations are identical to the proposal. The no-record gate exits **3**, solely for two absent accepted fixtures. The accepted fixtures were recorded, the publication was adopted at `e2231a7`, and both post-adoption checks pass as described below. No refs branch merge has occurred.

## Backup and scope

Session 1 approved the [proposal](2026-09-27-near-earth-object-monitor-proposal.md) in `comms/2026-09-27-211050-s1-neo-approved.md`, under the owner’s verbatim authorization: “ok, let's see if you and codex can one shot this”. This explicitly accepts AGU displaying the bibliography’s existing July 23 retrieval date. Execution uses `s2/neo-monitor-execution` from proposal merge `3f17ec0`.

Backup `/Volumes/Casa/refs-backups/2026-09-27-before-near-earth-object-monitor-conversion` validated before intake and again after the gate: catalog `c03298ee-caee-4e20-aa0c-ddf121aafc0a`, schema 6, revision 4775. Manifest member hashes/lengths, database integrity and foreign keys, schema and resource inventory all validate. External resource bytes are not included in this catalog backup. Final audited catalog revision is 4793.

## Inventory and consumers

One refs project, `near-earth-object-monitor`, has exactly two cited members. Both PDFs cite `nasa-neows` once and `cneos-pha` twice. One planned target, `reports/references.json` using `csl-json-v1`, serves both native consumers: ordinary Quarto PDF with default Chicago author-date, and `agu-pdf` with the bundled AGU CSL and class. Both use citeproc and LuaLaTeX; no engine or style change is needed.

The register selects the existing saved July 20–26 executed Markdown and figures from `.quarto/_freeze` explicitly. At the initial gate its scratch preparation checked citation keys, substituted the JSON bibliography in the scratch documents, and rendered without executing Jupyter. After adoption it retains the current source front matter with the saved computed body; no bibliography rewriting remains. It excludes `.env`, `.repo-retro`, live data/logs, caches and generated artifacts. The whole native publication layout renders; fresh NASA feed acquisition is outside this bibliography gate. This is the same approved boundary used for the proposal.

## Import outcomes by key

Import `db793fe1-0384-4f8c-8efa-b59747c2aa24` applied **2 new, 0 unchanged, 0 conflicts, 0 invalid**, with origin `near-earth-object-monitor`. Both original BibTeX entry byte strings were verified against immutable `import-applied` originals. Keys are unchanged; no filtered-out or uncited entry, existing-source reuse, relationship or identity substitution was required.

| Key | Outcome | Membership |
| --- | --- | --- |
| `nasa-neows` | Imported and completed | Cited |
| `cneos-pha` | Imported and completed | Cited |

## Record completions by key

Both records are webpages, with the approved existing corporate authors, titles and URLs. NASA’s site title is `NASA Open APIs`; CNEOS’s is `Center for Near Earth Object Studies`. The contradictory imported native `misc` labels were cleared, and the approved title protection applied (`NeoWs`, `NASA`, `APIs`, `PHA`). Bibliographic `accessed` remains **2026-07-23** for both; no issued date was invented. Revision-guarded CLI updates retained import provenance and appended the approved user-attributed date policy plus agent-attributed capture provenance.

Final metadata and protection equal the approved admitted records. The current CSL export is byte-identical to the proposal, SHA-256 `d5e6117bbebe6f7d375c8daeebbab2489a08572ce880a44554fb00d2626ed6fc`. No live publication export was performed.

## Sources found, fetched, and the fetch list for the owner

Both sources were acquired and attached; there is no owner fetch list or missing-source gap. NASA’s single JSON capture retains the landing HTML and complete official API-content JSON response containing NeoWs, not merely the empty JavaScript shell. CNEOS’s capture retains its complete glossary HTML response. Every member has its URL, retrieval timestamp, byte length and digest. All requests used ordinary curl certificate validation, without a browser or TLS bypass.

Captures were acquired September 27 in the owner’s local timezone, with corresponding September 28 UTC timestamps inside the records. Their actual timestamps are resource content and context, separate from the historical July 23 bibliography dates. The notes explicitly do not claim that these current captures establish what the pages contained on July 23.

## Attachments with final names and hashes

Both single-file captures were moved through `resource add --move --label capture`, after destination previews. Final files and their embedded member bytes were independently rehashed; scratch originals are absent after verified moves. The CLI’s naming rule retains these JSON filenames in managed `unfiled` placement.

| Key | Final path | SHA-256 |
| --- | --- | --- |
| `nasa-neows` | `/Volumes/Casa/refs/lib/unfiled/nasa-neows-capture.json` | `9915952b20eda44f2dfc870ecb334398c65347359cc9c5e51b054a8ceea2cb0b` |
| `cneos-pha` | `/Volumes/Casa/refs/lib/unfiled/cneos-pha-capture.json` | `eb4e9d3778fe90c89a6ab56bfae90c7b5b0b7b8f68aa44f8b3a808a0a573edc1` |

## Export gate table

Fresh no-record gate `/private/tmp/refs-neo-gate-01`, Quarto 1.10.18, Pandoc 3.10, LuaHBTeX/TeX Live 2026 and Poppler 26.09.0. Each actual string below equals its proposal prediction exactly. The before strings are the verified original-PDF baseline from the proposal. No entry is missing, no citation number changes (both lists are author-date), and all six inline citation strings remain identical. Only deliberate webpage formatting changes occur; the AGU site-name omission is its unchanged native style behavior, disclosed in the proposal.

| Consumer | Key | Before | Actual after | Assessment |
| --- | --- | --- | --- | --- |
| `neo-report` | `cneos-pha` | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. n.d. Glossary: Potentially Hazardous Asteroid (PHA). Accessed July 23, 2026. https://cneos.jpl.nasa.gov /glossary/PHA.html. | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. n.d. “Glossary: Potentially Hazardous Asteroid (PHA).” Center for Near Earth Object Studies. Accessed July 23, 2026. https://cneos.jpl.nasa.gov/glossary/PHA.html. | Expected; exact proposal match |
| `neo-report` | `nasa-neows` | National Aeronautics and Space Administration. n.d. Asteroids NeoWs: Near Earth Object Web Service. Accessed July 23, 2026. https://api.nasa.gov/. | National Aeronautics and Space Administration. n.d. “Asteroids NeoWs: Near Earth Object Web Service.” NASA Open APIs. Accessed July 23, 2026. https://api.nasa.gov/. | Expected; exact proposal match |
| `neo-report-agu` | `cneos-pha` | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. (n.d.). Glossary: Potentially hazardous asteroid (PHA). Retrieved from https       :// cneos.jpl.nasa.gov/glossary/PHA.html | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. (n.d.). Glossary: Potentially Hazardous Asteroid (PHA). Retrieved July 23, 2026, from https://cneos.jpl.nasa.gov/glossary/PHA.html | Expected; exact proposal match |
| `neo-report-agu` | `nasa-neows` | National Aeronautics and Space Administration. (n.d.). Asteroids NeoWs: Near earth object web service. Retrieved from https://api.nasa.gov/ | National Aeronautics and Space Administration. (n.d.). Asteroids NeoWs: Near Earth Object Web Service. Retrieved July 23, 2026, from https://api.nasa.gov/ | Expected; exact proposal match |

## Commits

Execution is isolated on `s2/neo-monitor-execution`. Before adoption the publication remained at `640b908a440b470c55daba4fd8ba7154a6e612b9`, with the two original `.repo-retro` files left alone. Bibliography, Quarto sources and selected frozen-input hashes remain unchanged. The authorized local `/.repo-retro/` exclude was added before recording to satisfy the clean-tree requirement; the owner’s files remain untouched. This branch contains the register row, this report and [structured execution evidence](2026-09-27-near-earth-object-monitor-execution.json); it now also contains both accepted fixtures.

## Timing

The approved pass ran September 27, following the 21:10 decision. Post-intake full suite: **1,123 passed in 44.35 seconds**, using scratch TEXMFVAR/TEXMFCACHE. Ruff, `ty check src/refs`, and whitespace checks pass. Scratch intake steps, original validation, attachment previews/results and gate logs remain in `/private/tmp/refs-neo-execution`; the durable execution evidence preserves the facts needed to review the result.

## Findings for refs

No product defect or new feature request. Exit 3 correctly identifies a successful first gate with absent accepted fixtures. Native webpage projection produces the approved output in both consumers.

## Findings for the guide

The proposed explicit frozen-input render boundary works through both native consumers without live acquisition. NASA’s content response must accompany its HTML shell in the source capture. Keep actual capture timestamps separate from historical bibliography access dates.

## Accepted fixture recording

Session 1 accepted the exact gate in `comms/2026-09-27-211736-s1-neo-gate-accepted.md`, under the owner’s quoted authorization: “ok, let's see if you and codex can one shot this”. A fresh `--record` run at `/private/tmp/refs-neo-record-01` used clean publication `640b908a440b470c55daba4fd8ba7154a6e612b9`. The clean-tree precheck required the previously authorized local-only `/.repo-retro/` exclude; no tracked publication file or owner retrospective file changed.

Both fixtures were recorded. Every extracted entry and both complete fixture mappings equal the accepted no-record gate exactly. Register provenance records the publication commit, timestamp, tool versions and artifact/fixture hashes. The record command exits 3 with `recorded: true`, correctly describing its pre-record missing-fixture state. No unexpected change occurred.

## Adoption and final verification

Session 1’s publication subagent adopted at `e2231a7fe8143dc86a4972e3b6fb42c32a26f4a8`: one `.refs.toml` target, `reports/references.json`, both consumers switched to that export, the hand-kept `.bib` retired, and `docs/refs.md` linked from README and tracked AGENTS instructions. Session 1 reviewed and authorized the conditional final record in `comms/2026-09-27-212159-s1-neo-adopted.md`, quoting the owner: “ok, let's see if you and codex can one shot this”.

The register’s temporary bibliography switch and legacy assertion are removed. The helper combines the current report’s front matter with its saved computed body and selected figures, checks citation keys, and renders both native formats without Jupyter/NASA execution. Thus the project owns its bibliography setting; the previously accepted computational boundary remains explicit.

The no-record run at `/private/tmp/refs-neo-adopted-check-01` exits 0 with all four entries identical to the accepted fixtures. Only after that comparison, the authorized fresh record at `/private/tmp/refs-neo-adopted-record-01` exits 0 with `recorded: true`. Both fixture files remain byte-for-byte unchanged, and their provenance now names adoption commit `e2231a7`. The publication was clean before and after these runs. No source or catalog edits were made during this final check.

**Next:** s1 reviews the completed execution branch and handles its merge gate and guide/ledger updates. No source gap, unexpected reference change or open decision remains.
