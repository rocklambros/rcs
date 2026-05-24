# The four-category taxonomy

The skill classifies every step of a student attempt into exactly one of these four categories. Worked examples per category below.

## Category (A) — right answer, wrong reasoning

**Definition:** the final answer matches the reference, but the method that produced it does not generalize. Often a coincidence on a friendly dataset, a wrong principle that accidentally gives the right number, or a numerical fluke.

**Why it matters:** the next variation of the problem will expose the gap. Marking (A) as "correct" without flagging trains the student to repeat the wrong reasoning.

### Worked examples

**Stats — mode coincidence:**
- Question: *"What is the mode of [3, 5, 7, 7, 9]?"*
- Reference: mode = 7 (appears twice, most frequent)
- Student: *"mean = 6.2, rounded to 7"*
- Verdict: (A). Answer right; method does not generalize. On `[3, 5, 7, 7, 13]` the mode is still 7 but the rounded mean is 7, masking the gap. On `[1, 5, 7, 7, 9]` the mode is 7 but the rounded mean is 6 — the gap shows.

**Algebra — sign cancellation:**
- Question: *"Solve x^2 - 4 = 0."*
- Reference: x = ±2
- Student: *"x = 2 because 2^2 = 4."*
- Verdict: (A). Got one of two solutions; reasoning misses the ± from the square root. Will fail on x^2 - 5x + 6 = 0 (missing one of two roots).

**Programming — off-by-luck:**
- Question: *"Write `count_evens([1,2,3,4])` to return 2."*
- Reference: `len([x for x in lst if x % 2 == 0])` → 2
- Student: `len([x for x in lst if x < 3])` → returns 2 by coincidence (1 and 2 are < 3, of which 2 is even)
- Verdict: (A). Method tests "less than 3," not "is even." Will fail on `[2, 4, 6, 8]` (returns 0 instead of 4).

### Feedback voice for (A)

Name the principle distinction explicitly. Then give a single-variation counter-example that breaks the wrong reasoning. Do not just say "you got it right, but..."

## Category (B) — wrong answer, right reasoning with one identifiable misstep

**Definition:** the reasoning is correct up to a specific identifiable step where one wrong decision was made; the rest of the work correctly follows from that wrong decision.

**Why it matters:** highest-value feedback opportunity. Naming the single decision point gives the student a clear next-action and recovers most of the lost partial credit on the next attempt.

### Worked examples

**Stats — design misclassification:**
- Question: *"24 patients, before/after cholesterol, Shapiro on differences p = 0.018, α = 0.05. Test?"*
- Reference: paired → Shapiro on differences rejects Normality → Wilcoxon signed-rank
- Student: independent two-sample → Shapiro per column → pooled two-sample t
- Misstep at step 1: treated paired data as independent
- Verdict: (B). Steps 2-4 are cascade from the step-1 misclassification; the reasoning AFTER step 1 was correct given the wrong design.

**Calc — sign error in chain rule:**
- Question: *"Differentiate cos(3x)."*
- Reference: -3 sin(3x)
- Student: 3 sin(3x) (missed the negative sign from the derivative of cosine)
- Misstep: forgot d/dx cos(u) = -sin(u) carries the negative
- Verdict: (B). The chain-rule structure was right; one sign error.

### Feedback voice for (B)

Name the single misstep at the specific step. Confirm that the reasoning AFTER the misstep was correct given the wrong starting point. This affirms what the student got right and isolates what to fix.

## Category (C) — legitimate alternate path

**Definition:** the student arrives at the same correct answer via a different valid method than the reference. Should be marked CORRECT.

**Why it matters:** marking (C) as wrong because "it does not match the answer key" punishes mathematical maturity. It also misses an opportunity to harvest a better solution path for next year's answer key.

### The three-test check for (C) legitimacy

1. **Same final answer** (within rounding tolerance, including for symbolic expressions reducible to the same form)
2. **Each step uses a valid principle** (named, defensible — not coincidence; passes the test of "could I describe this method to a peer?")
3. **The path generalizes** (mentally substitute different α / different data shape / different sample size; if the method still produces the right answer, the path generalizes)

If any of the three fails, the path is NOT (C). It is (A) or (B).

### Worked examples

**Stats — Bayesian alternate to frequentist:**
- Question: *"Given 7 successes in 10 trials, is p > 0.5?"*
- Reference: frequentist test, p-value reasoning
- Student: Bayesian update with Beta(1,1) prior; posterior probability that p > 0.5 = 0.828
- Verdict: (C). Different framework, valid principle, generalizes. Marked correct.

**CS — top-down memoization alternate to bottom-up DP:**
- Question: *"Find LCS of two strings."*
- Reference: bottom-up DP table fill
- Student: recursive function with memoization decorator
- Verdict: (C). Same answer, valid principle, generalizes.

**Algebra — alternate factoring:**
- Question: *"Factor x^2 - 5x + 6."*
- Reference: (x - 2)(x - 3)
- Student: completing the square → (x - 5/2)^2 - 1/4 → reducible to (x - 2)(x - 3)
- Verdict: (C). Different path, valid, generalizes.

### Feedback voice for (C)

Mark as correct. Note that the reference uses a different method. If the alternate is more elegant or more general than the reference, flag for the instructor as a candidate to add to next year's answer key.

## Category (D) — uncorrelated error

**Definition:** transcription, arithmetic, off-by-one, label swap, dropped sign in copy-paste. Independent of the student's conceptual understanding of the problem.

**Why it matters:** conflating (D) with conceptual errors makes the student "study harder" for what is a mechanical mistake. The remediation is "slow down" / "check arithmetic," not "re-read the chapter."

### Worked examples

**Arithmetic:**
- Reference: sum = 35
- Student: sum = 36 (one number added wrong)
- Verdict: (D). No conceptual gap.

**Transcription:**
- Reference: uses sample of n=24
- Student: copied n=42 from the problem statement (digit swap)
- Verdict: (D). The downstream test was applied correctly but to the wrong n.

**Label swap:**
- Reference: group A mean = 5.2, group B mean = 7.1
- Student: reports A = 7.1, B = 5.2 (swapped labels)
- Verdict: (D). All computations correct; labels swapped.

### Feedback voice for (D)

Name the mechanical error type (arithmetic / transcription / label / off-by-one). Do NOT recommend the student "re-read the chapter" — that is the wrong remediation. Recommend a slowdown / double-check workflow at the step where the error happened.

## Edge case: (D) inside a (B) cascade

If a student makes a (D) error at step 1 (e.g., transcribed n=24 as n=42) and the rest of the work correctly follows that wrong number, the verdict is (D) at step 1 + cascade marker on downstream steps. Do NOT mark downstream as fresh errors.

## Edge case: blank attempt for some steps

If the student skipped some steps entirely:
- If a skipped step is non-trivial → mark as "not attempted" (separate from the four categories) and recommend revisiting the underlying concept
- If a skipped step is trivial → fold into the surrounding step's feedback ("you skipped writing out the assumption check; this is normally a one-line note")
