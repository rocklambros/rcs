---
name: evaluating-binary-classifiers
description: >
  Produces a complete binary-classifier evaluation report from y_true and
  y_pred_proba: ROC curve + PR curve + calibration plot + confusion matrix +
  threshold sweep + class-imbalance check + bootstrap 95% CI on each metric.
  Triggers whenever a trained binary classifier needs scoring, whenever class
  imbalance is suspected, whenever a metric is reported as bare accuracy on
  imbalanced data, or whenever threshold selection is needed. Refuses to lead
  with bare accuracy under imbalance and refuses to default to the 0.5
  threshold without a sweep.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
  - stats-student
evidence:
  - email-spam-classifier-naive-bayes-comparisson-roc
  - multiturn-injection-detection
  - llm-safety-alignment-study
  - DU-MSDSAI-4432-TitanicSurvivalClassifiers
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
last-updated: 2026-05-23
---

# Evaluating Binary Classifiers

## When to use

Trigger this skill when:

- A trained binary classifier (logistic regression, gradient-boosted trees, neural net, naive Bayes, etc.) needs to be scored or certified for deployment
- Only `accuracy` is reported on a dataset where the minority class is plausibly under 20%
- A single number (AUC, F1, precision) is reported without a confidence interval or threshold context
- The user asks how to pick a classification threshold or says "I'm using 0.5"
- The user pastes `y_true` and `y_pred_proba` arrays (or equivalent) and asks for an evaluation
- Keywords: ROC, PR curve, AUC, calibration, confusion matrix, threshold, precision/recall, class imbalance, F1, MCC, bootstrap CI on a classifier

## When NOT to use

Skip this skill and hand off when:

- The classifier is multi-class (3+ labels) → use `ml-datasci/evaluating-multiclass-classifiers` (planned). One-vs-rest ROC on a 3-class problem is a workaround, not the right tool.
- The task is regression → use `ml-datasci/evaluating-regression-models`.
- The task is ranking or retrieval (recall@k / nDCG) → use `ml-datasci/evaluating-rag-retrieval` (planned).
- The user wants to pick a model rather than score one fitted model → use `ml-datasci/comparing-models-fairly` (planned, McNemar / paired-folds).
- The user wants a leakage audit on the train/test split → use `ml-datasci/auditing-train-test-split`.
- The request is pure pedagogy on what AUC means without a real model — explain the concept; do not force the full report.

## Quick start

User: "I trained a logistic regression on spam vs ham. I have `y_true` and `y_pred_proba` as NumPy arrays. Evaluate it."

Response: the full report defined below — class-balance check first, then ROC + PR + calibration + confusion matrix at default + threshold sweep + bootstrap 95% CIs on AUC and F1 — using `sklearn.metrics` + matplotlib.

```python
from sklearn.metrics import (
    roc_curve, precision_recall_curve, roc_auc_score,
    average_precision_score, confusion_matrix, f1_score,
)
from sklearn.calibration import calibration_curve
import numpy as np

# 1. Class balance check (lead with this)
print(f"positive rate: {y_true.mean():.4f}")

# 2. Threshold-free metrics with bootstrap 95% CI (see reference/bootstrap-ci.md)
roc_auc = roc_auc_score(y_true, y_pred_proba)
pr_auc  = average_precision_score(y_true, y_pred_proba)
```

See `reference/binary-eval-checklist.md` for the full report template; `reference/bootstrap-ci.md` for the bootstrap recipe; `reference/threshold-sweep-recipe.md` for the sweep template.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `y_true` | array-like of {0, 1} | yes | — | Ground-truth binary labels for the held-out (test) set. |
| `y_pred_proba` | array-like of float in [0, 1] | yes | — | Predicted probability of the positive class. Must align row-wise with `y_true`. |
| `positive_label` | int / str | no | `1` | Which class is "positive" (e.g. spam, fraud, malicious). |
| `cost_ratio` | float | no | `1.0` | Ratio of FN-cost to FP-cost. Drives threshold selection on the sweep. For fraud / security: typically > 1 (missing a positive is worse). |
| `n_bootstrap` | int | no | `1000` | Number of bootstrap resamples for 95% CI on AUC and F1. |
| `thresholds` | array-like | no | `np.linspace(0.01, 0.99, 99)` | Threshold grid for the sweep. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check items off as the evaluation progresses:

```
Binary-classifier eval progress:
- [ ] 0. Sanity checks (arrays align; y_pred_proba in [0, 1]; both classes present in y_true)
- [ ] 1. Class-balance check — report positive rate; flag if < 20% (or > 80%)
- [ ] 2. Threshold-free metrics: ROC-AUC + PR-AUC, each with bootstrap 95% CI
- [ ] 3. ROC curve + PR curve plotted; PR leads under class imbalance
- [ ] 4. Calibration plot (reliability diagram) + Brier score
- [ ] 5. Confusion matrix at default 0.5 threshold (reference only, not the final choice)
- [ ] 6. Threshold sweep — precision/recall/F1/MCC vs threshold; pick optimal per cost_ratio
- [ ] 7. Confusion matrix + precision/recall/specificity/F1 at the chosen threshold (with CI)
- [ ] 8. Report block: assumptions, chosen threshold + justification, residual risks
```

### Step 1: Class-balance check (lead with this)

Compute and print `positive_rate = y_true.mean()`. If outside `[0.2, 0.8]`, the data are imbalanced. In that case:

- **Lead the report with PR-AUC**, not ROC-AUC. ROC-AUC is misleadingly optimistic under heavy imbalance (false positives in a huge negative class are diluted).
- **Refuse to lead with bare accuracy.** A 99% fraud-classifier accuracy on 1% fraud is the always-predict-negative baseline.

### Step 2: Threshold-free metrics with bootstrap 95% CI

Report `ROC-AUC` and `PR-AUC`, each with a 95% CI via bootstrap resampling of `(y_true, y_pred_proba)` rows (n_bootstrap ≥ 1000). Stratify the resample by class when either class has < 100 examples. See `reference/bootstrap-ci.md`.

### Step 3: ROC + PR plots

Plot both. Annotate AUC values. Under imbalance, place the PR plot first in the report.

### Step 4: Calibration

Use `sklearn.calibration.calibration_curve` with `n_bins=10` (or fewer if the test set is small) and plot the reliability diagram. Report Brier score. If miscalibrated, recommend Platt scaling or isotonic regression as a post-hoc fix and re-evaluate.

### Step 5: Confusion matrix at default threshold

Report for reference only. Always pair with a threshold-swept version.

### Step 6: Threshold sweep

Plot precision, recall, F1, and MCC versus threshold across `np.linspace(0.01, 0.99, 99)`. Choose the operating threshold by:

- If `cost_ratio = 1`: argmax F1 (or argmax MCC)
- If `cost_ratio > 1` (FN-cost dominant — fraud, security): use cost-aware loss `cost = FP + cost_ratio * FN`; pick the threshold minimizing it
- If a hard precision floor is specified: pick the highest-recall threshold meeting the floor

Document the choice in the report.

### Step 7: Confusion matrix + metrics at chosen threshold

Report TP / FP / TN / FN + precision / recall / specificity / F1 / MCC at the chosen threshold, each with a 95% CI (bootstrap).

### Step 8: Report block

Final report includes: dataset positive rate, chosen threshold + rationale, all metrics with CIs, calibration verdict, and residual risks (drift sensitivity, class-imbalance fragility).

## Outputs

A markdown report with this structure:

1. **Dataset summary** — n, positive rate, missing-value handling
2. **Threshold-free** — PR-AUC and ROC-AUC, each `metric = value [95% CI: low, high]`; PR-AUC leads under imbalance
3. **Calibration** — reliability diagram, Brier score, verdict (well-calibrated / over- / under-confident)
4. **Threshold selection** — sweep plot + chosen threshold + rationale (cost_ratio or floor)
5. **At chosen threshold** — confusion matrix + per-metric value + 95% CI
6. **Residual risks** — sensitivity to drift, calibration fragility, sample-size caveats

## Failure modes

Known anti-patterns and how this skill catches them:

- **Bare accuracy on imbalanced data** — caught by step 1 class-balance check + explicit refusal to lead with accuracy.
- **Default 0.5 threshold without justification** — caught by step 6 threshold sweep; 0.5 is reference, not choice.
- **ROC-only on imbalanced data** — caught by step 3 placing PR ahead of ROC under imbalance.
- **Point estimates without CIs** — caught by bootstrap CI requirement on AUC and F1.
- **Miscalibration ignored** — caught by step 4 reliability diagram + Brier score.
- **Same-data threshold-pick + test report** — pick the threshold on a validation slice; report on held-out test. Note this caveat in the report.
- **Multi-class shoehorned into binary** — caught by `When NOT to use`; hand off to the multiclass skill.

## References

- `reference/binary-eval-checklist.md` — copy-paste report template
- `reference/bootstrap-ci.md` — stratified bootstrap recipe for AUC and F1 CIs
- `reference/threshold-sweep-recipe.md` — sweep template + cost-aware threshold selector
- [scikit-learn metrics user guide](https://scikit-learn.org/stable/modules/model_evaluation.html) — definitions of ROC-AUC, PR-AUC, Brier, MCC
- [Saito & Rehmsmeier 2015 *The PR plot is more informative than ROC when evaluating binary classifiers on imbalanced datasets*, PLOS ONE](https://doi.org/10.1371/journal.pone.0118432) — empirical case for PR-first under imbalance

## Examples

### Example 1: Spam classifier on roughly balanced data (happy-path)

Input: "Logistic regression on spam vs ham. y_true and y_pred_proba arrays. Positive rate ≈ 0.45. Evaluate."

Output: Skill produces the full 8-step report. ROC-AUC + PR-AUC both reported with bootstrap CIs; ROC plot leads because data are balanced; calibration plot + Brier score; threshold sweep with argmax-F1 choice (cost_ratio = 1 default); confusion matrix + per-metric CIs at the chosen threshold.

### Example 2: Fraud classifier with extreme imbalance (edge-case)

Input: "My fraud classifier has 99% accuracy. Sounds great, right?"

Output: Skill flags the suspicion immediately. Asks for the positive rate. Explains that 99% accuracy on a 1%-fraud problem is the always-predict-negative baseline. Recommends recomputing with PR-AUC leading, per-class recall, MCC, and a cost-aware threshold (cost_ratio > 1 for fraud). Refuses to certify the classifier without that report.

### Example 3: Hand-off on multi-class (anti-trigger)

Input: "I have a 3-class classifier — benign, malicious, suspicious. Evaluate it."

Output: Skill identifies the request as multi-class, not binary. Names the limits of one-vs-rest ROC for diagnostic decisions. Hands off to `evaluating-multiclass-classifiers` (planned) and offers a minimal stopgap (per-class precision/recall + confusion matrix) without forcing the binary report template.

## See also

- `ml-datasci/evaluating-regression-models` — the regression analogue of this skill
- `ml-datasci/building-baseline-models` — required pre-step; without a baseline, the metrics here have no comparison context
- `ml-datasci/auditing-train-test-split` — required pre-step; evaluating on a leaky split inflates every metric here
- `ml-datasci/reporting-effect-sizes` — sibling for hypothesis-test reporting (this skill is the classifier analogue)
- `ml-datasci/tuning-classification-threshold` (planned) — deeper dive on cost-aware threshold selection

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (Batch 3, skill 3.1) via PRAGMATIC discipline
