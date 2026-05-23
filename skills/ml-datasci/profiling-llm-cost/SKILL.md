---
name: profiling-llm-cost
description: >
  Profiles the per-call and per-task cost of an LLM-powered application by
  building a token-cost rollup from logged traces: input tokens, output tokens,
  cached vs. uncached input tokens, model tier, and downstream calls. Produces
  a $ / task figure with attribution (which step burns the most), a cache-hit
  rate trend, and a list of the highest-leverage cost-reduction opportunities.
  Triggers whenever production LLM cost is exceeding budget, whenever the
  user reports a sudden cost spike with no obvious traffic change, whenever
  prompt-cache hit rate is dropping, or whenever an agentic system's $-per-task
  is unknown and needs to be measured before optimization. Refuses to recommend
  cost-cutting actions without a measured baseline.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - data-scientist
  - ml-engineer
  - security-eng
  - devops
evidence:
  - multiturn-injection-detection
  - llm-safety-alignment-study
last-updated: 2026-05-23
---

# Profiling LLM Cost

## When to use

Trigger this skill when:

- A production LLM-powered application (chatbot, RAG, agent, batch task runner) needs a per-task or per-user $ cost measured for budgeting, pricing, or unit-economics analysis
- The user reports a cost spike ("our LLM bill doubled this month") and needs to find which step, which prompt, or which user pattern is responsible
- Prompt-cache hit rate is suspected of dropping (cache-control headers misconfigured, prompt prefix accidentally varying per call, model swap that does not share cache)
- An agentic system performs multiple LLM calls per task and the user does not know the per-task cost breakdown
- A pre-deployment budget gate is needed (estimate $ per task on a representative sample before scaling)
- Keywords: token cost, $ per task, cache hit rate, prompt caching, agent cost, LLM bill, token burn, context bloat

## When NOT to use

Skip this skill and hand off when:

- The user is in a free tier, local model (e.g., Ollama, llama.cpp), or sandbox where production $ does not apply — measure latency or quality instead
- The task is picking a model tier (Haiku vs Sonnet vs Opus) for a fresh deployment with no live data → use `ml-datasci/recommending-model-tier` (planned)
- The cost concern is non-LLM (vector DB cost, compute cost, network egress) — those are real but out of scope; this skill profiles only the LLM API spend
- The user wants embedding-model cost specifically → use `ml-datasci/selecting-embedding-model` (its cost-model reference covers that side)
- No call logs or traces exist and the user is unwilling to instrument — explain that profiling requires logged token counts and recommend instrumentation as the first step

## Quick start

User: *"Our customer-support agent's bill jumped from $4K to $11K last month and traffic only grew 20%. Find the cost."*

Response: build the per-call cost rollup from the trace log — per-call (input_tokens, output_tokens, cached_input_tokens, model), per-task (sum of calls in a logical user task), per-cohort (per-customer or per-route). Compute cache-hit rate trend by day. Compare current month to the prior baseline. Surface the top 3 cost-attribution slices and recommend the highest-leverage fix (typically cache-control restoration, context trimming, or model downgrade on a low-stakes step).

```python
import pandas as pd

def cost_per_call(row, pricing):
    # pricing dict: {model: {"in": $/M, "in_cached": $/M, "out": $/M}}
    p = pricing[row.model]
    return (
        (row.input_tokens - row.cached_input_tokens) * p["in"] / 1_000_000
        + row.cached_input_tokens * p["in_cached"] / 1_000_000
        + row.output_tokens * p["out"] / 1_000_000
    )
```

See `reference/cost-rollup-template.md` for the full report template, `reference/cache-diagnostic.md` for prompt-cache-hit troubleshooting, and `reference/pricing-snapshot.md` for the model pricing table format used in the rollup.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `trace_log` | CSV / parquet / list of dicts | yes | — | Per-call records with at minimum: `timestamp`, `model`, `input_tokens`, `cached_input_tokens`, `output_tokens`, `task_id` (or user / request id), and optionally `step_name`, `route`, `latency_ms`. |
| `pricing_table` | dict / YAML | yes | — | Per-model `$/M tokens` for input, cached input, and output. Cached-input rates are typically 10% of full input on Anthropic and OpenAI. |
| `baseline_window` | date range | no | prior 30 days | Window to compare the current period against. Comparison surfaces spike attribution. |
| `attribution_dims` | list of column names | no | `["model", "step_name", "route"]` | Which dimensions to slice the cost rollup by. |
| `task_id_column` | string | no | `"task_id"` | Column grouping calls into logical user-facing tasks. Without it, only per-call cost is meaningful. |

## Workflow

```
LLM-cost profiling progress:
- [ ] 0. Trace-log audit (required columns present, timestamps parseable, no negative tokens, no missing task ids)
- [ ] 1. Build per-call cost from input/output/cached tokens × pricing table
- [ ] 2. Roll up per task: sum cost over calls sharing a task_id; report mean, p50, p95, p99 $ per task
- [ ] 3. Cache-hit rate computation: cached_input_tokens / total_input_tokens, per day and per cohort
- [ ] 4. Attribution slice: $ by model, by step_name, by route, by user cohort, by task type
- [ ] 5. Baseline comparison: current window vs baseline_window; surface the deltas with the largest absolute $ swing
- [ ] 6. Top-3 cost drivers list with the $ each contributes and the cost-reduction hypothesis
- [ ] 7. Recommendations: ranked by ($ saved) / (engineering hours to implement); name the single highest-leverage change first
```

### Step 1: Per-call cost

For each row in the trace log:

```
cost = (
    (input_tokens - cached_input_tokens) * model_pricing["in_$/M"] / 1_000_000
    + cached_input_tokens * model_pricing["in_cached_$/M"] / 1_000_000
    + output_tokens * model_pricing["out_$/M"] / 1_000_000
)
```

Three failure modes to catch at this step:

- `cached_input_tokens > input_tokens` (some provider SDKs report cached separately, not as a subset) — handle per provider; document the convention used
- Missing pricing for a model that appears in the log (typo, deprecated model, beta endpoint) — fail loud, do not silently zero the cost
- Negative token counts from corrupt logs — drop the row, log the drop

### Step 2: Per-task rollup

Group by `task_id`. Sum cost across calls. Report:

- Mean $ per task
- p50, p95, p99 $ per task (the long tail is where most $ live)
- Distribution of `calls per task` (agentic systems should not balloon)

A p99 / p50 ratio above ~5x on $ per task means the long-tail tasks are doing very different things from the typical task — investigate.

### Step 3: Cache-hit rate

`cache_hit_rate = sum(cached_input_tokens) / sum(input_tokens)` per day.

Track the trend. Common patterns that drop the hit rate:

- A new system-prompt revision invalidates the cache for all callers until the warm-up replays
- A timestamp, run-id, or per-request identifier leaked into the prompt prefix (kills caching silently)
- Model-version pin floated forward (`claude-3-5-sonnet-20241022` → `claude-3-5-sonnet-latest`); cache is per-model-version
- Provider TTL change (Anthropic's API/SDK cache TTL reverted from 1h to 5m for some endpoints — see harness QC.4a)

See `reference/cache-diagnostic.md` for the troubleshooting checklist.

### Step 4: Attribution slice

Build a cost-by-dimension table. Common dimensions:

- **By model** — is most cost on the most expensive tier? Could parts of the workload use Haiku?
- **By step_name** (for agents/pipelines) — which step burns the most? Often "draft" or "research" steps run on the largest model when they could be cheaper
- **By route or endpoint** — is one endpoint disproportionately expensive?
- **By user cohort** — power users vs. casual users; whales drive the long tail

### Step 5: Baseline comparison

Compute current-window cost and baseline-window cost per slice. Surface the slices with the largest *absolute* $ delta (relative deltas can be misleading on small bases).

### Step 6: Top-3 cost drivers

A concise list, each with the $ contribution, the % of total, and the hypothesized cause.

### Step 7: Recommendations

Rank by `$ saved / engineering hours to implement`. Examples in descending typical leverage:

1. **Restore cache_control headers** — often near-zero engineering hours; recovers 30-90% of cached-input cost
2. **Tighten the prompt prefix** to be byte-stable (no timestamps, run-ids, varying tool definitions) — a few hours; immediate cache-hit-rate restoration
3. **Move a low-stakes step to a cheaper model** (Sonnet → Haiku for a router, classifier, or query-rewriter step) — measure quality before/after; usually a day of work
4. **Trim context length** (drop irrelevant chunks, drop verbose tool definitions, switch to summaries) — a few days; saves on input tokens
5. **Set a max_tokens budget** on output where the model is over-explaining — quick win on output cost

## Outputs

A markdown report with:

1. **Trace audit** — n calls, n tasks, date range, dropped rows
2. **Per-call cost summary** — total $, mean $ per call, p50/p95/p99
3. **Per-task cost summary** — mean / p50 / p95 / p99 $ per task; calls per task distribution
4. **Cache-hit rate trend** — by day, with annotations on drops
5. **Attribution slices** — cost by model, step, route, cohort; absolute and percent
6. **Baseline delta** — current vs prior window; slices with the largest $ swings
7. **Top-3 cost drivers** — $ contribution + hypothesis
8. **Recommendations** — ranked by ($ saved / hours); single highest-leverage first

## Failure modes

Known anti-patterns and how this skill catches them:

- **Recommending cost cuts without a baseline measurement** — caught by step 0 audit + step 5 baseline comparison; recommendations are anchored to measured deltas
- **Cache-hit rate not measured even when prompt-caching is in use** — caught by mandatory step 3; cache-hit erosion is the single most common silent-spike cause
- **Per-call cost only, no per-task rollup** — caught by step 2; agentic systems make 5-20 calls per task and per-call cost masks the real economics
- **Ignoring the long tail** — caught by mandatory p95 and p99 in step 2; the long tail often dominates total spend
- **Comparing relative deltas on small bases** — caught by step 5 ranking on *absolute* $ swings
- **Treating cached_input pricing as full input pricing** — caught by step 1 using the cached rate (typically 10% of input on Anthropic and OpenAI as of 2026)
- **Letting `model: claude-X-latest` float** — caught by step 3 diagnostic flagging model-version churn as a cache breaker
- **Recommending an Opus → Haiku swap on a quality-critical step without measuring** — recommendations always include "measure quality before/after"; do not blindly downgrade

## References

- `reference/cost-rollup-template.md` — copy-paste report template
- `reference/cache-diagnostic.md` — prompt-cache-hit troubleshooting checklist
- `reference/pricing-snapshot.md` — model pricing table format and update cadence
- [Anthropic, *Prompt caching*](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) — provider-canonical caching docs, including TTL and pricing
- [OpenAI, *Prompt caching*](https://platform.openai.com/docs/guides/prompt-caching) — provider-canonical caching docs for OpenAI models

## Examples

### Example 1: Production agent cost audit (happy-path)

Input: *"Our customer-support agent's bill jumped from $4K to $11K last month and traffic only grew 20%. We have a full trace log with model, input_tokens, cached_input_tokens, output_tokens, task_id, and step_name. Find where the cost went."*

Output: Skill audits the trace log, builds the per-call and per-task rollup, computes cache-hit rate trend, slices cost by model and step_name, compares current month to the baseline window. Surfaces (for example) that the `clarify_intent` step's cache-hit rate dropped from 85% to 12% on day 14 of the month — the date a system-prompt edit shipped that invalidated the cache. Recommends pinning the prompt-prefix structure and quantifies the expected $ recovery.

### Example 2: Cache-hit rate dropped (edge-case)

Input: *"Our prompt-cache hit rate dropped from 90% to 30% last week. Cost is up. What broke?"*

Output: Skill walks the cache-diagnostic checklist (`reference/cache-diagnostic.md`): system-prompt change, model-version pin float, timestamp/run-id leak in the prefix, tool definitions changing per call, provider TTL change. For each, names the artifact to inspect (recent commits to system-prompt files, model-config diffs, recent additions to the prompt-template renderer). Recommends restoring byte-stable prefix and pinning the model version.

### Example 3: Free-tier / sandbox project (anti-trigger)

Input: *"I'm building a side project with Ollama running llama-3 locally. Should I profile its cost?"*

Output: Skill identifies that local-model / free-tier workloads do not have a meaningful per-token $ cost in the API-spend sense. Names what IS worth measuring locally (latency, throughput, GPU memory, electricity at high volume) and notes that this skill is scoped to paid-API workloads. Does not force the full cost-rollup workflow.

## See also

- `ml-datasci/selecting-embedding-model` — sibling for the retrieval-side cost profile (this skill covers the generation side)
- `ml-datasci/evaluating-rag-retrieval` — the upstream quality eval; cost recommendations should always be paired with a quality measurement before/after
- `ml-datasci/recommending-model-tier` (planned) — sibling for choosing Haiku vs Sonnet vs Opus per workload step
- `claude-code-meta/auditing-instruction-hierarchy` — overlapping discipline for CLAUDE.md hierarchy size, which affects every cached prefix on the Claude Code side
- `workflow/auditing-context-window-pressure` — sibling for the session-level context-budget side

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v3-batch-3, skill 3) via PRAGMATIC discipline
