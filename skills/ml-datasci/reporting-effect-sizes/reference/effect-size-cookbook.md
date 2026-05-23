# Effect-size cookbook — per-test-family metrics + formulas + CI methods

Use this table to map a test family to its appropriate effect-size metric. Compute from summary stats; prefer library-computed values when possible.

## Two independent groups, parametric

**Cohen's d** = (mean₁ − mean₂) / pooled SD

Pooled SD = sqrt( ( (n₁−1)·SD₁² + (n₂−1)·SD₂² ) / (n₁ + n₂ − 2) )

**95% CI**: non-central t closed-form (use `pingouin.compute_esci(stat='cohen-d')`) or bootstrap with n_bootstrap ≥ 1000.

**Welch's variant** (unequal variance): use the same Cohen's d, but optionally report Hedges' g as a small-sample bias correction:
g = d · (1 − 3 / (4·(n₁ + n₂) − 9))

## Paired (within-subject), parametric

**Cohen's dz** = mean(differences) / SD(differences)

Different from unpaired d — dz accounts for within-subject correlation and is generally LARGER than the unpaired d on the same data.

**95% CI**: non-central t closed-form, or bootstrap.

**Common error**: reporting unpaired Cohen's d for paired data. The unpaired d ignores the within-subject correlation and underestimates the standardized effect. Always use dz for paired designs.

## Two independent groups, non-parametric

**Cliff's delta** = (count(x > y) − count(x < y)) / (n_x · n_y)

Range: [−1, 1]. Interpretable as the difference between the probability of x dominating y and the probability of y dominating x.

**95% CI**: bootstrap (no clean closed-form).

**Cohen 1988-style interpretation**:
- |δ| < 0.147 negligible
- 0.147 ≤ |δ| < 0.33 small
- 0.33 ≤ |δ| < 0.474 medium
- |δ| ≥ 0.474 large

## Paired, non-parametric (Wilcoxon signed-rank)

**Matched-pairs rank-biserial r** = (W+ − W−) / (W+ + W−)

Where W+ and W− are the positive and negative rank sums.

**Alternative**: Cliff's delta on the difference scores.

**95% CI**: bootstrap.

## Categorical 2×2 (chi-squared, Fisher)

**Odds ratio** = (a·d) / (b·c)

For a 2×2 table:
```
              Outcome+  Outcome−
Treatment      a         b
Control        c         d
```

**95% CI**:
- SE(log OR) = sqrt(1/a + 1/b + 1/c + 1/d)
- 95% CI for log OR = log(OR) ± 1.96 · SE
- 95% CI for OR = exp(log OR ± 1.96 · SE)

**Risk difference** = a/(a+b) − c/(c+d). Often more interpretable than OR; report both.

**Caveat**: if any cell has 0, add 0.5 to all cells (Haldane-Anscombe correction) or use Fisher's exact and report the exact OR.

## Categorical > 2×2

**Cramer's V** = sqrt( chi-squared / (n · min(rows−1, cols−1)) )

Range: [0, 1].

## Paired binary (McNemar)

For the 2×2 paired table of (test1, test2) outcomes:
```
                test2 +    test2 −
test1 +          a         b
test1 −          c         d
```

**Odds ratio from discordant pairs** = b / c

Only b and c (the discordant pairs) inform the test; a and d (concordant) drop out.

**95% CI**: SE(log b/c) = sqrt(1/b + 1/c); exp(log OR ± 1.96 · SE).

## ANOVA

**Partial eta-squared** = SS_effect / (SS_effect + SS_error)

Range: [0, 1]. Proportion of variance in the dependent variable attributable to the effect, after removing variance from other factors.

**Omega-squared** (less biased): more conservative; preferred for small samples.

**95% CI**: bootstrap.

## Linear regression

**Adjusted R-squared** for the overall model:
R²_adj = 1 − (1 − R²) · (n − 1) / (n − p − 1)

Where p = number of predictors. Always prefer adjusted over plain R² when there are multiple predictors.

**Standardized beta** per coefficient: β_std = β · (SD_x / SD_y). Compare coefficient magnitudes across different-scaled predictors.

**95% CI**: per-coefficient CIs from the regression output; for R² use bootstrap.

## Library functions

- Python: `pingouin.compute_esci(stat=...)`, `scipy.stats`, `statsmodels.stats.proportion`
- R: `effectsize` package, `compute.es`, `psych::cohen.d`
- Both: bootstrap with `arch.bootstrap`, `scipy.stats.bootstrap`, or `boot::boot`

## When the library is not available

The non-central t closed-form for Cohen's d 95% CI is in Cumming 2012 ("Understanding the New Statistics", chapter 13). For everything else, bootstrap n_bootstrap ≥ 1000 with a percentile CI is the safe default.
