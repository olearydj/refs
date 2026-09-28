# Near-Earth Object Monitor conversion proposal — 2026-09-27

## Backup and scope

Read-only proposal under `comms/2026-09-27-210138-s1-neo-monitor-conversion.md`, following conversion-guide steps 1–4. Proposed execution backup: `/Volumes/Casa/refs-backups/2026-09-27-before-near-earth-object-monitor-conversion`. No real catalog records, memberships, resources, publication files or ignore rules changed. Admission and export checks used disposable catalogs under `/private/tmp/refs-neo-proposal`; source-page retrieval was read-only, with no source files downloaded for attachment.

The owner calls this course project internal. Publication `/Volumes/Casa/dev/near-earth-object-monitor` is at `640b908a440b470c55daba4fd8ba7154a6e612b9`. Its only untracked files are `.repo-retro/retrospective.md` and `.repo-retro/retrospective.pdf`, explicitly left alone. No clean-tree check required a local exclude during this proposal; if recording later requires one, the authorized `/.repo-retro/` local exclude will be reported then. Tracked agent instructions are `AGENTS.md`; no separate ignored agent instruction file was found. `.env`, `.venv`, caches, generated reports, data and logs are ignored runtime state; no credentials were read or copied.

## Inventory and consumers

One hand-maintained bibliography, `reports/references.bib`, has two assigned hyphenated keys, both retained. Both reports cite `nasa-neows` once and `cneos-pha` twice outside code, with no uncited entry. Quarto cross-references are excluded. Each existing PDF has exactly those two references. `reports/hello-quarto.qmd` does not consume the bibliography. No synchronization script or additional bibliography consumer was found.

| Consumer | Actual engine and style | Planned target |
| --- | --- | --- |
| `reports/neo-report.qmd` → PDF | Quarto 1.10.18 / Pandoc 3.10 citeproc, default Chicago author-date; LuaLaTeX | `reports/references.json`, `csl-json-v1` |
| `reports/neo-report-agu.qmd` → `agu-pdf` | Same citeproc engine, bundled `american-geophysical-union.csl` and `agujournal2019` layout; LuaLaTeX | The same JSON target |

The AGU class contains legacy BibTeX declarations, but its actual generated TeX has `CSLReferences`, citeproc citations and keyed reference items. It does not run biber or BibTeX for these references. No engine standardization or second profile is needed. At adoption both source documents switch their bibliography to `references.json`; the unused hand-kept `.bib` can then retire. No style edit is proposed.

## Import outcomes by key

Planned import: two entries from the original BibTeX, origin `near-earth-object-monitor`, followed by one project with both keys cited. Read-only inspection of the active catalog found no matching key, URL, NeoWs/CNEOS title or potentially-hazardous-asteroid record. Both are expected new; actual import outcomes remain an execution check. Preserve both original entry byte strings. There are no DOIs, preprints, version substitutions or relationships to add.

## Record completions by key

| Key | Planned admitted record | Protection and context |
| --- | --- | --- |
| `nasa-neows` | `webpage`; existing corporate author National Aeronautics and Space Administration; title **Asteroids NeoWs: Near Earth Object Web Service**; site/container **NASA Open APIs**; existing URL `https://api.nasa.gov/`; accessed **2026-07-23**; no invented issued date | Protect `NeoWs`, `NASA` and `APIs`; title-case policy. Preserve the historical access date and record the actual later capture date separately. |
| `cneos-pha` | `webpage`; existing corporate author NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies; title **Glossary: Potentially Hazardous Asteroid (PHA)**; site/container **Center for Near Earth Object Studies**; existing URL `https://cneos.jpl.nasa.gov/glossary/PHA.html`; accessed **2026-07-23**; no invented issued date | Protect `PHA`; title-case policy. Same capture-date context convention. |

Clear the imported native BibTeX `misc` label during retyping: retaining a contradictory native label correctly fails admission. No kind or bibliographic note is needed. Both final candidates pass the current refs CLI's dry-run admission without warnings, and their current CSL export has no loss warnings. The [structured proposal](2026-09-27-near-earth-object-monitor-proposal.json) contains the exact admitted records and export.

## Sources found, fetched, and the fetch list for the owner

The [NASA Open APIs page](https://api.nasa.gov/) and its [official API content data](https://api.nasa.gov/assets/json/apis.json) confirm the NeoWs name/description and feed by close-approach dates. NASA hosts the documentation; the service credits the SpaceRocks team as maintainers, which does not require substituting those people for the corporate author of this cited documentation page. The [CNEOS glossary](https://cneos.jpl.nasa.gov/glossary/PHA.html) supplies the PHA definition using orbital distance and absolute magnitude; its linked [NEO Groups explanation](https://cneos.jpl.nasa.gov/about/neo_groups.html) explicitly distinguishes hazardous classification from an impact prediction. The existing descriptive glossary title is identifiable and retained. No unsupported cited claim requiring a prose correction was found.

No matching source capture was found in the project/figures, vault, managed library or Downloads; no matching DEVONthink export surfaced in the available filesystem inventory. The project’s reports and API data are not substitutes for the cited source pages. The owner’s own-work stores are inapplicable to these two NASA web pages. Both are capture acquisitions, not permanent URL-only records. No owner fetch is currently required: direct requests reach both relevant sources successfully through curl.

The NASA landing HTML is only a JavaScript shell. Execution will capture the original HTML **and** the complete official `assets/json/apis.json` response containing the NeoWs documentation into one JSON resource, with URLs, actual retrieval timestamp and member hashes. CNEOS needs one JSON resource retaining its full HTML response with URL, timestamp and hash. These are source-content captures, not browser screenshots or replicas of every remote asset. Python’s default trust store rejected the CNEOS certificate chain; curl succeeded with normal certificate validation, so no TLS bypass is proposed. The NASA HTML’s staging-base asset URL returns 404; the official same-host content endpoints work and will be named explicitly in capture provenance.

## Attachments with final names and hashes

Pending execution: two single-file captures, label `capture`, moved by `resource add --move` into convention-named `unfiled` placement. Preview actual destination names, then verify final bytes against the input hashes. Capture timestamps/context use the actual execution date (expected September 27); both bibliography `accessed` fields remain July 23. No attachment names or hashes are claimed before acquisition.

## Export gate table

Both full native formats were rendered from the project’s saved July 20–26 executed Markdown and figures, in baseline and candidate scratch copies, without calling the NASA feed, reading `.env` or executing Python cells. Thus the bibliography gate covers each native consumer and layout, while fresh weekly data acquisition is deliberately outside this check. Existing PDFs’ extracted references exactly equal the new baseline renders. All six in-text author-date citations remain text-identical; both reference lists retain their two author-ordered entries, with no reference numbering to shift. Native builds completed without citation warnings.

Execution should register these same two native consumers and explicitly select their frozen Markdown/figure files from the excluded `.quarto` directory. A named scratch-only preparation step reuses the saved computed body and switches the bibliography for the candidate; it must not copy credentials or run a fresh NASA request. After adoption it reads the adopted bibliography setting. Saved evidence and its source hashes must be rechecked before the execution gate. Four entry wordings are predicted below; PDF line wraps and AGU draft line numbers are normalized by extraction, while the existing split URL is retained as extracted evidence.

| Consumer | Key | Before | Proposed after | Expected change |
| --- | --- | --- | --- | --- |
| `neo-report` | `cneos-pha` | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. n.d. Glossary: Potentially Hazardous Asteroid (PHA). Accessed July 23, 2026. https://cneos.jpl.nasa.gov /glossary/PHA.html. | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. n.d. “Glossary: Potentially Hazardous Asteroid (PHA).” Center for Near Earth Object Studies. Accessed July 23, 2026. https://cneos.jpl.nasa.gov/glossary/PHA.html. | Quoted webpage title and site name; July 23 access date retained. |
| `neo-report` | `nasa-neows` | National Aeronautics and Space Administration. n.d. Asteroids NeoWs: Near Earth Object Web Service. Accessed July 23, 2026. https://api.nasa.gov/. | National Aeronautics and Space Administration. n.d. “Asteroids NeoWs: Near Earth Object Web Service.” NASA Open APIs. Accessed July 23, 2026. https://api.nasa.gov/. | Quoted webpage title and site name; July 23 access date retained. |
| `neo-report-agu` | `cneos-pha` | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. (n.d.). Glossary: Potentially hazardous asteroid (PHA). Retrieved from https       :// cneos.jpl.nasa.gov/glossary/PHA.html | NASA Jet Propulsion Laboratory, Center for Near Earth Object Studies. (n.d.). Glossary: Potentially Hazardous Asteroid (PHA). Retrieved July 23, 2026, from https://cneos.jpl.nasa.gov/glossary/PHA.html | Title case and newly visible July 23 retrieval date; native AGU webpage style omits the site name. |
| `neo-report-agu` | `nasa-neows` | National Aeronautics and Space Administration. (n.d.). Asteroids NeoWs: Near earth object web service. Retrieved from https://api.nasa.gov/ | National Aeronautics and Space Administration. (n.d.). Asteroids NeoWs: Near Earth Object Web Service. Retrieved July 23, 2026, from https://api.nasa.gov/ | Title case and newly visible July 23 retrieval date; native AGU webpage style omits the site name. |

## Commits

Proposal isolated on `s2/neo-monitor-proposal`, based on refs main `96283d8`. Publication source hashes and its two untracked owner files remain unchanged. No live import, backup, source attachment, registered target, accepted fixture or publication adoption occurred.

## Timing

Inventory, primary-source checks, warning-free admission and four full native render comparisons were performed September 27. Scratch evidence is retained under `/private/tmp/refs-neo-proposal`; final candidate renders use the exact admitted exported records. The proposal is ready for step 4; execution waits for s1’s decision.

## Findings for refs

No product change requested. Current profiles admit and export both records. The known distinction between a record’s historical access date and a later capture timestamp is kept in context/resource provenance.

## Findings for the guide

An AGU class’s legacy BibTeX declarations do not establish the active citation engine; inspect the generated TeX. A JavaScript documentation page may need its official content response captured alongside the shell. Saved computational outputs allow a full bibliography render without refreshing external data, provided the selected inputs and limitation are explicit.

## Open decision

**Accept AGU displaying the existing July 23, 2026 retrieval date?** Recommended: accept the native webpage result above. The stored date does not change, but AGU previously suppressed it for `misc` and now displays it for `webpage`. This is flagged because the kickoff says rendered access dates should not change. If that means the date must remain absent in AGU, a project-local style decision and another preview are needed; no style modification is currently proposed. No other modeling, engine, target, capture or source-availability decision is open.
