# Comparison matrix (report template)

Copy-paste this template; fill each section as the staged comparison progresses.

## 1. Candidates

| Name | Provider | Dim | Max input tokens | $/M tokens (input) | Cold-start latency p95 | Notes |
|---|---|---|---|---|---|---|

## 2. Intrinsic results (labeled-pair similarity correlation)

Labeled set: n pairs = ___, inter-annotator Cohen's κ = ___, domain = ___

| Candidate | Spearman | 95% CI |
|---|---|---|

## 3. Extrinsic results (retrieval on golden Q-A set)

Golden set: n questions = ___, source = ___, leakage check = ___

| Candidate | recall@1 | recall@5 | recall@10 | MRR | nDCG@10 |
|---|---|---|---|---|---|

Each cell: `value [95% CI: low, high]` from 1000+ bootstrap resamples.

## 4. Operational results

Production query volume estimate: ___ queries/month, average tokens per query: ___, corpus size: ___ docs, average tokens per doc: ___.

| Candidate | Monthly $ (queries) | Index build $ (one-time) | Index size (GB) | Latency p95 (steady) | Latency p95 (cold) |
|---|---|---|---|---|---|

## 5. Recommendation

| Candidate | Quality verdict | Cost verdict | Operational fit | Overall |
|---|---|---|---|---|

**Recommended:** ___

**Runner-up:** ___

**Trade-off rationale (single paragraph):** ___

**Revisit triggers:** corpus grows past ___; multilingual support added; latency budget shrinks below ___; new candidate available.
