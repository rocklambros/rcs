# Drift metric selection per feature type

The right metric depends on the feature type, cardinality, and tolerance for new levels. Wrong metric → either continuous false alarms or silent misses.

## Continuous features

### Population Stability Index (PSI)

- Bin on **reference quantiles** (e.g., 10 deciles of the reference distribution). Binning on current data lets bin definitions drift; binning on raw equal-width edges produces empty bins in skewed features.
- Apply Laplace smoothing: `p_i = (count_i + 1) / (total + bins)`. Prevents `log(0)` when a current bin is empty.
- Industry bands (Siddiqi 2017): < 0.1 stable, 0.1-0.25 minor, > 0.25 major. Use as a starting point only; always overlay the empirical noise floor from `threshold-calibration.md`.

```python
def psi(reference, current, bins=10):
    edges = np.quantile(reference, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    ref_p = (ref_counts + 1) / (ref_counts.sum() + bins)
    cur_p = (cur_counts + 1) / (cur_counts.sum() + bins)
    return float(np.sum((cur_p - ref_p) * np.log(cur_p / ref_p)))
```

### Kolmogorov-Smirnov (KS)

- Non-parametric, distribution-free. Catches shape changes (bimodality emergence, tail thickening) that PSI bins can smooth over.
- Two-sample KS statistic + p-value. With production-sized windows (10K+ rows), p-values are misleadingly small for trivial differences — use the KS *statistic* as the effect size, not the p-value.
- Use as a secondary metric: PSI for alerting, KS for diagnosis.

### Wasserstein / Earth-Mover's Distance

- Use when the absolute magnitude of the shift matters (regression targets, latency distributions). Wasserstein has units (the unit of the feature); PSI is dimensionless.
- More expensive to compute; reserve for low-cardinality continuous features where the unit interpretation is valuable.

## Ordinal features

Treat as continuous on the ordinal scale. PSI on the ordinal bin counts is the workhorse. Do NOT chi-square ordinal data — it discards the ordering information.

## Categorical features

### Jensen-Shannon divergence (JS)

- Symmetric, bounded in [0, 1] (with log base 2) or [0, log(2)] (with natural log).
- Handles **new levels in current that did not exist in reference** without producing infinite divergence (because of the averaged midpoint distribution).
- Recommended primary metric for low-to-moderate cardinality categoricals.

```python
def jensen_shannon(p, q):
    # p, q: probability vectors over the same support (use union of categories with Laplace smoothing)
    m = 0.5 * (p + q)
    return 0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m))
```

### Chi-squared

- Test of independence between distribution and window indicator. Use only when the expected count per cell is ≥ 5.
- Like KS, the p-value is misleading on production-sized samples; use the chi-squared statistic as the effect size with a Cramér's V normalization.

### Avoid: bare KL divergence

KL is asymmetric and unbounded. A new categorical level not present in reference makes KL infinite. JS is the symmetric, bounded fix.

## Boolean features

- Proportion of `True` in reference vs. current, with a binomial 95% CI on each.
- Alert when the CIs do not overlap AND the absolute delta exceeds a documented per-feature minimum (e.g., 0.02 absolute).

## High-cardinality text / IDs

- Skip PSI / JS — they are noise-dominated and unstable on long-tail distributions.
- Track instead: (a) count of new levels not seen in reference, (b) total distinct cardinality, (c) frequency of the top-K most common levels.
- A "new level" rate exceeding 1% / day on a feature that historically had 0.01% / day is the actionable signal.

## Datetime features

- Out-of-range count: rows with `event_date > today()` or `event_date < min_plausible_year`. Cross-reference `workflow/validating-temporal-fields`.
- Cadence: events / day. Sudden change in cadence is often pipeline failure, not data drift.

## Missingness as a first-class signal

Compute null rate per feature in both windows. A null-rate jump from 0.1% to 8% is rarely "drift" — it is almost always an instrumentation bug. Alert on missingness as its own check, distinct from value-distribution drift.
