---
name: generating-shap-explanations
description: >
  Generates SHAP (SHapley Additive exPlanations) feature attributions for a trained
  tree, kernel, or deep model with a deliberately-chosen background dataset, reports
  attribution stability across background-set perturbations, and outputs a
  global-importance summary plus per-instance waterfall plots. Use when a stakeholder
  asks "why did the model predict this?", when interpretability is required for
  regulatory compliance (EU AI Act, FCRA adverse action), when the user has a
  tree-ensemble or deep model and needs feature attribution, or when debugging a
  surprising prediction. Refuses to use SHAP on linear models (closed-form coefficients
  already give the attribution) and warns when the background set is too small or
  poorly chosen.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, ai-security]
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - llm-toxicity-visual-analysis
last-updated: 2026-05-23
---

# Generating SHAP Explanations

## When to use

Trigger this skill when:

- A stakeholder asks "why did the model predict this for this case?" — per-instance explanation
- A stakeholder asks "what features matter most globally?" — global feature importance
- Regulatory or compliance context requires explanations (EU AI Act high-risk, FCRA adverse-action notices, GDPR Article 22)
- The user is debugging a surprising prediction and wants attribution
- The model is a tree ensemble (XGBoost, LightGBM, RandomForest), a kernel model, or a deep network where post-hoc attribution is needed

## When NOT to use

Skip and hand off when:

- The model is a linear regression / logistic regression — the coefficients ARE the attribution (×_feature_value); SHAP adds nothing except computational cost and obscures the closed form
- The user wants a causal explanation ("would the outcome change if I changed X?") — SHAP gives statistical attribution, not counterfactuals; hand off to `analyzing-causal-DAG` or counterfactual-explanation tools
- The user wants model debugging via input-perturbation sanity checks — use a simpler permutation-importance approach
- The user expects SHAP values to be the "true" feature effect — they are NOT; they are model-specific attributions that depend on the background set
- The model is so simple (one decision tree, ≤ 5 features) that direct inspection of splits is more honest

## Quick start

User says: "I have an XGBoost classifier predicting diabetes. Why did it predict positive for patient 42? Also, what are the most important features overall?"

Skill response: chooses TreeExplainer (XGBoost is tree-based), constructs a background dataset stratified by the outcome (typically 100-1000 representative samples, NOT the full train set), computes SHAP values for patient 42 + a global sample, produces a waterfall plot for patient 42, a bar-plot of mean(|SHAP|) for global importance, and a summary beeswarm. Reports background-set choice + size + stratification explicitly. Runs a stability check (recomputes attributions across 3 different background subsamples; warns if rank order of top features changes).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| model | trained model object | yes | — | sklearn / xgboost / lightgbm / torch / tf model |
| explainer_kind | "tree" \| "kernel" \| "deep" \| "linear" | yes | inferred | Tree for tree ensembles, kernel for model-agnostic, deep for neural nets. Linear is rejected with a hand-off. |
| X_explain | array, shape (n_explain, n_features) | yes | — | Instances to explain. |
| X_background | array | yes | — | Background dataset. Should be a stratified sample of the training distribution, typically 100-1000 rows. Smaller = noisier; full train = too slow. |
| feature_names | list[str] | no | None | For plot labels. |
| stability_check | bool | no | true | If true, recompute SHAP across 3 background subsamples and report top-feature rank stability. |

## Workflow

```
SHAP explanation progress:
- [ ] Step 1: Pick explainer matching model class (tree / kernel / deep); refuse for linear with hand-off
- [ ] Step 2: Construct background dataset — stratified, sized appropriately, NOT the full train set
- [ ] Step 3: Compute SHAP values for X_explain
- [ ] Step 4: Per-instance waterfall plots for the cases the user asked about
- [ ] Step 5: Global mean(|SHAP|) bar chart + beeswarm summary
- [ ] Step 6: Stability check across 3 background subsamples (skip only if user opts out)
- [ ] Step 7: Report — attribution table + plots + background-set documentation + stability verdict
```

### Step 1: Pick the explainer

- Tree ensembles (XGBoost, LightGBM, RandomForest, CatBoost, sklearn GradientBoosting) → `shap.TreeExplainer` (exact, fast)
- Deep networks (PyTorch / TF / Keras) → `shap.DeepExplainer` or `shap.GradientExplainer` (gradient-based, requires background)
- Black-box / scikit-learn pipelines / arbitrary callables → `shap.KernelExplainer` (model-agnostic, slow)
- Linear models → REJECT. Coefficient × feature_value already gives the SHAP value in closed form; the user should read the coefficients directly. Hand off.

### Step 2: Construct the background

- The background represents "the absence of information about a feature"; SHAP imputes by sampling the background
- Stratify by the outcome variable to avoid baseline drift (e.g., 50/50 positive/negative for binary classification)
- Size: 100-1000 typically; smaller = noisier attributions, larger = more compute. Document the choice.
- DO NOT use the full training set as background by default — KernelExplainer is O(n_background × n_features), gets slow fast
- For TreeExplainer in "interventional" mode, the background defines the conditional expectation; in "tree_path_dependent" mode, the background is unused but the underlying assumption is the training distribution

### Step 3: Compute SHAP

- `explainer.shap_values(X_explain)` returns one attribution per (instance, feature). For multi-class, returns one matrix per class.
- For tree models, prefer `explainer(X_explain)` (returns `shap.Explanation` object with base value, values, data) over the older API

### Step 4: Per-instance waterfall

- `shap.plots.waterfall(shap_values[i])` for each instance i the user asked about
- Show the base value (expected model output over the background), then each feature's contribution adding/subtracting to reach f(x)

### Step 5: Global importance

- `shap.plots.bar(shap_values)` — mean(|SHAP|) per feature, ranked
- `shap.plots.beeswarm(shap_values)` — per-feature distribution of attributions across instances
- Do NOT rank features by raw mean(SHAP) — sign cancels out; use mean of absolute values

### Step 6: Stability check

- Resample the background 3 times (different random seeds)
- Recompute SHAP for the X_explain set
- Compare the rank order of the top 5 features across the 3 runs
- If rank order changes, the attributions are background-sensitive; warn loudly, recommend larger / more stratified background

### Step 7: Report

Include:

1. Background-set summary (size, stratification, source)
2. Stability verdict (top features stable / unstable across resamples)
3. Per-instance waterfall plot(s) the user asked about
4. Global importance bar plot
5. Beeswarm summary
6. Explicit limitations statement (see Failure modes)

## Outputs

- Markdown report linking to (or embedding) the plots
- A SHAP values matrix (`shap_values.values` for tree, `shap_values` array for kernel/deep) saved to disk
- A `shap_metadata.json` documenting model, explainer kind, background size + seed, n_explain, library version

## Failure modes

- **Background-set thinness** — using only 10-20 rows as background; attributions are noisy and per-run unstable. Caught by: Step 2 minimum + Step 6 stability check.
- **Full-training-set background** — using full train as background on a KernelExplainer; computation hangs. Caught by: Step 2 explicit sizing guidance.
- **Linear-model SHAP** — running SHAP on a linear/logistic model and reporting attributions. The skill rejects this case (Step 1) and points to coefficients.
- **Causal misinterpretation** — stakeholder reads SHAP as "if we changed X, the prediction would change by SHAP(X)". This is FALSE in general (especially for correlated features). Caught by: Step 7 limitations statement.
- **Sign-cancellation in global ranking** — ranking by mean(SHAP) instead of mean(|SHAP|). Caught by: Step 5 mandates mean of absolute values.
- **Multi-class confusion** — for multi-class models, SHAP returns one array per class; reporting only one class's attribution and calling it "the explanation" misleads. Each class needs its own report (or pick the predicted class explicitly).
- **Background distribution drift** — using a production-time background that no longer matches training-time distribution; attributions silently shift. Document the background source.

## References

- `reference/explainer-decision-table.md` — which explainer for which model class
- `reference/background-set-rules.md` — sizing, stratification, and "interventional vs path-dependent" choice
- [SHAP library documentation](https://shap.readthedocs.io/)
- [Lundberg & Lee 2017 — A Unified Approach to Interpreting Model Predictions (NeurIPS)](https://arxiv.org/abs/1705.07874)

## Examples

### Example 1: XGBoost diabetes classifier, per-instance + global (happy-path)

Input: XGBoost binary classifier; user wants explanation for patient 42 + global feature importance.

Output: TreeExplainer chosen. Background = 500-row stratified sample from train. Patient 42 waterfall shows glucose_fasting +0.18, BMI +0.09, age +0.04, family_history +0.03 pushing prediction from base 0.12 to 0.46. Global bar: glucose_fasting, BMI, age, glucose_2hr, family_history are top 5. Beeswarm shows glucose_fasting has strong positive attribution above ~120 mg/dL. Stability check: top 5 stable across 3 background resamples (rank ties at positions 4/5 between glucose_2hr and family_history; flagged but not material). Report includes "SHAP is attribution, not counterfactual" limitation note.

### Example 2: 50-row background warning (edge-case)

Input: User passes a 50-row background for a 30-feature deep network with DeepExplainer.

Output: Skill flags the background as undersized for the feature dimensionality. Computes SHAP anyway but runs the stability check first; reports that rank order of top-5 features changes between resamples (e.g., feature_7 appears at position 2 in one resample, position 5 in another). Recommends increasing background to ≥ 200 stratified rows before publishing the attribution.

### Example 3: Logistic regression (anti-trigger)

Input: "Run SHAP on my logistic regression for credit scoring."

Output: Skill rejects with explanation: for logistic regression, the per-instance attribution is the coefficient × (feature_value − background_mean), available in closed form from `model.coef_` and a chosen background. Running KernelExplainer would just approximate this with sampling noise. Hands the user the closed-form expression and the recommended background-mean choice (test-set mean, training-set mean, or zero depending on the regularization).

## See also

- `ml-datasci/auditing-model-fairness` — uses SHAP to check whether protected-attribute proxies dominate attributions
- `ml-datasci/analyzing-causal-DAG` — for causal "what if" questions SHAP cannot answer
- `ml-datasci/evaluating-binary-classifiers` — performance first, attribution second
- `ml-datasci/enforcing-leakage-firewall` — high-importance feature that perfectly tracks the label is often a leak

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
