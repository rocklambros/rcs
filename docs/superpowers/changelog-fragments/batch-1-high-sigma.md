### Batch 1: high-sigma — 2026-05-23

Skills shipped:

- `workflow/enforcing-seed-hygiene` v0.1.0 — first-cell seed gate covering Python/NumPy/PyTorch/JAX/TF/R + CPU-pin for cross-platform sampler determinism + pre-commit hook (Σ 20, status: shipped)
- `workflow/validating-temporal-fields` v0.1.0 — reject-future + min-year-fallback + event-vs-disclosure-date separation for temporal corpora (Σ 19, status: shipped)
- `security/auditing-pinned-dependencies` v0.1.0 — grep audit for unpinned installs across README/Dockerfile/CI/package.json/mcp.json with per-file findings + pinned-form suggestions (Σ 19, status: shipped)
- `ml-datasci/reporting-effect-sizes` v0.1.0 — per-test-family effect-size selector + 95% CI + direction sentence; refuses bare-p-value (Σ 19, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 12 dispatches (4 skills × 3 scenarios). Full 3-model (Haiku + Sonnet + Opus) validation deferred to a future re-run.

Eval results (all scenarios scored 3/3):

| Skill | Happy-path | Edge-case | Anti-trigger |
|---|---|---|---|
| `enforcing-seed-hygiene` | 3/3 | 3/3 | 3/3 |
| `validating-temporal-fields` | 3/3 | 3/3 | 3/3 |
| `auditing-pinned-dependencies` | 3/3 | 3/3 | 3/3 |
| `reporting-effect-sizes` | 3/3 | 3/3 | 3/3 |

All 4 skills meet PRAGMATIC pass thresholds (happy 3/3, edge 3/3, anti ≥ 2/3) and retain `status: shipped`.

Notes: no calibration corrections needed; all 12 scenarios passed on the first eval pass. Authored in-place on `feature/v1.0.0-batch-1-high-sigma` in the main repo (no worktree) per session feedback memory.
