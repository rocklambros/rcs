---
name: checking-test-assumptions
description: >
  Runs the appropriate assumption checks for a chosen statistical test
  (Shapiro-Wilk or Anderson-Darling for Normality, Levene or Brown-Forsythe for
  equal variance, QQ-plot for residuals, Cook's D for influence, expected-cell-
  count rule for chi-squared) and reports pass/fail per assumption with the
  evidence (test statistic + p-value) and the consequence if the assumption
  fails. Use whenever the user is about to run a parametric test, has just run
  one and wants to validate, or asks 'are the assumptions met?'.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, stats-student, instructor, ml-engineer]
evidence:
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Checking Test Assumptions

## When to use

Trigger this skill when the user asks for or implies one of:

- "Check the assumptions for [test]" or "are the assumptions met?"
- About to run a parametric test (t-test, ANOVA, linear regression) and wants assumption confirmation
- Has just run a test and wants post-hoc assumption validation (residual diagnostics)
- Provides Shapiro / Levene / QQ-plot output and asks for interpretation
- Reports a 2x2 contingency table and asks about chi-squared vs Fisher
- Phrases like "should I use a t-test or Wilcoxon?", "is my data Normal?", "are these variances equal?"

This skill pairs with `ml-datasci/selecting-statistical-test` — that skill picks the test; this one runs the gating checks.

## When NOT to use

Skip this skill and hand off when:

- The user is running a **non-parametric** test (Sign test, Wilcoxon, Mann-Whitney, Kruskal-Wallis) — most of the parametric assumption checks (Shapiro, Levene) do not apply
- The user is running a **permutation / randomization / bootstrap** test — the only "assumption" is exchangeability under the null; Shapiro / Levene are not the relevant checks
- The user is running a Bayesian analysis where prior + posterior diagnostics replace classical assumption checks
- The user is doing pure descriptive statistics with no inference (no p-values, no CIs)

## Quick start

User says: "I want to run a two-sample t-test on tumor sizes between treatment and control. n = 30 per group. Check the assumptions."

Skill response: walks the assumption checklist for an independent two-sample t-test — Normality per group (Shapiro-Wilk) + equal variance (Levene's test) — reports the per-assumption verdict table (Assumption · Test · Statistic · p-value · Verdict · Consequence-if-fail), and recommends the path forward (pooled t / Welch / Mann-Whitney) based on the verdicts.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| test | "one-sample-t" \| "paired-t" \| "two-sample-t" \| "anova" \| "linear-regression" \| "chi-squared" \| "logistic-regression" | yes | — | The planned parametric test whose assumptions need checking. |
| data | data path or pasted | yes | — | The data (or summary statistics if data is private). |
| n_per_group | integer or list | required for two-sample / ANOVA | — | Sample size per group; drives small-n vs large-n test choice. |
| skip_normality | bool | no | false | If true, only run variance and structural checks (use only when CLT applies AND user has justified it). |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check items off as each check completes:

```
Assumption-check progress:
- [ ] Step 1: Identify the test and look up its required assumptions
- [ ] Step 2: Run each assumption check; record statistic + p-value
- [ ] Step 3: Produce per-assumption verdict table
- [ ] Step 4: For each FAIL verdict, state the consequence + recommended alternative test
- [ ] Step 5: Final recommendation — proceed with planned test / switch to alternative / re-collect data
```

### Step 1: Map test → required assumptions

| Test | Required assumptions |
|---|---|
| one-sample t | Normality, independence |
| paired t | Normality of **differences**, independence of pairs |
| pooled (Student) two-sample t | Normality per group, **equal variance** (Levene), independence |
| Welch's two-sample t | Normality per group, independence (does NOT require equal variance) |
| one-way ANOVA | Normality per group, homoscedasticity (Levene / Brown-Forsythe), independence |
| repeated-measures ANOVA | Normality of residuals, **sphericity** (Mauchly), independence of subjects |
| linear regression | Linearity, Normality of residuals, homoscedasticity of residuals, independence (no autocorrelation), no influential outliers (Cook's D) |
| logistic regression | Linearity in the logit, independence, no separation, no multicollinearity (VIF), large-enough n per predictor (rule of thumb ≥ 10–20 events per predictor) |
| chi-squared independence | Independent observations, **all expected counts ≥ 5** for 2x2; ≤ 20% of cells below 5 for larger tables |

### Step 2: Run the assumption check(s)

| Assumption | Preferred check | Alternative | Threshold |
|---|---|---|---|
| Normality (n ≤ 50) | Shapiro-Wilk | Anderson-Darling, Lilliefors | p < 0.05 → reject Normality |
| Normality (n > 50) | Anderson-Darling | Kolmogorov-Smirnov (with corrected critical value) | p < 0.05 → reject Normality |
| Normality (any n) | QQ-plot | — | Visual inspection; heavy tails / S-shape → non-Normal |
| Equal variance | Levene's test (most robust to non-Normality) | Brown-Forsythe (uses median), Bartlett's (assumes Normality, less robust) | p < 0.05 → unequal variance |
| Sphericity (repeated-measures ANOVA) | Mauchly's test | — | p < 0.05 → sphericity violated; apply Greenhouse-Geisser or Huynh-Feldt |
| Residual Normality (regression) | Shapiro on residuals + QQ-plot of residuals | — | p < 0.05 OR visible deviation → consider transform |
| Residual homoscedasticity (regression) | Breusch-Pagan or White test, plus residuals-vs-fitted plot | Goldfeld-Quandt | p < 0.05 → heteroscedasticity; use robust (HC1/HC3) SE |
| Independence (regression) | Durbin-Watson | — | DW far from 2 (< 1.5 or > 2.5) → autocorrelation |
| Influential observations | Cook's distance | — | Cook's D > 1 → highly influential; > 4/n → flag |
| Expected cell counts (chi-squared) | Compute E_ij = (row_i × col_j) / N | — | Any cell < 5 for 2x2 → use Fisher exact |
| Multicollinearity (regression) | Variance Inflation Factor (VIF) | Condition index | VIF > 5 → concerning; > 10 → severe |

### Step 3: Produce the per-assumption verdict table

Required columns:

| Assumption | Test | Statistic | p-value (if applicable) | Verdict | Consequence if fail |
|---|---|---|---|---|---|

### Step 4: For each FAIL verdict, state the consequence and the alternative

- **Normality fails** → switch to the non-parametric analog (Wilcoxon / Mann-Whitney / Kruskal-Wallis / Friedman) OR justify CLT for large n (and accept that prediction intervals are still affected)
- **Equal variance fails** → switch to Welch's t (not pooled t) for 2 groups; switch to Welch's ANOVA for 3+
- **Sphericity fails** → apply Greenhouse-Geisser correction (conservative) or Huynh-Feldt (less conservative)
- **Residual Normality fails (regression)** → consider log/sqrt transform on Y; or use a generalized linear model (GLM with appropriate family); or use robust regression
- **Residual homoscedasticity fails (regression)** → use heteroscedasticity-consistent SE (HC1, HC3), or weighted least squares
- **Independence fails (regression)** → use generalized least squares with autocorrelation structure, or include lagged term, or use HAC SE (Newey-West)
- **Cook's D > 1** → investigate the observation; data entry error vs genuine influence; do NOT silently drop
- **Expected cell counts < 5 (chi-squared)** → switch to Fisher's exact test (2x2) or Fisher-Freeman-Halton (larger) or Monte-Carlo p-value
- **Multicollinearity (VIF > 10)** → drop one of the correlated predictors, or use ridge regression, or use PCA

### Step 5: Final recommendation

State explicitly:

1. Which test is now recommended (the planned test if all assumptions hold; the alternative if any failed)
2. The single decisive verdict that drove the recommendation
3. What evidence the user should attach in their writeup (Shapiro p, Levene p, QQ-plot, expected cell counts)

## Outputs

A short markdown response with:

1. **Test under audit** — name and required assumptions
2. **Per-assumption verdict table** — required columns above
3. **Failures highlighted** — bold or marked with FAIL
4. **Final recommendation** — proceed / switch test / re-collect
5. **Reporting checklist** — what to put in the methods/results section

## Failure modes

- **Skipping the assumption check entirely** — running a paired t-test on n = 18 without Shapiro. The DU-MSDSAI-4441-Final GRADING_ISSUES.md #1 grader call-out. Caught by: Step 1 requires looking up assumptions BEFORE running the test.
- **Conditional inference on Normality** — running Shapiro, finding p < 0.05, then running the t-test anyway because "n is reasonable." The DU-MSDSAI-4441-Final GRADING_ISSUES.md #5 grader call-out. Caught by: Step 4 requires switching to the non-parametric alternative when Normality fails, not ignoring the failure.
- **Wrong column for paired-t Normality** — Shapiro-testing the raw `before` and `after` columns instead of `after − before`. Caught by: Step 1 maps `paired-t` → "Normality of differences" explicitly.
- **Using chi-squared on a sparse table** — running chi-squared on a 2x2 where an expected count is 3. The DU-MSDSAI-4441-Final GRADING_ISSUES.md #7 grader call-out. Caught by: Step 1 lists expected-count-≥5 as the chi-squared gating assumption; Step 4 routes to Fisher on fail.
- **Treating non-parametric / permutation as needing Shapiro** — wasting effort running Levene / Shapiro for a Mann-Whitney or randomization test. Caught by: "When NOT to use" explicitly excludes those tests; skill hands off.
- **Reporting only the verdict without evidence** — "assumptions met" with no Shapiro p, no Levene p, no QQ-plot. Caught by: the per-assumption verdict table mandates a Statistic + p-value column.

## References

- [`reference/assumption-cookbook.md`](reference/assumption-cookbook.md) — per-test assumption checklist with thresholds, code snippets, and consequence-if-fail
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for workflow-checklist pattern
- Field, *Discovering Statistics Using R* — chapter on assumption checking for parametric tests

## Examples

### Example 1: Two-sample t-test pre-check (happy-path)

Input: "I want to run a two-sample t-test on tumor sizes between treatment and control. n = 30 per group. Check assumptions."

Output: Test = pooled two-sample t-test. Required assumptions: Normality per group + equal variance + independence. Per-assumption table:

| Assumption | Test | Statistic | p-value | Verdict | Consequence if fail |
|---|---|---|---|---|---|
| Normality (treatment) | Shapiro-Wilk | W = `<value>` | `<value>` | pass/fail | Switch to Mann-Whitney |
| Normality (control) | Shapiro-Wilk | W = `<value>` | `<value>` | pass/fail | Switch to Mann-Whitney |
| Equal variance | Levene's test | F = `<value>` | `<value>` | pass/fail | Switch from pooled t to Welch's t |
| Independence | (design check) | — | — | confirmed by study design | (not testable from data) |

Recommendation: report the actual values from the user's data, then route per the table — if all pass → pooled t; if Levene fails only → Welch's t; if either Shapiro fails → Mann-Whitney U.

### Example 2: Mixed verdicts (edge-case)

Input: "Shapiro for group A: p = 0.12. Shapiro for group B: p = 0.001. Levene: p = 0.04. What now?"

Output: Group A Normality verdict = pass (p = 0.12 ≥ 0.05). Group B Normality verdict = **fail** (p = 0.001 < 0.05). Levene verdict = **fail** (p = 0.04 < 0.05; variances unequal). Two violations: non-Normality in one group, unequal variance. Recommendation: **Mann-Whitney U test** is the cleanest path — it sidesteps both the Normality failure and the variance inequality concern. Welch's t-test is a fallback that handles the variance issue but does not address the non-Normality of group B; only use Welch if the user can justify CLT for both groups (large n) and is willing to accept the residual non-Normality.

### Example 3: Permutation test (anti-trigger)

Input: "I'm running a randomization permutation test. Check assumptions."

Output: Permutation / randomization tests do not have the same parametric assumptions as t-tests / ANOVA. Shapiro-Wilk and Levene's test are NOT appropriate gating checks here. The relevant assumption is **exchangeability under the null hypothesis**: the labels (group / treatment / order) must be interchangeable if H₀ is true. The skill explains the difference, lists exchangeability-relevant concerns (e.g., independent observations, no carryover effect for paired permutations), and hands off — there is no Shapiro / Levene table to produce.

## See also

- `ml-datasci/selecting-statistical-test` — picks the test; this skill runs the gating checks
- `ml-datasci/reporting-effect-sizes` — once the test is appropriate, pair with the right effect size
- `ml-datasci/auditing-train-test-split` — different concern (ML eval validity), but shares the "audit before reporting" discipline

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
