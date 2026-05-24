---
name: building-conformal-prediction-set
description: >
  Builds a split-conformal prediction set or prediction interval around any
  black-box classifier or regressor that produces a score or a point estimate,
  giving a distribution-free finite-sample marginal coverage guarantee at the
  user-chosen level (typically 1 - alpha = 0.9 or 0.95). Walks the four-step
  recipe: train / calibration / test split, nonconformity-score choice, quantile
  computation on the calibration set, and prediction-set construction at test
  time. Includes the empirical coverage check on the held-out test set and the
  exchangeability red-flag list. Use when the user wants calibrated uncertainty
  on a model that does not produce trustworthy probabilities, when the user
  asks for prediction intervals around a regression point estimate, or when a
  downstream system needs a guaranteed coverage rate. Refuses to engage when
  no calibration set can be carved out, when the data are non-exchangeable
  without an adaptation, or when a bare point prediction is sufficient.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - stats-student
  - security-eng
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Building Conformal Prediction Set

## When to use

Trigger this skill when the user does any of the following:

- Asks "how do I get calibrated uncertainty from `<black-box model>`?"
- Names "conformal prediction", "split conformal", "CP set", "prediction set", "prediction interval"
- Reports that `predict_proba` outputs are mis-calibrated and wants a guaranteed coverage rate instead
- Wants a guaranteed coverage rate around a regression point estimate (`y_hat ± width` with documented coverage)
- A downstream consumer (clinical decision support, autonomous-system gate, fraud queue) requires "the prediction set must contain the true label at least 90% of the time"
- Has a black-box scorer (LightGBM, neural net, ensemble, external API) where probability calibration via Platt or isotonic isn't acceptable because they only adjust the score, not the coverage guarantee

## When NOT to use

Skip this skill and hand off or refuse when:

- No held-out calibration set can be carved out — conformal needs at least ~200–500 points NOT used in training and NOT used in final evaluation
- The user only wants a point prediction and has no downstream coverage requirement — adding conformal here is overhead with no payoff
- Data are heavily non-exchangeable (concept drift across time, group leakage, distribution shift between training and deployment) AND no adaptation (weighted conformal, conformal under covariate shift) is in scope — naive split conformal will under-cover. Hand off to the user with a flag rather than producing a fake guarantee
- The base model produces well-calibrated probabilities already (well-fit logistic regression on a clean problem) AND the user only needs marginal calibration, not a coverage guarantee — Platt / isotonic / Brier-score-driven recalibration is lighter
- This is a multi-class problem with thousands of classes and the user wants per-class conditional coverage, not marginal coverage — that is conditional conformal, a more advanced variant not covered here
- The setup is online / streaming and the user needs adaptive coverage on every step — point them to ACI (Adaptive Conformal Inference) or fully online conformal, not split conformal

## Quick start

User says: "I trained an XGBoost classifier on 10,000 rows. I want 90% prediction sets — each test point should produce a set of class labels that contains the true label at least 90% of the time. Walk me through it."

Skill response, in order:

1. **Carve the data into three disjoint splits** — train / calibration / test. Typical 70 / 15 / 15. The training set fits the model; the calibration set computes the conformal quantile; the test set verifies empirical coverage. NEVER reuse the calibration set for any other purpose; it has been "spent" once used.
2. **Pick a nonconformity score**. For classification with score outputs: `s(x, y) = 1 - hat_p_y(x)` (one minus the model's predicted probability of the true class). For regression: `s(x, y) = |y - hat_y(x)|` (absolute residual). For asymmetric regression intervals: use quantile regression as the base model and `s(x, y) = max(hat_q_lo(x) - y, y - hat_q_hi(x))` (CQR — conformalized quantile regression).
3. **Compute the conformal quantile** on the calibration set: `q = Quantile(s_cal, (1 - alpha) * (n_cal + 1) / n_cal)`. The finite-sample correction `(n+1)/n` is required — using the bare `1 - alpha` quantile under-covers.
4. **Construct the prediction set / interval** at test time. Classification: `C(x_new) = {y : 1 - hat_p_y(x_new) ≤ q}`. Regression: `C(x_new) = [hat_y(x_new) - q, hat_y(x_new) + q]`. CQR: `C(x_new) = [hat_q_lo(x_new) - q, hat_q_hi(x_new) + q]`.
5. **Verify empirical coverage** on the held-out test set: fraction of `y_test` inside `C(x_test)` must be approximately `1 - alpha`. For `alpha = 0.1` with `n_test = 1000`, expect coverage in roughly `[0.88, 0.92]` (the marginal-coverage interval is `[1 - alpha - 1/sqrt(n_test), 1 - alpha + 1/sqrt(n_test)]` as a quick sanity range).
6. **Report set size** alongside coverage. A set that covers 100% by returning every class is not useful. Average set size (`E[|C(x)|]`) for classification or average interval width for regression is the second mandatory number.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| task | "classification" \| "regression" \| "quantile-regression" | yes | — | Determines the nonconformity-score family |
| base_model | any fitted scikit-learn-style estimator | yes | — | Must produce either `predict_proba` (classification), `predict` (regression), or `predict` returning low/high quantiles (CQR) |
| alpha | float in (0, 1) | yes | — | Miscoverage rate; coverage target is `1 - alpha`. Typical values 0.1 (90%) or 0.05 (95%) |
| nonconformity_score | "softmax" \| "absolute-residual" \| "cqr" \| "custom-callable" | no | "softmax" for classification, "absolute-residual" for regression | Function that maps `(x, y)` to a real-valued score; higher score = more nonconforming |
| n_calibration | int | yes | — | Calibration-set size; minimum 200 for stable quantile, 500+ recommended for `alpha = 0.05` |
| split_strategy | "random" \| "stratified" \| "group-aware" \| "temporal" | no | "random" | Calibration split must respect any group / time structure to avoid leakage; matches `auditing-train-test-split` discipline |
| return_set_size | bool | no | true | Include average set size / interval width in the output report (mandatory in practice; opt-out is rare) |
| coverage_check_n | int | no | 500 | Held-out test-set size used to verify empirical coverage |

## Workflow

Copy this checklist into the response and check off each step as it lands:

```
Conformal-prediction progress:
- [ ] Step 1: Carve train / calibration / test splits (typical 70/15/15)
       and document split strategy (random / stratified / group / temporal)
- [ ] Step 2: Fit base model on train split ONLY
- [ ] Step 3: Choose nonconformity score (softmax / abs-residual / CQR / custom)
- [ ] Step 4: Compute scores on calibration set; compute quantile q with
       finite-sample correction (1 - alpha) * (n_cal + 1) / n_cal
- [ ] Step 5: At test time, construct prediction set / interval using q
- [ ] Step 6: Verify empirical coverage on the test set ≈ 1 - alpha
- [ ] Step 7: Report average set size / interval width alongside coverage
- [ ] Step 8: Check exchangeability red flags; if violated, flag as
       coverage-guarantee-broken
```

### Step 1 — Splits

Calibration set MUST be disjoint from both training and test. Group structure (multiple rows per patient, user, customer) must be respected: GroupShuffleSplit or GroupKFold. Temporal structure: split by date, calibration set chronologically before test set. The `ml-datasci/auditing-train-test-split` discipline applies here verbatim.

Minimum `n_calibration` for stable coverage:

| alpha | Recommended n_cal | Note |
|---|---|---|
| 0.1 (90%) | ≥ 200 | Lower end; quantile noisy below this |
| 0.05 (95%) | ≥ 500 | Tail quantile needs more data |
| 0.01 (99%) | ≥ 2000 | Far-tail quantile needs much more data |

### Step 3 — Nonconformity-score choices

**Classification (softmax / score):**
`s(x, y) = 1 - hat_p_y(x)`

Higher when the model is confident in a wrong label. Simple, works for any classifier with `predict_proba` or score outputs (softmax LLMs included).

**Classification (APS — Adaptive Prediction Set, optional improvement):**
`s(x, y) = sum of predicted probabilities for classes ranked >= y by probability`

Produces smaller sets when the model is confident. More complex; consider once the simple score is working.

**Regression (absolute residual):**
`s(x, y) = |y - hat_y(x)|`

Symmetric interval `[hat_y - q, hat_y + q]`. Same width everywhere — does NOT adapt to local heteroscedasticity.

**Regression (CQR — Conformalized Quantile Regression):**
Train a quantile-regression model that predicts `hat_q_lo(x)` and `hat_q_hi(x)` at quantile levels `alpha/2` and `1 - alpha/2`. Then `s(x, y) = max(hat_q_lo(x) - y, y - hat_q_hi(x))`. The conformal correction widens (or shrinks) the quantile interval by `q`. Produces narrower intervals where the model is confident and wider where it isn't — the right default for heteroscedastic regression.

### Step 4 — Finite-sample quantile

```python
import numpy as np
s_cal = np.array([score(x, y, model) for x, y in zip(X_cal, y_cal)])
n = len(s_cal)
q = np.quantile(s_cal, np.ceil((1 - alpha) * (n + 1)) / n, method="higher")
```

The `(n + 1) / n` correction and `method="higher"` together give exact finite-sample marginal coverage of at least `1 - alpha` (Vovk, 2005). Skipping the correction means coverage drifts slightly low; on a 200-point calibration set with `alpha = 0.1`, true coverage drops to ~0.89 instead of ≥ 0.90.

### Step 5 — Prediction set construction

**Classification:**
```python
def predict_set(x_new, model, q):
    probs = model.predict_proba([x_new])[0]
    return [y for y, p in enumerate(probs) if (1 - p) <= q]
```

If the resulting set is empty (no class has `1 - p ≤ q`), include the top-1 prediction as a fallback. An empty set is not better than a single-element set.

**Regression (absolute residual):**
```python
def predict_interval(x_new, model, q):
    yhat = model.predict([x_new])[0]
    return (yhat - q, yhat + q)
```

**CQR:**
```python
def predict_interval_cqr(x_new, model, q):
    lo, hi = model.predict_quantiles([x_new])[0]  # quantile model
    return (lo - q, hi + q)
```

### Step 6 — Empirical coverage check

```python
coverage = np.mean([y in predict_set(x, model, q) for x, y in zip(X_test, y_test)])
# Expect coverage in [1 - alpha - 2/sqrt(n_test), 1 - alpha + 2/sqrt(n_test)]
```

If empirical coverage is well outside this band, something is wrong: split leakage, exchangeability violation, or buggy nonconformity score. Re-check before shipping.

### Step 8 — Exchangeability red flags

The marginal-coverage guarantee assumes the calibration and test points are exchangeable. Naive split conformal under-covers when:

- Temporal drift: training / cal data is from January, deployment from July
- Covariate shift: deployment features look systematically different from cal features
- Label drift: prevalence of the positive class shifts after deployment
- Group structure leaked: same patient / user in cal and test

When any of these apply, the marginal guarantee is BROKEN. Either:

1. Use weighted conformal (re-weight calibration samples by likelihood ratio) for known covariate shift
2. Use Adaptive Conformal Inference (ACI) for online / streaming with drift
3. Document the gap and refuse to claim the marginal-coverage guarantee

## Outputs

A short report containing:

1. **Split summary** — train / calibration / test sizes, split strategy used
2. **Base-model summary** — model type, training metric on train split
3. **Nonconformity-score choice** — name + brief justification
4. **Conformal quantile** `q` — single number, computed on calibration set
5. **Empirical coverage** on the test set — fraction with 95% CI
6. **Average set size** (classification) or **average interval width** (regression)
7. **Conditional coverage by group** (optional but recommended) — coverage broken out by any sensitive attribute or group of interest; flags under-coverage in any subgroup
8. **Exchangeability statement** — explicit yes / no on whether the assumption holds; if no, document the gap

## Failure modes

- **Reusing calibration set as test set** — empirical coverage looks perfect because the same data informed `q` and is being scored. Caught by: Step 1 requires three disjoint splits; lint the user's setup if they only have two.
- **Skipping the (n+1)/n correction** — coverage drifts slightly below target on small calibration sets. Caught by: Step 4 example uses `np.ceil((1 - alpha) * (n + 1)) / n` explicitly.
- **Empty prediction set in classification** — when `q` is small and no class has probability above the threshold. Caught by: Step 5 fallback rule — always return at least the top-1 prediction.
- **Marginal coverage masking poor conditional coverage** — overall 90% coverage but only 60% on a minority subgroup. Caught by: Step 7 conditional-coverage report by group; flag any subgroup below `(1 - alpha) - 5%`.
- **Non-exchangeable cal/test split** — temporal split with calibration before test plus a regime change between them → empirical coverage drops well below target. Caught by: Step 8 red-flag checklist; refuse to claim marginal guarantee when violated.
- **Set size of "all classes"** — wide quantile + dispersed probabilities → conformal returns every class. Caught by: Step 7 mandates set-size reporting; trivial-set sizes invalidate the deployment value even if coverage is met.
- **Conformalizing on a model that has data leakage in training** — calibration set might inherit the leak; coverage looks fine but is on a corrupted task. Caught by: cross-reference `ml-datasci/auditing-train-test-split` BEFORE the conformal split.
- **Coverage drift after deployment** — model deployed unchanged for 6 months while the data distribution shifts. Caught by: pair deployment with `ml-datasci/monitoring-prediction-drift`; recompute `q` on a fresh calibration window periodically.

## References

- [`reference/sklearn-conformal-example.py`](reference/sklearn-conformal-example.py) — split-conformal classification (softmax score) and regression (absolute-residual and CQR) on a scikit-learn pipeline
- [`reference/coverage-vs-set-size.md`](reference/coverage-vs-set-size.md) — discussion of the coverage / set-size tradeoff and the exchangeability red-flag checklist
- [Angelopoulos & Bates, "A Gentle Introduction to Conformal Prediction" (2022)](https://arxiv.org/abs/2107.07511) — canonical tutorial
- [Vovk, Gammerman, Shafer, "Algorithmic Learning in a Random World" (2005)](https://link.springer.com/book/10.1007/b106715) — foundational text
- [MAPIE library docs](https://mapie.readthedocs.io/) — production-grade Python implementation
- `ml-datasci/auditing-train-test-split` — prerequisite for clean split discipline
- `ml-datasci/monitoring-prediction-drift` — post-deployment companion for drift-aware coverage recalibration
- `ml-datasci/running-bayesian-workflow` — alternative uncertainty quantification when priors and posteriors are tractable

## Examples

### Example 1: XGBoost 90% prediction sets on 10k-row classifier (happy-path)

Input: "I trained an XGBoost classifier on 10,000 rows. I want 90% prediction sets — each test point should produce a set of class labels that contains the true label at least 90% of the time. Walk me through it."

Output: Split 7,000 / 1,500 / 1,500 random (or stratified if class imbalance > 80/20). Fit XGBoost on the 7,000-row train set. Compute `s = 1 - p_true_class` for each row of the 1,500 calibration rows. Compute `q = np.quantile(s_cal, np.ceil(0.9 * 1501) / 1500, method="higher")`. At test time, for each `x`, return `{y : 1 - p_y(x) <= q}`. Fall back to top-1 if set is empty. Verify on the 1,500 test rows: empirical coverage should fall in `[0.875, 0.925]` (95% CI for n=1500). Report empirical coverage AND average set size; the latter is the practical measure of usefulness. Document exchangeability: random split with no temporal or group structure, so the assumption holds.

### Example 2: Small calibration set, alpha=0.05 (edge-case)

Input: "I want 95% prediction intervals on a regression model. I only have 150 calibration rows available because the dataset is small. Is conformal still viable?"

Output: Marginally. With n_cal = 150 and alpha = 0.05, the quantile lands at index `ceil(0.95 * 151) = 144`, leaving only six points above the cut — the tail quantile is noisy and the resulting interval width has high run-to-run variance. Options: (1) accept the noise but report it — interval width may swing 20–30% across different calibration draws; (2) drop the target coverage to 90% so the quantile lands at index `ceil(0.9 * 151) = 136`, leaving fifteen tail points (more stable); (3) use cross-conformal or jackknife+ instead of split conformal — they reuse data more efficiently at the cost of more compute and a slightly different theoretical guarantee; (4) collect more data if at all possible. Do NOT silently produce a 95% interval claim with `n_cal = 150` — name the imprecision in the output.

### Example 3: Bare point prediction, no coverage requirement (anti-trigger)

Input: "I'm building a regression model to predict the next day's electricity demand for internal capacity planning. I just need a point estimate; we already have a separate process for forecasting uncertainty at the grid-operator level. Should I wrap it in conformal prediction?"

Output: No. Conformal adds setup cost (a third data split, a calibration step, a quantile to track and refresh) and produces a deliverable — a prediction interval with a documented coverage guarantee — that the user explicitly says they do not need here. The downstream consumer (capacity planning, grid-operator forecasting handled elsewhere) is not asking for a coverage rate on the user's point prediction. Ship the point estimate and standard regression diagnostics (RMSE, MAE, residual plots — hand off to `ml-datasci/evaluating-regression-models`). Revisit conformal IF a future requirement appears, e.g., a downstream system needs "the predicted demand should be inside the reported interval 90% of the time" as a contract.

## See also

- `ml-datasci/auditing-train-test-split` — required prerequisite for the train / calibration / test split discipline
- `ml-datasci/monitoring-prediction-drift` — coverage degrades when the data distribution shifts; pair with periodic re-calibration
- `ml-datasci/running-bayesian-workflow` — Bayesian credible intervals offer different (model-dependent) uncertainty when priors are tractable
- `ml-datasci/evaluating-binary-classifiers` — once a binary conformal set is in hand, evaluate the underlying scorer with this skill
- `ml-datasci/evaluating-regression-models` — for the underlying point predictor in the regression case

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
