---
name: reporting-effect-sizes
description: >
  Reports statistical results with effect sizes plus 95% confidence intervals plus
  direction, and refuses to report bare p-values as 'significant'. Use whenever the
  user reports a t-test, regression, chi-squared, McNemar, or any hypothesis test
  result; the user is writing up a stats homework / paper / report; or the user says
  'p < 0.05 so X is true'. Selects the appropriate effect-size metric per test family
  (Cohen's d for parametric two-group, Cliff's delta for non-parametric, odds ratio
  for categorical, partial eta squared for ANOVA, adjusted R-squared for regression).
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, stats-student, instructor, ml-engineer]
evidence:
  - DU-MSDSAI-4441-Final
  - DU-MSDSAI-4441-pset-weekly
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Reporting Effect Sizes

## When to use

Trigger this skill when the user asks for or implies one of:

- Reporting a hypothesis test result (t-test, paired-t, Wilcoxon, Mann-Whitney, chi-squared, Fisher, McNemar, ANOVA, regression coefficient)
- Writing up statistics for a homework / paper / report / dashboard / presentation
- Saying "p < 0.05 so significant" or "the difference was significant" without naming an effect size
- Comparing two groups (means, medians, proportions) and reporting the comparison
- Building a results table or summary statistics block

## When NOT to use

Skip this skill and hand off when:

- The task is pure pedagogy about p-value mechanics (e.g., a lecture explaining Type I error or the history of the 0.05 convention) — do NOT block teaching with a real-reporting mandate
- The task is descriptive statistics only (means, SDs, percentiles) with no hypothesis test
- The task is power analysis / sample-size planning (different skill: `running-power-analysis`)
- The task is statistical-test selection before any test has been run (different skill: `selecting-statistical-test`)

## Quick start

User says: "We ran a paired t-test on before/after blood pressure for 30 patients. p = 0.012, t(29) = 2.68, mean diff = 4.3 mmHg. Help me report this."

Skill response: produces a Cohen's dz (paired) with 95% CI plus direction sentence. Example:

> Paired t-test on systolic BP before vs. after treatment (n = 30): mean difference = 4.3 mmHg (95% CI: 1.0, 7.6), Cohen's dz = 0.49 (95% CI: 0.12, 0.86), t(29) = 2.68, p = 0.012. After-treatment BP was lower than before-treatment BP by 4.3 mmHg on average.

Note: Cohen's dz (paired, not the unpaired d), explicit CI, and direction sentence — all three are required.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| test_family | string | yes | — | The test that was run: `t`, `welch-t`, `paired-t`, `wilcoxon`, `mann-whitney`, `paired-wilcoxon`, `chi-squared`, `fisher`, `mcnemar`, `anova`, `regression`. |
| summary_stats | object | yes | — | Test statistic, df, p-value, group means/medians, group SDs, sample size(s). |
| ci_level | float | no | 0.95 | Confidence interval level (95% conventional). |
| interpretation | bool | no | true | If true, include a Cohen-1988 interpretation tag (small / medium / large) with explicit "domain matters more than rules of thumb" caveat. |

## Workflow

Copy this checklist into the response and check off items as the report is built:

```
Effect-size reporting progress:
- [ ] Identify the test family (t / Welch / Wilcoxon / Mann-Whitney / paired / chi-sq / Fisher / McNemar / ANOVA / regression)
- [ ] Select the appropriate effect-size metric for that test family
- [ ] Compute the effect size from the provided summary statistics
- [ ] Compute the 95% confidence interval for the effect size (bootstrap or closed-form)
- [ ] Write the direction sentence (which group higher / lower, by how much)
- [ ] Refuse to report bare p-value as "significant" without effect size + CI present
```

### Step 1: Map test family to effect-size metric

See `reference/effect-size-cookbook.md` for the per-test table. Summary:

| Test family | Effect size | Why |
|---|---|---|
| Two-sample t / Welch | Cohen's d | Standardized mean difference |
| Paired t | Cohen's dz | Within-subject standardized mean difference |
| Mann-Whitney / Wilcoxon (independent) | Cliff's delta | Non-parametric rank dominance |
| Wilcoxon signed-rank (paired) | Rank-biserial r OR matched-pairs rank-biserial | Non-parametric paired effect |
| Chi-squared 2x2 | Odds ratio + risk difference | Categorical 2x2 effect |
| Chi-squared > 2x2 | Cramer's V | Categorical effect for larger tables |
| Fisher's exact 2x2 | Odds ratio | Same as chi-sq but for small expected counts |
| McNemar (paired binary) | Odds ratio from discordant pairs | Paired-binary effect |
| ANOVA | Partial eta-squared (or omega-squared for unbiased) | Variance explained |
| Linear regression | Adjusted R-squared per model; standardized beta per coefficient | Per-coefficient and overall effect |

### Step 2: Compute the effect size

Compute from the summary stats provided. See `reference/effect-size-cookbook.md` for the formulas. Prefer library-computed values (`scipy.stats`, `pingouin`, `effectsize` in R) over hand-computation when possible.

### Step 3: Compute the 95% CI

For Cohen's d / dz: use the non-central t-distribution closed-form, or bootstrap (n_bootstrap ≥ 1000).
For Cliff's delta: bootstrap.
For odds ratio: log-OR ± 1.96 × SE(log-OR), then exponentiate.
For partial eta-squared: bootstrap.

### Step 4: Direction sentence

ALWAYS state which group is higher / lower and by how much in the original units. "Groups differ" is not acceptable; "After-treatment BP was 4.3 mmHg lower than before-treatment BP" is acceptable.

### Step 5: Refuse bare p-value

If the user-provided result is just a p-value with no test-statistic or summary stats, refuse to write the report and ask for the missing information. "p < 0.05" alone cannot be reported as "significant" without an effect size + CI.

## Outputs

A report sentence (or block) with these required components:

1. **Test name + sample size** — "Paired t-test on systolic BP (n = 30)"
2. **Effect size + CI** — "Cohen's dz = 0.49 (95% CI: 0.12, 0.86)"
3. **Test statistic + df + p-value** — "t(29) = 2.68, p = 0.012"
4. **Direction sentence** — "After-treatment BP was lower than before-treatment by 4.3 mmHg on average"
5. **Optional interpretation tag** — "Conventionally medium effect (Cohen 1988), though clinical significance depends on the patient population"

## Failure modes

Known pitfalls in effect-size reporting and how this skill catches them:

- **Bare p-value report** — "p < 0.05 so significant" without effect size or CI. Caught by: refusal in Step 5 + explicit "all 5 output components required" enforcement.
- **Wrong-family effect size** — reporting Cohen's d (unpaired) for a paired t-test, masking the within-subject correlation. Caught by: Step 1 mapping table distinguishes paired (Cohen's dz) from unpaired (Cohen's d).
- **Non-parametric mismatch** — reporting Cohen's d on data where the test was Mann-Whitney (chosen because Normality failed). Caught by: Step 1 mapping table assigns Cliff's delta to non-parametric tests.
- **Missing direction sentence** — "groups differ significantly" without naming which group is higher. Caught by: Step 4 + explicit "groups differ is not acceptable" rule.
- **Interpretation overreach** — labelling d = 0.8 as "large" without acknowledging domain context. Caught by: optional interpretation tag explicitly includes the "domain matters more than rules of thumb" caveat.
- **Confounding p-value pedagogy with reporting** — pivoting a pedagogical request about p-value mechanics into an effect-size mandate. Caught by: explicit "When NOT to use" anti-trigger.

## References

- `reference/effect-size-cookbook.md` — per-test-family effect-size metrics, formulas, and CI methods
- `reference/cohen-1988-interpretation.md` — small/medium/large conventions with explicit domain caveats
- [Cumming 2014 *The new statistics: why and how*](https://journals.sagepub.com/doi/10.1177/0956797613504966) — case for effect sizes + CIs over p-values
- [Wilkinson & APA Task Force 1999](https://psycnet.apa.org/record/1999-11334-001) — APA recommendation to report effect sizes

## Examples

### Example 1: Paired t-test write-up (happy-path)

Input: "We ran a paired t-test on before/after blood pressure for 30 patients. p = 0.012, t(29) = 2.68, mean diff = 4.3 mmHg, SD of differences = 8.8. Help me report this."

Output: "Paired t-test on systolic BP before vs. after treatment (n = 30): mean difference = 4.3 mmHg (95% CI: 1.0, 7.6), Cohen's dz = 0.49 (95% CI: 0.12, 0.86), t(29) = 2.68, p = 0.012. After-treatment BP was lower than before-treatment BP by 4.3 mmHg on average. Cohen 1988 conventions would label this a medium effect, though the clinical meaning depends on the baseline BP and the patient population."

Note: Cohen's dz (paired, not unpaired d), explicit CI, direction sentence naming the lower group.

### Example 2: Wilcoxon signed-rank (edge-case)

Input: "Shapiro on the differences says they aren't Normal (p = 0.003). I ran a Wilcoxon signed-rank instead: V = 38, p = 0.018, n = 18 paired observations. Now what?"

Output: Skill switches from Cohen's d (which assumes Normality) to a non-parametric paired effect size — matched-pairs rank-biserial r OR Cliff's delta on the difference scores. Reports: rank-biserial r ≈ 0.57 (95% CI from bootstrap), direction sentence naming which side dominates. Explicitly does NOT report Cohen's d on non-Normal data.

### Example 3: P-value pedagogy lecture (anti-trigger)

Input: "For our stats lecture this week, explain how the p-value formula works and why p < 0.05 became conventional. Don't worry about effect sizes — that's next week."

Output: Skill does NOT pivot to an effect-size mandate. Explains the p-value mechanics as asked (probability of seeing a test statistic at least as extreme as observed, under the null). Notes briefly that real reporting also requires effect sizes + CIs, but does not block the lecture or rewrite it. Hands off to teaching content for the p-value formula derivation.

## See also

- `ml-datasci/selecting-statistical-test` — runs BEFORE this skill: decides which test to run
- `ml-datasci/checking-test-assumptions` — runs ALONGSIDE this skill: verifies the test was appropriate
- `ml-datasci/comparing-models-fairly` — McNemar / paired-folds tests for ML model comparison; uses this skill for the effect-size report
- `ml-datasci/interpreting-conflicting-tests` — handles the case where parametric and non-parametric disagree (planned)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: derived from DU-MSDSAI-4441-Final/GRADING_ISSUES.md items #4 (effect-size omission) and #6 (direction-sentence omission), reinforced by every DU-MSDSAI-4441 weekly pset and the llm-safety-alignment-study reporting discipline
