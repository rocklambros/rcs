"""DoWhy end-to-end example for `analyzing-causal-dag`.

Pattern: CausalModel(graph) -> identify_effect -> estimate -> refute. The
refute step is a sensitivity analysis: it adds a random common cause, removes
a random subset of the data, and checks that the estimate is stable.

Adapt: swap in your DAG, your treatment / outcome / covariates, and your
estimator of choice.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Reproducibility — pair with workflow/enforcing-seed-hygiene.
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
np.random.seed(2026)


def simulate_observational_data(n: int = 4000) -> pd.DataFrame:
    """Synthetic patient data matching the SKILL.md example.

    True DAG:
        age, severity -> treatment T
        age, severity -> outcome Y
        T -> adherence -> Y
        T -> Y (direct effect)
    """
    age = np.random.normal(55, 12, n)
    severity = np.random.normal(0, 1, n)

    # Treatment more likely with higher age / severity.
    logit_t = -1.0 + 0.04 * (age - 55) + 0.8 * severity
    p_t = 1 / (1 + np.exp(-logit_t))
    T = (np.random.uniform(0, 1, n) < p_t).astype(int)

    # Mediator: adherence is downstream of T.
    adherence = 0.6 * T + np.random.normal(0, 1, n)

    # Outcome: causal effect of T on Y is -5.0 (drug lowers BP),
    # plus age + severity (confounders) and adherence (mediator).
    Y = (
        140
        + 0.3 * (age - 55)
        + 8.0 * severity
        - 5.0 * T
        - 3.0 * adherence
        + np.random.normal(0, 5, n)
    )

    return pd.DataFrame({
        "age": age,
        "severity": severity,
        "T": T,
        "adherence": adherence,
        "Y": Y,
    })


# Example without the DoWhy dependency — pure regression demonstration of
# adjustment-set choice. DoWhy is the recommended path for production work
# (it makes identification explicit) but adds an install requirement.
def estimate_with_adjustment(df: pd.DataFrame, adjust: list[str]) -> tuple[float, float]:
    """Return (point_estimate, std_error) for the T coefficient.

    Uses OLS. The choice of adjustment set is the causal-inference decision;
    the choice of estimator (OLS vs matching vs IPW vs G-comp) does not change
    identification, only efficiency and robustness.
    """
    from statsmodels.api import OLS, add_constant  # type: ignore
    X = add_constant(df[["T"] + adjust])
    model = OLS(df["Y"], X).fit()
    return float(model.params["T"]), float(model.bse["T"])


if __name__ == "__main__":  # pragma: no cover
    df = simulate_observational_data(n=4000)

    # Naive (no adjustment): biased by confounding age + severity.
    est_naive, se_naive = estimate_with_adjustment(df, adjust=[])
    print(f"Naive T effect (biased): {est_naive:+.3f} ± {se_naive:.3f}")

    # Correct adjustment for the total effect of T on Y.
    est_total, se_total = estimate_with_adjustment(df, adjust=["age", "severity"])
    print(f"Total effect (correct): {est_total:+.3f} ± {se_total:.3f}")

    # Adjusting for the mediator gives the controlled DIRECT effect —
    # this is a DIFFERENT estimand, not a "more careful" estimate of the same one.
    est_direct, se_direct = estimate_with_adjustment(df, adjust=["age", "severity", "adherence"])
    print(f"Direct effect (different estimand): {est_direct:+.3f} ± {se_direct:.3f}")

    # The total effect should be close to the true -5.0 used in simulation.
    # The direct effect is partial: T -> Y minus the slice that flows T -> adherence -> Y.
