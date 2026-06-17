---
name: comparing-models-fairly
description: >
  Picks the right paired statistical test to compare two or more models head-to-
  head on the same test data, instead of eyeballing two unpaired metrics. For
  two classifiers on the SAME held-out test set: McNemar on the disagreement
  table (or DeLong for threshold-free ROC-AUC). For k-fold CV comparisons:
  paired t-test if per-fold diffs are roughly Normal, otherwise Wilcoxon signed-
  rank (Demsar 2006). For 3+ models: multiple-comparison correction (Bonferroni,
  Holm-Bonferroni, or Friedman + Nemenyi). Triggers when comparing candidate
  models, picking a deployment winner, when two metrics differ but their CIs
  overlap, or when the user reports a winner without a paired test. Refuses
  unpaired t-tests on per-fold metrics and refuses to skip correction with 3+
  models.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - stats-student
evidence:
  - DU-MSDSAI-4432-MultiModelDiseaseProg
  - DU-MSDSAI-4432-MultiModelBikeShareRegression
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Comparing Models Fairly

## When to use

Trigger this skill when:

- Two or more candidate models need to be compared head-to-head to pick a deployment winner
- The user reports two model metrics (Model A AUC = 0.83, Model B AUC = 0.85) without a paired test
- Two confidence intervals overlap and the user is unsure whether the difference is real
- A model-selection plan involves running 3+ candidates and there is no plan for multiple-comparison correction
- The user mentions cross-validation comparison, paired t-test, Wilcoxon signed-rank, McNemar, Friedman, Nemenyi, Bonferroni, Holm
- Keywords: model comparison, A vs B, beat the baseline, statistically significant difference, paired test

## When NOT to use

Skip this skill and hand off when:

- Only one model is being reported (not comparing) → use `ml-datasci/evaluating-binary-classifiers` / `evaluating-multiclass-classifiers` / `evaluating-regression-models`
- The "comparison" is between a single model and a single fixed threshold (operating-point selection) → use `ml-datasci/tuning-classification-threshold`
- The models are being compared on DIFFERENT test sets — the paired tests in this skill require the SAME test instances scored by both models; if test sets differ, comparison is unpaired and the proper framing is two independent samples (not in scope of this skill, requires a different methodology)
- The user wants help with leakage / split discipline before comparison → use `ml-datasci/enforcing-leakage-firewall` first; comparing two models on a leaky split inflates BOTH and the test result is uninterpretable
- Pure pedagogy on what McNemar's test does without a real comparison — explain the concept and do not force the workflow

## Quick start

User: "Model A reaches 0.83 AUC on the test set. Model B reaches 0.85 AUC on the same test set. Is B significantly better?"

Response: same test set + two classifiers → McNemar on the disagreement table (predictions at the operating threshold). For threshold-free comparison on the same test set, use DeLong's test for ROC-AUC. Both account for the paired structure of "both models scored every test sample". An unpaired test (two-sample t on the AUC point estimates) would discard the paired information and is wrong.

```python
from statsmodels.stats.contingency_tables import mcnemar
import numpy as np

# Same threshold (0.5 default unless tuned per ml-datasci/tuning-classification-threshold)
pred_A = (p_A >= 0.5).astype(int)
pred_B = (p_B >= 0.5).astype(int)
both_right = ((pred_A == y_test) & (pred_B == y_test)).sum()
A_right_B_wrong = ((pred_A == y_test) & (pred_B != y_test)).sum()
A_wrong_B_right = ((pred_A != y_test) & (pred_B == y_test)).sum()
both_wrong = ((pred_A != y_test) & (pred_B != y_test)).sum()

table = [[both_right, A_right_B_wrong], [A_wrong_B_right, both_wrong]]
result = mcnemar(table, exact=False, correction=True)
print(f"McNemar chi-sq = {result.statistic:.3f}, p = {result.pvalue:.4f}")
```

See `reference/comparison-tests-decision-table.md` for the full selector.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `predictions_per_model` | dict[str, array-like] | yes | — | Map of model name → predictions on the SAME test instances. Same length, same order across models. |
| `y_test` | array-like | yes | — | Ground-truth labels for the shared test set. |
| `metric` | str or callable | yes | — | Comparison metric: `accuracy`, `f1`, `roc-auc`, `pr-auc`, `rmse`, `mae`, or a custom callable. Drives the test choice in some branches. |
| `cv_results_per_model` | dict[str, array-like of float] | conditional | — | Required when comparing via k-fold CV. Per-model array of per-fold metric values; arrays must have the same length and the SAME fold-index mapping across models (paired folds). |
| `alpha` | float | no | `0.05` | Significance level after correction. |
| `correction` | str | conditional | `holm` | Required when `len(predictions_per_model) >= 3`. One of `bonferroni`, `holm` (Holm-Bonferroni), `none` (only with explicit justification). |
| `paired_fold_test` | str | no | `auto` | When comparing CV results: `t` (paired t), `wilcoxon` (signed-rank), or `auto` (pick by Shapiro on the per-fold differences). |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

```
Fair-comparison progress:
- [ ] 0. Same-test-set check — confirm all models scored the SAME instances in the SAME order
- [ ] 1. Pick the test branch (same-test-set predictions, CV per-fold metrics, or threshold-free ROC-AUC)
- [ ] 2. For 3+ models, lock the correction plan BEFORE running tests
- [ ] 3. Run the paired test(s)
- [ ] 4. Apply correction if >= 3 comparisons
- [ ] 5. Report per-pair p-value, effect size (e.g. delta-AUC or delta-accuracy with bootstrap CI), AND verdict
- [ ] 6. Pick the winner only if (a) the difference is statistically significant AND (b) the effect size is operationally meaningful (delta passes a pre-registered threshold)
```

### Step 1: Pick the test branch

| Setup | Recommended test |
|---|---|
| Two classifiers, same test set, predictions at a chosen threshold | **McNemar** on the disagreement table (continuity-corrected for n >= 25, exact mid-p for smaller n) |
| Two classifiers, same test set, threshold-free ROC-AUC | **DeLong's test** (analytic CI on the AUC difference accounting for the paired structure) |
| Two models compared on k-fold CV per-fold metrics | **Paired t-test** if per-fold differences are roughly Normal (Shapiro p > 0.05) on n >= 10 folds; OR **Wilcoxon signed-rank** otherwise. Demsar 2006 recommends Wilcoxon by default for robustness. |
| 3+ models on k-fold CV | **Friedman omnibus** then **Nemenyi post-hoc** (Demsar 2006), OR pairwise Wilcoxon with Holm-Bonferroni |
| Two regression models, same test instances | **Paired t-test** on per-instance squared (or absolute) errors, OR **Wilcoxon** if per-instance error differences are non-Normal |

### Step 2: Lock the correction plan BEFORE testing

For 3+ models, the number of pairwise tests is `k * (k - 1) / 2`. Running them without correction inflates the family-wise error rate from `alpha = 0.05` to roughly `1 - (1 - 0.05)^m`. With 5 models, that is 10 pairs and ~40% chance of at least one false positive.

| Correction | When |
|---|---|
| `bonferroni` | Most conservative; multiply each p by `m` (cap at 1.0). Use when m is small (< 10) and false positives are costly. |
| `holm` (Holm-Bonferroni) | Uniformly more powerful than Bonferroni; sort p-values ascending and reject in step-down order against `alpha / (m - i + 1)`. Recommended default. |
| `friedman + nemenyi` | Demsar 2006 standard for comparing k models on N datasets / folds. Friedman omnibus tests "any model differs"; Nemenyi gives pairwise post-hoc with critical-difference plot. |
| `none` | Only with explicit justification (single planned comparison; exploratory analysis where the family is not the same as the test family). Document the choice. |

### Step 3: Run the paired test(s)

Use the test selected in step 1. For McNemar, the off-diagonal cells (A-right-B-wrong, A-wrong-B-right) are what the test reads. For paired t on CV folds, the input is the per-fold difference vector.

### Step 4: Apply correction

For `m` pairwise tests with Holm-Bonferroni:

```python
import numpy as np
def holm_bonferroni(p_values, alpha=0.05):
    m = len(p_values)
    order = np.argsort(p_values)
    reject = np.zeros(m, dtype=bool)
    for i, idx in enumerate(order):
        adjusted_alpha = alpha / (m - i)
        if p_values[idx] < adjusted_alpha:
            reject[idx] = True
        else:
            break  # step-down: stop at first non-rejection
    return reject
```

### Step 5: Report per-pair

For each pair: test name, test statistic, raw p, corrected p, effect size (delta metric with bootstrap 95% CI), verdict (significant after correction / not significant).

### Step 6: Pick the winner

Statistical significance alone is not enough. Require:

1. The difference is significant after correction
2. The effect size exceeds a pre-registered operationally-meaningful threshold (e.g. `delta_auc > 0.01`, `delta_accuracy > 1 percentage point`, `delta_rmse > 5% of target SD`)

If only (1) holds, the difference is real but too small to matter; report the result honestly and pick on a secondary criterion (cost, latency, interpretability).

## Outputs

A markdown report with this structure:

1. **Setup** — n_models, n_test_instances OR n_folds, metric, alpha, correction
2. **Test selector** — which test for which pair, with rationale
3. **Per-pair results** — model_A vs model_B, statistic, raw p, corrected p, delta metric + 95% CI, verdict
4. **Family-wise verdict** — which differences survive correction
5. **Recommendation** — winner (or tie / multiple admissible models) with operational-significance justification

## Failure modes

Known anti-patterns and how this skill catches them:

- **Unpaired two-sample t-test on per-fold CV metrics** — wrong; discards the paired structure and inflates the variance estimate. Caught by step 1 enforcing paired-t or Wilcoxon.
- **No paired test at all — just eyeballing 0.83 vs 0.85** — caught by `When to use` triggers and step 1.
- **No correction across 3+ models** — caught by step 2 lock-correction-before-testing.
- **Significance reported without effect size** — caught by step 5 requiring delta + CI alongside the p-value.
- **Statistical significance treated as operational significance** — caught by step 6 requiring a pre-registered meaningful-effect threshold.
- **DeLong's test on different test sets** — caught by step 0 same-test-set check.
- **McNemar on different threshold choices for the two models without disclosure** — both models must be at their own properly-tuned threshold; the comparison is then "best A vs best B at their respective operating points"; the skill requires the threshold choice to be documented.

## References

- `reference/comparison-tests-decision-table.md` — copy-paste implementations of McNemar, DeLong, paired-t, Wilcoxon, Friedman+Nemenyi
- [Demsar 2006 *Statistical comparisons of classifiers over multiple data sets*](https://www.jmlr.org/papers/v7/demsar06a.html) — Wilcoxon signed-rank + Friedman + Nemenyi framework
- [Dietterich 1998 *Approximate statistical tests for comparing supervised classification learning algorithms*](https://doi.org/10.1162/089976698300017197) — McNemar + 5x2 CV t-test rationale
- [DeLong et al. 1988 *Comparing the areas under two or more correlated ROC curves*](https://www.jstor.org/stable/2531595) — DeLong's test
- [scikit-learn StatsModels McNemar](https://www.statsmodels.org/dev/generated/statsmodels.stats.contingency_tables.mcnemar.html) — McNemar implementation

## Examples

### Example 1: A vs B on the same test set (happy-path)

Input: "Two binary classifiers (Logistic Regression vs Gradient Boosting) on the same 5,000-instance test set. LogReg gets 0.83 AUC; GB gets 0.85 AUC. Is GB significantly better?"

Output: Skill picks DeLong's test for threshold-free ROC-AUC comparison on the same test instances. Computes delta-AUC = 0.02 with 95% CI via DeLong's analytic variance. Reports p-value and CI. If GB also has a tuned operating threshold, also runs McNemar on the disagreement table at the chosen threshold. Notes that statistical significance is necessary but not sufficient — asks whether 0.02 AUC delta clears the operational threshold for switching from a simpler / cheaper LogReg to a more complex GB model.

### Example 2: 4 models on 10-fold CV with multiple-comparison correction (edge-case)

Input: "I'm comparing 4 models on 10-fold cross-validation: LogReg, RandomForest, XGBoost, LightGBM. I have per-fold accuracy for each model. Which is best, and which differences are real after multiple-comparison correction?"

Output: Skill computes pairwise paired-t (or Wilcoxon signed-rank if per-fold differences are non-Normal — checks with Shapiro on each pair). Reports raw and Holm-Bonferroni-corrected p-values for all 6 pairs. Recommends Friedman omnibus first to confirm any difference exists at all, then Nemenyi post-hoc with the critical-difference plot. Refuses to declare a winner from raw p-values without correction. Final recommendation includes effect size (delta accuracy + bootstrap 95% CI) for each surviving pair, not just the p-value.

### Example 3: Single model, no comparison (anti-trigger)

Input: "I trained a logistic regression on customer churn. Test accuracy is 0.78. Can you tell me if it's good?"

Output: Skill identifies this as a single-model evaluation, NOT a comparison. The paired tests in this skill require two or more models scored on the same test instances. Hands off to `ml-datasci/evaluating-binary-classifiers` for single-classifier scoring (ROC, PR, calibration, threshold sweep, bootstrap CIs) and `ml-datasci/building-baseline-models` for the baseline that contextualizes the 0.78 accuracy. Does NOT force a paired-test workflow on a one-model report.

## See also

- `ml-datasci/evaluating-binary-classifiers` — single-classifier scoring; required before comparison
- `ml-datasci/evaluating-multiclass-classifiers` — single-classifier scoring for 3+ class tasks
- `ml-datasci/evaluating-regression-models` — single-regressor scoring
- `ml-datasci/building-baseline-models` — required pre-step; the comparison space must include a baseline
- `ml-datasci/enforcing-leakage-firewall` — required pre-step; both models must clear the firewall on the same split before any comparison
- `ml-datasci/tuning-classification-threshold` — for McNemar, both models should be at their own properly-tuned threshold, not the default 0.5
- `ml-datasci/auditing-train-test-split` — required pre-step; comparing on a leaky split inflates both models

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-2, skill 2) via PRAGMATIC discipline
