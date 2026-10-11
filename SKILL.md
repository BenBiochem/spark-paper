---
name: spark-paper
description: >
  Depth on one academic paper. PREP: a pre-read brief. READ: a guided read.
  ANNOTATE: a durable note, cheat-sheet workbook rows (.xlsx), and a Zotero
  note, cross-checked against the source by a draft-blind verifier. CURRICULUM:
  a learning hub for a topic (explicit request only). Triggers: "prep me for this
  paper", "read this paper with me", "walk me through this paper", "annotate this
  paper", "write a literature note", "make reading notes", "summarize this paper
  into a note", "make a cheat sheet for this paper", "add this to the reading
  spreadsheet", "put this in Zotero", "explain this concept from the paper". Not
  for critiquing a claim, deciding what to pursue, or surveying many sources.
---

# spark-paper

Depth on one paper. Two commitments:

- **Orient, do not pre-digest.** Give the map and the vocabulary; leave the verdict to the reader. Choosing "key findings" is itself a reading judgment, so it is presented as an aid.
- **Trace and cross-check.** Every claim points to a place in the source and is re-derived by a verifier that never saw the draft. The skill reports what the paper says, not whether the paper is right.

Method, labels, agents, and the cross-check procedure: `reading-method.md`. Output formats: `templates.md`.

## Pipeline (every mode)

| Stage | What happens |
|-------|--------------|
| 1. Resolve | Read config (below). Never block on it; announce the target in one line. |
| 2. Source | Identify the paper and read it. PDF and figures: natively with the Read tool (`pages` for long PDFs); text extraction is a search aid, never the read. Word/ODT/PPTX/HTML/txt: `scripts/extract_text.py`. In Zotero: `scripts/zotero_bridge.py find`, then `pdf <key>`. Metadata: `scripts/verify_doi.py` (Crossref); anything unverifiable is `[unverified]`. |
| 3. Draft | Fill the mode's template (`templates.md`). |
| 4. Check | Run the self-check (below). |
| 5. Emit | Write the outputs, then print the report line. |

**Config.** Look for a `CONVENTIONS (spark-paper)` block in the project `CLAUDE.md`, or `.spark-paper.yml`. Defaults apply for anything missing:

| Key | Default |
|-----|---------|
| `annotations_dir` | `./papers/` |
| `index_file` | `./papers/INDEX.md` |
| `naming` | `Author Year -- Short Title.md` |
| `wikilinks` | `false` (standard markdown links) |
| `workbook` | `./papers/Paper_Reading_Notes.xlsx` |
| `zotero` | `auto` (or `off`) |
| `zotero_collection` | none |

## Modes

| Mode | Trigger | Output | Status |
|------|---------|--------|--------|
| PREP | "prep me", "pre-read", or a paper named with no verb | Brief (template A) and a `to-read` workbook row (central question only) | `to-read` |
| READ | "read with me", "walk me through" | Guided passes and running notes; no files | none |
| ANNOTATE | "annotate", "note", "cheat sheet", "summarize into a note" | Note (B), record (D) into the workbook (E) and Zotero (F) | `summary` or `read` |
| CURRICULUM | explicit only | Learning hub (C) | none |

The concept-aid (`reading-method.md` section 5) runs inside any mode on request.

## ANNOTATE sequence

1. Draft the note and the record (one JSON per paper, `templates.md` D). The note, the workbook rows, and the Zotero note are all rendered from the same record.
2. Run the blind cross-check with the Verifier agent (`reading-method.md` sections 3 and 4). `read` only after it completes.
3. `scripts/cheatsheet.py check record.json`.
4. Zotero, if `zotero` is not `off` and `zotero_bridge.py status` shows it reachable and writable: `zotero_bridge.py push record.json --workbook <workbook> --write-back`. No write key: say so in one line and continue (`zotero_bridge.py auth` grants it once). Unreachable: skip, say so, continue.
5. `scripts/cheatsheet.py upsert record.json --workbook <workbook>`.
6. Write the note to `annotations_dir`; append one line to `index_file` if configured.

## Self-check (before every emit)

1. Every claim has a locus: page, section, or figure.
2. Citation fields come from Crossref or the title page; the rest are `[unverified]`.
3. Findings carry a producer label; method items carry a stated/inferred/unspecified label.
4. `read` means the blind cross-check ran and every difference is reconciled or logged. Otherwise `summary`.
5. `cheatsheet.py check` passes with no errors (read its warnings).
6. PREP and READ contain no verdict language.

## Report line (fixed format, last thing printed)

```
spark-paper | <short> | status <s> | cross-check <done, N diffs | not run> | note <path> | sheet <+rows | skipped> | zotero <created | updated | unchanged | skipped>
```

## Rules

- Never invent a DOI, author, year, or link.
- Claim only what the check delivers: "cross-checked against the source", not "verified".
- A result the paper only cites is not its finding; label it REPORTED FROM CITED WORK.
- No bare analogy: ship all four parts (mapping, holds, breaks, net) or none.
- Zotero is add-only: the skill's own note, two tags (`spark-paper`, `sp:status:<status>`), and a workbook link. Highlights are read-only and not copied unless asked.
- Never overwrite a workbook an editor has open (the script refuses; do not pass `--force` unprompted).
- Stay in lane: critique and go/no-go decisions belong to a critique skill, breadth to a research skill.
- Egress: Crossref metadata only; the Zotero bridge talks to localhost only; a local PDF never leaves the machine; full-text web fetch only if the user supplies the URL or DOI.
