#!/usr/bin/env python3
"""lint_frontmatter.py: check a note's YAML frontmatter for required fields.

Part of the `read-paper` skill. A durable note is only useful on later lookback
if its frontmatter is complete and its `status` is honest. This is a
lightweight, dependency-free check (no PyYAML) intended to run after a note is
written.

Required fields default to: title, date, authors, year, doi, venue, status.
`status` must be one of: to-read, summary, read.

Usage:
    lint_frontmatter.py note.md
    lint_frontmatter.py --required title,date,status note.md

Exit code 0 = clean, 1 = problems (printed).
"""
import argparse
import sys

DEFAULT_REQUIRED = ["title", "date", "authors", "year", "doi", "venue", "status"]
STATUS_OK = {"to-read", "summary", "read"}


def parse_frontmatter(text):
    """Return a dict of top-level YAML frontmatter keys, or None if absent.

    Deliberately minimal: handles the flat `key: value` lines that the
    templates emit. Not a full YAML parser; nested structures are ignored.
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    fm = {}
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or line.startswith(" "):
            continue  # skip blanks, comments, and nested/indented lines
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("note", help="path to the .md note")
    ap.add_argument("--required", default=",".join(DEFAULT_REQUIRED),
                    help="comma-separated required field names")
    args = ap.parse_args()
    required = [f.strip() for f in args.required.split(",") if f.strip()]

    try:
        with open(args.note, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise SystemExit("cannot read %s: %s" % (args.note, exc))

    fm = parse_frontmatter(text)
    problems = []
    if fm is None:
        problems.append("no YAML frontmatter block found")
    else:
        for field in required:
            value = fm.get(field, "")
            if not value or value in ("[]", "''", '""'):
                problems.append("missing or empty: %s" % field)
        status = fm.get("status", "")
        if status and status not in STATUS_OK:
            problems.append("status '%s' not in %s" % (status, sorted(STATUS_OK)))

    if problems:
        print("FAIL %s" % args.note)
        for p in problems:
            print("  - %s" % p)
        sys.exit(1)
    print("OK   %s" % args.note)


if __name__ == "__main__":
    main()
