# Artifact templates

The exact `.md` shapes the skill writes. All are **neutral**: placeholders, no
domain content. Replace the angle-bracket fields; drop sections that don't apply.
Internal links use `[[wikilinks]]` or standard markdown per the resolved
CONVENTIONS.

---

## Frontmatter (all notes)

```yaml
---
title: <Author Year -- Short Title>
date: <YYYY-MM-DD>
tags: [paper, <topic>]
authors: <Last F, Last F, ...>
year: <YYYY>
doi: <https://doi.org/...  or  [unverified]>
venue: <journal / conference>
status: <to-read | summary | read>
---
```

`status` ladder: **to-read** (PREP only), then **summary** (metadata verified,
short note, no deep read), then **read** (full read plus the draft-blind
cross-check has run and reconciled).

---

## A. Pre-read brief  (PREP, `status: to-read`)

> Orient, don't spoil. No conclusions, no verdict.

```markdown
# Pre-read: <Author Year -- Short Title>

> [!info] Brief, not a summary. This gets you to the starting line; the verdict
> is yours to form while reading. Any ranking below is a reading aid, not a
> ruling on the work.

## The 5 C's (pass 1)
- **Category:** <method / discovery / theory / benchmark / review>
- **Context:** <prior work it sits against; lineage>
- **Correctness to check:** <assumptions to keep an eye on while reading, not yet judged>
- **Contributions claimed:** <what it says is new>
- **Clarity:** <how hard a read; where it will be dense>

## The central question
<the one problem the paper sets out to answer, in a sentence>

## Prerequisites and jargon (pre-taught)
| Term / concept | What you need to know going in |
|----------------|--------------------------------|
| <term> | <plain, verified explanation; link a concept-aid if dense> |

## Where it sits
<neighbours and what to read alongside; links to related notes you already have>

## Author / lab / venue
<who, which group, where published; context only>

## Reading map
| Section | Read how | Why |
|---------|----------|-----|
| Abstract | close | frame the contributions |
| <Methods> | close | <the spine you'll reconstruct later> |
| <Results Xn> | close / skim | <...> |
| <...> | skim | <...> |

**Figures first:** <order to look at figures and tables>
**Estimated effort:** <skim vs focused read vs deep; scale to your own pace>

## Questions to hold while reading
- <open question 1>
- <open question 2>
```

---

## B. Annotation, FULL  (ANNOTATE, `status: read`)

Genericized from a literature-note pattern; the comprehension scaffold is QALMRI.

```markdown
# <Author et al. Year: Full Title>

> [!note] Provenance
> <what was verified vs knowledge-based>. Citation Crossref-verified <date>.
> Blind cross-check: <verifier run, draft hidden; N disagreements; what changed>.

## Citation
- Authors: <full list>
- Year, Venue, DOI
- <affiliations, funding, disclosed conflicts, if relevant>

## Core claim
<the paper's central claim in 2 to 4 sentences (QALMRI: Question plus Inference); a faithful report of the paper's claim, not the skill's opinion>

## Key findings
<bulleted; ordered by the paper's own emphasis (confirmed against the blind verifier)>
- <finding, with the evidence that supports it (QALMRI: Results)>

## Methods, summarized
<approach in plain terms, key technique(s) and why, inputs to process to outputs, how validated. 30-second read.>

## Methods, expanded
<reproduction-grade. Label every item.>
- Protocol: <step> `[stated]`
- Parameters: <name = value> `[stated]` / <x> `[inferred]` / <y> `[unspecified]`
- Tools and versions, datasets (size/source), equations and statistics with definitions
- Controls, replicates, seeds, splits
- **Reproducibility gaps:** <what the paper does not specify> `[unspecified]`

## Reading guide
**Read in this order:** <1 ... n, with why>
**Jargon to know:**
- **<term>:** <verified definition>; `analogy (checked): valid for A, breaks at B` (optional)

## Open questions
<QALMRI: Alternatives plus the R-to-I gap; phrased as questions, not verdicts>
- <what else could explain X?>
- <where does the conclusion outrun the evidence?>

## Relevance   <!-- optional; fill ONLY from supplied context, never auto-opinion -->
<how it bears on the reader's stated work; omit if no context given>

## Key takeaway
<one durable sentence>

## Related
- <links to neighbouring notes>
```

---

## C. Annotation, SUMMARY  (ANNOTATE, `status: summary`)

Short form: metadata verified, no deep read yet (and no blind cross-check yet).

```markdown
# <Author et al. Year: Title>

> [!note] Provenance
> Metadata Crossref-verified <date>; interpretive summary pending a full read and
> the blind cross-check.

## Citation
<authors, year, venue, DOI>

## Core claim
<2 to 3 sentences>

## Key findings
<3 to 6 bullets>

## Methods, summarized
<30-second version>

## Key takeaway
<one sentence>

## Related
- <links>
```

---

## D. Curriculum / Learning Hub  (CURRICULUM, explicit request only)

For preparing a reader to enter a *body* of literature.

```markdown
---
title: <Topic> -- Learning Hub
date: <YYYY-MM-DD>
tags: [learning, <topic>]
status: active
---

# <Topic>: Learning Hub

A self-contained path from "<entry state>" to "<target competence>" in about <N>
sittings.

> [!important] The one sentence to leave with
> <the single load-bearing idea>

## What you'll know at the end
1. <objective> ...

## The framework to internalize first
<a table or map that organizes the whole topic>

## Reading order
| # | Paper | Goal | Self-check question |
|---|-------|------|--------------------|
| 1 | <Author Year> | <what this one establishes> | <a question you should be able to answer> |

Each paper gets its own annotation (template B or C) as you work through it.
```

---

## E. Index entry  (appended to `index_file`, if configured)

One line per paper, grouped by theme, with a descriptor:

```markdown
- [[<path to note>|<Author Year -- Title>]]: <one-line descriptor of the contribution>
```
