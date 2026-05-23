---
name: evaluating-multiclass-classifiers
description: >
  Produces a complete multi-class classifier evaluation report from y_true
  (integer or string labels, 3+ classes) and y_pred_proba (n_samples x n_classes
  matrix): per-class precision / recall / F1, macro-F1 + weighted-F1 + micro-F1,
  full K x K confusion matrix (counts plus row-normalized), top-k accuracy where
  k makes sense, one-vs-rest ROC and PR per class, per-class support, and class
  imbalance check. Triggers whenever a trained classifier has 3 or more labels
  (image classification across N categories, intent classification, multi-class
  vulnerability triage, ICD-code prediction). Refuses to lead with bare overall
  accuracy under imbalance, refuses to report only macro-F1 without naming
  whether macro or weighted matches the deployment cost model, and hands off to
  evaluating-binary-classifiers when the task is actually two-class.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
  - stats-student
evidence:
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - llm-toxicity-visual-analysis
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Evaluating Multi-Class Classifiers

## When to use

Trigger this skill when:

- A trained classifier produces 3 or more labels (image classes, intent buckets, severity tiers, ICD codes, language IDs, attack categories) and needs to be scored or certified for deployment
- The user pastes a `y_true` array of integer / string labels with `n_classes >= 3` and a `y_pred_proba` matrix of shape `(n_samples, n_classes)` and asks for an evaluation
- Only overall `accuracy` is reported for a 3+-class task, especially when one or more classes is rare
- The user mentions per-class metrics, macro-F1, weighted-F1, one-vs-rest ROC, top-k accuracy, or a `K x K` confusion matrix
- A multi-class report exists but the user is unsure whether to lead with macro or weighted aggregation
- Keywords: macro-F1, weighted-F1, micro-F1, per-class precision, top-k, one-vs-rest, K x K confusion, Cohen's kappa, multiclass log loss

## When NOT to use

Skip this skill and hand off when:

- The task is binary (2 labels) → use `ml-datasci/evaluating-binary-classifiers`. One-vs-rest aggregations on a binary task are just the binary metrics with extra plumbing.
- The task is multi-label (each sample can belong to multiple classes simultaneously) → multi-label needs per-label binarization and Hamming loss / subset accuracy. This skill assumes single-label-per-sample.
- The task is regression → use `ml-datasci/evaluating-regression-models`.
- The task is ranking / retrieval (recall@k on documents) → use `ml-datasci/evaluating-rag-retrieval` (planned).
- The user wants to pick between models rather than score one fitted model → use `ml-datasci/comparing-models-fairly` (planned, paired McNemar on multi-class is via per-class binarization or via a paired-folds approach).
- The user wants a leakage audit on the train/test split → use `ml-datasci/auditing-train-test-split`.
- The request is pure pedagogy on what macro-F1 means without a real model — explain the concept and do not force the full report.

## Quick start

User: "I trained a 5-class image classifier on a hospital diagnosis dataset. I have `y_true` (integer labels 0-4) and `y_pred_proba` (shape `(n, 5)`). Evaluate it."

Response: the full report defined below — class-balance check first, per-class precision / recall / F1 with support, macro / weighted / micro aggregations, full 5 x 5 confusion matrix (counts plus row-normalized), top-2 accuracy, one-vs-rest ROC and PR per class, calibration check via multi-class log loss + Brier, Cohen's kappa.

```python
from sklearn.metrics import (
    classification_report, confusion_matrix, top_k_accuracy_score,
    cohen_kappa_score, log_loss, roc_auc_score, average_precision_score,
)
import numpy as np

y_pred = y_pred_proba.argmax(axis=1)

# 1. Class balance check (lead with this)
classes, counts = np.unique(y_true, return_counts=True)
print(dict(zip(classes, counts / counts.sum())))

# 2. Per-class + aggregated metrics
print(classification_report(y_true, y_pred, digits=4))

# 3. K x K confusion matrix
print(confusion_matrix(y_true, y_pred))
```

See `reference/multiclass-eval-checklist.md` for the full report template and `reference/aggregation-choice.md` for how to pick between macro / weighted / micro.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `y_true` | array-like of int or str | yes | — | Ground-truth class labels for the held-out (test) set; must have at least 3 distinct values represented across train + test. |
| `y_pred_proba` | array-like of shape `(n_samples, n_classes)` | yes | — | Predicted probability per class. Rows must sum to ~1.0. Column order must match the `classes_` attribute of the fitted model. |
| `class_names` | list of str | no | derived from `y_true` | Human-readable class labels for the confusion matrix axes and the per-class report. |
| `top_k` | int | no | `min(3, n_classes - 1)` | Compute top-k accuracy. Skip if `n_classes == 3` and `k == 2` is uninformative (random baseline already at 2/3). |
| `cost_matrix` | array-like of shape `(n_classes, n_classes)` | no | uniform | Optional `K x K` cost matrix `C[i, j]` = cost of predicting `j` when truth is `i`. Drives weighted-F1 vs macro-F1 selection per `reference/aggregation-choice.md`. |
| `n_bootstrap` | int | no | `1000` | Bootstrap resamples for 95% CI on macro-F1 and per-class F1. Stratify by class. |

## Workflow

Copy this checklist into the response and check items off as the evaluation progresses.

```
Multi-class eval progress:
- [ ] 0. Sanity checks (n_classes >= 3 in y_true; y_pred_proba rows sum to 1.0; class order alignment confirmed)
- [ ] 1. Class-balance check — per-class support and proportion; flag imbalance ratio max/min > 10
- [ ] 2. Per-class precision / recall / F1 + support (sklearn classification_report)
- [ ] 3. Aggregated F1: macro AND weighted AND micro; pick the right one for the cost model (see reference/aggregation-choice.md)
- [ ] 4. Full K x K confusion matrix in BOTH counts and row-normalized form
- [ ] 5. Top-k accuracy where k makes sense (k=3 default for K>=5; skip when k == K-1)
- [ ] 6. One-vs-rest ROC and PR per class; report per-class AUC and average-precision
- [ ] 7. Multi-class log loss and Brier score; Cohen's kappa for inter-rater agreement framing
- [ ] 8. Bootstrap 95% CI on macro-F1 and per-class F1
- [ ] 9. Confusion-pair audit: name the top 2-3 off-diagonal cells; check whether they are domain-meaningful (e.g. melanoma confused with nevus, not melanoma confused with broken-bone)
- [ ] 10. Report block: aggregation rationale, per-class verdict, dominant confusions, residual risks
```

### Step 1: Class-balance check (lead with this)

Report per-class support and proportion. Compute `imbalance_ratio = max(counts) / min(counts)`. If `imbalance_ratio > 10`:

- Lead the report with weighted-F1 if deployment cost scales with class frequency (e.g. overall user-facing accuracy on a skewed traffic mix)
- Lead with macro-F1 if every class matters equally regardless of frequency (e.g. rare-disease screening, rare-attack detection)
- Refuse to lead with bare overall accuracy. On a 10-class dataset where one class is 50% of the data, predicting always-class-0 gets 50% accuracy.

### Step 2: Per-class precision / recall / F1 + support

Use `sklearn.metrics.classification_report(y_true, y_pred, digits=4)`. Read the per-class rows individually before reading the aggregate rows. A high macro-F1 hides per-class collapse on the rarest 2-3 classes.

### Step 3: Pick the right aggregation

| Aggregation | When to lead with it |
|---|---|
| **macro-F1** | Every class matters equally (fairness, rare-class detection, balanced-fairness mandate). Penalizes per-class collapse. |
| **weighted-F1** | Deployment cost scales with class frequency (overall user-facing accuracy). Forgives collapse on rare classes. |
| **micro-F1** | Equivalent to overall accuracy in a single-label multi-class setting. Useful only as a sanity check, not as the lead metric. |

Report all three. Justify which one the report leads with using the cost model. If a `cost_matrix` was provided, also report cost-weighted-F1 per `reference/aggregation-choice.md`.

### Step 4: Full K x K confusion matrix in two views

Always render both views. The counts version shows scale (a `13 -> 14` confusion of 200 instances is different from a confusion of 2 instances). The row-normalized version shows per-class behavior independent of class size (rare-class recall is impossible to read off the raw counts).

### Step 5: Top-k accuracy

Default `k = min(3, n_classes - 1)`. Skip when `k = n_classes - 1` because the metric collapses (only one wrong class to exclude). Top-k is informative when there is a downstream re-ranker, a human-in-the-loop reviewer, or when the prediction is the seed of a candidate set.

### Step 6: One-vs-rest ROC and PR per class

For each class `c`, treat it as the positive class against all others. Report per-class ROC-AUC and average-precision. Under heavy class imbalance for class `c`, lead with PR for that class. Note in the report that one-vs-rest aggregations are diagnostic, not the lead metric.

### Step 7: Calibration and agreement

- **Multi-class log loss**: `sklearn.metrics.log_loss(y_true, y_pred_proba)` — penalizes confidently wrong predictions
- **Multi-class Brier**: mean of `sum_c (y_true_one_hot[c] - y_pred_proba[c])^2`
- **Cohen's kappa**: agreement against chance. Useful when classes are imbalanced or when the report needs an inter-rater-agreement framing (e.g. clinician vs model)

### Step 8: Bootstrap 95% CI

Stratified bootstrap by class with `n_bootstrap = 1000`. Report CIs for macro-F1 and for the per-class F1 of every class with support < 100 (rare classes have wide CIs that point estimates hide).

### Step 9: Confusion-pair audit

Sort the off-diagonal cells of the row-normalized confusion matrix in descending order. Pick the top 2-3 pairs. For each, name the pair (e.g. `class_2 -> class_5` = 18% of true class_2 misclassified as class_5) and ask whether this confusion is domain-meaningful (e.g. visually similar species, semantically close intents) or whether it signals a labeling error / leakage / collapsed feature representation.

### Step 10: Report block

Final report includes: dataset class distribution, aggregation rationale, per-class precision / recall / F1 with support, K x K confusion (both views), top-k where informative, per-class one-vs-rest AUC and AP, log loss + kappa, dominant confusions named, residual risks.

## Outputs

A markdown report with this structure:

1. **Dataset summary** — n, per-class support and proportion, imbalance ratio, label source / split source
2. **Aggregation choice** — macro vs weighted vs micro; justification using the cost model
3. **Per-class table** — precision / recall / F1 / support per class, sorted by support ascending (so the rare classes are read first)
4. **K x K confusion matrix** — both counts and row-normalized
5. **Top-k accuracy** — if `k` is informative
6. **Per-class one-vs-rest** — ROC-AUC and AP per class
7. **Calibration and agreement** — multi-class log loss, Brier, Cohen's kappa
8. **CIs** — bootstrap 95% CI on macro-F1 and per-class F1 for rare classes
9. **Dominant confusions** — top 2-3 confusion pairs with domain interpretation
10. **Residual risks** — sample-size caveats for rare classes, drift sensitivity, single-label assumption

## Failure modes

Known anti-patterns and how this skill catches them:

- **Bare overall accuracy on imbalanced multi-class** — caught by step 1 imbalance ratio + explicit refusal to lead with overall accuracy when ratio > 10.
- **Macro-F1 reported as "the" metric without justification** — caught by step 3 explicit aggregation choice with cost-model justification.
- **Per-class collapse hidden by macro average** — caught by step 2 reading per-class rows before aggregates and step 9 confusion-pair audit.
- **K x K confusion in counts only** — counts-only hides rare-class recall; step 4 mandates row-normalized view alongside.
- **Top-k abused as the lead** — caught by step 5; top-k is supporting, not lead.
- **One-vs-rest ROC treated as the lead metric** — caught by step 6 framing as diagnostic.
- **Point estimates for rare-class F1** — rare-class CIs are huge; step 8 bootstrap CI is mandatory for classes with support < 100.
- **Binary task forced into the multiclass template** — caught by `When NOT to use`; hand off to evaluating-binary-classifiers.
- **Multi-label task treated as multi-class** — multi-label needs per-label binarization and Hamming loss / subset accuracy; the skill rejects single-label-per-sample assumption violations.

## References

- `reference/multiclass-eval-checklist.md` — copy-paste report template
- `reference/aggregation-choice.md` — macro vs weighted vs micro decision rule with cost-model framing
- [scikit-learn multiclass metrics guide](https://scikit-learn.org/stable/modules/model_evaluation.html#multiclass-and-multilabel-classification) — definitions of macro / weighted / micro averaging
- [Cohen 1960 *A Coefficient of Agreement for Nominal Scales*](https://doi.org/10.1177/001316446002000104) — Cohen's kappa origin

## Examples

### Example 1: 5-class image diagnosis classifier (happy-path)

Input: "5-class hospital diagnosis classifier on tabular + image features. `y_true` integer labels 0-4. `y_pred_proba` shape `(n, 5)`. Roughly balanced per class. Evaluate."

Output: Skill produces the full 10-step report. Per-class precision / recall / F1 with support; macro-F1 leads because every class matters equally in a clinical setting; full 5 x 5 confusion matrix in counts and row-normalized; top-3 accuracy as a supporting metric for downstream review; one-vs-rest ROC + AP per class; multi-class log loss + Cohen's kappa; bootstrap CI on macro-F1; dominant confusion pairs named.

### Example 2: 10-class long-tail classifier (edge-case)

Input: "10-class severity classifier. Class 0 is 70% of samples, classes 7-9 are 1% each. I'm reporting 91% overall accuracy and 0.62 macro-F1. Is this good?"

Output: Skill flags the imbalance ratio of 70 immediately. Refuses to call 91% accuracy "good" — predicting always-class-0 already gets 70%. Demands per-class F1 reading for classes 7-9, where macro-F1 of 0.62 likely hides per-class F1 near 0 for the rare classes. Recommends switching the lead metric to weighted-F1 if deployment cost follows traffic mix, or keeping macro-F1 and being honest about per-class collapse if every class matters equally. Recommends stratified bootstrap CI on per-class F1 for the rare classes (likely very wide).

### Example 3: Hand-off on binary task (anti-trigger)

Input: "I have a binary classifier — spam vs ham. y_true is 0/1, y_pred_proba shape `(n, 2)`. Evaluate it as multi-class please."

Output: Skill identifies the task as binary. Explains that multi-class metrics on a binary task collapse to the binary metrics with extra plumbing (macro-F1 = mean of class-0-F1 and class-1-F1, etc.). Hands off to `evaluating-binary-classifiers` for the right tool set (ROC + PR + threshold sweep + cost-weighted threshold selection). Does not force the K x K confusion matrix or one-vs-rest ROC on a 2 x 2 problem.

## See also

- `ml-datasci/evaluating-binary-classifiers` — the 2-class analogue of this skill; hand off when `n_classes == 2`
- `ml-datasci/evaluating-regression-models` — the regression analogue
- `ml-datasci/tuning-classification-threshold` — sibling for cost-aware decision-rule selection; in multi-class, the analogue is per-class threshold (top-1 with reject) or cost-weighted argmax
- `ml-datasci/building-baseline-models` — required pre-step; a Dummy classifier with `strategy='stratified'` gives the baseline that contextualizes every metric here
- `ml-datasci/auditing-train-test-split` — required pre-step; per-class recall on a leaky split is meaningless

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-1, skill 1) via PRAGMATIC discipline
