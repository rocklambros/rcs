---
name: writing-pset-walkthrough
description: >
  Writes a problem-set walkthrough that uses a four-part template per step:
  "What it's asking" (restates the question in the student's own conceptual
  vocabulary), "Why this works" (names the principle / theorem / method
  being applied), "What the result tells us" (interprets the numerical or
  symbolic output back into the original question), and "Gotcha" (names the
  predictable failure mode at that step). Triggers when a student, TA, or
  instructor wants a worked walkthrough of a non-trivial problem set
  (statistics, probability, machine learning, applied math, programming
  exercises) where bare answer keys are insufficient because the student
  needs to recognize the pattern in future variations. Refuses to produce a
  walkthrough for a one-line trivial computation where the four-part
  template is overkill, and refuses to write an answer key that does not
  include the why-this-works step (which is the only part that transfers
  to the next problem).
version: 0.1.0
status: shipped
track: teaching
audience:
  - instructor
  - ta
  - stats-student
  - skill-author
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
last-updated: 2026-05-23
---

# Writing a Problem-Set Walkthrough

## When to use

Trigger this skill when:

- A student asks for a worked walkthrough of a multi-step problem (statistics, probability, machine learning, regression diagnostics, applied math, programming exercise)
- A TA or instructor is writing reference solutions for a graded problem set and wants the solutions to teach pattern recognition, not just produce answers
- The user says *"I got the right answer but I don't understand why this approach worked,"* which signals the four-part template's "Why this works" step is the missing piece
- The user submits *"here is my work, where did I go wrong?"* — the walkthrough format is the diagnostic tool to compare against
- An answer key already exists but reviewers report students *"can do the homework problems but bomb the exam variations"* — the existing answer key skipped the principle and the interpretation
- An instructor is producing exam-prep material and wants the explicit pattern-naming step so students recognize the structure under modified conditions

## When NOT to use

Skip this skill and hand off when:

- The problem is a one-line trivial computation (`mean of [1, 2, 3, 4, 5]`) — the four-part template is overkill; a one-line answer is sufficient
- The problem has multiple legitimate solution paths and the user wants comparative analysis of which is best (use `teaching/diffing-instructor-vs-student-solution` for the comparison)
- The user wants a pure conceptual explanation with no specific problem in hand (use `teaching/explaining-statistical-concept`)
- The artifact is an automated grading rubric (use `teaching/writing-graded-rubric`)
- The user wants a research-paper walkthrough or theorem proof exposition — different format (literature walk, not pset walk)
- The user explicitly wants an answer key WITHOUT pedagogical scaffolding (e.g., for an assessment where the principle is the thing being tested) — in that case, produce a bare key and explicitly note the trade-off

## Quick start

User: *"Here's a problem from our intro stats pset: 'A clinical trial of 24 patients tests whether a new drug lowers cholesterol. Before/after differences have Shapiro-Wilk p = 0.018. Choose and run the appropriate test at α = 0.05.' Write the walkthrough."*

Response: produce a four-part walkthrough per step, in order. Do not skip the "Why this works" step (the only part that transfers to the next problem). Do not skip the "Gotcha" step (where the student is most likely to slip).

```markdown
## Step 1: Read the design

- **What it's asking:** is this a one-group or two-group comparison? Are observations paired or independent?
- **Why this works:** the design dictates the test family before any number is computed.
- **What the result tells us:** before/after on the same 24 patients → PAIRED, one-group on differences.
- **Gotcha:** new students often code a two-sample t-test here because there are "two columns" (before, after). The two columns belong to the SAME patient — that is paired data.

## Step 2: Check the gating assumption

- **What it's asking:** are the differences Normally distributed? (Required for the paired t-test.)
- **Why this works:** assumption violations invalidate the parametric test's p-value.
- **What the result tells us:** Shapiro-Wilk p = 0.018 < α = 0.05 → reject Normality of the differences.
- **Gotcha:** students often run Shapiro on the BEFORE column AND the AFTER column. For paired tests, Shapiro is run on the DIFFERENCES.

## Step 3: Pick the right test
- **What it's asking:** which paired test handles non-Normal data?
- **Why this works:** ...
```

See `reference/four-part-template.md` for the per-step skeleton + worked examples, `reference/gotcha-catalog.md` for the cataloged failure modes by topic (paired-vs-independent, Normality-assumption, multiple-comparison, leakage, etc.), and `reference/student-vocabulary-tiers.md` for the rule on matching the "What it's asking" vocabulary to the student's stage.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `problem_text` | string / markdown | yes | — | The verbatim problem-set question. Drives the walkthrough structure; ambiguity in the problem text surfaces as ambiguity in the walkthrough. |
| `audience_tier` | enum | yes | — | `high-school` \| `undergrad-intro` \| `undergrad-advanced` \| `grad` \| `practitioner`. Drives the vocabulary in "What it's asking" — the principle name in "Why this works" can stay constant, but the restatement must match the tier. |
| `topic` | string | yes | — | Topic tag (e.g., `paired-t`, `linear-regression`, `chi-squared`, `bayesian-update`, `cross-validation`, `dynamic-programming`). Drives which gotcha catalog applies. |
| `student_attempt` | markdown / code / image | no | none | The student's attempted solution. If provided, the walkthrough is comparative (uses `teaching/diffing-instructor-vs-student-solution` workflow alongside). |
| `step_count_target` | integer | no | auto | Suggested number of steps. Default: skill chooses based on problem complexity (typical: 3-7 steps). Above 10 steps, recommend splitting the problem. |
| `include_alternate_path` | bool | no | `false` | If `true`, add a final section showing an alternate valid approach (e.g., the Bayesian path alongside the frequentist path). Use sparingly; can confuse early-tier students. |
| `bare_key_mode` | bool | no | `false` | If `true`, produce a bare answer key without pedagogical scaffolding. Explicitly notes the trade-off being made. |

## Workflow

```
Pset walkthrough authoring progress:
- [ ] 0. Confirm scope: is the problem non-trivial AND multi-step? If not, recommend bare answer
- [ ] 1. Audience tier check: what vocabulary will the student own at this stage?
- [ ] 2. Decompose problem into 3-7 steps; each step is one atomic decision or computation
- [ ] 3. Per step, write the four parts: What-asking · Why-works · Result-tells-us · Gotcha
- [ ] 4. Cross-check: the "Why this works" sentences should form a complete principle chain (read them alone — they tell the meta-story)
- [ ] 5. Verify the gotcha catalog: each named gotcha is a known student failure mode (no invented ones)
- [ ] 6. Final-answer recap: one paragraph stating the answer + the principle that produced it
- [ ] 7. Connect to the next problem: name the variation pattern (e.g., "if α changed, step 4 changes; if pairing changed, step 1 changes")
```

### The four-part template per step

**1. What it's asking** — restates the step's question in the student's vocabulary. For early-tier students, avoid jargon that has not been introduced yet (e.g., "homoscedasticity" → "the spread of residuals is roughly constant"). For practitioner tier, the jargon is the vocabulary; do not under-tier.

**2. Why this works** — names the principle, theorem, method, or rule being applied. This is the ONLY part that transfers. A student who reads three walkthroughs of paired t-tests with the same "Why this works" sentence will internalize the rule.

**3. What the result tells us** — interprets the output back into the original question. A p-value is not the answer; the interpretation in the original question's language is the answer.

**4. Gotcha** — names the predictable failure mode at this step. Pull from `reference/gotcha-catalog.md` by topic. Do NOT invent gotchas — only catalog real, observed student errors.

### Step 4: Cross-check the principle chain

Read the "Why this works" sentences alone, in order, without the other three parts. They should form a complete reasoning chain for the problem. If they do not, the walkthrough has gaps. This step catches "I'm computing something but I do not know why" walkthroughs.

Example (paired non-Normal test):

> Step 1: design dictates the test family.
> Step 2: assumption checks gate the parametric variant.
> Step 3: when the assumption fails, switch to the non-parametric variant within the same family.
> Step 4: hypothesis tests answer YES/NO at a stated α; effect sizes answer "how much."
> Step 5: confidence intervals quantify the uncertainty around the effect.

Read alone, those sentences teach the meta-pattern: design → assumption → test choice → significance → magnitude → uncertainty. That is the pattern the student needs for the next pset.

### Step 5: Gotcha discipline — no invented failure modes

Every gotcha line must be a real, observed student error. Source from:

- The instructor's grading history (most powerful source)
- Published taxonomies (Cohen's misuse-of-stats catalog, ESL chapter on common pitfalls)
- `reference/gotcha-catalog.md` (curated by topic in this skill)

Forbidden: inventing a gotcha that sounds plausible but has never actually tripped a student up. Inventing gotchas dilutes the catalog and trains students to defend against ghosts.

### Step 7: Connect to the next problem

End every walkthrough with one paragraph naming the variation patterns:

- *If α changed, step 4 changes (compare p to new α).*
- *If the pairing changed (independent groups), step 1 changes (two-sample test family).*
- *If the sample size dropped below 8-10 per group, step 2 changes (Shapiro is underpowered; use a QQ-plot judgment).*

This step turns the walkthrough from "answer to one problem" into "pattern for a class of problems."

## Outputs

A markdown walkthrough containing:

1. **Problem restatement** — verbatim question + a one-sentence reading of the decision the student must make
2. **3-7 numbered steps**, each with the four-part template (What-asking · Why-works · Result-tells-us · Gotcha)
3. **Principle chain recap** — the "Why this works" sentences extracted in order, as a one-paragraph summary of the meta-pattern
4. **Final answer** — one paragraph restating the answer + the principle that produced it
5. **Variation guide** — names the patterns under which the walkthrough generalizes ("if X changed, step Y changes")

Length: typically 400-1500 words. Above 1500, the problem is likely composite — split into two walkthroughs.

## Failure modes

Known anti-patterns and how this skill catches them:

- **Bare answer key with no principle** — caught by mandatory "Why this works" per step; the principle chain recap is a hard gate
- **Walkthrough that computes correctly but never interprets** — caught by mandatory "What the result tells us"; p-values and t-statistics are never the final answer
- **Invented gotchas that sound plausible but have not been observed** — caught by the gotcha-catalog discipline (step 5); only catalog real student errors
- **Vocabulary mismatch with audience tier** — caught by step 1 tier check; jargon below the student's stage gets translated, jargon at or above the tier stays
- **Walkthrough that solves the problem but does not generalize** — caught by step 7 variation guide; explicit "if X changed, step Y changes" framing
- **Composite problem treated as one walkthrough (> 10 steps)** — caught by step 2 decomposition target; split into two walkthroughs
- **The principle chain has gaps when read alone** — caught by step 4 cross-check; if the "Why this works" sentences do not form a complete chain, add the missing step
- **Walkthrough labeled "correct" but the gotcha section is empty** — caught by gotcha-per-step requirement; if a step has zero observed failure modes, the step is likely trivial and should fold into the adjacent step
- **Multi-path problem forced into one path** — caught by the `include_alternate_path` flag; if the user knows multiple valid approaches exist, the walkthrough can surface them

## References

- `reference/four-part-template.md` — per-step skeleton with worked examples (paired t, regression, classification, dynamic programming)
- `reference/gotcha-catalog.md` — cataloged student failure modes by topic (paired-vs-independent, Normality, multiple comparison, leakage, cross-validation, regression diagnostics)
- `reference/student-vocabulary-tiers.md` — rule for matching the "What it's asking" vocabulary to the student's stage (high-school / undergrad-intro / undergrad-advanced / grad / practitioner)
- [Bloom's taxonomy of educational objectives](https://en.wikipedia.org/wiki/Bloom%27s_taxonomy) — the four-part template aligns to Knowledge (What-asking) → Comprehension (Why-works) → Application + Analysis (Result-tells-us) → Evaluation (Gotcha)
- [Cohen, *Statistical Power Analysis*, 1988](https://www.routledge.com/Statistical-Power-Analysis-for-the-Behavioral-Sciences/Cohen/p/book/9780805802832) — source for many gotchas in the parametric-test catalog

## Examples

### Example 1: Paired non-Normal stats problem (happy-path)

Input: *"Write a walkthrough for this pset problem: 'A clinical trial of 24 patients tests whether a new drug lowers cholesterol. Before/after differences have Shapiro-Wilk p = 0.018. Choose and run the appropriate test at α = 0.05.' Audience tier: undergrad-intro."*

Output: skill produces a 5-step walkthrough. Step 1 (design): paired (same patients before/after), gotcha: students confuse two columns for two groups. Step 2 (assumption): Shapiro on the differences (not on each column), p = 0.018 < 0.05 → reject Normality, gotcha: running Shapiro on each column separately. Step 3 (test choice): Wilcoxon signed-rank (paired + non-Normal), gotcha: defaulting to paired t even when the assumption fails. Step 4 (run + report): test statistic V, p-value, interpretation. Step 5 (effect size): rank-biserial r or Cliff's δ for paired non-parametric, with CI, gotcha: reporting only p without effect size. Principle chain: design → assumption → test choice → significance → magnitude. Final-answer paragraph names the conclusion in cholesterol-lowering language, not p-value language. Variation guide: if α changed → step 4; if pairing changed → step 1; if n < 10 → step 2 (Shapiro underpowered).

### Example 2: Multi-path optimization problem (edge-case)

Input: *"Write a walkthrough for: 'Find the longest common subsequence of strings ABCBDAB and BDCABA. Audience: undergrad-advanced.' I want students to see the DP table approach AND the recursive-with-memoization approach."*

Output: skill produces the four-part walkthrough for the canonical DP table approach (5 steps: subproblem definition, recurrence, table fill order, traceback, answer extraction). At the end, adds a clearly-labeled `Alternate path: top-down memoization` section showing the same problem solved with recursion + memo, with a one-sentence note on the trade-off (DP table is iterative + cache-friendly; memoization is closer to the recurrence definition + can skip unreachable states). Names the gotcha specific to the alternate path (memoization with mutable default arguments). Does NOT collapse the two paths into a confusing hybrid. Variation guide: if the strings are very long → step 3 changes (rolling array to save space).

### Example 3: Trivial one-line problem (anti-trigger)

Input: *"Write a walkthrough for: 'Compute the mean of [3, 5, 7, 9, 11].'"*

Output: skill recognizes this as a one-line trivial computation. Refuses to produce the four-part template (overkill — the four parts would each be one trivial sentence). Returns a one-line answer: `mean = (3+5+7+9+11)/5 = 7`. Explicitly notes the decision: *"This problem is a single computation; the four-part walkthrough template is for multi-step problems where pattern recognition is the goal. If the surrounding pset uses this as a warmup before a multi-step problem, you may want a walkthrough for the multi-step problem instead."* Offers to walk through a related multi-step problem if the user supplies one.

## See also

- `teaching/diffing-instructor-vs-student-solution` — when the student has an attempt and the user wants comparative feedback
- `teaching/explaining-statistical-concept` — when the user wants a pure conceptual explanation, not tied to a specific problem
- `teaching/writing-graded-rubric` — when the artifact being authored is an assessment rubric, not a walkthrough
- `teaching/writing-onboarding-guide` — multi-audience format; pset walkthroughs are single-audience (one student tier)
- `ml-datasci/selecting-statistical-test` — the underlying test-selection decision tree often invoked inside a stats walkthrough
- `ml-datasci/checking-test-assumptions` — the assumption-check skill that step 2 of a stats walkthrough typically invokes

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v6-batch-3, skill 3) via PRAGMATIC discipline
