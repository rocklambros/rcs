---
name: analyzing-regression-diagnostics
description: >
  Runs the standard diagnostic battery on a fitted linear or generalized linear
  regression model — linearity (residuals vs fitted), Normality of residuals
  (QQ-plot + Shapiro / Anderson-Darling), homoscedasticity (Breusch-Pagan or
  White, residuals-vs-fitted spread), autocorrelation (Durbin-Watson),
  leverage and Cook's distance for influential observations, and
  multicollinearity (VIF). Reports a per-diagnostic verdict with the
  consequence if the diagnostic fails and a routed remediation. Use whenever a
  linear / OLS / GLS / GLM regression has been fit and inference, confidence
  intervals, or coefficient interpretation are about to be reported, or the
  user asks 'are my regression diagnostics OK?'.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, stats-student, instructor]
evidence:
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4441-Final
last-updated: 2026-05-23
---

# Analyzing Regression Diagnostics

## When to use

Trigger this skill when the user asks for or implies one of:

- A linear, OLS, GLS, ridge, lasso, or GLM regression has just been fit and the user is about to report coefficients, p-values, or confidence intervals
- Residual diagnostics are needed — "check my residuals", "is the fit OK?", "are there influential points?"
- A regression has surprising results (a sign flip, an SE far larger than expected) and the user wants to investigate
- The user reports R² alone and asks whether the regression is trustworthy
- Phrases like "Cook's D", "leverage", "heteroscedasticity", "QQ-plot of residuals", "residuals vs fitted", "Durbin-Watson", "VIF"

This skill pairs with `ml-datasci/evaluating-regression-models` — that skill measures predictive performance; this one audits inferential validity (the assumptions that p-values, CIs, and coefficient interpretation depend on).

## When NOT to use

Skip this skill and hand off when:

- The model is a **non-linear / tree / kernel / neural** model (random forest, gradient boosting, XGBoost, MLP, CNN, transformer) — none of these residual diagnostics apply. Use `ml-datasci/evaluating-regression-models` for predictive scoring or `ml-datasci/auditing-deep-learning-overfit` (planned) for deep models.
- The regression has **not yet been fit** — assumption checks BEFORE fitting belong in `ml-datasci/checking-test-assumptions`
- The user is doing **pure prediction** with no coefficient interpretation, no p-values, no CIs — diagnostics are about inferential validity; prediction-only workflows care about hold-out RMSE / MAE, not Cook's D
- The model is **Bayesian** — posterior-predictive checks and R-hat / ESS replace classical residual diagnostics

## Quick start

User says: "I fit a multiple linear regression on bike-share demand from 8 features. R² = 0.78. Run the diagnostics."

Skill response: walks the 6-step diagnostic checklist (linearity, residual Normality, homoscedasticity, autocorrelation, leverage / influence, multicollinearity), produces the per-diagnostic verdict table (Diagnostic · Test · Statistic · p-value · Verdict · Consequence-if-fail), and routes each failure to the appropriate remediation (transform, robust SE, GLS, drop predictor, refit with influential point removed and report both, etc.).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| model_family | "ols" \| "gls" \| "ridge" \| "lasso" \| "glm-gaussian" \| "glm-binomial" \| "glm-poisson" | yes | — | The fitted regression family; selects which diagnostics apply and which thresholds to use. |
| data | data path or fitted model object | yes | — | The data or the fitted model (so the skill can compute residuals, leverage, Cook's D). |
| n | integer | yes | — | Sample size; drives the Cook's-D `4/n` cutoff and small-n Normality test choice. |
| p | integer | yes | — | Number of predictors; drives VIF interpretation and the leverage `2(p+1)/n` cutoff. |
| time_index | column name | no | — | If present, run Durbin-Watson and inspect residual autocorrelation (only meaningful for time-ordered data). |
| influential_action | "report-both" \| "drop-and-justify" \| "keep" | no | "report-both" | What to do if Cook's D flags a point — the default forces reporting both with and without the point, never silent removal. |

## Workflow

Copy this checklist into the response and check items off as each diagnostic runs:

```
Regression-diagnostic progress:
- [ ] Step 1: Linearity — residuals vs fitted plot inspection
- [ ] Step 2: Normality of residuals — QQ-plot + Shapiro-Wilk (n ≤ 50) or Anderson-Darling (n > 50)
- [ ] Step 3: Homoscedasticity — Breusch-Pagan or White test + residuals-vs-fitted spread
- [ ] Step 4: Independence — Durbin-Watson (time-ordered data only)
- [ ] Step 5: Influence — leverage + Cook's distance (flag any D > 4/n; investigate any D > 1)
- [ ] Step 6: Multicollinearity — VIF per predictor (flag VIF > 5; severe at > 10)
- [ ] Per-diagnostic verdict table + per-failure remediation + final recommendation
```

### Step 1: Linearity (residuals vs fitted)

Plot residuals vs fitted values. Expect a flat band centered at 0 with no systematic curvature.

- Visible **U-shape or inverted-U** → linearity violated; add a polynomial term, log-transform a predictor, or fit a GAM
- Visible **fan / cone** (spread changes with fitted value) → heteroscedasticity, not linearity; route to Step 3
- Visible **clusters or gaps** → consider a missing categorical or an interaction

### Step 2: Normality of residuals

QQ-plot is the primary visual; pair with a hypothesis test:

| n | Test | Reject Normality if |
|---|---|---|
| ≤ 50 | Shapiro-Wilk | p < 0.05 |
| > 50 | Anderson-Darling | A² > critical value (typically p < 0.05) |
| any | QQ-plot | Visible S-shape, heavy tails, or curvature |

If Normality fails:
- **Mild deviation, large n** → rely on CLT for SE; report robustly (HC1/HC3 SE)
- **Severe deviation** → log / sqrt / Box-Cox transform on Y; or switch to a GLM with the right family (e.g., Poisson for counts, gamma for positive skewed)

### Step 3: Homoscedasticity

Two evidence streams: a hypothesis test (Breusch-Pagan or White) plus the residuals-vs-fitted spread.

| Test | When | Reject equal-variance if |
|---|---|---|
| Breusch-Pagan | Linear OLS | p < 0.05 |
| White | Mixed linear + non-linear effects | p < 0.05 |
| Goldfeld-Quandt | Suspect specific high-variance group | p < 0.05 |

If heteroscedasticity is present, the OLS point estimates are still unbiased but the SEs are wrong. Remediation:

- **Heteroscedasticity-consistent SE**: HC1 (sandwich), HC3 (preferred for small n) — keep the OLS estimates, replace SEs
- **Weighted least squares (WLS)**: if you can model the variance structure
- **GLS**: full generalized least squares if both autocorrelation and heteroscedasticity are present

### Step 4: Independence (time-ordered data only)

Durbin-Watson:

| DW value | Interpretation |
|---|---|
| ≈ 2.0 | No autocorrelation |
| < 1.5 | Positive autocorrelation (common in time series) |
| > 2.5 | Negative autocorrelation (rarer; check for over-differencing) |

If autocorrelation is present: include a lagged-Y term, fit with HAC (Newey-West) SE, or switch to a time-series model (ARIMA, GLS-AR1).

Do NOT run Durbin-Watson on non-time-ordered cross-sectional data; the test assumes a meaningful ordering.

### Step 5: Influence (leverage + Cook's distance)

Two complementary measures:

- **Leverage (`h_ii`)**: how unusual the *predictors* are for observation `i`. Flag any `h_ii > 2(p+1)/n`.
- **Cook's distance (`D_i`)**: how much the fitted coefficients would change if observation `i` were removed. Flag any `D_i > 4/n`; **highly influential** if `D_i > 1`.

Routing per the `influential_action` flag:

- `report-both` (default): refit without the flagged observations, report both regressions, let the reader judge
- `drop-and-justify`: drop only if you can name a substantive reason (data-entry error, off-protocol case); document it
- `keep`: keep all observations, but note in the writeup that observation `i` drives result X

**Never silently drop influential observations.**

### Step 6: Multicollinearity (VIF)

For each predictor, compute VIF = 1 / (1 - R²_predictor), where R²_predictor comes from regressing that predictor on all the others.

| VIF | Verdict |
|---|---|
| < 5 | OK |
| 5–10 | Concerning — inspect; consider dropping or combining |
| > 10 | Severe — drop one of the correlated predictors, or use ridge regression, or combine via PCA |

Multicollinearity does NOT bias OLS estimates, but it inflates SEs and makes individual coefficient interpretation unreliable. For prediction-only work this is less critical; for inference it is decisive.

## Outputs

A short markdown report:

1. **Model summary** — family, n, p, R² and adjusted-R²
2. **Per-diagnostic verdict table**: Diagnostic · Test · Statistic · p-value (if applicable) · Verdict (pass / warn / fail) · Consequence if fail
3. **Failure list** — one row per fail or warn with the recommended remediation
4. **Refit comparisons** — if any high-influence points or remediations were applied, side-by-side coefficient table (with vs without the change)
5. **Reporting checklist** — what to put in the methods / results section (which SE flavor, which transforms, which influence diagnostics ran)

## Failure modes

- **Skipping diagnostics on a "good R²" model** — believing R² = 0.85 means the assumptions are met. Caught by: this skill is triggered by the *act of reporting coefficients / CIs*, not by R² value; the workflow runs regardless of R².
- **Silently dropping high-Cook's-D observations** — refitting without observation 42 because "it was throwing off the regression." Caught by: Step 5 default `influential_action = "report-both"` forces reporting both regressions.
- **Reporting OLS SEs under heteroscedasticity** — the point estimate is fine but the p-values and CIs are wrong. Caught by: Step 3 fail explicitly routes to HC1 / HC3 robust SE.
- **Running Durbin-Watson on cross-sectional data** — the test assumes ordering; cross-sectional data has no meaningful order and DW values become noise. Caught by: Step 4 gated on the `time_index` argument; absent it, Durbin-Watson is skipped.
- **Treating VIF > 5 as a death sentence for prediction work** — multicollinearity does not bias point estimates; for pure prediction, high VIF is tolerable. Caught by: Step 6's verdict table notes the prediction-vs-inference distinction.
- **Reporting "diagnostics OK" with no evidence** — a one-line "assumptions met" sentence with no table. Caught by: the per-diagnostic verdict table is required output; verdicts without statistics are not acceptable.

## References

- [`reference/diagnostics-cookbook.md`](reference/diagnostics-cookbook.md) — per-diagnostic Python (statsmodels) + R (base / car) code snippets and thresholds
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for the workflow-checklist pattern
- Belsley, Kuh & Welsch, *Regression Diagnostics: Identifying Influential Data and Sources of Collinearity* (Wiley, 1980) — origin of leverage and Cook's D thresholds
- Fox, *Applied Regression Analysis and Generalized Linear Models* — chapter on residual diagnostics and remediations

## Examples

### Example 1: OLS with heteroscedasticity (happy-path)

Input: "I fit a multiple linear regression of house price on 6 features (size, bedrooms, bathrooms, age, lot_size, neighborhood-fixed-effects). n = 240, R² = 0.71. Residuals vs fitted shows a clear fan pattern (spread grows with price). Run the diagnostics."

Output: Per-diagnostic table — Linearity: pass (no curvature); Normality: warn (Shapiro p = 0.04, mild right tail on QQ-plot, n = 240 means CLT applies but flag); Homoscedasticity: **fail** (Breusch-Pagan p < 0.001; fan pattern confirmed); Independence: skipped (no `time_index`); Influence: 3 observations with Cook's D > 4/n = 0.017, none > 1 → flag and refit; Multicollinearity: VIF all < 3 → pass. Remediation: switch to **HC3 robust SE**; refit and report both with and without the 3 flagged observations; consider a log-transform on price (right-skewed Y is consistent with the fan pattern).

### Example 2: High-leverage outlier (edge-case)

Input: "Cook's D for one observation is 1.4, all others are below 0.05. n = 80, p = 3. Should I just drop it?"

Output: Cook's D = 1.4 with all others ≤ 0.05 is **highly influential**. Default action is NOT to silently drop. Recommend: (1) inspect the observation — is it a data-entry error? An out-of-scope case (different population)? A genuine but rare event? (2) refit without the observation and report BOTH regressions side-by-side; let the reader see which coefficients change and by how much; (3) if you have a substantive justification (e.g., the observation is a duplicate of another or measured under different conditions), document it and drop with justification; otherwise keep and note. The skill produces a side-by-side coefficient table for the with-vs-without refit.

### Example 3: Random forest model (anti-trigger)

Input: "I trained a random forest regressor with 500 trees on the same dataset. R² = 0.84. Run the regression diagnostics."

Output: Random forest is non-linear and ensemble-based; residual Normality, homoscedasticity, leverage, Cook's D, and VIF do not apply (no coefficients to be biased; SE-of-coefficient is not defined). Skill hands off: for performance scoring use `ml-datasci/evaluating-regression-models` (RMSE / MAE / R² with CV); for feature-importance interpretation use SHAP or permutation importance, not classical regression diagnostics. The skill does NOT pretend to compute Cook's D for a tree ensemble.

## See also

- `ml-datasci/evaluating-regression-models` — predictive scoring (RMSE / MAE / R²) for any regression model, including non-linear
- `ml-datasci/checking-test-assumptions` — pre-fit assumption checks for parametric tests (t / ANOVA / linear-regression)
- `ml-datasci/reporting-effect-sizes` — once diagnostics pass, pair with the right effect size (adj-R², partial η²) for reporting
- `workflow/auditing-mathematical-claims` — for the theoretical-claim variant when the regression is presented as evidence for a stronger formal claim

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
