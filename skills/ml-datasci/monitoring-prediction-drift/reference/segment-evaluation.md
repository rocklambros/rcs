# Per-segment evaluation with confidence intervals

A globally-stable AUC can hide one segment whose AUC has cratered. Per-segment evaluation surfaces the gap. Without confidence intervals, thin segments look like alarms when they are just noise.

## Bootstrap CI on a metric

```python
import numpy as np
from sklearn.metrics import roc_auc_score

def bootstrap_metric_ci(y_true, y_pred_proba, metric_fn=roc_auc_score, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(y_true)
    scores = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        # Resampled split must include both classes; skip degenerate samples
        if len(np.unique(y_true[idx])) < 2:
            continue
        scores.append(metric_fn(y_true[idx], y_pred_proba[idx]))
    scores = np.array(scores)
    return float(scores.mean()), (float(np.quantile(scores, 0.025)), float(np.quantile(scores, 0.975)))
```

Pair every per-segment metric with its bootstrap 95% CI. The width of the CI tells you whether the segment is well-measured or noise-dominated.

## Segment table format

| Segment | n | base_rate | AUC | AUC 95% CI | F1 | F1 95% CI | Calibration slope | Status |
|---|---|---|---|---|---|---|---|---|
| enterprise | 4,200 | 0.18 | 0.71 | [0.67, 0.75] | 0.42 | [0.38, 0.46] | 0.62 | decayed |
| mid-market | 12,500 | 0.11 | 0.81 | [0.79, 0.83] | 0.39 | [0.36, 0.42] | 0.95 | stable |
| smb | 38,000 | 0.07 | 0.83 | [0.82, 0.84] | 0.31 | [0.30, 0.33] | 0.98 | stable |

**Status** definition:

- `stable` — current CI overlaps reference CI on every metric
- `decayed` — current CI does NOT overlap reference CI on at least one primary metric
- `new` — segment did not exist in reference window (do not call out as erosion; track forward separately)
- `thin` — n < 200 (or 5× the inverse-base-rate, whichever larger); CI is too wide to act on

## Simpson's paradox: a worked case

Reference window globals: AUC = 0.82, calibration slope = 0.98.

Current window globals: AUC = 0.80, calibration slope = 0.95. → looks stable.

But per-segment:

- `enterprise`: AUC 0.83 → 0.71 (decayed)
- `mid-market`: AUC 0.79 → 0.81 (stable)
- `smb`: AUC 0.83 → 0.83 (stable)

Why is the global stable? `enterprise` is only 8% of the population. The 12-point AUC drop on 8% of the data moves the global by ~1 point, which is within noise. But the operational impact on the enterprise customer base is severe.

The lesson: always carry per-segment metrics, even when the global looks fine, when any segment is small relative to the population.

## Avoiding common segment-evaluation mistakes

- **Defining segments post-hoc to chase a finding.** If you slice 50 ways looking for one bad slice, you will find one by chance. Pre-register the segment set (region, product line, customer tier) before looking.
- **Per-segment metric without CI.** A 0.65 AUC on n=50 is meaningless without the [0.45, 0.85] CI.
- **Comparing absolute AUC across segments to declare "this segment is worse."** Different segments have different base rates and feature distributions; the actionable question is "is this segment worse than its own reference?", not "is this segment worse than another segment?".
- **Letting a new segment register a fake "improvement" or "decay".** A segment that did not exist in the reference window cannot have decayed; track forward separately.

## Multi-class and regression analogs

- Multi-class: per-class precision / recall / F1; macro-F1 with bootstrap CI for the global view. Track per-class AND per-segment if both axes matter.
- Regression: RMSE, MAE, R² per segment. Calibration intercept = `mean(y_true) - mean(y_pred)`; calibration slope = regression coefficient of `y_true` on `y_pred`.

## Reporting cadence

- Daily roll-up: global metric + per-segment table; alert only on `decayed` or `thin`-but-trending segments
- Weekly executive view: trend lines per segment for the last 12 weeks
- Quarterly model-card update: snapshot of the per-segment table for the historical record
