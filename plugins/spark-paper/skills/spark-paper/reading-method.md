# Method

Reference for the pipeline in SKILL.md: how to read, how to label, who reads, how to check.

## 1. Read: three passes, one lens

| Pass | Mode | Goal |
|------|------|------|
| 1. Skim | PREP | Shape of the paper. The 5 C's: Category, Context, Correctness to check, Contributions claimed, Clarity. |
| 2. Read | READ | Follow the argument with QALMRI. |
| 3. Reconstruct | ANNOTATE | Could the work be re-derived? Expanded methods, figure values. |

The 5 C's (Keshav's first-pass checklist):

- **Category:** what kind of paper it is: method, discovery, theory, benchmark, or review.
- **Context:** the prior work it sits against, and its lineage.
- **Correctness:** the assumptions to check while reading. Listed, not yet judged.
- **Contributions:** what the paper claims is new.
- **Clarity:** how well it is written, and where it will be hard going.

QALMRI: Question, Alternatives, Logic, Method, Results, Inferences. Open questions come from A (what else could explain it) and from the gap between R and I. They are phrased as questions, never verdicts.

Sources: Keshav (2007), How to Read a Paper, ACM SIGCOMM CCR 37(3):83-84, doi 10.1145/1273445.1273458. Brosowsky and Parshina (2017), Using the QALMRI Method to Scaffold Reading of Primary Sources.

## 2. Labels (every claim carries one)

| Where | Label | Meaning |
|-------|-------|---------|
| Finding | MEASURED BY THE AUTHORS | Obtained in this paper |
| Finding | REPORTED FROM CITED WORK | Quoted from another paper; that paper is the evidence |
| Finding | AUTHORS' INTERPRETATION | What the authors conclude |
| Finding | BACKGROUND STATEMENT | Context with no measurement or specific citation |
| Method item | stated | The paper or its supplement says it |
| Method item | inferred | Standard practice or derivable, not the paper's word |
| Method item | unspecified | The paper omits it (a reproducibility gap) |

Status ladder: `to-read` (PREP only), `summary` (metadata verified, short note, no cross-check), `read` (full read plus a completed blind cross-check).

## 3. Agents (who reads the source)

Optional helpers that read the paper. Each gets only what it needs, returns a fixed JSON shape, and is never shown a draft.

| Agent | When | Input | Returns |
|-------|------|-------|---------|
| Verifier | ANNOTATE `read` (required) | The source only | Extraction JSON (below) |
| Section reader | Long papers (about 15+ pages) or many figures | The source and one page range | The same JSON, limited to its range |
| Concept checker | A high-stakes analogy | The concept and its source locus | Source facts the analogy violates |

**Brief (send verbatim, fill the brackets):**

> Read [source path] natively (PDF with the Read tool[, pages X-Y]). Do not look for or use any existing notes about this paper. Return only JSON in the schema below. Cite where (page, section, or figure) for every item. Tag each finding's producer and each method item's label. If something is not in the source, leave it out; do not infer.

**Schema:**

```json
{
  "citation": {"title": "", "authors": "", "year": "", "venue": "", "doi": ""},
  "core_claim": "",
  "findings": [{"finding": "", "where": "", "producer": "", "number": ""}],
  "methods": [{"item": "", "detail": "", "label": "", "where": ""}],
  "figures": [{"ref": "", "shows": "", "values": ""}]
}
```

Section readers: merge by concatenating, then dedupe on `where` plus meaning. Agent output is evidence, not truth; disagreements are settled at the source by the main reader. No sub-agents available: run a same-context re-read, call it a "self-consistency pass", and keep status `summary`.

## 4. Blind cross-check (gates `read`)

1. Draft the note and the record.
2. Run the Verifier (section 3) on the source alone. Limit its extraction to the chosen sections (it always returns the citation and core claim), which also makes the check cheaper.
3. Diff its JSON against the record. Classify each difference: *value mismatch*, *draft-only* (possible fabrication), *source-only* (gap), *emphasis mismatch*, *label mismatch* (method label or producer label).
4. Reconcile at the source: correct the draft, or keep it and cite the locus. Log each difference in `crosscheck_log` (field, draft, verifier, class, resolution, locus).
5. Set `cross_check` (done, date, disagreements). `read` is allowed only now.

Why blind: a re-read with the draft in view confirms its own confident errors; a verifier that never saw the draft errs independently, so agreement is evidence and disagreement is a flag. This checks fidelity to the paper, not whether the paper is right. Say "cross-checked against the source", never "verified true".

## 5. Concept-aid (on request, any mode)

Two registers: *conceptualize* (first principles, a minimal worked example) and *analogize* (map to a familiar domain). Output four parts, always:

| Part | Content |
|------|---------|
| Mapping | X is like Y because... |
| Holds | Inferences that are safe to draw |
| Breaks | Source properties not to import, each corrected back to the real mechanism |
| Net | Use it for A and B; for P, use the real mechanism |

Run a best-effort falsity check against the source; if a material falsehood cannot be fenced, refine or discard. An analogy without Breaks is not shipped. A checked aid may be stored in the Terms sheet as `analogy` and `breaks`.
