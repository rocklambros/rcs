# Section cookbook — copy-paste cells per section per stack

Cell snippets for each of the 6 sections, per stack (jupyter-python, jupyter-r, rmarkdown, quarto). Adapt by filling in the TODO markers.

## Section 1 — Header + seed + imports

### Jupyter-Python

Markdown cell:

```markdown
# <COURSE-CODE> — Pset <N>: <title>

**Author:** <name> · **Date:** <YYYY-MM-DD> · **Stack:** jupyter-python

## Questions covered
- Q1: <one-line summary>
- Q2: <one-line summary>
```

Seed cell:

```python
import os
os.environ["PYTHONHASHSEED"] = "42"
import random
import numpy as np
random.seed(42)
np.random.seed(42)
# TODO: add torch / jax / tf seed calls if used by this pset
```

Imports cell:

```python
import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
```

### RMarkdown

YAML header:

```yaml
---
title: "<COURSE-CODE> — Pset <N>: <title>"
author: "<name>"
date: "<YYYY-MM-DD>"
output: html_document
---
```

Setup chunk:

```r
set.seed(42)
library(tidyverse)
library(broom)
library(effsize)  # Cohen's d, Cliff's delta
# library(lme4); library(brms)  # uncomment for mixed / Bayesian models
```

## Section 2 — Data audit

### Jupyter-Python

```python
df = pd.read_csv("TODO-data.csv")  # or read_excel / read_parquet
# Per-column audit
audit = pd.DataFrame({
    "dtype":   df.dtypes.astype(str),
    "n_null":  df.isna().sum(),
    "pct_null": (df.isna().mean() * 100).round(2),
    "n_unique": df.nunique(),
    "min":     df.select_dtypes("number").min(),
    "max":     df.select_dtypes("number").max(),
    "mean":    df.select_dtypes("number").mean().round(3),
    "std":     df.select_dtypes("number").std().round(3),
})
audit
```

Then a markdown cell noting any flagged columns (high null %, suspicious ranges, sentinel values, cardinality alarms).

### RMarkdown

```r
df <- read_csv("TODO-data.csv")
df %>%
  summarise(across(everything(), list(
    n_null = ~sum(is.na(.)),
    pct_null = ~mean(is.na(.)) * 100,
    n_unique = ~n_distinct(.)
  )))
df %>% select(where(is.numeric)) %>% summary()
```

## Section 3 — Assumption checks

### Two-sample t-test (Python)

```python
g1 = df.loc[df["group"] == "treatment", "outcome"]
g2 = df.loc[df["group"] == "control", "outcome"]

print("Shapiro (treatment):", stats.shapiro(g1))
print("Shapiro (control):",   stats.shapiro(g2))
print("Levene equal-variance:", stats.levene(g1, g2))

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
stats.probplot(g1, dist="norm", plot=axes[0]); axes[0].set_title("QQ — treatment")
stats.probplot(g2, dist="norm", plot=axes[1]); axes[1].set_title("QQ — control")
plt.tight_layout(); plt.show()
```

Then a markdown cell with the verdict: "Shapiro treatment p = X (passes / fails Normality), Shapiro control p = Y, Levene p = Z (passes / fails equal-variance). Therefore <decision: t-test / Welch / Mann-Whitney>."

### Paired t-test (Python)

```python
d = df["after"] - df["before"]
print("Shapiro on differences:", stats.shapiro(d))

fig, ax = plt.subplots(figsize=(5, 4))
stats.probplot(d, dist="norm", plot=ax); ax.set_title("QQ — differences")
plt.show()
```

### Chi-squared 2x2 (Python)

```python
contingency = pd.crosstab(df["group"], df["outcome"])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
print("Expected counts:\n", expected)
print("All expected ≥ 5:", (expected >= 5).all())
# If any expected < 5, switch to Fisher exact
```

### OLS regression (Python)

```python
model = smf.ols("y ~ x1 + x2 + C(group)", data=df).fit()
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
# Residuals vs fitted
axes[0].scatter(model.fittedvalues, model.resid)
axes[0].axhline(0, color="red", linestyle="--")
axes[0].set_xlabel("Fitted"); axes[0].set_ylabel("Residuals")
axes[0].set_title("Residuals vs Fitted")
# QQ-plot of residuals
sm.qqplot(model.resid, line="s", ax=axes[1]); axes[1].set_title("QQ — residuals")
# Cook's D
influence = model.get_influence()
axes[2].stem(influence.cooks_distance[0])
axes[2].set_title("Cook's D")
plt.tight_layout(); plt.show()
```

### Bayesian (PyMC)

```python
import pymc as pm
import arviz as az
with pm.Model() as m:
    # TODO: define priors and likelihood
    pass
    idata = pm.sample(2000, tune=1000, target_accept=0.95, random_seed=42)
print(az.summary(idata))
az.plot_trace(idata); plt.show()
# Verdict: R-hat near 1.01, ESS > 400, zero divergences → convergence OK
```

## Section 4 — Tests

Per question part, one cell with the test call. Reference back to Section 3's assumption-check verdict to justify the choice.

```python
# Q1 — two-sample comparison
# Section 3 verdict: Normality OK, equal-variance OK → use pooled-variance t-test
t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=True)
print(f"t = {t_stat:.3f}, p = {p_val:.4f}, df = {len(g1) + len(g2) - 2}")
```

## Section 5 — Effect sizes + 95% CIs

```python
# Cohen's d for two-sample test
def cohens_d(a, b):
    n1, n2 = len(a), len(b)
    s_pooled = np.sqrt(((n1 - 1) * a.var(ddof=1) + (n2 - 1) * b.var(ddof=1)) / (n1 + n2 - 2))
    return (a.mean() - b.mean()) / s_pooled

d = cohens_d(g1, g2)
# Bootstrap CI
rng = np.random.default_rng(42)
boot = [cohens_d(rng.choice(g1, len(g1), replace=True),
                 rng.choice(g2, len(g2), replace=True)) for _ in range(2000)]
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"Cohen's d = {d:.3f} [95% CI: {lo:.3f}, {hi:.3f}]")
```

## Section 6 — Interpretation + conclusion

Markdown cell per question, following the canonical sentence template:

```markdown
**Q1.** The two-sample t-test showed Cohen's d = 0.62 [95% CI: 0.18, 1.07],
direction: the treatment group's mean outcome was higher than control by
4.3 units, n = 30 + 30. This is a medium-sized effect (per Cohen 1988
convention) and the confidence interval excludes zero, supporting the
hypothesis that treatment increases the outcome.

**Q2.** ...
```
