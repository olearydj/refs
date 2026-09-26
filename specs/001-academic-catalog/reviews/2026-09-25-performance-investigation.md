# Performance investigation, 2026-09-25

Owner direction, after corpus round three's rerun had run for two and a half hours: "Do more detailed timing tests so you can propose multiple improvements in the next round. Include parallel execution so we can actually take better advantage of the hardware." Goal set: make it fast. This records what was measured, on a consistent copy of the round's 27,644-source work catalog taken with SQLite's backup API into scratch space, with a slice of Beebe's `tugboat.bib` that the copy had not yet imported. Every number below is from those measurements, not from reports.

## Where the time goes

A first-time import into the 27,644-source catalog costs 356 ms per entry. Into an empty catalog it costs 4 ms. The difference is two full scans, and everything else is noise.

| Cost per imported entry at 27k sources | Measured | Cause |
| --- | --- | --- |
| Full record load, called twice per entry | 2 × 143 ms | `originals` has no index on `source_id`; three of the loader's queries scan 85,074 rows |
| Search index refresh | 28 ms | `DELETE FROM search_projection WHERE source_id=?` is a full scan of 160,620 FTS rows; FTS5 cannot index a plain column |
| Title likely-match query, twice | 2 × 45 ms | `lower(json_extract(metadata_json,'$.title'))` over every source |
| Everything else: parse, validate, bind, insert, commit, log fsync | about 4 ms | The fresh-catalog cost; fsync is 0.1 ms per entry on this disk |

With one index on `originals(source_id)` the full record load falls to 1.4 ms and the entry cost to 77 ms. With the search-index delete done by rowid through an indexed side table it falls from 21 ms to 0.17 ms. With a title plan built once per batch, the way the DOI plan already is, the two title scans go. The remaining cost is the 4 ms floor.

The same missing index and the same loader explain the other slow commands:

| Command at 27k sources, 241 import batches | Measured | Cause | Measured fix |
| --- | --- | --- | --- |
| `project cite --from-import` | 12.5 s | One join whose `OR` between the batch-id path and the legacy digest path defeats every index; proportional to sources times imports | Split into two indexed queries and union: 0.13 s |
| `import list` | 14.5 s | Loads the full record, including a BibTeX parse of each preserved original, for all 54,899 entries of all batches, to print counts the `imports` row already holds | Aggregates only; `import show` uses the core record; original parsing stays in `show` |
| `search`, `list` | 0.3 s | One pass over active rows | Acceptable |
| `resource check`, `collection list`, `project show`, `show`, `import show` | 0.1 to 0.2 s | | Acceptable |
| `export`, 1,000 entries | 0.5 s to assess | | Acceptable |

## What the harness adds on top

The corpus gate is one process on one core, file after file, and each file's gate is an import, a re-import, a citation, an export and a pandoc render. With the fixes above the import cost is minutes for the whole corpus; the citation is milliseconds; the render is about a second per file and is the floor. Five hundred files serial is therefore about fifteen minutes. The files are independent, so the gate parallelizes by file: each worker takes its own copy of the sample catalog once, runs its share of files, and the results merge. Eight workers on this machine bring a round to about three minutes, and the shared-catalog history mode, which found the value conflicts in round one, remains as a serial pass over a sample.

## Changes proposed, in one batch

1. Migration: an index on `originals(source_id)` and one on `project_sources(source_id)`. Measured: 356 to 77 ms per entry.
2. Search index deletes by rowid: a small `search_rows(rowid, source_id)` table with an index, maintained by the refresh, so removing a source's rows is a lookup. Measured: 21 ms to 0.17 ms.
3. A title plan built once per batch, the DOI plan's pattern, replacing the per-entry title scan in binding and in the likely-match warning. Expected: 90 ms to under 1 ms per entry.
4. `project cite --from-import` as two queries and a union. Measured: 12.5 s to 0.13 s.
5. `import list` from the `imports` row's counts; `inspect_batch` on the core record, never parsing originals. Expected: 14.5 s to under 0.1 s.
6. The corpus harness parallel by file with N workers and merged results, the shared-catalog mode kept as a serial sample; per-file wall time in every report; ceilings back to 30 minutes and 4 GB, since the runs will fit.

Expected after all six: a first-time import at 27k sources at about 5 ms per entry, seventy times faster than measured; corpus round three in minutes rather than hours; and no command over one second at this catalog size.

## What was not the problem

The fsync per mutation line and the full-sync commit per entry cost 0.1 ms and a few ms respectively; the design decisions behind them stand. The originals duplicate check is indexed and instant. The DOI scan was already fixed in round two.
