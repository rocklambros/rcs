# Bayesian Diagnostic Cheatsheet

Reference for the five-check diagnostic gate in `running-bayesian-workflow`. Every check must pass before the posterior is interpreted. Each row gives the threshold, the cause when it fails, and the concrete fix.

## The five checks

| Diagnostic | Pass threshold | Failure means | Fix |
|---|---|---|---|
| `r_hat` | ≤ 1.01 for every parameter | Chains have not mixed; posterior may be multi-modal or chains stuck in different modes | Run more chains (≥ 4). If still failing, the posterior is likely multi-modal — re-think the model |
| `ess_bulk` | ≥ 400 per chain (so ≥ 1600 with 4 chains) | Bulk of the posterior is poorly explored; mean and median estimates have high Monte Carlo error | Run more draws, OR tighten priors (often the same root cause as divergences) |
| `ess_tail` | ≥ 400 per chain (so ≥ 1600 with 4 chains) | Tails of the posterior poorly explored; tail-quantile / HDI claims unreliable | Run more draws; re-parameterize if hierarchical |
| `divergences` | 0 ideally; < 10 non-systematic acceptable with caveat | NUTS hit numerical instability on the typical set; posterior is biased toward the easy-to-sample region | Re-parameterize hierarchical models to non-centered form; raise `target_accept` to 0.95–0.99; tighten variance-component priors |
| `E-BFMI` | ≥ 0.3 per chain | Energy transitions are too small relative to marginal energy variance; sampler cannot traverse the posterior | Tighten variance-component priors; re-parameterize; check for unidentified parameters |

## Failure pattern → recipe

### Divergences clustered in the funnel

Symptom: `divergences = 50+`, concentrated where a group-level SD is small.

Recipe:

1. Re-parameterize the affected hierarchical level to non-centered form:
   ```python
   # Centered (problematic when sigma is small)
   alpha = pm.Normal("alpha", mu=mu_alpha, sigma=sigma_alpha, dims="group")

   # Non-centered (the fix)
   alpha_raw = pm.Normal("alpha_raw", mu=0, sigma=1, dims="group")
   alpha = pm.Deterministic("alpha", mu_alpha + sigma_alpha * alpha_raw, dims="group")
   ```
2. Raise `target_accept` from 0.8 → 0.95.
3. Tighten the prior on `sigma_alpha` from `HalfNormal(100)` → `HalfNormal(1)`.
4. Re-sample and re-check.

### r_hat persistently > 1.01

Symptom: One or more parameters has `r_hat = 1.3` after multiple re-runs.

Recipe: The posterior is multi-modal. NUTS within a single run cannot mix between modes. Options:

1. Re-think the model — non-identifiable parameters (e.g., sign-flip symmetry) cause this. Add a constraint or re-parameterize.
2. Tighter priors that break the symmetry.
3. Multi-start initialization plus more chains can sometimes mix, but is a workaround not a fix.

### ESS bulk low everywhere

Symptom: `ess_bulk = 80` per chain on a 4-chain run.

Recipe: The sampler is heavily autocorrelated. Either run more draws (cheap), tighten priors (free), or re-parameterize (one-time effort). If ESS is uniformly low, the issue is sampler step size or mass-matrix adaptation — try a longer warmup (`tune=3000` instead of `tune=1000`).

### ESS tail much lower than ESS bulk

Symptom: `ess_bulk = 2000` but `ess_tail = 150`.

Recipe: The posterior has heavy tails or is bi-modal in the tails. Tail-quantile claims (89% HDI lower bound, 99% upper bound) are unreliable. Either run more draws or report a tighter interval (e.g., 50% HDI instead of 89%).

### Low E-BFMI

Symptom: `E-BFMI = 0.18` on one or more chains.

Recipe: The energy distribution is poorly explored. Almost always traces back to a variance-component prior that is too diffuse. Tighten priors on hierarchical SDs and re-sample.

## LOO / WAIC pareto_k

Threshold: All `pareto_k ≤ 0.7` for LOO to be reliable.

If `pareto_k > 0.7` for some observations:

- LOO importance-sampling weights have unbounded variance for those points
- The posterior is unduly influenced by a small number of high-leverage observations
- Switch to `k-fold` cross-validation, OR refit without the high-leverage points to check sensitivity

## When the model is fine but the priors are wrong

Prior-predictive predicts impossible outcomes (e.g., negative counts, probabilities > 1, blood pressure of 500 mmHg). The prior is too diffuse. Tighten and re-check.

## Determinism

Same seed, different machine, different posterior. The seed alone is not enough — pin BLAS thread counts and JAX device routing BEFORE importing the modeling library:

```python
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["JAX_PLATFORM_NAME"] = "cpu"
```

This is documented in `workflow/enforcing-seed-hygiene` and the `incident-rank-validation` failure.
