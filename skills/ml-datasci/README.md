# ML / Data Science Track

For data scientists, ML engineers, applied-ML practitioners, and stats students.

This track encodes disciplines that recur across model-building work: statistical-test selection from data characteristics, classifier and regression evaluation, calibration, leakage firewalls, baseline-model discipline, regression diagnostics, fine-tuning audits, and RAG retrieval evaluation.

## Shipped skills

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`reporting-effect-sizes`](reporting-effect-sizes/) | Selects the appropriate effect-size metric per test family (Cohen's d / dz, Cliff's δ, rank-biserial, OR, partial η², adj-R²) + 95% CI + direction sentence; refuses bare-p-value reports | When reporting any hypothesis-test result, writing stats homework / papers / dashboards, or seeing 'p < 0.05 so significant' without an effect size | 19 |
| [`evaluating-binary-classifiers`](evaluating-binary-classifiers/) | ROC + PR + calibration + CM + threshold sweep + bootstrap 95% CI from `(y_true, y_pred_proba)`; refuses bare accuracy on imbalanced data; refuses default 0.5 threshold | A trained binary classifier needs scoring; class imbalance suspected; only accuracy reported on imbalanced data; threshold selection needed | 19 |
| [`selecting-statistical-test`](selecting-statistical-test/) | Decision-tree walk from data characteristics (sample count, paired/independent, scale, distributional assumptions) to recommended test, naming the gating assumption check | User has a hypothesis + data and needs to commit to a test before running it | 18 |
| [`checking-test-assumptions`](checking-test-assumptions/) | Per-test assumption checks (Shapiro / Levene / QQ / residual diagnostics) with pass/fail verdicts and consequences | Before running any parametric test, after running one to validate, or when asked 'are the assumptions met?' | 18 |
| [`auditing-train-test-split`](auditing-train-test-split/) | Leakage / stratification / group-aware / temporal-order audit of a train/test split | User creates a split; accuracy looks suspiciously high; same ID in train+test; time-series random-split; or group-aware data is row-split | 18 |
| [`building-baseline-models`](building-baseline-models/) | 3-rung baseline ladder (Dummy / Linear / RandomForest) fit on the SAME train/test split and SAME metric as the final model; refuses to certify a complex-model metric without baseline comparison | About to fit gradient boosting / deep learning / any complex model; a metric is reported without comparison context; "is `<metric>` good?" without a baseline | 17 |
| [`evaluating-regression-models`](evaluating-regression-models/) | RMSE + MAE + R² + adjusted-R² + residual plots (residuals-vs-fitted, QQ, histogram) + k-fold CV (`mean ± SD`) + Cook's D; refuses R² alone; recommends walk-forward CV for time-series | A regression model needs scoring; only R² is reported without RMSE/MAE; residual diagnostics needed; CV missing | 17 |
| [`auditing-prompt-token-budget`](auditing-prompt-token-budget/) | Tokenizes an Anthropic API request (system + tools + tool_results + every turn), classifies blocks into stable-prefix vs volatile-suffix, recommends `cache_control` breakpoint placement at the end of the stable region with explicit `"ttl": "1h"`, projects write-vs-read cost vs no-cache cost, and prescribes cache-hit-rate telemetry; refuses to engage on prompts under ~500 tokens | Per-call cost is climbing, latency on first turns is too high, request is approaching the 200k window, shipping a new agentic / RAG / multi-turn workflow, or the user asks where to put cache_control | 16 |
| [`evaluating-multiclass-classifiers`](evaluating-multiclass-classifiers/) | Full multi-class classifier report: per-class precision / recall / F1 with support, macro + weighted + micro aggregations with cost-model justification, K x K confusion matrix in counts and row-normalized views, top-k accuracy where informative, one-vs-rest ROC and PR per class, multi-class log loss / Brier / Cohen's kappa, bootstrap 95% CI on macro-F1 and rare-class F1; refuses bare overall accuracy under imbalance and hands off to evaluating-binary-classifiers on 2-class tasks | A trained classifier has 3 or more labels and needs to be scored; overall accuracy is reported on a 3+-class task with imbalance; or the user is unsure whether macro / weighted / micro aggregation matches the deployment cost model | 16 |
| [`tuning-classification-threshold`](tuning-classification-threshold/) | Domain-aware threshold selection with five selectors (F-beta, TPR-at-fixed-FPR, precision-at-fixed-recall, cost-weighted, Youden's J), enforced validation-slice tuning + held-out-test reporting separation, mandatory calibration check before applying any probability threshold; refuses default 0.5 and refuses to pick threshold on the test set | A trained binary classifier is moving to deployment; a metric is reported at threshold 0.5 without justification; a hard FPR / precision / recall budget exists; or there is FN-vs-FP cost asymmetry (fraud, security, medical screening) | 16 |
| [`running-chollet-ratio-check`](running-chollet-ratio-check/) | Chollet samples-per-word ratio decision rule for text / sequence classification model-family selection: ratio < 1500 favors TF-IDF + linear (BoW); 1500-15000 is a transition zone for small RNN / 1D-CNN; > 15000 supports Transformer / pretrained fine-tune; includes domain-pretraining threshold adjustment and per-class minimum sanity check; always requires a BoW baseline comparison; refuses to recommend a Transformer below the threshold without domain-pretraining justification and refuses to apply the ratio to non-sequence data | A user is starting a text classification project, picking between TF-IDF baseline and a deep model, or about to fine-tune a Transformer on a small labeled dataset where the ratio test predicts the deep model will overfit | 16 |
| [`interpreting-conflicting-tests`](interpreting-conflicting-tests/) | Adjudicates between two statistical tests on the same data that disagree (paired-t vs Wilcoxon, two-sample-t vs Mann-Whitney, McNemar vs exact binomial sign, chi-squared vs Fisher) by building an assumption-status table, picking the test whose assumptions hold (NOT the smaller p-value), and committing to one primary with the matched effect-size + 95% CI; refuses 'mixed evidence' hand-waving and p-hacking via test-shopping | Two tests on the same data disagree, user asks which p-value to report, reviewer flagged conflicting results in a manuscript, or user wants to keep running tests until one is significant | 16 |
| [`generating-data-dictionary`](generating-data-dictionary/) | Generates a per-column data dictionary (type, null %, unique count, range, semantic class, role, PII flag, anomaly notes) for a tabular dataset | When receiving a fresh client / partner / vendor dataset, before fitting any model on an undocumented dataset, or as the first step before broader data-quality auditing | 15 |
| [`analyzing-regression-diagnostics`](analyzing-regression-diagnostics/) | Six-step diagnostic battery on a fitted OLS / GLS / GLM regression (linearity, residual Normality, homoscedasticity, autocorrelation, leverage + Cook's D, multicollinearity / VIF) with per-diagnostic verdict + remediation; refuses to run on tree / kernel / neural models | A linear or GLM regression has been fit and inference (coefficients, p-values, CIs) is about to be reported; surprising results need investigation; or 'are my regression diagnostics OK?' | 14 |
| [`enforcing-leakage-firewall`](enforcing-leakage-firewall/) | Four-check leakage defense for supervised pipelines: LOFO sweep (target-encoded / post-event features), hub-firewall for crosswalk / multi-source data, group-aware splitting for multi-row-per-entity data, no-row-in-two-splits row-hash invariant; refuses to trust a held-out metric until all four checks pass on the relevant subset | A dataset is assembled from multiple sources (crosswalk, registry merge); has natural group structure (patient_id, user_id, customer_id); the held-out metric looks suspiciously high; or after any join / merge step that could create cross-split row identity | 14 |
| [`comparing-models-fairly`](comparing-models-fairly/) | Paired statistical tests for head-to-head model comparison: McNemar / DeLong for two classifiers on the same test set, paired-t or Wilcoxon signed-rank for k-fold CV, Friedman + Nemenyi or Holm-Bonferroni correction for 3+ models; requires effect-size + bootstrap CI alongside p-value and distinguishes statistical from operational significance; refuses unpaired tests on per-fold metrics and refuses to skip multiple-comparison correction | Two or more candidate models need a deployment winner; two metrics differ but their CIs overlap; the user reports a 'better' model without a paired test; or 3+ models are being compared without a correction plan | 14 |
| [`evaluating-rag-retrieval`](evaluating-rag-retrieval/) | Staged RAG eval from a golden Q-A set — retrieval metrics (recall@k, MRR, nDCG@k) separated from generation metrics (faithfulness, answer relevance, context utilization scored on retrieval hits) plus a retrieval-vs-generation failure-attribution 2x2 driving the next experiment; refuses single aggregate scores that conflate stages | A RAG pipeline needs scoring, the user reports "RAG feels worse than direct LLM" but cannot localize the stage, a chunking / embedding / reranker / top-k change needs A/B comparison, or the generation looks wrong but retrieval looks fine | 14 |
| [`profiling-llm-cost`](profiling-llm-cost/) | Per-call → per-task → per-cohort LLM cost rollup from a logged trace (input / cached_input / output tokens × pricing snapshot), cache-hit-rate trend, attribution slices by model / step / route / cohort, baseline-window delta, top-3 cost drivers, and recommendations ranked by $ saved per engineering hour; refuses cost-cutting actions without a measured baseline | A production LLM bill spikes without proportional traffic growth, prompt-cache hit rate drops, an agentic system's $-per-task is unknown, or a budget gate is needed before scaling | 14 |
| [`recommending-model-tier`](recommending-model-tier/) | Decomposes a pipeline into discrete LLM calls and recommends Haiku 4.5 / Sonnet 4.6 / Opus 4.7 per task based on reasoning depth, latency budget, cost target, safety-critical status, and same-family-cache lineage; pairs every downgrade with an escalation rule and an eval; refuses to engage on policy-locked single-tier deployments | Designing a new LLM pipeline, single-tier deployment is too slow / expensive, choosing tier for a specific task, responding to a benchmark that disagrees with production, or shipping a multi-stage agent | 14 |
| [`running-power-analysis`](running-power-analysis/) | Prospective (a-priori) power / n / MDE calculation for any planned test (t / ANOVA / chi-squared / correlation / regression / logistic) with required effect-size provenance (pilot / literature / SESOI / Cohen rule-of-thumb) and sensitivity check; refuses post-hoc / observed power and routes to TOST or CI interpretation | Designing a study, writing a grant / pre-registration / IRB, choosing between designs, or being asked 'what was the power?' on a non-significant result | 13 |
| [`writing-model-cards`](writing-model-cards/) | Mitchell-2019 model card with AIBOM addendum: intended use + out-of-scope use, factors / subgroups, metrics with 95% CIs disaggregated by subgroup, evaluation + training data provenance with collection-window + license + known biases, concrete deployment-specific harms with paired mitigations, dependencies + versions + hashes for AI supply-chain traceability; refuses vague 'may have biases' language and refuses to author a card for a throwaway research notebook | A model is moving to production deployment; an EU AI Act / NIST AI RMF / ISO 23894 compliance review requests documentation; an open-weights release; or a customer / regulator / auditor requests a model card | 13 |
| [`selecting-embedding-model`](selecting-embedding-model/) | Three-axis embedding-model comparison (intrinsic similarity correlation on domain pairs + extrinsic retrieval recall@k / MRR / nDCG on a golden Q-A set + operational cost including per-query, index-build amortization, latency, and dim-driven index size) with bootstrap-CI tie-detection and operational tiebreaker; refuses recommendations from public leaderboards alone | Starting a new RAG / semantic-search / dedupe pipeline, considering swapping the embedding model, deciding between two candidates that "feel similar" on MTEB, or trading off a high-tier paid model against a self-hosted alternative | 13 |

## Planned skills

### Statistical / mathematical reasoning

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `running-bayesian-workflow` | Priors → posterior-predictive → R-hat/ESS → divergence check | 10 | 📝 planned |
| `building-conformal-prediction-set` | Split-conformal calibration, coverage check | 11 | 📝 planned |
| `analyzing-causal-DAG` | Confounder checklist, do-calculus walk | 9 | 📝 planned |

### ML / DL hygiene

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-deep-learning-overfit` | Train/val gap, learning curves, weight-norm growth | 12 | 📝 planned |
| `generating-shap-explanations` | SHAP / LIME / IG / permutation-importance scaffolding | 11 | 📝 planned |
| `auditing-model-fairness` | Eq-opp / dem-parity / calibration-within-group + intersectional | 12 | 📝 planned |

### RAG / fine-tuning / MLOps

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `auditing-chunking-strategy` | Chunk-size + overlap + boundary-aware splits | 13 | 📝 planned |
| `auditing-embedding-drift` | KL/cosine drift between embedding distributions over time | 11 | 📝 planned |
| `building-rag-eval-set` | Golden Q/A + held-out + adversarial set | 12 | 📝 planned |
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
