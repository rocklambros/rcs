# Coverage vs Set Size: the Conformal Tradeoff

Reference notes for `building-conformal-prediction-set`. Marginal coverage is one of two numbers; set size (or interval width) is the other. Reporting only one is misleading.

## The two numbers

| Metric | Definition | Why it matters |
|---|---|---|
| Marginal coverage | Fraction of test points whose true label / value is inside the prediction set / interval | The guarantee the user buys with conformal prediction |
| Average set size (classification) | Mean number of labels in the prediction set across the test set | Useful sets are small; sets of size = K (all classes) achieve trivial coverage |
| Average interval width (regression) | Mean of `hi - lo` across the test set | Useful intervals are narrow; very wide intervals are uninformative |

A 90% coverage target met by returning all K classes for every input is technically valid and practically useless. Both numbers must appear in the output.

## What drives set size

- **Model quality.** A confident, well-fit base model produces small sets. The conformal layer cannot make a bad model into a good prediction set — it can only convert the model's score distribution into a coverage-guaranteed set.
- **Choice of nonconformity score.** APS / Adaptive Prediction Sets and similar scores produce smaller sets than the naive 1 - p score in the regime where the model is confident.
- **Heteroscedasticity (regression).** Absolute-residual conformal gives constant-width intervals everywhere. CQR (conformalized quantile regression) lets the interval widen in noisy regions and narrow in confident regions, often reducing average width while maintaining coverage.
- **Alpha.** Smaller alpha (95% vs 90% coverage) means a higher quantile, which means a wider interval / larger set. The tradeoff is unavoidable.

## Conditional coverage

Marginal coverage is an average over the test distribution. It can hide systematic miscoverage in subgroups:

- 90% marginal coverage with 95% coverage on the majority group and 60% coverage on a minority group is the textbook fairness failure
- Report coverage broken out by any sensitive attribute, label class, or relevant subgroup
- A coverage drop of 5 percentage points or more in any subgroup is a red flag worth fixing — consider Mondrian conformal (separate quantile per group) or class-conditional conformal

## The exchangeability assumption

The marginal-coverage guarantee assumes calibration and test points are exchangeable (a weaker assumption than i.i.d., but stronger than nothing). Coverage breaks when:

| Violation | Why it breaks coverage | Mitigation |
|---|---|---|
| Temporal drift | Distribution at deployment differs from calibration window | Refresh calibration window periodically; consider Adaptive Conformal Inference |
| Covariate shift | Test x's come from a different distribution than calibration x's | Weighted conformal with known likelihood ratio |
| Label drift | Class prevalence shifts after deployment | Class-conditional conformal; track marginal label distribution over time |
| Group leakage | Same patient / user / customer in cal and test | Use GroupKFold for the cal/test split |
| Selection bias in calibration | Calibration set is not representative of deployment | Re-sample calibration to match deployment when possible; otherwise document and flag |

When any of these apply, the marginal guarantee is broken. Be honest in the report. Conformal does not magically defend against non-exchangeability.

## Set size sanity checks

If average set size equals K (all classes) on a K-class problem, the model is uninformative or alpha is set too aggressively. Either condition needs intervention; do not ship the result.

If average set size equals 1, conformal is contributing nothing beyond top-1 prediction. That is acceptable when the underlying model is highly confident, but should be noted; the user could ship the top-1 prediction without the conformal layer and get the same set, with no coverage guarantee but no setup cost either.

## Reporting template

For every conformal deployment:

```
Conformal prediction summary
  - Coverage target: 1 - alpha = 0.90
  - Empirical coverage on test (n = 1,500): 0.913 [95% CI: 0.896, 0.927]
  - Average set size: 1.4 (classification), or average interval width: 8.2 minutes (regression)
  - Coverage by subgroup:
      group A (n = 1,200): 0.915
      group B (n =   300): 0.880  <-- flag for review
  - Exchangeability: random split, no temporal or group structure; assumption holds
```

Without these five lines, the conformal claim is incomplete.
