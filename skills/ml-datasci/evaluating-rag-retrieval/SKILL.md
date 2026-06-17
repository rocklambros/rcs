---
name: evaluating-rag-retrieval
description: >
  Produces a complete evaluation report for a Retrieval-Augmented Generation
  (RAG) system from a golden Question-Answer set, separating retrieval-stage
  metrics (recall@k, MRR, nDCG@k) from generation-stage metrics (faithfulness,
  answer relevance, context utilization). Triggers whenever a RAG pipeline
  needs scoring, whenever the user reports the RAG "feels worse than direct
  LLM" but cannot localize where, whenever retrieval-vs-generation failure
  attribution is needed, or whenever a chunking or embedding-model change is
  being evaluated. Refuses to report a single aggregate score that conflates
  retrieval and generation failures.
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
  - email-spam-classifier-naive-bayes-comparisson-roc
last-updated: 2026-05-23
---

# Evaluating RAG Retrieval

## When to use

Trigger this skill when:

- A RAG pipeline (retrieval over an indexed corpus plus LLM generation grounded in retrieved chunks) needs to be scored end-to-end
- The user reports "the RAG system feels worse than asking the LLM directly" but cannot localize whether retrieval or generation is the failing stage
- A chunking-strategy change, embedding-model swap, reranker addition, or top-k change needs A/B comparison on a held-out set
- Keywords appear: recall@k, MRR, nDCG, faithfulness, answer relevance, golden Q-A, hit rate, context precision, RAGAS, retrieval evaluation
- The user reports good retrieval (correct chunks in top-k) but the generated answer is wrong, or vice versa
- A regression-test set for the RAG system is being designed before deployment

## When NOT to use

Skip this skill and hand off when:

- The system is a pure LLM call with no retrieval over an external corpus — there are no retrieval metrics to compute; use a direct LLM-eval skill instead
- The task is classification or regression scored on `y_true` / `y_pred` arrays → use `ml-datasci/evaluating-binary-classifiers` or `ml-datasci/evaluating-regression-models`
- The user wants to pick an embedding model in isolation (independent of an end-to-end pipeline) → use `ml-datasci/selecting-embedding-model`
- The corpus has no ground-truth Question-Answer pairs and the user is unwilling to build one — explain that evaluation requires labels and recommend the golden-set construction step before scoring
- The task is auditing retrieval-only ranking on a TREC-style benchmark without a generation stage → use a pure information-retrieval evaluation skill (planned)

## Quick start

User: *"Our RAG system answers customer-support questions over 10K product docs. We have 150 golden Question-Answer pairs with the correct doc id for each. Evaluate the pipeline end-to-end."*

Response: run the staged report — **retrieval first** (recall@k, MRR, nDCG@k against the labeled correct doc ids), **then generation** (faithfulness, answer relevance, context utilization on the LLM output given the retrieved chunks), **then end-to-end** (correct-answer rate on the full pipeline). Failure-attribution table separates retrieval misses from generation misses.

```python
from sklearn.metrics import ndcg_score
import numpy as np

# 1. Retrieval-stage metrics (per question)
def recall_at_k(retrieved_ids, gold_ids, k):
    top_k = set(retrieved_ids[:k])
    return len(top_k & set(gold_ids)) / len(gold_ids)

def reciprocal_rank(retrieved_ids, gold_ids):
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in gold_ids:
            return 1.0 / rank
    return 0.0
```

See `reference/rag-eval-checklist.md` for the full report template, `reference/golden-qa-construction.md` for golden-set rules, and `reference/failure-attribution-matrix.md` for the retrieval-vs-generation diagnostic table.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `golden_qa_set` | list of `{question, gold_doc_ids, gold_answer}` | yes | — | Held-out Q-A pairs. Each item carries the question, the set of doc ids that should be retrieved to answer correctly, and a reference answer for generation scoring. |
| `retrieved_per_question` | list of `[doc_id]` ranked lists | yes | — | What the retriever actually returned, in rank order, per golden question. Length per question ≥ `max_k`. |
| `generated_answers` | list of strings | yes | — | What the generation stage produced, one per golden question, given the retrieved context. |
| `retrieved_chunks_per_question` | list of `[chunk_text]` | yes | — | The actual chunk text used as LLM context per golden question. Needed for faithfulness scoring. |
| `k_values` | list of int | no | `[1, 3, 5, 10]` | Top-k cutoffs for recall@k and nDCG@k. |
| `judge_model` | string | no | `"sonnet-4-6"` | LLM judge model for faithfulness and answer-relevance scoring. Pin and document. |
| `n_bootstrap` | int | no | `1000` | Bootstrap resamples for 95% CI on each metric. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off as the evaluation progresses:

```
RAG eval progress:
- [ ] 0. Sanity checks (golden set ≥ 50 questions; gold_doc_ids non-empty per Q; retrieved length ≥ max(k_values))
- [ ] 1. Golden-set audit (coverage of intent classes, no train-set leakage into the golden Qs)
- [ ] 2. Retrieval-stage metrics: recall@k for k in k_values, MRR, nDCG@k — each with bootstrap 95% CI
- [ ] 3. Per-question retrieval verdict: hit (gold in top-k) vs miss
- [ ] 4. Generation-stage metrics on questions where retrieval HIT: faithfulness, answer relevance, context utilization
- [ ] 5. End-to-end correctness: judge-model verdict on (generated_answer vs gold_answer) per question
- [ ] 6. Failure attribution: 2x2 table of {retrieval-hit, retrieval-miss} x {generation-correct, generation-wrong}
- [ ] 7. Report block: per-stage metrics, attribution table, top failure modes, recommended next experiment
```

### Step 1: Golden-set audit (do this BEFORE scoring)

Verify the golden Q-A set before computing any metric:

- **Coverage:** the question distribution should reflect production traffic. If 60% of real queries are "policy lookups" but only 5% of golden Qs are, the eval underweights what matters
- **No-leakage:** no golden question can have appeared in the retrieval training corpus or in the LLM's fine-tune data (when applicable)
- **Multi-answer awareness:** some questions have multiple valid gold documents — `gold_doc_ids` is a set, not a single id
- **Size:** ≥ 50 Q-A pairs is the practical floor for stable bootstrap CIs at the dataset level. Below that, report the metrics but treat conclusions as exploratory

See `reference/golden-qa-construction.md` for the construction protocol.

### Step 2: Retrieval-stage metrics

Compute and report each with a bootstrap 95% CI (resample the golden questions, recompute the metric, repeat ≥ 1000 times):

- **recall@k** for `k ∈ {1, 3, 5, 10}` (or user-specified): fraction of `gold_doc_ids` recovered in the top-k retrieved
- **MRR (Mean Reciprocal Rank):** mean of `1/rank` of the first gold doc id in the retrieved list (0 if not retrieved)
- **nDCG@k:** rank-weighted gain at cutoff k (use `sklearn.metrics.ndcg_score` or compute from gain vector)

Place recall@k first when the system retrieves a small number of chunks (k ≤ 5); place nDCG@k first when the system retrieves a larger list and rank position matters.

### Step 3: Per-question retrieval verdict

For each golden question, label `retrieval_hit` (any gold doc in top-k) or `retrieval_miss`. This partitions the rest of the evaluation.

### Step 4: Generation-stage metrics (on retrieval HITS only)

Generation can only be fairly scored when the retrieval gave the LLM the right context. Use the LLM judge (or a sentence-similarity scorer for faithfulness) on questions where retrieval succeeded:

- **Faithfulness:** does every factual claim in `generated_answer` derive from `retrieved_chunks`? Score 0-1, judge-model verdict
- **Answer relevance:** does the answer address the question (vs. tangential restatement of context)? Score 0-1
- **Context utilization:** what fraction of cited chunks was actually used (no padding, no irrelevant chunks dominating)?

Always pin and document the judge model. See `reference/judge-prompts.md`.

### Step 5: End-to-end correctness

For every golden question (hit and miss), judge the `generated_answer` against `gold_answer`. Report end-to-end correct-answer rate with bootstrap 95% CI.

### Step 6: Failure attribution

Build the 2x2 attribution table:

|                | Generation correct | Generation wrong |
|----------------|---|---|
| Retrieval hit  | Working as intended | **Generation failure** — chunks were there, LLM failed to use them |
| Retrieval miss | Lucky | **Retrieval failure** — fix the retriever first |

The mix dictates the next experiment:

- Retrieval-failure dominant → tune chunking, switch embedding model, add reranker, increase k
- Generation-failure dominant → tune prompt, switch generation model, add citation requirement, prune context
- Both substantial → fix retrieval first (cheap fixes available); generation issues often dissolve once context arrives

### Step 7: Report block

Include in every report:

1. Golden-set stats (n, intent coverage, leakage verdict)
2. Retrieval metrics with CIs
3. Generation metrics with CIs (on hits only)
4. End-to-end correctness with CI
5. Attribution table
6. Top 3 failure cases (question + retrieved + generated + diagnosis)
7. Recommended next experiment

## Outputs

A markdown report with:

1. **Golden set summary** — n questions, intent coverage, leakage verdict
2. **Retrieval stage** — recall@{1,3,5,10}, MRR, nDCG@10 — each `metric = value [95% CI: low, high]`
3. **Generation stage (on retrieval hits)** — faithfulness, answer relevance, context utilization — same CI format
4. **End-to-end correctness** — `value [95% CI: low, high]`
5. **Failure attribution table** — the 2x2 with counts and percentages
6. **Top failure exemplars** — at least 3 worked examples diagnosing the failing stage
7. **Recommended next experiment** — single highest-leverage change for the next iteration

## Failure modes

Known anti-patterns and how this skill catches them:

- **Single aggregate score (e.g., "RAG accuracy = 0.62") conflating retrieval and generation** — caught by mandatory stage separation in steps 2 and 4
- **Scoring generation on retrieval misses** — caught by step 4 restricting generation metrics to retrieval hits, so a bad retriever does not get blamed for a bad generator and vice versa
- **Using the LLM that generates the answer as its own judge for faithfulness** — caught in `reference/judge-prompts.md`; use an independent judge, pin the model, document the choice
- **Golden set too small for meaningful CIs (< 50 questions)** — caught by step 1; flagged but evaluation proceeds with a "treat as exploratory" caveat
- **Golden set leaks into retrieval corpus** — caught by step 1 leakage check; common when the golden set was sampled from production logs that also feed the corpus
- **No CI on metrics** — caught by mandatory bootstrap CI on every reported value; point estimates alone hide variance
- **Ignoring intent-class coverage** — caught by step 1; a golden set skewed toward easy lookups will inflate end-to-end correctness compared to production
- **Forgetting that "good retrieval" requires picking k** — recall@1 and recall@10 are different metrics; report at multiple k values to expose rank quality vs. raw hit rate

## References

- `reference/rag-eval-checklist.md` — copy-paste end-to-end report template
- `reference/golden-qa-construction.md` — building the labeled Q-A set without leakage
- `reference/failure-attribution-matrix.md` — the 2x2 retrieval-vs-generation diagnostic
- `reference/judge-prompts.md` — independent-judge prompt patterns for faithfulness and answer relevance
- [Saad-Falcon et al. 2024, *ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation*, NAACL](https://aclanthology.org/2024.naacl-long.20/) — automated RAG eval framework underpinning faithfulness/relevance scoring
- [RAGAS documentation](https://docs.ragas.io/) — open-source RAG-eval library implementing the metric family

## Examples

### Example 1: Customer-support RAG over 10K product docs (happy-path)

Input: *"Our RAG answers customer-support questions over 10K product docs. We have 150 golden Q-A pairs with the correct doc id for each. Evaluate the pipeline."*

Output: Skill performs the staged report — golden-set audit, then retrieval metrics (`recall@1`, `recall@5`, `MRR`, `nDCG@10` each with bootstrap 95% CI), then generation metrics on retrieval hits (faithfulness, answer relevance, context utilization), then end-to-end correct-answer rate, then the failure-attribution 2x2. Recommends the next experiment based on which cell dominates the misses.

### Example 2: Retrieval right, generation wrong (edge-case)

Input: *"Our RAG retrieves the correct doc in the top-3 for 90% of golden questions, but the final answer is wrong 40% of the time. What's going on?"*

Output: Skill computes the attribution table; identifies the *retrieval-hit / generation-wrong* cell as dominant. Walks the generation diagnostic checklist (prompt instructing the LLM to ground in chunks? citation requirement? context length blowing past the prompt limit? hallucinated extrapolation past the chunk?). Recommends prompt-tuning or generation-model swap before tuning the retriever.

### Example 3: No retrieval present (anti-trigger)

Input: *"I'm using GPT-4 to answer customer support questions directly from its training data — no document store, no retrieval. Evaluate it like a RAG."*

Output: Skill identifies the request as not a RAG (no retrieval stage exists; no chunks, no doc ids, no top-k). Refuses to compute recall@k or MRR. Recommends a pure LLM-evaluation skill (or describes how to evaluate a direct-LLM QA system with answer-correctness + faithfulness-against-source if a source is later added).

## See also

- `ml-datasci/selecting-embedding-model` — the upstream skill for picking the retriever's encoder before this end-to-end eval
- `ml-datasci/profiling-llm-cost` — sibling for measuring the cost side of the RAG pipeline (this skill measures quality)
- `ml-datasci/evaluating-binary-classifiers` — sibling pattern for non-RAG classifier evaluation (similar staged-report discipline)
- `ml-datasci/auditing-train-test-split` — required pre-step ensuring the golden set is not contaminated by the retrieval corpus or LLM fine-tune data
- `workflow/pre-registering-eval-study` — required pre-step locking the golden-set composition and stopping rule before running comparisons

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-3, skill 1) via PRAGMATIC discipline
