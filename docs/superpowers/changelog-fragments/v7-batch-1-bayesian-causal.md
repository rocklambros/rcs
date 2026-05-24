### v7-batch-1: Bayesian + uncertainty + causal — 2026-05-23

Skills shipped:

- `ml-datasci/running-bayesian-workflow` v0.1.0 — weakly-informative priors, prior-predictive check, NUTS sampling, five-check diagnostic gate (r_hat / ESS bulk / ESS tail / divergences / E-BFMI), posterior-predictive check, LOO comparison, CPU-pin determinism block (Σ 10, status: shipped)
- `ml-datasci/building-conformal-prediction-set` v0.1.0 — split-conformal classification (softmax score), regression (absolute-residual), and CQR; finite-sample-corrected quantile (n+1)/n; coverage + set-size reporting; exchangeability red-flag checklist (Σ 11, status: shipped)
- `ml-datasci/analyzing-causal-dag` v0.1.0 — node classification (confounder / mediator / collider / IV), backdoor criterion, adjustment-set screening, E-value sensitivity analysis, RCT anti-trigger (Σ 9, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 subagent dispatches (3 scenarios × 3 skills), all returning 3/3 rubric pass against intent-matched scoring. Full 3-model (Haiku / Sonnet / Opus) validation deferred to a future re-run.

Eval results:

| Skill | Happy-path | Edge-case | Anti-trigger |
|---|---|---|---|
| `running-bayesian-workflow` | 3/3 | 3/3 | 3/3 |
| `building-conformal-prediction-set` | 3/3 | 3/3 | 3/3 |
| `analyzing-causal-dag` | 3/3 | 3/3 | 3/3 |

Notes: all three skills passed the Sonnet-only PRAGMATIC thresholds (happy-path 3/3, edge-case 3/3, anti-trigger ≥ 2/3) on the first authoring pass. No demotions. Lint and pytest clean (27/27).
