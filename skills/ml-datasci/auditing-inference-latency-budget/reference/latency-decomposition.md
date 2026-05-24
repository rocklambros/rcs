# Per-stage latency decomposition

End-to-end latency is the sum of stage latencies. Without per-stage instrumentation, the cause of a P99 breach is invisible. Without instrumentation per stage AND per request, the cause of the *tail* is invisible.

## The minimum-viable instrumentation contract

For each request, log per-stage durations in ms:

| Stage | What it measures | Typical contribution to P99 |
|---|---|---|
| `tokenize_ms` | Tokenizer encode + pad + truncate | 1-5% (low) on most stacks; can spike on long inputs |
| `feature_lookup_ms` | Per-request feature-store / cache fetch | 5-30% — common tail driver |
| `preprocess_ms` | Normalization, embedding lookup, batching prep | 1-10% |
| `model_forward_ms` | Model inference (GPU / CPU forward pass) | 30-70% — often the dominant stage |
| `postprocess_ms` | Softmax / argmax / probability mapping / business-logic transform | 1-5% |
| `serialize_ms` | Response JSON / protobuf serialization | < 1% normally; can spike with large nested outputs |
| `network_ms` | Inter-service hop, retrieval calls, agent tool calls | Highly variable |
| `total_ms` | End-to-end (matches the SLO contract) | 100% |

`total_ms` should equal the sum of per-stage `*_ms` columns within a small overhead (a few %). Large discrepancies indicate either un-instrumented stages or queue-wait time.

## Instrumentation pattern

```python
import time
from contextlib import contextmanager

@contextmanager
def stage_timer(record, stage_name):
    t0 = time.perf_counter_ns()
    try:
        yield
    finally:
        record[stage_name + "_ms"] = (time.perf_counter_ns() - t0) / 1_000_000

def serve(request, record):
    with stage_timer(record, "tokenize"):
        tokens = tokenizer.encode(request.text)
    with stage_timer(record, "feature_lookup"):
        features = feature_store.fetch(request.user_id)
    with stage_timer(record, "preprocess"):
        batch = preprocess(tokens, features)
    with stage_timer(record, "model_forward"):
        logits = model(batch)
    with stage_timer(record, "postprocess"):
        out = postprocess(logits)
    with stage_timer(record, "serialize"):
        body = serialize(out)
    record["total_ms"] = (time.perf_counter_ns() - record.get("t_start", 0)) / 1_000_000
    return body
```

`time.perf_counter_ns()` is preferred over `time.time()` — monotonic, high resolution, immune to wall-clock adjustments. `time.process_time()` excludes I/O wait which is exactly what you want NOT to do for a latency audit.

## Common-cause table per stage

| Stage | Common tail-driver pattern | Diagnostic |
|---|---|---|
| `tokenize` | Long inputs (sequence length spike); slow tokenizer on rare scripts (emoji-heavy text on a BPE tokenizer) | Regress `tokenize_ms` on `len(request.text)` and on `len(tokens)`; high R² confirms |
| `feature_lookup` | Cache miss on cold users; unbatched feature-store on multi-user requests; slow per-user fanout | Per-request `cache_hit` flag; regress on `n_users_in_request` |
| `preprocess` | Heavy normalization on rare input types; PIL decode on large images | Regress on input size (bytes, pixels, tokens) |
| `model_forward` | Sequence-length / batch-size variance (transformer attention is O(n²)); cold-start; GPU contention | Regress on `len(tokens)` and on `batch_size`; group by `gpu_id` to find contention |
| `postprocess` | Multi-label decoding fanout; per-class business-logic transforms | Regress on `n_labels` or `n_classes_returned` |
| `serialize` | Large nested outputs; JSON encoding of float arrays | Regress on `len(body_bytes)` |
| `network` | Retrieval to slow vector DB; third-party API; cross-region call | Per-call timing of each external dependency |

## Whole-request budget vs. stage budget

A clean way to think about the audit:

- The SLO sets a `total_ms` budget (e.g., 200ms P99)
- Each stage gets a per-stage budget that sums to the total
- A stage breaching its budget AT THE PERCENTILE THAT MATTERS is the optimization target

| Stage | P99 measured | P99 budget | Status |
|---|---|---|---|
| tokenize | 8 ms | 10 ms | OK |
| feature_lookup | 280 ms | 30 ms | BREACH (the tail driver) |
| preprocess | 5 ms | 10 ms | OK |
| model_forward | 110 ms | 120 ms | OK |
| postprocess | 4 ms | 10 ms | OK |
| serialize | 1 ms | 5 ms | OK |
| network | 80 ms | 30 ms | overrun |
| total | 480 ms | 200 ms | BREACH |

This table makes the optimization target unambiguous: feature_lookup is the dominant breach; network is a secondary breach.

## Sampling rate for latency logs

Full request-level latency logging at 100% sample is rarely needed and often expensive. Recommended:

- **Always-on summary**: per-minute P50 / P95 / P99 / max + per-stage means
- **Sampled detail**: 1-5% per-request detail with per-stage breakdown for ad-hoc analysis
- **Always-on slow-request capture**: any request with `total_ms > P99_threshold` is logged in full

Tail-driver analysis requires the slow-request capture; without it, the dominant cause is invisible.

## Common pitfalls

- **Timing the wall clock around the awaits in async code without distinguishing CPU time from queue-wait time.** In async serving, a coroutine waiting on a slow downstream is queue-wait, not CPU. Distinguish with explicit pre-await and post-await timestamps.
- **Aggregating per-stage means then summing.** Means of percentile distributions do not sum. Aggregate per-stage at the percentile level.
- **Including request queue-wait in `total_ms` but not in any stage.** Queue-wait shows up as the gap between sum-of-stages and total. Surface it explicitly: `queue_wait_ms = total_ms - sum(*_ms)`.
