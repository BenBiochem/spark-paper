# Templates

Fixed shapes for every output. Replace angle-bracket fields; omit a section only where noted. Links follow the resolved config (markdown by default, wikilinks if configured).

## Frontmatter (all notes)

```yaml
---
title: <Author Year -- Short Title>
date: <YYYY-MM-DD>
tags: [paper, <topic>]
authors: <Last F, Last F, ...>
year: <YYYY>
doi: <https://doi.org/... or [unverified]>
venue: <journal or conference>
status: <to-read | summary | read>
zotero: <zotero://select/library/items/KEY, when synced>
---
```

## A. Pre-read brief (PREP)

```markdown
# Pre-read: <Author Year -- Short Title>

> Brief, not a summary. Any ranking below is a reading aid, not a ruling on the work.

## 5 C's
- **Category:** <method | discovery | theory | benchmark | review>
- **Context:** <prior work and lineage>
- **Correctness to check:** <assumptions to watch while reading; not yet judged>
- **Contributions claimed:** <what the paper says is new>
- **Clarity:** <how hard a read; where it is dense>

## Central question
<one sentence>

## Prerequisites and jargon
| Term | What to know going in |
|------|-----------------------|

## Reading map
| Section | Read how | Why |
|---------|----------|-----|

**Figures first:** <order>

## Questions to hold while reading
- <question>
```

## B. Note (ANNOTATE)

Full (`read`) uses every section. Summary tier (`summary`) keeps Citation, Core claim, Key findings (3 to 6), Methods summarized, Key takeaway, Related.

```markdown
# <Author et al. Year: Full Title>

> [!note] Provenance
> Citation Crossref-verified <date>. Blind cross-check: <done, N differences, what changed | not run>.

## Citation
<authors, year, venue, DOI; affiliations and funding if relevant>

## Core claim
<2 to 4 sentences; the paper's own claim (QALMRI: Question and Inferences)>

## Key findings
- <finding> (<where>) [<producer label>]

## Methods, summarized
<approach, key technique and why, inputs to outputs, how validated>

## Methods, expanded
- <item>: <detail> `[stated | inferred | unspecified]` (<where>)

## Reading guide
**Order:** <1 ... n, with why>
**Jargon:** <term>: <definition> (optional: `analogy (checked): holds for A, breaks at B`)

## Open questions
- <question from QALMRI A or the R-to-I gap>

## Key takeaway
<one sentence>

## Related
- <links>
```

## C. Learning hub (CURRICULUM)

```markdown
---
title: <Topic> -- Learning Hub
date: <YYYY-MM-DD>
tags: [learning, <topic>]
status: active
---

# <Topic>: Learning Hub

> <the one load-bearing idea>

## Outcomes
1. <what the reader can do at the end>

## Framework
<a table or map that organizes the topic>

## Reading order
| # | Paper | Goal | Self-check question |
|---|-------|------|---------------------|
```

## D. Record (one JSON per paper; the single source for note, workbook, and Zotero)

Fields with no source are omitted, never invented.

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
  "zotero": {"item_key": "", "pdf_key": ""},
  "cross_check": {"done": true, "date": "YYYY-MM-DD", "disagreements": 0},
  "sets_out": "the central question",
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

`page` is the PDF page index, so a Where cell can link to that page in the Zotero reader.

## E. Workbook (`scripts/cheatsheet.py`)

One multi-paper `.xlsx`. Re-annotating a paper replaces only its rows; grey-blue header columns (Notes, Answer, Discussion Status) belong to the reader and are kept; the hidden `Key` column ties rows to papers; text is stored as text, never as a formula.

| Sheet | One row per | Holds |
|-------|-------------|-------|
| About | legend | Status ladder, labels, live counts |
| Papers | paper | Citation, DOI, type, topic, status, cross-check, central question, summary, takeaways, Zotero and PDF links, tags |
| Findings | claim | Where, finding, number, producer, figure, check |
| Methods | method item | Item, detail, label, where, check |
| Figures | figure or table | What it shows, values read, which findings it supports |
| Terms | term | Definition, where, checked analogy and where it breaks |
| Discussion | question or limitation | Kind, point, QALMRI letter, reader status and answer |
| CrossCheck | difference | Field, draft, verifier, class, resolution, locus |
| Lists | value | Vocabularies behind the drop-downs |

## F. Zotero note (`zotero_bridge.py push`)

One child note per paper, tagged `spark-paper`, rendered from the record: provenance, central question, summary, takeaways, key findings with producer labels, reproducibility gaps, open questions. Re-pushing updates it in place. The parent item gets tags `spark-paper` and `sp:status:<status>` (an older status tag is replaced; nothing else is touched) and a linked-file attachment pointing at the workbook.

## G. Index line (`index_file`)

```markdown
- [<Author Year -- Title>](<path>): <one-line descriptor of the contribution>
```
