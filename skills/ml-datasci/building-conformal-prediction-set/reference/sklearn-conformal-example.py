"""Split-conformal prediction for scikit-learn classifiers and regressors.

Reference implementation for `building-conformal-prediction-set`. Covers:

1. Classification with the softmax nonconformity score (1 - p_true_class)
2. Regression with the absolute-residual nonconformity score
3. Conformalized Quantile Regression (CQR) for heteroscedastic regression

Each function:

- Takes train / calibration / test splits already carved by the caller
- Returns the prediction set / interval AND the empirical coverage AND the
  average set size or interval width on the test split
- Uses the finite-sample-corrected quantile (1 - alpha) * (n_cal + 1) / n_cal

Adapt: swap in your own base model. The interface is sklearn-style
(predict_proba for classification, predict for regression).
"""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import Callable


def _conformal_quantile(scores: NDArray[np.floating], alpha: float) -> float:
    """Finite-sample-corrected upper quantile of nonconformity scores."""
    n = len(scores)
    if n < 1:
        raise ValueError("calibration set is empty")
    level = np.ceil((1.0 - alpha) * (n + 1)) / n
    level = min(level, 1.0)
    return float(np.quantile(scores, level, method="higher"))


def conformal_classification(
    model,
    X_cal: NDArray,
    y_cal: NDArray,
    X_test: NDArray,
    y_test: NDArray,
    alpha: float,
) -> dict:
    """Split-conformal multi-class classification with softmax nonconformity.

    Returns:
        dict with keys:
            - q: conformal quantile
            - prediction_sets: list of label sets per test point
            - empirical_coverage: fraction of test points whose true label is in their set
            - avg_set_size: mean cardinality of the prediction sets
    """
    proba_cal = model.predict_proba(X_cal)
    scores_cal = 1.0 - proba_cal[np.arange(len(y_cal)), y_cal]
    q = _conformal_quantile(scores_cal, alpha)

    proba_test = model.predict_proba(X_test)
    pred_sets = []
    covered = 0
    for i, probs in enumerate(proba_test):
        s = 1.0 - probs
        labels = np.where(s <= q)[0].tolist()
        if not labels:  # never return empty set; fall back to top-1
            labels = [int(np.argmax(probs))]
        pred_sets.append(labels)
        if y_test[i] in labels:
            covered += 1

    return {
        "q": q,
        "prediction_sets": pred_sets,
        "empirical_coverage": covered / len(y_test),
        "avg_set_size": float(np.mean([len(s) for s in pred_sets])),
    }


def conformal_regression(
    model,
    X_cal: NDArray,
    y_cal: NDArray,
    X_test: NDArray,
    y_test: NDArray,
    alpha: float,
) -> dict:
    """Split-conformal regression with absolute-residual nonconformity.

    Returns:
        dict with keys: q, intervals, empirical_coverage, avg_width.
    """
    yhat_cal = model.predict(X_cal)
    scores_cal = np.abs(y_cal - yhat_cal)
    q = _conformal_quantile(scores_cal, alpha)

    yhat_test = model.predict(X_test)
    lo = yhat_test - q
    hi = yhat_test + q
    intervals = list(zip(lo.tolist(), hi.tolist()))
    covered = np.mean((y_test >= lo) & (y_test <= hi))
    width = float(np.mean(hi - lo))

    return {
        "q": q,
        "intervals": intervals,
        "empirical_coverage": float(covered),
        "avg_width": width,
    }


def conformal_cqr(
    quantile_predict: Callable[[NDArray], tuple[NDArray, NDArray]],
    X_cal: NDArray,
    y_cal: NDArray,
    X_test: NDArray,
    y_test: NDArray,
    alpha: float,
) -> dict:
    """Conformalized Quantile Regression (CQR) for heteroscedastic intervals.

    `quantile_predict(X)` returns (lo, hi) arrays — predicted lower and upper
    quantiles at levels alpha/2 and 1 - alpha/2 respectively from a base
    quantile-regression model fitted on the training split.
    """
    lo_cal, hi_cal = quantile_predict(X_cal)
    scores_cal = np.maximum(lo_cal - y_cal, y_cal - hi_cal)
    q = _conformal_quantile(scores_cal, alpha)

    lo_test, hi_test = quantile_predict(X_test)
    lo_adj = lo_test - q
    hi_adj = hi_test + q
    intervals = list(zip(lo_adj.tolist(), hi_adj.tolist()))
    covered = np.mean((y_test >= lo_adj) & (y_test <= hi_adj))
    width = float(np.mean(hi_adj - lo_adj))

    return {
        "q": q,
        "intervals": intervals,
        "empirical_coverage": float(covered),
        "avg_width": width,
    }
