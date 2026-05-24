# Drift metrics cookbook

Formulas and reference implementations for the three drift metrics used in `auditing-embedding-drift`.

## 1. Per-dimension Jensen-Shannon divergence

Captures distributional shift along each embedding dimension independently.

```python
import numpy as np
from scipy.spatial.distance import jensenshannon

def js_per_dim(baseline: np.ndarray, comparison: np.ndarray, n_bins: int | None = None) -> np.ndarray:
    """
    baseline: (N_baseline, dim) array of embeddings
    comparison: (N_comparison, dim) array of embeddings
    returns: (dim,) array of per-dim JS divergence in [0, 1]
    """
    n_bins = n_bins or int(np.sqrt(min(len(baseline), len(comparison))))
    dim = baseline.shape[1]
    out = np.zeros(dim)
    for i in range(dim):
        lo = min(baseline[:, i].min(), comparison[:, i].min())
        hi = max(baseline[:, i].max(), comparison[:, i].max())
        edges = np.linspace(lo, hi, n_bins + 1)
        p, _ = np.histogram(baseline[:, i], bins=edges, density=False)
        q, _ = np.histogram(comparison[:, i], bins=edges, density=False)
        p = (p + 1) / (p.sum() + n_bins)  # Laplace smoothing
        q = (q + 1) / (q.sum() + n_bins)
        out[i] = jensenshannon(p, q, base=2) ** 2  # scipy returns sqrt(JS); square it back
    return out
```

Report the mean across dims as the overall scalar, plus the top-N highest-divergence dims for the drift-attribution step. Use Jensen-Shannon over KL by default because it is symmetric and bounded in [0, 1]; flip to KL only when explicitly requested.

## 2. Centroid cosine distance

Captures overall shift of the embedding cohort's center of mass.

```python
import numpy as np

def centroid_cosine_dist(baseline: np.ndarray, comparison: np.ndarray) -> float:
    """
    Returns a scalar in [0, 2]; 0 = identical centroids, 1 = orthogonal, 2 = opposite.
    """
    c_base = baseline.mean(axis=0)
    c_comp = comparison.mean(axis=0)
    c_base /= np.linalg.norm(c_base)
    c_comp /= np.linalg.norm(c_comp)
    return 1.0 - float(c_base @ c_comp)
```

For normalized-by-default embeddings (OpenAI, Voyage), centroid cosine distance under ~0.01 is typically within noise; over ~0.05 is usually actionable. Calibrate against the no-drift bootstrap distribution rather than the rule of thumb.

## 3. Intra-cohort mean pairwise distance shift

Captures whether the comparison cohort is becoming more spread out (new sub-topics) or more clustered (concept collapse).

```python
import numpy as np
from sklearn.metrics import pairwise_distances

def intra_cohort_dist_shift(baseline: np.ndarray, comparison: np.ndarray, sample_size: int = 1000) -> float:
    """
    Returns: mean_pairwise(comparison) - mean_pairwise(baseline)
    Positive = comparison is more spread; negative = comparison is more clustered.
    Subsamples to sample_size if cohorts are large (pairwise is O(N^2)).
    """
    def sample(x):
        if len(x) > sample_size:
            idx = np.random.choice(len(x), sample_size, replace=False)
            return x[idx]
        return x
    d_base = pairwise_distances(sample(baseline), metric="cosine").mean()
    d_comp = pairwise_distances(sample(comparison), metric="cosine").mean()
    return float(d_comp - d_base)
```

## 4. Bootstrap 95% CI for any of the above

```python
import numpy as np

def bootstrap_ci(baseline: np.ndarray, comparison: np.ndarray, metric_fn, n_iter: int = 1000, ci: float = 0.95):
    """
    metric_fn(baseline_resample, comparison_resample) -> scalar or array
    Returns (point_estimate, lower, upper).
    """
    point = metric_fn(baseline, comparison)
    samples = []
    for _ in range(n_iter):
        b_idx = np.random.choice(len(baseline), len(baseline), replace=True)
        c_idx = np.random.choice(len(comparison), len(comparison), replace=True)
        samples.append(metric_fn(baseline[b_idx], comparison[c_idx]))
    samples = np.array(samples)
    alpha = (1 - ci) / 2
    lower = np.quantile(samples, alpha, axis=0)
    upper = np.quantile(samples, 1 - alpha, axis=0)
    return point, lower, upper
```

Bootstrap with `n_iter = 1000` for stable CIs. If the metric is array-valued (per-dim), this returns per-dim CIs; report them alongside the per-dim point estimates.

## 5. Top-N drifted documents

```python
import numpy as np
from sklearn.metrics import pairwise_distances_argmin_min

def top_n_drifted_docs(baseline: np.ndarray, comparison: np.ndarray, n: int = 20):
    """
    For each comparison document, find distance to nearest baseline doc.
    Return indices of the n with the largest such distance (most "novel").
    """
    _, dists = pairwise_distances_argmin_min(comparison, baseline, metric="cosine")
    top_idx = np.argsort(dists)[-n:][::-1]
    return top_idx, dists[top_idx]
```

These are the documents most likely to represent new content categories. Pair with their metadata (category, source, language) for the attribution step.

## What this cookbook will NOT do for you

- Pick a drift alert threshold for your corpus — see `reference/drift-thresholds.md` for defaults; calibrate against the bootstrap no-drift distribution
- Tell you whether to re-embed — that is a cost-benefit decision, not a metric
- Handle multimodal embeddings (image + text) — the formulas assume single-modality continuous embeddings; for multimodal, run drift per-modality separately
