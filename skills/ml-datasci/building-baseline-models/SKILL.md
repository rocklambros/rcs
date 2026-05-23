---
name: building-baseline-models
description: >
  Builds simple baseline models (Dummy / LogisticRegression or LinearRegression
  / RandomForest) BEFORE fitting a complex model, so a fancy-model metric has a
  meaningful comparison and "better than chance" has a concrete number.
  Triggers when the user is about to fit gradient boosting, deep learning, or
  any complex model; when a metric is reported without comparison context; or
  when the user asks whether their fancy model is actually better than chance.
  Refuses to certify a complex-model metric as "good" without a baseline
  comparison on the same evaluation regime.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - stats-student
evidence:
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - DU-MSDSAI-4432-OptimalClusteringComparison
last-updated: 2026-05-23
---

# Building Baseline Models

## When to use

Trigger this skill when:

- The user announces they're about to fit XGBoost, LightGBM, CatBoost, a neural net, a transformer, or any model more complex than logistic / linear regression
- The user reports a metric (accuracy, AUC, RMSE, R²) without saying "vs. what" — no chance-baseline, no linear-baseline, no naive-prior comparison
- The user asks variants of "is 0.92 AUC good?" / "is RMSE = 4.3 good?" / "is my model actually better than guessing?"
- The user is comparing two or more complex models and there is no Dummy or LinearRegression / LogisticRegression rung in the comparison
- Keywords: baseline, dummy, naive, chance, prior, "is this good", "better than random"

## When NOT to use

Skip this skill and hand off when:

- The task is pure unsupervised (clustering, PCA, anomaly detection without labels) — "baseline" in the supervised-learning sense does not apply; use `ml-datasci/auditing-train-test-split` and domain-specific stability checks instead
- The user already has a Dummy + linear-baseline comparison and now wants help fitting the next rung — skip ahead; do not re-litigate
- The user is doing pure pedagogy on what gradient boosting is — do not block the explanation with a baselines mandate
- The task is forecasting and the appropriate baseline is the persistence / seasonal-naive forecast (different from this skill's Dummy ladder) — use forecasting-specific baselines (note this in the response)

## Quick start

User: "I'm training XGBoost on a binary classification task. What baselines should I add?"

Response: The 3-rung baseline ladder, fit and scored with the SAME train/test split and SAME metric the user plans to use for XGBoost.

```python
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

models = {
    "Dummy (stratified)": DummyClassifier(strategy="stratified", random_state=42),
    "Logistic":           LogisticRegression(max_iter=2000, random_state=42),
    "RandomForest":       RandomForestClassifier(n_estimators=200, random_state=42),
}

results = {}
for name, m in models.items():
    m.fit(X_train, y_train)
    results[name] = roc_auc_score(y_test, m.predict_proba(X_test)[:, 1])

# Report table: baseline · metric (with CI from ml-datasci/evaluating-binary-classifiers)
```

For regression, swap to `DummyRegressor(strategy="mean")`, `LinearRegression`, `RandomForestRegressor`, and use RMSE / MAE / R².

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `task` | "classification" \| "regression" | yes | — | Determines which baseline ladder to use. |
| `X_train`, `y_train`, `X_test`, `y_test` | array-like | yes | — | The same split that will be used for the final complex model. |
| `metric` | str / callable | yes | — | Same metric the user plans to report for the complex model (e.g. roc_auc_score, f1_score, rmse). |
| `cv_folds` | int | no | `5` | Optional: cross-validate each baseline at the same fold count as the final model. |
| `extra_baselines` | list | no | `[]` | Domain-specific extras (e.g. persistence baseline for forecasting; majority-class baseline for severely imbalanced classification). |
| `seed` | int | no | `42` | Single seed for all baselines; report seed in the comparison table. |

## Workflow

Copy this checklist into the response:

```
Baseline-ladder progress:
- [ ] 0. Confirm task type (classification / regression) and chosen metric
- [ ] 1. Lock train/test split (or CV folds) — same for all baselines AND the final model
- [ ] 2. Fit Dummy baseline (stratified-classifier or mean-regressor)
- [ ] 3. Fit linear baseline (LogisticRegression or LinearRegression)
- [ ] 4. Fit tree baseline (RandomForest with default hyperparameters)
- [ ] 5. Compute the same metric for all 3 baselines on the same test slice
- [ ] 6. (Optional) Add domain baseline (persistence forecast, majority-class, prior-based predictor)
- [ ] 7. Comparison table: baseline · metric · 95% CI · lift over Dummy
- [ ] 8. Block reporting the complex-model metric until the table is filled
```

### Step 1: Lock the evaluation regime

Every baseline and the final model must score on the SAME train/test split (or SAME CV folds), with the SAME metric, the SAME preprocessing pipeline (imputers / scalers fit on train only), and the SAME random seed where applicable. Drift on any of these dimensions invalidates the comparison.

### Step 2: Dummy baseline

For classification:

- `DummyClassifier(strategy="stratified")` — predicts class labels in proportion to training set frequency. This is the "random with priors" baseline.
- For severely imbalanced classification, also report `DummyClassifier(strategy="most_frequent")` — the always-predict-majority baseline. This is the number a 99%-accuracy fraud classifier is competing against.

For regression:

- `DummyRegressor(strategy="mean")` — predicts the training mean for every test row. R² = 0 here by construction.
- For asymmetric / heavy-tailed targets, also report `strategy="median"`.

### Step 3: Linear baseline

- Classification: `LogisticRegression(max_iter=2000, random_state=seed)`.
- Regression: `LinearRegression()` or `Ridge(alpha=1.0)` if multicollinearity is suspected.

If features include un-encoded categoricals or wildly different scales, build a `Pipeline` with `ColumnTransformer` so the linear baseline gets a fair shot.

### Step 4: Tree baseline

- `RandomForestClassifier(n_estimators=200, random_state=seed)` or `RandomForestRegressor(n_estimators=200, random_state=seed)` with otherwise-default hyperparameters. The point is "what does a strong off-the-shelf nonlinear model get with no tuning."

### Step 5: Same metric, same slice

Compute the metric the user plans to report for the complex model. Pair it with a bootstrap 95% CI (see `ml-datasci/evaluating-binary-classifiers` reference/bootstrap-ci.md, or for regression compute bootstrap CIs over RMSE / MAE / R²).

### Step 6: Comparison table

| Model | Metric | 95% CI | Lift over Dummy |
|---|---|---|---|
| Dummy (stratified) | `<value>` | `[low, high]` | — |
| Logistic | `<value>` | `[low, high]` | `<delta>` |
| RandomForest | `<value>` | `[low, high]` | `<delta>` |
| **Final model (XGBoost / NN / ...)** | `<value>` | `[low, high]` | `<delta>` |

If the final model's CI overlaps the linear baseline's CI, the complex model has not earned its complexity yet.

### Step 7: Refusal rule

If the user asks "is `<metric>` good?" without supplying baseline numbers, refuse to render a verdict. Ask for the Dummy and linear-baseline values first. Lift over baseline is the right framing; the absolute number alone is not.

## Outputs

A markdown report block:

1. **Evaluation regime** — train/test split or CV fold definition; preprocessing pipeline summary; metric name; seed
2. **Baseline table** — Dummy · Linear · RandomForest, each with metric + 95% CI
3. **Domain baselines** (optional) — persistence / majority-class / prior-based, with rationale
4. **Final-model comparison** — same row in the same table; lift over baselines highlighted
5. **Verdict** — does the complex model clear linear by a CI-disjoint margin? If no: flag and recommend either more data, more features, or accepting the simpler model

## Failure modes

- **No baseline at all** — caught by the refusal rule in step 7.
- **Different evaluation regime per model** — caught by the "lock the evaluation regime" requirement; baselines and final model use the same split / preprocessing / metric / seed.
- **Cherry-picked baseline** — using `DummyClassifier(strategy="uniform")` on imbalanced data understates the baseline; the right strategy is `"stratified"` (or `"most_frequent"` as a stricter floor). Caught by explicitly naming `strategy="stratified"` as the default.
- **Linear baseline with no encoding** — a LogisticRegression fed raw categorical strings or unscaled features looks artificially weak. Caught by step 3 pipeline note.
- **No CI on the comparison** — the metric difference might be inside sampling noise. Caught by step 5 bootstrap CI requirement.
- **Time-series mis-baseline** — for forecasting, the right baseline is persistence (`y_pred[t] = y[t-1]`) or seasonal-naive, not Dummy mean. Caught by the `extra_baselines` argument + the time-series caveat in `When NOT to use`.

## References

- [scikit-learn DummyClassifier docs](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html) — strategy options and semantics
- [scikit-learn DummyRegressor docs](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyRegressor.html) — strategy options and semantics
- [Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* — naive forecasts](https://otexts.com/fpp3/simple-methods.html) — persistence and seasonal-naive baselines for time series
- `ml-datasci/evaluating-binary-classifiers` (reference/bootstrap-ci.md) — bootstrap CI recipe used in step 5
- `ml-datasci/evaluating-regression-models` — regression analogue plus residual diagnostics

## Examples

### Example 1: XGBoost-bound user (happy-path)

Input: "I'm training XGBoost on a binary classification task. What baselines should I add?"

Output: Skill names the 3-rung ladder — `DummyClassifier(strategy='stratified')` + `LogisticRegression` + `RandomForestClassifier` — fit and scored on the same train/test split and metric as the planned XGBoost run, with bootstrap 95% CIs and a comparison table.

### Example 2: Bare-metric question (edge-case)

Input: "My XGBoost gets 0.92 ROC-AUC. Is that good?"

Output: Skill refuses to render a verdict. Asks for the Dummy-stratified ROC-AUC and the LogisticRegression ROC-AUC on the same test set, then explains that lift over baseline (not the absolute 0.92) is the right framing — and that if the linear baseline already hits 0.91, the complexity may not be earning its keep.

### Example 3: Unsupervised PCA (anti-trigger)

Input: "I'm running PCA on my data to find the top components. What baselines do I need?"

Output: Skill explains that supervised baselines (Dummy / Logistic / RF) don't apply to unsupervised dimensionality reduction. Recommends variance-explained per component, Kaiser criterion (eigenvalue > 1), and scree-plot inspection as the relevant sanity checks. Does not force a Dummy run.

## See also

- `ml-datasci/evaluating-binary-classifiers` — required follow-up for classification; the metric + CI machinery lives there
- `ml-datasci/evaluating-regression-models` — required follow-up for regression; same idea, RMSE / MAE / R² flavor
- `ml-datasci/auditing-train-test-split` — required pre-step; baselines and final model must use the SAME leakage-clean split
- `ml-datasci/comparing-models-fairly` (planned) — McNemar / paired-folds for declaring statistical significance between models
- `ml-datasci/running-chollet-ratio-check` (planned) — informs whether even the linear baseline is appropriate given samples-to-features ratio

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (Batch 3, skill 3.2) via PRAGMATIC discipline
