# SLO construction and latency budget

A latency SLO is a contract with the consumer of the service: "we will respond within X ms at percentile P, with error-budget B per period." A latency audit without an SLO has nothing to compare against.

## Choosing the percentile

| User-facing behavior | Right percentile |
|---|---|
| Synchronous user-blocking (chat, search) | P95 or P99 |
| Asynchronous (background scoring, analytics) | P50 or P95 |
| Multi-call orchestration where one slow call blocks the rest | P99 or P99.9 |
| Batch / offline | wall-clock budget, not percentile |

The general rule: pick the percentile whose breach has consumer-visible impact. Mean is almost never the right percentile for a real-time SLO.

## Sizing the SLO

Three approaches:

1. **Top-down**: the user-facing product SLO (e.g., "page loads in 1s") divided across the call chain (e.g., "200ms for the model service").
2. **Bottom-up**: measured per-stage P99 on a representative workload; SLO is the sum plus a small headroom.
3. **Comparative**: peer benchmark — what do comparable services in industry guarantee?

Use top-down to set the *target* and bottom-up to confirm the target is *feasible*. If they disagree, either reduce per-stage latency, parallelize, or renegotiate the user-facing SLO.

## Multi-tier SLOs

For workloads with heterogeneous input shapes, one global SLO punishes large requests or rewards small ones. Multi-tier SLOs:

| Tier | Input criterion | P99 SLO |
|---|---|---|
| Standard | tokens ≤ 1k | 150 ms |
| Long-form | 1k < tokens ≤ 10k | 800 ms |
| Bulk | batch ≥ 100 rows | 5 s |

Each tier has its own routing, capacity, and SLO. Reduces tail-driven false breaches and lets capacity planning match demand.

## Error budget

SLO breach is not pass/fail per request; it is rate over a window:

```
allowed_breach_rate = 1 - 0.99   # if SLO P99 budget is 1%
n_breaches_allowed_per_day = traffic_per_day * allowed_breach_rate
```

For 1M requests/day with a P99 SLO, 10,000 breaches per day are within budget. A breach incident is when:

- Rolling 24h breach count exceeds budget AND
- The trend is sustained (not a one-time spike)

Tracking the error budget AS A BUDGET (you can spend it on a deploy, a scaling event, a known capacity reduction) is the SRE pattern; this skill aligns with it.

## Latency vs. quality vs. cost trade-offs

Every latency optimization has a quality or cost cost. The audit should surface the trade-off, not hide it:

| Optimization | Latency saved | Quality cost | $ cost |
|---|---|---|---|
| Truncate long inputs | High | Possibly high (loss of signal in tail) | Free |
| Smaller / faster model | High | Variable (depends on task) | Lower |
| Quantization (int8 / int4) | Medium | Small but real | Lower (smaller weights) |
| Distillation to a smaller student | High | Task-dependent | Higher (training cost) |
| Pre-warming + min-replicas | Medium | None | Higher (idle capacity) |
| Caching | Medium | Staleness if results vary | Storage cost |
| Async pre-fetch | Medium | None | Code complexity |
| Parallelize stages | Variable | None | Code complexity |
| Switch model architecture | Variable | Variable | Engineering cost |

Recommend optimizations starting with the highest `latency_saved / quality_cost` ratio, NOT the highest `latency_saved` alone.

## SLO documentation pattern

```yaml
service: fraud-scoring-api
version: 1.4
slo:
  p50_ms: 80
  p95_ms: 160
  p99_ms: 200
  error_budget_pct: 1.0   # 1% of requests may breach per day
  measurement_window: 24h
tiers:
  - name: standard
    criterion: "batch_size <= 10"
    slo: {p99_ms: 200}
  - name: bulk
    criterion: "batch_size > 10"
    slo: {p99_ms: 1500}
cold_start_window_min: 5
last_validated: 2026-04-01
notes: >
  Tier SLOs are independent. Bulk tier is routed to a dedicated pool.
  Cold-start window excludes requests in the first 5 minutes after a scale-up event.
```

This is what the audit produces a verdict against. Without it, "the service is slow" is not falsifiable.

## Common SLO anti-patterns

- **No SLO at all** — every optimization is unanchored. Set one before auditing.
- **Mean-based SLO** — invisible to the tail. Almost always wrong for real-time services.
- **Aspirational SLO not derivable from the architecture** — e.g., a 50ms P99 SLO on a system whose median model_forward is 80ms. Bottom-up sizing catches this.
- **Single SLO for heterogeneous traffic** — multi-tier or per-route SLOs are usually the right answer.
- **Error budget never used** — if the budget is permanently green, the SLO is too loose; if always red, too tight. Tune it.
