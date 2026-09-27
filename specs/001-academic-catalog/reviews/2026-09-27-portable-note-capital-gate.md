# Portable note capital — consumer gates, 2026-09-27

Base: refs `ff5939a`. Only portable note serialization changes: an initial uppercase character is braced unless an existing brace already protects it. BibLaTeX and CSL JSON retain their prior bytes; the owner-catalog regression compares successful exports and existing refusals. The BibTeX adapter removes the brace on import, including Unicode capitals. Both the system `plain.bst` and vendored `elsarticle-num.bst` preserve `{A}uburn` in the three minimized manufacturing records.

## Recorded-project walk

Normal `conversion_check.py --all`, no `--record`: family report 92 identical, family site 103 identical, jose-danvas Quarto 11 identical, JOSE 11 identical. No changed or missing entry and no fixture edits. Quarto 1.10.18, Pandoc 3.10 and Poppler 26.09.0. Evidence: `/private/tmp/refs-note-capital-walk/gate.json` and `gate.md`.

## Manufacturing, current catalog

Both consumers ran through the pending register from execution branch `8285228`, which stages the proposed bibliography routing only in the disposable project copy. All 39 entries render in each consumer. Comparison is against the preceding portable-misc gate (the code merged at `ff5939a`), not an accepted publication fixture. The pending harness still reports missing accepted fixtures and exits 1; no adoption or fixture recording is authorized by this run. Publication and catalog source records are untouched.

HTML/CSL: **39 identical**. Elsevier: **31 identical, eight changed**, all from protecting the leading note capital. The current BibTeX export equals the previous gate's bytes after removing only the new first-character braces; CSL JSON export bytes are identical. There is no unrelated metadata drift. The IISE ampersand remains correct. The three Auburn outlets now print `Auburn Engineering News` with the capital intact.

The table covers every reference; printed PDF numbers follow the citation order in the rendered LaTeX. `identical` means exact extracted text. Entry 35's wider capital moves a line break, yielding extracted `2016-12- 01`; the exported date and PDF meaning remain `2016-12-01`.

| PDF entry | Key | HTML | Elsevier change |
| --- | --- | --- | --- |
| 1 | `degiorgio2023adopting` | identical | identical |
| 2 | `wang2024frontier` | identical | identical |
| 3 | `fang2023hmd` | identical | identical |
| 4 | `tang2003compa` | identical | `event:` → `Event:` |
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
| 15 | `buttner2020augme` | identical | `event:` → `Event:` |
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
| 29 | `auburn2025honda` | identical | `auburn Engineering News` → `Auburn Engineering News` |
| 30 | `auburn2022ge` | identical | `auburn Engineering News` → `Auburn Engineering News` |
| 31 | `auburn2024hartzell` | identical | `auburn Engineering News` → `Auburn Engineering News` |
| 32 | `amouzgar2025novel` | identical | identical |
| 33 | `oleary2025framework` | identical | identical |
| 34 | `azuma1994impro` | identical | `event:` → `Event:` |
| 35 | `marchand2016pose` | identical | `issued:` → `Issued:` |
| 36 | `nakajima1988intro` | identical | identical |
| 37 | `ngcorrales2020overa` | identical | `issued:` → `Issued:` |
| 38 | `conover1982analysis` | identical | identical |
| 39 | `sahoo2026laser` | identical | identical |

## Exact changed PDF entries

| Entry | Before | After |
| --- | --- | --- |
| 4 | [4] A. Tang, C. Owen, F. Biocca, W. Mou, Comparative effectiveness of augmented reality in object assembly, in: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03, ACM Press, 2003, pp. 73–80, event: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03. doi:10.1145/642611.642626. | [4] A. Tang, C. Owen, F. Biocca, W. Mou, Comparative effectiveness of augmented reality in object assembly, in: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03, ACM Press, 2003, pp. 73–80, Event: Proceedings of the Conference on Human Factors in Computing Systems - CHI ’03. doi:10.1145/642611.642626. |
| 15 | [15] S. Büttner, M. Prilla, C. Röcker, Augmented reality training for industrial assembly work - are projection- based AR assistive systems an appropriate tool for assembly training, in: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, ACM, 2020, pp. 1–12, event: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems. doi:10.1145/3313831.3376720. | [15] S. Büttner, M. Prilla, C. Röcker, Augmented reality training for industrial assembly work - are projection- based AR assistive systems an appropriate tool for assembly training, in: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems, ACM, 2020, pp. 1–12, Event: Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems. doi:10.1145/3313831.3376720. |
| 29 | [29] C. Nelson, Honda returns to Auburn for lean manufacturing training, auburn Engineering News; Issued: 2025-05-27 (May 2025). URL https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing- training.html | [29] C. Nelson, Honda returns to Auburn for lean manufacturing training, Auburn Engineering News; Issued: 2025-05-27 (May 2025). URL https://www.eng.auburn.edu/news/2025/05/honda-returns-to-auburn-for-lean-manufacturing- training.html |
| 30 | [30] C. Nelson, Tiger Motors lab hosts GE Aviation training session, auburn Engineering News; Issued: 2022-03-03 (Mar. 2022). URL https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session | [30] C. Nelson, Tiger Motors lab hosts GE Aviation training session, Auburn Engineering News; Issued: 2022-03-03 (Mar. 2022). URL https://eng.auburn.edu/news/2022/03/tiger-motors-lab-hosts-ge-aviation-training-session |
| 31 | [31] C. Nelson, Hartzell Engine Tech elevates manufacturing practices through Tiger Motors training, auburn Engineering News; Issued: 2024-04-12 (Apr. 2024). URL https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices- through-tiger-motors-training.html | [31] C. Nelson, Hartzell Engine Tech elevates manufacturing practices through Tiger Motors training, Auburn Engineering News; Issued: 2024-04-12 (Apr. 2024). URL https://www.eng.auburn.edu/news/2024/04/hartzell-engine-tech-elevates-manufacturing-practices- through-tiger-motors-training.html |
| 34 | [34] R. T. Azuma, G. Bishop, Improving static and dynamic registration in an optical see-through HMD, in: SIGGRAPH ’94, Association for Computing Machinery, 1994, pp. 197–204, event: SIGGRAPH ’94. doi:10.1145/192161.192199. | [34] R. T. Azuma, G. Bishop, Improving static and dynamic registration in an optical see-through HMD, in: SIGGRAPH ’94, Association for Computing Machinery, 1994, pp. 197–204, Event: SIGGRAPH ’94. doi:10.1145/192161.192199. |
| 35 | [35] E. Marchand, H. Uchiyama, F. Spindler, Pose Estimation for Augmented Reality: A hands-on survey, IEEE Transactions on Visualization and Computer Graphics 22 (12) (2016) 2633–2651, issued: 2016-12-01. doi:10.1109/tvcg.2015.2513408. | [35] E. Marchand, H. Uchiyama, F. Spindler, Pose Estimation for Augmented Reality: A hands-on survey, IEEE Transactions on Visualization and Computer Graphics 22 (12) (2016) 2633–2651, Issued: 2016-12- 01. doi:10.1109/tvcg.2015.2513408. |
| 37 | [37] L. d. C. Ng Corrales, M. P. Lambán, M. E. Hernandez Korner, J. Royo, Overall equipment effectiveness: Systematic literature review and overview of different approaches, Applied Sciences 10 (18) (2020) 6469, issued: 2020-09-17. doi:10.3390/app10186469. URL https://www.mdpi.com/2076-3417/10/18/6469 | [37] L. d. C. Ng Corrales, M. P. Lambán, M. E. Hernandez Korner, J. Royo, Overall equipment effectiveness: Systematic literature review and overview of different approaches, Applied Sciences 10 (18) (2020) 6469, Issued: 2020-09-17. doi:10.3390/app10186469. URL https://www.mdpi.com/2076-3417/10/18/6469 |

Scratch evidence: `/private/tmp/refs-note-capital-manufacturing/gate.json`; prior comparison: `/private/tmp/refs-portable-misc-manufacturing/gate.json`. Full suite: 1,028 passed; Ruff and ty on `src/refs` passed. No publication exports or recorded fixtures were changed.
