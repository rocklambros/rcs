# Failure attribution matrix

The 2x2 that turns "the RAG is bad" into a specific, actionable diagnosis.

## The table

|                | Generation correct | Generation wrong |
|----------------|---|---|
| Retrieval hit  | **A — working** | **B — generation failure** |
| Retrieval miss | **C — lucky guess** | **D — retrieval failure** |

Definitions:

- **Retrieval hit:** at least one document from `gold_doc_ids` is present in the top-k retrieved
- **Generation correct:** judge-model verdict pass on the generated answer compared against the gold answer

## What each cell means

### A. Retrieval hit + generation correct (the goal)

System working as intended. The numerator of correct-answer-rate.

### B. Retrieval hit + generation wrong (generation failure)

The retriever surfaced the right chunks. The LLM had them in context. The answer was still wrong.

Common causes:
- Prompt does not instruct grounding in the retrieved context
- Generation LLM extrapolates beyond the chunks (hallucinated synthesis)
- Context window overflowed; the chunks were truncated before the LLM saw them
- Generation LLM ignored a chunk because it was buried mid-context (lost-in-the-middle)
- Chunk text contains contradictory information the LLM averaged into a hedged wrong answer

Diagnostic actions:
- Audit the prompt for an explicit "answer using only the provided context" instruction
- Add citation requirement; track citations per chunk
- Measure context-window utilization; if generations consistently appear past the model's recall sweet spot, reduce top-k or use a stronger model
- Re-rank retrieved chunks so the most-relevant is first

### C. Retrieval miss + generation correct (lucky guess)

The retriever failed but the LLM happened to know the answer from its parametric memory. Looks like a win on aggregate accuracy but is fragile:

- The same query on a slightly different LLM will fail
- For domains where the corpus is the source of truth (policies, recent product docs), this masks a retrieval bug that will surface the moment the LLM has stale knowledge

Treat this cell as a latent failure, not a success.

### D. Retrieval miss + generation wrong (retrieval failure)

The clear path: fix the retriever first.

Diagnostic actions:
- Inspect what was retrieved. Was the right doc in the corpus at all? (indexing bug vs. ranking bug)
- Compare query embedding to gold-doc embedding cosine similarity. Far apart → embedding model is wrong domain. Close but not top-k → reranker or top-k bump
- Audit chunking strategy. If gold answer spans chunk boundaries, the right chunk may not exist
- Add hybrid retrieval (BM25 + dense) when dense alone struggles on rare-term queries

## Mix-driven next experiment

| Dominant cell | Likely highest-leverage fix |
|---|---|
| B (gen failure) | Prompt tuning, citation requirement, lost-in-the-middle mitigation, model upgrade |
| D (retrieval failure) | Embedding-model swap, chunk-size sweep, reranker, top-k bump, hybrid retrieval |
| Mixed B + D | Fix retrieval first — many "generation failures" turn out to be context-quality failures that vanish once retrieval improves |
| C significant | Investigate why parametric memory is doing the retriever's job; corpus might be too small, too stale, or wrong-domain |

## Reporting note

Always report the full 2x2 with counts and percentages, not just the dominant cell. Stakeholders need to see the *mix* to weigh fixes against deployment risk.
