---
name: spark-paper
description: >
  Depth on one academic paper, kept in one Excel workbook. PREP: pre-read rows
  (central question, jargon, questions to hold, a reading plan). READ: a guided
  read. ANNOTATE: findings, methods, figures, terms, and open questions,
  cross-checked against the source by a draft-blind verifier, with optional
  Zotero sync. CURRICULUM: a reading order for a topic (explicit request only).
  Triggers: "prep me for this paper", "read this paper with me", "walk me through
  this paper", "annotate this paper", "make reading notes", "summarize this
  paper", "make a cheat sheet for this paper", "add this to the reading
  spreadsheet", "find it in Zotero", "read it from my Zotero", "put this in
  Zotero", "set up Zotero access", "explain this concept from the paper". Not for
  critiquing a claim, deciding what to pursue, or surveying many sources.
---

# spark-paper

Depth on one paper, kept in one workbook. Two commitments:

- **Orient, do not pre-digest.** Give the map and the vocabulary; leave the verdict to the reader. Choosing "key findings" is itself a reading judgment, so it is presented as an aid.
- **Trace and cross-check.** Every claim points to a place in the source and is re-derived by a verifier that never saw the draft. The skill reports what the paper says, not whether the paper is right.

The workbook is the pre-read, the starting notes, and the record. The reader owns its Notes sheet; the skill never writes to it. Method, labels, agents, and the cross-check procedure: `reading-method.md`. Formats: `templates.md`.

## Pipeline (every mode)

| Stage | What happens |
|-------|--------------|
| 1. Resolve | Read config (below) and settle the sections (see Sections). Never block on config; announce the target in one line. |
| 2. Source | Identify the paper and read it. **Zotero is the first place to look** whenever a paper is named without a file and `zotero` is not `off`: `scripts/zotero_bridge.py source "<what was said>"` takes a DOI, item key, title, author and year, or a few words, and returns matches with a local PDF path and a highlight count. One match: read it. Several: ask which. None: say so, then fall back to a file or DOI; never add a paper to Zotero just to read it. Read the PDF and figures natively with the Read tool (`pages` for long PDFs), from the Zotero path or a given path; text extraction is a search aid, never the read. If the reader has highlights (`zotero_bridge.py annotations <key>`), treat them as pointers to what they found notable, not as findings. Word/ODT/PPTX/HTML/txt: `scripts/extract_text.py`. Metadata: `scripts/verify_doi.py` (Crossref); anything unverifiable is `[unverified]`. |
| 3. Draft | Build the record (`templates.md` A): one JSON per paper. |
| 4. Check | Run the self-check (below). |
| 5. Emit | Write to the workbook (and Zotero if chosen), then print the report line. |

**Other hosts.** A PDF attached to the conversation counts as a given file; several PDFs are annotated one at a time into the same workbook. If the host cannot run scripts or spawn a sub-agent, skip the script step or use the self-consistency fallback (status stays `summary`) and say which was skipped. With no project folder, write the workbook where the host provides and hand the file back.

**Config.** Look for a `CONVENTIONS (spark-paper)` block in the project `CLAUDE.md`, or `.spark-paper.yml`. Defaults apply for anything missing:

| Key | Default |
|-----|---------|
| `workbook` | `./papers/Paper_Reading_Notes.xlsx` |
| `zotero` | `auto` (or `off`) |
| `zotero_collection` | none |
| `sections` | `ask` (or `quick`, `standard`, `full`, or a list) |

## Modes

| Mode | Trigger | Writes | Status |
|------|---------|--------|--------|
| PREP | "prep me", "pre-read", or a paper named with no verb | A `to-read` record: Papers row (central question, topic, reading plan), Terms (jargon), and Discussion questions to hold while reading. No findings. | `to-read` |
| READ | "read with me", "walk me through" | Nothing: guided passes and running notes in chat | none |
| ANNOTATE | "annotate", "notes", "cheat sheet", "summarize" | The record for the chosen sections, into the workbook, plus the Zotero note if chosen | `summary` or `read` |
| CURRICULUM | explicit only | A reading order on the Curriculum sheet (`templates.md` D) | none |

The concept-aid (`reading-method.md` section 5) runs inside any mode on request.

## Sections (ask once)

ANNOTATE can produce a lot, so the reader chooses what to include. If the request does not say and `sections` is `ask`, ask once with the presets below, remember the answer for the session, and offer to save it as `sections:` in config. Where the host cannot ask, use Standard. In Claude Code, use a single-choice question with the presets, then a multi-select only if they pick Custom.

| Preset | Includes |
|--------|----------|
| Quick | Papers row, Findings |
| Standard (default) | Quick, plus Methods, Discussion, and the Zotero note |
| Full | Standard, plus Figures, Terms, and CrossCheck |
| Custom | Any mix of the sheets (Findings, Methods, Figures, Terms, Discussion, CrossCheck) and the Zotero note |

Papers and Notes are always present. The choice sets what is drafted, what the verifier extracts, and which sheets exist; the blind cross-check still gates `read`. A section not chosen is left out of the record (list the chosen ones in `sections`), not written blank. PREP does not ask: it always writes the pre-read rows.

## ANNOTATE sequence

1. Draft the record for the chosen sections. The workbook rows and the Zotero note are both rendered from it.
2. Run the blind cross-check with the Verifier agent (`reading-method.md` sections 3 and 4), limited to the chosen sections. `read` only after it completes.
3. `scripts/cheatsheet.py check record.json`.
4. Zotero note, if chosen, `zotero` is not `off`, and `zotero_bridge.py status` shows it reachable and writable: `zotero_bridge.py push record.json --workbook <workbook> --write-back`. No write key: say so in one line and continue (`zotero_bridge.py auth` grants it once). Unreachable: skip, say so, continue.
5. `scripts/cheatsheet.py upsert record.json --workbook <workbook>`.

PREP and CURRICULUM run steps 3 and 5 only (`cheatsheet.py curriculum` for a reading order).

## Self-check (before every emit)

1. Every claim has a locus: page, section, or figure.
2. Citation fields come from Crossref or the title page; the rest are `[unverified]`.
3. Findings carry a producer label; method items carry a stated/inferred/unspecified label.
4. `read` means the blind cross-check ran and every difference is reconciled or logged. Otherwise `summary`.
5. `cheatsheet.py check` passes with no errors (read its warnings).
6. PREP and READ contain no verdict language.

## Report line (fixed format, last thing printed)

```
spark-paper | <short> | source <zotero | file | doi> | sections <quick | standard | full | custom> | status <s> | cross-check <done, N diffs | not run> | sheet <+rows | skipped> | zotero <created | updated | unchanged | skipped>
```

## Rules

- Never invent a DOI, author, year, or link.
- Claim only what the check delivers: "cross-checked against the source", not "verified".
- A result the paper only cites is not its finding; label it REPORTED FROM CITED WORK.
- No bare analogy: ship all four parts (mapping, holds, breaks, net) or none.
- A paper the user names is looked up in Zotero before asking for a file.
- Zotero writes are add-only: the skill's own note, two tags (`spark-paper`, `sp:status:<status>`), and a workbook link. Highlights are read-only and not copied unless asked.
- Never write to the Notes sheet. Never overwrite a workbook an editor has open (the script refuses; do not pass `--force` unprompted).
- Stay in lane: critique and go/no-go decisions belong to a critique skill, breadth to a research skill.
- Egress: Crossref metadata only; the Zotero bridge talks to localhost only; a local PDF never leaves the machine; full-text web fetch only if the user supplies the URL or DOI.
