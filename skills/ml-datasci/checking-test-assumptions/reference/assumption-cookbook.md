# Assumption checking cookbook

Per-test cards. Each card lists the required assumptions, the recommended check, the threshold, and the consequence if the assumption fails.

## One-sample t-test

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Normality of the sample | Shapiro-Wilk (n ≤ 50), Anderson-Darling (n > 50), QQ-plot always | p < 0.05 → reject Normality | Wilcoxon signed-rank vs known median, or Sign test |
| Independence | Study-design check | (not testable from data) | Cluster-robust or paired design instead |

## Paired t-test

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Normality of the **differences** (`after − before`) | Shapiro-Wilk on the differences | p < 0.05 → reject Normality | Wilcoxon signed-rank on the differences |
| Independence of pairs | Study-design check | (not testable from data) | Mixed-effects model with subject random effect |

**Gotcha:** Shapiro-test the differences, NOT the raw before and raw after columns.

## Pooled (Student) two-sample t-test

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Normality per group | Shapiro-Wilk per group | any p < 0.05 → reject | Mann-Whitney U |
| Equal variance | Levene's test | p < 0.05 → unequal variance | Welch's t-test |
| Independence | Study-design check | (not testable) | Mixed-effects model |

**Why Levene over Bartlett:** Bartlett assumes Normality, Levene doesn't. If you're already worried about Normality, Bartlett's result is suspect.

## Welch's t-test

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Normality per group | Shapiro-Wilk per group | any p < 0.05 → reject | Mann-Whitney U |
| Independence | Study-design check | (not testable) | Mixed-effects model |

**Note:** Welch's does NOT require equal variance — that's the whole point. Default to Welch over pooled when in doubt.

## One-way ANOVA

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Normality per group | Shapiro-Wilk per group; or residuals after the fit | any p < 0.05 → reject | Kruskal-Wallis |
| Homoscedasticity (equal variance) | Levene's test or Brown-Forsythe | p < 0.05 → unequal | Welch's ANOVA OR Kruskal-Wallis |
| Independence | Study-design check | (not testable) | Mixed-effects model |

## Repeated-measures ANOVA

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Normality of residuals | Shapiro-Wilk on residuals + QQ-plot | p < 0.05 → reject | Friedman test |
| **Sphericity** | Mauchly's test | p < 0.05 → violated | Greenhouse-Geisser correction (conservative) or Huynh-Feldt (less conservative) |
| Independence of subjects | Study-design check | (not testable) | Crossed random-effects model |

## Linear regression

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Linearity (in parameters) | Residuals-vs-fitted plot, component-plus-residual plot | Visible curvature → non-linear | Polynomial terms, splines, or non-linear model |
| Normality of **residuals** | Shapiro on residuals + QQ-plot | p < 0.05 or visible deviation → reject | Transform Y (log / sqrt), use GLM with appropriate family, or robust regression |
| Homoscedasticity of residuals | Breusch-Pagan test + residuals-vs-fitted plot | p < 0.05 OR funnel shape → heteroscedasticity | Use heteroscedasticity-consistent SE (HC1, HC3); or weighted least squares |
| Independence (no autocorrelation) | Durbin-Watson; ACF / PACF plots if time-indexed | DW < 1.5 or > 2.5 → autocorrelation | Generalized least squares, or HAC SE (Newey-West), or include lagged term |
| No influential outliers | Cook's distance, leverage | Cook's D > 1 → highly influential; > 4/n → flag | Investigate (not silently drop); robust regression as a sensitivity analysis |
| No multicollinearity | Variance Inflation Factor (VIF) | VIF > 5 → concerning; > 10 → severe | Drop one of the correlated predictors; ridge regression; PCA |

## Logistic regression

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Linearity **in the logit** | Box-Tidwell test; or empirical logit plot per predictor | Significant non-linearity → violated | Transform the predictor, or add a spline term |
| Independence | Study-design check | (not testable from data) | GLMM with random effect |
| No separation (perfect prediction) | Inspect fit; coefficients exploding to ±∞ | Coefficient SEs explode | Penalized logistic (Firth, ridge); drop the separating predictor |
| No multicollinearity | VIF (on the design matrix) | VIF > 10 → severe | Drop / combine predictors |
| Adequate events per predictor | Count events / predictors | < 10 → unstable; < 5 → unreliable | Reduce predictors, regularize, or collect more data |

## Chi-squared test of independence

| Assumption | Check | Threshold | If fail |
|---|---|---|---|
| Independence | Study-design check | (not testable) | McNemar (paired) or mixed-effects logistic |
| Expected counts (2x2) | Compute `E_ij = (row_i × col_j) / N` for all 4 cells | Any cell < 5 → violated | Fisher's exact test |
| Expected counts (larger tables) | Compute all E_ij | > 20% of cells < 5, or any cell < 1 → violated | Fisher-Freeman-Halton, or Monte-Carlo p-value, or collapse categories |

## Common misuses to flag

- Shapiro on the **raw paired columns** instead of the **differences**
- Using Bartlett's when Levene is more appropriate
- Running chi-squared on a sparse 2x2 without computing expected counts
- Ignoring sphericity for repeated-measures ANOVA
- Reporting "assumptions met" without the statistic + p-value
- Treating CLT as a license to skip the Normality check at n = 30
- Dropping influential observations silently to make the fit nicer

## Code snippets (reference patterns; not auto-runnable from the skill)

### Python / SciPy + statsmodels

```python
from scipy.stats import shapiro, levene, fisher_exact
import statsmodels.api as sm

# Shapiro on the differences for paired-t
diffs = after - before
W, p = shapiro(diffs)

# Levene's for equal variance
F, p = levene(group_a, group_b, center='median')  # Brown-Forsythe variant

# Cook's distance after linear regression
influence = model.get_influence()
cooks_d = influence.cooks_distance[0]
flagged = cooks_d > 1.0
```

### R

```r
shapiro.test(after - before)           # paired-t differences
car::leveneTest(y ~ group)             # equal variance
fisher.test(matrix(c(3, 7, 8, 12), nrow=2))  # sparse 2x2
cooks.distance(lm_model) > 1            # influence
performance::check_model(lm_model)      # one-call regression diagnostics
```
