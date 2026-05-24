# Rock's Claude Skills (RCS)

Production-quality Claude Code skills for AI security researchers, data scientists, and ML engineers. Every skill encodes a discipline that would otherwise be rebuilt from scratch each project — statistical-test selection, leakage firewalls, seed hygiene, MCP pre-trust audits, adversarial premortems. Catalog-free by design: no bundled framework controls, no ISO mirrors, no drift to maintain. Methodology only.

## Audience routing

- **Security engineer or AI red-teamer?** Start with `skills/security/`.
- **Data scientist, ML engineer, or stats student?** Start with `skills/ml-datasci/`.
- **Researcher working across both?** Start with `skills/workflow/` (cross-cutting hygiene).
- **Instructor or TA?** Start with `skills/teaching/` (pedagogy patterns).
- **Claude Code skill author?** Start with `skills/claude-code-meta/`.

## Install

### Claude Code

Clone and symlink each skill you want into `~/.claude/skills/`:

```bash
git clone https://github.com/rocklambros/rcs.git
cd rcs
for skill in skills/*/*/; do
  name=$(basename "$skill")
  ln -s "$(pwd)/$skill" "$HOME/.claude/skills/$name"
done
```

### Copilot CLI, Gemini CLI, Anthropic API

The `skills/<track>/<name>/SKILL.md` files follow the Anthropic Skills format and work in any host that supports the spec. Symlink or copy the directories into your tool's skill discovery path. For the Anthropic API, upload via the SDK per the Skills guide.

## Skill catalog

| Skill | Track | What it does | Status | Σ |
|---|---|---|---|---|
| [`enforcing-seed-hygiene`](skills/workflow/enforcing-seed-hygiene/) | workflow | First-cell seed gate (Python/NumPy/PyTorch/JAX/TF/R) + CPU-pin for cross-platform sampler determinism + pre-commit hook | ✅ shipped | 20 |
| [`validating-temporal-fields`](skills/workflow/validating-temporal-fields/) | workflow | Reject-future + min-year-fallback + event-vs-disclosure separation for temporal corpora | ✅ shipped | 19 |
| [`auditing-pinned-dependencies`](skills/security/auditing-pinned-dependencies/) | security | Grep audit for unpinned installs across README / Dockerfile / CI / package.json / mcp.json | ✅ shipped | 19 |
| [`reporting-effect-sizes`](skills/ml-datasci/reporting-effect-sizes/) | ml-datasci | Per-test-family effect-size selector + 95% CI + direction sentence; refuses bare-p-value | ✅ shipped | 19 |
| [`evaluating-binary-classifiers`](skills/ml-datasci/evaluating-binary-classifiers/) | ml-datasci | ROC + PR + calibration + CM + threshold sweep + bootstrap 95% CI from `(y_true, y_pred_proba)` | ✅ shipped | 19 |
| [`auditing-mcp-server-pre-trust`](skills/security/auditing-mcp-server-pre-trust/) | security | Six-check audit before registering an MCP server | ✅ shipped | 18 |
| [`selecting-statistical-test`](skills/ml-datasci/selecting-statistical-test/) | ml-datasci | Decision-tree walk from data characteristics to a recommended test, naming the gating assumption | ✅ shipped | 18 |
| [`checking-test-assumptions`](skills/ml-datasci/checking-test-assumptions/) | ml-datasci | Per-test assumption checks (Shapiro / Levene / QQ / residual) with pass/fail verdicts | ✅ shipped | 18 |
| [`auditing-train-test-split`](skills/ml-datasci/auditing-train-test-split/) | ml-datasci | Leakage / stratification / group-aware / temporal-order audit of a train/test split | ✅ shipped | 18 |
| [`deduplicating-records`](skills/workflow/deduplicating-records/) | workflow | Multi-key dedup with index-refresh, union-find transitive collapse, and ID-format normalization | ✅ shipped | 18 |
| [`authoring-skill`](skills/claude-code-meta/authoring-skill/) | claude-code-meta | Anthropic best-practices + RCS Layer-3 contract for authoring a new skill | ✅ shipped | 18 |
| [`auditing-instruction-hierarchy`](skills/claude-code-meta/auditing-instruction-hierarchy/) | claude-code-meta | Audits the agent-instruction file hierarchy for size budget, cache hygiene, and drift | ✅ shipped | 18 |
| [`running-adversarial-premortem`](skills/workflow/running-adversarial-premortem/) | workflow | Multi-round adversarial premortem on spec / plan / paper / proof / codebase | ✅ shipped | 17 |
| [`pinning-reproducible-environments`](skills/workflow/pinning-reproducible-environments/) | workflow | Per-ecosystem lockfile pattern + runtime-version pinning + base-image digest pinning + CI drift-check | ✅ shipped | 17 |
| [`auditing-data-quality`](skills/workflow/auditing-data-quality/) | workflow | Per-column null / range / type / cardinality audit + semantic-class detection + row-level integrity | ✅ shipped | 17 |
| [`building-baseline-models`](skills/ml-datasci/building-baseline-models/) | ml-datasci | 3-rung baseline ladder (Dummy / Linear / RandomForest) on the same train/test split + same metric as the final model | ✅ shipped | 17 |
| [`evaluating-regression-models`](skills/ml-datasci/evaluating-regression-models/) | ml-datasci | RMSE + MAE + R² + adjusted-R² + residual plots + k-fold CV; refuses R² alone | ✅ shipped | 17 |
| [`auditing-context-window-pressure`](skills/workflow/auditing-context-window-pressure/) | workflow | Multi-turn session pressure audit: context %, cache-hit-rate, instruction-hierarchy size, tool-result bloat (mandatory file-offload + subagent-summary triage) | ✅ shipped | 17 |
| [`auditing-jupyter-execution-order`](skills/workflow/auditing-jupyter-execution-order/) | workflow | Static audit of `.ipynb` cell execution_count for out-of-order or unrun cells with downstream dependents | ✅ shipped | 16 |
| [`auditing-source-provenance`](skills/workflow/auditing-source-provenance/) | workflow | Audits ingest pipelines for per-record provenance + transform-survival + CI gating | ✅ shipped | 16 |
| [`pre-registering-eval-study`](skills/workflow/pre-registering-eval-study/) | workflow | Locks hypothesis, falsification, stopping rule, and power justification BEFORE data observation | ✅ shipped | 16 |
| [`auditing-prompt-token-budget`](skills/ml-datasci/auditing-prompt-token-budget/) | ml-datasci | Anthropic API prompt-budget audit with stable-vs-volatile classification + `cache_control` breakpoint with `"ttl": "1h"` + write-vs-read cost projection | ✅ shipped | 16 |
| [`evaluating-multiclass-classifiers`](skills/ml-datasci/evaluating-multiclass-classifiers/) | ml-datasci | Per-class P/R/F1 + macro/weighted/micro with cost-model justification + K x K confusion in counts and row-normalized + top-k + one-vs-rest ROC/PR + log loss + Cohen's kappa | ✅ shipped | 16 |
| [`tuning-classification-threshold`](skills/ml-datasci/tuning-classification-threshold/) | ml-datasci | Five-selector threshold selection (F-beta, TPR-at-fixed-FPR, precision-at-fixed-recall, cost-weighted, Youden's J) with val-pick / test-report separation and calibration check | ✅ shipped | 16 |
| [`running-chollet-ratio-check`](skills/ml-datasci/running-chollet-ratio-check/) | ml-datasci | Chollet samples-per-word ratio decision rule for text classification model-family selection (BoW vs RNN/CNN vs Transformer) | ✅ shipped | 16 |
| [`interpreting-conflicting-tests`](skills/ml-datasci/interpreting-conflicting-tests/) | ml-datasci | Adjudicates between disagreeing statistical tests via assumption-status table; refuses p-hacking via test-shopping | ✅ shipped | 16 |
| [`building-deterministic-data-pipelines`](skills/workflow/building-deterministic-data-pipelines/) | workflow | 8-step bit-identical pipeline checklist (canonicalization, LF endings, sorted output, stable floats, provenance.json, content-hash snapshot, CI drift check) | ✅ shipped | 15 |
| [`writing-successor-primers`](skills/workflow/writing-successor-primers/) | workflow | Cold-pickup handoff doc (founding principles, false-confidence warnings, glossary, what is NOT here) | ✅ shipped | 15 |
| [`writing-release-notes-as-postmortem`](skills/workflow/writing-release-notes-as-postmortem/) | workflow | Six-field per-fix postmortem entries with severity sort and "regressions NOT yet fixed" section | ✅ shipped | 15 |
| [`generating-data-dictionary`](skills/ml-datasci/generating-data-dictionary/) | ml-datasci | Per-column data dictionary (type, null %, unique count, range, semantic class, role, PII flag, anomaly notes) for a tabular dataset | ✅ shipped | 15 |
| [`analyzing-regression-diagnostics`](skills/ml-datasci/analyzing-regression-diagnostics/) | ml-datasci | Six-step diagnostic battery on a fitted OLS / GLS / GLM regression (linearity, Normality, homoscedasticity, autocorrelation, leverage, multicollinearity) | ✅ shipped | 14 |
| [`enforcing-leakage-firewall`](skills/ml-datasci/enforcing-leakage-firewall/) | ml-datasci | Four-check leakage defense (LOFO + hub-firewall + group-aware split + row-hash invariant) for multi-source / grouped data | ✅ shipped | 14 |
| [`comparing-models-fairly`](skills/ml-datasci/comparing-models-fairly/) | ml-datasci | Paired-test library for head-to-head model comparison (McNemar / DeLong / paired-t / Wilcoxon / Friedman + Nemenyi) with multiple-comparison correction | ✅ shipped | 14 |
| [`evaluating-rag-retrieval`](skills/ml-datasci/evaluating-rag-retrieval/) | ml-datasci | Staged RAG eval separating retrieval metrics (recall@k / MRR / nDCG) from generation metrics (faithfulness / answer relevance) plus failure-attribution 2x2 | ✅ shipped | 14 |
| [`profiling-llm-cost`](skills/ml-datasci/profiling-llm-cost/) | ml-datasci | Per-call → per-task → per-cohort LLM cost rollup with cache-hit-rate trend, attribution slices, baseline-window delta, and top-3 drivers | ✅ shipped | 14 |
| [`recommending-model-tier`](skills/ml-datasci/recommending-model-tier/) | ml-datasci | Per-task Haiku 4.5 / Sonnet 4.6 / Opus 4.7 routing with reasoning-depth × task-category baseline + safety / latency / cost / cache-lineage modifiers | ✅ shipped | 14 |
| [`auditing-notebook-narrative`](skills/workflow/auditing-notebook-narrative/) | workflow | Audits notebook markdown narrative against rendered code-cell outputs; flags directional / numeric mismatches between prose claims and figures | ✅ shipped | 13 |
| [`validating-schema-evolution`](skills/workflow/validating-schema-evolution/) | workflow | Diffs old vs new schemas, classifies each change as breaking / non-breaking / ambiguous, and scaffolds safe migrations | ✅ shipped | 13 |
| [`auditing-mathematical-claims`](skills/workflow/auditing-mathematical-claims/) | workflow | ATACE four-field per-claim audit (Location · Concern · Strongest-counter · Stops-mattering-if) on theorems / lemmas / bounds / definitions | ✅ shipped | 13 |
| [`running-power-analysis`](skills/ml-datasci/running-power-analysis/) | ml-datasci | Prospective power / n / MDE calculation for any planned test with required effect-size provenance; refuses post-hoc / observed power | ✅ shipped | 13 |
| [`writing-model-cards`](skills/ml-datasci/writing-model-cards/) | ml-datasci | Mitchell-2019 model card + AIBOM addendum (intended + out-of-scope use, subgroup-disaggregated metrics, data provenance, harms + mitigations, dependencies + hashes) | ✅ shipped | 13 |
| [`selecting-embedding-model`](skills/ml-datasci/selecting-embedding-model/) | ml-datasci | Three-axis embedding-model comparison (intrinsic + extrinsic + operational cost) with bootstrap-CI tie-detection; refuses leaderboard-only recommendations | ✅ shipped | 13 |
| [`triaging-vulnerability-findings`](skills/security/triaging-vulnerability-findings/) | security | SARIF triage pipeline (parse → dedupe across tools → reachability → EPSS → rank → suppress-with-rationale → PR comment); refuses silent suppression | ✅ shipped | 14 |
| [`auditing-transitive-vulnerabilities`](skills/security/auditing-transitive-vulnerabilities/) | security | SBOM/lockfile + Grype/Trivy/OSV scan → dep-path → EPSS → reachability (callgraph/import-only) → ranked remediation | ✅ shipped | 13 |
| [`threat-modeling-llm-app`](skills/security/threat-modeling-llm-app/) | security | STRIDE-style threat-modeling walk over LLM apps against a user-supplied catalog (OWASP LLM Top 10 / MITRE ATLAS / MAESTRO / custom); methodology only, no bundled catalogs | ✅ shipped | 13 |
| [`running-prompt-injection-eval`](skills/security/running-prompt-injection-eval/) | security | Generic single-turn injection harness consuming a user-supplied JSONL corpus; 7-step workflow + four-class outcome classification; refuses without RoE / corpus / authorization | ✅ shipped | 13 |
| [`packaging-model-for-deployment`](skills/ml-datasci/packaging-model-for-deployment/) | ml-datasci | Versioned artifact + input/output schema + manifest + smoke test (joblib / ONNX / TorchScript per stack); refuses to certify deploy-ready without a smoke test that round-trips through the saved artifact | ✅ shipped | 12 |
| [`scaffolding-pytorch-training-loop`](skills/ml-datasci/scaffolding-pytorch-training-loop/) | ml-datasci | Production PyTorch training-loop scaffold (seed + AMP + grad-clip + LR schedule + early stop + atomic-write full-state checkpoint + W&B resume) | ✅ shipped | 12 |
| [`running-hyperparameter-sweep`](skills/ml-datasci/running-hyperparameter-sweep/) | ml-datasci | Disciplined Optuna / Ray Tune sweep (search-space design, TPE + ASHA, sweep-vs-retrain budget split, seed-stratified top-K retrain, boundary alarms, single-shot test eval) | ✅ shipped | 12 |
| [`running-eval-before-after-finetune`](skills/ml-datasci/running-eval-before-after-finetune/) | ml-datasci | Paired before/after fine-tune evaluation with metric-family-driven test selection (McNemar / paired-t / Wilcoxon / Cochran's Q / Friedman); effect size + 95% CI + power-check | ✅ shipped | 12 |
| [`generating-sbom`](skills/security/generating-sbom/) | security | CycloneDX / SPDX SBOM from any stack via syft + per-ecosystem fallbacks; software components only (not AI-BOM) | ✅ shipped | 12 |
| [`scaffolding-red-team-engagement`](skills/security/scaffolding-red-team-engagement/) | security | Signed RoE + scope inventory + kill-switch protocol + tamper-evident logging + coordinated-disclosure template before any attack traffic flows; refuses solo personal jailbreak experiments | ✅ shipped | 12 |
| [`running-multiturn-attack-suite`](skills/security/running-multiturn-attack-suite/) | security | Multi-turn attack harness with per-script session isolation, per-turn state snapshots, per-turn + per-script outcome classes, cross-script pattern analysis; refuses single-turn-only targets | ✅ shipped | 12 |
| [`running-encoded-payload-suite`](skills/security/running-encoded-payload-suite/) | security | Encoded-payload filter-bypass audit (base64 / hex / ROT13 / URL / unicode-confusables / zero-width / RTL / leetspeak / language-switch / tokenizer-boundary) with mandatory filter-presence + plain-text baseline; refuses no-filter base models | ✅ shipped | 12 |
| [`monitoring-data-drift`](skills/ml-datasci/monitoring-data-drift/) | ml-datasci | Per-feature drift monitor (PSI / KS continuous, JS / chi-squared categorical); baseline-noise calibration + per-cohort attribution + root-cause hierarchy before retraining | ✅ shipped | 11 |
| [`monitoring-prediction-drift`](skills/ml-datasci/monitoring-prediction-drift/) | ml-datasci | Prediction-side drift monitor (calibration over time, score-distribution shift, per-segment AUC / F1 with bootstrap 95% CI on labeling-delay-aware windows); recommends Platt / isotonic recalibration before retraining | ✅ shipped | 11 |
| [`auditing-sft-dataset`](skills/ml-datasci/auditing-sft-dataset/) | ml-datasci | Pre-training audit of an SFT corpus (schema / chat-template / length / exact + MinHash dedup / n-gram leakage / PII / label-quality sample) with quarantine-not-silent-drop and eval-set protection | ✅ shipped | 11 |
| [`auditing-synthetic-data-utility`](skills/ml-datasci/auditing-synthetic-data-utility/) | ml-datasci | TSTR / TRTS / TRTR utility audit for tabular SDG output with bootstrap 95% CI on utility ratio + per-marginal KS / Wasserstein + pairwise-correlation Frobenius gap; refuses without a real held-out test set | ✅ shipped | 11 |
| [`building-data-dictionary-with-consent-class`](skills/ml-datasci/building-data-dictionary-with-consent-class/) | ml-datasci | Per-field dictionary with consent class (collected / inferred / derived / public / synthetic) + DSR scope per right per regime + Article-9 flagging + lineage cascade + orphan-field detection | ✅ shipped | 11 |
| [`threat-modeling-agentic-systems`](skills/security/threat-modeling-agentic-systems/) | security | Threat model walk for autonomous / multi-agent systems against a user-supplied catalog (MAESTRO / ATLAS / OWASP ASI); mandatory runaway-loop / blast-radius subsection; methodology only | ✅ shipped | 11 |
| [`building-rollback-plan`](skills/ml-datasci/building-rollback-plan/) | ml-datasci | Versioned artifact store + deterministic triggers + oncall as decision authority + named control-plane reversal + state reconciliation + smoke-test re-entry gate | ✅ shipped | 10 |
| [`auditing-inference-latency-budget`](skills/ml-datasci/auditing-inference-latency-budget/) | ml-datasci | Real-time inference latency audit vs stated SLO (P50 / P95 / P99 per-stage; slow-vs-fast tail attribution; input-shape regression; (ms saved at P99) / (eng hours) ranking) | ✅ shipped | 10 |
| [`writing-finetune-spec-sheet`](skills/ml-datasci/writing-finetune-spec-sheet/) | ml-datasci | 7-section fine-tune spec sheet (immutable revision SHA + data provenance + recipe + paired eval evidence + limitations + license reconciliation + intended/out-of-scope use) | ✅ shipped | 10 |
| [`auditing-synthetic-data-leakage`](skills/ml-datasci/auditing-synthetic-data-leakage/) | ml-datasci | Empirical privacy audit for tabular SDG output (shadow-model MIA with bootstrap CI + DCR / NNDR + near-duplicate + per-attribute disclosure); CI upper bound is the operative number on sensitive classes | ✅ shipped | 10 |
| [`building-canary-rollout`](skills/ml-datasci/building-canary-rollout/) | ml-datasci | Staged traffic split with pre-committed business + technical + per-cohort guardrail thresholds and a deterministic auto-rollback trigger wired before the first flip | ✅ shipped | 9 |

_65 shipped (+ 1 drafting) of ~99 planned skills. See each track's README for the planned-skills roadmap; see [`docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md`](docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md) for the v2–v7 roadmap._

## Governance

- **License:** MIT (see `LICENSE`)
- **Contributing:** See `CONTRIBUTING.md` — eval-first workflow, gerund naming, no AI attribution
- **Versioning:** SemVer per skill (`frontmatter.version`) + loose repo-level batch tags (`v1`, `v1.1`, ...)
- **Documentation contract:** See `docs/conventions.md`

## Acknowledgments

Skill design follows the [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) document and the patterns demonstrated by the official `anthropics/claude-code` skills, `obra/superpowers`, and `affaan-m/everything-claude-code` repos.

## Disclaimer

Skills are tooling, not advice. They encode disciplines and decision trees observed in real research and engineering practice. Verify outputs against authoritative sources before relying on them in regulated or safety-critical contexts.
