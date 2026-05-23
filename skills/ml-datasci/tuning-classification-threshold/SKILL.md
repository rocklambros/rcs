---
name: tuning-classification-threshold
description: >
  Selects a classification decision threshold using a domain-aware sweep instead
  of the default 0.5: F-beta optimization (beta > 1 when recall matters,
  beta < 1 when precision matters), TPR-at-fixed-FPR (security and medical
  screening with hard FPR budgets), precision-at-fixed-recall, and full
  cost-weighted loss with an explicit FN-cost-to-FP-cost ratio (which is
  typically 10x to 1000x in fraud, security, and medical use cases). Requires
  threshold selection on a validation slice and final reporting on a held-out
  test slice to avoid optimistic bias. Triggers whenever a trained binary
  classifier is moving to deployment, whenever a user reports a metric at
  threshold 0.5 without justification, whenever the user mentions a hard FPR /
  precision / recall budget, or whenever a cost-asymmetry exists (FN cost not
  equal to FP cost). Refuses to recommend 0.5 by default and refuses to pick
  the threshold on the test set.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
evidence:
  - multiturn-injection-detection
  - llm-safety-alignment-study
  - email-spam-classifier-naive-bayes-comparisson-roc
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
last-updated: 2026-05-23
---

# Tuning Classification Threshold

## When to use

Trigger this skill when:

- A trained binary classifier is being moved to deployment and the operating decision rule (threshold) needs to be chosen
- A metric is reported at threshold 0.5 without justification ("F1 = 0.78 at 0.5")
- The user mentions a hard FPR budget, hard precision floor, or hard recall floor (compliance, security alert volume, SLA on review queue)
- The use case has cost asymmetry — FN cost is materially different from FP cost (fraud, security alerts, medical screening, content moderation, churn intervention)
- The user asks "what threshold should I use?", "how do I pick the cutoff?", "is 0.5 the right threshold?", or shows an ROC / PR curve and asks for an operating point
- Keywords: threshold, cutoff, operating point, decision rule, F-beta, TPR at FPR, precision at recall, cost-weighted, Youden's J, expected cost

## When NOT to use

Skip this skill and hand off when:

- The task is multi-class with a softmax argmax and no operating-point question (the decision rule is "max probability class") → for multi-class threshold variants (top-1 with reject, per-class cost-weighted), use `ml-datasci/evaluating-multiclass-classifiers` plus a custom cost matrix
- The task is regression → no threshold to tune; use `ml-datasci/evaluating-regression-models`
- The user wants the full evaluation report (ROC, PR, calibration, CM, sweep) and not just the threshold pick → use `ml-datasci/evaluating-binary-classifiers`; this skill is the focused threshold-selection subset
- The classifier is uncalibrated and the user wants a probabilistic threshold ("alert if probability > 0.7") → calibrate first (Platt or isotonic); a 0.7 probability on an uncalibrated model is not a 0.7 probability
- The user wants to pick between models rather than pick a threshold → use `ml-datasci/comparing-models-fairly` (planned)
- The request is pure pedagogy on what threshold tuning does without a real classifier — explain the concept; do not force the workflow

## Quick start

User: "Fraud classifier on credit transactions. y_true and y_pred_proba on a held-out set. Missing a fraud is ~100x worse than a false alarm. What threshold?"

Response: cost-weighted sweep with `cost_ratio = 100`. Pick the threshold minimizing `cost = FP + 100 * FN` on a validation slice. Report the chosen threshold along with precision / recall / TPR / FPR at that threshold on the held-out test slice — never on the slice used to pick.

```python
from sklearn.metrics import roc_curve, precision_recall_curve, confusion_matrix
import numpy as np

# 1. Compute precision / recall across thresholds on the VALIDATION slice
fpr, tpr, t_roc = roc_curve(y_val, p_val)
precision, recall, t_pr = precision_recall_curve(y_val, p_val)

# 2. Cost-aware sweep
cost_ratio = 100  # FN cost / FP cost
thresholds = np.linspace(0.001, 0.999, 999)
costs = []
for t in thresholds:
    pred = (p_val >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_val, pred).ravel()
    costs.append(fp + cost_ratio * fn)
t_star = thresholds[int(np.argmin(costs))]

# 3. Report on TEST slice (not validation)
pred_test = (p_test >= t_star).astype(int)
```

See `reference/threshold-selection-recipes.md` for the full library of selectors (F-beta, TPR-at-FPR, precision-at-recall, cost-weighted, Youden's J).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `y_val` | array-like of {0, 1} | yes | — | Ground-truth labels on the validation slice used to PICK the threshold. |
| `p_val` | array-like of float in [0, 1] | yes | — | Predicted positive-class probabilities on the validation slice. Must align with `y_val`. |
| `y_test` | array-like of {0, 1} | yes | — | Ground-truth labels on the held-out test slice used to REPORT the chosen-threshold metrics. |
| `p_test` | array-like of float in [0, 1] | yes | — | Predicted positive-class probabilities on the test slice. |
| `selector` | str | yes | — | One of `f-beta`, `tpr-at-fpr`, `precision-at-recall`, `cost-weighted`, `youdens-j`. Picks the selection criterion. |
| `beta` | float | conditional | `1.0` | Required when `selector = 'f-beta'`. `> 1` weights recall; `< 1` weights precision. |
| `fpr_budget` | float | conditional | — | Required when `selector = 'tpr-at-fpr'`. Hard cap on FPR (e.g. 0.01 for "1% false alarm rate"). |
| `recall_floor` | float | conditional | — | Required when `selector = 'precision-at-recall'`. Minimum recall the operating point must satisfy (e.g. 0.95). |
| `cost_ratio` | float | conditional | — | Required when `selector = 'cost-weighted'`. Ratio of FN-cost to FP-cost. Document the source (cost model, business policy, regulatory floor). |
| `thresholds` | array-like | no | `np.linspace(0.001, 0.999, 999)` | Threshold grid. |
| `calibration_check` | bool | no | `True` | Verify the model is calibrated (Brier vs always-predict-base-rate baseline) before applying a probability threshold. |

## Workflow

```
Threshold selection progress:
- [ ] 0. Sanity check — y and p align; both classes present in y_val and y_test; probabilities in [0, 1]
- [ ] 1. Calibration check on val (Brier vs baseline); if uncalibrated, calibrate (Platt or isotonic) BEFORE selection
- [ ] 2. Choose selector + parameter (justify per cost model / SLA / regulatory floor)
- [ ] 3. Compute sweep across thresholds ON VALIDATION (precision / recall / TPR / FPR / F-beta / expected cost as appropriate)
- [ ] 4. Pick threshold per selector
- [ ] 5. Report chosen-threshold metrics ON TEST (precision / recall / TPR / FPR / confusion matrix + 95% CI)
- [ ] 6. Note residual risks (selector-vs-deployment-cost mismatch, drift sensitivity, calibration fragility)
```

### Step 1: Calibration check

A "probability threshold" only makes sense if the model is calibrated. Compute Brier on val and compare to the always-predict-base-rate baseline. If Brier is worse than baseline or the reliability diagram shows systematic over/underconfidence, calibrate via Platt scaling or isotonic regression on a held-out fold BEFORE picking the threshold. Document the calibration step in the report.

### Step 2: Choose the selector

| Selector | Use when | Parameter |
|---|---|---|
| `f-beta` | No hard budget; just want a precision-recall trade-off knob. `beta=1` is F1; `beta=2` weights recall 2x precision; `beta=0.5` weights precision 2x recall. | `beta` |
| `tpr-at-fpr` | Hard FPR budget (alert volume in a SOC, false-alarm rate in medical screening, compliance ceiling on user disruption). | `fpr_budget` |
| `precision-at-recall` | Hard recall floor (regulatory must-catch rate, SLA on missed cases). | `recall_floor` |
| `cost-weighted` | Explicit business / clinical / security cost asymmetry. `cost_ratio = FN-cost / FP-cost`; in fraud often 50-500, in cancer screening often 1000+. | `cost_ratio` |
| `youdens-j` | Roughly balanced costs and no hard budget; maximizes `TPR - FPR`. Use as a fallback when no domain signal is available; flag the lack of cost model in the report. | — |

Refuse to default to `0.5`. The default 0.5 is only correct when `cost_ratio = 1` AND class base rate is 0.5 AND the classifier is perfectly calibrated.

### Step 3: Sweep on validation

Compute the selector's metric across the threshold grid on the validation slice. Plot:

- For `f-beta`: F-beta vs threshold; mark argmax
- For `tpr-at-fpr`: TPR vs FPR; mark the operating point at the FPR budget
- For `precision-at-recall`: precision vs recall; mark the operating point at the recall floor
- For `cost-weighted`: expected cost vs threshold; mark argmin
- For `youdens-j`: TPR - FPR vs threshold; mark argmax

### Step 4: Pick the threshold

Read off the threshold corresponding to the optimal point. If multiple thresholds achieve the optimum (tie), pick the highest threshold (more conservative on the positive class) and document the tie.

### Step 5: Report on test

Apply the chosen threshold to `p_test`. Report the chosen-threshold confusion matrix and metrics on `y_test` / `p_test` with bootstrap 95% CIs. The test metrics are the deployment-realistic ones — validation metrics at the chosen threshold are optimistic because the threshold was picked on that slice.

### Step 6: Residual risks

Document:

- **Selector-vs-deployment-cost mismatch**: if the team used `youdens-j` because no cost model was available, note that production cost asymmetry may warrant a re-tune
- **Drift sensitivity**: a threshold tuned on a snapshot drifts as the score distribution drifts; recommend periodic re-tuning
- **Calibration fragility**: if Platt or isotonic was used, note that calibration trained on val may degrade on test or in production
- **Sample-size caveats**: tiny validation slices give noisy threshold picks; recommend k-fold tuning if val is small

## Outputs

A markdown report with this structure:

1. **Calibration verdict** — Brier vs baseline; calibrated / re-calibrated / verdict
2. **Selector + parameter** — which selector, why, parameter source
3. **Validation sweep** — sweep plot + chosen threshold
4. **Test-slice report** — confusion matrix + precision / recall / TPR / FPR / F-beta / expected cost at the chosen threshold, each with 95% CI
5. **Residual risks** — drift sensitivity, calibration fragility, sample-size caveats

## Failure modes

Known anti-patterns and how this skill catches them:

- **Default 0.5 with no justification** — caught by step 2 explicit selector + parameter requirement.
- **Threshold picked on test set** — optimistic bias; caught by enforced val/test separation. The skill rejects single-slice inputs and demands `y_val + y_test`.
- **Probability threshold on an uncalibrated model** — meaningless; caught by step 1 calibration check.
- **`cost_ratio = 1` assumed without domain check** — caught by step 2 selector parameter being required, not defaulted.
- **F1 (beta = 1) reported as "the" optimum on an asymmetric-cost task** — F1 implies symmetric costs; caught by step 2 cost-model justification.
- **TPR-at-FPR without naming the FPR budget** — meaningless; caught by required `fpr_budget` parameter.
- **Same-data tune-and-report** — caught by val/test separation.
- **Drift-blind deployment** — caught by step 6 residual-risks block recommending periodic re-tuning.

## References

- `reference/threshold-selection-recipes.md` — copy-paste implementations for each selector (F-beta, TPR-at-FPR, precision-at-recall, cost-weighted, Youden's J)
- [scikit-learn precision-recall and ROC](https://scikit-learn.org/stable/modules/model_evaluation.html#precision-recall-and-f-measures) — definitions
- [Youden 1950 *Index for rating diagnostic tests*](https://doi.org/10.1002/1097-0142%281950%293%3A1%3C32%3A%3AAID-CNCR2820030106%3E3.0.CO%3B2-3) — Youden's J origin
- [Drummond and Holte 2006 *Cost curves: An improved method for visualizing classifier performance*](https://doi.org/10.1007/s10994-006-8199-5) — cost-curve foundations

## Examples

### Example 1: Fraud with FN >> FP cost (happy-path)

Input: "Credit-card fraud classifier on a 50,000-transaction test set. Base rate of fraud is about 0.6%. Missing a fraud costs roughly 100x a false alarm (analyst review overhead). I have y_val, p_val, y_test, p_test. What threshold?"

Output: Skill picks `selector = 'cost-weighted'` with `cost_ratio = 100`. Calibrates if needed. Computes expected cost across thresholds on val, picks `t*` at argmin. Reports the test-slice confusion matrix + precision / recall / TPR / FPR at `t*` with bootstrap CIs. Notes that the chosen threshold will likely be far below 0.5 (because false negatives dominate the cost). Flags drift sensitivity and recommends quarterly re-tuning as the fraud distribution shifts.

### Example 2: Unknown cost model (edge-case)

Input: "Internal classifier flagging anomalous user sessions. We don't have a cost model — no one has quantified the FP / FN trade-off in dollars. Just give me the threshold."

Output: Skill refuses to silently default to `cost_ratio = 1`. Either elicits a cost proxy (analyst-hour cost vs miss-incident-cost rough estimate) OR uses `selector = 'youdens-j'` as a conservative cost-blind default, documenting in the report that the lack of cost model means the threshold may need re-tuning once cost is quantified. Alternative: suggests `selector = 'tpr-at-fpr'` with `fpr_budget` set by the team's review capacity (e.g. "we can review at most 50 flags per day → FPR budget = 50 / negatives per day").

### Example 3: Multi-class softmax argmax (anti-trigger)

Input: "I have a 5-class intent classifier. The decision rule is argmax over the softmax. Help me tune the threshold."

Output: Skill identifies that multi-class softmax-argmax has no single threshold to tune — the decision rule is "max-probability class". Names variants that DO have tunable thresholds in multi-class (top-1 with reject below a confidence floor; per-class cost-weighted argmax via a `K x K` cost matrix) and hands off to `evaluating-multiclass-classifiers` for the broader multi-class evaluation. Does not force the binary threshold-selection workflow on a multi-class softmax.

## See also

- `ml-datasci/evaluating-binary-classifiers` — full binary evaluation report; this skill is the focused threshold-selection subset
- `ml-datasci/evaluating-multiclass-classifiers` — multi-class evaluation; hand off when the task is 3+ classes with softmax argmax
- `ml-datasci/auditing-train-test-split` — required pre-step; if val and test leak into each other, threshold selection is meaningless
- `ml-datasci/building-baseline-models` — required pre-step; a DummyClassifier at the chosen threshold gives the cost-baseline that contextualizes the selection
- `ml-datasci/reporting-effect-sizes` — sibling for hypothesis-test reporting

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-1, skill 2) via PRAGMATIC discipline
