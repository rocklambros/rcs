# Background set rules

The SHAP background is the implicit "default" against which feature contributions are measured. Choosing it badly invalidates the attributions.

## Rule 1: Stratify by outcome

For classification, sample the background stratified by `y` so that the base value (E[f(X)] over background) reflects the class balance you care about. For regression, sample uniformly across the target range; for very-skewed targets, use quantile stratification.

## Rule 2: Size proportional to feature dimensionality

A 30-feature model needs more background than a 5-feature model. Rough rule: background size ≥ 5 × n_features for stable per-instance attributions, ≥ 10 × n_features for stable global rankings.

## Rule 3: Do NOT use the full training set

Tempting and easy, but for KernelExplainer this is O(n_background × n_features) per instance and will hang. Use a stratified subsample.

## Rule 4: Document the source

Every SHAP report includes: background size, stratification scheme, random seed, source dataset (train? validation? a separate "reference" set?). Without this, the attributions are not reproducible.

## Rule 5: Production background ≠ training background

If a model is deployed and a production explanation API recomputes SHAP per request, the background MUST be a fixed reference set committed alongside the model artifact. Recomputing from rolling production data drifts the attributions silently.

## Rule 6: Stability check is mandatory for stakeholder-facing reports

Resample the background 3 times with different seeds; recompute SHAP; compare top-5 feature rank order. If rank changes, the attribution is background-sensitive and the report must say so (or you must enlarge the background).

## What "interventional" vs "tree_path_dependent" mode actually means

In `interventional` mode, SHAP marginalizes feature j by replacing its value with samples from the background distribution — this estimates the causal-style Shapley value E[f(X) | X_S = x_S]. The supplied background is used.

In `tree_path_dependent` mode, SHAP uses the tree structure to compute conditional expectations along tree paths. The supplied background is ignored; the implicit "background" is the training distribution as encoded in the tree weights.

For audit / regulatory use, prefer `interventional` so the background is explicit and documented. For fast exploratory analysis, `tree_path_dependent` is fine. NEVER mix the two in a single report without naming which was used.
