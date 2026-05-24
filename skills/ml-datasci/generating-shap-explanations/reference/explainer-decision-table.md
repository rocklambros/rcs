# SHAP explainer decision table

| Model class | Recommended explainer | Why |
|---|---|---|
| XGBoost, LightGBM, CatBoost | `shap.TreeExplainer` | Exact attribution via tree path; fast |
| sklearn RandomForestClassifier / Regressor | `shap.TreeExplainer` | Same; supported natively |
| sklearn GradientBoostingClassifier / Regressor | `shap.TreeExplainer` | Same |
| PyTorch / TensorFlow / Keras dense network | `shap.DeepExplainer` | Gradient-based; requires background tensor |
| PyTorch / TensorFlow CNN / RNN | `shap.GradientExplainer` | Handles non-trivial topology; slower than DeepExplainer |
| Arbitrary black-box callable (sklearn pipeline, ensemble of mixed types) | `shap.KernelExplainer` | Model-agnostic; O(n_background × n_features); SLOW |
| Linear / logistic regression | DO NOT USE SHAP | Coefficients × (x − background_mean) IS the SHAP value in closed form |
| Single decision tree (≤ 5 features) | DO NOT USE SHAP | Direct tree inspection is more honest |
| LLM / transformer | `shap.PartitionExplainer` or specialized libraries | SHAP for text has caveats; consider attention-based or perturbation-based alternatives |

## Mode choice for TreeExplainer

- **`feature_perturbation='interventional'`** — uses the supplied background to define E[f(X) | features in S]. More principled (Shapley values in causal sense), but slower. Requires non-trivial background size.
- **`feature_perturbation='tree_path_dependent'`** — uses the structure of the tree to define conditional expectations. Fast, ignores supplied background. Implicit background is the training distribution.

Use interventional for fairness / regulatory contexts where the background must be documented. Use path-dependent for speed in exploratory analysis.

## Background size guidance

| Use case | Recommended background size |
|---|---|
| Exploratory / debugging | 100 |
| Per-instance explanation for a stakeholder report | 500 |
| Regulatory / audit-grade | 1000+ (with stratification documented) |
| Production explanation API (per-request) | precompute on a fixed reference set, do NOT resample per request |
