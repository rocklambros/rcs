# Regression diagnostics cookbook

Per-diagnostic code snippets and thresholds. Pair with the SKILL.md workflow.

## Step 1: Linearity (residuals vs fitted)

**Python (statsmodels):**

```python
import statsmodels.api as sm
import matplotlib.pyplot as plt

fitted = result.fittedvalues
resid = result.resid
plt.scatter(fitted, resid)
plt.axhline(0, color="red")
plt.xlabel("Fitted values")
plt.ylabel("Residuals")
plt.title("Residuals vs Fitted")
```

**R (base):**

```r
plot(fitted(model), resid(model))
abline(h = 0, col = "red")
```

**Visual interpretation:**

- Flat band centered at 0 → linearity OK
- U-shape or inverted-U → missing polynomial term or wrong link function
- Fan / cone → heteroscedasticity (route to Step 3, not Step 1)

## Step 2: Normality of residuals

**Python:**

```python
from scipy.stats import shapiro, anderson
import statsmodels.api as sm

# QQ-plot
sm.qqplot(resid, line="45")

# Hypothesis test
if len(resid) <= 50:
    stat, p = shapiro(resid)
    print(f"Shapiro-Wilk: W = {stat:.4f}, p = {p:.4f}")
else:
    result = anderson(resid, dist="norm")
    print(f"Anderson-Darling: A² = {result.statistic:.4f}")
    print(f"Critical values: {result.critical_values}")
```

**R:**

```r
qqnorm(resid(model)); qqline(resid(model))
shapiro.test(resid(model))           # n <= 5000
nortest::ad.test(resid(model))       # any n
```

**Thresholds:**

| n | Test | Reject Normality if |
|---|---|---|
| ≤ 50 | Shapiro-Wilk | p < 0.05 |
| > 50 | Anderson-Darling | A² > critical at α = 0.05 |
| any | QQ-plot | Visible S-shape, heavy tails |

## Step 3: Homoscedasticity

**Python (statsmodels):**

```python
from statsmodels.stats.diagnostic import het_breuschpagan, het_white

bp_lm, bp_lm_p, bp_f, bp_f_p = het_breuschpagan(resid, result.model.exog)
print(f"Breusch-Pagan: LM = {bp_lm:.4f}, p = {bp_lm_p:.4f}")

w_lm, w_lm_p, w_f, w_f_p = het_white(resid, result.model.exog)
print(f"White: LM = {w_lm:.4f}, p = {w_lm_p:.4f}")
```

**R:**

```r
lmtest::bptest(model)        # Breusch-Pagan
car::ncvTest(model)          # non-constant-variance test
```

**Remediation if fail:**

```python
# HC3 robust SE (preferred for small n)
robust_result = result.get_robustcov_results(cov_type="HC3")
print(robust_result.summary())
```

```r
# R: HC3 robust SE via sandwich + lmtest
library(sandwich); library(lmtest)
coeftest(model, vcov = vcovHC(model, type = "HC3"))
```

## Step 4: Independence (Durbin-Watson, time-ordered only)

**Python:**

```python
from statsmodels.stats.stattools import durbin_watson
dw = durbin_watson(resid)
print(f"Durbin-Watson: {dw:.3f}")
```

**R:**

```r
lmtest::dwtest(model)
```

**Interpretation:**

| DW | Interpretation |
|---|---|
| ≈ 2.0 | No autocorrelation |
| < 1.5 | Positive autocorrelation |
| > 2.5 | Negative autocorrelation |

**Remediation: HAC (Newey-West) SE:**

```python
result.get_robustcov_results(cov_type="HAC", maxlags=2)
```

```r
coeftest(model, vcov = NeweyWest(model, lag = 2))
```

## Step 5: Influence (leverage + Cook's D)

**Python:**

```python
influence = result.get_influence()
leverage = influence.hat_matrix_diag
cooks_d = influence.cooks_distance[0]

n = len(resid)
p = result.df_model
leverage_cutoff = 2 * (p + 1) / n
cooks_cutoff = 4 / n

flagged = [(i, l, c) for i, (l, c) in enumerate(zip(leverage, cooks_d))
           if l > leverage_cutoff or c > cooks_cutoff]
high_influence = [(i, c) for i, c in enumerate(cooks_d) if c > 1.0]
```

**R:**

```r
influence_data <- influence.measures(model)
cooks <- cooks.distance(model)
high_cooks <- which(cooks > 4 / nrow(data))
very_high <- which(cooks > 1)
```

**Action thresholds:**

| Cook's D | Verdict | Action |
|---|---|---|
| ≤ 4/n | OK | None |
| > 4/n and ≤ 1 | Flag | Investigate; refit + report-both |
| > 1 | Highly influential | Investigate; refit + report-both; do not silently drop |

## Step 6: Multicollinearity (VIF)

**Python (statsmodels):**

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
X = result.model.exog
vifs = [variance_inflation_factor(X, i) for i in range(X.shape[1])]
```

**R:**

```r
car::vif(model)
```

**Thresholds:**

| VIF | Verdict |
|---|---|
| < 5 | OK |
| 5–10 | Concerning — inspect |
| > 10 | Severe — drop, ridge, or PCA |

## Combined diagnostic call

For Python, statsmodels provides a one-stop summary:

```python
print(result.summary())   # Includes Durbin-Watson, condition number (VIF proxy), Jarque-Bera (Normality)
```

For R, the `car::residualPlots` and `gvlma` packages bundle several diagnostics.

These convenience calls are fine for an overview, but produce the per-diagnostic verdict table from the skill workflow — the individual tests + their interpretations are what the verdict table requires.
