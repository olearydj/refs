from: s2
next: s1
kind: report
re: 2026-09-28-232657-s1-cv-second-revision.md

Second revision ready at `1a9b690` on `s2/cv-proposal`, rebased on `416757e` (the adopted works/activity rule). Clean worktree: `/Volumes/Casa/dev/refs/worktrees/cv-proposal`. The same proposal `.md`, `.json` and `-project.patch` are rewritten in place.

The candidate has 23 works (22 settled plus provisional GameTech), 11 PDF pages, and both native HTML/PDF renders completed. “Conference Presentations” now contains ten candidate bibliography entries; “Panels and Participation” contains the two organized panels and 2015 moderator/speaker role in the original plain format. The four invited activities stay plain; no FIEA/Air University/MGMWERX refs records or deck links remain in the plan. Campus has eleven activities, adding November 5, 2024 while retaining April 25 and the owner's November 9, 2020 DSSA date. All seventeen retained activity rows have identical before/after HTML text, and all eighteen candidate activity rows were found in PDF text after accounting for date-column placement. The report includes exact conference, activity and title comparisons. All 34 bibliography entries (11 baseline, 23 candidate) agree between their HTML/PDF renderings; eight non-first-author underlines remain correct.

Family testimony is entirely unchanged: Dan stays Dan, no appended caveat. A fresh proposed catalog contains six shared canonical changes plus the Hossain link, no family changes. All-project gate without --record: exit 0, all 379 entries identical across five projects/twelve consumers, including family report 92 and site 103. No new product code. Live CV clean and live catalog hash unchanged.

Two proposals remain for the owner:

1. Move activity lists into `data/activities.yml` at adoption. The patch and renders demonstrate it, but it is explicitly not treated as approved. Cost: one data file, one existing-PyYAML load, three existing renderer calls, no new dependency/schema; about 20–30 minutes including adoption verification. If declined, retain the lists with identical visible behavior.
2. GameTech: public investigation found the owner's posted 2021 CV with the exact title/date and a contemporaneous NCS-hosted report about the Orlando conference and an unnamed n-Space president speaking. No talk-specific program, posted deck or recording was found; these sources do not independently establish that exact citable work. The report links both and states their limits. The scratch candidate demonstrates the requested `oleary-2013-independentGame` move, but admission is conditional. Recommend leaving it as an activity until a public work record is located, unless the owner explicitly accepts the available evidence as sufficient. It must not be silently admitted as verified. No search-process or organizer narrative was added to its context.

Artifacts: `/private/tmp/refs-cv-second-revision/{baseline,candidate}/_output/cv-master.{html,pdf}` and `/private/tmp/refs-cv-second-revision/shared-gate-second/gate.json`. Companion evidence includes activity rows, final records, exact comparisons and hashes. Project patch passes git apply --check against baseline. No live execution, merge or fixture recording. Ending the turn without polling.
