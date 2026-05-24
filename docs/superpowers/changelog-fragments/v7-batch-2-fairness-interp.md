### v7-batch-2: fairness + interpretability + overfit — 2026-05-23

Skills shipped:

- `ml-datasci/auditing-model-fairness` v0.1.0 — multi-metric fairness audit (equal-opportunity, equalized-odds, demographic-parity, calibration-within-group, four-fifths rule, intersectional) with explicit Kleinberg-Mullainathan-Raghavan impossibility-trade-off naming; refuses single-metric verdicts and low-power group drops (Σ 12, status: shipped)
- `ml-datasci/generating-shap-explanations` v0.1.0 — SHAP attribution workflow with explainer-per-model-class selection, stratified background sizing (≥ 5× n_features), per-instance waterfall + global summary + beeswarm, mandatory stability check across 3 background resamples; refuses SHAP on linear/logistic models (closed-form coefficients suffice) (Σ 11, status: shipped)
- `ml-datasci/auditing-deep-learning-overfit` v0.1.0 — 7-step diagnostic decision tree distinguishing classic overfit from plateau / shift / label-noise / underfit, with priority-ordered remediation (early stop → augment → dropout → weight decay → reduce capacity → more data); refuses the "add dropout" reflex without ruling out shift / label noise and refuses to apply to classical ML (Σ 12, status: shipped)
- `ml-datasci/evaluating-ood-detection` v0.1.0 — OOD evaluation with REQUIRED near-OOD set + optional far-OOD set, AUROC + AUPR-out + FPR-at-95-TPR reported per OOD set separately, bootstrap CIs, method-selection table (MSP / energy / Mahalanobis / KNN / ODIN); refuses far-OOD-only evaluation and refuses closed-world deployments (Σ 9, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each of the 12 scenarios (4 skills × 3 scenarios) dispatched to a fresh general-purpose subagent (model: sonnet) with the SKILL.md body inlined into the prompt and the scenario query as the user message; subagent responded as Claude would after loading the skill. Parent session judged each completion against the 3-rubric scenario card using intent-matched scoring (PRAGMATIC explicit policy: "judge each rubric item against intent, not literal phrasing"). Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run via `tools.run_evals`.

Eval results (rubric items passed / 3):

| Skill | happy-path | edge-case | anti-trigger |
|---|---|---|---|
| auditing-model-fairness | 3/3 | 3/3 | 3/3 |
| generating-shap-explanations | 3/3 | 3/3 | 3/3 |
| auditing-deep-learning-overfit | 3/3 | 3/3 | 3/3 |
| evaluating-ood-detection | 3/3 | 3/3 | 3/3 |

All 36/36 rubric items passed. All four skills clear PRAGMATIC Sonnet thresholds (happy 3/3, edge 3/3, anti ≥ 2/3) and ship as `status: shipped`.

Notes:

- Plan-file slug `evaluating-OOD-detection` was renamed to `evaluating-ood-detection` at lint time per `docs/conventions.md` (lowercase-kebab requirement). All eval JSONs, frontmatter `name`, and directory updated; cross-references in other v7-batch-2 skills' "See also" sections use the lowercase form.
- `auditing-model-fairness` bundles two `reference/` files: `metric-definitions.md` (formulas for all gap metrics + bootstrap procedure) and `impossibility-trade-offs.md` (KMR + Chouldechova summary).
- `generating-shap-explanations` bundles `explainer-decision-table.md` (model-class → explainer + mode choice for TreeExplainer interventional vs path_dependent) and `background-set-rules.md` (sizing, stratification, production vs training background).
- `auditing-deep-learning-overfit` bundles `diagnostic-decision-tree.md` (full Q1-Q5 tree) and `regularization-priority.md` (8-step priority list with cost / signal / sample-complexity rules of thumb).
- `evaluating-ood-detection` bundles `method-selection-table.md` (method × backbone-change × cost × near/far strength) and `near-vs-far-ood.md` (per-domain worked examples; curation guidance).
- All four skills are on the ml-datasci / AI-safety boundary; track placement (ml-datasci) chosen because the workflow is anchored on a trained model and an eval method, not on an authorized engagement scope.
