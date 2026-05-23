# Golden Q-A set construction protocol

A RAG eval is only as honest as its golden set. These rules prevent the common construction mistakes.

## Composition rules

1. **Intent-class coverage matches production traffic.** Sample golden questions from a production-log distribution, not from what is convenient to label. If 60% of production queries are "policy lookups" and 10% are "comparison questions," the golden set should preserve that ratio.
2. **Multi-document gold sets are allowed.** `gold_doc_ids` is a set, not a single id. Some questions are answerable from any of several documents (e.g., a policy referenced in three locations).
3. **Adversarial slice.** Reserve at least 10% of the set for known-hard questions: paraphrased queries, queries that require multi-hop synthesis, queries that look easy but trigger near-duplicate-document confusion. Score this slice separately.
4. **Out-of-corpus questions.** Include a small slice of questions whose answer is NOT in the corpus. The system should refuse to answer or escalate, not hallucinate. Score refusal correctness, not answer correctness, on this slice.

## Leakage audits

Run these BEFORE the first metric is computed.

### Corpus overlap

For each golden question, check whether the question text appears verbatim (or near-verbatim) in any indexed corpus document. If it does, the retriever can win trivially by lexical match; the metric will not generalize.

### Training-set overlap

If the embedding model or generation LLM was fine-tuned on a corpus derived from your production data, the golden Q-A pairs may have been seen during training. Audit by checking timestamps (the golden set must post-date the model's training-data cutoff) or by holding out a slice of newly-collected questions for the final report.

### Annotator drift

If the golden set was built by multiple annotators, compute inter-annotator agreement (Cohen's κ on gold-doc-id labeling for a shared subsample). Below κ = 0.6, the gold labels themselves are unreliable; address before scoring.

## Size guidance

| n questions | Recommendation |
|---|---|
| < 50 | Treat as exploratory; report metrics but do not gate deployment on them |
| 50–150 | Standard eval; bootstrap CIs are usable |
| 150–500 | Robust eval; can detect ~5% metric deltas between systems |
| 500+ | Production-grade; can detect smaller deltas, supports subgroup analysis |

## Refresh cadence

The golden set is a living artifact. Refresh quarterly (or whenever the production query distribution shifts noticeably). Keep older versions as snapshots so longitudinal comparisons remain meaningful.
