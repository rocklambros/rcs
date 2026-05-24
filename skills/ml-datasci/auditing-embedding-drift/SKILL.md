---
name: auditing-embedding-drift
description: >
  Audits a deployed RAG or retrieval system for embedding drift over time or
  across cohorts. Computes per-dimension Jensen-Shannon divergence, centroid
  cosine distance, and intra-cohort distance shift between a baseline cohort
  and a comparison cohort, with bootstrap 95% confidence intervals so
  small-sample wobble is not reported as drift, then attributes the drift to
  new content categories, upstream-data shift, or provider-side model
  re-versioning. Use when retrieval recall is eroding without a code change,
  when an embedding model has been re-versioned, when comparing two embedding
  cohorts (training vs production, old vs new ingest, region A vs B), or for
  a periodic drift check on a long-running RAG. Refuses on a single-time-point
  dataset (no second cohort) or when the user has already decided to swap
  embedding models wholesale (the right action is re-embed, not drift
  analysis).
version: 0.1.0
status: shipped
track: ml-datasci
audience: [ml-engineer, data-scientist, ai-security]
evidence:
  - ai_security_framework_crosswalk
  - multiturn-injection-detection
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Auditing Embedding Drift

## When to use

Trigger this skill when the user:

- Reports that retrieval recall on a deployed RAG system has eroded over months without any code change
- Has been notified that the embedding model has been re-versioned by the provider (OpenAI silently pointing `text-embedding-3-large` at new weights; Voyage model deprecation; Cohere re-release)
- Is comparing two embedding cohorts (training set vs production set, last quarter's ingest vs this quarter's, region A vs region B, English vs translated corpus)
- Is scheduling a periodic (monthly / quarterly) embedding-drift health check on a long-running retrieval system
- Reports that "the same query that worked 6 months ago now returns different documents"
- Is investigating whether to re-embed the corpus, and needs to quantify the cost-benefit
- Just rolled out a new content category (e.g., a new product line added to a knowledge base) and wants to confirm the embedding distribution didn't drift in a way that breaks existing retrieval

## When NOT to use

Skip and hand off when:

- The dataset is single-time-point and has no second cohort to compare against (drift requires two distributions; if there is only one, this is not a drift question)
- The user has already decided to swap embedding models wholesale (the right action is to re-embed everything; quantifying the drift between an obsolete model and the new one is academic)
- The user is debugging chunking strategy — drift in retrieval can come from chunking too (use `auditing-chunking-strategy` to rule that out first)
- The user is debugging supervised-classifier prediction drift (use `monitoring-prediction-drift` for predicted labels, or `monitoring-data-drift` for input-feature drift)
- The user is in greenfield / pre-deployment — there is no baseline window yet against which to measure drift
- The user wants a one-shot RAG eval (use `evaluating-rag-retrieval`); drift is a longitudinal concern, not a one-shot one

## Quick start

User: *"My customer-support RAG retrieval has gotten worse over the last 6 months. Same code, same embedding model (text-embedding-3-large), but recall dropped from 0.84 to 0.71. Audit for embedding drift."*

Skill walks the 6-step workflow: (1) define baseline cohort (first month of production) and comparison cohort (last month), (2) compute drift metrics (KL / JS divergence per dimension, centroid cosine distance, intra-cohort mean distance shift), (3) bootstrap 95% CIs on each metric to separate signal from sample noise, (4) identify top-N most-drifted dimensions and top-N most-drifted documents, (5) attribute drift to one of three causes (new content categories, upstream data shift, embedding-model re-versioning), (6) recommend action (re-embed, drift-aware reranking, content-category gating, or no action if drift is within noise).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| baseline_embeddings | array[float] of shape (N_baseline, dim) | yes | — | Baseline embedding set with corresponding `baseline_ids` and `baseline_timestamps`. |
| comparison_embeddings | array[float] of shape (N_comparison, dim) | yes | — | Comparison embedding set with corresponding `comparison_ids` and `comparison_timestamps`. |
| embedding_model | string | yes | — | Model ID with revision pin (e.g., `openai/text-embedding-3-large@2026-01-15`). Used to detect provider-side re-versioning. |
| doc_metadata | dataframe | no | null | Optional per-document metadata (category, source, language) — enables drift attribution by slice. |
| n_bootstrap | int | no | 1000 | Bootstrap iterations for CI on drift metrics. |
| drift_alert_threshold | object | no | see reference/drift-thresholds.md | Per-metric thresholds above which drift is reported as actionable (vs noise). |
| top_n | int | no | 20 | Number of most-drifted dimensions and documents to surface in the report. |
| visualization | bool | no | true | Whether to render UMAP / t-SNE of the two cohorts and per-dim histograms for the top-shifted dims. |

## Workflow

Copy this checklist into the response and check off each step as the audit lands:

```
Audit progress:
- [ ] 1. Define baseline cohort and comparison cohort (time window, source slice, or explicit ID list)
- [ ] 2. Compute drift metrics: per-dim KL/JS divergence, centroid cosine distance, intra-cohort distance shift
- [ ] 3. Bootstrap 95% CIs (n=1000 default); drop any metric whose CI crosses the no-drift null
- [ ] 4. Identify top-N drifted dimensions + top-N drifted documents (highest contribution to overall drift)
- [ ] 5. Attribute drift to cause: new content categories, upstream data shift, or embedding-model re-versioning
- [ ] 6. Recommend action: re-embed, drift-aware reranking, gate by content category, or no action if within noise
```

### Step 1 — Define cohorts

The baseline cohort is what "normal" looked like; the comparison cohort is what's changed. Common splits:

| Split | Baseline | Comparison |
|---|---|---|
| Time | First month of production | Last month |
| Cohort | Training data | Production data |
| Re-version | Embeddings computed before YYYY-MM-DD | Embeddings computed after |
| Region | Docs from region A | Docs from region B |

Refuse to proceed if `min(N_baseline, N_comparison) < 100` — bootstrap CIs are unreliable below that and any reported "drift" is sample noise.

### Step 2 — Compute drift metrics

Three metrics, each capturing a different drift shape:

| Metric | What it captures | Formula |
|---|---|---|
| `kl_per_dim` | Per-dimension distributional shift | `KL(baseline_dim_i, comparison_dim_i)` averaged across `i`; histogram-based via N bins, N = sqrt(min cohort size) |
| `centroid_cosine_dist` | Overall semantic shift of the embedding space center | `1 - cos(centroid_baseline, centroid_comparison)` |
| `intra_cohort_dist_shift` | Whether the cohort is becoming more spread out or more clustered (concept clumping) | `mean_pairwise_dist(comparison) - mean_pairwise_dist(baseline)` |

Jensen-Shannon (`js_per_dim`) is preferred over KL when either distribution has zero-density bins; JS is symmetric and bounded. Use JS by default; flip to KL only if the user explicitly asks.

See `reference/drift-metrics-cookbook.md` for the formulas and numpy / sklearn implementations.

### Step 3 — Bootstrap CIs

Without CIs, you cannot tell "real drift" from "I happened to sample noisy embeddings." For each metric:

1. Resample with replacement from each cohort `n_bootstrap` times
2. Re-compute the metric on each resample
3. Report the 95% CI (2.5th and 97.5th percentile of the bootstrap distribution)

If the metric's 95% CI crosses the no-drift null (typically zero for divergences, zero for centroid distance change, zero for intra-cohort distance change), drop the metric — that is not actionable drift, that is sample wobble.

### Step 4 — Top-N most drifted

Two views:

- **Top-N dimensions**: which embedding dimensions account for the most KL/JS divergence? In a 1536-dim space, drift is typically concentrated in 20-50 dimensions. Surface these so the user can see whether drift is broad (every dim shifts a little — likely model re-versioning) or narrow (a few dims shift a lot — likely content-category shift).
- **Top-N documents**: which individual comparison-cohort documents are farthest from their nearest-neighbor in the baseline cohort? These are the docs that are "novel" relative to the baseline — often the smoking gun for "new content categories arrived."

### Step 5 — Attribute drift

Three attribution hypotheses, in order of likelihood when each pattern is observed:

| Pattern | Most likely cause | Confirming check |
|---|---|---|
| Broad drift across most dimensions, small per-dim magnitude, no new doc categories | Embedding-model re-versioning by the provider | Re-embed a sample of OLD docs and compare to their original embeddings — if they don't match, the model changed under you |
| Narrow drift in a few dimensions, top-N drifted docs cluster in a new category | New content category was added (new product line, new region, new language) | Group comparison-cohort docs by metadata.category; compute per-category centroid distance to baseline; one category will dominate |
| Drift correlates with timestamp gradually, no model change, no new category | Upstream-data shift (user-question phrasing drifted; source-of-truth content was edited) | Sample 10 raw documents from each cohort and qualitatively compare them; ask the data owner |

A drift audit that doesn't try to attribute is just a number. The attribution is what makes the recommendation actionable.

### Step 6 — Recommend action

| Attribution | Recommended action |
|---|---|
| Model re-versioning | Re-embed the corpus with the new model version. Document the model revision pin in the embedding config so future drift is detected immediately. |
| New content category | Either re-embed (if cost-acceptable) or add drift-aware reranking that downweights baseline-only documents in favor of recent ones for queries that look like the new category. |
| Upstream data shift | Re-embed at next scheduled refresh; if drift accelerates between refreshes, shorten the refresh cadence. |
| Within noise (CIs include zero) | No action. Document the audit date + the no-action decision so a future audit doesn't re-investigate the same finding. |

## Outputs

A markdown audit report containing:

- Baseline vs comparison cohort sizes + time windows
- Drift-metric table (one row per metric: point estimate, 95% CI, alert threshold, verdict)
- Top-N most-drifted dimensions (with per-dim JS divergence + CI)
- Top-N most-drifted documents (with their nearest-baseline-neighbor distance + metadata)
- UMAP / t-SNE plot of baseline vs comparison cohorts (one figure; optional)
- Per-dim histogram for the top-5 drifted dimensions (small multiples; optional)
- Drift-attribution analysis (which of the three hypotheses; with confirming evidence)
- Recommended action with cost estimate (re-embed corpus cost = `N_corpus * cost_per_embedding`)

## Failure modes

Known pitfalls and how this skill catches them:

- **Reporting drift without CIs** — small-sample noise looks identical to real drift in a point estimate. Caught by step 3 bootstrap CIs and step 1 refusing to proceed if cohort size < 100.
- **Conflating chunking drift with embedding drift** — if the chunking config changed between the cohorts, the embeddings will look "drifted" but the cause is upstream. Caught by step 1 documenting the chunking config in BOTH cohorts and aborting if they differ.
- **Missing the model re-versioning attribution** — providers silently re-train and re-deploy embedding models without changing the public model_id. Caught by step 5 confirming check (re-embed a sample of OLD docs with the CURRENT model and check whether the embeddings match).
- **Acting on within-noise drift** — paying $10K to re-embed because a CI just barely excludes zero is bad cost-benefit. Caught by step 3 requiring the point estimate to exceed an alert threshold (not just a non-zero CI) before recommending action.
- **No attribution** — a drift number with no diagnosis tells the user something is wrong but not what to do. Caught by step 5 forcing one of three attributions before step 6 recommends.
- **Running on too-small cohorts** — bootstrap CIs collapse on tiny samples and produce false-confident "drift" reports. Caught by step 1 hard minimum of 100 per cohort.

## References

- `reference/drift-metrics-cookbook.md` — formulas + numpy/sklearn snippets for KL, JS, centroid cosine, bootstrap CI
- `reference/drift-thresholds.md` — default per-metric alert thresholds calibrated to the most common embedding dims (768, 1024, 1536, 3072)
- [Hugging Face `evaluate` library, KL/JS modules](https://huggingface.co/docs/evaluate/) — third-party drift-metric implementations (one-level reference)
- [scikit-learn `pairwise_distances`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise_distances.html) — for intra-cohort distance computation

## Examples

### Example 1: Six-month deployment with declining retrieval (happy-path)

Input: *"My customer-support RAG retrieval has gotten worse over the last 6 months. Same code, same chunking, same embedding model (text-embedding-3-large). Recall on a fixed eval set dropped from 0.84 to 0.71. Audit for embedding drift. I have ~5000 baseline embeddings from month 1 and ~7000 from month 6, with document metadata including category and ingestion_date."*

Output: Skill walks all 6 steps. Defines cohorts as month-1 vs month-6 embeddings. Computes JS divergence per dim, centroid cosine distance, intra-cohort distance shift; bootstraps 95% CIs on each. Finds JS divergence concentrated in ~30 dimensions (narrow, not broad — rules out model re-versioning). Top-N drifted docs cluster in a "Returns & Refunds" category that grew 4x between month 1 and month 6 (new content category attribution). Recommends drift-aware reranking with category-gating as a cheaper interim, OR a full re-embed if cost-acceptable. Provides cost estimate: ~7000 docs × $0.13/1M tokens ≈ $1-3 to re-embed.

### Example 2: Static benchmark dataset, no second cohort (anti-trigger)

Input: *"I'm using the MS-MARCO dataset to evaluate my RAG system. Audit the embeddings for drift."*

Output: Skill declines. Explains drift requires two distributions across a meaningful axis (time, source, model version). A single static dataset like MS-MARCO has no second cohort to compare against — there is no drift dimension. Suggests `evaluating-rag-retrieval` for one-shot retrieval-quality measurement, or `auditing-chunking-strategy` if the user suspects the chunking config is the issue.

### Example 3: Provider re-versioned the embedding model (edge-case)

Input: *"OpenAI updated text-embedding-3-large last month and we noticed our retrieval got weird right after. Audit drift. We have 3000 embeddings from before the update and 3000 from after."*

Output: Skill walks all 6 steps. Cohorts split on the update date. Finds broad drift across most dimensions with small per-dim magnitudes (signature of model re-versioning, not content shift). Confirming check: re-embeds 50 OLD documents with the CURRENT model and computes cosine similarity to their original embeddings; if mean cosine < 0.95, confirms model changed. Attribution: provider re-versioning. Recommendation: re-embed the entire corpus with the new model version, AND pin the revision date in the embedding config (e.g., `openai/text-embedding-3-large@2026-01-15` not bare `text-embedding-3-large`) so the next re-version is detected at deploy time rather than after retrieval erodes.

## See also

- `ml-datasci/auditing-chunking-strategy` — rule out chunking drift before attributing to embedding drift
- `ml-datasci/evaluating-rag-retrieval` — one-shot retrieval-quality measurement (orthogonal to longitudinal drift)
- `ml-datasci/selecting-embedding-model` — the upstream decision (which model to use); revisit on re-versioning events
- `ml-datasci/monitoring-data-drift` — sibling pattern for tabular-feature drift (not embedding drift)
- `ml-datasci/monitoring-prediction-drift` — sibling pattern for predicted-label drift
- `ml-datasci/building-rag-eval-set` — the eval set needed to QUANTIFY whether drift is actually hurting retrieval

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
