# read-paper

A Claude Code skill for reading one paper closely: get ready to read it, read it with guidance, write a durable note, and check that note back against the source.

It follows one rule: orient, don't pre-digest. The skill builds the map and the vocabulary and reads alongside you, but it leaves the verdict to you. Choosing what counts as a key finding is itself a reading call, so the brief offers its ranking as an aid, not a ruling.

## Quick start

Point it at a paper (PDF, Word, or a DOI), then say one of these:

| Say | You get |
|-----|---------|
| prep me for this paper | a pre-read brief: the 5 C's, the central question, the jargon, a reading map. No spoilers. |
| read this paper with me | a guided pass, section by section, with the figures and methods explained. |
| annotate this paper | a durable note (short or full), then a draft-blind check against the source. |
| analogize [a hard idea] | an analogy with its limits marked, plus a best-effort falsity-check. |
| build a reading curriculum for [topic] | a learning hub across several papers (on request). |

## Where it sits

Three sibling skills cover different needs:

| Want | Use |
|------|-----|
| Depth on one paper | read-paper (this) |
| A verdict on a claim or design | research-council |
| Breadth across many sources | hyperresearch |

Next to public paper tools:

| Tool type | What it does | What read-paper does instead |
|-----------|--------------|------------------------------|
| Summarizers (Scholarcy) | hand you the conclusion | get you ready to read it yourself |
| Explainers (Explainpaper, SciSpace) | explain a passage | explain, then falsity-check the analogy |
| RAG-QA (PaperQA2) | answer questions over a corpus | audit its own note against the source |
| Guided readers (InsightGUIDE) | take a position | stay neutral |

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| PREP | "prep me for this paper" | a pre-read brief (5 C's, central question, jargon, reading map); no spoilers |
| READ | "read this with me" | guided, section by section; QALMRI lens; running notes |
| ANNOTATE | "annotate / write a note / summarize into a note" | a durable note (short or full) plus a draft-blind check |
| CURRICULUM | explicit only | a learning hub for a set of papers |

The concept-aid runs across all of them. Ask it to analogize or explain a hard idea and it returns the mapping, where it holds, where it breaks, and the net, then checks that against the source.

## The two checks

| Check | How it works | What it claims |
|-------|--------------|----------------|
| Cross-check (notes) | a sub-agent reads the source without seeing the draft, re-extracts the same fields, and the draft is diffed against it; every difference is reconciled at the source. Gates `status: read`. | the note is consistent, traced to a locus, and diffed by a verifier that never saw it. Not a proof of truth, and it checks fidelity to the paper, not whether the paper is right. |
| Falsity-check (analogies) | generate, check against the source, fence the leaks or drop the analogy | best-effort, not a proof |

Why the verifier works blind: a model re-reading its own draft tends to confirm its own confident mistakes. A verifier that never sees the draft has errors independent of it, so agreement is real evidence and a difference is a real flag.

## What a note looks like

A full note has: Citation, Core claim, Key findings, Methods (a short version and a reproduction-grade version, with each detail in the long one marked `[stated]`, `[inferred]`, or `[unspecified]`), a Reading guide, Open questions, Key takeaway, and Related links, plus a provenance line that logs the cross-check. The short tier drops the expanded methods and the cross-check until you do a full read.

## Install

Copy `read-paper/` into `~/.claude/skills/`, or into a project's `.claude/skills/`. The core has no dependencies. The Python helpers use only the standard library, so Word, ODT, PPTX, HTML, and text extraction work out of the box, and PDFs (with their figures) are read natively by the host. `convert_docx.sh` is an optional higher-fidelity path that needs `pandoc`.

Inputs: PDF and figures read natively; Word, ODT, PPTX, HTML, and text via `extract_text.py`; DOIs verified through Crossref; arXiv and URL metadata, with full text opt-in.

## Where notes land

Nothing is hard-coded. The skill reads a `CONVENTIONS (read-paper)` block from your project `CLAUDE.md` (or a `.read-paper.yml`). If there is none, it uses sane defaults and goes ahead, asking only if you object. Example:

```yaml
# CONVENTIONS (read-paper)
annotations_dir: references/annotations
index_file: references/References.md
naming: "Author Year -- Short Title.md"
wikilinks: true
```

## Files

```
read-paper/
  SKILL.md            modes, conventions, persistence
  reading-method.md   the reading passes, the draft-blind cross-check, methods labels, rules
  templates.md        prep brief, annotation (full and short), curriculum, index entry
  scripts/            verify_doi.py, extract_text.py, convert_docx.sh, lint_frontmatter.py
```

## Glossary

- Keshav three-pass: a standard way to read a paper (skim, then read, then reconstruct). The first pass uses the 5 C's: Category, Context, Correctness, Contributions, Clarity.
- QALMRI: a comprehension checklist (Question, Alternatives, Logic, Method, Results, Inferences).

## Credits and license

- Reading method: Keshav, How to Read a Paper (ACM SIGCOMM CCR, 2007).
- Comprehension scaffold: Brosowsky and Parshina, Using the QALMRI Method (2017).
- The blind check follows the work on LLM explanation faithfulness: a model's self-explanation can be plausible but unfaithful, so independence from the draft is what makes the check mean something.

MIT.
