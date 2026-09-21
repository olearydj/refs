"""Synthetic design probe, not a refs importer or an implementation test.

Run: adhoc-python specs/001-academic-catalog/reviews/model-examples-2026-09-21/check.py
Uses Pandoc as an independent BibTeX reader. Writes only adjacent results.json.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# These examples deliberately use the same semantic values through three routes.
# The Zotero route is a small, explicit mapping hypothesis; CSL is the oracle.
CASES = [
    {
        "id": "thesis",
        "zotero": {"itemType": "thesis", "title": "Example Thesis", "thesisType": "Doctoral dissertation", "university": "Example University", "date": "2024"},
        "bibtex": "@phdthesis{thesis, title={Example Thesis}, type={Doctoral dissertation}, school={Example University}, year={2024}}",
        "expected": {"type": "thesis", "title": "Example Thesis", "genre": "Doctoral dissertation", "publisher": "Example University", "issued": {"date-parts": [[2024]]}},
    },
    {
        "id": "report",
        "zotero": {"itemType": "report", "title": "Example Report", "reportType": "Technical report", "institution": "Example Institute", "reportNumber": "TR-17", "date": "2023"},
        "bibtex": "@techreport{report, title={Example Report}, type={Technical report}, institution={Example Institute}, number={TR-17}, year={2023}}",
        "expected": {"type": "report", "title": "Example Report", "genre": "Technical report", "publisher": "Example Institute", "number": "TR-17", "issued": {"date-parts": [[2023]]}},
    },
    {
        "id": "article",
        "zotero": {"itemType": "journalArticle", "title": "Example Article", "publicationTitle": "Example Journal", "volume": "8", "issue": "2", "pages": "10-19", "date": "2024-01"},
        "bibtex": "@article{article, title={Example Article}, journal={Example Journal}, volume={8}, number={2}, pages={10--19}, year={2024}, month=jan}",
        "expected": {"type": "article-journal", "title": "Example Article", "container-title": "Example Journal", "volume": "8", "issue": "2", "page": "10-19", "issued": {"date-parts": [[2024, 1]]}},
    },
    {
        "id": "chapter",
        "zotero": {"itemType": "bookSection", "title": "Example Chapter", "bookTitle": "Example Book", "publisher": "Example Press", "place": "Example City", "pages": "20-29", "date": "2022"},
        "bibtex": "@incollection{chapter, title={Example Chapter}, booktitle={Example Book}, publisher={Example Press}, address={Example City}, pages={20--29}, year={2022}}",
        "expected": {"type": "chapter", "title": "Example Chapter", "container-title": "Example Book", "publisher": "Example Press", "publisher-place": "Example City", "page": "20-29", "issued": {"date-parts": [[2022]]}},
    },
    {
        "id": "web",
        "zotero": {"itemType": "webpage", "title": "Example Web Page", "url": "https://example.org/reference", "date": "2024"},
        "bibtex": "@misc{web, title={Example Web Page}, howpublished={Web page}, url={https://example.org/reference}, year={2024}}",
        "expected": {"type": "webpage", "title": "Example Web Page", "URL": "https://example.org/reference", "issued": {"date-parts": [[2024]]}},
    },
]

TYPE = {"thesis": "thesis", "report": "report", "journalArticle": "article-journal", "bookSection": "chapter", "webpage": "webpage"}
FIELDS = {"title": "title", "thesisType": "genre", "reportType": "genre", "university": "publisher", "institution": "publisher", "reportNumber": "number", "publicationTitle": "container-title", "bookTitle": "container-title", "publisher": "publisher", "place": "publisher-place", "volume": "volume", "issue": "issue", "pages": "page", "url": "URL"}

CASES.extend([
    {"id": "preprint", "zotero": {"itemType": "preprint", "title": "Learning With AI", "repository": "arXiv", "archiveID": "2401.01234", "date": "2024"}, "bibtex": "@unpublished{preprint,title={Learning With {AI}},eprint={2401.01234},archiveprefix={arXiv},year={2024}}", "expected": {"type": "article", "title": "Learning With AI", "issued": {"date-parts": [[2024]]}}, "extension_expected": {"eprint": {"repository": "arXiv", "identifier": "2401.01234"}}},
    {"id": "conference", "zotero": {"itemType": "conferencePaper", "title": "Learning With Python", "proceedingsTitle": "Proceedings of Example Research", "conferenceName": "Example Research Conference", "date": "2024"}, "bibtex": "@inproceedings{conference,title={Learning With {Python}},booktitle={Proceedings of Example Research},eventtitle={Example Research Conference},year={2024}}", "expected": {"type": "paper-conference", "title": "Learning With Python", "container-title": "Proceedings of Example Research", "event-title": "Example Research Conference", "issued": {"date-parts": [[2024]]}}},
    {"id": "book", "zotero": {"itemType": "book", "title": "Working With LaTeX", "edition": "2", "series": "Example Methods", "ISBN": "9780306406157", "date": "2020"}, "bibtex": "@book{book,title={Working With {LaTeX}},edition={2},series={Example Methods},isbn={9780306406157},year={2020}}", "expected": {"type": "book", "title": "Working With LaTeX", "edition": "2", "collection-title": "Example Methods", "ISBN": "9780306406157", "issued": {"date-parts": [[2020]]}}},
    {"id": "magazine", "zotero": {"itemType": "magazineArticle", "title": "Measuring pH", "publicationTitle": "Example Monthly", "date": "2024-03"}, "bibtex": "@article{magazine,title={Measuring {pH}},journal={Example Monthly},year={2024},month=mar}", "expected": {"type": "article-magazine", "title": "Measuring pH", "container-title": "Example Monthly", "issued": {"date-parts": [[2024, 3]]}}},
    {"id": "standard", "zotero": {"itemType": "standard", "title": "Example Standard", "number": "EX-42", "creators": [{"creatorType": "author", "name": "Research and Standards Council"}], "date": "2024"}, "bibtex": "@standard{standard,title={Example Standard},number={EX-42},author={{Research and Standards Council}},year={2024}}", "expected": {"type": "standard", "title": "Example Standard", "number": "EX-42", "author": [{"literal": "Research and Standards Council"}], "issued": {"date-parts": [[2024]]}}},
    {"id": "patent", "zotero": {"itemType": "patent", "title": "Example Device", "patentNumber": "US-EX-42", "assignee": "Research and Devices Ltd", "creators": [{"creatorType": "inventor", "firstName": "Ada", "lastName": "Example"}], "date": "2024"}, "bibtex": "@patent{patent,title={Example Device},number={US-EX-42},holder={{Research and Devices Ltd}},author={Example, Ada},year={2024}}", "expected": {"type": "patent", "title": "Example Device", "number": "US-EX-42", "author": [{"family": "Example", "given": "Ada"}], "issued": {"date-parts": [[2024]]}}, "extension_expected": {"patent_assignees": [{"literal": "Research and Devices Ltd"}]}},
    {"id": "presentation", "zotero": {"itemType": "presentation", "title": "Example Presentation", "meetingName": "Example Conference", "creators": [{"creatorType": "presenter", "firstName": "Alex", "lastName": "Example"}], "date": "2024"}, "bibtex": "@misc{presentation,title={Example Presentation},author={Example, Alex},howpublished={Presentation at Example Conference},year={2024}}", "expected": {"type": "speech", "title": "Example Presentation", "event-title": "Example Conference", "author": [{"family": "Example", "given": "Alex"}], "issued": {"date-parts": [[2024]]}}},
    {"id": "particle", "zotero": {"itemType": "book", "title": "Example Names", "creators": [{"creatorType": "author", "firstName": "Alex", "lastName": "de Example"}], "date": "2024"}, "bibtex": "@book{particle,title={Example Names},author={de Example, Alex},year={2024}}", "expected": {"type": "book", "title": "Example Names", "author": [{"family": "de Example", "given": "Alex"}], "issued": {"date-parts": [[2024]]}}},
    {"id": "corporate", "zotero": {"itemType": "report", "title": "Research With R", "institution": "Research and Training Institute", "creators": [{"creatorType": "author", "name": "Research and Training Institute"}], "date": "2024"}, "bibtex": "@techreport{corporate,title={Research With {R}},author={{Research and Training Institute}},institution={{Research and Training Institute}},year={2024}}", "expected": {"type": "report", "title": "Research With R", "publisher": "Research and Training Institute", "author": [{"literal": "Research and Training Institute"}], "issued": {"date-parts": [[2024]]}}},
])

TYPE.update({"preprint": "article", "conferencePaper": "paper-conference", "book": "book", "magazineArticle": "article-magazine", "standard": "standard", "patent": "patent", "presentation": "speech"})
# Every candidate alias is explicitly scoped by source type, including the old five.
SCOPED = {
    "thesis": ["university", "publisher", "thesisType"],
    "report": ["institution", "publisher", "reportType", "reportNumber"],
    "journalArticle": ["publicationTitle", "volume", "issue", "pages"],
    "magazineArticle": ["publicationTitle", "volume", "issue", "pages"],
    "bookSection": ["bookTitle", "publisher", "place", "pages"],
    "book": ["publisher", "place"],
}
TYPE_FIELDS = {kind: {k: FIELDS[k] for k in ["title", "url", *SCOPED.get(kind, [])]} for kind in TYPE}
TYPE_FIELDS["preprint"].update({"archiveID": "number", "repository": "archive"})
TYPE_FIELDS["conferencePaper"].update({"proceedingsTitle": "container-title", "conferenceName": "event-title"})
TYPE_FIELDS["book"].update({"edition": "edition", "series": "collection-title", "ISBN": "ISBN"})
TYPE_FIELDS["standard"].update({"number": "number"})
TYPE_FIELDS["patent"].update({"patentNumber": "number"})
TYPE_FIELDS["presentation"].update({"meetingName": "event-title"})
CASES[5]["expected"].update({"number": "2401.01234", "archive": "arXiv"})
del CASES[5]["extension_expected"]


def title_comparable(value):
    # Pandoc applies sentence casing and nocase markup. Neither is a refs import rule.
    import re
    return re.sub(r"</?span[^>]*>", "", value).casefold()


def agent_projection(record):
    # Agent route is explicit CSL-shaped input: validate the exercised structures,
    # then retain them. This deliberately makes no claim of a complete validator.
    if record.get("type") not in TYPE.values() or not record.get("title"):
        raise ValueError("invalid synthetic agent record")
    if any(set(name) & {"literal"} and set(name) & {"family", "given"} for name in record.get("author", [])):
        raise ValueError("mixed name forms")
    return json.loads(json.dumps(record))


def zotero_projection(record):
    result = {"type": TYPE[record["itemType"]]}
    for name, value in record.items():
        if name in TYPE_FIELDS[record["itemType"]]:
            target = TYPE_FIELDS[record["itemType"]][name]
            if target in result and result[target] != value:
                raise ValueError(f"conflicting aliases for {target}")
            result[target] = value
    # Only these clean fixture dates are parsed here. Free-text dates need the
    # original plus separately validated API meta.parsedDate in the real design.
    result["issued"] = {"date-parts": [[int(p) for p in record["date"].split("-")]]}
    if "creators" in record:
        result["author"] = [{"literal": c["name"]} if "name" in c else {"family": c["lastName"], "given": c["firstName"]} for c in record["creators"]]
    return result


def main():
    results = {"purpose": "Design evidence only; no refs code exists", "pandoc": subprocess.check_output(["pandoc", "--version"], text=True).splitlines()[0], "cases": []}
    for case in CASES:
        parsed = json.loads(subprocess.check_output(["pandoc", "-f", "biblatex", "-t", "csljson"], input=case["bibtex"], text=True))[0]
        z = zotero_projection(case["zotero"])
        comparison = dict(parsed)
        if "event" in comparison and "event-title" not in comparison:
            comparison["event-title"] = comparison["event"]
        differences = {k: {"expected": v, "pandoc": comparison.get(k)} for k, v in case["expected"].items() if (title_comparable(comparison.get(k, "")) != title_comparable(v) if k in {"title", "container-title", "collection-title", "event-title"} else comparison.get(k) != v)}
        assert z == case["expected"], case["id"]
        agent_input = json.loads(json.dumps(case["expected"]))
        agent = agent_projection(agent_input)
        assert agent == z, case["id"]
        # Deliberately report reader differences rather than massage its result.
        additional = {}
        if case["id"] == "patent":
            additional = {"patent_assignees": [{"literal": case["zotero"]["assignee"]}]}
            assert additional == case["extension_expected"]
        results["cases"].append({**case, "agent_input": agent_input, "agent_projection": agent, "zotero_projection": z, "extension_projection": additional, "pandoc_projection": parsed, "pandoc_differences": differences})

    # Conflicting synonyms must be surfaced, not accepted as independent facts.
    conflict = {"itemType": "thesis", "date": "2024", "university": "A", "publisher": "B"}
    try:
        zotero_projection(conflict)
    except ValueError:
        results["alias_conflict_detected"] = True
    else:
        raise AssertionError("conflicting publisher aliases accepted")

    # No lossy upstream crosswalk is implicitly admitted to this candidate map.
    excluded = ["programmingLanguage", "applicationNumber", "session", "priorityNumbers", "codeNumber", "committee"]
    assert all(field not in FIELDS for field in excluded)
    results["approximate_aliases_not_collapsed"] = excluded
    (ROOT / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"cases": len(CASES), "differences": {c["id"]: c["pandoc_differences"] for c in results["cases"]}, "alias_conflict_detected": True}, indent=2))


if __name__ == "__main__":
    main()
