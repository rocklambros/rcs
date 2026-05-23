# Paired model-comparison test recipes

Pick from the decision table; implementations below.

## Decision table

| Setup | Test | Why this test |
|---|---|---|
| 2 classifiers, same test set, predictions at chosen threshold | **McNemar** | Reads the off-diagonal cells of the agreement table — accounts for the paired structure of both models scoring the same instances. |
| 2 classifiers, same test set, ROC-AUC comparison | **DeLong's test** | Analytic CI on AUC difference that handles correlated AUCs from paired predictions. |
| 2 models, k-fold CV with paired folds, per-fold diffs roughly Normal | **Paired t-test** | Standard parametric paired test; valid when n_folds >= 10 and Shapiro on diffs gives p > 0.05. |
| 2 models, k-fold CV with paired folds, per-fold diffs non-Normal | **Wilcoxon signed-rank** | Demsar 2006 recommended default; robust to non-Normality. |
| 3+ models, k-fold CV | **Friedman omnibus → Nemenyi post-hoc** (Demsar 2006) OR pairwise Wilcoxon + Holm-Bonferroni | Friedman tests "any difference exists"; Nemenyi gives pairwise comparisons with critical-difference plot. |
| 2 regression models, same test instances, per-instance squared error | **Paired t** OR **Wilcoxon** on per-instance error differences | Same as the CV branch; paired structure preserved per test instance. |

## Implementations

### McNemar

```python
from statsmodels.stats.contingency_tables import mcnemar
import numpy as np

def mcnemar_compare(y_true, pred_A, pred_B):
    A_right = (pred_A == y_true)
    B_right = (pred_B == y_true)
    n00 = np.sum(~A_right & ~B_right)
    n01 = np.sum(~A_right & B_right)  # A wrong, B right
    n10 = np.sum(A_right & ~B_right)  # A right, B wrong
    n11 = np.sum(A_right & B_right)
    table = [[n11, n10], [n01, n00]]
    # exact mid-p for small n (n01 + n10 < 25); continuity correction otherwise
    use_exact = (n01 + n10) < 25
    result = mcnemar(table, exact=use_exact, correction=not use_exact)
    return {"statistic": result.statistic, "pvalue": result.pvalue,
            "A_right_B_wrong": n10, "A_wrong_B_right": n01}
```

### DeLong's test

```python
# scikit-learn does not include DeLong's directly; use the implementation from
# https://github.com/yandexdataschool/roc_comparison or compute via the Hanley-McNeil approximation:

import numpy as np
from scipy.stats import norm

def delong_test(y_true, p_A, p_B):
    """Approximate DeLong's; for production, use the validated yandexdataschool implementation."""
    from sklearn.metrics import roc_auc_score
    auc_A = roc_auc_score(y_true, p_A)
    auc_B = roc_auc_score(y_true, p_B)
    delta = auc_A - auc_B
    # Bootstrap variance as a stand-in for the analytic DeLong variance
    n_bootstrap = 2000
    deltas = []
    idx = np.arange(len(y_true))
    for _ in range(n_bootstrap):
        b = np.random.choice(idx, size=len(idx), replace=True)
        a = roc_auc_score(y_true[b], p_A[b]); c = roc_auc_score(y_true[b], p_B[b])
        deltas.append(a - c)
    se = np.std(deltas)
    z = delta / se if se > 0 else 0
    p = 2 * (1 - norm.cdf(abs(z)))
    return {"delta_auc": delta, "se": se, "z": z, "pvalue": p,
            "ci_95": (delta - 1.96 * se, delta + 1.96 * se)}
```

### Paired t-test on per-fold metrics

```python
from scipy.stats import ttest_rel, shapiro, wilcoxon

def paired_cv_compare(metrics_A, metrics_B, auto_pick=True):
    diffs = np.array(metrics_A) - np.array(metrics_B)
    use_t = True
    if auto_pick and len(diffs) >= 3:
        sh = shapiro(diffs)
        use_t = sh.pvalue > 0.05
    if use_t:
        result = ttest_rel(metrics_A, metrics_B)
        test = "paired-t"
    else:
        result = wilcoxon(metrics_A, metrics_B)
        test = "wilcoxon-signed-rank"
    return {"test": test, "statistic": result.statistic, "pvalue": result.pvalue,
            "mean_diff": diffs.mean(), "n_folds": len(diffs)}
```

### Holm-Bonferroni

```python
def holm_bonferroni(pvals, alpha=0.05):
    pvals = np.asarray(pvals)
    order = np.argsort(pvals)
    reject = np.zeros(len(pvals), dtype=bool)
    for i, idx in enumerate(order):
        if pvals[idx] < alpha / (len(pvals) - i):
            reject[idx] = True
        else:
            break
    corrected = np.minimum(pvals * np.arange(len(pvals), 0, -1)[np.argsort(order)], 1.0)
    return {"reject": reject, "corrected": corrected}
```

### Friedman + Nemenyi (Demsar 2006)

```python
from scipy.stats import friedmanchisquare
# Nemenyi via scikit-posthocs:
# from scikit_posthocs import posthoc_nemenyi_friedman

def friedman_then_nemenyi(metrics_per_model_per_fold):
    """metrics_per_model_per_fold: dict[model_name] -> array of per-fold metrics."""
    arrays = list(metrics_per_model_per_fold.values())
    omnibus = friedmanchisquare(*arrays)
    # Post-hoc Nemenyi requires scikit-posthocs:
    # nemenyi = posthoc_nemenyi_friedman(np.column_stack(arrays))
    return {"friedman_statistic": omnibus.statistic, "friedman_p": omnibus.pvalue}
```

## Effect-size reporting

Always report alongside the p-value:

```python
def delta_with_bootstrap_ci(y_true, p_A, p_B, metric_fn, n_bootstrap=1000):
    idx = np.arange(len(y_true))
    deltas = []
    for _ in range(n_bootstrap):
        b = np.random.choice(idx, size=len(idx), replace=True)
        deltas.append(metric_fn(y_true[b], p_A[b]) - metric_fn(y_true[b], p_B[b]))
    return {"delta": np.mean(deltas), "ci_95": (np.percentile(deltas, 2.5),
                                                  np.percentile(deltas, 97.5))}
```

## Operational vs statistical significance

Pre-register an operationally-meaningful effect size threshold BEFORE running the test. Examples:

- For ROC-AUC: `delta_auc > 0.01` (1 AUC point)
- For accuracy: `delta_accuracy > 0.01` (1 percentage point)
- For RMSE: `delta_rmse > 5% of target SD`
- For F1: `delta_f1 > 0.02`

A difference can be statistically significant (p < 0.05) but operationally negligible (delta below threshold). In that case, pick the cheaper / simpler / more interpretable model and document the result honestly.
