# Drift alert thresholds (defaults)

Default per-metric alert thresholds for `auditing-embedding-drift`. Use these as starting points and recalibrate against your own bootstrap no-drift distribution (resample within the baseline cohort and see how large the metric gets by chance alone).

The thresholds assume L2-normalized embeddings (the default for OpenAI, Voyage, Cohere). For un-normalized embeddings, the centroid cosine threshold below does not apply directly — re-scale or normalize first.

## Mean per-dim Jensen-Shannon divergence

| Embedding dim | Within-noise (likely sample wobble) | Actionable drift | Strong drift |
|---|---|---|---|
| 384 (MiniLM) | < 0.01 | 0.01 – 0.05 | > 0.05 |
| 768 (BGE-base, MPNet) | < 0.008 | 0.008 – 0.04 | > 0.04 |
| 1024 (BGE-large, Cohere) | < 0.006 | 0.006 – 0.03 | > 0.03 |
| 1536 (text-embedding-3-small) | < 0.005 | 0.005 – 0.025 | > 0.025 |
| 3072 (text-embedding-3-large) | < 0.004 | 0.004 – 0.02 | > 0.02 |

Higher-dim spaces have lower per-dim divergence at a given semantic drift level because the drift is spread across more dimensions. That is why the threshold scales inversely with dim.

## Centroid cosine distance (L2-normalized embeddings)

| Range | Interpretation |
|---|---|
| < 0.01 | Within noise; centroid has barely shifted |
| 0.01 – 0.05 | Mild drift; investigate top-N drifted docs |
| 0.05 – 0.15 | Clear drift; recommend action |
| > 0.15 | Strong drift; likely model re-versioning or major content-category shift |

## Intra-cohort mean pairwise distance shift

This metric is signed. Positive = comparison is more spread; negative = more clustered.

| Absolute value | Interpretation |
|---|---|
| < 0.005 | Within noise |
| 0.005 – 0.02 | Mild distribution-shape change |
| > 0.02 | Clear concept clumping or fragmentation; investigate |

## How to recalibrate

If these thresholds produce too-noisy alerts on your specific corpus + embedding model, recalibrate:

1. Sample two non-overlapping subsets of the BASELINE cohort (no time-axis drift)
2. Compute each drift metric between the two subsets
3. Repeat 100 times
4. Use the 95th percentile of each metric's distribution as the new "within-noise" upper bound

This gives you a corpus-specific noise floor. Anything above this floor is real signal.

## What the thresholds will NOT catch

- Adversarial drift (someone is intentionally feeding similar-looking embeddings to evade detection) — needs a separate adversarial-perturbation audit
- Concept drift in the GROUND-TRUTH labels — embeddings can be stable while the right answer for a query changes; use `building-rag-eval-set` and re-score periodically
- Slow drift that never crosses the threshold individually but compounds — schedule monthly re-audits with the SAME baseline (don't roll the baseline forward) so cumulative drift is visible
