# Reading method, checks, and rules

Load this in READ and ANNOTATE modes, and whenever the concept-aid fires. It
carries the methodology, the two checks, and the hard rules.

---

## 1. The reading spine: Keshav's three passes

Three increasing-effort passes (Keshav, *How to Read a Paper*, ACM SIGCOMM CCR
2007). They map onto the status ladder, so the skill's depth and the note's
`status` always agree:

| Pass | Effort | Goal | Maps to mode | Status |
|------|--------|------|--------------|--------|
| **1** | skim | Bird's-eye: get the shape, not the detail | PREP | `to-read`, then `summary` |
| **2** | focused read | Grasp the content; follow the argument; ignore fine proofs | READ | `summary`, then `read` |
| **3** | deep | Reconstruct: could you re-implement or re-derive it? | ANNOTATE (Methods-expanded) + cross-check | `read` |

The pass, not a clock, is the unit of effort. Keshav attaches rough durations for a first-time reader, but an expert is much faster and often will not need pass 3 in full, so scale to your own speed.

**Pass-1 checklist, the 5 C's** (use these to build the PREP brief):
- **Category**: what kind of paper (method, discovery, theory, benchmark, review)?
- **Context**: what prior work does it sit against; what lineage?
- **Correctness**: what assumptions should the reader plan to check (not yet judge)?
- **Contributions**: what does it claim is new?
- **Clarity**: is it well-written; where will the reader struggle?

## 2. The comprehension lens: QALMRI

When reading (pass 2) and when filling "key findings" and "open questions", run
the paper through QALMRI (Brosowsky & Parshina, 2017). It forces the argument's
skeleton into view without judging it:

| Letter | Question to answer from the text |
|--------|----------------------------------|
| **Q**, Question | What problem is the paper actually answering? |
| **A**, Alternatives | What competing explanations or approaches existed? |
| **L**, Logic | Why does answering Q require this method? |
| **M**, Method | What did they concretely do? |
| **R**, Results | What did they find? |
| **I**, Inferences | What do *they* conclude, and what is the gap between R and I? |

The **A** and **I** letters feed the note's "open questions" (what else could
explain this; where the conclusion outruns the evidence), phrased as questions,
never as the skill's verdict.

---

## 3. The draft-blind cross-check (ANNOTATE)

After a note is drafted, check it by re-deriving the facts from the source with a
verifier that **cannot see the draft**. This makes the audit's errors independent
of the draft's errors, the property a same-context re-read lacks (same weights
plus the draft in context reproduce the same mistakes).

**Why blind, not a re-read.** A same-model re-read with the draft in context
catches transcription slips but ratifies confident fabrications and directional
misreadings, because it regenerates them from the same prior. A verifier that
never sees the draft cannot anchor on it, so its agreement is real evidence and
its disagreement is a real flag.

**Procedure:**
1. Draft the note.
2. **Spawn a verifier sub-agent** (Agent tool, `general-purpose`). Give it ONLY
   the source (the PDF to read natively, or the extracted text, plus any figure
   image paths) and a field list to extract independently. Do NOT include the
   draft. Ask it to return:
   - citation metadata (it may run `scripts/verify_doi.py`),
   - the central claim, in its own words,
   - the key findings, ranked by the paper's emphasis,
   - every Methods item it can find, each tagged `stated`/`inferred`/`unspecified` by it,
   - the specific numeric values it sees (parameters, dataset sizes, headline results),
   - figure-derived values, if figures were provided.
3. **Diff** the verifier's extraction against the draft. Classify each disagreement:
   - *value mismatch*: a number or label differs,
   - *draft-only*: a claim in the draft the verifier could not find in the source (a possible fabrication),
   - *source-only*: a fact the verifier found that the draft omits (a gap),
   - *emphasis mismatch*: a different ranking of what is load-bearing,
   - *label mismatch*: `stated` vs `inferred` vs `unspecified` differs.
4. **Reconcile at the source.** For each disagreement, open the actual locus and
   decide: correct the draft, or keep it and cite the locus if the draft was
   right and the verifier missed it.
5. **Gate.** `status: read` requires the blind cross-check has run and every
   disagreement is reconciled or logged as an open question. Otherwise the note
   stays `summary`.
6. **Provenance log**, for example:
   > Blind cross-check: verifier run on the source (draft hidden). 4
   > disagreements: 1 value corrected, 2 gaps added, 1 emphasis re-ranked, 0
   > fabrications. Reconciled to source.

**Cost:** one verifier pass plus targeted reconciliation, cheaper than repeated
full re-reads. Default it on for `read` notes; it is the gate, not an optional add.

**Honest scope.** This checks fidelity to the paper (did the note capture what
the paper says, accurately and completely). It does NOT check whether the paper
is correct. It reduces, it does not eliminate, fabrication and misreading: the
verifier is still a model, but its errors are now independent of the draft's.

**Fallback when sub-agents are unavailable.** If the runtime cannot spawn a
verifier, do a same-context re-read, but label the result honestly as a
"self-consistency pass", keep `status` at `summary`, and state that the blind
cross-check was not run. Do not call a self-consistency pass "verified".

---

## 4. The concept-aid (analogize / conceptualize, then falsity-check)

Triggered on request ("analogize this", "I don't get X", "conceptualize this") or
offered when a concept is dense. An unverified analogy is worse than none: it can
install a confident misconception (the documented LLM failure mode, a plausible
but unfaithful explanation that breeds false confidence). So every aid ships with
its own limits shown.

**Two registers:**
- **Conceptualize**: break it down (first principles, components, a minimal
  worked example, plain restatement). Guards against the "lie-to-children" trap
  where simplification quietly becomes false.
- **Analogize**: map the concept to a familiar source domain. Guards against
  leaked properties, traits of the source the reader must not import.

**Output object (always four parts):**

| Part | Content |
|------|---------|
| **Mapping** | "X is like Y because..." the correspondence |
| **Holds** | the inferences you may safely draw from it |
| **Breaks** | the source properties you must NOT import, each leak named, with the correction back to ground truth |
| **Net** | "use it for intuition about A and B; for property P, drop the analogy and use the real mechanism" |

**Best-effort falsity-check:** generate the aid, then check it against the source
concept; name where the mapping diverges from truth under *Breaks*; if a material
falsehood can't be cheaply fenced, refine or discard and try another domain. This
is a best-effort check by the same model, **not a proof**. For a high-stakes
analogy, route its *Breaks* claims through the draft-blind verifier (section 3).

A checked aid may be persisted to the note's jargon glossary as
`analogy (checked): valid for A, breaks at B`. Honest framing: an aid is
scaffolding with limits shown, not "the truth".

---

## 5. Methods, summarized vs expanded

| Section | In `summary` note | In `read` note | Pass |
|---------|:-:|:-:|:-:|
| **Methods, summarized** | yes | yes | 2 |
| **Methods, expanded** | no | yes | 3 |

- **Summarized**: approach in plain terms, key technique(s) and why chosen,
  inputs to process to outputs, how they validated. Readable in 30 seconds.
- **Expanded**: reproduction-grade. Step-by-step protocol, parameters and
  thresholds, tools and versions, datasets (size and source), equations and
  statistics with definitions, controls, replicates, seeds, splits, and
  reproducibility gap-flags.

**Label every expanded item.** Methods is the highest hallucination zone (it is
tempting to fill in "standard" parameters the paper never stated):

| Label | Meaning |
|-------|---------|
| `[stated]` | paper or SI explicitly says it |
| `[inferred]` | standard practice or derivable, NOT the paper's word |
| `[unspecified]` | the paper omits it, a reproducibility gap |

The labels are a discipline, not a guarantee; the real check is the blind
verifier (section 3), which re-tags every Methods item independently and flags
any `label mismatch`. Code or command snippets only when the paper or SI provides
them or it is a faithful transcription, never fabricated.

---

## 6. Input handling

| Source | How |
|--------|-----|
| Local PDF | **Read NATIVELY with the Read tool**: renders figures, equations, tables visually (required; figure-reading is first-class). `pages` for long PDFs. Text-only `extract_text.py`/pdftotext is a search dump, never the read |
| Figures / images | Read **natively** as images (Read tool), embedded or standalone PNG/JPG. Figure values feed the cross-check; never review blind from text when figures exist |
| Word / ODT / PPTX / HTML / text | `scripts/extract_text.py <file>`, stdlib-only, no pandoc; graceful on corrupt files |
| DOI | `scripts/verify_doi.py <doi>` for Crossref metadata; full text only if supplied |
| arXiv / URL | landing-page metadata; full-text fetch opt-in (egress) |
| legacy .doc / .rtf | `scripts/extract_text.py` (external tool if present) or resave as .docx |

---

## 7. Anti-patterns and hard rules (read before every run)

Each is a real failure mode this skill exists to prevent.

- **Never fabricate a citation field.** No invented DOI, author, year, or link.
  Unverifiable goes to `[unverified]`, never a guess. Crossref-verify; reconcile
  against the title page; note corrections in provenance.
- **`[inferred]` is never dressed as `[stated]`.** A reader trusts the note to
  reproduce the paper; do not let them inherit a parameter the paper never gave.
- **Claim only what the check delivers.** A `read` note is "cross-checked against
  the source" (draft-blind verifier run and reconciled), not "verified true". An
  analogy gets a "best-effort falsity-check", not a proof. Do not write "no
  falsehood" or "verified".
- **No `read` note without the blind cross-check.** If it did not run, the note is
  `summary`, and say so.
- **No bare analogy.** An analogy without its *Breaks* fence is a misconception
  generator. Ship the four-part object or discard.
- **PREP and READ never deliver a verdict.** Orienting the reader is not judging
  the paper. Surface claim-to-evidence and questions; leave the verdict to the
  reader or a critique skill. Be honest that selecting "key findings" is itself a
  reading judgment, presented as an aid.
- **Don't summarize a PDF you only skimmed.** A `read` note asserts a full pass
  happened and was cross-checked. If you only saw the abstract, it is
  `to-read`/`summary`.

---

## Attribution

- Keshav, S. (2007). *How to Read a Paper.* ACM SIGCOMM CCR 37(3), 83-84.
  DOI 10.1145/1273445.1273458.
- Brosowsky, N. P., & Parshina, O. (2017). *Using the QALMRI Method to Scaffold
  Reading of Primary Sources.* In *How We Teach Now* (APS).
- The draft-blind cross-check and the analogy falsity-check follow the
  LLM-explanation-faithfulness literature (for example arXiv 2504.14150): a
  same-model self-explanation can be plausible but unfaithful, so independence
  from the draft is what makes the check meaningful.
