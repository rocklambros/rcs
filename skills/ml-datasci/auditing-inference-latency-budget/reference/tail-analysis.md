# Tail analysis patterns

A breach where P50 is healthy and P99 is blown is a tail problem. Tail problems are caused by something different from the median request, not by everything being slow. Five common patterns, each with a distinct fix.

## Pattern 1: Input-shape variance

**Symptom**: P50 within budget, P99 5-10x larger. A single covariate (sequence length, batch size, retrieval fanout) correlates strongly with the slow group.

**Diagnostic**: regress per-stage latency on input_shape_dims; plot a scatter of latency vs. each covariate. A clear positive slope on one dim is the smoking gun.

**Example**: an LLM document-classifier with mean input 500 tokens, P99 input 50,000 tokens. The forward pass is O(n) (or O(n²) for full attention). The P99 tokenization + forward latency is dominated by the long-input 1% of traffic.

**Fixes ranked**:

1. **Route long inputs to a slower-but-larger tier** with a different SLO. Cleanest. Quality preserved. Hours of work.
2. **Truncate inputs at a cap** (with summary or chunking fallback). Hours of work. Quality risk if the truncation loses signal.
3. **Chunk and parallelize** then merge. Days of work. Quality risk in the merge step.
4. **Switch to a model with O(n) or sub-quadratic attention** (FlashAttention, sliding-window attention). Days to weeks. Often the right long-term answer.

## Pattern 2: Cold-start

**Symptom**: P99 spikes immediately after a scale-up event (autoscaler added replicas, deploy rolled out, traffic surged). Steady-state P99 is fine.

**Diagnostic**: filter latency log to exclude requests within `cold_start_window_min` of a scale-up event. If filtered P99 is in SLO and unfiltered is not, the cause is cold-start.

**Example**: a Kubernetes pod takes 45 seconds to load the model into GPU memory. During scale-up, the new pod accepts traffic immediately but its first 200 requests pay the loading tax.

**Fixes ranked**:

1. **Pre-warming via readiness probe**: do not mark the pod ready until the model is loaded. Almost free. Eliminates the symptom.
2. **Higher min-replica count** so the autoscaler does not have to scale up under load. Cost trade-off.
3. **Faster model load** (memory-mapped weights, tensor sharding, smaller checkpoint). Days of work.
4. **Request shaping** — degrade gracefully on cold replicas (e.g., return a cached approximation). Quality trade-off.

## Pattern 3: Contention / noisy neighbor

**Symptom**: P99 latency correlates with other tenants' traffic, not with the request itself. Per-GPU or per-host slicing shows some hardware is uniformly slower.

**Diagnostic**: per-`host_id` / `gpu_id` latency distribution. If one host is materially slower than the others on the same request workload, contention is the cause.

**Example**: a shared GPU pool where one tenant's batched preprocessing saturates PCIe bandwidth and slows model_forward for all tenants on the host.

**Fixes ranked**:

1. **Dedicated capacity** for SLO-bound routes. The cleanest fix; the cost is real.
2. **QoS isolation** (cgroups, GPU partitioning, MIG slices). Days of work. Imperfect on shared CUDA contexts.
3. **Tenant rate-limit** to prevent one neighbor from saturating. Days of work.
4. **Move to single-tenant per pod** with autoscaling. The brute-force fix; cost trade-off.

## Pattern 4: External-dependency tail

**Symptom**: model_forward and feature_lookup are fast; one external call (vector DB, retrieval API, third-party data feed) has a wide P99 distribution that dominates the request.

**Diagnostic**: per-external-call timing. The slow dependency stands out.

**Example**: a RAG pipeline where vector-DB retrieval has P50 12ms and P99 280ms because the DB's cache-miss path involves a disk read on cold partitions.

**Fixes ranked**:

1. **Asynchronous prefetch** — start the slow call before its result is needed, overlap with other stages. Often free latency.
2. **Cache the dependency response** — assuming results are stable enough. Hours of work.
3. **Timeout + fallback** — bound the slow call; degrade gracefully on timeout. Quality trade-off (the fallback path may be lower quality).
4. **Replace the dependency** — switch vector DBs, vendor APIs, etc. Days to weeks; large surface change.

## Pattern 5: Cache miss

**Symptom**: latency is bimodal — fast on cache hit, slow on cache miss. The miss-rate determines the P99.

**Diagnostic**: tag each request with `cache_hit: bool`. Per-`cache_hit` latency distribution shows the bimodality.

**Example**: an embedding cache with a 3% miss rate where misses go to the slow recompute path. P99 is in the miss group.

**Fixes ranked**:

1. **Pre-warm the cache** on common items at startup or via a background populator. Hours of work.
2. **Larger cache** to reduce miss rate (more RAM or longer TTL). Cost trade-off.
3. **Faster slow-path** so the miss penalty is smaller. Days of work; depends on what the slow path is.
4. **Negative caching** for misses on items unlikely to exist. Quality trade-off (stale).

## Combined-cause situations

Production tails are often multiple causes stacked. Diagnose them ONE at a time:

1. Filter out cold-start (Pattern 2).
2. Check input-shape variance on the filtered set (Pattern 1).
3. Check per-host contention on the filtered, shape-bounded set (Pattern 3).
4. What remains in the tail is dependency / cache (Patterns 4 and 5).

Each filter you apply should make the P99 distribution narrower. If it does not, the cause you filtered for was not present.

## When the tail is irreducible

Some workloads have an irreducible tail driven by user-input distributions you cannot control. The right answer is then SLO renegotiation, not engineering effort:

- Document the tail driver in the model card / service SLO
- Set the P99 SLO to a feasible level given the input distribution
- Add a P99.9 watch (informational, not budget-bound) for outlier monitoring

This is not a failure of optimization. It is a correct recognition that the tail belongs to the world, not to the system.
