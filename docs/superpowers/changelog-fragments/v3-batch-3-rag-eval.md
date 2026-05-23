### v3-batch-3: RAG eval — 2026-05-23

Skills shipped:
- `ml-datasci/evaluating-rag-retrieval` v0.1.0 — staged RAG eval separating retrieval-stage metrics (recall@k / MRR / nDCG@k against gold doc ids) from generation-stage metrics (faithfulness / answer relevance / context utilization scored on retrieval hits only) plus the retrieval-vs-generation failure-attribution 2x2; refuses single aggregate scores that conflate the two stages (Σ 14, status: shipped)
- `ml-datasci/selecting-embedding-model` v0.1.0 — three-axis embedding-model comparison (intrinsic Spearman on domain-labeled pairs + extrinsic retrieval metrics on a golden Q-A set + operational cost including per-query, index-build amortization, latency, max-input-tokens, and dimensionality-driven index size) with bootstrap-CI tie-detection and operational tiebreaker; refuses recommendations from MTEB / BEIR leaderboards alone (Σ 13, status: shipped)
- `ml-datasci/profiling-llm-cost` v0.1.0 — per-call → per-task → per-cohort LLM cost rollup from a logged trace (input / cached_input / output tokens × pricing snapshot) with cache-hit-rate trend, attribution slices, baseline-window delta, top-3 drivers, and recommendations ranked by $ saved per engineering hour; refuses cost-cutting actions without a measured baseline (Σ 14, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 dispatches (3 scenarios × 3 skills); all scored 3/3 against intent (27/27 rubric items pass). Full 3-model (Haiku / Sonnet / Opus) validation deferred to a future re-run.

Notes: No deviations or calibration corrections. All three skills retained `status: shipped` after eval validation. Cross-references between the three skills (evaluating-rag-retrieval ↔ selecting-embedding-model ↔ profiling-llm-cost) form a coherent RAG-system evaluation cluster covering quality of the assembled pipeline, quality + cost of the retriever's embedding component, and cost of the generator side.
