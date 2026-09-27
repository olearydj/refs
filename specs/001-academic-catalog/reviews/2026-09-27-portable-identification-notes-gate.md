# Portable identification notes — consumer gates, 2026-09-27

Base: refs `b9ad60a`. Portable export omits issued-day notes and their former `issued_day_in_note` assessment, reports the loss of day precision as `issued_precision_projected`, and omits an event note when its title equals the container title. Year/month round trips are unchanged; day precision remains in the catalog and BibLaTeX. Seasons retain their existing month information. Outlet, publisher, genre, medium, version and distinct event notes remain. CSL JSON and BibLaTeX bytes match the base over the owner catalog, including unchanged existing refusals.

## Recorded-project walk

`conversion_check.py --all`, without `--record`: family report **92 identical**, family site **103 identical**, jose-danvas Quarto **11 identical**, JOSE **11 identical**. No changed or missing entries. No fixture was edited. Evidence: `/private/tmp/refs-identification-walk/gate.json` and `gate.md`.

## Manufacturing, current catalog

Both consumers rendered all 39 references using the pending register from execution branch `8285228`. Its bibliography routing is staged only in scratch. This comparison is against the preceding capital-protection gate at `b9ad60a`, recorded in [the preceding review](2026-09-27-portable-note-capital-gate.md), not an accepted manufacturing fixture. The harness exits 1 because accepted fixtures do not yet exist; rendering succeeded. No catalog records, publication files or accepted fixtures were changed.

HTML/CSL: **39 identical**. Elsevier: **31 identical, eight changed**. Five issued-day notes disappear; three duplicate event notes disappear. All three news entries still print **Auburn Engineering News** with its initial capital. The IISE ampersand remains correct. No other entry changes. PDF reflow changes extracted whitespace in entries 15, 34 and 35, including inside DOI strings; the exported DOI values are unchanged.

Tools: Quarto 1.10.18, Pandoc 3.10, R 4.5.3, BibTeX 0.99e (TeX Live 2026), Poppler 26.09.0. Current scratch evidence: `/private/tmp/refs-identification-manufacturing/gate.json`; before: `/private/tmp/refs-note-capital-manufacturing/gate.json`.

| PDF entry | Key | HTML | Elsevier |
| --- | --- | --- | --- |
| 1 | `degiorgio2023adopting` | identical | identical |
| 2 | `wang2024frontier` | identical | identical |
| 3 | `fang2023hmd` | identical | identical |
| 4 | `tang2003compa` | identical | changed: duplicate Event note removed |
| 5 | `chu2020compa` | identical | identical |
| 6 | `vanneste2020cogni` | identical | identical |
| 7 | `funk2016interactive` | identical | identical |
| 8 | `yang2023industrial` | identical | identical |
| 9 | `caudell1992augmented` | identical | identical |
| 10 | `kaplan2021effec` | identical | identical |
| 11 | `kolla2021compa` | identical | identical |
| 12 | `gonzalez-franco2017immer` | identical | identical |
| 13 | `hoover2020measu` | identical | identical |
| 14 | `alves2022compa` | identical | identical |
| 15 | `buttner2020augme` | identical | changed: duplicate Event note removed |
| 16 | `wang2021role` | identical | identical |
| 17 | `marino2024assessing` | identical | identical |
| 18 | `moro2021virtu` | identical | identical |
| 19 | `chu2021experimental` | identical | identical |
| 20 | `degiorgio2022assessing` | identical | identical |
| 21 | `daling2023assemble` | identical | identical |
| 22 | `ariansyah2024learnability` | identical | identical |
| 23 | `havard2021case` | identical | identical |
| 24 | `anderson1982acqui` | identical | identical |
| 25 | `newell1981mecha` | identical | identical |
| 26 | `crossman1959theory` | identical | identical |
| 27 | `moyo2013devel` | identical | identical |
| 28 | `oleary2024augmented` | identical | identical |
| 29 | `auburn2025honda` | identical | changed: Issued note removed |
| 30 | `auburn2022ge` | identical | changed: Issued note removed |
| 31 | `auburn2024hartzell` | identical | changed: Issued note removed |
| 32 | `amouzgar2025novel` | identical | identical |
| 33 | `oleary2025framework` | identical | identical |
| 34 | `azuma1994impro` | identical | changed: duplicate Event note removed |
| 35 | `marchand2016pose` | identical | changed: Issued note removed |
| 36 | `nakajima1988intro` | identical | identical |
| 37 | `ngcorrales2020overa` | identical | changed: Issued note removed |
| 38 | `conover1982analysis` | identical | identical |
| 39 | `sahoo2026laser` | identical | identical |

## Exact changed PDF entries

| Entry | Before | After |
| --- | --- | --- |
| 4 | [4] A. Tang, C. Owen, F. Biocca, W. Mou, Comparative effectiveness of augmented reality in object assembly, in: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03, ACM Press, 2003, pp. 73–80, Event: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03. doi:10.1145/642611.642626. | [4] A. Tang, C. Owen, F. Biocca, W. Mou, Comparative effectiveness of augmented reality in object assembly, in: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03, ACM Press, 2003, pp. 73–80. doi:10.1145/642611.642626. |
| 15 | [15] S. Büttner, M. Prilla, C. Röcker, Augmented reality training for industrial assembly work - are projection- based AR assistive systems an appropriate tool for assembly training, in: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, ACM, 2020, pp. 1–12, Event: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems. doi:10.1145/3313831.3376720. | [15] S. Büttner, M. Prilla, C. Röcker, Augmented reality training for industrial assembly work - are projection-based AR assistive systems an appropriate tool for assembly training, in: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, ACM, 2020, pp. 1–12. doi: 10.1145/3313831.3376720. |
| 29 | [29] C. Nelson, Honda returns to Auburn for lean manufacturing training, Auburn Engineering News; Issued: 2025-05-27 (May 2025). URL https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing- training.html | [29] C. Nelson, Honda returns to Auburn for lean manufacturing training, Auburn Engineering News (May 2025). URL https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing- training.html |
| 30 | [30] C. Nelson, Tiger Motors lab hosts GE Aviation training session, Auburn Engineering News; Issued: 2022-03-03 (Mar. 2022). URL https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session | [30] C. Nelson, Tiger Motors lab hosts GE Aviation training session, Auburn Engineering News (Mar. 2022). URL https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session |
| 31 | [31] C. Nelson, Hartzell Engine Tech elevates manufacturing practices through Tiger Motors training, Auburn Engineering News; Issued: 2024-04-12 (Apr. 2024). URL https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices- through-tiger-motors-training.html | [31] C. Nelson, Hartzell Engine Tech elevates manufacturing practices through Tiger Motors training, Auburn Engineering News (Apr. 2024). URL https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices- through-tiger-motors-training.html |
| 34 | [34] R. T. Azuma, G. Bishop, Improving static and dynamic registration in an optical see-through HMD, in: SIGGRAPH ’94, Association for Computing Machinery, 1994, pp. 197–204, Event: SIGGRAPH ’94. doi:10.1145/192161.192199. | [34] R. T. Azuma, G. Bishop, Improving static and dynamic registration in an optical see-through HMD, in: SIGGRAPH ’94, Association for Computing Machinery, 1994, pp. 197–204. doi:10.1145/192161.192 199. |
| 35 | [35] E. Marchand, H. Uchiyama, F. Spindler, Pose Estimation for Augmented Reality: A hands-on survey, IEEE Transactions on Visualization and Computer Graphics 22 (12) (2016) 2633–2651, Issued: 2016-12- 01. doi:10.1109/tvcg.2015.2513408. | [35] E. Marchand, H. Uchiyama, F. Spindler, Pose Estimation for Augmented Reality: A hands-on survey, IEEE Transactions on Visualization and Computer Graphics 22 (12) (2016) 2633–2651. doi:10.1109/ tvcg.2015.2513408. |
| 37 | [37] L. d. C. Ng Corrales, M. P. Lambán, M. E. Hernandez Korner, J. Royo, Overall equipment effectiveness: Systematic literature review and overview of different approaches, Applied Sciences 10 (18) (2020) 6469, Issued: 2020-09-17. doi:10.3390/app10186469. URL https://www.mdpi.com/2076-3417/10/18/6469 | [37] L. d. C. Ng Corrales, M. P. Lambán, M. E. Hernandez Korner, J. Royo, Overall equipment effectiveness: Systematic literature review and overview of different approaches, Applied Sciences 10 (18) (2020) 6469. doi:10.3390/app10186469. URL https://www.mdpi.com/2076-3417/10/18/6469 |

## Verification

Full suite: **1,037 passed**. Ruff and ty on `src/refs` passed. The consumer tests exercise the three minimized news records through plain.bst and the vendored elsarticle-num.bst, and conference records with matching and distinct event titles through elsarticle-num.bst. Adapter tests pin whole-record round trips with only the documented loss of day precision; the existing leading-capital tests remain. No fixture recording or publication adoption was performed.
