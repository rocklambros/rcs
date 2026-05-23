# Threshold selection recipes

Copy-paste sklearn / NumPy implementations for each selector. All five operate on `(y_val, p_val)` to pick `t*`, then the chosen `t*` is applied to `(y_test, p_test)` for the reported metrics.

## Shared setup

```python
import numpy as np
from sklearn.metrics import roc_curve, precision_recall_curve, confusion_matrix, fbeta_score

thresholds = np.linspace(0.001, 0.999, 999)
```

## 1. F-beta

```python
def pick_threshold_fbeta(y_val, p_val, beta, thresholds=thresholds):
    scores = [fbeta_score(y_val, (p_val >= t).astype(int), beta=beta, zero_division=0) for t in thresholds]
    return thresholds[int(np.argmax(scores))]
```

- `beta = 1` → F1 (symmetric)
- `beta = 2` → weights recall 2x (use when missing positives hurts more)
- `beta = 0.5` → weights precision 2x (use when false alarms hurt more)

## 2. TPR at fixed FPR budget

```python
def pick_threshold_tpr_at_fpr(y_val, p_val, fpr_budget):
    fpr, tpr, t = roc_curve(y_val, p_val)
    # Pick the threshold whose FPR is the largest value <= fpr_budget (most TPR within budget)
    eligible = fpr <= fpr_budget
    if not eligible.any():
        raise ValueError(f"No threshold achieves FPR <= {fpr_budget}; loosen the budget")
    # ROC thresholds are sorted descending; among eligible, max TPR is at the largest FPR <= budget
    idx = np.where(eligible)[0]
    best = idx[np.argmax(tpr[idx])]
    return t[best]
```

- Use when there is a hard SOC alert volume budget, a hard false-alarm rate for screening, or a regulatory ceiling on user friction.

## 3. Precision at fixed recall floor

```python
def pick_threshold_precision_at_recall(y_val, p_val, recall_floor):
    precision, recall, t = precision_recall_curve(y_val, p_val)
    # precision_recall_curve returns one fewer threshold than precision/recall arrays
    precision, recall = precision[:-1], recall[:-1]
    eligible = recall >= recall_floor
    if not eligible.any():
        raise ValueError(f"No threshold achieves recall >= {recall_floor}; loosen the floor")
    idx = np.where(eligible)[0]
    best = idx[np.argmax(precision[idx])]
    return t[best]
```

- Use when there is a regulatory must-catch rate (e.g. "the screening test must achieve >= 95% recall") and the goal is the highest precision compatible with that recall.

## 4. Cost-weighted (FN-cost vs FP-cost asymmetry)

```python
def pick_threshold_cost_weighted(y_val, p_val, cost_ratio, thresholds=thresholds):
    """cost_ratio = FN_cost / FP_cost. Pick t* minimizing FP + cost_ratio * FN."""
    costs = []
    for t in thresholds:
        pred = (p_val >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_val, pred, labels=[0, 1]).ravel()
        costs.append(fp + cost_ratio * fn)
    return thresholds[int(np.argmin(costs))]
```

- Document the `cost_ratio` source: business cost model, clinical cost study, regulatory floor, security-incident historical loss.
- Typical ranges: fraud 50-500, cancer screening 1000+, content moderation 5-50 (varies with platform), churn intervention 1-10.

## 5. Youden's J (cost-blind fallback)

```python
def pick_threshold_youdens_j(y_val, p_val):
    fpr, tpr, t = roc_curve(y_val, p_val)
    j = tpr - fpr
    return t[int(np.argmax(j))]
```

- Use only when no cost model is available. Document the absence of a cost model in the report so the team knows to re-tune once cost is quantified.

## Reporting the test-slice metrics at t*

```python
def report_at_threshold(y_test, p_test, t_star):
    pred = (p_test >= t_star).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    fpr = 1 - specificity
    return {
        "t_star": float(t_star),
        "confusion": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "precision": precision, "recall": recall, "specificity": specificity, "fpr": fpr,
    }
```

Wrap with bootstrap resampling of `(y_test, p_test)` rows (n_bootstrap >= 1000) to get 95% CIs on every metric.
