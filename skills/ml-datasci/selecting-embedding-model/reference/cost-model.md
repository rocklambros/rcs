# Operational cost model

The monthly $ figure for an embedding candidate has three parts. Get all three.

## Part 1: Per-query embedding cost

```
monthly_query_cost = (
    production_query_volume_per_month
    * avg_tokens_per_query
    * provider_$_per_million_tokens
    / 1_000_000
)
```

This is the part most cost sheets show. It is rarely the full cost.

## Part 2: Index-build cost (one-time + refresh)

When you change embedding models, the entire corpus must be re-embedded.

```
index_build_cost = (
    corpus_size_docs
    * avg_tokens_per_doc
    * provider_$_per_million_tokens
    / 1_000_000
)
```

Amortize over the refresh cadence. If the corpus refreshes weekly with 5% new documents:

```
monthly_index_refresh_cost = (
    0.05 * corpus_size_docs * 4_refreshes_per_month
    * avg_tokens_per_doc * provider_$_per_million_tokens
    / 1_000_000
)
```

For a 1M-document corpus with weekly 5% refresh and 500 tokens per doc at $0.13 per million tokens, this is ~$13/month — small. For a 100M-document corpus the same calculation gives ~$1300/month — not small.

## Part 3: Index storage cost

Vector index size in bytes:

```
index_size_bytes = corpus_size_docs * dim * bytes_per_float
```

- fp32: 4 bytes per float
- fp16: 2 bytes per float
- int8 quantized: 1 byte per float (with quality loss in cosine similarity ranking — measure)

For 80K documents:

- 768-dim fp32: 246 MB
- 1536-dim fp32: 492 MB
- 3072-dim fp32: 983 MB

The cost differential of holding 1 GB vs 250 MB in a managed vector DB (Pinecone, Weaviate, Qdrant Cloud) is real and recurring. Look up the actual pricing tier of your vector store at each candidate's dimensionality.

## Part 4: Latency budget contribution

Embedding latency adds to the user-perceived query latency:

```
total_query_latency = embedding_latency + retrieval_latency + reranker_latency + generation_latency
```

If the latency budget is 2 seconds end-to-end and the embedding model's p95 latency is 800 ms, only 1.2 seconds remain for retrieval + rerank + generation. Run the math; if the budget is busted, the candidate is out regardless of quality.

## Self-hosted candidates

For self-hosted models (e.g., `bge-large-en-v1.5` on a GPU), $/M tokens is:

```
$_per_M_tokens_self_hosted = (gpu_hourly_$ * 1_000_000) / (tokens_per_hour_throughput)
```

Measure `tokens_per_hour_throughput` on your actual hardware at production batch size. Vendor-claimed throughput is usually best-case; production traffic with variable batch sizes runs slower.

Add: storage, idle GPU cost (paying for a 24/7 GPU that processes traffic 8 hours/day means the effective $/token is 3x), and operational overhead (monitoring, restarts, model-update labor). For most teams, self-hosted is cheaper at high volume and more expensive at low volume — find the break-even.

## Reporting

Show all three parts in the comparison matrix separately. A candidate that wins on per-query cost but loses massively on index-storage cost should not be hidden under a single "monthly $" figure.
