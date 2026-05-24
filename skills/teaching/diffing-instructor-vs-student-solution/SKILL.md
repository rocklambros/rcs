---
name: diffing-instructor-vs-student-solution
description: >
  Produces a side-by-side diff between an instructor's reference solution
  and a student's attempt, then writes formative feedback that distinguishes
  (a) the student got the right answer via wrong reasoning, (b) the student
  got the wrong answer via reasoning that was right up to a single
  identifiable misstep, (c) the student took a legitimate alternate path
  that arrives at the same answer, and (d) the student made an error
  uncorrelated with the surrounding reasoning (transcription, arithmetic,
  off-by-one). Triggers when a TA or instructor is grading a multi-step
  pset attempt, when a student submits work for review, or when an
  automated grader returned a wrong-answer verdict and the question is
  WHY. Refuses to engage when no reference solution exists (the diff has
  no anchor), refuses to give a binary pass / fail without naming the
  category, and refuses to mark a legitimate alternate path as wrong just
  because it differs from the reference.
version: 0.1.0
status: shipped
track: teaching
audience:
  - instructor
  - ta
  - stats-student
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
last-updated: 2026-05-23
---

# Diffing Instructor vs. Student Solution

## When to use

Trigger this skill when:

- A TA or instructor is grading a multi-step problem-set attempt and wants formative feedback (not just a numerical score)
- A student submits work asking *"where did I go wrong?"* and a reference solution exists to compare against
- An automated grader returned wrong-answer but the answer-only verdict is not actionable for the student
- A student got the right final answer but the instructor suspects the reasoning was wrong (right-for-wrong-reason class)
- A student got the wrong final answer but the reasoning looks mostly sound (locate-the-single-misstep class)
- An instructor wants to spot legitimate alternate solution paths that the answer key did not anticipate
- A code submission diverges from the reference implementation and the question is whether the divergence is correct or buggy

## When NOT to use

Skip this skill and hand off when:

- No reference solution exists — the diff has no anchor; in that case, use `teaching/writing-pset-walkthrough` to first author a reference, then return
- The submission is open-ended (essay, research proposal, design doc) where there is no single canonical solution to diff against — use criterion-referenced rubric scoring instead (`teaching/writing-graded-rubric`)
- The task is a binary correctness check on a one-line answer where formative feedback is overkill (the answer is right or wrong; no diff needed)
- The user wants a pure conceptual explanation, not a diff (`teaching/explaining-statistical-concept`)
- The user wants assessment summary statistics across an entire class cohort (different problem — class-wide grade analysis, not per-student diff)
- The student attempt is essentially blank or one line — there is nothing meaningful to diff; in that case, walk the reference solution as a tutorial

## Quick start

User: *"Here's the reference solution and a student attempt for our paired-t-test pset problem. Diff them and give the student formative feedback."*

Response: produce a step-by-step side-by-side comparison. At each step, classify into one of four categories: (A) right-answer-wrong-reasoning, (B) wrong-answer-right-reasoning-with-one-misstep, (C) legitimate-alternate-path, (D) uncorrelated-error (transcription / arithmetic / off-by-one). Write the formative feedback in the student's voice, naming the principle that was missed or applied incorrectly, NOT just the symptom.

```markdown
## Per-step diff

| Step | Reference | Student | Category | Feedback |
|---|---|---|---|---|
| 1. Identify design | Paired (same patients before/after) | Two-sample t-test | (B) wrong-reasoning at the first decision; everything downstream follows from this | "You treated 'before' and 'after' as two independent groups. Look again at the data: each row is the same patient measured twice. That makes it paired." |
| 2. Assumption check | Shapiro on differences, p = 0.018 | Shapiro on each column separately, p = 0.41 / p = 0.23 | (B) wrong-reasoning, propagation from step 1 | "Because the design is paired, the assumption check runs on the differences (after - before), not on each column. The differences are the new data object." |
| 3. Test choice | Wilcoxon signed-rank | Pooled two-sample t-test | Cascade from step 1 | "Once step 1 is fixed (paired), and step 2 finds non-Normal differences, the correct test is Wilcoxon signed-rank, not paired t." |
```

See `reference/category-definitions.md` for the four-category taxonomy with worked examples per category, `reference/feedback-voice.md` for the rules on writing student-facing feedback that names principles (not symptoms), and `reference/alternate-path-recognition.md` for the heuristics to spot a legitimate alternate path vs. a wrong path that happens to arrive at the same answer.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `reference_solution` | markdown / code / notebook | yes | — | The instructor's canonical solution. The skill refuses to engage without one. |
| `student_attempt` | markdown / code / notebook | yes | — | The student's work. If empty or near-empty (≤ 10% of reference length), the skill recommends walking the reference as a tutorial instead. |
| `problem_text` | string | yes | — | The original question. Needed to interpret what "correct" means and to recognize legitimate alternate paths. |
| `audience_tier` | enum | yes | — | `high-school` \| `undergrad-intro` \| `undergrad-advanced` \| `grad` \| `practitioner`. Drives feedback vocabulary; matches `teaching/writing-pset-walkthrough` tier definitions. |
| `grading_mode` | enum | no | `formative` | `formative` (feedback-first, score-secondary) \| `summative` (score-first, feedback-secondary) \| `diagnostic` (no score, only category breakdown for course-wide pattern analysis). |
| `allow_alternate_paths` | bool | no | `true` | If `true`, the skill actively looks for category (C) (legitimate alternate path) and marks it as correct. If `false`, only the reference solution path is accepted (use sparingly — usually for assessments where the path IS the thing being tested). |
| `partial_credit_policy` | enum | no | `cascade-aware` | `cascade-aware` (a misstep at step N reduces credit for downstream steps proportionally, since the student cannot recover without authority info) \| `independent-steps` (each step graded in isolation, ignoring earlier missteps). |

## Workflow

```
Diff-and-feedback progress:
- [ ] 0. Confirm scope: reference solution exists AND student attempt has meaningful content; if not, hand off
- [ ] 1. Decompose both solutions into matching steps; align by step number where the structure is parallel
- [ ] 2. Per step, compare and classify into one of (A) (B) (C) (D)
- [ ] 3. Recognize cascade: a misstep at step N often propagates; mark downstream steps as "cascade from N" not as fresh errors
- [ ] 4. Detect legitimate alternate paths: does the student's path arrive at the same answer via a different valid principle?
- [ ] 5. Write per-step feedback in student-facing voice, naming the PRINCIPLE not just the symptom
- [ ] 6. Compute partial credit per the partial_credit_policy
- [ ] 7. Summary: name the top 1-2 conceptual gaps + the top 1-2 mechanical errors
- [ ] 8. Suggest next-action: which pset section / concept / pre-req should the student revisit before the next problem
```

### The four categories — definitions

- **(A) Right answer, wrong reasoning** — the student arrives at the same final answer but via a method that does not generalize (often coincidence on a friendly dataset). MUST be flagged even though the answer is "right." The next variation of the problem will expose the wrong reasoning.

- **(B) Wrong answer, right reasoning with one identifiable misstep** — the student's reasoning is correct up to a specific identifiable step where one wrong decision was made; everything downstream follows from that decision. Highest-value feedback opportunity: name the single decision point.

- **(C) Legitimate alternate path** — the student arrives at the correct answer via a different valid method than the reference. Should be marked CORRECT, with a note that the reference uses a different method. If the alternate is more elegant, instructors may consider adding it to next year's answer key.

- **(D) Uncorrelated error** — transcription, arithmetic, off-by-one, label swap. Independent of the student's conceptual understanding. Flag separately from (A) / (B) so the student does not "study harder" for what is a mechanical mistake.

### Step 3: Cascade recognition

A category-(B) misstep at step 1 of a multi-step problem usually propagates. Steps 2, 3, 4 are "wrong" only because they correctly followed from the wrong step-1 decision. Mark them as `cascade from step 1`, not as fresh errors. The student fixes step 1 and re-runs; the cascade resolves.

If you mark every downstream step as an independent error, the student:

1. Sees five red marks instead of one
2. Cannot tell that fixing one decision fixes everything
3. Believes they made five conceptual errors when they made one
4. Loses confidence disproportionately to the actual gap

Cascade recognition is the single largest empathy gain in grading.

### Step 4: Alternate-path recognition

A path is legitimately alternate if:

1. It arrives at the SAME final answer (within rounding tolerance), AND
2. Each step uses a valid principle (named, defensible — not coincidence), AND
3. The path generalizes to known variations of the problem (test by mentally substituting a different α / different data shape / different sample size)

If any of those three fails, the path is NOT a legitimate alternate — it is a wrong path that happens to arrive at the right answer (category A) or wrong answer (category B).

Common legitimate alternates:

- Bayesian path arriving at the same numerical answer as the frequentist reference
- Top-down memoization arriving at the same DP answer as bottom-up tabulation
- Closed-form solution arriving at the same answer as an iterative algorithm
- Algebraic manipulation arriving at the same answer as a numerical method

### Step 5: Feedback voice

Per-step feedback to the student names the PRINCIPLE, not just the symptom.

- ❌ Symptom-only: *"You used the wrong test."*
- ✅ Principle-named: *"You ran a two-sample t-test because the data has two columns. For paired data — same subject measured twice — the test family is paired, not two-sample. The principle: design determines the test family before any numbers are computed."*

Reading the feedback should leave the student knowing the GENERAL rule, not just the specific correction for this problem. Otherwise the student "fixes" the surface error and walks into the same error on the next pset.

### Step 7: Conceptual gaps vs. mechanical errors — separate them

Conclude with two named lists:

- **Top 1-2 conceptual gaps** — these are the things to study before the next pset
- **Top 1-2 mechanical errors** — these are the things to slow down on (transcription, arithmetic)

Conflating these is a common feedback failure. A student told "you have 5 errors" when 4 are arithmetic and 1 is conceptual studies the wrong thing.

## Outputs

A markdown diff report containing:

1. **Per-step diff table** — step number, reference, student, category, feedback (in student-facing voice)
2. **Cascade map** — which downstream steps are cascades from earlier missteps (single underlying decision)
3. **Alternate-path notes** — any category (C) paths the student discovered, marked correct with provenance
4. **Conceptual gaps** — top 1-2 named, with a pointer to the principle / section to study
5. **Mechanical errors** — top 1-2 named separately from concepts
6. **Score** (if grading_mode = `summative`) — per the partial_credit_policy
7. **Next-action recommendation** — which pset / concept / pre-req to revisit before the next attempt

Length: typically 300-1200 words for a single multi-step pset attempt. Longer for code submissions with many functions.

## Failure modes

Known anti-patterns and how this skill catches them:

- **Marking right-answer-wrong-reasoning as correct** — caught by mandatory category classification (A is a category; right-answer alone is not enough)
- **Treating downstream cascade as fresh errors** — caught by step 3 cascade recognition; a five-step cascade from one misstep is one error, not five
- **Marking legitimate alternate paths as wrong** — caught by step 4 alternate-path-recognition test (same answer + valid principles + generalizes)
- **Feedback names symptom but not principle** — caught by step 5; the principle is the only thing that transfers
- **Conflating conceptual and mechanical errors** — caught by step 7 separated lists
- **Binary pass / fail with no category breakdown** — caught by mandatory per-step category assignment
- **No reference solution provided** — caught by step 0; refuses to engage and hands off to `teaching/writing-pset-walkthrough`
- **Empty / near-empty student attempt being "diffed"** — caught by step 0 minimum-content check; recommends walking the reference as a tutorial instead
- **Cascade-aware partial credit applied where steps are independent** — caught by `partial_credit_policy` argument; user picks the right policy for the problem structure
- **Feedback longer than the attempt itself** — caught informally by the output length guidance; over-feedback overwhelms the student

## References

- `reference/category-definitions.md` — full taxonomy with worked examples for each of (A) (B) (C) (D)
- `reference/feedback-voice.md` — rules for student-facing feedback (name the principle, not the symptom; one feedback message per step, not stacked)
- `reference/alternate-path-recognition.md` — the three-test heuristic for legitimate alternates plus common patterns by topic
- [Hattie & Timperley, *The Power of Feedback*, Review of Educational Research 2007](https://journals.sagepub.com/doi/10.3102/003465430298487) — academic source on formative feedback effectiveness
- [Black & Wiliam, *Inside the Black Box*, Phi Delta Kappan 1998](https://www.researchgate.net/publication/44836144_Inside_the_Black_Box_Raising_Standards_through_Classroom_Assessment) — origin of "formative assessment" as a graded-feedback discipline

## Examples

### Example 1: Cascading-error stats pset (happy-path)

Input: *"Reference solution and student attempt for the paired-cholesterol problem. The reference uses paired-design + Shapiro on differences (p = 0.018) + Wilcoxon. The student used two-sample t-test on the columns, ran Shapiro on each column separately, both passed, ran a pooled two-sample t. Give formative feedback."*

Output: skill diffs step-by-step. Step 1 (design): category (B) — student treated paired data as independent groups. Steps 2-4 (assumption + test choice + report): marked `cascade from step 1`, NOT as four fresh errors. Feedback for step 1 names the principle ("design determines the test family before any numbers are computed; same subjects measured twice = paired"). Cascade note: fixing step 1 propagates downstream. Conceptual gap: paired-vs-independent recognition. Mechanical errors: none. Next action: re-read the design-decision section before the next pset; the rest of the procedure was applied correctly to the wrong design.

### Example 2: Right answer, wrong reasoning (edge-case)

Input: *"Student answered '7' to the question 'What is the mode of [3, 5, 7, 7, 9]?' The answer is correct. But the student's work shows: 'mean = (3+5+7+7+9)/5 = 6.2, rounded to 7.' Did they get it right?"*

Output: skill classifies as category (A): right answer, wrong reasoning. The mode is 7 because 7 appears twice (most frequent), not because the mean rounds to 7. Feedback names the principle distinction (mode = most frequent value; mean = arithmetic average; these are different summary statistics that happen to coincide here by coincidence). Notes that the same approach would fail on `[3, 5, 7, 7, 13]` where the mode is still 7 but the rounded mean is 7. Recommends the student revisit the central-tendency section before the next pset. Does NOT mark the answer as correct without the feedback (the variation would expose the gap).

### Example 3: No reference solution provided (anti-trigger)

Input: *"Here's a student's attempt at a stats problem. Tell me how they did."* (Student attempt provided; problem text provided; no reference solution.)

Output: skill identifies the missing input (no reference solution) and refuses to produce a diff. Explains that the diff requires an anchor — without a reference, "feedback" would be the model's own interpretation of the problem, which conflates the model's judgment with the instructor's intended grading. Recommends two paths: (a) the user supplies a reference solution and the skill returns to produce the diff, or (b) the user invokes `teaching/writing-pset-walkthrough` to first author a canonical solution, then returns here for the diff. Does NOT proceed by inventing a reference under the hood.

## See also

- `teaching/writing-pset-walkthrough` — the upstream skill for authoring the reference solution when one does not exist
- `teaching/writing-graded-rubric` — for criterion-referenced rubric scoring on open-ended work where no canonical solution exists
- `teaching/explaining-statistical-concept` — for when the student needs concept-level remediation rather than per-step feedback
- `teaching/writing-onboarding-guide` — multi-audience format; a diff is single-audience (one student) so not a substitute
- `ml-datasci/selecting-statistical-test` — the underlying decision tree often invoked in stats-pset diffs
- `ml-datasci/checking-test-assumptions` — the assumption-check skill whose failure modes show up in diff feedback

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v6-batch-3, skill 4) via PRAGMATIC discipline
