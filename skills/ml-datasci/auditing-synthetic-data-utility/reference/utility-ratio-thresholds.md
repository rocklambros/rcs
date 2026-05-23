# Utility Ratio Thresholds and Verdict Rubric

Thresholds for converting a TSTR / TRTR utility ratio into a use / use-with-caveats / reject verdict. These are starting points; tune to the stakes of the downstream task.

## Default classification thresholds (ROC-AUC, normalized against 0.5 chance)

| Point ratio | 95% CI lower | Verdict | Acceptable use cases |
|---|---|---|---|
| ≥ 0.95 | ≥ 0.90 | **Use as real** | Public-research datasets, benchmark sharing, ML pipeline regression tests, model-development sandboxes |
| 0.85 – 0.95 | 0.80 – 0.90 | **Use with caveats** | Internal R&D, hypothesis generation, model debugging, ablation studies (NOT for clinical / financial / safety-critical final results) |
| < 0.85 | < 0.80 | **Reject** | Not suitable for downstream-task substitution; SDG needs to be re-fit or replaced |

## Higher-stakes contexts (clinical, financial, safety-critical)

| Point ratio | 95% CI lower | Verdict |
|---|---|---|
| ≥ 0.98 | ≥ 0.95 | Use as real |
| 0.95 – 0.98 | 0.92 – 0.95 | Use with caveats — domain-expert sign-off required |
| < 0.95 | < 0.92 | Reject |

In clinical / financial / safety-critical contexts the bar is higher because the downstream model's errors carry asymmetric harm. A 5% utility loss can translate to a meaningful change in false-negative rate on rare-but-serious conditions.

## Regression thresholds

For regression, define `ratio = TRTR_rmse / TSTR_rmse` (note: inverted from classification — RMSE is loss, not score). A ratio of 1.0 means synth matches real; ratios above 1.0 mean synth-trained model is more accurate (suspicious, often signals leakage).

| Ratio | 95% CI | Verdict |
|---|---|---|
| 0.90 – 1.05 | Lower ≥ 0.85 | Use as real |
| 0.75 – 0.90 | Lower in 0.70 – 0.85 | Use with caveats |
| < 0.75 OR ratio > 1.10 | Lower < 0.70 OR upper > 1.20 | Reject (low utility OR suspicious over-fit / leakage) |

## Rare-class adjustment

If the downstream task has any class with support < 5% of the dataset, compute the utility ratio per class as well as in aggregate. A weighted-F1 ratio of 0.94 can hide a per-rare-class F1 ratio of 0.4. Reject the aggregate verdict if any rare class drops below the same threshold band as the aggregate.

## Calibration with the TRTS sanity cell

Before accepting the verdict, check the TRTS / TRTR ratio:

- TRTS / TRTR in [0.90, 1.10] — synth distribution is well-calibrated; utility verdict is meaningful
- TRTS / TRTR > 1.10 — synth is over-smoothed; TSTR may be inflated because synth is easier than real
- TRTS / TRTR < 0.90 — synth is over-noised; TSTR may be deflated, hiding good utility

When TRTS / TRTR is outside [0.90, 1.10], note the calibration concern in the verdict regardless of where the utility ratio lands.

## Verdict-block template

```markdown
## Utility verdict

- TRTR (baseline): {trtr_metric:.3f}
- TSTR (utility): {tstr_metric:.3f}
- Utility ratio: {ratio:.3f} [95% CI: {lo:.3f}, {hi:.3f}]
- TRTS sanity: {trts_metric:.3f} (TRTS/TRTR = {ratio_sanity:.3f}, calibration: {ok|warn})
- Verdict: {USE_AS_REAL | USE_WITH_CAVEATS | REJECT}
- Caveats / failure attribution: {...}
```
