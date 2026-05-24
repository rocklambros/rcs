# Calibration diagnostics

A binary classifier is well-calibrated if, among predictions with `p̂ = 0.7`, roughly 70% of outcomes are positive. Calibration is independent of discrimination — a model can rank well (high AUC) but be poorly calibrated (predicted probabilities are systematically wrong).

## Three complementary views

### Reliability curve (calibration plot)

Bin predictions by `y_pred_proba` (10 quantile bins; using quantile binning prevents empty bins on imbalanced classes). For each bin, plot:

- x-axis: mean predicted probability in the bin
- y-axis: observed positive rate in the bin
- Identity line `y = x` is perfect calibration

A bowed-down curve (observed below predicted) → over-confident model.
A bowed-up curve (observed above predicted) → under-confident model.
S-shape → both regions of the score range are miscalibrated.

```python
import numpy as np

def reliability_curve(y_true, y_pred_proba, n_bins=10):
    # Quantile binning so no empty bins on imbalanced data
    bin_edges = np.quantile(y_pred_proba, np.linspace(0, 1, n_bins + 1))
    bin_edges[0], bin_edges[-1] = 0.0, 1.0 + 1e-9
    bin_ids = np.digitize(y_pred_proba, bin_edges) - 1
    rows = []
    for b in range(n_bins):
        mask = bin_ids == b
        if mask.sum() < 5:
            continue  # skip thin bins; they are noise
        rows.append({
            "bin": b,
            "n": int(mask.sum()),
            "mean_pred": float(y_pred_proba[mask].mean()),
            "observed_rate": float(y_true[mask].mean()),
        })
    return rows
```

### Slope / intercept

Logistic regression of `y_true` on `log_odds(y_pred_proba)`:

- slope (β1): 1.0 = ideal; < 1 over-confident; > 1 under-confident
- intercept (β0): 0.0 = ideal; non-zero = systematic bias

This is a single-number summary that the reliability-curve plot makes visual.

```python
from sklearn.linear_model import LogisticRegression

def calibration_slope_intercept(y_true, y_pred_proba):
    eps = 1e-12
    p = np.clip(y_pred_proba, eps, 1 - eps)
    log_odds = np.log(p / (1 - p)).reshape(-1, 1)
    lr = LogisticRegression(C=1e6, solver="lbfgs").fit(log_odds, y_true)
    return float(lr.coef_[0][0]), float(lr.intercept_[0])
```

The very high `C` disables regularization so the slope reflects the data directly, not a prior-pulled estimate.

### Brier score

`mean((y_pred_proba - y_true) ** 2)` — single-number summary capturing discrimination AND calibration. Lower is better.

Decompose Brier as `Reliability - Resolution + Uncertainty`:

- Reliability: weighted MSE of bin predictions vs. observed rates (lower is better)
- Resolution: variance of observed rates across bins (higher is better)
- Uncertainty: marginal base-rate variance (cannot be improved by the model)

The decomposition tells you whether the model lacks calibration (high reliability term) or lacks discrimination (low resolution term).

## Recalibration methods

### Platt scaling

Fit a logistic regression on `log_odds(y_pred_proba)` → `y_true` on a held-out calibration window. Use the fitted model to transform live predictions.

```python
from sklearn.linear_model import LogisticRegression

def fit_platt_calibrator(y_true_cal, y_pred_cal):
    eps = 1e-12
    p = np.clip(y_pred_cal, eps, 1 - eps)
    log_odds = np.log(p / (1 - p)).reshape(-1, 1)
    return LogisticRegression(solver="lbfgs").fit(log_odds, y_true_cal)

def apply_platt(calibrator, y_pred_proba):
    eps = 1e-12
    p = np.clip(y_pred_proba, eps, 1 - eps)
    log_odds = np.log(p / (1 - p)).reshape(-1, 1)
    return calibrator.predict_proba(log_odds)[:, 1]
```

Pros: works well on moderate sample sizes; parametric and stable.
Cons: assumes a sigmoidal miscalibration shape; will not fix arbitrary deformations.

### Isotonic regression

Fits a monotonic step function from predicted to observed probability. More flexible than Platt but needs more data (rough rule: ≥ 1000 examples in the calibration window).

```python
from sklearn.isotonic import IsotonicRegression

def fit_isotonic_calibrator(y_true_cal, y_pred_cal):
    return IsotonicRegression(out_of_bounds="clip").fit(y_pred_cal, y_true_cal)
```

Pros: handles non-sigmoidal miscalibration.
Cons: can overfit on small calibration windows; staircase shape can look ugly.

### Temperature scaling (deep learning)

For deep networks with logits, divide logits by a single learned temperature `T` before softmax. Cheap, single-parameter, no architectural change. See Guo et al. 2017.

## Recalibration validation

Critical: recalibrate on one window, validate on a different held-out window. Recalibrating and evaluating on the same window is in-sample fit, not a generalization claim.

Pattern:

1. Split the labeled-and-mature live data into `cal_window` and `eval_window` (temporally — `cal_window.end < eval_window.start`)
2. Fit the recalibrator on `cal_window`
3. Apply to `eval_window` predictions and re-measure slope / intercept / Brier
4. The re-measured calibration should be near-ideal on `eval_window`; if not, the recalibration is overfit or the miscalibration is shape-dependent across windows

## Common mistakes

- **Using `predict_proba` from a model trained without `class_weight='balanced'` on imbalanced data and being surprised by poor calibration.** Class-weighting helps discrimination, hurts calibration; consider always calibrating post-hoc.
- **Treating tree-based ensembles' `predict_proba` as calibrated.** Random forests and gradient boosters rarely are; calibrate via Platt or isotonic before reporting probabilities to stakeholders.
- **Reporting a single reliability-curve plot without slope / intercept / Brier numbers.** Visual calibration is hard to compare across snapshots; numbers are reproducible.
- **Comparing reliability curves with different binning schemes.** Always use quantile binning with the same `n_bins`.
