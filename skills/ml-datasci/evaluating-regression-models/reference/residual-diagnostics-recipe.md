# Residual diagnostics recipe — residuals vs fitted, QQ, histogram, Cook's D

Use after the headline-metric step. Generates the four diagnostic plots and the influential-row list referenced in `regression-eval-checklist.md`.

## Recipe (matplotlib + statsmodels + scipy)

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


def residual_diagnostics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    sd_threshold: float = 3.0,
) -> dict:
    """Return diagnostic arrays + flagged row indices for outlier residuals."""
    resid = y_true - y_pred
    std = resid.std(ddof=1)
    flagged = np.flatnonzero(np.abs(resid) > sd_threshold * std)
    return {
        "residuals": resid,
        "fitted": y_pred,
        "std": std,
        "flagged_idx": flagged,
    }


def plot_residuals_vs_fitted(diag: dict, ax=None):
    ax = ax or plt.gca()
    ax.scatter(diag["fitted"], diag["residuals"], alpha=0.5, s=20)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("fitted values")
    ax.set_ylabel("residuals")
    ax.set_title("Residuals vs fitted — look for funnel, U-shape, or trend")
    return ax


def plot_qq(diag: dict, ax=None):
    ax = ax or plt.gca()
    stats.probplot(diag["residuals"], dist="norm", plot=ax)
    ax.set_title("QQ-plot of residuals vs Normal")
    return ax


def plot_residual_histogram(diag: dict, ax=None, bins: int = 30):
    ax = ax or plt.gca()
    ax.hist(diag["residuals"], bins=bins, edgecolor="black", alpha=0.7)
    ax.axvline(0, color="red", lw=1.0)
    ax.set_xlabel("residual")
    ax.set_ylabel("count")
    ax.set_title("Residual histogram — check skew and tails")
    return ax
```

## Cook's D for OLS models (statsmodels)

Cook's D measures the influence of each observation on the fitted coefficients. Threshold conventions:

- `D > 1` is the classical strict threshold
- `D > 4 / n` is a softer threshold that flags more rows for review

```python
import statsmodels.api as sm

# Fit OLS (statsmodels gives easy access to influence measures)
X_with_const = sm.add_constant(X_train)
ols = sm.OLS(y_train, X_with_const).fit()
influence = ols.get_influence()

cooks_d, _ = influence.cooks_distance
strict_flagged = np.flatnonzero(cooks_d > 1)
soft_flagged   = np.flatnonzero(cooks_d > 4 / len(y_train))
```

For non-OLS models (gradient boosting, neural nets), Cook's D is not defined. Use the `|residual| > sd_threshold * SD` flag from `residual_diagnostics` as a generic-model substitute.

## What the verdicts mean

| Pattern | Diagnosis | Action |
|---|---|---|
| Funnel (variance grows with fit) | Heteroscedasticity | log-transform target, switch to GLM/quantile, or use HC-robust SEs |
| U-shape | Missing nonlinear term | add polynomial / spline / interaction |
| Trend (slope on fitted) | Missing feature or systematic bias | investigate the missing covariate |
| Heavy tails on QQ | Non-Normal residuals | matters for inference; usually doesn't block prediction |
| Cook's D > 1 on a single row | High-leverage observation | investigate row before excluding; never silent-drop |

## Caveats

- Plots interpret on raw residuals; for non-OLS regression that uses a link function, work on the linear-predictor scale instead.
- For very small samples (< 30), QQ-plot judgments are noisy. Pair with the Shapiro-Wilk test from `ml-datasci/checking-test-assumptions`.
- For time-series data, also plot the residual ACF — autocorrelation in residuals means the model is missing temporal structure.
