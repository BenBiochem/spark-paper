# read-paper

A Claude Code skill for going deep on **one paper**: prepare to read it, read it
with guidance, annotate it into a durable note, and cross-check those notes
against the source with a draft-blind verifier.

Built on one principle: **orient, don't pre-digest.** A summarizer hands you the
conclusion and robs you of the read. This skill hands you the map and the
vocabulary, then gets out of the way so you form the verdict. (Honest caveat:
choosing what is "load-bearing" is itself a reading judgment, so the brief
presents its ranking as a reading aid, not a ruling.)

## Where it sits

| If you want | Use |
|-------------|-----|
| Depth on one paper (prep, read, annotate) | **read-paper** (this) |
| A verdict: pressure-test a claim or design | a critique panel (for example research-council) |
| Breadth: synthesis across many sources | a deep-research skill (for example hyperresearch) |

How it differs from public tools:
- **Summarizers** (Scholarcy, TLDRs) pre-digest; this orients.
- **Explain-at-level** (Explainpaper, SciSpace) explain but never check the
  explanation; this runs a best-effort falsity-check on every analogy.
- **Agentic RAG-QA** (PaperQA2) grounds answers over a corpus; this cross-checks
  its own annotation with a draft-blind verifier.
- **Guided critical readers** (InsightGUIDE) are deliberately opinionated; this is
  the neutral counterpart.

## Modes

| Mode | Trigger | Output |
|------|---------|--------|
| **PREP** | "prep me for this paper" | a pre-read brief (5 C's, central question, jargon, reading map); no spoilers |
| **READ** | "read this with me" | guided section by section; QALMRI lens; running notes |
| **ANNOTATE** | "annotate / write a note / summarize into a note" | a durable `.md` note (summary or full) plus a draft-blind cross-check |
| **CURRICULUM** | explicit only | a learning hub for a body of literature |

Cross-cutting: a **concept-aid** that builds an analogy or conceptualization and
runs a **best-effort falsity-check** against the source (mapping, holds, breaks,
net), so a stray analogy does not install a misconception.

## The two checks (what they do and do not claim)

- **Cross-check (notes).** After drafting, a **draft-blind verifier** (a sub-agent
  that reads the source without seeing the draft) re-extracts the same fields
  independently; the draft is diffed against it and every disagreement is
  reconciled at the source. This gates `status: read`. It delivers "internally
  consistent, traced to a source locus, blind-diff cross-checked." It is not a
  proof of truth, and it checks fidelity to the paper, not whether the paper is
  correct.
- **Falsity-check (analogies).** Best-effort: generate, check against the source,
  fence the leaks or discard. Not a proof.

Mini-glossary: **Keshav three-pass** is a standard reading method (skim, read,
reconstruct); its first pass uses the **5 C's** (Category, Context, Correctness,
Contributions, Clarity). **QALMRI** is a comprehension checklist (Question,
Alternatives, Logic, Method, Results, Inferences).

## Install

Copy `read-paper/` into `~/.claude/skills/` (user scope) or a project's
`.claude/skills/`. The core needs no dependencies. `verify_doi.py`,
`extract_text.py`, and `lint_frontmatter.py` use only the Python standard
library; Word/ODT/PPTX/HTML/text extraction works out of the box, and PDFs are
read natively (with figures) by the host Read tool. `convert_docx.sh` is an
optional higher-fidelity Word-to-markdown path that needs `pandoc`.

## Conventions (where notes land), default-first

Neutral by default, nothing hard-coded. The skill resolves a target from a
`CONVENTIONS (read-paper)` block in your project `CLAUDE.md` (or a
`.read-paper.yml`); if none exists it uses sane defaults and proceeds, and only
asks if you object. Example block:

```yaml
# CONVENTIONS (read-paper)
annotations_dir: references/annotations
raw_dir: references/raw
index_file: references/References.md
naming: "Author Year -- Short Title.md"
wikilinks: true
```

## Files

```
read-paper/
  SKILL.md            router: mode detection, conventions, persistence
  reading-method.md   Keshav 3-pass + QALMRI, the draft-blind cross-check, methods labels, hard rules
  templates.md        prep brief, annotation (full/summary), curriculum, index entry
  README.md           this file
  scripts/
    verify_doi.py        Crossref metadata verification (stdlib only)
    extract_text.py      robust text extraction: Word/ODT/PPTX/HTML/txt (stdlib); PDF/doc/rtf via fallback
    convert_docx.sh      optional higher-fidelity .docx to markdown (needs pandoc)
    lint_frontmatter.py  required-field / status check (stdlib only)
```

## Attribution

- Keshav, *How to Read a Paper*, ACM SIGCOMM CCR 2007 (three-pass + 5 C's).
- Brosowsky & Parshina, *Using the QALMRI Method*, 2017 (comprehension scaffold).
- The draft-blind cross-check follows the LLM-explanation-faithfulness literature:
  a same-model self-explanation can be plausible but unfaithful, so independence
  from the draft is what makes the check meaningful.

## License

MIT.
