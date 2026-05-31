#!/usr/bin/env python3
"""verify_doi.py: verify a paper's bibliographic metadata against Crossref.

Part of the `spark-paper` skill. Enforces the IRON RULE "never fabricate a
citation field": before a note's Citation block is written, the DOI or title is
resolved against Crossref (the open scholarly-metadata registry) so that
authors, year, venue, and the canonical DOI come from an authority rather than
from the model's memory.

Standard library only (no `pip install`). Read-only: a single GET to
api.crossref.org. No API key required; set the CROSSREF_MAILTO environment
variable to an email to join Crossref's faster "polite pool".

Usage:
    verify_doi.py 10.3389/fbioe.2020.558247
    verify_doi.py --title "Cartesian ddG protocol for stability"
    verify_doi.py --doi 10.xxxx/yyyy --json
"""
import argparse
import json
import os
import urllib.parse
import urllib.request

API = "https://api.crossref.org/works"


def _get(url):
    """GET a Crossref URL and return parsed JSON, identifying politely."""
    mailto = os.environ.get("CROSSREF_MAILTO", "").strip()
    ua = "spark-paper-skill/1.0 (https://www.crossref.org/; mailto:%s)" % mailto \
        if mailto else "spark-paper-skill/1.0 (https://www.crossref.org/)"
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def by_doi(doi):
    """Resolve a single work by DOI (accepts bare, doi:, or URL forms)."""
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return _get("%s/%s" % (API, urllib.parse.quote(doi)))["message"]


def by_title(title):
    """Resolve the best-matching work by bibliographic title query."""
    query = urllib.parse.urlencode({"query.bibliographic": title, "rows": 1})
    items = _get("%s?%s" % (API, query))["message"].get("items", [])
    if not items:
        raise SystemExit("No Crossref match for title: %s" % title)
    return items[0]


def fmt(message):
    """Reduce a Crossref work record to the citation fields a note needs."""
    authors = ", ".join(
        " ".join(part for part in (a.get("given"), a.get("family")) if part)
        for a in message.get("author", [])
    ) or "[unverified]"
    date_parts = message.get("issued", {}).get("date-parts", [[None]])
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    doi = message.get("DOI")
    return {
        "title": (message.get("title") or ["[unverified]"])[0],
        "authors": authors,
        "year": year if year else "[unverified]",
        "venue": (message.get("container-title") or ["[unverified]"])[0],
        "doi": "https://doi.org/%s" % doi if doi else "[unverified]",
        "type": message.get("type", ""),
    }


def main():
    ap = argparse.ArgumentParser(description="Verify paper metadata via Crossref.")
    ap.add_argument("doi", nargs="?",
                    help="DOI in bare, doi:, or https://doi.org/ form")
    ap.add_argument("--doi", dest="doi_flag", help="DOI (alternative to positional)")
    ap.add_argument("--title", help="resolve by bibliographic title instead")
    ap.add_argument("--json", action="store_true", help="emit raw JSON")
    args = ap.parse_args()

    try:
        if args.title:
            record = by_title(args.title)
        else:
            doi = args.doi_flag or args.doi
            if not doi:
                ap.error("supply a DOI (positional or --doi) or --title")
            record = by_doi(doi)
    except SystemExit:
        raise
    except Exception as exc:  # network / parse / HTTP errors
        raise SystemExit("Crossref lookup failed: %s" % exc)

    out = fmt(record)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for key in ("title", "authors", "year", "venue", "doi", "type"):
            print("%-8s %s" % (key + ":", out[key]))


if __name__ == "__main__":
    main()
