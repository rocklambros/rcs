# Bootstrap 95% CI for binary-classifier metrics

Stratified bootstrap recipe for AUC, F1, and other classifier metrics. Use when reporting any single number (AUC, F1, precision) so the reader can judge sampling uncertainty.

## Why stratified

If either class has fewer than ~100 examples in the test set, plain resampling can produce bootstrap samples with zero positives (or zero negatives), making ROC-AUC undefined. Stratifying the resample by class fixes this.

## Recipe (NumPy + scikit-learn)

```python
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score

def bootstrap_ci(
    y_true: np.ndarray,
    y_score: np.ndarray,
    metric_fn,                              # e.g. roc_auc_score
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    stratify: bool = True,
    seed: int = 42,
) -> tuple[float, float, float]:
    """
    Returns (point_estimate, ci_low, ci_high) for the metric.
    metric_fn signature: metric_fn(y_true, y_score) -> float
    For threshold-dependent metrics like f1_score, pass y_pred
    (already-thresholded) as y_score and use lambda yt, yp: f1_score(yt, yp).
    """
    rng = np.random.default_rng(seed)
    point = metric_fn(y_true, y_score)

    n = len(y_true)
    pos_idx = np.flatnonzero(y_true == 1)
    neg_idx = np.flatnonzero(y_true == 0)

    boots = []
    for _ in range(n_bootstrap):
        if stratify:
            sample_pos = rng.choice(pos_idx, size=len(pos_idx), replace=True)
            sample_neg = rng.choice(neg_idx, size=len(neg_idx), replace=True)
            idx = np.concatenate([sample_pos, sample_neg])
        else:
            idx = rng.integers(0, n, size=n)
        try:
            boots.append(metric_fn(y_true[idx], y_score[idx]))
        except ValueError:
            # Single-class bootstrap sample under non-stratified mode; skip
            continue

    boots = np.asarray(boots)
    lo = np.quantile(boots, alpha / 2)
    hi = np.quantile(boots, 1 - alpha / 2)
    return point, lo, hi
```

## Usage

```python
# Threshold-free
auc, auc_lo, auc_hi = bootstrap_ci(y_true, y_proba, roc_auc_score)
pr,  pr_lo,  pr_hi  = bootstrap_ci(y_true, y_proba, average_precision_score)

# Threshold-dependent (use already-thresholded predictions)
y_pred = (y_proba >= t_star).astype(int)
f1, f1_lo, f1_hi = bootstrap_ci(
    y_true, y_pred, lambda yt, yp: f1_score(yt, yp)
)
```

## Caveats

- For very small samples (< 50 in either class), bootstrap CIs can be unstable. Report the n explicitly and consider analytic CIs (DeLong for AUC) as a complement.
- `n_bootstrap = 1000` is the floor. For final reports, use 10,000 if compute allows.
- The seed is fixed for reproducibility. Bootstrap CIs are NOT model-fit randomness; they reflect sampling uncertainty of the test set.
- If the user wants per-class metric CIs, run the bootstrap separately for each class subset.
