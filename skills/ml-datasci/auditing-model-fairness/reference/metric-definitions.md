# Fairness metric definitions

For each protected attribute A with groups g ∈ {g₁, g₂, ..., gₖ}.

## Per-group rates

- **Base rate**: P(Y = 1 | A = g) — the true positive frequency in the group
- **Selection rate**: P(Ŷ = 1 | A = g) — the predicted-positive frequency in the group (depends on threshold)
- **True positive rate (TPR / recall / sensitivity)**: P(Ŷ = 1 | Y = 1, A = g)
- **False positive rate (FPR)**: P(Ŷ = 1 | Y = 0, A = g)
- **True negative rate (TNR / specificity)**: 1 − FPR
- **False negative rate (FNR)**: 1 − TPR
- **Precision (PPV)**: P(Y = 1 | Ŷ = 1, A = g)
- **Negative predictive value (NPV)**: P(Y = 0 | Ŷ = 0, A = g)

## Gap metrics across groups

- **Demographic-parity gap**: maxₘ selection_rate(g) − minₘ selection_rate(g)
- **Equal-opportunity gap**: maxₘ TPR(g) − minₘ TPR(g)
- **Equalized-odds gap**: max(equal-opportunity gap, FPR gap)
- **Predictive-parity gap**: maxₘ precision(g) − minₘ precision(g)

## Four-fifths rule (EEOC)

For each group, compute ratio = selection_rate(g) / maxₘ selection_rate(g). If any ratio < 0.80, a disparate-impact concern is triggered. This is a regulatory threshold, not a statistical one.

## Calibration within group

- Bin predicted probabilities into 10 deciles
- For each bin b in group g, observed_rate(g, b) = mean(Y | A = g, predicted ∈ bin b)
- Calibration slope (group g): regression of observed_rate on bin midpoint; slope = 1 means perfectly calibrated
- **Brier score per group**: mean((p̂ − y)²) for records in group g; lower is better
- A group whose calibration curve systematically over- or under-predicts (slope ≠ 1, intercept ≠ 0) is mis-calibrated for that subpopulation

## Bootstrap CI procedure

For a gap statistic G (e.g., TPR gap):

1. Draw n_bootstrap ≥ 1000 samples with replacement from the test set (stratified by group when group sizes are small)
2. Recompute G on each resample
3. Report the 2.5th and 97.5th percentiles as the 95% CI

A CI that crosses zero indicates the gap is not statistically distinguishable from zero at the given sample size. A wide CI on a small group reflects sampling uncertainty, not the absence of disparity in the population.

## Impossibility theorems (cite explicitly)

- **Kleinberg-Mullainathan-Raghavan 2017**: calibration-within-group, balance-for-positive-class (equal TPR), and balance-for-negative-class (equal FPR) cannot all hold simultaneously when base rates differ across groups (except in trivial cases)
- **Chouldechova 2017**: predictive parity and equal FPR/FNR cannot both hold when base rates differ

These mean: when base rates differ across groups, the deployer must pick which metric to honor. The audit reports the trade-off; the deployer owns the choice.
