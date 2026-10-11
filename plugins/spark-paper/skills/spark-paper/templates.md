# Templates

Fixed shapes for every output. The workbook is the output; the record is how it is filled.

## A. Record (one JSON per paper)

The single source for the workbook rows and the Zotero note. Fields with no source are omitted, never invented.

```json
{
  "id": "Author2020",
  "short": "Author 2020 Venue",
  "citation": "Author A, Author B. Title. Venue vol:pages (year).",
  "doi": "10.xxxx/yyyy",
  "pmid": "",
  "type": "research article",
  "topic": "short topic phrase",
  "status": "to-read | summary | read",
  "tags": [],
  "sections": ["findings", "methods"],
  "zotero": {"item_key": "", "pdf_key": ""},
  "cross_check": {"done": true, "date": "YYYY-MM-DD", "disagreements": 0},
  "sets_out": "the central question",
  "reading_plan": "what to read first and what to skim",
  "summary": "about 1000 characters",
  "takeaways": "about 1500 characters",
  "findings": [{"where": "p. 3, Results", "page": 3, "finding": "", "number": "",
    "producer": "MEASURED BY THE AUTHORS", "figure": "Fig. 2B", "check": "matched"}],
  "methods": [{"item": "", "detail": "", "label": "stated", "where": "p. 2", "page": 2}],
  "figures": [{"ref": "Fig. 2", "shows": "", "values": "", "supports": "F1", "page": 3}],
  "terms": [{"term": "", "definition": "", "where": "", "page": 2, "analogy": "", "breaks": ""}],
  "discussion": [{"kind": "Question", "point": "", "where": "", "qalmri": "A"}],
  "crosscheck_log": [{"field": "", "draft": "", "verifier": "", "class": "value mismatch",
    "resolution": "", "locus": ""}]
}
```

| Field | Allowed values (anything else is rejected) |
|-------|--------------------------------------------|
| `status` | to-read, summary, read (`read` is written as `summary` unless `cross_check.done`) |
| `producer` | MEASURED BY THE AUTHORS, REPORTED FROM CITED WORK, AUTHORS' INTERPRETATION, BACKGROUND STATEMENT |
| `label` | stated, inferred, unspecified |
| `check` | matched, corrected, added, open |
| `class` | value mismatch, draft-only, source-only, emphasis mismatch, label mismatch |
| `kind` | Question, Limitation (stated by the authors), Limitation (evident to a careful reader) |
| `qalmri` | Q, A, L, M, R, I |
| `sections` | findings, methods, figures, terms, discussion, crosscheck |

`sections` is optional: the sections the reader chose. A section not chosen has no list in the record; with `sections` set, a missing list is not flagged. `page` is the PDF page index, so a Where cell can link to that page in the Zotero reader.

**Pre-read record (PREP).** The same record with `status: "to-read"`, no `findings`, and these fields filled: `sets_out` (the central question), `type`, `topic`, `reading_plan`, `terms` (jargon to know going in), and `discussion` rows of kind Question (questions to hold while reading). Nothing in it is a verdict.

## B. Workbook (`scripts/cheatsheet.py`)

One multi-paper `.xlsx`. Only the chosen sheets exist (Papers and Notes always do); a later paper that adds a section adds its sheet. Re-annotating a paper replaces only its rows; grey-blue header columns belong to the reader and are kept; the hidden `Key` column ties rows to papers; text is stored as text, never as a formula.

| Sheet | One row per | Holds |
|-------|-------------|-------|
| About | legend | Status ladder, labels, live counts |
| Papers | paper | Citation, DOI, type, topic, status, cross-check, central question, reading plan, summary, takeaways, Zotero and PDF links, tags, reader notes |
| Notes | reader note | The reader's own space: paper, date, kind, note, page. The skill never writes to it. |
| Findings | claim | Where, finding, number, producer, figure, check |
| Methods | method item | Item, detail, label, where, check |
| Figures | figure or table | What it shows, values read, which findings it supports |
| Terms | term | Definition, where, checked analogy and where it breaks |
| Discussion | question or limitation | Kind, point, QALMRI letter, reader status and answer |
| CrossCheck | difference | Field, draft, verifier, class, resolution, locus |
| Curriculum | paper in a reading order | Topic, order, paper, goal, self-check question, reader status |
| Lists (hidden) | value | Vocabularies behind the drop-downs; no need to open it |

## C. Zotero note (`zotero_bridge.py push`)

One child note per paper, tagged `spark-paper`, rendered from the record: provenance, central question, reading plan, summary, takeaways, key findings with producer labels, reproducibility gaps, open questions. Re-pushing updates it in place. The parent item gets tags `spark-paper` and `sp:status:<status>` (an older status tag is replaced; nothing else is touched) and a linked-file attachment pointing at the workbook.

## D. Curriculum record (CURRICULUM, explicit request only)

```json
{"topic": "Topic name",
 "papers": [{"paper": "Author 2020 Venue", "goal": "what this one establishes",
   "question": "a question the reader should be able to answer"}]}
```

`cheatsheet.py curriculum file.json --workbook <workbook>` adds or replaces that topic's rows on the Curriculum sheet. The reader's Status column is kept on re-runs.
