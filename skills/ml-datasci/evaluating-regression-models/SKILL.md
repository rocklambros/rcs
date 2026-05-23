---
name: evaluating-regression-models
description: >
  Produces a complete regression-model evaluation report: RMSE + MAE + R² (with
  adjusted-R² for multi-feature models) + residual plots (residuals vs fitted,
  QQ-plot of residuals, residual histogram) + k-fold cross-validation (mean ±
  SD across folds). Triggers whenever a regression model needs scoring,
  whenever residual diagnostics are needed, whenever only R² is reported
  without RMSE / MAE, or whenever CV is missing. Refuses to report R² alone
  and refuses k-fold CV on time-series data (recommends walk-forward CV
  instead).
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - stats-student
evidence:
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - DU-MSDSAI-4432-MultiModelDiseaseProg
last-updated: 2026-05-23
---

# Evaluating Regression Models

## When to use

Trigger this skill when:

- A regression model (linear / Ridge / Lasso / RandomForest / XGBoost / NN) needs scoring or certification for deployment
- A metric is reported as bare R² (no RMSE, no MAE, no CV) — especially when the user says "R² = 0.85, is that good?"
- Residual diagnostics (residuals vs fitted, QQ-plot, Cook's D, heteroscedasticity) are needed
- Cross-validation is missing from the evaluation (single train/test point estimate only)
- The user is comparing two regression models and wants a fair comparison
- Keywords: RMSE, MAE, MSE, R², adjusted R², residuals, QQ-plot, k-fold, cross-validation, regression evaluation

## When NOT to use

Skip this skill and hand off when:

- The task is classification (binary or multi-class) → use `ml-datasci/evaluating-binary-classifiers`.
- The task is forecasting / time-series regression where the right CV is **walk-forward** (not k-fold) → use this skill's `time_series=True` mode AND `ml-datasci/auditing-train-test-split` for the temporal-split audit. Standard k-fold on time series leaks future information into training and inflates every metric below.
- The task is causal-effect estimation (ATE / CATE) rather than predictive — different evaluation regime (use causal-inference tooling).
- The user wants a leakage audit on the train/test split → use `ml-datasci/auditing-train-test-split`.
- The user wants residual diagnostics for hypothesis testing on regression coefficients → still applies here, but the deeper hypothesis machinery lives in `ml-datasci/checking-test-assumptions`.

## Quick start

User: "I fit a multiple linear regression to predict house price from 8 features (n = 1,200). Evaluate it."

Response: the full report — RMSE + MAE in dollar units, R² and adjusted-R² (because 8 features), residual diagnostics, and 5-fold cross-validation.

```python
import numpy as np
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
)
from sklearn.model_selection import cross_val_score, KFold

# Point-estimate metrics on held-out test
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae  = mean_absolute_error(y_test, y_pred)
r2   = r2_score(y_test, y_pred)
n, p = X_test.shape
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

# 5-fold CV on the same metric (negative RMSE for sklearn convention)
cv = cross_val_score(model, X, y, scoring="neg_root_mean_squared_error",
                     cv=KFold(n_splits=5, shuffle=True, random_state=42))
print(f"CV RMSE: {-cv.mean():.3f} ± {cv.std():.3f}")
```

See `reference/regression-eval-checklist.md` for the full report template; `reference/residual-diagnostics-recipe.md` for residual plots and Cook's D.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `y_true` | array-like float | yes | — | Ground-truth target values on the held-out test set. |
| `y_pred` | array-like float | yes | — | Model predictions, aligned row-wise with `y_true`. |
| `n_features` | int | yes (if computing adjusted R²) | — | Number of features used by the model; needed for adjusted-R². |
| `model`, `X`, `y` | sklearn-style estimator + full data | yes (for CV) | — | Used to run k-fold CV with the same metric on the same data. |
| `cv_folds` | int | no | `5` | Number of CV folds. |
| `time_series` | bool | no | `False` | If True, swap k-fold for `TimeSeriesSplit` (walk-forward CV). |
| `target_units` | str | no | inferred | Label for RMSE / MAE in the report (e.g. "USD", "mmHg") to keep the numbers interpretable. |
| `seed` | int | no | `42` | Random seed for shuffled k-fold. |

## Workflow

Copy this checklist into the response:

```
Regression-model eval progress:
- [ ] 0. Sanity checks (arrays align; no NaN/inf in y_true or y_pred; target is continuous)
- [ ] 1. Compute RMSE + MAE in target units + R² (+ adjusted-R² if multi-feature)
- [ ] 2. Identify time-series vs cross-sectional (if time-series → use walk-forward CV)
- [ ] 3. k-fold CV (default 5-fold) — report mean ± SD of the metric across folds
- [ ] 4. Residuals vs fitted plot — check for heteroscedasticity / structure
- [ ] 5. QQ-plot of residuals — check Normality (matters for inference, not for prediction)
- [ ] 6. Residual histogram — check skew and heavy tails
- [ ] 7. Cook's D (for OLS) or per-row residual magnitude — flag high-influence rows
- [ ] 8. Report block: metrics with CIs/SDs, residual verdicts, residual risks
```

### Step 1: Headline metrics in target units

Refuse to report R² alone. R² is unitless and can look great while RMSE is operationally unacceptable. Always pair:

- **RMSE** — interpretable in target units (dollars, mmHg, kWh); penalizes large errors more
- **MAE** — interpretable in target units; robust to outliers; closer to typical-error intuition
- **R²** — fraction of variance explained (unitless); communicates "how much better than predicting the mean"
- **Adjusted R²** (when n_features > 1) — penalizes adding features that don't reduce residual variance

Formula: `adjusted_R² = 1 - (1 - R²) * (n - 1) / (n - p - 1)` where `p = n_features`.

### Step 2: Time-series detection

If the rows have a temporal ordering and the target is forecasted into the future (next day's demand, next month's price), **k-fold is wrong**: it lets future rows train the model that predicts past rows, leaking information. Use `sklearn.model_selection.TimeSeriesSplit` (walk-forward / expanding-window) instead. Note this in the report.

### Step 3: Cross-validation

- Default: `KFold(n_splits=5, shuffle=True, random_state=seed)` on the same metric the user reports
- Time series: `TimeSeriesSplit(n_splits=5)` (walk-forward)
- Group-aware (multiple rows per patient / user / customer): `GroupKFold` (cross-reference `ml-datasci/auditing-train-test-split`)

Report `mean ± SD` of the metric across folds — not just the mean. A 5-fold CV RMSE of `4.3 ± 0.2` means stable; `4.3 ± 1.7` means the metric is fold-dependent and may not generalize.

### Step 4: Residuals vs fitted plot

Plot `residuals (y_true - y_pred)` against fitted values. Look for:

- **Funnel shape** → heteroscedasticity; the model's variance depends on the predicted value. Consider log-transforming the target, switching to a quantile or GLM model, or using HC-robust SEs for inference.
- **U-shape or trend** → missing nonlinear term or interaction; the model is under-specified.
- **Random cloud** → residuals look uncorrelated with the prediction; this is what you want.

### Step 5: QQ-plot of residuals

Q-Q against a Normal distribution. Heavy tails or systematic deviation matter when:

- The user wants confidence intervals or p-values on coefficients (parametric inference assumes Normal residuals)
- The target is being modeled with a method that assumes Normality (OLS regression for inference; not gradient boosting for prediction)

For pure prediction (no inference on coefficients), residual non-Normality is informational, not blocking.

### Step 6: Residual histogram

Quick visual check on skew and tails. Pairs with the QQ-plot — together they catch what neither catches alone.

### Step 7: Influence / outliers

- For OLS: report rows with Cook's D > 1 (or > 4/n as a softer threshold)
- For any model: report rows with `|residual| > 3 * SD(residual)` so the user can investigate
- Do not silently drop high-influence rows; flag them with row index and predicted/actual values

### Step 8: Report block

Final report includes: headline metrics in target units, CV stability, residual verdicts (heteroscedasticity / non-Normality / influential rows), and residual risks (extrapolation outside training range, drift sensitivity).

## Outputs

A markdown report with this structure:

1. **Dataset & model summary** — n, n_features, target description (units, mean, SD), model name
2. **Headline metrics** — RMSE (units), MAE (units), R², adjusted-R² (if multi-feature); single test slice
3. **Cross-validation** — fold scheme (k-fold / TimeSeriesSplit / GroupKFold), per-fold metric, `mean ± SD`
4. **Residual diagnostics** — residuals-vs-fitted plot, QQ-plot, histogram, Cook's D / outlier list with row indices
5. **Verdicts** — heteroscedasticity (yes/no), residual Normality (yes/no), influential rows (count)
6. **Residual risks** — extrapolation outside training feature range, drift sensitivity, time-series caveats

## Failure modes

- **R² reported alone** — caught by step 1; always pair with RMSE / MAE in target units.
- **k-fold on time-series data** — caught by step 2 + step 3; recommend `TimeSeriesSplit` and flag the leakage class.
- **Single train/test point estimate without CV** — caught by step 3 mean ± SD requirement.
- **Adjusted-R² omitted with multi-feature model** — caught by step 1 conditional rule (n_features > 1 → adjusted-R² required).
- **Residual diagnostics skipped** — caught by steps 4–7; a model with great R² and a funnel residual plot is misspecified.
- **High-leverage rows silently dropped** — caught by step 7 reporting rule (flag, do not delete).
- **Train R² mistaken for test R²** — always confirm which slice the metric came from; recommend recomputing if ambiguous.

## References

- `reference/regression-eval-checklist.md` — copy-paste report template
- `reference/residual-diagnostics-recipe.md` — residuals-vs-fitted + QQ + histogram + Cook's D code
- [scikit-learn cross-validation user guide](https://scikit-learn.org/stable/modules/cross_validation.html) — KFold / TimeSeriesSplit / GroupKFold semantics
- [statsmodels OLS diagnostics](https://www.statsmodels.org/stable/diagnostic.html) — Cook's D, leverage, influence measures for linear models
- [Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* — time-series cross-validation](https://otexts.com/fpp3/tscv.html) — walk-forward CV rationale

## Examples

### Example 1: Multiple linear regression on house prices (happy-path)

Input: "I fit a multiple linear regression to predict house price (USD) from 8 features. n_train = 960, n_test = 240. Evaluate."

Output: Skill produces the full 8-step report — RMSE and MAE in USD, R² + adjusted-R² (8 features), 5-fold CV with mean ± SD on RMSE, residuals-vs-fitted plot, QQ-plot of residuals, histogram, Cook's D flagging any high-leverage rows. Flags heteroscedasticity if the funnel shape appears.

### Example 2: Bare R² question (edge-case)

Input: "My R² is 0.85. Sounds great, right?"

Output: Skill refuses to render a verdict from R² alone. Requests RMSE in target units (so 0.85 R² with RMSE = $80k on a $400k median house is very different from RMSE = $8k). Asks whether the 0.85 came from the training set or a held-out test set. Requests CV result before certifying.

### Example 3: Forecasting with k-fold (anti-trigger)

Input: "I'm forecasting monthly demand 24 months ahead from 10 years of weekly data. My 5-fold CV RMSE is 12.3. Evaluate."

Output: Skill flags the 5-fold result as invalid for forecasting — standard k-fold shuffles past and future rows together, letting future weeks train the model that predicts past weeks. Recommends `TimeSeriesSplit` (walk-forward / expanding-window) instead and re-evaluation. Explains that the 12.3 likely overstates real forecast accuracy.

## See also

- `ml-datasci/evaluating-binary-classifiers` — the binary-classification analogue of this skill
- `ml-datasci/building-baseline-models` — required pre-step; without `DummyRegressor(strategy='mean')` and `LinearRegression` baselines, the metrics here have no comparison context
- `ml-datasci/auditing-train-test-split` — required pre-step; evaluating on a leaky split (time-series shuffled, group-leaked) inflates every metric here
- `ml-datasci/checking-test-assumptions` — sibling for the inference path; residual Normality / equal-variance checks live there with hypothesis-test framing
- `ml-datasci/analyzing-regression-diagnostics` (planned) — deeper dive on residual diagnostics, leverage, influence, multicollinearity

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (Batch 3, skill 3.3) via PRAGMATIC discipline
