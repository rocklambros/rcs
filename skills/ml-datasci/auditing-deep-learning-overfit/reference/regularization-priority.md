# Regularization priority

When classic overfit is confirmed, work this list top-to-bottom. Each row lists the technique, cost, and the signal that says "this is the right one".

| Priority | Technique | Cost | When it's the right one |
|---|---|---|---|
| 1 | Early stopping | Free (zero training cost; you already have the trajectory) | val loss has a clear minimum epoch |
| 2 | Data augmentation | Cheap (training time ~same; one-time augmentation pipeline build) | input modality has known invariances (vision: rotation/flip/color; text: paraphrase/back-translation; audio: noise/pitch) |
| 3 | Dropout | Cheap (training time ~same; small inference cost) | network has dense / fully-connected layers; works less well on conv layers without spatial dropout |
| 4 | Weight decay (L2 reg) | Cheap | weight norm trajectory is rising; targets parameter magnitude memorization |
| 5 | Label smoothing | Cheap | classifier outputs are over-confident; helps calibration AND overfit |
| 6 | Reduce model capacity | Medium (re-train) | even after 1-5 the gap persists; smaller model may match if data is limited |
| 7 | Collect more data | High (expensive in time / cost) | when the rule of thumb (≥ 100-1000 examples per learnable feature for tabular, 10²-10³ images per class with augmentation) is violated; sometimes the only fix |
| 8 | Architecture change (different topology entirely) | Very high | last resort; only after 1-7 exhausted |

## Why this order

- **Free things first.** Early stopping costs zero and often resolves "overfit" on its own.
- **Cheap, well-targeted things next.** Data augmentation expands the effective training distribution at near-zero cost.
- **Cheap untargeted things next.** Dropout / weight decay are general-purpose; cheap to add, but adding them when the actual issue is shift or label noise is wasted effort.
- **Capacity reduction is risky.** A smaller model that fits better on small data may underperform once more data arrives.
- **More data is expensive.** Use as a guide, not a first move.

## Anti-priority — what NOT to reach for first

- **Adding more regularizers in parallel** (dropout + weight decay + label smoothing all at once) — you cannot tell which one helped, and they interact.
- **Pre-training on a different dataset** — useful in transfer learning contexts but it changes the question; not an "overfit remediation" per se.
- **Switching frameworks (Keras → PyTorch)** — does nothing for overfit; sometimes a sign the user is troubleshooting the wrong layer.

## Sample-complexity rules of thumb (rough; use as floor, not ceiling)

| Data type | Rough minimum n_train for the model to generalize without strong regularization |
|---|---|
| Tabular, 10-50 features | 1,000 - 10,000 |
| Tabular, 50-500 features | 10,000 - 100,000 |
| Image classification (single class), with augmentation | 100 - 1,000 per class |
| Image classification, no augmentation | 1,000 - 10,000 per class |
| Text classification, transformer fine-tune | 1,000 - 10,000 per class |
| Sequence-to-sequence, from scratch | 100,000+ |

These are rough. They depend heavily on intra-class variability, label noise, and target metric.
