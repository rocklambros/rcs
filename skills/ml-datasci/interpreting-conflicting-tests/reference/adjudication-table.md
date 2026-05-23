# Conflict-Adjudication Table

Per-test-pair reference for the SKILL.md Step 4 adjudication rule. The convention: **the test whose assumptions HOLD wins**, regardless of which p-value is smaller.

## Paired t vs Wilcoxon signed-rank

| Situation | Winner | Reason |
|---|---|---|
| Shapiro on differences p ≥ 0.05 AND no extreme outliers | Paired t | t is more powerful when Normality holds |
| Shapiro p < 0.05 AND n < 30 | Wilcoxon | CLT rescue not in effect; Normality really matters |
| Shapiro p < 0.05 BUT n > 50 AND only mild skew | Paired t (cautiously) | CLT rescue kicks in for n > 50 with non-extreme deviations |
| One or two extreme differences drive Shapiro | Hodges-Lehmann or trimmed-mean | Outlier-driven; report robust estimator instead |
| Pre-registered to one test | The pre-registered test | Adjudication is moot; pre-reg wins |

## Two-sample t (pooled) vs Welch t

| Situation | Winner |
|---|---|
| Levene p ≥ 0.05 (equal variance OK) | Pooled t |
| Levene p < 0.05 (unequal variance) | Welch t — always |
| Sample sizes very different (ratio > 2:1) | Welch t even if Levene OK (more robust) |

Welch is almost always the safe default; pooled t is only meaningfully more powerful when variances really are equal AND sample sizes are equal.

## Two-sample t vs Mann-Whitney U

| Situation | Winner |
|---|---|
| Both groups' Shapiro p ≥ 0.05 | Two-sample t (use Welch if Levene rejects equal variance) |
| Either group's Shapiro p < 0.05 with n < 30 per group | Mann-Whitney U |
| Both groups n > 50, mild non-Normality | Welch t (CLT rescue) |
| Distribution shapes clearly different (one skewed, one symmetric) | Neither test is great — consider a permutation test or report median difference with Hodges-Lehmann CI |

## Chi-squared vs Fisher's exact (2×2)

| Situation | Winner |
|---|---|
| All expected counts ≥ 5 | Chi-squared (without continuity correction) |
| Any expected count < 5 | Fisher's exact — always |
| Default for small samples | Fisher (no harm; just slightly less powerful at large n) |

The "5" threshold is the conventional rule from Cochran; some sources use "expected counts ≥ 1 with no more than 20% < 5" for tables larger than 2×2.

## McNemar vs exact binomial sign test

| Situation | Winner |
|---|---|
| Discordant pairs ≥ 25 | McNemar (with or without continuity correction) |
| Discordant pairs < 25 | Exact binomial sign test |
| McNemar with vs without continuity correction disagrees at α = 0.05 | Exact binomial — the corrected p straddles in the borderline case |

## ANOVA vs Kruskal-Wallis

| Situation | Winner |
|---|---|
| All groups Shapiro p ≥ 0.05 AND Levene p ≥ 0.05 | One-way ANOVA |
| Any group Shapiro p < 0.05 with small n | Kruskal-Wallis |
| Variances differ across groups (Levene fails) | Welch's ANOVA or Brown-Forsythe (NOT pooled ANOVA, NOT Kruskal-Wallis if shape changes too) |
| Repeated-measures within-subject | Mixed-effects model is the better answer than either ANOVA or Friedman |

## Welch ANOVA vs Brown-Forsythe

| Situation | Winner |
|---|---|
| Variances differ but Normality OK | Welch's ANOVA |
| Variances differ AND Normality questionable | Brown-Forsythe (uses medians; more robust) |

## Pearson r vs Spearman ρ

| Situation | Winner |
|---|---|
| Linear relationship + both variables Normal | Pearson r |
| Monotonic but not linear, OR either variable non-Normal | Spearman ρ |
| Many ties in either variable | Kendall τ (less affected by ties) |

## Default decision when ALL assumptions hold for both tests

If both tests legitimately apply and neither has a violated assumption:

1. If pre-registered → pre-registered wins
2. Otherwise → parametric wins (more powerful estimator when assumptions hold)
3. Report the loser in the supplement for transparency

## When BOTH tests have violations

Sometimes BOTH tests in a pair have problems:

| Both violated | Recommendation |
|---|---|
| Paired t Normality + Wilcoxon symmetry both fail | Sign test (exact binomial) — assumes only independence |
| Two-sample t Normality + Mann-Whitney same-shape both fail | Permutation test on a chosen statistic (mean diff, median diff, trimmed-mean diff) |
| Chi-squared expected-count + Fisher's exact independence fails | The independence violation is fatal; the design is broken; no test can rescue it |
| Repeated-measures ANOVA sphericity + Friedman ties both fail | Mixed-effects model with appropriate correlation structure |

## Effect-size pairing

Once the winner is decided, use the matched effect-size metric:

| Winning test | Effect size + CI |
|---|---|
| Paired t | Cohen's dz with 95% CI |
| Two-sample t / Welch t | Cohen's d with 95% CI |
| Wilcoxon signed-rank | Paired rank-biserial r OR Hodges-Lehmann median difference with 95% CI |
| Mann-Whitney U | Cliff's δ with 95% CI |
| Chi-squared (2×2) | Odds ratio with 95% CI; risk difference for absolute scale |
| Fisher's exact | Odds ratio with exact 95% CI |
| McNemar | Risk difference for matched pairs with 95% CI |
| ANOVA | Partial η² or ω² with 95% CI |
| Kruskal-Wallis | Epsilon-squared (ε²) with 95% CI |

Cross-pairing (e.g., reporting Cohen's d after committing to Mann-Whitney as the primary) is a Step 7 failure mode.

## Documentation template (Step 8)

> Two candidate tests were considered for the [primary outcome]: a [parametric test] and a [non-parametric test]. The [parametric test's gating assumption — e.g., Normality of differences] was assessed via [check — e.g., Shapiro-Wilk]; the result was [statistic, p-value]. Because [the assumption was violated / held], the [winning test] was adopted as the primary analysis. The [winning test] yielded [statistic, p-value, effect size, 95% CI]. The [losing test] is reported in the supplement (Table S[N]) for transparency.

Adapt the bracket-fills to the actual test pair and result.
