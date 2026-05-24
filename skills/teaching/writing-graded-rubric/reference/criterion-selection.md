# Selecting 4-6 criteria mapped to learning objectives

The criterion list is the rubric's backbone. Too many criteria → graders cannot hold them in working memory. Too few → rubric collapses to a holistic score.

## The 4-6 target

| Criterion count | Symptom |
|---|---|
| 1-2 | Rubric is essentially a holistic score; "did I like this work overall" leaks in |
| 3 | Workable for low-stakes assignments; risky for capstones |
| 4-6 | Sweet spot — graders can hold the criteria in working memory while reading |
| 7-8 | Graders cluster criteria mentally and grade by gestalt; the rubric becomes post-hoc documentation |
| 9+ | Rubric is broken; either split the assignment into two parts or collapse overlapping criteria |

## Heuristics for criterion selection

### 1. Each criterion must map to at least one learning objective

A criterion that does not measure a learning objective is scope creep. Drop it.

A learning objective that no criterion measures is uncovered. Add a criterion or restructure the assignment.

### 2. No two criteria should measure the same underlying skill

"Methodology" and "method justification" are not two criteria; they are one (methodology, with justification being part of what makes it proficient or advanced).

"Writing quality" and "argument clarity" are not two criteria; collapse or split along orthogonal axes (e.g., "argument structure" vs. "language mechanics").

### 3. Prefer criteria that are observable in the artifact itself

"Effort" is not observable in the final artifact. "Reproducibility" is. Pick the observable cousin.

### 4. Bias toward criteria that differ across submissions

A criterion where all submissions land in the same band is useless — it does not discriminate. Pre-test by writing three hypothetical submissions and checking that they spread across bands on this criterion. If they all cluster, drop it.

### 5. Cover both content and form

A typical rubric covers:

- **Content criteria** (the substance: methodology, analysis, argument, correctness)
- **Form criteria** (the artifact: writing quality, reproducibility, structure, presentation)

A rubric that is all-content misses form failures; a rubric that is all-form misses content failures. Aim for ~70% content / ~30% form.

## Worked example: applied stats final project

**Learning objectives:**

1. Frame a research question
2. Choose appropriate statistical methods
3. Check assumptions
4. Report effect sizes with uncertainty
5. Document reproducibly

**Candidate criteria (15 brainstormed, narrowed to 5):**

- ❌ "Effort" — not observable in artifact, drop
- ❌ "Length" — not a quality measure, drop
- ❌ "Originality" — too subjective, drop without operationalization
- ❌ "Use of citations" — sub-element of methodology / framing, fold in
- ❌ "Statistical correctness" — overlaps with methodology + assumption-checking, redundant
- ❌ "Writing quality" — fold into framing for content; for form, see reproducibility
- ❌ "Domain knowledge demonstrated" — sub-element of framing, fold in
- ❌ "Clarity of presentation" — fold into framing
- ❌ "Visual aids" — only applies to oral defense, drop for written
- ❌ "Conclusion strength" — sub-element of framing + effect-size discussion, fold in
- ❌ "Peer review quality" — only applies if peer review is part of assignment, drop
- ✅ "Problem framing" → objective 1
- ✅ "Methodology choice" → objective 2
- ✅ "Assumption checking" → objective 3
- ✅ "Effect-size reporting" → objective 4
- ✅ "Reproducibility" → objective 5

Final: 5 criteria, each mapping to exactly one objective, all observable in the submitted artifact.

## When the learning objectives outnumber the criterion budget

If you have 8 learning objectives and a 4-6 criterion budget, some objectives must combine into one criterion.

Combine when:
- Two objectives measure the same underlying skill at different granularities
- Two objectives are typically demonstrated together in the same artifact section
- Two objectives are taught together and assessed together

Do NOT combine when:
- Two objectives are independent enough that a student could be strong on one and weak on the other
- The combination obscures which objective the score reflects (defeats criterion-referenced grading)

If combination would lose too much information, the alternative is to split the assignment into two parts, each with its own rubric.

## Weights: how to allocate

The default is uniform weights. Allocate differently when:

- A criterion is core to the assessment's purpose (weight it higher)
- A criterion is supporting (weight it lower)
- A learning objective is a course-wide priority (weight it higher)

Document the rationale per weight. "Methodology weighted 25% because the course emphasizes method selection" is defensible. Uniform-because-default is also fine when the criteria are genuinely equal in importance — but state that explicitly.

Common allocations:

| Assessment type | Typical weight pattern |
|---|---|
| Methods-heavy stats project | Methodology 25% + assumption-checking 20% + effect-size 20% + reproducibility 20% + framing 15% |
| Writing-heavy essay | Argument 30% + evidence 25% + structure 20% + language 15% + citation 10% |
| Code-heavy implementation | Correctness 35% + code quality 25% + testing 20% + reproducibility 20% |
| Capstone (everything matters equally) | Uniform across 4-5 criteria |
