# CV conversion execution gate — 2026-09-28

The authorized catalog conversion is complete. All 22 works match the approved candidate in native HTML and Typst PDF (44 expected comparisons), and all 379 existing consumer entries remain identical. The gate exits 3 solely because the new CV fixtures have not been recorded. This is the stop before owner acceptance: no `--record`, live CV export, CV commit, or merge has been performed.

## Scope and preflight

Execution follows proposal `1a9b690`, merged on `main` at `122b0c5`, on branch `s2/cv-execution`. The live catalog matched the proposal snapshot byte-for-byte before mutation; the live CV was clean at `07d3b2b948d265879edbd35a22fc47a445f37cbd` and remains so. The kickoff's count was clarified in the acknowledgement: 22 total works means 15 new records and seven reused identities, including Judgment Economy. GameTech 2013 remains an activity and has no catalog record. The four invited activities likewise remain outside the catalog.

The backup at `/Volumes/Casa/refs-backups/2026-09-28-before-cv-conversion` was validated before mutation. It contains the catalog, configuration, and resource manifest; it does not contain external file contents. The companion JSON retains its validated manifest and receipts.

## Catalog changes

The approved canonical payloads were previewed, rehearsed against a disposable catalog, and applied through refs services: 15 refs-JSON admissions, six revision-guarded updates, and one unchanged reuse. This was not a bulk BibTeX import batch. Sixteen retained original entries from `cv/refs/all.bib` were preserved as exact raw bytes with their approved identity mappings, `import-cv` origin, and source locators; their bytes were checked after preservation. The service operations also preserve their normal originals and log their mutations.

The six shared corrections are: AR/MR Framework's explicit English language; removal of stale forthcoming context and protection of INSIGHT; GradeBot's short accepted-program/deck-title context while retaining Comprehensive; AI4SE's Danny J. canonical name, Dan byline caveat, and title protection; Ballard's straight canonical apostrophe, speech retype, event data and short title/byline caveats while retaining Neurodiverse; and Ficken's speech retype, event data and Dan caveat. Judgment Economy is reused unchanged. Hossain R6 links bidirectionally to the earlier `hossain_exploring_2024` identity, which is not added to CV membership. The full family testimony record is unchanged.

The new `cv` project contains exactly the 22 keys below. Nine own-work files were linked in place, with source hashes unchanged. The public US7497779B2 patent PDF was acquired, its first page checked, and admitted through a verified copy-before-delete managed move with label `patent`. Its digest is `62bab0f5c2f25379cc30115c6b6af19585cbb64148129fa512b7f4b546287ab0`. All resource paths, identities and receipts are in the companion JSON.

Known source gaps remain the current unblinded Hossain R6, final MBSE2026 poster, error-patterns draft, and three 1997 chapter scans. These were not substituted with other versions or represented as acquired.

## Native consumer results

The register adds native HTML and Typst PDF consumers. A scratch-only preparation applies the reviewable [adoption patch](2026-09-28-cv-adoption.patch), then Quarto renders both formats. HTML extraction reads the actual bibliography divs. PDF extraction reads `pdftotext -layout` output, verifies each complete reference against its HTML identity, and retains the actual PDF substring. The readable implementation is `tests/fixtures/real-trial/cv_consumer.py`; its source is embedded in the register so the disposable render can run independently.

The first scratch attempt refused the non-rendering `docs/sessions` symlink. Excluding that directory allowed the native render to complete. The successful individual gate and all-project gate have identical CV extractions. The PDF has 11 pages. All 19 activity rows match in both formats, including restored GameTech under Panels and Participation. The split section headings are present, and the old combined heading is absent. Exact approved and actual entry strings, format-specific wrapping, activity results, tool versions and artifact digests are retained in [the evidence JSON](2026-09-28-cv-execution.json).

| Catalog key | HTML vs approved candidate | PDF vs approved candidate |
|---|---|---|
| `oleary2025framework` | Expected, identical | Expected, identical |
| `oleary2025econ-uncertainty` | Expected, identical | Expected, identical |
| `madachyolearymcdermott2026genai-se-tips` | Expected, identical | Expected, identical |
| `olearyledford2026insight` | Expected, identical | Expected, identical |
| `hossain2024lean-industry40` | Expected, identical | Expected, identical |
| `oleary2026danvas-jose` | Expected, identical | Expected, identical |
| `oleary-2026-instructionalInformation` | Expected, identical | Expected, identical |
| `oleary2026instructional-media-tradeoffs` | Expected, identical | Expected, identical |
| `oleary-2026-pipyerEvidence` | Expected, identical | Expected, identical |
| `ganesh2026ai-driven-dema` | Expected, identical | Expected, identical |
| `ganesh2026ai-enhanced-dema` | Expected, identical | Expected, identical |
| `gadzey2026dema-digital-thread` | Expected, identical | Expected, identical |
| `oleary-2026-judgmentEconomy` | Expected, identical | Expected, identical |
| `oleary2025binary-classification` | Expected, identical | Expected, identical |
| `oleary2025ai4se` | Expected, identical | Expected, identical |
| `olearyficken2025innovation-culture` | Expected, identical | Expected, identical |
| `ballard2024role` | Expected, identical | Expected, identical |
| `ficken2023blending` | Expected, identical | Expected, identical |
| `oleary2009time-dilation` | Expected, identical | Expected, identical |
| `kreitzman-1997-animatingControllers` | Expected, identical | Expected, identical |
| `oleary-1997-animatingExpressions` | Expected, identical | Expected, identical |
| `oleary-1997-animatingMultiple` | Expected, identical | Expected, identical |

The all-project gate preserves JHL report/site (92/103), danvas Quarto/JOSE (11/11), manufacturing HTML/Elsevier (39/39), DEMA TDD HTML/PDF and PDD DOCX/PDF (34/34/6/6), and NEO standard/AGU (2/2): 379 identical entries. The two CV consumers each have 22 entries and missing fixtures. The generic gate labels those new entries changed because there is no recorded baseline; comparison with the approved candidate marks all 44 expected-identical, with no unexpected changes.

Validation: 23 conversion harness tests passed; repository Ruff and source ty checks passed; the patch applied successfully in both scratch gates. No product source changed. All eight live export-target rows remain exactly equal to the pre-conversion backup. No accepted fixture was written.

## Adoption handoff

After the owner accepts the gate, session 1's adoption agent can apply the adoption patch to the still-clean CV, export the `cv` membership to `refs/cv.json`, and adopt its project-local configuration, section manifest/script, CSL/highlighter, split headings and `data/activities.yml`. The old bibliography cleanup and project documentation updates remain adoption work. Remove the execution-only patch application and embedded adoption patch from the register/helper once the live project supplies those files; keep native rendering and extraction. Recording accepted fixtures and merging each branch remain separate owner gates.

Scratch evidence is under `/private/tmp/refs-cv-execution`: successful individual gate `cv-gate-02`, all-project gate `all-gate`, and intake/backup receipts. The live catalog has been mutated as authorized; the live CV has not. Do not rerun the intake script against the already-converted catalog.
