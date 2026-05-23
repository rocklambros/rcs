# LLM cost rollup (report template)

Copy-paste this template; fill each section as the profiling progresses.

## 1. Trace audit

| Field | Value |
|---|---|
| Date range | |
| n calls | |
| n tasks | |
| n unique models | |
| Rows dropped (negative tokens / missing model / corrupt) | |
| Notes | |

## 2. Per-call cost summary

| Stat | $ per call | Token count |
|---|---|---|
| Total | | |
| Mean | | |
| p50 | | |
| p95 | | |
| p99 | | |

## 3. Per-task cost summary

Group by `task_id`.

| Stat | $ per task | Calls per task |
|---|---|---|
| Mean | | |
| p50 | | |
| p95 | | |
| p99 | | |

If `p99 / p50 > 5x`, investigate the long tail separately.

## 4. Cache-hit rate trend

| Day | input_tokens | cached_input_tokens | cache_hit_rate | % vs baseline |
|---|---|---|---|---|

Annotate days where the rate moves by more than 10 percentage points.

## 5. Attribution slices

### By model

| Model | $ total | $ share | n calls |
|---|---|---|---|

### By step name

| step_name | $ total | $ share | n calls | mean $ per call |
|---|---|---|---|---|

### By route / endpoint

| route | $ total | $ share | n tasks |
|---|---|---|---|

### By user cohort

| cohort | $ total | $ share | n users |
|---|---|---|---|

## 6. Baseline delta

| Slice | Current $ | Baseline $ | Δ ($) | Δ (%) |
|---|---|---|---|---|

Sort by absolute Δ ($), not relative.

## 7. Top-3 cost drivers

1. **Driver:** ___ — contributes $___ (___% of total). Hypothesis: ___
2. **Driver:** ___ — contributes $___ (___% of total). Hypothesis: ___
3. **Driver:** ___ — contributes $___ (___% of total). Hypothesis: ___

## 8. Recommendations

Ranked by `$ saved per engineering hour`. For each:

| Action | Expected $ saved / month | Engineering hours | Quality risk | Verification step |
|---|---|---|---|---|

Always pair a cost-reduction action with a quality verification step (regression eval, golden-set re-score, latency check).
