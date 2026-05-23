# Binary-classifier evaluation report — copy-paste template

Replace `<...>` placeholders with computed values. Keep section order; under class imbalance, swap the order of the PR and ROC subsections within the Threshold-free section.

---

## Dataset summary

- n = `<n>`
- Positive rate = `<positive_rate>` (`< 0.20 → imbalanced` / `0.20–0.80 → roughly balanced` / `> 0.80 → imbalanced (positive-majority)`)
- Missing-value handling: `<dropna / impute-with-X / explicit-null-category>`
- Train/test split source: `<file:line or commit>` (see `ml-datasci/auditing-train-test-split` for leakage audit)

## Threshold-free metrics

**Under imbalance, PR-AUC leads; ROC follows.**

- PR-AUC = `<value> [95% CI: <low>, <high>]` (bootstrap n = `<n_bootstrap>`)
- ROC-AUC = `<value> [95% CI: <low>, <high>]` (bootstrap n = `<n_bootstrap>`)

Plots:

- `pr-curve.png` — precision-recall curve; AP annotated
- `roc-curve.png` — ROC curve; AUC annotated

## Calibration

- Brier score = `<value>` (lower is better; 0.25 = always-predict-0.5 baseline)
- Reliability diagram: `calibration-plot.png` (10 bins or fewer if n < 500)
- Verdict: `<well-calibrated | systematic-overconfidence | systematic-underconfidence>`
- If miscalibrated: recommended post-hoc fix = `<Platt | isotonic>`

## Threshold selection

- Sweep grid: `np.linspace(0.01, 0.99, 99)`
- Cost ratio (FN-cost : FP-cost) = `<cost_ratio>`
- Chosen threshold = `<t*>`
- Rationale = `<argmax-F1 | argmin-cost-aware-loss | precision-floor-≥-X>`
- Sweep plot: `threshold-sweep.png` (precision, recall, F1, MCC vs threshold)

## At chosen threshold

|        | Predicted Positive | Predicted Negative |
|---     |---                 |---                 |
| **Actual Positive** | TP = `<tp>` | FN = `<fn>` |
| **Actual Negative** | FP = `<fp>` | TN = `<tn>` |

- Precision = `<value> [95% CI]`
- Recall = `<value> [95% CI]`
- Specificity = `<value> [95% CI]`
- F1 = `<value> [95% CI]`
- MCC = `<value> [95% CI]`

## Residual risks

- Drift sensitivity: `<thoughts on whether the test set represents production traffic>`
- Calibration fragility: `<does recalibration on a fresh batch shift Brier > 0.05?>`
- Sample-size caveats: `<minority class n; bootstrap CI width as a function of that n>`
- Pre-step sanity: confirm `auditing-train-test-split` ran clean before trusting any number above
