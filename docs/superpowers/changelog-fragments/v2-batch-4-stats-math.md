### v2-batch-4: stats + math depth — 2026-05-23

Skills shipped:
- `ml-datasci/analyzing-regression-diagnostics` v0.1.0 — six-step regression diagnostic battery (linearity, Normality, homoscedasticity, autocorrelation, influence, multicollinearity) with per-diagnostic verdict + remediation; refuses to run on tree / kernel / neural models (Σ 14, status: shipped)
- `ml-datasci/running-power-analysis` v0.1.0 — prospective power / n / MDE calculation for any planned test with required effect-size provenance and sensitivity check; refuses post-hoc / observed power and routes to TOST or CI interpretation (Σ 13, status: shipped)
- `workflow/auditing-mathematical-claims` v0.1.0 — generalized ATACE four-field per-claim audit template (Location · Concern · Strongest-counter · Stops-mattering-if) for theorems / lemmas / bounds / definitions with severity × likelihood / detectability triage; routes empirical claims to running-adversarial-premortem (Σ 13, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 dispatches (3 scenarios × 3 skills); all scored 3/3 against intent. Full 3-model (Haiku / Sonnet / Opus) validation deferred to a future re-run.

Notes: No deviations or calibration corrections. All three skills retained `status: shipped` after eval validation.
