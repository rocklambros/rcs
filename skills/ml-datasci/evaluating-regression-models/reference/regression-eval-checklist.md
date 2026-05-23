# Regression-model evaluation report — copy-paste template

Replace `<...>` placeholders with computed values. For time-series tasks, swap the CV section's k-fold language for `TimeSeriesSplit`.

---

## Dataset & model summary

- n_train = `<n_train>`, n_test = `<n_test>`, n_features = `<p>`
- Target: `<name>` in `<units>`; mean = `<mu>`, SD = `<sigma>`, range = [`<min>`, `<max>`]
- Model: `<name>` (`<key hyperparameters>`)
- Train/test split source: `<file:line or commit>`  (see `ml-datasci/auditing-train-test-split`)

## Headline metrics (held-out test slice)

- RMSE = `<rmse>` `<units>` (penalizes large errors; same units as target)
- MAE  = `<mae>` `<units>` (robust to outliers; same units as target)
- R²   = `<r2>` (fraction of variance explained vs predicting the mean)
- Adjusted R² = `<adj_r2>` (only when p > 1; `1 - (1 - R²) * (n - 1) / (n - p - 1)`)

## Cross-validation

- Scheme: `<KFold(k=5, shuffle=True) | TimeSeriesSplit(k=5) | GroupKFold(...)>`
- Per-fold RMSE: `[<f1>, <f2>, <f3>, <f4>, <f5>]`
- Mean ± SD: `<mean> ± <sd>` `<units>`
- Stability verdict: `<stable | fold-dependent — investigate the high-error fold>`

## Residual diagnostics

- **Residuals vs fitted** (`residuals-vs-fitted.png`)
  - Verdict: `<random cloud | funnel — heteroscedasticity | U-shape — missing nonlinear term | trend — missing feature>`
- **QQ-plot of residuals** (`qq-plot.png`)
  - Verdict: `<approximately Normal | heavy tails | systematic skew>`
- **Residual histogram** (`residual-histogram.png`)
  - Skew = `<value>`, kurtosis = `<value>`
- **Influence**
  - Rows with Cook's D > 1: `<row indices or "none">`
  - Rows with |residual| > 3·SD: `<row indices>`
  - Action: `<flag for review | investigated and excluded with justification | none>` — never silent drops

## Verdicts

- Heteroscedasticity: `<yes/no>`; if yes, candidates = `<log-transform target | quantile regression | HC-robust SEs>`
- Residual Normality: `<yes/no>`; matters for parametric inference on coefficients, not for prediction
- Influential rows: `<count>` rows flagged; recommend follow-up before deployment

## Residual risks

- Extrapolation: `<X-feature ranges in test that fall outside training>`
- Drift sensitivity: `<does refitting on a fresh batch shift RMSE > 20%?>`
- Time-series caveat: `<if applicable, restate that walk-forward CV was used and naming the train/test temporal boundary>`
- Pre-step sanity: confirm `auditing-train-test-split` ran clean before trusting any number above
