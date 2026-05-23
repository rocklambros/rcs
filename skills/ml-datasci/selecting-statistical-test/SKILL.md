---
name: selecting-statistical-test
description: >
  Walks a decision tree from data characteristics (sample count, paired vs
  independent, measurement scale, distributional assumptions) to a recommended
  statistical test (t / Welch / Wilcoxon / Mann-Whitney / Sign / paired-t /
  Fisher / chi-squared / McNemar / Cochran-Q). Names the gating assumption
  check that determined the choice. Use when the user has a hypothesis and
  data in hand and needs to commit to a test before running it.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, stats-student, instructor, ml-engineer]
evidence:
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Selecting a Statistical Test

## When to use

Trigger this skill when the user asks for or implies one of:

- "Which test should I use for...?" given a described design and data
- A hypothesis with described data shape (sample count, paired/independent, continuous/categorical) but no chosen test yet
- A request to confirm or challenge a test choice before they run it
- Phrases like "t-test or Wilcoxon?", "chi-squared or Fisher?", "what's the right test for paired binary outcomes?"
- The user has Shapiro / Levene / QQ output and is asking what to do with it

The skill is for the **selection** decision. The follow-on assumption check itself lives in `ml-datasci/checking-test-assumptions`.

## When NOT to use

Skip this skill and hand off when:

- The test is already chosen and the user wants help running it in Python / R / SPSS — that is a coding task, not a selection task
- The workflow is Bayesian (posterior, BF, credible interval) — different paradigm; selection logic does not transfer
- The user wants a Monte-Carlo / permutation / randomization test (those have minimal distributional assumptions; the decision tree below does not apply cleanly)
- The user is doing exploratory data analysis with no pre-specified hypothesis — pre-register the hypothesis first, then return

## Quick start

User says: "I have before/after blood pressure measurements for 18 patients. Shapiro on the differences gives p = 0.003. Which test should I use?"

Skill response: walks the decision tree (1 sample of differences → paired design → continuous → n = 18 small → Normality gating check failed: Shapiro p = 0.003 < 0.05 → Normality rejected) and recommends the **Wilcoxon signed-rank test**. Explicitly names the Shapiro p = 0.003 as the gating assumption check that ruled out the paired t-test.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| design | "paired" \| "independent" \| "one-sample" \| "repeated-measures" | yes | — | Within-subject (paired/repeated) vs between-subject (independent) vs single-sample. |
| scale | "continuous" \| "ordinal" \| "binary" \| "nominal" | yes | — | Measurement scale of the outcome variable. |
| n_per_group | integer or list of integers | yes | — | Sample size per group (or total for one-sample / paired). |
| normality_status | "normal" \| "non-normal" \| "unknown" | no | "unknown" | Result of Normality assumption check (Shapiro / Anderson-Darling / QQ). If "unknown", the skill will ask. |
| equal_variance_status | "equal" \| "unequal" \| "unknown" | no | "unknown" | Result of Levene / Brown-Forsythe. Only relevant for 2-independent-sample continuous. |
| expected_counts_min | integer | no | — | For 2x2 categorical: the minimum cell expected count. Drives chi-squared vs Fisher decision. |

If `design`, `scale`, or `n_per_group` are unknown, the skill MUST ask before recommending a test.

## Workflow

Copy this checklist into the response and check items off as the decision tree is walked:

```
Test-selection progress:
- [ ] Step 1: Confirm design — paired / independent / one-sample / repeated-measures
- [ ] Step 2: Confirm measurement scale — continuous / ordinal / binary / nominal
- [ ] Step 3: Confirm sample size per group
- [ ] Step 4: Identify the gating assumption check for this design + scale
- [ ] Step 5: Walk the decision tree to a recommended test
- [ ] Step 6: State the test recommendation AND name the gating check that drove it
```

### Step 1: Confirm the design

- **Paired** — same subject measured twice (before/after, matched pairs)
- **Independent** — different subjects in each group
- **One-sample** — a single sample compared to a known constant
- **Repeated-measures** — same subject measured 3+ times

If the user did not say, ask. Do not guess.

### Step 2: Confirm the measurement scale

- **Continuous** — interval / ratio; mean is meaningful (e.g., blood pressure, weight)
- **Ordinal** — ranked but interval-irregular (e.g., Likert 1–5)
- **Binary** — two-level categorical (success/failure)
- **Nominal** — multi-level categorical without order (e.g., color)

### Step 3: Confirm sample size

Small n (< 30 per group) pushes you toward non-parametric tests OR requires a Normality check. Large n leans on the CLT and softens the Normality requirement for **the test statistic**, but does not soften it for prediction intervals or per-observation inference.

### Step 4: Identify the gating assumption check

| Design + scale | Gating check |
|---|---|
| 1-sample continuous | Normality (Shapiro / Anderson-Darling) |
| Paired continuous | Normality of the **differences** (Shapiro on `after − before`) |
| 2 independent continuous | Normality per group + equal variance (Levene) |
| 3+ independent continuous (ANOVA) | Normality per group + homoscedasticity (Levene / Brown-Forsythe) |
| 2x2 categorical | Minimum expected cell count ≥ 5 (chi-squared) vs < 5 (Fisher) |
| Paired binary | n ≥ 25 → McNemar with continuity correction; n < 25 → McNemar exact |
| 3+ repeated binary | Cochran's Q |

### Step 5: Walk the decision tree

```
1 group?
├── one-sample continuous → Normality?
│   ├── Normal → one-sample t-test
│   └── Non-normal → Wilcoxon signed-rank (against median) OR Sign test
├── one-sample binary (proportion) → exact binomial OR normal-approximation z
└── one-sample categorical k-level → chi-squared goodness-of-fit

2 groups?
├── Paired
│   ├── Continuous → Normality of differences?
│   │   ├── Normal → paired t-test
│   │   └── Non-normal → Wilcoxon signed-rank
│   ├── Ordinal → Wilcoxon signed-rank
│   └── Binary → McNemar (continuity correction if n ≥ 25; exact if n < 25)
├── Independent
│   ├── Continuous → Normality?
│   │   ├── Normal + equal variance → pooled (Student) t-test
│   │   ├── Normal + unequal variance → Welch's t-test
│   │   └── Non-normal → Mann-Whitney U
│   ├── Ordinal → Mann-Whitney U
│   └── Binary / 2x2 → all expected counts ≥ 5?
│       ├── Yes → chi-squared test of independence
│       └── No → Fisher's exact test

3+ groups?
├── Paired / repeated-measures continuous → repeated-measures ANOVA (or Friedman if non-normal)
├── Paired / repeated-measures binary → Cochran's Q
├── Independent continuous → one-way ANOVA (or Kruskal-Wallis if non-normal)
└── Independent categorical k×j → chi-squared test of independence (or Fisher-Freeman-Halton for sparse cells)
```

### Step 6: State the test AND the gating check

A correct recommendation has two parts:

1. The test name
2. The single assumption result that drove the choice — e.g., "Wilcoxon signed-rank, because Shapiro p = 0.003 on the differences rejected Normality at α = 0.05"

If the gating check was not provided, recommend running it FIRST and return.

## Outputs

A short markdown response with the following structure:

1. **Design summary** — confirmed design, scale, sample size
2. **Gating assumption check** — name + result (Shapiro p, Levene p, expected counts, etc.)
3. **Recommended test** — exact name (e.g., "Welch's t-test", not "t-test")
4. **Why** — one sentence linking the gating check to the choice
5. **Fallback** — what the alternative would be if the gating check flipped (e.g., "If Shapiro had passed, paired t-test")

## Failure modes

- **Recommending a test without an assumption check** — selecting paired t-test for n = 18 without first knowing Shapiro. Caught by: Step 4 makes the gating check mandatory before Step 5.
- **Mixing up the chi-squared vs Fisher rule** — using chi-squared on a sparse 2x2 where any expected cell is below 5. The DU-MSDSAI-4441-Final GRADING_ISSUES.md #7 grader call-out was exactly this. Caught by: explicit expected-count column in Step 5 decision tree.
- **Treating paired data as independent** — running an independent t-test on before/after data inflates Type II error. Caught by: Step 1 forces the design confirmation before anything else.
- **Ignoring measurement scale** — running a t-test on Likert data. Caught by: Step 2 separates ordinal from continuous; ordinal routes to Wilcoxon / Mann-Whitney.
- **Assuming CLT covers small n** — invoking the CLT for n = 12 to skip the Normality check. Caught by: Step 3 makes sample size explicit; tree only takes "Normal → t" if Normality was actually confirmed.

## References

- [`reference/decision-tree.md`](reference/decision-tree.md) — full text decision tree with worked branches
- [`reference/test-cookbook.md`](reference/test-cookbook.md) — per-test card: when to use, assumptions, effect size to pair with, common gotchas
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for workflow-checklist pattern
- Sheskin, *Handbook of Parametric and Nonparametric Statistical Procedures* — full procedural reference

## Examples

### Example 1: Paired non-normal small-n (happy-path)

Input: "I have before/after blood pressure for 18 patients. Shapiro on the differences gives p = 0.003. Which test?"

Output: Design = paired (within-subject). Scale = continuous. n = 18 (small). Gating check = Shapiro on differences → p = 0.003 < 0.05, Normality rejected. **Recommended test: Wilcoxon signed-rank test.** Reason: paired + continuous + non-Normal differences → the parametric paired t-test is not appropriate; Wilcoxon signed-rank is the rank-based paired equivalent. Fallback: had Shapiro p ≥ 0.05, the paired t-test would be the correct choice.

### Example 2: Sparse 2x2 (edge-case)

Input: "I have a 2x2 contingency table: 3 successes / 7 failures vs 8 successes / 12 failures. Chi-squared or Fisher?"

Output: Design = independent. Scale = binary. n = 30 total (10 + 20). Expected counts: row sums [10, 20], col sums [11, 19], grand total 30 → E11 = 10×11/30 = 3.67, E12 = 10×19/30 = 6.33, E21 = 20×11/30 = 7.33, E22 = 20×19/30 = 12.67. **Minimum expected count = 3.67 < 5.** Recommended test: **Fisher's exact test**, not chi-squared. Reason: chi-squared approximation requires all expected cell counts ≥ 5; one cell is 3.67. Fallback: if all expected counts had been ≥ 5, chi-squared with Yates' continuity correction would be acceptable.

### Example 3: Pre-test request (anti-trigger)

Input: "Run a t-test on this column for me."

Output: The skill refuses to recommend or run a test without first confirming three things: (1) Is this paired or independent? (2) What's the sample size per group? (3) Has Normality been checked? Without those, picking "t-test" is guessing. Lists what to provide and offers to run the assumption checks first via `ml-datasci/checking-test-assumptions`.

## See also

- `ml-datasci/checking-test-assumptions` — run the gating assumption check this skill names
- `ml-datasci/reporting-effect-sizes` — pair the test with the right effect size (Cohen's d, Cliff's δ, odds ratio, etc.)
- `ml-datasci/evaluating-binary-classifiers` — for ML eval significance testing (McNemar, paired bootstrap)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
