---
name: selecting-embedding-model
description: >
  Selects an embedding model for a retrieval or semantic-similarity workload by
  running a head-to-head comparison across candidate models on three axes:
  intrinsic quality (similarity ranking on labeled pairs from the target
  domain), extrinsic quality (retrieval recall@k / MRR / nDCG@k on a golden
  Q-A set), and operational cost (latency, dollars per million tokens, index
  size, dimensionality). Triggers whenever the user is starting a new RAG or
  semantic-search project, considering swapping the embedding model in an
  existing pipeline, or trying to pick between two candidates that "feel
  similar" on a benchmark. Refuses to recommend a model from leaderboards
  alone without a domain-specific extrinsic comparison.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
evidence:
  - llm-toxicity-visual-analysis
  - multiturn-injection-detection
last-updated: 2026-05-23
---

# Selecting an Embedding Model

## When to use

Trigger this skill when:

- A new RAG, semantic-search, deduplication, clustering, or recommendation pipeline is being built and the user must pick an embedding model
- An existing embedding model is suspected of underperforming and a swap is being considered (the user reports "retrieval feels off" or "similarity scores are unreliable")
- Two or more candidate models look similar on public leaderboards (e.g., MTEB) and the user is trying to decide between them for their specific domain
- A cost-vs-quality trade-off is forcing a decision between a high-tier paid model (`text-embedding-3-large`, `voyage-3-large`, `Cohere embed-v3`) and a lower-tier or self-hosted alternative
- Keywords: embedding model, embedding selection, MTEB, retrieval quality, embedding swap, vector dimensionality, cosine similarity, semantic search backbone

## When NOT to use

Skip this skill and hand off when:

- The pipeline already includes retrieval AND generation and the user wants an end-to-end score on the assembled system — use `ml-datasci/evaluating-rag-retrieval` (this skill is the upstream component evaluator)
- The user is locked into a single provider with no swap option — there is nothing to compare; explain the constraint and offer a "tune what you have" path (chunking, reranker, hybrid retrieval) instead
- The task is picking a generative LLM, not an embedding model → use `ml-datasci/recommending-model-tier` (planned)
- The user has no labeled data in their domain and is unwilling to construct any — explain that selection requires either labeled pairs or a downstream metric, and recommend constructing a minimal golden set first

## Quick start

User: *"We're building a semantic search over our internal engineering documentation, about 80K markdown files. We're choosing between `text-embedding-3-large` (OpenAI), `voyage-3-large` (Voyage), and a self-hosted `bge-large-en-v1.5`. Pick one for us."*

Response: refuse to recommend from leaderboards alone. Run the staged comparison — **intrinsic** (similarity ranking on labeled pairs from the engineering-docs domain), **extrinsic** (retrieval metrics on a domain-specific golden Q-A set), and **operational** (latency p95, dollars per million tokens for the production volume, index size at the candidate dimensionalities). Report a recommendation table with the trade-offs explicit.

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Intrinsic: rank labeled pairs by similarity, compute Spearman against gold ranking
def intrinsic_correlation(emb_a, emb_b, gold_similarity):
    cos_sim = cosine_similarity(emb_a, emb_b).diagonal()
    return spearmanr(cos_sim, gold_similarity).correlation
```

See `reference/comparison-matrix.md` for the head-to-head report template, `reference/intrinsic-eval-recipe.md` for the pair-ranking protocol, and `reference/cost-model.md` for the operational-cost calculator.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `candidate_models` | list of `{name, provider, dim, max_input_tokens, $/M_tokens, latency_p95_ms}` | yes | — | The embedding-model candidates. At least 2; typically 3-5. |
| `domain_pairs` | list of `{text_a, text_b, gold_similarity ∈ [0, 1]}` | conditionally yes | — | Labeled similarity pairs from the target domain for intrinsic eval. ≥ 200 pairs recommended. Required unless an extrinsic golden Q-A set is supplied. |
| `golden_qa_set` | list of `{question, gold_doc_ids}` | conditionally yes | — | Extrinsic eval set. Required unless intrinsic `domain_pairs` is supplied (both is best). |
| `production_query_volume` | int per month | no | — | Used to compute monthly $ cost in the operational stage. |
| `index_corpus_size` | int (n docs) | no | — | Used to compute index storage cost at each candidate's dimensionality. |
| `n_bootstrap` | int | no | `1000` | Bootstrap resamples for 95% CI on each metric. |

## Workflow

```
Embedding-model selection progress:
- [ ] 0. Pre-check (candidates ≥ 2; at least one of {domain_pairs, golden_qa_set} provided; production volume estimated)
- [ ] 1. Intrinsic eval (if domain_pairs provided): Spearman or Kendall correlation of cosine-similarity ranking vs. gold ranking, per candidate; bootstrap 95% CI
- [ ] 2. Extrinsic eval (if golden_qa_set provided): recall@k / MRR / nDCG@k on the domain golden set, per candidate; bootstrap 95% CI
- [ ] 3. Operational eval: latency p50/p95, $/M tokens, monthly $ at production volume, index size at candidate dim, max input token limit
- [ ] 4. Tie-detection: if top candidates are within bootstrap CIs of one another on quality, declare a tie and break on operational axis
- [ ] 5. Recommendation table: per-candidate score on each axis + verdict + caveats
```

### Step 1: Intrinsic evaluation (similarity-ranking on labeled pairs)

The intrinsic eval asks: does this embedding model agree with humans about which pairs of texts are more similar?

- Sample at least 200 pairs from the target domain. Label each with a similarity score on a 0-1 (or 0-5) scale. Cohen's κ across labelers should exceed 0.6
- For each candidate model, embed all `text_a` and `text_b`; compute pairwise cosine similarity; compute Spearman (or Kendall) correlation against the gold similarity scores
- Bootstrap-resample the pair set to compute a 95% CI on the correlation
- The intrinsic correlation is a fast cheap signal but does not always predict downstream retrieval performance — pair it with the extrinsic eval

See `reference/intrinsic-eval-recipe.md` for the labeling protocol.

### Step 2: Extrinsic evaluation (retrieval metrics on a golden Q-A set)

The extrinsic eval asks: when this embedding model is plugged into the retriever, does it actually retrieve the right documents?

- Build (or reuse) a golden Q-A set per `ml-datasci/evaluating-rag-retrieval` (`reference/golden-qa-construction.md`)
- For each candidate model, embed the corpus, embed the queries, retrieve top-k by cosine similarity
- Report `recall@1`, `recall@5`, `recall@10`, `MRR`, `nDCG@10`, each with bootstrap 95% CI
- The extrinsic eval is the ground truth for selection. When intrinsic and extrinsic disagree, trust extrinsic

### Step 3: Operational evaluation

The operational eval asks: what does this model cost in production?

For each candidate, measure:

- **Latency:** p50 and p95 of the embedding call, measured on 100+ representative queries at the production batch size. Cold-start (first call after idle) often differs from steady-state — measure both
- **$ per million tokens:** from the provider's pricing page; for self-hosted, amortize the GPU-hour cost over expected token throughput
- **Monthly $:** `$/M tokens × production_query_volume × avg tokens per query`. Don't forget index-build cost (corpus_size × avg tokens per doc) as a one-time or refresh-cadence amortized cost
- **Index size at dim:** `corpus_size × dim × 4 bytes` (fp32) or `× 1 byte` (int8 quantized). At 80K docs, the difference between 768-dim and 3072-dim is the difference between fitting in a small Pinecone tier or needing a larger one
- **Max input tokens:** if the model truncates docs above N tokens, the chunking strategy must respect that limit

### Step 4: Tie-detection and operational break

If the top candidates' extrinsic metrics have overlapping bootstrap CIs, they are statistically indistinguishable on quality. In that case, the tiebreaker is operational: pick the cheaper, lower-latency, or lower-dimensional option.

When CIs do not overlap, the quality leader wins unless the operational delta is large enough to warrant the trade-off (e.g., 2 percentage points on recall@5 in exchange for 10x cost is rarely worth it; 10 percentage points usually is — document the decision).

### Step 5: Recommendation table

Final report includes a candidate-by-axis matrix:

| Candidate | Intrinsic Spearman | Recall@5 | MRR | $ / month | Latency p95 | Verdict |
|---|---|---|---|---|---|---|
| A | | | | | | |
| B | | | | | | |
| C | | | | | | |

With each metric carrying its 95% CI and the verdict naming the winner per axis and the overall recommendation.

## Outputs

A markdown report with:

1. **Candidate list** — model name, provider, dim, max tokens, $/M tokens, latency p95
2. **Intrinsic results** — Spearman per candidate `value [95% CI: low, high]`, with the labeled-pair stats (n pairs, κ)
3. **Extrinsic results** — recall@{1,5,10}, MRR, nDCG@10 per candidate, with CIs
4. **Operational results** — monthly $, index size, latency, max input tokens per candidate
5. **Comparison table** — the full matrix
6. **Recommendation** — single recommended model with explicit trade-off rationale; named runner-up; conditions under which the recommendation should be revisited (corpus growth, latency-budget change, multilingual addition, etc.)

## Failure modes

Known anti-patterns and how this skill catches them:

- **Picking from leaderboards alone (MTEB, BEIR) without a domain test** — caught by requiring at least one of `domain_pairs` or `golden_qa_set`; leaderboards average across many domains and your domain may not be represented
- **Intrinsic-only evaluation when downstream is retrieval** — caught by the disagreement-handling rule: if intrinsic Spearman ranks A > B but extrinsic recall ranks B > A, trust extrinsic
- **Ignoring tie detection** — caught by step 4 bootstrap-CI overlap check; declaring a quality winner inside the noise floor leads to flip-flopping decisions
- **Cost computed only at the per-query rate, ignoring index-build** — caught by step 3 including index-build amortization in the monthly figure
- **Dimensionality ignored at index sizing** — caught by step 3 explicit index-size calculation
- **Latency measured at cold-start only or steady-state only** — caught by step 3 requiring both
- **Comparing against an old model version** — pin provider model versions; `text-embedding-3-large` and `text-embedding-ada-002` are different products
- **Same-provider monoculture** — when the LLM provider and embedding provider are the same, consider at least one cross-provider candidate to break the bundle bias

## References

- `reference/comparison-matrix.md` — copy-paste report template
- `reference/intrinsic-eval-recipe.md` — labeled-pair construction and Spearman-correlation protocol
- `reference/cost-model.md` — monthly $ calculator including index-build amortization
- [Muennighoff et al. 2023, *MTEB: Massive Text Embedding Benchmark*, EACL](https://aclanthology.org/2023.eacl-main.148/) — the leaderboard whose results need domain-specific verification
- [Thakur et al. 2021, *BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models*, NeurIPS](https://openreview.net/forum?id=wCu6T5xFjeJ) — retrieval-specific benchmark; same caveat about domain transfer applies

## Examples

### Example 1: Three candidates on engineering docs (happy-path)

Input: *"We're building semantic search over 80K internal engineering markdown files. We're choosing between `text-embedding-3-large`, `voyage-3-large`, and `bge-large-en-v1.5`. Pick one for us."*

Output: Skill refuses to pick from leaderboards. Requests (or constructs) a 200-pair intrinsic labeled set and a 100-question golden Q-A extrinsic set drawn from real engineering queries. Embeds the corpus with each candidate; runs the three-stage report; produces the comparison matrix with bootstrap CIs; recommends the candidate with the best extrinsic recall@5 unless the operational delta forces a different choice. Names a runner-up and the conditions under which to revisit.

### Example 2: Tie within CI; cost breaks the tie (edge-case)

Input: *"Recall@5 for `text-embedding-3-large` is 0.78 (CI 0.74-0.82) on our golden set, and for `text-embedding-3-small` it's 0.76 (CI 0.72-0.80). Pick one."*

Output: Skill identifies the CIs as overlapping and the candidates as statistically indistinguishable on quality. Switches to the operational tiebreaker: `text-embedding-3-small` is roughly 6x cheaper and lower-dimensional (smaller index). Recommends `small` with an explicit "revisit if recall@5 < 0.70 in production drift" guardrail.

### Example 3: Single-provider lock-in (anti-trigger)

Input: *"We're using OpenAI for everything and we can't add another provider. Should we switch our embedding model?"*

Output: Skill notes that selection requires comparing candidates, and with a lock-in there is no meaningful selection. Offers a constrained path: compare OpenAI's own embedding tiers (`text-embedding-3-small` vs `text-embedding-3-large` vs `text-embedding-ada-002`), or pivot to non-embedding fixes (chunking strategy, reranker, hybrid retrieval) that can lift retrieval quality without changing providers.

## See also

- `ml-datasci/evaluating-rag-retrieval` — the downstream skill that uses the chosen embedding model in an end-to-end RAG eval
- `ml-datasci/profiling-llm-cost` — sibling for measuring the generation-side cost; this skill measures the retrieval-side cost
- `ml-datasci/comparing-models-fairly` (planned) — sibling pattern for statistically rigorous model comparison (McNemar / paired-folds discipline)
- `workflow/pre-registering-eval-study` — required pre-step locking the candidate list and golden set before scoring (prevents tweaking until your favored model wins)

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-3, skill 2) via PRAGMATIC discipline
