### v5-batch-1: deployment — 2026-05-23

Skills shipped:
- `ml-datasci/packaging-model-for-deployment` v0.1.0 — packages a trained model as a versioned artifact + input/output schema + manifest + smoke test, refusing to certify deploy-ready without a smoke test that round-trips through the saved artifact (Σ 12, status: shipped)
- `ml-datasci/building-canary-rollout` v0.1.0 — staged traffic split with pre-committed business + technical + per-cohort guardrail thresholds and a deterministic auto-rollback trigger wired before the first flip (Σ 9, status: shipped)
- `ml-datasci/building-rollback-plan` v0.1.0 — versioned artifact store + deterministic triggers + oncall decision authority + named control-plane reversal mechanism + state reconciliation + smoke-test re-entry gate (Σ 10, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 general-purpose subagent dispatches (3 skills × 3 scenarios). All 9 scenarios scored 3/3 on the intent-matched rubric. Pass thresholds (happy: 3/3, edge: 3/3, anti: ≥ 2/3) met for every skill. Full 3-model (Haiku + Sonnet + Opus) validation deferred to a future re-run.

Notes: no failures, no deviations, no calibration corrections. All three skills retain `status: shipped`. Lint sweep clean (`tools.lint_frontmatter`, `tools.lint_skill_md`, `tools.lint_links` all OK). Full test suite passes (27/27).
