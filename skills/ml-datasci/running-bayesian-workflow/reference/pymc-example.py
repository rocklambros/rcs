"""Hierarchical Bayesian logistic regression in PyMC.

Reference implementation for `running-bayesian-workflow`. Covers all eight
workflow steps end-to-end: determinism block, weakly-informative priors,
prior-predictive check, NUTS sampling with target_accept=0.95, the
five-check diagnostic gate, posterior-predictive check, LOO model comparison,
and posterior credible-interval reporting.

The site-level intercepts are written in non-centered form to handle the
hierarchical funnel without divergences.

Adapt: swap the likelihood, predictors, and the centered-vs-non-centered
parameterization to match the user's problem.
"""
from __future__ import annotations

# Step 1 — DETERMINISM. Set BEFORE importing PyMC / NumPyro.
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az

SEED = 2026
np.random.seed(SEED)


def build_model(df: pd.DataFrame) -> pm.Model:
    """Hierarchical logistic regression.

    df columns expected: site_id (int, 0..n_sites-1), treatment (0/1),
    age_std (standardized), outcome (0/1).
    """
    site_idx = df["site_id"].to_numpy()
    treatment = df["treatment"].to_numpy(dtype=float)
    age_std = df["age_std"].to_numpy(dtype=float)
    outcome = df["outcome"].to_numpy(dtype=int)
    n_sites = int(site_idx.max() + 1)

    coords = {"site": np.arange(n_sites), "obs": np.arange(len(df))}

    with pm.Model(coords=coords) as model:
        # Step 2 — weakly-informative priors scaled to standardized predictors.
        mu_alpha = pm.Normal("mu_alpha", mu=0.0, sigma=2.5)
        sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=1.0)

        # Non-centered parameterization to avoid funnel divergences.
        alpha_raw = pm.Normal("alpha_raw", mu=0.0, sigma=1.0, dims="site")
        alpha = pm.Deterministic("alpha", mu_alpha + sigma_alpha * alpha_raw, dims="site")

        beta_treatment = pm.Normal("beta_treatment", mu=0.0, sigma=1.0)
        beta_age = pm.Normal("beta_age", mu=0.0, sigma=1.0)

        logit_p = alpha[site_idx] + beta_treatment * treatment + beta_age * age_std
        pm.Bernoulli("y", logit_p=logit_p, observed=outcome, dims="obs")

    return model


def fit_and_diagnose(model: pm.Model) -> az.InferenceData:
    with model:
        # Step 3 — PRIOR PREDICTIVE. Plot the result to verify priors are sane.
        prior_pred = pm.sample_prior_predictive(samples=200, random_seed=SEED)

        # Step 4 — SAMPLE. target_accept=0.95 for hierarchical models.
        trace = pm.sample(
            draws=2000,
            tune=1000,
            chains=4,
            cores=4,
            target_accept=0.95,
            random_seed=SEED,
            return_inferencedata=True,
            progressbar=False,
        )
        trace.extend(prior_pred)

        # Step 6 — POSTERIOR PREDICTIVE.
        pp = pm.sample_posterior_predictive(trace, random_seed=SEED, progressbar=False)
        trace.extend(pp)

    # Step 5 — DIAGNOSTIC GATE. ANY failure here should block interpretation.
    summary = az.summary(trace, var_names=["mu_alpha", "sigma_alpha", "beta_treatment", "beta_age"])
    max_rhat = float(summary["r_hat"].max())
    min_ess_bulk = float(summary["ess_bulk"].min())
    min_ess_tail = float(summary["ess_tail"].min())
    n_divergent = int(trace.sample_stats["diverging"].sum())

    assert max_rhat <= 1.01, f"r_hat gate failed: max r_hat = {max_rhat}"
    assert min_ess_bulk >= 400 * 4, f"ess_bulk gate failed: min = {min_ess_bulk}"
    assert min_ess_tail >= 400 * 4, f"ess_tail gate failed: min = {min_ess_tail}"
    assert n_divergent == 0, f"divergence gate failed: {n_divergent} divergent transitions"

    return trace


def compare_models(traces: dict[str, az.InferenceData]) -> pd.DataFrame:
    """Step 7 — LOO model comparison.

    traces: mapping of model_name -> InferenceData with posterior + log_likelihood.

    Returns the comparison DataFrame. If any pareto_k > 0.7, the caller should
    re-run with k-fold cross-validation instead — PSIS-LOO is unreliable in
    that regime.
    """
    return az.compare(traces, ic="loo")


def report_posterior(trace: az.InferenceData, param: str = "beta_treatment") -> str:
    """Step 8 — report posterior mean, median, and 89% HDI as a directional sentence."""
    post = trace.posterior[param].values.flatten()
    mean = float(np.mean(post))
    median = float(np.median(post))
    hdi = az.hdi(trace, var_names=[param], hdi_prob=0.89)
    lo, hi = float(hdi[param].values[0]), float(hdi[param].values[1])
    direction = "increases" if mean > 0 else "decreases"
    return (
        f"Posterior for {param}: mean = {mean:+.3f}, median = {median:+.3f}, "
        f"89% HDI = [{lo:+.3f}, {hi:+.3f}]. "
        f"The effect {direction} the log-odds of the outcome over this credible interval."
    )
