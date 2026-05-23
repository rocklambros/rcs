# ML / Data Science Track

For data scientists, ML engineers, applied-ML practitioners, and stats students.

This track encodes disciplines that recur across model-building work: statistical-test selection from data characteristics, classifier and regression evaluation, calibration, leakage firewalls, baseline-model discipline, regression diagnostics, fine-tuning audits, and RAG retrieval evaluation.

## Shipped skills

_Populated in Phase 2._

| Skill | What it does | When to use | Σ |
|---|---|---|---|

## Planned skills

### Statistical / mathematical reasoning

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `selecting-statistical-test` | Decision tree from data characteristics → recommends t / Welch / Wilcoxon / Mann-Whitney / Sign / paired-t / Fisher / χ², names the gating assumption | 18 | 📝 planned (Phase 3) |
| `checking-test-assumptions` | Shapiro / Levene / QQ / residual diagnostics → pass/fail per assumption with evidence | 18 | 📝 planned (Phase 3) |
| `reporting-effect-sizes` | Cohen's d / Cliff's δ / R² + 95% CI + direction; refuses bare p-value | 19 | 📝 planned (Phase 2) |
| `interpreting-conflicting-tests` | Assumption-status table to commit to a winner when t / Wilcoxon disagree | 16 | 📝 planned |
| `analyzing-regression-diagnostics` | Linearity / residual normality / homoscedasticity / leverage / Cook's D | 14 | 📝 planned |
| `running-power-analysis` | Sample-size + MDE + effect-size sanity check before running the study | 13 | 📝 planned |
| `running-bayesian-workflow` | Priors → posterior-predictive → R-hat/ESS → divergence check | 10 | 📝 planned |
| `building-conformal-prediction-set` | Split-conformal calibration, coverage check | 11 | 📝 planned |
| `analyzing-causal-DAG` | Confounder checklist, do-calculus walk | 9 | 📝 planned |

### ML / DL hygiene

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-train-test-split` | Leakage detection, stratification check, group-aware verification, temporal split for time series | 18 | 📝 planned (Phase 3) |
| `building-baseline-models` | Dummy / LogReg / RF before fancy model | 17 | 📝 planned (Phase 4) |
| `evaluating-binary-classifiers` | ROC + PR + calibration + CM + threshold sweep + class-imbalance + bootstrap CI from (y_true, y_proba) | 19 | 📝 planned (Phase 4) |
| `evaluating-regression-models` | RMSE / MAE / R² / residual plots + cross-validation | 17 | 📝 planned (Phase 4) |
| `evaluating-multiclass-classifiers` | Macro/micro F1, per-class PR, confusion matrix, top-k | 16 | 📝 planned |
| `tuning-classification-threshold` | Domain-aware threshold sweep (FN-cost » FP-cost in security) | 16 | 📝 planned |
| `running-chollet-ratio-check` | Samples-to-mean-seq-length → BoW vs LSTM vs Transformer recommendation | 16 | 📝 planned |
| `enforcing-leakage-firewall` | LOFO / hub-firewall / group-leakage check | 14 | 📝 planned |
| `comparing-models-fairly` | McNemar / paired-folds tests | 14 | 📝 planned |
| `auditing-deep-learning-overfit` | Train/val gap, learning curves, weight-norm growth | 12 | 📝 planned |
| `writing-model-cards` | AIBOM-compatible model card from fitted model + eval results | 13 | 📝 planned |
| `generating-shap-explanations` | SHAP / LIME / IG / permutation-importance scaffolding | 11 | 📝 planned |
| `auditing-model-fairness` | Eq-opp / dem-parity / calibration-within-group + intersectional | 12 | 📝 planned |

### RAG / fine-tuning / MLOps

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `evaluating-rag-retrieval` | recall@k / MRR / nDCG / faithfulness / answer-relevance | 14 | 📝 planned |
| `auditing-chunking-strategy` | Chunk-size + overlap + boundary-aware splits | 13 | 📝 planned |
| `auditing-embedding-drift` | KL/cosine drift between embedding distributions over time | 11 | 📝 planned |
| `building-rag-eval-set` | Golden Q/A + held-out + adversarial set | 12 | 📝 planned |
| `selecting-embedding-model` | Intrinsic vs extrinsic comparison | 13 | 📝 planned |
| `evaluating-OOD-detection` | Mahalanobis / energy / max-softmax-prob | 9 | 📝 planned |
| `auditing-sft-dataset` | PII / dup / leakage / format / chat-template | 11 | 📝 planned |
| `running-eval-before-after-finetune` | Paired McNemar / regression on perplexity | 12 | 📝 planned |
| `writing-finetune-spec-sheet` | Base model + data + recipe + eval | 10 | 📝 planned |
| `scaffolding-pytorch-training-loop` | Seed / AMP / grad-clip / lr-sched / early-stop / resume | 12 | 📝 planned |
| `running-hyperparameter-sweep` | Seed-stratified optuna/ray-tune | 12 | 📝 planned |
| `packaging-model-for-deployment` | Signature + schema + smoke test | 12 | 📝 planned |
| `building-canary-rollout` | Traffic-split policy + rollback | 9 | 📝 planned |
| `monitoring-data-drift` | PSI / KL / KS per feature | 11 | 📝 planned |
| `monitoring-prediction-drift` | Calibration-over-time, score-distribution shift | 11 | 📝 planned |
| `auditing-inference-latency-budget` | P50/P95/P99 budget vs SLO | 10 | 📝 planned |
| `building-rollback-plan` | Versioned rollback + smoke tests | 10 | 📝 planned |

### Synthetic data + privacy

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-synthetic-data-utility` | Downstream-task fidelity | 11 | 📝 planned |
| `auditing-synthetic-data-leakage` | Membership-inference | 10 | 📝 planned |
| `applying-differential-privacy` | ε/δ budget tracking | 8 | 📝 planned |
| `building-data-dictionary-with-consent-class` | Per-field consent class for DSR readiness | 11 | 📝 planned |
| `generating-data-dictionary` | Per-field type / range / null / semantic class | 15 | 📝 planned |

### Performance / cost (LLM apps)

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `profiling-llm-cost` | Per-call token cost rollup | 14 | 📝 planned |
| `auditing-prompt-token-budget` | Detect prompt bloat | 16 | 📝 planned |
| `recommending-model-tier` | Haiku / Sonnet / Opus selection per task | 14 | 📝 planned |

### Scaffolding

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `scaffolding-ml-research-notebook` | uv/poetry + src/ + data/raw immutable + tests/ + claudedocs/ + seed util + pre-commit | 15 | 📝 planned |
| `scaffolding-grad-school-pset` | Jupyter/RMarkdown template with stats discipline baked in | 12 | 📝 planned |
| `scaffolding-llm-eval-harness` | model_id + dataset_hash + prompt_version + judge_model + results.jsonl | 14 | 📝 planned |

## Cross-track references

- For seed hygiene, train/test split discipline, and reproducibility, see `workflow/`.
- For research discipline (premortems, pre-registration), see `workflow/`.
- For teaching variations of these skills (rubrics, walkthroughs), see `teaching/` (planned).
