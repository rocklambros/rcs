# Threshold sweep + cost-aware selector

Plotting precision / recall / F1 / MCC versus threshold, with an explicit selector that picks the operating threshold per cost ratio or precision floor.

## Why a sweep instead of 0.5

The default 0.5 threshold is correct only when:

- Classes are balanced AND
- FP and FN costs are equal AND
- The classifier outputs well-calibrated probabilities

For fraud, security, medical screening, content moderation, and most production binary classifiers, at least one of those fails. The sweep makes the choice explicit.

## Recipe

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_score, recall_score, f1_score, matthews_corrcoef,
    confusion_matrix,
)

def sweep(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    thresholds: np.ndarray = np.linspace(0.01, 0.99, 99),
) -> dict:
    """Return per-threshold metric arrays for plotting and selection."""
    P, R, F1, MCC = [], [], [], []
    for t in thresholds:
        y_pred = (y_proba >= t).astype(int)
        P.append(precision_score(y_true, y_pred, zero_division=0))
        R.append(recall_score(y_true, y_pred, zero_division=0))
        F1.append(f1_score(y_true, y_pred, zero_division=0))
        MCC.append(matthews_corrcoef(y_true, y_pred))
    return {
        "thresholds": thresholds,
        "precision": np.asarray(P),
        "recall":    np.asarray(R),
        "f1":        np.asarray(F1),
        "mcc":       np.asarray(MCC),
    }


def pick_threshold(
    sweep_result: dict,
    y_true: np.ndarray,
    y_proba: np.ndarray,
    *,
    cost_ratio: float = 1.0,        # FN cost / FP cost
    precision_floor: float | None = None,
) -> tuple[float, str]:
    """
    Returns (t_star, rationale_string).

    Selection rules (in priority order):
      1. If precision_floor is set: highest-recall threshold meeting the floor
      2. Else if cost_ratio == 1: argmax F1 (ties broken by argmax MCC)
      3. Else: argmin cost-aware loss = FP + cost_ratio * FN
    """
    ts = sweep_result["thresholds"]

    if precision_floor is not None:
        eligible = sweep_result["precision"] >= precision_floor
        if not eligible.any():
            raise ValueError(
                f"No threshold meets precision_floor={precision_floor}; "
                f"max precision in sweep = {sweep_result['precision'].max():.3f}"
            )
        # highest recall among the eligible
        recalls = np.where(eligible, sweep_result["recall"], -np.inf)
        i = int(np.argmax(recalls))
        return float(ts[i]), f"highest-recall threshold meeting precision ≥ {precision_floor}"

    if cost_ratio == 1.0:
        i = int(np.argmax(sweep_result["f1"]))
        return float(ts[i]), "argmax F1 (cost_ratio = 1)"

    losses = []
    for t in ts:
        y_pred = (y_proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        losses.append(fp + cost_ratio * fn)
    i = int(np.argmin(losses))
    return float(ts[i]), f"argmin cost-aware loss (cost_ratio = {cost_ratio})"


def plot_sweep(sweep_result: dict, ax=None):
    ax = ax or plt.gca()
    for key in ("precision", "recall", "f1", "mcc"):
        ax.plot(sweep_result["thresholds"], sweep_result[key], label=key)
    ax.set_xlabel("threshold")
    ax.set_ylabel("metric value")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return ax
```

## Usage

```python
sw = sweep(y_true, y_proba)
t_star, why = pick_threshold(sw, y_true, y_proba, cost_ratio=5.0)  # fraud
print(f"Chosen threshold = {t_star:.3f} ({why})")
plot_sweep(sw); plt.axvline(t_star, ls="--"); plt.savefig("threshold-sweep.png")
```

## Caveats

- **Pick on validation, report on test.** Selecting `t_star` on the same data used for the final metric report inflates the chosen-threshold metrics. Use a separate validation slice for the pick, then report at the chosen `t_star` on the held-out test set.
- For severe miscalibration, fix the calibration first (Platt / isotonic), then re-sweep. A threshold on a miscalibrated score has no probabilistic interpretation.
- `cost_ratio` is a domain decision, not a statistical one. Document where the value came from.
