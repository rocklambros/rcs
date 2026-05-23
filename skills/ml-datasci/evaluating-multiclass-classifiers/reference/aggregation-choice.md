# Choosing between macro / weighted / micro / cost-weighted F1

The aggregation choice is a cost-model statement, not a default. Pick it before reading the score.

## Decision rule

1. **Are all classes equally important regardless of frequency?** (Rare-disease detection, rare-attack detection, fairness audit across groups, balanced-care mandate.)
   - **Use macro-F1.** Each class contributes equally to the mean. Per-class collapse on the rarest classes is penalized.

2. **Does deployment cost scale with class frequency?** (User-facing accuracy on a skewed traffic mix where being right on the majority matters more.)
   - **Use weighted-F1.** Each class contributes proportional to its support. Rare-class collapse is forgiven (which may or may not match the cost model — say so explicitly).

3. **Is this single-label multi-class and only a sanity check is needed?**
   - **Micro-F1 = overall accuracy.** Useful only to confirm the math agrees with the accuracy figure; never the lead.

4. **Is there an explicit cost matrix?** (`C[i, j]` = cost of predicting `j` when truth is `i`.)
   - **Use cost-weighted-F1 or cost-weighted total loss.** Compute per-cell cost from the confusion matrix and the cost matrix. Report total expected cost per sample and compare against the always-predict-majority baseline.

## Common mistakes

- **Reporting only macro-F1 because "it's the fair one"** without checking whether the cost model agrees. On a 100x-imbalanced task where the majority class drives revenue and the rare class is a low-cost miss, weighted-F1 is what the business cares about.
- **Reporting only weighted-F1 because "it tracks accuracy"** on a rare-disease task where missing the rare class is the whole point. Weighted-F1 will read 0.95 while per-class recall on the rare class is 0.05.
- **Treating micro-F1 as a third metric** that adds information. In single-label, micro-F1 = accuracy = micro-precision = micro-recall. Reporting it as a separate metric is double-counting.
- **Hiding per-class collapse behind any aggregate.** Always read the per-class rows before any aggregated row.

## Example

5-class severity classifier, support = [1000, 800, 600, 50, 30], F1 per class = [0.92, 0.88, 0.82, 0.10, 0.05].

- macro-F1 = 0.554 — penalizes the rare-class collapse
- weighted-F1 = 0.842 — driven by the common classes
- micro-F1 = 0.84 (matches accuracy) — sanity check only

Lead with macro-F1 if rare severities matter equally to common ones. Lead with weighted-F1 if the rare severities are operationally negligible (say so, then justify). Either choice is defensible; reporting both without picking is not.
