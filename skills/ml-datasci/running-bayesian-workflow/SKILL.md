---
name: running-bayesian-workflow
description: >
  Walks the full Bayesian workflow for a regression or hierarchical-regression
  problem: picks weakly-informative priors with prior-predictive checks, samples
  the posterior with NUTS (PyMC / NumPyro / Stan / brms), validates the fit
  with R-hat, ESS-bulk, ESS-tail, divergence count, and E-BFMI, then runs
  posterior-predictive checks plus LOO / WAIC for model comparison. Triggers
  whenever the user fits a Bayesian model, asks about priors, reports
  divergences or low effective sample size, wants posterior intervals not
  point estimates, or hands over a hierarchical / multilevel design. Refuses
  to ship a Bayesian fit with un-checked diagnostics and refuses to engage on
  pure-frequentist OLS where the Bayesian machinery adds no value.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - stats-student
  - ml-engineer
  - instructor
evidence:
  - incident-rank-validation
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Running Bayesian Workflow

## When to use

Trigger this skill when the user does any of the following:

- Asks "how do I fit a Bayesian model?" or names PyMC / NumPyro / Stan / brms / rstanarm
- Reports diagnostic output: `divergences`, `r_hat > 1.01`, `ess_bulk < 400`, `BFMI < 0.3`, "the sampler is slow"
- Wants posterior credible intervals, posterior-predictive plots, or model comparison via LOO / WAIC
- Has a hierarchical / multilevel design (varying intercepts or slopes across groups) that frequentist OLS handles poorly
- Needs to encode prior information from a previous study, a meta-analysis, or expert elicitation
- Reports cross-platform non-reproducibility on a Bayesian fit — same seed, different machine, different posterior (CPU-pin issue; pair with `workflow/enforcing-seed-hygiene`)
- Wants to quantify uncertainty about a parameter, not just point-estimate it

## When NOT to use

Skip and hand off when:

- The user wants a single point estimate from an OLS-class problem with no hierarchy, no prior information, and large n — frequentist OLS / GLM is faster, cheaper, and equally informative. Hand off to `ml-datasci/analyzing-regression-diagnostics`
- The user is writing a sklearn pipeline that needs cross-validation scores — Bayesian fits don't naturally produce CV scores; use the frequentist path
- This is a teaching context where the explicit goal is contrasting Bayesian vs frequentist mechanics — follow the lecture, not the workflow
- The user already has a fit and only wants posterior credible-interval extraction from the saved trace — that's a sub-task, not the full workflow
- The dataset is so small (n < 10) or so unidentified that any reasonable prior dominates the posterior — flag and stop before the user reports posterior-as-evidence

## Quick start

User says: "I'm fitting a hierarchical logistic regression in PyMC: 30 sites, ~50 patients per site, binary outcome. Walk me through it."

Skill response, in order:

1. **Lock determinism** before fitting: set seeds across the stack (`numpy`, `pymc`, OS env) and pin to CPU for cross-platform reproducibility (`OMP_NUM_THREADS=1`, `JAX_PLATFORM_NAME=cpu` for NumPyro). Cross-reference `workflow/enforcing-seed-hygiene`. The `incident-rank-validation` failure was a NUTS fit that diverged across machines without the CPU pin.
2. **Pick weakly-informative priors** scaled to the data: site intercepts `~ Normal(0, sigma_alpha)`, `sigma_alpha ~ HalfNormal(1)`, fixed-effect coefficients `~ Normal(0, 1)` on standardized predictors. Avoid `Normal(0, 1000)` "flat" priors — they trigger funnel divergences and slow mixing.
3. **Run a prior-predictive check** before sampling: draw 200 samples from the prior, push through the likelihood, plot the predicted outcome distribution. If the prior predicts impossible outcomes (e.g., positive cure probability of 99.9% with no data), tighten the prior.
4. **Sample with NUTS**: 4 chains, 2000 draws, 1000 warmup. `target_accept = 0.95` for hierarchical models (default 0.8 often diverges on funnels).
5. **Check diagnostics** in order (any failure → fix before interpreting):
   - `r_hat ≤ 1.01` for every parameter
   - `ess_bulk ≥ 400` per chain × 4 chains = 1600 total
   - `ess_tail ≥ 400`
   - `divergences == 0` (or document why a small handful are acceptable)
   - `E-BFMI ≥ 0.3` per chain
6. **Posterior-predictive check** (`pm.sample_posterior_predictive`): overlay observed vs predicted distributions; flag systematic miscalibration.
7. **Model comparison** if multiple candidates: `az.compare(loo_dict)`; rank by `elpd_loo`; flag any model with `pareto_k > 0.7` for any observation (LOO is unreliable there — switch to k-fold).
8. **Report posterior intervals**, not point estimates: 89% or 95% credible interval per parameter of interest, plus the posterior-predictive plot.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| framework | "pymc" \| "numpyro" \| "stan" \| "brms" \| "rstanarm" | yes | — | Drives the API surface and the diagnostic naming |
| model_kind | "linear" \| "logistic" \| "hierarchical" \| "glm" \| "survival" \| "custom" | yes | — | Picks the likelihood and the default prior recipe |
| n_chains | int | no | 4 | Number of independent NUTS chains; `r_hat` needs ≥ 2 chains to be computable |
| n_draws | int | no | 2000 | Post-warmup draws per chain |
| n_warmup | int | no | 1000 | Warmup / tuning draws per chain; NUTS uses these to adapt the mass matrix |
| target_accept | float in (0, 1) | no | 0.95 (hierarchical) / 0.8 (flat) | NUTS step-size target; raise to 0.95–0.99 for funnels |
| priors | "weakly-informative" \| "informative" \| "user-specified" | no | "weakly-informative" | Default recipe vs explicit prior dict |
| prior_predictive_n | int | no | 200 | Draws for the prior-predictive check |
| posterior_predictive_n | int | no | 1000 | Draws for the posterior-predictive check |
| seed | int | yes | — | Global seed; combine with CPU pin for cross-platform reproducibility |
| cpu_pin | bool | no | true | Set `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `JAX_PLATFORM_NAME=cpu`; required for cross-platform determinism |
| comparison_method | "loo" \| "waic" \| "k-fold" | no | "loo" | Cross-model comparison; switch to k-fold when LOO `pareto_k > 0.7` |

## Workflow

Copy this checklist into the response and check off each step as it lands:

```
Bayesian-workflow progress:
- [ ] Step 1: Lock determinism (seeds + CPU pin) BEFORE any sampling call
- [ ] Step 2: Pick weakly-informative priors scaled to standardized predictors
- [ ] Step 3: Prior-predictive check — plot predicted outcome distribution
- [ ] Step 4: Sample with NUTS, 4 chains, target_accept set for the model class
- [ ] Step 5: Diagnostic gate (r_hat, ess_bulk, ess_tail, divergences, E-BFMI)
- [ ] Step 6: Posterior-predictive check — overlay observed vs predicted
- [ ] Step 7: Model comparison (LOO / WAIC) if multiple candidates
- [ ] Step 8: Report posterior credible intervals, not point estimates
```

### Step 1 — Determinism

The same seed alone is NOT sufficient for cross-platform reproducibility. NUTS internally uses multi-threaded BLAS and platform-specific RNG paths. The pin block:

```python
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["JAX_PLATFORM_NAME"] = "cpu"  # NumPyro / BlackJAX
import numpy as np
import pymc as pm
SEED = 2026
np.random.seed(SEED)
```

The `incident-rank-validation` failure was exactly this: same seed, same code, different rank-validation posterior on Linux GPU vs Mac CPU because of the missing CPU pin.

### Step 2 — Prior choice

| Predictor / parameter | Weakly-informative default | Reason |
|---|---|---|
| Fixed-effect coefficient on standardized X | `Normal(0, 1)` | Standardized predictors keep slope in `[-3, 3]` with high prior mass |
| Intercept on standardized outcome | `Normal(0, 2.5)` | Stan / brms default; covers plausible intercept range |
| Variance components (random-effects SD) | `HalfNormal(1)` or `HalfStudentT(3, 0, 1)` | Bounded ≥ 0, weak preference for small SD |
| Group-level means in hierarchical model | `Normal(mu_overall, sigma_group)` | Partial pooling |
| Correlation matrices | `LKJ(eta=2)` | Weak preference for non-extreme correlations |
| Observation noise | `HalfNormal(sd(y))` | Scaled to outcome SD |

Avoid `Normal(0, 1000)` and `Uniform(-inf, inf)` "non-informative" priors — they cause divergences on hierarchical funnels and add no real information.

### Step 3 — Prior-predictive check

```python
with model:
    prior_pred = pm.sample_prior_predictive(samples=200, random_seed=SEED)
az.plot_ppc(prior_pred, group="prior")
```

The plot should overlap the plausible range of the outcome. If priors predict impossible outcomes (negative counts, probabilities > 1, blood pressure of 500 mmHg), tighten before fitting.

### Step 4 — Sampling

```python
with model:
    trace = pm.sample(
        draws=2000, tune=1000, chains=4, cores=4,
        target_accept=0.95, random_seed=SEED, return_inferencedata=True,
    )
```

`target_accept` 0.95 for hierarchical models (handles funnels). Drop to 0.8 only for flat non-hierarchical models when the sampler is already clean.

### Step 5 — Diagnostic gate (DO NOT skip)

Run all five checks. ANY failure means stop and re-fit; never interpret a fit that failed diagnostics.

| Check | Threshold | What failure means |
|---|---|---|
| `r_hat` | ≤ 1.01 for all params | Chains have not mixed; posterior is multi-modal or sampler stuck |
| `ess_bulk` | ≥ 400 per chain × n_chains | Bulk of posterior poorly explored; intervals are unreliable |
| `ess_tail` | ≥ 400 per chain × n_chains | Tails poorly explored; tail-quantile claims are unreliable |
| `divergences` | 0 (or < 10 + non-systematic) | Sampler hit numerical instability on the typical set; intervals biased |
| `E-BFMI` | ≥ 0.3 per chain | Energy poorly explored; sampler can't traverse the posterior |

Fixes when a check fails:

- Divergences on a hierarchical model → re-parameterize to non-centered form (`alpha = mu + sigma * alpha_raw` with `alpha_raw ~ Normal(0, 1)`)
- Low ESS → run more draws OR tighten priors (often the same root cause as divergences)
- High r_hat → run more chains; if it persists, the posterior is multi-modal and the model is mis-specified
- Low E-BFMI → tighten priors on variance components; flat HalfNormal(100) is a common cause

### Step 6 — Posterior-predictive check

```python
with model:
    pp = pm.sample_posterior_predictive(trace, random_seed=SEED)
az.plot_ppc(pp)
```

Overlay observed distribution (histogram) vs posterior-predictive draws (line cloud). Systematic miscalibration (predicted center off, predicted tails wrong) means the model is mis-specified — likelihood family wrong, predictor missing, or hierarchy under-pooling.

### Step 7 — Model comparison

```python
compare_df = az.compare({"m1": trace_m1, "m2": trace_m2}, ic="loo")
```

Rank by `elpd_loo` (expected log predictive density, leave-one-out). The model with the highest `elpd_loo` is preferred; the difference `delta_elpd` with `dse` (SE of the difference) is the comparison statistic. Treat `|delta_elpd| < 2 × dse` as "indistinguishable."

If `pareto_k > 0.7` for any observation, LOO is unreliable — switch to `k-fold` cross-validation. PSIS-LOO is an importance-sampling approximation that breaks down for high-leverage observations.

### Step 8 — Reporting

Per parameter of interest, report:

- Posterior **mean** AND **median** (they disagree under skew)
- 89% or 95% **credible interval** (HDI preferred over equal-tailed for skew)
- A short directional sentence: "The posterior for `treatment_effect` is concentrated at +0.42 [89% HDI: 0.18, 0.65], i.e., treatment increases the outcome by 0.18–0.65 with 89% posterior probability."
- The diagnostic summary line: "All r_hat < 1.01, min ESS_bulk = 1820, 0 divergences, all E-BFMI > 0.5."

## Outputs

A short report containing:

1. **Determinism block** — seeds + CPU pin code, captured for reproducibility
2. **Prior table** — parameter, prior distribution, justification
3. **Prior-predictive plot** — visual sanity check on the prior
4. **Diagnostic table** — r_hat, ESS bulk/tail, divergences, E-BFMI per parameter
5. **Posterior-predictive plot** — observed vs predicted distribution
6. **Posterior summary table** — mean, median, 89% HDI per parameter of interest
7. **Model comparison table** (if applicable) — elpd_loo, dse, weight per candidate
8. **Reported credible intervals** — directional sentences per parameter of interest

## Failure modes

- **Skipping the diagnostic gate** — interpreting a posterior with `r_hat = 1.3` or divergences treats noise as signal. Caught by: Step 5 is a hard gate; refuse to report intervals until all five checks pass.
- **Cross-platform non-determinism** — same seed, different posterior on a different machine. Caught by: Step 1 CPU pin (`OMP_NUM_THREADS=1`, `JAX_PLATFORM_NAME=cpu`); cross-reference the `incident-rank-validation` failure pattern.
- **Flat priors on hierarchical variance components** — `sigma ~ HalfNormal(100)` triggers funnel divergences. Caught by: Step 2 default of `HalfNormal(1)`; reject `HalfNormal(>10)` without justification.
- **Centered parameterization on a funnel** — `alpha[i] ~ Normal(mu, sigma)` with small `sigma` posterior → divergences cluster near the funnel neck. Caught by: Step 5 fix recipe — re-parameterize to non-centered form.
- **LOO with high pareto_k** — PSIS-LOO is unreliable when `pareto_k > 0.7`. Caught by: Step 7 explicitly checks pareto_k and switches to k-fold when needed.
- **Reporting posterior mean alone under skew** — for log-normal or heavy-tailed posteriors, mean ≠ median. Caught by: Step 8 requires both, plus HDI.
- **Default `target_accept=0.8` on hierarchical** — divergences appear; user re-runs many times without raising target_accept. Caught by: Step 4 default of 0.95 for hierarchical models.
- **Prior-predictive predicts impossible outcomes** — flat priors on logit-scale parameters often produce predicted probabilities concentrated at 0 or 1. Caught by: Step 3 mandates the prior-predictive plot before any sampling time is spent.

## References

- [`reference/pymc-example.py`](reference/pymc-example.py) — copy-paste hierarchical-logistic example covering determinism, priors, prior-predictive, sampling, all five diagnostic checks, posterior-predictive, and LOO comparison
- [`reference/diagnostic-cheatsheet.md`](reference/diagnostic-cheatsheet.md) — table of every diagnostic, threshold, likely cause on failure, and fix recipe
- [PyMC documentation](https://www.pymc.io/) — official API and diagnostic guidance
- [Stan reference manual — convergence diagnostics](https://mc-stan.org/docs/reference-manual/analysis.html) — canonical reference for r_hat, ESS, E-BFMI
- [Bayesian Workflow paper (Gelman, Vehtari, Simpson et al., 2020)](https://arxiv.org/abs/2011.01808) — the workflow this skill encodes
- `workflow/enforcing-seed-hygiene` — required prerequisite for the determinism block
- `ml-datasci/analyzing-regression-diagnostics` — frequentist alternative when Bayesian machinery is overkill
- `ml-datasci/building-conformal-prediction-set` — frequentist uncertainty without priors

## Examples

### Example 1: Hierarchical logistic regression (happy-path)

Input: "I'm fitting a hierarchical logistic regression in PyMC: 30 sites, ~50 patients per site, binary outcome. The default sampler has 47 divergences."

Output: Step 1 lock seeds + CPU pin. Step 2 review priors — most likely cause of divergences is a flat prior on the site-level SD (`sigma_site ~ HalfNormal(100)`); tighten to `HalfNormal(1)`. Step 3 prior-predictive check overlapping plausible outcome range. Step 4 re-sample with `target_accept = 0.95` AND re-parameterize the site intercepts to non-centered form (`alpha_site = mu + sigma_site * alpha_site_raw`, `alpha_site_raw ~ Normal(0, 1)`). Step 5 expect divergences to drop to 0; verify all r_hat < 1.01 and ESS_bulk > 1600. Step 6 posterior-predictive overlay observed vs predicted. Step 8 report posterior treatment-effect HDI plus the diagnostic summary line.

### Example 2: NUTS divergences across machines (edge-case)

Input: "Same PyMC model, same seed (2026), same code. On my Mac laptop the posterior treatment-effect mean is +0.42. On our Linux GPU server it's +0.31. Why?"

Output: This is the cross-platform determinism failure documented in `incident-rank-validation`. The seed alone does not pin BLAS thread count, MKL behavior, or JAX device routing. NUTS sampling is sensitive to these because the mass-matrix adaptation depends on the order of floating-point operations. Fix: set `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, and `JAX_PLATFORM_NAME=cpu` (NumPyro / BlackJAX) BEFORE importing PyMC. Re-run both machines with the pin; the posteriors should now agree to within sampling noise (< 0.01 on the mean for 2000 × 4 draws). If they still disagree, the issue is elsewhere — likely a Python or NumPy version mismatch, or a non-deterministic data-loading order. Cross-reference `workflow/enforcing-seed-hygiene`.

### Example 3: Simple OLS on 50,000 rows, no hierarchy, no prior information (anti-trigger)

Input: "I have 50,000 rows of house price data and want to fit a simple linear regression of price on square footage, bedrooms, and zip code. Should I do it Bayesian?"

Output: Not unless there's a reason. For this setup — single-level OLS, large n, no hierarchical structure, no prior information to encode, no need for posterior intervals on a derived quantity — frequentist OLS is faster (seconds vs minutes), cheaper (no sampler diagnostics to manage), and gives the same point estimates plus standard errors. The Bayesian fit would converge cleanly with diffuse priors but offers no scientific advantage. Hand off to `ml-datasci/analyzing-regression-diagnostics` for the OLS path. Bayesian becomes the right choice if: (a) zip code has many groups and a varying-intercept (hierarchical) structure is needed, (b) prior information from a previous study should be encoded, (c) the user needs posterior credible intervals on a derived quantity like the expected price at a hypothetical new house. None of those apply here.

## See also

- `workflow/enforcing-seed-hygiene` — the CPU-pin discipline that prevents cross-platform divergence drift
- `ml-datasci/analyzing-regression-diagnostics` — frequentist alternative for non-hierarchical regression
- `ml-datasci/building-conformal-prediction-set` — frequentist uncertainty quantification without priors
- `ml-datasci/running-hyperparameter-sweep` — when the Bayesian model itself has hyperparameters (priors counted as hyperparameters here)
- `ml-datasci/checking-test-assumptions` — paired skill for the frequentist assumption-check path

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
