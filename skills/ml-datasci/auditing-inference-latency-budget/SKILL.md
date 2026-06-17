---
name: auditing-inference-latency-budget
description: >
  Audits the inference-latency budget for a deployed ML model against a stated
  SLO — measures P50, P95, and P99 latency end-to-end and per-stage
  (tokenization or feature lookup, preprocessing, model forward, postprocessing,
  serialization), attributes the tail to the dominant per-stage contributor,
  and recommends ranked optimizations by latency-saved-per-engineering-hour.
  Triggers whenever a real-time inference service is breaching or about to
  breach its P95 / P99 SLO, whenever latency tail behavior is unexplained,
  whenever an input-shape distribution change is suspected of inflating the
  tail, or whenever pre-launch SLO sizing must be derived from a measured
  profile. Refuses to recommend optimizations without measured per-stage
  attribution and refuses to engage on batch / offline workloads where
  latency SLO does not apply (throughput optimization is the right skill).
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - ml-engineer
  - data-scientist
  - devops
evidence:
  - multiturn-injection-detection
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Auditing Inference Latency Budget

## When to use

Trigger this skill when:

- A real-time inference service (chatbot, recommender, fraud-scoring API, real-time RAG, online classification) is breaching or close to breaching its P95 or P99 SLO
- The latency tail (P99 / max) looks unexplained — typical requests are fast but a few are very slow
- An input-shape or context-length distribution change is suspected of inflating the tail (e.g., a new use case sends 10x longer inputs than the baseline)
- A pre-launch SLO sizing exercise needs a measured per-stage breakdown to confirm the proposed SLO is realistic on the chosen architecture
- The user reports "the model is slow", "P99 is breaching", "we're seeing timeouts", "cold-start is killing us", "the long tail is unexplained"
- A capacity / cost planning task needs latency vs. batch-size vs. quality trade-offs measured before scaling

## When NOT to use

Skip this skill and hand off when:

- The workload is batch / offline / nightly — latency SLOs do not apply; the right analysis is throughput, $ per million records, and end-to-end wall-clock budget, none of which are this skill's focus
- The concern is LLM API spend ($ per million tokens, cache-hit rate) — use `ml-datasci/profiling-llm-cost`
- The concern is model quality (accuracy, calibration, drift) — use the appropriate eval / drift skill; this skill scopes latency only
- The system is a one-shot prototype with no SLO and no users to disappoint
- The cause is known and trivial (e.g., the operator already knows it is a network hop or a database query) — go fix that
- The system is research-grade with no production traffic shape to profile

## Quick start

User: *"Our real-time fraud-scoring API has a 200ms P99 SLO. We're breaching at 480ms P99 in production. Mean and P50 look fine (~80ms). Help me find the cause."*

Response: P50 fine + P99 blown is the signature of input-shape variance or per-request contention, not steady-state slowness. Capture a representative sample of slow (P95-P99) and fast (P50) requests with full per-stage timing. Decompose per-stage latency for both groups; the stage with the largest absolute slow-minus-fast delta is the tail driver. Common patterns: long input sequences hitting an O(n²) attention layer, a feature-store cache miss forcing a slow path, cold-start of a low-traffic model variant, a tail-end retrieval call to an external service. Recommend the highest-leverage fix ranked by latency-saved-per-engineering-hour with quality-impact noted.

```python
import time
from contextlib import contextmanager

@contextmanager
def stage_timer(record, stage_name):
    t0 = time.perf_counter_ns()
    yield
    record[stage_name + "_ms"] = (time.perf_counter_ns() - t0) / 1_000_000

# Per-request:
record = {}
with stage_timer(record, "tokenize"):
    tokens = tokenizer.encode(text)
with stage_timer(record, "feature_lookup"):
    features = store.fetch(user_id)
with stage_timer(record, "model_forward"):
    logits = model(tokens, features)
with stage_timer(record, "postprocess"):
    out = postprocess(logits)
record["total_ms"] = sum(v for k, v in record.items() if k.endswith("_ms"))
```

See `reference/latency-decomposition.md` for the per-stage decomposition recipe and common-cause table, `reference/tail-analysis.md` for input-shape-variance and cold-start tail-driver isolation, and `reference/slo-and-budget.md` for the SLO-construction discipline.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `latency_log` | DataFrame / parquet / SQL | yes | — | Per-request timing records: `request_id`, `timestamp`, per-stage `*_ms` columns, `total_ms`, and the input-shape covariates (sequence length, batch size, number of features). |
| `slo_target` | dict | yes | — | The SLO contract: `{p50_ms, p95_ms, p99_ms, error_budget_pct}`. Drives breach detection and budget allocation. |
| `slow_request_threshold` | string ("p95", "p99", "ms") | no | "p95" | Defines "slow" for the tail-vs-fast comparison. |
| `input_shape_dims` | list of column names | no | none | Covariates that may explain tail (sequence_length, n_tools, batch_size, retrieval_doc_count). Drives shape-vs-latency analysis. |
| `cohort_dims` | list of column names | no | none | Per-cohort latency split (route, model_variant, customer_tier, region). |
| `cold_start_window_min` | integer | no | 5 | Minutes after a deploy / scale-up event during which "cold-start" latency is excluded from steady-state SLO assessment. |
| `compare_to_baseline` | bool | no | false | If a prior latency log exists, run regression check vs. that baseline. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

```
Latency-budget audit progress:
- [ ] 0. Confirm scope: real-time workload, SLO exists, latency log exists with per-stage breakdown OR can be instrumented
- [ ] 1. End-to-end snapshot: P50 / P95 / P99 / max on total_ms; verdict vs slo_target
- [ ] 2. Per-stage P50 / P95 / P99: which stage contributes most to each percentile?
- [ ] 3. Slow-vs-fast comparison: pull P95-P99 slow group and P40-P50 fast group; per-stage delta; identify the tail driver
- [ ] 4. Input-shape correlation: regress per-stage latency on input_shape_dims (sequence length, batch size, retrieval count); large R² on one dim flags it
- [ ] 5. Cohort split: per-route / per-variant / per-region latency table; surface cohorts whose P99 is dramatically worse than the global P99
- [ ] 6. Cold-start filter: exclude requests within cold_start_window_min of a scale-up event; re-run P99; if filtered P99 is in SLO and unfiltered is not, cold-start is the issue
- [ ] 7. Tail-cause hypothesis: tail driver classified as input-shape variance / cold-start / contention (noisy neighbor) / external dependency / cache miss / fanout depth
- [ ] 8. Optimization ranking: candidate fixes ranked by (ms saved at P99) / (engineering hours), with quality-impact note for each
- [ ] 9. Capacity / SLO recommendation: if the tail cannot be optimized, propose a tighter SLO or more capacity
```

### Step 1: End-to-end snapshot

Compute P50, P95, P99, and max on `total_ms`. Compare each to `slo_target`. A common reporting mistake is leading with the mean — production SLOs are almost always P-percentile based, and mean is dominated by the long tail in a misleading direction.

| Percentile | Measured | SLO | Headroom | Status |
|---|---|---|---|---|
| P50 | 78 ms | 100 ms | +22 ms | green |
| P95 | 165 ms | 180 ms | +15 ms | green |
| P99 | 480 ms | 200 ms | -280 ms | breach |
| max | 2,840 ms | (informational) | — | tail |

### Step 2: Per-stage P50 / P95 / P99

For each instrumented stage, report its P50 / P95 / P99. A stage with a stable P50 and a blown P99 is a tail-only contributor — likely input-shape-variance or contention-driven. A stage with a uniformly slow distribution is a steady-state bottleneck.

### Step 3: Slow-vs-fast comparison

Pull two groups:

- **Fast group**: requests with `total_ms` in [P40, P50] of the distribution
- **Slow group**: requests with `total_ms` in [P95, P99] of the distribution

For each stage, compute `mean_slow - mean_fast`. The stage with the largest absolute delta is the tail driver. This is the cheapest, highest-signal diagnostic.

### Step 4: Input-shape correlation

Regress per-stage latency on `input_shape_dims`. Large R² on a single dimension is the tail driver. For example:

- Tokenization regressed on `sequence_length`: R² = 0.98 → tokenization is sequence-length-bound (expected)
- Model forward regressed on `sequence_length`: R² = 0.91, slope = 0.4 ms/token → forward pass is O(n) in length; for sequences > 1k tokens, the tail is here
- Feature lookup regressed on `n_users_in_batch`: R² = 0.62 → batching is contention-driven

A scatter plot of latency vs. shape often reveals the shape of the tail driver more clearly than the R² alone.

### Step 6: Cold-start filter

Cold-start latency is a real production problem but it is a separate problem from steady-state SLO breach. Always report both:

- Unfiltered P99: includes cold-start
- Filtered P99 (excluding requests within cold_start_window_min of a scale-up event): steady-state only

If filtered P99 is within SLO and unfiltered is not, cold-start is the issue and the fix is in capacity planning (pre-warming, larger min-replica count) not model optimization.

### Step 7: Tail-cause hypothesis menu

Classify the tail driver into one (or more) of:

- **Input-shape variance** — long sequences, large batch sizes, deep retrieval fanout. Fix: cap input length; route long requests to a slower-but-larger tier; chunk and parallelize
- **Cold-start** — model load time + first-token autoregressive warmup. Fix: keep-warm replicas; pre-load; serverless cold-start mitigations
- **Contention / noisy neighbor** — shared GPU, shared CPU, shared network. Fix: dedicated capacity for SLO-bound routes; QoS isolation
- **External dependency** — feature-store lookup, vector DB, third-party API. Fix: caching, batched lookups, async prefetch where possible
- **Cache miss** — embedding cache, KV cache, feature cache. Fix: pre-warm; smarter TTL; LRU sizing
- **Fanout depth** — agentic chain with many tool calls. Fix: parallelize independent steps; cap depth; fail-fast on slow tools

Refuse to recommend a fix without naming the hypothesis. "Add a cache" without measurement adds a cache where one is not needed and leaves the real tail driver in place.

### Step 8: Optimization ranking

Each candidate fix gets:

- Estimated P99 ms saved (from the slow-vs-fast delta or input-shape regression)
- Engineering hours to implement
- Quality / behavior risk (e.g., truncating long sequences may degrade output quality; cache pre-warming is risk-free)
- Reversibility (can we roll back if it breaks something?)

Sort by `(ms saved) / (engineering hours)`, highest first. Name the single highest-leverage fix first.

## Outputs

A markdown report with:

1. **Workload provenance** — service name, SLO contract, latency-log window, n requests
2. **End-to-end snapshot** — P50 / P95 / P99 / max vs. SLO with status per percentile
3. **Per-stage table** — stage · P50 · P95 · P99 · % contribution to P99
4. **Slow-vs-fast diff** — per-stage `mean_slow - mean_fast`; tail-driver identification
5. **Input-shape correlation** — R² + slope per (stage, covariate) pair; flag dominant drivers
6. **Cohort split** (if `cohort_dims`) — per-cohort P99 with deltas from global P99
7. **Cold-start verdict** — filtered vs. unfiltered P99
8. **Tail-cause hypothesis** — one (or more) of input-shape / cold-start / contention / dependency / cache / fanout
9. **Optimization ranking** — ranked candidates; highest leverage first with quality / risk notes
10. **SLO / capacity recommendation** — fix the tail OR re-negotiate the SLO; explicit choice

## Failure modes

Known anti-patterns and how this skill catches them:

- **Leading with mean latency** — caught by step 1 reporting P50 / P95 / P99 / max; mean is misleading for SLO assessment
- **Optimizing the model forward pass when the tail is in feature lookup** — caught by step 2 per-stage breakdown; the dominant stage is rarely the assumed stage
- **"Add a cache" without measuring the cache-miss-rate tail contribution** — caught by step 7 hypothesis classification requiring the cache-miss path to be measured first
- **Treating cold-start latency as steady-state breach** — caught by step 6 cold-start filter; pre-warming vs. model optimization are different fixes for different problems
- **Reporting only global P99 when one cohort is dragging the tail** — caught by step 5 cohort split; a 10x slower P99 in one route can move global P99 by 50% with only 5% of traffic
- **Recommending a fix without quality impact** — caught by step 8 mandatory quality / risk note; truncation, lower-precision quantization, smaller models all save latency at quality cost
- **Optimizing for P99 when the SLO is on mean** — caught by step 1 reading the SLO contract; the right percentile is whatever the SLO says
- **Ignoring input-shape variance because "most requests are normal"** — caught by step 4 input-shape regression; a 1% rate of 10x-longer requests can dominate P99
- **Conflating one-time deploy hiccups with persistent breach** — caught by step 0 scope confirmation; an incident from yesterday is not a budget audit, it is a postmortem

## References

- `reference/latency-decomposition.md` — per-stage decomposition recipe and common-cause table
- `reference/tail-analysis.md` — input-shape-variance, cold-start, and contention isolation patterns
- `reference/slo-and-budget.md` — SLO construction discipline (percentile choice, error budget, multi-tier routing)
- [Tail at Scale, Dean and Barroso, Communications of the ACM 2013](https://research.google/pubs/the-tail-at-scale/) — origin of tail-latency thinking for distributed systems
- [Latency Lingo: A Taxonomy of Tail Latency Behavior, Lo et al. 2014](https://www.usenix.org/system/files/conference/atc14/atc14-paper-lo.pdf) — categorizes tail-latency causes
- [vLLM Serving documentation, Continuous Batching](https://docs.vllm.ai/) — practical reference for LLM-serving latency-vs-throughput trade-offs

## Examples

### Example 1: Real-time fraud-scoring API breaching P99 SLO (happy-path)

Input: *"Our fraud-scoring API has a 200ms P99 SLO. We're at 480ms P99 in production. Mean and P50 look fine (~80ms). The model is the same one we trained 3 months ago. Help me find the cause."*

Output: Skill walks the 9-step workflow. Confirms steady-state breach (P50 healthy, P99 blown — classic tail-driver case). Per-stage breakdown shows feature_lookup P99 = 280ms while feature_lookup P50 = 6ms — a 47x ratio. Slow-vs-fast comparison confirms feature_lookup is the tail driver. Input-shape regression on `n_users_in_batch` produces R² = 0.71 on feature_lookup — batch-size variance is implicated. Cohort split reveals the `bulk-merchant-onboarding` route is 92% of the slow group despite being 8% of total traffic, and it submits 200-row batches vs. the typical 1-row request. Tail-cause: input-shape variance (large batch) hitting an unbatched feature-store path. Optimization ranking: (a) implement batched feature-store fetch (~3 days, ~250ms P99 reduction, low quality risk), (b) route bulk-merchant traffic to a dedicated tier (~1 day, removes contention, no model change), (c) cap batch size at 50 with client-side chunking (~half a day, ~150ms P99 reduction, no quality impact). Names (a) as the highest-leverage long-term fix and (b) as the fastest short-term mitigation.

### Example 2: Input-shape variance hiding in average request size (edge-case)

Input: *"Our LLM-based document classifier P99 is 4.2s against a 1.5s SLO. We've already tried switching to a faster model and the breach is unchanged. We can't figure out why some requests are so slow when our average input is only 500 tokens."*

Output: Skill identifies the symptom (mean OK, P99 blown, model swap did not help) as consistent with input-shape variance, not steady-state slowness. Recommends step 4 input-shape regression. Likely finding: a long-tail distribution of input lengths where 95% of requests are <1k tokens but 1% are >50k tokens, and those few drive the P99. Recommends: (a) measure the input-length distribution (histogram + p50 / p95 / p99 of `sequence_length`); (b) compute per-token latency for the model — if it's O(n) the P99 reflects the longest inputs; (c) options to fix: route long inputs to a separate slower tier with a different SLO, chunk and parallelize, or cap input length with truncation (note quality impact). Explicitly names that switching models did not help because the bottleneck is sequence length, which a different model of the same family also pays. Refuses to declare the fix without measuring the input-length distribution first.

### Example 3: Nightly batch job (anti-trigger)

Input: *"Our nightly batch model run is taking 6 hours and we want it to be faster. Can you audit its latency?"*

Output: Skill identifies this as a batch / offline workload, not a real-time latency-SLO context. Explains the difference: batch jobs are throughput-bound and wall-clock-bound, not per-request-percentile-bound; the right analysis is total wall-clock vs. budget, throughput (records/sec), $-per-record, and parallelism utilization. Per-request percentile analysis is irrelevant — there is no user waiting on each record. Hands off the right analysis: profile the batch job stage-by-stage for wall-clock attribution, measure throughput on different batch sizes, evaluate whether the bottleneck is I/O, CPU, GPU, or shuffling. Notes that this skill's latency framework can still be useful as a *technique* if applied to per-stage wall-clock attribution, but the SLO framing and percentile-of-the-request distribution are inapplicable. Does NOT force a latency budget onto a batch job.

## See also

- `ml-datasci/monitoring-data-drift` — sibling for input-side distribution drift; data drift can change input-shape distribution and indirectly inflate the latency tail
- `ml-datasci/monitoring-prediction-drift` — sibling for prediction-side quality drift; latency optimization with quality-cost should be paired with a prediction-quality check
- `ml-datasci/profiling-llm-cost` — sibling for LLM API spend; cost and latency optimizations often trade off (smaller model = cheaper and faster but lower quality)
- `ml-datasci/recommending-model-tier` — overlapping concern for Haiku-vs-Sonnet-vs-Opus latency / cost / quality trade-off
- `ml-datasci/tuning-classification-threshold` — orthogonal: latency does not change threshold choice, but cost-weighted thresholding can change how often the model is invoked

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-2, skill 3) via PRAGMATIC discipline
