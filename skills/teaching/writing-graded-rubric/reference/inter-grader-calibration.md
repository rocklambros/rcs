# Inter-grader calibration

The pre-grading norming protocol that drops inter-grader disagreement from typical "1-2 bands per criterion" to "almost always agree."

## Why calibration matters

Even a tight rubric does not eliminate grader disagreement. Different graders bring different priors about what "proficient" looks like. A 30-minute calibration session up front prevents:

- Student appeals based on inter-grader inconsistency
- Re-grading costs (1 re-grade ≈ 3x the original grade time, in instructor effort)
- Erosion of student trust in the grading process

## The norming protocol

### Step 1: Pick 2-3 sample works

From a prior cohort, or from the first 2-3 submissions of the current cohort. Sample works should span the expected quality range — pick a strong one, a middle one, and a weak one, not three middles.

### Step 2: Each grader applies the rubric INDEPENDENTLY

No conferring. Each grader reads each sample work and assigns a band per criterion. Record the band assignments (per grader, per criterion, per work).

### Step 3: Compare

Build a matrix:

| Criterion | Sample 1 | Sample 2 | Sample 3 |
|---|---|---|---|
| Methodology | G1: Proficient · G2: Developing | G1: Proficient · G2: Proficient | G1: Advanced · G2: Proficient |

Identify disagreements: same work, same criterion, different band.

### Step 4: Discuss EACH disagreement

For each disagreement, both graders explain their reasoning. The conversation surfaces:

- **Vague descriptor:** the band descriptor's wording allowed different interpretations. Fix: tighten the descriptor.
- **Different prior:** the graders have different mental models of "proficient." Fix: agree on the prior; if needed, add evidence anchors to the descriptor.
- **Different attention:** one grader noticed an element the other missed. Fix: re-read together; agree on what is present in the work.

### Step 5: Re-norm

After discussion, both graders re-apply the rubric to the same samples. Disagreements should drop substantially (typical: 70-90% reduction).

If disagreement does NOT drop after norming, the rubric is genuinely too vague for the grader pool. Rewrite the descriptors and re-norm.

### Step 6: Lock the agreement

Document the agreed-upon interpretation in a one-paragraph "grader notes" section attached to the rubric. Future graders read the rubric AND the grader notes.

## Norming session length

| Pool size | Typical session length |
|---|---|
| 2 graders (instructor + 1 TA) | 30-45 minutes |
| 4-6 graders (course staff) | 60-90 minutes |
| 20+ peer graders | 90-120 minutes with structured small-group breakouts |

The session is not optional for peer graders. Peers without a norming session produce scores that are roughly noise. The norming session is the only thing that makes peer grades meaningful.

## During grading: ongoing recalibration

If, during actual grading, a grader encounters a submission that lands ambiguously on the rubric, the right move is NOT to grade it alone. Flag it for a brief 2-grader discussion. This:

- Catches rubric drift early (the rubric does not handle this case → fix the rubric or document a special case)
- Preserves consistency across the cohort
- Builds shared understanding for the rest of the cohort

This is more costly per-submission for ambiguous cases, but pays off in appeals avoided.

## Inter-grader disagreement metrics

For courses where grading quality matters as a research / accreditation question, compute:

- **Cohen's κ** (two graders, categorical bands): a κ above 0.7 is acceptable, above 0.8 is good, above 0.9 is excellent. Below 0.5 is a broken rubric.
- **Intraclass correlation (ICC)** for ordinal bands treated as numeric: ICC above 0.75 acceptable for high-stakes assessment.
- **Krippendorff's α** for multi-grader settings.

These metrics are overkill for routine grading but valuable when the assessment is part of accreditation review or external audit.

## When graders disagree EVEN AFTER norming

If two graders consistently disagree on a criterion after norming, the most likely cause is that the criterion is measuring two different things, and each grader is attending to a different one. The fix is to split the criterion.

Example: a criterion called "code quality" disagreed-on by two graders, where one weighted readability and the other weighted modularity. Split into "readability" and "modularity" as separate criteria; each is then well-defined.

## Anti-patterns

- **Skipping norming because "we agree on what good work looks like"** — the data does not support this assumption; norming surfaces gaps you did not know existed.
- **Norming by averaging band assignments rather than discussing disagreements** — averages hide the underlying interpretation gap, which will recur on the next batch.
- **Setting the rubric in stone after norming and refusing to update during grading** — calibration is iterative; if a real submission exposes a rubric gap, fix the rubric (and re-grade any prior submissions that turned on the gap).
- **Public norming sessions where grader hierarchies dominate** — junior graders defer to senior graders even when the senior is wrong. Use anonymous independent band assignment FIRST, then discuss; the order matters.
