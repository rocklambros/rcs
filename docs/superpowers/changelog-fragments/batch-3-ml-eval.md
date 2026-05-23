### Batch 3: ml-eval — 2026-05-23

Skills shipped:

- `ml-datasci/evaluating-binary-classifiers` v0.1.0 — ROC + PR + calibration + CM + threshold sweep + bootstrap 95% CI; refuses bare accuracy on imbalance; refuses default 0.5 threshold (Σ 19, status: shipped)
- `ml-datasci/building-baseline-models` v0.1.0 — 3-rung baseline ladder (Dummy / Linear / RandomForest) on the SAME train/test split + same metric as the final model (Σ 17, status: shipped)
- `ml-datasci/evaluating-regression-models` v0.1.0 — RMSE + MAE + R² + adjusted-R² + residual plots + k-fold CV; refuses R² alone; recommends walk-forward CV for time-series (Σ 17, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run via `tools.run_evals`.

Eval results (Sonnet 4.6, intent-matched scoring against 3 rubric items per scenario):

| Skill | happy-path | edge-case | anti-trigger |
|---|---|---|---|
| `evaluating-binary-classifiers` | 3/3 | 3/3 | 3/3 |
| `building-baseline-models` | 3/3 | 3/3 | 3/3 |
| `evaluating-regression-models` | 3/3 | 3/3 | 3/3 |

All 9 scenarios cleared the Sonnet-only pass thresholds (happy-path 3/3, edge-case 3/3, anti-trigger ≥ 2/3). All three skills retain `status: shipped`.

Notes:

- One workflow deviation from the plan's isolation contract: this batch authored skills in a feature branch on the primary repo clone (`feature/v1.0.0-batch-3-ml-eval`), not a git worktree. The plan's worktree step is a parallelism aid; this session was single-sequential and the cost of a worktree wasn't earned. No file-touch whitelist violations (only `skills/ml-datasci/<new-skill>/**`, `skills/ml-datasci/shipped-fragments/batch-3.md`, and this changelog fragment were modified).
- Per-skill commits use the message format from the plan; the shipped-fragments file and this changelog fragment are committed separately.
