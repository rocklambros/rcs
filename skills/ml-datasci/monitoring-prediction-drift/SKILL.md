---
name: monitoring-prediction-drift
description: >
  Builds a prediction-side drift monitor for a deployed ML model — tracks the
  predicted-score distribution, calibration over time (reliability curve slope
  and intercept), and per-segment performance erosion (AUC / F1 / precision-recall
  by cohort). Triggers whenever a production model has accumulated live
  predictions plus labels for at least one labeling-delay-aware evaluation
  window, whenever performance metrics suggest erosion but the input features
  look stable, whenever predicted scores look unusually high or low, or
  whenever per-segment fairness or accuracy must be tracked over time.
  Refuses to interpret calibration without a labeling-delay-aware window
  and refuses to engage on pre-deployment systems where no live predictions
  exist yet.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - devops
evidence:
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Monitoring Prediction Drift

## When to use

Trigger this skill when:

- A production ML model has produced live predictions long enough to accumulate at least one labeling-delay-aware evaluation window (e.g., a 30-day-loan-default model needs 60+ days of post-prediction time before labels are usable)
- Model performance is suspected of erosion but feature distributions look stable (data-drift monitor is green; prediction-side drift is the next hypothesis)
- The predicted score distribution looks different from the training-time distribution (mean / p50 / p95 shifted; the histogram tail looks unfamiliar)
- A per-segment or per-cohort fairness commitment requires periodic tracking of AUC / precision / recall by group
- The user asks for "calibration monitoring", "score-shift detection", "per-segment performance tracking", "model-quality monitoring in prod"
- A regulator or model-card commitment requires periodic post-deployment performance attestation

## When NOT to use

Skip this skill and hand off when:

- The model has not been deployed yet — prediction drift requires live predictions; use `ml-datasci/evaluating-binary-classifiers` or `ml-datasci/evaluating-regression-models` for pre-deployment scoring
- The concern is input-side feature drift (PSI / KS / JS on features) — use `ml-datasci/monitoring-data-drift`
- The concern is latency / throughput / SLO compliance — use `ml-datasci/auditing-inference-latency-budget`
- Ground-truth labels are not available and will not be (true unsupervised production deployment with no feedback signal) — recommend proxy metrics (downstream business KPI, human-in-the-loop sampling) instead
- The labeling delay is so short that supervised-quality monitoring covers the case directly (e.g., real-time content moderation with immediate human review) — collapse to the standard eval skill on a rolling window
- The system is a one-shot batch model that will not be retrained — drift monitoring overhead exceeds value

## Quick start

User: *"Our loan-default classifier has been in prod 9 months. Feature drift looks stable (PSI < 0.1 on all features). But our finance team says default-rate predictions are coming in noticeably lower than the actuals they're seeing in the books. Find out what's going on."*

Response: stable input features + diverging output behavior is the classic prediction-drift signature. Set up: (1) labeling-delay-aware evaluation window (loans have a 30-90-day mature-to-default delay — pick a window where labels are present), (2) reliability curve (predicted probability bins vs. actual default rate), (3) calibration slope (β1) and intercept (β0) from logistic regression of outcome on predicted log-odds — slope ≠ 1 or intercept ≠ 0 means miscalibration, (4) score-distribution shift on predictions only (PSI on `y_pred_proba` between reference and current). Distinguish three causes: calibration drift (slope/intercept moved; recalibrate via Platt or isotonic), distribution shift in the predicted scores (often follows from cohort-mix change), or true label-distribution change (concept drift on `y`).

```python
import numpy as np
from sklearn.linear_model import LogisticRegression

def calibration_slope_intercept(y_true, y_pred_proba):
    # Fit logistic: y ~ log_odds(pred) ; ideal slope=1, intercept=0
    eps = 1e-12
    p = np.clip(y_pred_proba, eps, 1 - eps)
    log_odds = np.log(p / (1 - p)).reshape(-1, 1)
    lr = LogisticRegression(C=1e6, solver="lbfgs").fit(log_odds, y_true)
    return float(lr.coef_[0][0]), float(lr.intercept_[0])
```

See `reference/calibration-diagnostics.md` for the full reliability-curve / slope-intercept recipe, `reference/segment-evaluation.md` for per-cohort AUC / F1 tracking with confidence intervals, and `reference/label-delay-handling.md` for the labeling-delay window construction.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `predictions_log` | DataFrame / parquet / SQL | yes | — | Per-prediction records: `prediction_id`, `timestamp`, `y_pred_proba` (or `y_pred_score`), `y_pred_class`, `segment` columns. |
| `labels_log` | DataFrame / parquet / SQL | yes | — | Per-outcome records: `prediction_id`, `label_timestamp`, `y_true`. Joined to predictions by `prediction_id`. |
| `labeling_delay_days` | integer | yes | — | Days between a prediction being made and its label becoming reliably observable. Drives the evaluation-window construction. |
| `reference_window` | date range | yes | — | The baseline evaluation window (model launch or last validated period). Calibration and per-segment metrics for this window are the comparison anchor. |
| `current_window` | date range | yes | — | The recent evaluation window. Must be `current_window.end < today() - labeling_delay_days` so labels are mature. |
| `task_type` | "binary" \| "multiclass" \| "regression" | yes | — | Drives the metric set (binary: AUC + calibration; multiclass: per-class F1; regression: RMSE + MAE + residual diagnostics). |
| `segments` | list of column names | no | none | Per-cohort dimensions (region, channel, product line) for per-segment erosion tracking. |
| `calibration_method` | "platt" \| "isotonic" | no | "platt" | If recalibration is recommended, which method to apply on the live post-deployment data. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

```
Prediction-drift monitoring progress:
- [ ] 0. Confirm scope: labels available with delay accounted for; model is live; goal documented
- [ ] 1. Construct labeling-delay-aware windows: reference_window.end < today() - labeling_delay_days; same for current_window
- [ ] 2. Score-distribution shift: PSI on y_pred_proba between reference and current; track mean / p50 / p95 of predicted score
- [ ] 3. Calibration check: reliability curve (10 quantile bins) + calibration slope/intercept; report Brier score for each window
- [ ] 4. Per-segment evaluation: AUC, precision, recall, F1 (or RMSE/MAE for regression) per segment with bootstrap 95% CI
- [ ] 5. Erosion vs. reference: compute the delta per segment; flag segments whose CI no longer overlaps the reference CI
- [ ] 6. Diagnose cause: (a) calibration drift (slope/intercept moved), (b) score distribution shift, (c) cohort-mix change, (d) true label-shift / concept drift
- [ ] 7. Recommend: recalibrate (Platt/isotonic) if (a); investigate cohort mix if (c); retrain only after (b) (d) are ruled in
- [ ] 8. Alert payload: severity, segment, metric delta, hypothesis, suggested next action
- [ ] 9. Document the evaluation snapshot for the model-card history
```

### Step 1: Labeling-delay-aware windows

The most common mistake is treating predictions made yesterday as if their labels are observable today. They are not.

- For a 30-day-loan-default model with a 30-90-day mature-to-default delay, set `labeling_delay_days = 90`. The current_window must end at least 90 days before today.
- For a click-prediction model with a 1-hour conversion window, `labeling_delay_days ≈ 1/24`. Windows are near-real-time.
- For a customer-churn model with a 90-day churn definition, `labeling_delay_days = 90`. A "today" current window cannot be evaluated; only windows ending 90+ days ago are interpretable.

Document the labeling-delay assumption explicitly. A wrong assumption silently turns the calibration check into noise.

### Step 3: Calibration

Two views of calibration:

1. **Reliability curve** — bin predictions by `y_pred_proba` (10 quantile bins). For each bin, plot mean predicted probability vs. observed positive rate. A well-calibrated model sits on `y = x`.
2. **Slope / intercept** — logistic regression of `y_true` on `log_odds(y_pred_proba)`. A well-calibrated model has slope ≈ 1, intercept ≈ 0.
   - Slope < 1 → predictions are too extreme (over-confident)
   - Slope > 1 → predictions are too conservative (under-confident)
   - Intercept ≠ 0 → predictions are systematically biased high (intercept < 0) or low (intercept > 0)

**Brier score** = `mean((y_pred_proba - y_true) ** 2)`. Lower is better. Use as a single-number summary that captures both discrimination and calibration.

If only calibration is broken (slope/intercept off, but the score-ranking AUC is stable), apply post-hoc recalibration (Platt or isotonic) — no retraining needed. This is the single largest cost saving the skill produces.

### Step 4: Per-segment evaluation

For each `segment`, compute the metric set + bootstrap 95% CI (≥ 1000 resamples). The interesting signal is not the absolute level, it is the change vs. reference.

Watch for:

- One segment with a wide CI (small n) — do not over-interpret single-segment swings on thin slices
- Segments with deteriorating AUC and stable calibration → discrimination failure, possibly because a feature the model relied on is now noisy in that segment
- Segments with stable AUC and deteriorating calibration → recalibration candidate; retraining is overkill
- New segments not present in reference (e.g., a new geography enrolled mid-year) — these are not "drift", they are first-time observations; handle separately

### Step 6: Cause hierarchy

Always test the cheap hypothesis first:

1. **Calibration drift** — slope / intercept moved, AUC roughly stable. Fix: Platt or isotonic recalibration on recent labeled data. Cost: minutes.
2. **Score distribution shift** — PSI on `y_pred_proba` exceeds the calibrated threshold (use the `monitoring-data-drift` baseline-noise calibration discipline for prediction scores too). Cause: usually a feature or cohort-mix change upstream. Cross-check with the input-side drift monitor.
3. **Per-segment erosion with stable global metrics** — Simpson's-paradox case; population-level metric hides segment-level decay. Action: per-segment recalibration or a segment-aware model.
4. **True label-distribution shift (concept drift)** — `y_true` rate changed (e.g., default rate went from 3% to 6% across all segments). Recalibration alone won't fix; retraining or threshold tuning is appropriate.

Refuse to recommend retraining as the first action when calibration drift is the cheaper, sufficient fix.

## Outputs

A markdown report with:

1. **Window provenance** — reference / current windows with labeling-delay-aware end dates, n predictions, n labels matched, labeling-delay assumption
2. **Score-distribution shift** — PSI on `y_pred_proba`, mean / p50 / p95 deltas
3. **Calibration snapshot** — reliability curve summary, slope / intercept, Brier score; reference vs. current
4. **Per-segment table** — segment · n · AUC + CI · precision + CI · recall + CI · F1 + CI · status (stable / decayed)
5. **Cause hierarchy verdict** — calibration drift / score shift / segment erosion / concept drift (ranked by evidence)
6. **Recommendation** — recalibration / cohort investigation / retrain decision, with explicit cost-vs-impact reasoning
7. **Model-card update** — appended snapshot for the historical post-deployment record

## Failure modes

Known anti-patterns and how this skill catches them:

- **Evaluating on windows where labels are not mature** — caught by step 1 mandatory labeling-delay-aware window construction; running calibration on unlabeled or partially-labeled predictions produces garbage
- **Reporting only global AUC with no per-segment view** — caught by step 4 per-segment evaluation with bootstrap CI; Simpson's paradox hides segment-level erosion
- **Recommending retraining for pure calibration drift** — caught by step 6 cause hierarchy ordering; recalibration is minutes, retraining is days
- **Treating reliability curve "near y=x" as good enough without quantifying** — caught by step 3 slope / intercept + Brier; visual calibration is misleading on imbalanced classes
- **Brier score reported without baseline** — caught by paired reference / current Brier; absolute Brier on a 1%-positive class is dominated by the negative class
- **Per-segment metrics on tiny n (one cohort with 30 predictions) treated as signal** — caught by mandatory bootstrap CI; thin slices have huge CIs and should not drive action
- **Confusing concept drift (label rate moved) with feature drift (inputs moved)** — caught by step 6 forcing the four-cause hypothesis menu; a moved `y_true` rate is concept drift and recalibration alone won't fix
- **Recalibrating on the calibration window then evaluating on the same window** — temporally-aware recalibration: fit on an older labeled subwindow, evaluate on a held-out newer window
- **Letting a new segment introduce itself silently into the per-segment table** — caught by step 4 segment-existence check; first-time segments deserve a separate "new since reference" callout, not a deterioration alert

## References

- `reference/calibration-diagnostics.md` — reliability curve + slope/intercept + Brier recipe with worked example
- `reference/segment-evaluation.md` — per-cohort AUC / F1 tracking with bootstrap CI and Simpson's paradox example
- `reference/label-delay-handling.md` — labeling-delay-aware window construction patterns for common task types
- [Calibration of Modern Neural Networks, Guo et al. 2017](https://arxiv.org/abs/1706.04599) — modern calibration measurement (ECE) and temperature scaling
- [Niculescu-Mizil and Caruana 2005, Platt Scaling and Isotonic Regression](https://www.cs.cornell.edu/~alexn/papers/calibration.icml05.crc.rev3.pdf) — calibration-method comparison
- [NannyML documentation, Performance Estimation](https://nannyml.readthedocs.io/en/stable/tutorials/performance_estimation.html) — open-source library for performance estimation under labeling delay

## Examples

### Example 1: Loan default classifier with stable features but eroding accuracy (happy-path)

Input: *"Our loan-default classifier has been in production for 9 months. Feature drift looks stable (PSI < 0.1 on every feature). But the finance team says actual default rates are higher than the model predicted last quarter. Help me find what shifted."*

Output: Skill identifies this as prediction-side drift with stable inputs — exactly the case this skill is for. Walks the 9-step workflow. Constructs labeling-delay-aware windows (loan defaults take 30-90 days to mature). Computes calibration slope / intercept on the reference 30-day window post-launch (slope ≈ 1.02, intercept ≈ -0.01 — well-calibrated) and on the current 30-day window ending 90 days ago (slope ≈ 0.68, intercept ≈ -0.34 — under-predicting). Reports Brier scores. Identifies this as a calibration-drift case (slope and intercept both moved; per-segment AUC stable). Recommends Platt recalibration on the most recent labeled window, NOT retraining the underlying model. Provides the recalibration code and the validation plan (recalibrate on a hold-out window not used to detect the drift).

### Example 2: Per-segment erosion with stable global metric (edge-case)

Input: *"Our customer-churn classifier has stable global AUC (0.81 vs 0.80 last year) and stable PSI on every feature. But our customer-success team thinks one of our enterprise customer segments has gotten much harder to predict. Is that real or anecdote?"*

Output: Skill recognizes this as a Simpson's-paradox candidate — global metric stable, segment-level erosion suspected. Computes per-segment AUC + bootstrap 95% CI for each customer segment using a labeling-delay-aware window (churn definition delay). Surfaces that the `enterprise_customer` segment AUC has dropped from 0.83 [0.80, 0.86] to 0.71 [0.67, 0.75] — CIs no longer overlap, the erosion is real. SMB and mid-market segments are stable. Calibration on the enterprise segment also moved (slope dropped from 0.98 to 0.62). Recommends: (a) segment-specific recalibration as the immediate fix, (b) investigate whether the enterprise feature distribution changed even though the global PSI is stable (segment-stratified PSI is the right view; global PSI can hide segment-level drift), (c) consider a segment-aware model if the underlying behavior genuinely diverges.

### Example 3: Pre-deployment system (anti-trigger)

Input: *"We're launching a new recommendation model next week. Can you set up prediction-drift monitoring for it now, before launch, so we catch problems on day one?"*

Output: Skill identifies this as a pre-deployment system. Explains that prediction-drift monitoring requires (a) live predictions and (b) labels for those predictions — neither exists yet. Hands off the pre-deployment work to `ml-datasci/evaluating-binary-classifiers` (or the appropriate task-type evaluator) for the launch-readiness scoring on the held-out test set, and `ml-datasci/auditing-train-test-split` for leakage / temporal-order checks. Provides a forward-looking pre-deployment checklist: (1) log per-prediction `prediction_id`, `timestamp`, `y_pred_proba` from day one, (2) define the labeling-delay-days assumption for this task type, (3) pre-stage the prediction-drift monitor code to run once `today() - launch_date > labeling_delay_days`. Does NOT force the full workflow onto a system with no live predictions.

## See also

- `ml-datasci/monitoring-data-drift` — sibling for the input-side feature drift; pair with this skill for a complete drift picture
- `ml-datasci/auditing-inference-latency-budget` — sibling for the latency-side production monitoring
- `ml-datasci/evaluating-binary-classifiers` — the pre-deployment counterpart; use that one until the model is live
- `ml-datasci/evaluating-regression-models` — the regression-task counterpart for pre-deployment evaluation
- `ml-datasci/tuning-classification-threshold` — useful when prediction drift suggests the operating threshold needs revisiting
- `ml-datasci/comparing-models-fairly` — when comparing the recalibrated model against the prior version, use the paired-comparison discipline

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-2, skill 2) via PRAGMATIC discipline
