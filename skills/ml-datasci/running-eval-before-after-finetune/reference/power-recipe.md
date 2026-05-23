# Power-check recipes — paired before/after fine-tune

This reference documents the power-computation recipes invoked by Step 5 of `running-eval-before-after-finetune`. Each metric_family has a slightly different formulation. Both an analytic recipe and a simulation recipe are documented; the simulation recipe is the safer fallback when the analytic assumptions are uncertain.

## Concepts

- **MDE (minimum detectable effect)** — the smallest effect size the user cares to detect. Below the MDE, "no significant difference" is not interesting (the user does not care about effects smaller than the MDE).
- **Achieved power at observed effect** — given the observed effect size and the eval size, what fraction of the time would a re-run detect this effect? If < 0.8, the eval is underpowered for the observed effect; the "p > alpha" finding is not informative.
- **Power-at-MDE** — given the eval size, what fraction of the time would a re-run detect an effect of size MDE? Use this *before* running the eval to size it.

The skill's Step 5 reports both: achieved power at the observed effect (always), and power-at-MDE if `minimum_detectable_effect` was supplied.

## paired-binary (McNemar)

**Analytic recipe** (normal approximation, valid when expected discordant count is not tiny):

Given observed discordance rate `p_d = (b + c) / n`, the McNemar test's power to detect a true `Δaccuracy = (c - b) / n = δ` at significance `α` and sample size `n` is approximately:

```
SE_under_null = sqrt(p_d / n)
SE_under_alt  = sqrt((p_d - δ²) / n)         # approximation
z_alpha = Φ⁻¹(1 - α/2)                        # two-sided
power = 1 - Φ((z_alpha * SE_under_null - δ) / SE_under_alt)
```

Implementation: `statsmodels.stats.contingency_tables.mcnemar` doesn't include power directly; use `statsmodels.stats.proportion.power_proportions_2indep` adapted for the paired-proportion test, OR use the simulation recipe below.

**Simulation recipe** (preferred when discordant count is small or skewed):

```python
import numpy as np
from scipy.stats import binomtest

def simulate_mcnemar_power(p_d, delta, n, alpha=0.05, n_sims=5000, seed=0):
    rng = np.random.default_rng(seed)
    # Under the alternative: per-row probability of being discordant = p_d,
    # given discordant, P(c) = 0.5 + delta / (2 * p_d)
    p_c_given_discord = 0.5 + delta / (2 * p_d)
    rejections = 0
    for _ in range(n_sims):
        discord_count = rng.binomial(n, p_d)
        c = rng.binomial(discord_count, p_c_given_discord)
        b = discord_count - c
        if b + c < 25:
            # exact binomial McNemar
            p = binomtest(c, b + c, p=0.5).pvalue
        else:
            # continuity-corrected
            chi2 = (abs(c - b) - 1) ** 2 / (b + c)
            from scipy.stats import chi2 as chi2_dist
            p = 1 - chi2_dist.cdf(chi2, df=1)
        if p < alpha:
            rejections += 1
    return rejections / n_sims
```

Run for the observed `p_d` and a range of `delta` values to produce the power-curve plot.

## paired-continuous (paired-t or Wilcoxon)

**Analytic recipe (paired-t)** — `statsmodels.stats.power.tt_solve_power`:

```python
from statsmodels.stats.power import tt_solve_power

# Effect size dz = mean(d) / sd(d)
# Compute observed dz, or use MDE expressed as dz
power = tt_solve_power(effect_size=dz, nobs=n, alpha=0.05, alternative='two-sided')
```

For Wilcoxon, there is no clean closed-form; use a simulation recipe with the empirical distribution of per-row differences (resample with replacement, recompute the test, count rejections).

**Simulation recipe (Wilcoxon)**:

```python
import numpy as np
from scipy.stats import wilcoxon

def simulate_wilcoxon_power(observed_diffs, mde_shift, n, alpha=0.05, n_sims=5000, seed=0):
    rng = np.random.default_rng(seed)
    rejections = 0
    for _ in range(n_sims):
        # Resample with replacement, shift by the MDE to construct the alternative
        sample = rng.choice(observed_diffs, size=n, replace=True) + mde_shift
        _, p = wilcoxon(sample, alternative='two-sided')
        if p < alpha:
            rejections += 1
    return rejections / n_sims
```

## paired-multi-checkpoint (Cochran's Q / Friedman)

Power for K-sample paired tests is rarely closed-form; the simulation recipe generalizes the per-pair pattern above across K columns of per-row outcomes. Document the assumed pairwise effects and resample within rows to preserve the paired structure.

## When the power-check matters most

- **Small eval sets (n < 200)** — almost any "no significant difference" finding is underpowered for effects under MDE = 5 percentage points
- **Skewed discordance** (`p_d < 0.1` in paired-binary) — most rows are concordant; the effective sample size for the test is `b + c`, not `n`
- **Heavy-tailed continuous metrics** — paired-t's power calculation is wrong; use the Wilcoxon simulation recipe
- **Multi-checkpoint families** — power per pairwise comparison drops as the family grows (Holm correction tightens the per-test alpha)

## Pre-eval sizing guide

Before running an eval against a fine-tune candidate, use this to choose `n`:

| Test family | Want to detect MDE | Want power | Target n (rough) |
|---|---|---|---|
| McNemar at p_d = 0.20 | 2 pp Δaccuracy | 0.80 | ~1500 |
| McNemar at p_d = 0.20 | 5 pp Δaccuracy | 0.80 | ~250 |
| McNemar at p_d = 0.10 | 5 pp Δaccuracy | 0.80 | ~500 |
| paired-t | dz = 0.10 | 0.80 | ~785 |
| paired-t | dz = 0.20 | 0.80 | ~199 |
| paired-t | dz = 0.50 | 0.80 | ~34 |

These are rough targets to start the conversation. Re-run the proper power computation with the actual observed `p_d` or `sd(d)` once a pilot is run.
