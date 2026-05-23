# Power-analysis cookbook

Per-test Python (statsmodels) + R (pwr) code snippets with worked examples.

## Two-sample t (independent)

**Python:**

```python
from statsmodels.stats.power import TTestIndPower
analysis = TTestIndPower()
# Solve for n per group
n = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.80, alternative="two-sided")
# Solve for power
power = analysis.solve_power(effect_size=0.5, alpha=0.05, nobs1=64, alternative="two-sided")
# Solve for MDE
d = analysis.solve_power(nobs1=50, alpha=0.05, power=0.80, alternative="two-sided")
```

**R:**

```r
pwr::pwr.t.test(d = 0.5, sig.level = 0.05, power = 0.80,
                type = "two.sample", alternative = "two.sided")
```

Effect-size = Cohen's d = (μ₁ − μ₂) / σ_pooled.

## Paired t

**Python:**

```python
from statsmodels.stats.power import TTestPower
analysis = TTestPower()
n = analysis.solve_power(effect_size=0.4, alpha=0.05, power=0.80, alternative="two-sided")
```

**R:**

```r
pwr::pwr.t.test(d = 0.4, sig.level = 0.05, power = 0.80,
                type = "paired", alternative = "two.sided")
```

Effect-size = Cohen's dz = mean_difference / SD_of_differences. Note: dz is on the difference scale and is typically smaller than the between-subject d unless the within-pair correlation is high.

## One-way ANOVA

**Python:**

```python
from statsmodels.stats.power import FTestAnovaPower
analysis = FTestAnovaPower()
n_total = analysis.solve_power(effect_size=0.25, alpha=0.05, power=0.80, k_groups=3)
# n per group = n_total / k_groups
```

**R:**

```r
pwr::pwr.anova.test(k = 3, f = 0.25, sig.level = 0.05, power = 0.80)
```

Effect-size = Cohen's f = sqrt(η² / (1 − η²)).

## Chi-squared

**Python:**

```python
from statsmodels.stats.power import GofChisquarePower, NormalIndPower
gof = GofChisquarePower()
n = gof.solve_power(effect_size=0.30, alpha=0.05, power=0.80, n_bins=4)
```

**R:**

```r
pwr::pwr.chisq.test(w = 0.30, df = 3, sig.level = 0.05, power = 0.80)
```

Effect-size = Cohen's w = sqrt(Σ (p_observed − p_expected)² / p_expected).

## Correlation

**R (most convenient):**

```r
pwr::pwr.r.test(r = 0.30, sig.level = 0.05, power = 0.80, alternative = "two.sided")
```

**Python (via Fisher z-transform):**

```python
import math
from scipy.stats import norm
def n_for_correlation(r, alpha, power, tails=2):
    z_r = 0.5 * math.log((1 + r) / (1 - r))
    z_alpha = norm.ppf(1 - alpha / tails)
    z_beta = norm.ppf(power)
    n = ((z_alpha + z_beta) / z_r) ** 2 + 3
    return n
n = n_for_correlation(0.30, 0.05, 0.80)
```

## Logistic regression

**Python (via simulation; recommended for non-trivial designs):**

```python
import numpy as np
import statsmodels.api as sm

def simulate_logistic_power(n_per_group, p0, p1, alpha=0.05, n_sims=2000, seed=42):
    rng = np.random.default_rng(seed)
    rejections = 0
    for _ in range(n_sims):
        x = np.concatenate([np.zeros(n_per_group), np.ones(n_per_group)])
        y = rng.binomial(1, np.where(x == 0, p0, p1))
        X = sm.add_constant(x)
        try:
            r = sm.Logit(y, X).fit(disp=0)
            if r.pvalues[1] < alpha:
                rejections += 1
        except Exception:
            pass
    return rejections / n_sims
power = simulate_logistic_power(n_per_group=100, p0=0.10, p1=0.18)
```

Rule of thumb: 10–20 events per predictor is a separate constraint regardless of the power calc.

## Linear regression: added predictor

**R:**

```r
pwr::pwr.f2.test(u = 1, f2 = 0.15, sig.level = 0.05, power = 0.80)
# u = numerator df = number of predictors being tested
# f² = R²_added / (1 − R²_full)
```

Cohen f² conventions: 0.02 small, 0.15 medium, 0.35 large.

## McNemar (paired binary)

**R:**

```r
# Effect via p_disagree-up vs p_disagree-down
# Use the discordant-pair proportions
pwr::pwr.p.test(h = ES.h(0.20, 0.05), sig.level = 0.05, power = 0.80)
# h is Cohen's h = 2·(arcsin(√p1) − arcsin(√p2))
```

## Sensitivity analysis pattern

For any test, repeat the calc at 0.75× and 1.25× the planned effect-size:

```python
analysis = TTestIndPower()
for mult in [0.75, 1.0, 1.25]:
    n = analysis.solve_power(effect_size=0.417 * mult, alpha=0.05, power=0.80)
    print(f"d = {0.417 * mult:.3f}: n = {n:.0f} per arm")
```

## TOST equivalence test (use INSTEAD of post-hoc power)

**Python (statsmodels):**

```python
from statsmodels.stats.weightstats import ttost_ind
# Pre-specify equivalence bounds in standardized units
# Or in raw units via the low / upp arguments
p_value, _, _ = ttost_ind(group1, group2, low=-3, upp=3, usevar="pooled")
```

**R:**

```r
TOSTER::tsum_TOST(m1 = 5.2, m2 = 3.8, sd1 = 4.1, sd2 = 4.0, n1 = 40, n2 = 40,
                  low_eqbound = -1, high_eqbound = 1, eqbound_type = "raw")
```

If both one-sided tests reject, conclude "effect is bounded inside the equivalence region." This is the right tool when the user wants to interpret a non-significant result, NOT observed power.

## Reporting checklist

In the methods section, document:

1. Test family + design (paired / independent / one-sample)
2. α, β, tails
3. Effect-size value AND provenance (pilot / literature / SESOI / Cohen rule-of-thumb)
4. Software + version (statsmodels 0.14 / pwr 1.3.0 / G*Power 3.1.9.7)
5. Sensitivity result (n at ± 25% effect-size)
6. Assumptions you are relying on (Normality, equal variance, etc.)
