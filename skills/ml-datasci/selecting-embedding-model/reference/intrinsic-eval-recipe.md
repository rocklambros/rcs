# Intrinsic eval recipe (labeled-pair similarity)

The intrinsic eval is a cheap, fast comparison that runs in minutes per candidate model. It does not replace the extrinsic eval — but it surfaces "this model has no idea what is similar in our domain" cases quickly.

## What is a labeled pair?

A pair `(text_a, text_b, gold_similarity)` where:

- `text_a` and `text_b` are short excerpts drawn from the production corpus (paragraphs, sentences, or chunks at the deployment chunk size)
- `gold_similarity` is a 0-1 (or 0-5) score from human labelers indicating semantic similarity for the deployment task (information overlap? topical overlap? answerable-by-the-same-document? — pick one, document it)

## Construction protocol

1. **Sample 200+ pairs** stratified to include:
   - ~30% "near-duplicate" pairs (paraphrases, restatements) — should score high
   - ~30% "topical but different question" pairs — should score medium
   - ~30% "same topic, different polarity or entity" pairs (e.g., two policies that look similar but apply to different customer tiers) — should score low-medium
   - ~10% "completely unrelated" pairs — should score near zero
2. **Label with at least 2 annotators per pair.** Compute Cohen's κ on a held-out 20-pair subsample. If κ < 0.6, the task definition is ambiguous — tighten it before labeling at scale
3. **Document the labeling guideline.** What counts as similar in your domain (information-overlap vs. topical-overlap vs. answerable-by-same-doc) is a project-level decision and changes the right embedding model

## Scoring per candidate

```python
from scipy.stats import spearmanr
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Embed each side
emb_a = embed_model(texts_a)  # shape (n, dim)
emb_b = embed_model(texts_b)  # shape (n, dim)

# Pairwise cosine similarity (diagonal)
cos_sim = (emb_a * emb_b).sum(axis=1) / (
    np.linalg.norm(emb_a, axis=1) * np.linalg.norm(emb_b, axis=1)
)

# Correlation with gold labels
rho, p = spearmanr(cos_sim, gold_similarity)
```

## Bootstrap CI

Resample the n pairs with replacement; recompute Spearman; repeat ≥ 1000 times. Report `rho [95% CI: low, high]` per candidate.

## What the score means

- **rho > 0.80:** model agrees with humans about similarity in your domain
- **rho 0.60 – 0.80:** workable but not strong; check the extrinsic results before deciding
- **rho < 0.60:** model has weak signal in your domain; likely needs domain-tuned embedding or hybrid retrieval

## When intrinsic disagrees with extrinsic

Trust the extrinsic. Two common patterns produce intrinsic-extrinsic disagreement:

1. The intrinsic pairs sample a different distribution than the production queries (e.g., near-duplicate-heavy intrinsic vs. open-ended-question production)
2. The retrieval task involves multi-hop or aggregation queries where pair-wise similarity is not the right shape of the problem

In either case, the extrinsic golden Q-A set reflects the deployed task; the intrinsic set is a diagnostic only.
