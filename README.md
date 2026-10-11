# spark-paper
<img width="1024" height="1535" alt="Study smart with Spark-Paper" src="https://github.com/user-attachments/assets/e913b824-c210-4970-9ddf-7f7bb9332ecf" />

SparkNotes for academic papers, with a twist. A normal summary reads the paper for you so you can skip it. spark-paper does the opposite: it helps you read and understand the paper yourself.

It works in four steps: it gets you ready to read, goes through the paper with you, writes clear notes you can keep, and then checks those notes back against the paper so nothing is wrong or made up.

Think of it as a study partner for dense papers, not a shortcut around them.

## Quick start

Point it at a paper (a PDF, a Word file, a DOI, or just its name if it is in your Zotero library), then say one of these:

| Say | You get |
|-----|---------|
| prep me for this paper | a pre-read brief: the 5 C's, the central question, the jargon, a reading map. No spoilers. |
| read this paper with me | a guided pass, section by section, with the figures and methods explained. |
| annotate this paper | a durable note (short or full), then a draft-blind check against the source. |
| make a cheat sheet for this paper | the same paper as rows in an Excel workbook: findings, methods, figures, terms, open questions. |
| put this in Zotero | a note and a status tag on the paper's Zotero item, linked to the workbook. |
| analogize [a hard idea] | an analogy with its limits marked, plus a best-effort falsity-check. |
| build a reading curriculum for [topic] | a learning hub across several papers (on request). |

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| PREP | "prep me for this paper" | a pre-read brief (5 C's, central question, jargon, reading map); no spoilers |
| READ | "read this with me" | guided, section by section; QALMRI lens; running notes |
| ANNOTATE | "annotate / write a note / summarize into a note" | a durable note (short or full) plus a draft-blind check |
| CURRICULUM | explicit only | a learning hub for a set of papers |

<img width="1024" height="572" alt="image" src="https://github.com/user-attachments/assets/9998611b-6832-446c-bf72-2e7e1afcd4e4" />


The concept-aid runs across all of them. Ask it to analogize or explain a hard idea and it returns the mapping, where it holds, where it breaks, and the net, then checks that against the source.

## The 5 C's

PREP uses Keshav's five questions for a first skim of any paper. They set up the read without judging the paper. They belong to the pre-read brief; the workbook does not repeat them.

| C | What it asks |
|---|--------------|
| Category | What kind of paper is it: method, discovery, theory, benchmark, or review? |
| Context | What prior work does it sit against? |
| Correctness | What assumptions should you check while reading? Listed, not yet judged. |
| Contributions | What does it claim is new? |
| Clarity | How well is it written, and where will it be hard going? |

## The two checks

| Check | How it works | What it claims |
|-------|--------------|----------------|
| Cross-check (notes) | a sub-agent reads the source without seeing the draft, re-extracts the same fields, and the draft is diffed against it; every difference is reconciled at the source. Gates `status: read`. | the note is consistent, traced to a locus, and diffed by a verifier that never saw it. Not a proof of truth, and it checks fidelity to the paper, not whether the paper is right. |
| Falsity-check (analogies) | generate, check against the source, fence the leaks or drop the analogy | best-effort, not a proof |

Why the verifier works blind: a model re-reading its own draft tends to confirm its own confident mistakes. A verifier that never sees the draft has errors independent of it, so agreement is real evidence and a difference is a real flag.

## Cheat sheet

Annotating a paper can also add it to one Excel workbook that grows as you read: a Papers index plus sheets for Findings, Methods, Figures, Terms, Discussion, and the cross-check log. Each finding is labeled by who produced it: measured by the authors, cited from other work, the authors' interpretation, or background. Re-annotating a paper updates its rows and leaves your own notes columns alone.

## Choose what you get

Annotating a paper can produce a lot, so the skill asks once which sections you want:

| Preset | What it includes |
|--------|------------------|
| Quick | The Papers row and Findings |
| Standard (default) | Quick, plus Methods, Discussion, and the Zotero note |
| Full | Standard, plus Figures, Terms, the cross-check log, and a Markdown note |
| Custom | Any mix of those |

Only the sheets you choose are created. The cross-check still runs either way. To skip the question, set `sections: standard` (or `quick`, `full`) in your config.

## Zotero

Zotero works in both directions, and reading from it comes first.

**Reads from Zotero.** Name a paper and the skill looks for it in your library before asking for a file. Say "annotate the Keshav 2007 paper", give a DOI, or type a few words from the title. It searches your library, opens the PDF from there, and reads any highlights you made. If several papers match it asks which one; if none match it says so and asks for a file or DOI.

**Writes to Zotero.** After annotating, it can add a note, a status tag, and a link to the workbook to that same item. It only adds. It never edits or deletes anything else in your library, and it never adds a paper just to read it.

Everything stays on your own machine; the skill talks to Zotero locally.

Setup:

1. To read: in Zotero, turn on "Allow other applications on this computer to communicate with Zotero" (Advanced settings). That is all that is needed to search and read.
2. To write (optional): ask Claude to set up Zotero write access. It runs `zotero_bridge.py auth` once; choose "Always Allow" in the Zotero window.

## What a note looks like

The Markdown note is optional; the workbook covers the same ground. When you ask for it, a full note has: Citation, Core claim, Key findings, Methods (a short version and a reproduction-grade version, with each detail in the long one marked `[stated]`, `[inferred]`, or `[unspecified]`), a Reading guide, Open questions, Key takeaway, and Related links, plus a provenance line that logs the cross-check. The short tier drops the expanded methods and the cross-check until you do a full read.

## Install

**As a plugin** (Claude Code 2.1.275 or later):

```
/plugin install spark-paper --marketplace BenBiochem/spark-paper
```

On an older version of Claude Code, use two steps: `/plugin marketplace add BenBiochem/spark-paper`, then `/plugin install spark-paper@spark-paper`.

**On claude.ai (web):** go to Customize > Plugins > Add > Add marketplace > Add from a repository, enter `BenBiochem/spark-paper`, choose Sync, then add the plugin from the list. There is nothing to download.

**By hand:** copy the skill folder into your skills directory (or a project's `.claude/skills/`):

```bash
cp -r plugins/spark-paper/skills/spark-paper ~/.claude/skills/
```

The core has no dependencies. The Python helpers use only the standard library (the workbook script also needs `openpyxl`), so Word, ODT, PPTX, HTML, and text extraction work out of the box, and PDFs (with their figures) are read natively by the host. `convert_docx.sh` is an optional higher-fidelity path that needs `pandoc`.

Inputs: PDF and figures read natively; Word, ODT, PPTX, HTML, and text via `extract_text.py`; DOIs verified through Crossref; arXiv and URL metadata, with full text opt-in.

## Other places it runs

It is built for Claude Code, where everything works. On other Claude surfaces or agents, attach one PDF or several to the conversation and it works through them one at a time, as far as the host can read PDFs and run scripts. Without sub-agents the cross-check falls back to a self-consistency pass and the note stays at `summary`. Without access to your machine, the Zotero steps are skipped, and a DOI or an attached PDF is the source instead. On claude.ai the session workspace is temporary: download the note and workbook when it finishes, and attach the workbook next time to keep adding rows to it.

## Where notes land

Nothing is hard-coded. The skill reads a `CONVENTIONS (spark-paper)` block from your project `CLAUDE.md` (or a `.spark-paper.yml`). If there is none, it uses sane defaults and goes ahead, asking only if you object. Example:

```yaml
# CONVENTIONS (spark-paper)
annotations_dir: references/annotations
index_file: references/References.md
naming: "Author Year -- Short Title.md"
wikilinks: true
workbook: references/Paper_Reading_Notes.xlsx
zotero: auto            # or off
sections: ask           # or quick, standard, full
```

## Files

```
.claude-plugin/marketplace.json
plugins/spark-paper/
  .claude-plugin/plugin.json
  skills/spark-paper/
    SKILL.md            pipeline, modes, self-check, rules
    reading-method.md   reading passes, labels, agents, the draft-blind cross-check
    templates.md        prep brief, note, curriculum, record, workbook, Zotero note
    scripts/            verify_doi.py, extract_text.py, convert_docx.sh, lint_frontmatter.py,
                        cheatsheet.py (workbook), zotero_bridge.py (Zotero)
    examples/           record.example.json
```

## Glossary

- Keshav three-pass: a standard way to read a paper (skim, then read, then reconstruct). The first pass uses the 5 C's.
- The 5 C's: see [The 5 C's](#the-5-cs) above.
- QALMRI: a comprehension checklist (Question, Alternatives, Logic, Method, Results, Inferences).

## Credits

- Reading method: Keshav, How to Read a Paper (ACM SIGCOMM CCR, 2007).
- Comprehension scaffold: Brosowsky and Parshina, Using the QALMRI Method (2017).
- The blind check follows the work on LLM explanation faithfulness: a model's self-explanation can be plausible but unfaithful, so independence from the draft is what makes the check mean something.

## License

MIT. Copyright (c) 2026 Benjamin E. Peterson. See [LICENSE](LICENSE).
