---
name: read-paper
description: >
  Depth-on-one-paper companion: prepare to read it, read it with guidance,
  annotate it into a durable note, and cross-check those notes against the
  source with a draft-blind verifier. Four modes: PREP (a pre-read brief that
  orients without spoiling), READ (guided section by section), ANNOTATE (a
  two-tier durable note plus a draft-blind cross-check), and CURRICULUM (a
  learning hub for a body of literature, on explicit request only). Includes a
  cross-cutting concept-aid that builds analogies or conceptualizations and runs
  a best-effort falsity-check against the source. Core principle: ORIENT, DON'T
  PRE-DIGEST. Scaffold the reader's thinking rather than hand them a verdict.
  Outputs are persistent .md files written to a knowledge base whose location and
  conventions are resolved from the project (neutral by default, nothing
  hard-coded). MANDATORY TRIGGERS: "prep me for this paper", "prepare me to
  read", "read this paper with me", "walk me through this paper", "annotate this
  paper", "write a literature note", "make reading notes for", "summarize this
  paper into a note". STRONG TRIGGERS: "help me understand this paper", "what
  does this paper actually do", "analogize this concept", "I don't understand X
  in this paper", "build a reading curriculum for a topic". Do NOT trigger for:
  pressure-testing or critiquing a claim, or deciding what to pursue (that is
  research-council), broad multi-source synthesis across the literature (that is
  hyperresearch), or a simple factual lookup.
---

# Read-Paper

A focused companion for going deep on **one paper**: prepare to read it, read it
with guidance, turn it into a durable note, and make the note trustworthy by
cross-checking it against the source.

It rests on one principle:

> **Orient, don't pre-digest.** A summarizer hands you the conclusion and robs
> you of the read. This skill hands you the map and the vocabulary (the
> structure, the jargon, the central question, what to watch for), then gets out
> of the way so you form the verdict. PREP scaffolds thinking; it does not spoil.
> Honest caveat: deciding what is "load-bearing" or which findings are "key" is
> itself a reading judgment, so PREP presents its ranking as a reading aid, not a
> ruling on the work. A verdict on whether the paper is correct is a different
> job (that is research-council).

And one honest claim about its checks:

> **Every aid is traced to the source and cross-checked.** A finished note is
> re-derived by a **draft-blind verifier** (a separate pass that reads the source
> without seeing the draft) and diffed against the draft; analogies get a
> best-effort falsity-check. This delivers "internally consistent, traced to a
> source locus, and blind-diff cross-checked." It does not claim to prove truth,
> and it cannot verify the science itself, only fidelity to the paper.

## What this is NOT (so it stays in its lane)

- Not a critic. It reports faithfully what the paper says and how strongly; it
  does not rule on whether the paper is correct. Critique is research-council.
- Not a literature-survey engine. It goes deep on one paper, not wide.
- Standalone. It calls no other skill (it does spawn its own draft-blind
  verifier sub-agent during ANNOTATE).

## Mini-glossary (terms used below)

- **Keshav three-pass**: a standard reading method (skim, then read, then
  reconstruct). The first pass uses the **5 C's**: Category, Context,
  Correctness-to-check, Contributions, Clarity.
- **QALMRI**: a comprehension checklist (Question, Alternatives, Logic, Method,
  Results, Inferences) used to expose a paper's argument without judging it.

Full definitions live in `reading-method.md`.

## Egress note

Metadata is verified against **Crossref** (open API, bibliographic data only).
Full-text web fetch of a paper is opt-in, only when the user supplies a URL or
DOI and asks for it; a local PDF never leaves the machine. Never POST a paper's
contents anywhere.

---

## Step 0: Resolve CONVENTIONS (where notes go), default-first

Outputs are `.md` files. Resolve the target **without blocking the first run**:

1. **Project config.** Look for a `CONVENTIONS (read-paper)` block in the
   project's `CLAUDE.md`, or a `.read-paper.yml` at the project root. If present,
   use it. Fields: `annotations_dir`, `raw_dir`, `index_file`, `naming`
   (default `Author Year -- Short Title.md`), `frontmatter`, `status_values`,
   `wikilinks`.
2. **Neutral defaults, used immediately if no config exists** (do not stop to
   ask): `annotations_dir: ./papers/`, `index_file: ./papers/INDEX.md`, naming
   `Author Year -- Short Title.md`, standard markdown links, frontmatter
   `[title, date, authors, year, doi, venue, status]`.
3. **Ask only if the user objects to the default or the location is genuinely
   ambiguous.** One question maximum, then proceed and don't ask again this
   session.

Announce the resolved target in one line: `Notes -> <dir>, index <file>, links
<wiki|md>`, so the user can correct it.

---

## Step 1: Detect MODE and resolve the INPUT

**MODE** (pick from the request):

| Mode | Triggered by | Loads |
|------|-------------|-------|
| **PREP** | "prep/prepare me", "get me ready", "pre-read" | `templates.md` prep-brief |
| **READ** | "read with me", "walk/guide me through" | `reading-method.md` passes |
| **ANNOTATE** | "annotate", "write a note", "make notes", **"summarize into a note"** | `templates.md` + the draft-blind cross-check |
| **CURRICULUM** | explicit only: "build a curriculum/learning hub for a topic" | `templates.md` curriculum |

Disambiguation (Naive-reader fix): if a paper is named with no verb, default to
PREP. "summarize" or "notes" routes to ANNOTATE (a durable note), not PREP. PREP
never produces a verdict; ANNOTATE does record a faithful "core claim", which is
a report of the paper's own claim, not the skill's opinion.

The **concept-aid** (analogize or conceptualize, then falsity-check) is
cross-cutting; it can fire inside any mode on request.

**INPUT**, resolve the source:

| Source | Handling |
|--------|----------|
| Local **PDF** | **Read NATIVELY with the Read tool** (`pages` for long PDFs). This renders figures, equations, and tables visually, which the skill needs. Never substitute text-only extraction for the read; it loses the figures. |
| **Figures / images** | Read **natively** as images (Read tool), embedded in the PDF or standalone PNG/JPG. Figure values feed the cross-check. |
| **Word / ODT / PPTX / HTML / txt / md** | `scripts/extract_text.py <file>`, pure stdlib, no pandoc required; degrades gracefully on corrupt files. |
| **DOI** | Verify metadata via `scripts/verify_doi.py` (Crossref). Full text only if the user supplies it. |
| **arXiv / URL** | Metadata from the landing page; full-text fetch opt-in. |
| legacy **.doc / .rtf** | `scripts/extract_text.py` (uses antiword/unrtf/libreoffice if present), else resave as `.docx`. |

If no source is given, ask which paper.

---

## Step 2: Ingest and VERIFY metadata (before writing a citation)

1. Run `scripts/verify_doi.py` with the DOI (or `--title`) to pull authors,
   year, venue, and the canonical DOI from Crossref.
2. Reconcile against the source's own title page. If they disagree, trust the
   verified record and note the correction in provenance.
3. **Rule:** never fabricate or guess a DOI, author, or link. Unverifiable
   fields are marked `[unverified]`, never invented.

---

## Step 3: Run the mode

Load the matching section of `reading-method.md` and `templates.md`, then:

### PREP, a pre-read brief (orient, don't spoil)
Produce the brief in `templates.md`: the 5 C's, the central question,
prerequisite concepts and a jargon glossary, where it sits, author/lab/venue,
and a reading map (which sections to read closely vs skim, figure order, time).
No conclusions, no verdict. Default status `to-read`.

### READ, guided reading
Walk the paper with the three-pass method. Clarify figures, equations, and
methods; surface the claim-to-evidence structure with QALMRI; pose questions. Do
not judge the work. Keep running notes that can feed ANNOTATE.

### ANNOTATE, durable note plus draft-blind cross-check
1. Draft the note from the template, two tiers: short-form (`summary`) or full
   (`read`). Full includes **Methods, summarized** and **Methods, expanded**
   (with `[stated]/[inferred]/[unspecified]` labels).
2. Run the **draft-blind cross-check** (`reading-method.md`, section 3): spawn a
   verifier sub-agent that reads the source **without the draft**, re-extracts
   the same fields independently, then diff its extraction against the draft.
   Disagreements are the audit. Reconcile each at the source and revise.
3. A note earns `status: read` only after the blind cross-check has run and every
   disagreement is reconciled or logged as an open question. Record it in the
   provenance callout.
4. Write the file to `annotations_dir`; append a one-line entry to `index_file`
   if one is configured.

### CURRICULUM, learning hub (explicit request only)
Build the multi-paper hub in `templates.md`: objectives, a framework table, a
paper map, and a reading order with goals.

---

## Cross-cutting: the concept-aid (analogize / conceptualize, then falsity-check)

On request, or when offering help with a dense concept, use the concept-aid
protocol in `reading-method.md`. It produces a four-part object (mapping, holds,
breaks "don't import this", net) and runs a **best-effort falsity-check** against
the source: if a material falsehood can't be cheaply fenced, refine or discard
the analogy. This is a best-effort check by the same model, not a proof; for a
high-stakes analogy, route its "breaks" claims through the draft-blind verifier
too. For a researcher audience, offer aids, don't force them.

---

## Persistence rules ("repository info Claude looks back at")

- **Auto** (inside `annotations_dir`): the note and the index entry.
- **Prompt** (anything outside the notes dir): a pointer in a memory file, a
  cross-link into another project's `CLAUDE.md`, or promotion to a curriculum
  hub. Offer, don't do these silently.
- Every note is self-documenting: frontmatter `status` plus a provenance callout
  recording what was verified and what the blind cross-check changed.

---

## Operating rules

- **Resolve conventions, default-first.** Never block the first run; never
  scatter notes in the wrong place.
- **Verify before you cite.** Crossref metadata first; `[unverified]` over
  invented.
- **Orient, don't pre-digest.** PREP and READ never deliver a verdict.
- **Label inference.** In expanded methods, `[inferred]`/`[unspecified]` is never
  dressed as `[stated]`. The blind verifier re-tags methods independently, which
  is the real check on this.
- **Claim only what the check delivers.** A `read` note is "cross-checked against
  the source," not "verified true." No bare analogy, no `read` note without the
  blind cross-check.
- **Stay in lane.** Critique goes to research-council; breadth goes to
  hyperresearch; this skill is depth on one paper.
- **Researcher depth.** Pitch at an expert reader; skip definitional
  hand-holding unless asked.
