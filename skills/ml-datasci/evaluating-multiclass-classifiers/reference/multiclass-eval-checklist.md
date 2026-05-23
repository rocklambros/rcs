# Multi-class classifier evaluation report — copy-paste template

Replace `<...>` placeholders with computed values. Keep section order. Adjust the aggregation choice in section 2 per `aggregation-choice.md`.

---

## Dataset summary

- n = `<n_test>`
- n_classes = `<K>`
- Per-class support: `<{class: count, ...}>`
- Per-class proportion: `<{class: proportion, ...}>`
- Imbalance ratio (max / min) = `<ratio>` (`> 10 → imbalanced` triggers cost-model justification)
- Label source: `<file:line>`
- Split source: `<file:line>` (see `ml-datasci/auditing-train-test-split` for leakage audit)

## Aggregation choice (lead-metric justification)

- Macro-F1 = `<value>` — `<all classes weighted equally>`
- Weighted-F1 = `<value>` — `<classes weighted by support>`
- Micro-F1 = `<value>` (= overall accuracy in single-label) — `<sanity check>`
- **Lead metric chosen**: `<macro | weighted | cost-weighted>` because `<cost-model rationale>`

## Per-class metrics (sorted by support ascending)

| Class | Precision | Recall | F1 | Support | 95% CI (F1) |
|---|---|---|---|---|---|
| `<rare_class>` | `<p>` | `<r>` | `<f1> [<lo>, <hi>]` | `<n>` | `<bootstrap>` |
| ... |
| `<common_class>` | `<p>` | `<r>` | `<f1>` | `<n>` | — |

## Confusion matrix (counts)

|        | `<pred_0>` | `<pred_1>` | ... | `<pred_K-1>` |
|---     |---         |---         |---  |---           |
| `<true_0>` | `<n_00>` | `<n_01>` | ... | `<n_0,K-1>` |
| ... |

## Confusion matrix (row-normalized)

Same shape; cells in `[0, 1]` reading "of true class i, fraction predicted as class j".

## Top-k accuracy

- Top-`<k>` accuracy = `<value> [95% CI]`
- Skip if `k = K - 1` (collapses to trivial).

## Per-class one-vs-rest

| Class | ROC-AUC | Average Precision |
|---|---|---|
| `<class_0>` | `<auc>` | `<ap>` |
| ... |

Under imbalance for class `c`, lead its row with AP rather than AUC.

## Calibration and agreement

- Multi-class log loss = `<value>`
- Multi-class Brier = `<value>`
- Cohen's kappa = `<value>` (`< 0.40 weak / 0.40-0.75 fair to good / > 0.75 strong`)

## Dominant confusions (top 2-3 off-diagonal pairs, row-normalized)

| True | Pred | Fraction | Domain interpretation |
|---|---|---|---|
| `<class_i>` | `<class_j>` | `<x.xx>` | `<visually-similar / labeling-error / collapsed-feature>` |
| ... |

## Residual risks

- Sample-size caveats: classes with support < `<n>` have CIs of width `<w>`; treat point estimates as indicative only
- Drift sensitivity: per-class proportion in production vs test
- Single-label assumption: if a sample plausibly belongs to multiple classes, the multi-class framing is wrong; use multi-label evaluation instead
