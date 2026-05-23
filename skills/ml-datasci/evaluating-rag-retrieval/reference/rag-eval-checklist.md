# RAG eval checklist (report template)

Copy-paste this template; fill each section as the staged evaluation completes.

## 1. Golden set summary

- n questions: ___
- Intent-class coverage (compared to production traffic): ___
- Leakage check: ___ (corpus-overlap audit, training-set-overlap audit)
- Stability note: bootstrap CIs are wider when n < 100; below n = 50 treat as exploratory

## 2. Retrieval stage

Report each metric as `value [95% CI: low, high]` from 1000+ bootstrap resamples.

| Metric | Value | 95% CI |
|---|---|---|
| recall@1 | | |
| recall@3 | | |
| recall@5 | | |
| recall@10 | | |
| MRR | | |
| nDCG@10 | | |

Lead with the cutoff that matches the deployed top-k (e.g., if production uses top-5, recall@5 is the headline).

## 3. Generation stage (on retrieval HITS only)

Restricting to questions where retrieval succeeded prevents blaming the generator for a retrieval failure.

| Metric | Value | 95% CI | Judge model |
|---|---|---|---|
| Faithfulness | | | |
| Answer relevance | | | |
| Context utilization | | | |

If the same LLM is used for generation and judging, document the bias risk and re-run with an independent judge.

## 4. End-to-end correctness

`correct-answer-rate = value [95% CI: low, high]` on all golden questions (hits + misses).

## 5. Failure attribution

|                | Generation correct | Generation wrong |
|----------------|---|---|
| Retrieval hit  | n = ___ (___%) | n = ___ (___%) |
| Retrieval miss | n = ___ (___%) | n = ___ (___%) |

Dominant cell drives the next experiment.

## 6. Top failure exemplars

Pick at least 3 representative misses spanning the dominant attribution cells. For each:

- **Question:** verbatim
- **Gold doc(s):** id(s)
- **Retrieved top-k:** doc ids in rank order
- **Generated answer:** verbatim
- **Diagnosis:** which stage failed and why
- **Hypothesized fix:** one sentence

## 7. Recommended next experiment

Single highest-leverage change for the next iteration, with the expected metric delta and the cost-to-implement.
