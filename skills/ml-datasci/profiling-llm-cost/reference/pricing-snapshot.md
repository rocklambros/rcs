# Pricing snapshot

The pricing table feeds the cost-rollup arithmetic. These rules keep it accurate.

## Format

A YAML or dict keyed by exact model identifier:

```yaml
# pricing snapshot — last verified YYYY-MM-DD against provider pricing page
claude-opus-4-7:
  in: 15.00          # $ per million input tokens
  in_cached: 1.50    # $ per million cached input tokens (10% of in on Anthropic)
  out: 75.00         # $ per million output tokens
claude-sonnet-4-6:
  in: 3.00
  in_cached: 0.30
  out: 15.00
claude-haiku-4-5-20251001:
  in: 0.80
  in_cached: 0.08
  out: 4.00
gpt-4o-2024-11-20:
  in: 2.50
  in_cached: 1.25    # OpenAI cached pricing is typically 50% of input
  out: 10.00
```

## Update rules

1. **Pin per provider snapshot.** Use the exact pricing line item the provider publishes for the exact model identifier in use. Do not generalize across model families
2. **Date-stamp the snapshot.** Each entry needs a `# last verified YYYY-MM-DD` comment; refresh quarterly or on any provider pricing announcement
3. **Cached-input pricing differs by provider.** Anthropic prices cached input at ~10% of input; OpenAI at ~50%. Do not assume one rate
4. **Beware promotional pricing.** Some providers offer time-limited discounts (e.g., batch API at 50% off, evals tier discounts); annotate the entry if a discount is in effect
5. **Output pricing is always higher than input.** If you see a snapshot with `out < in`, it is wrong; verify

## How to detect a stale snapshot

If the rollup produces a $ figure ~50% different from the actual provider invoice for the same period, the most common cause is a stale pricing snapshot — provider rates moved and the snapshot did not update.

Cross-check: pull the provider's bill for the same week the rollup covers; compare per-model totals; adjust the pricing snapshot if they disagree.

## Provider-specific gotchas

### Anthropic

- Cached-input rate is ~10% of full input
- 1h TTL is opt-in via `"ttl": "1h"` and silently downgrades to 5m without telemetry
- Cache requires a minimum region size to be eligible

### OpenAI

- Cached-input rate is ~50% of input (less aggressive discount than Anthropic)
- Some models charge separately for "reasoning tokens" (o1, o3 series) — track these as output tokens but priced differently
- Batch API offers a discount with a 24h SLA; if used, the model identifier or endpoint distinguishes batch from sync calls

### Voyage / Cohere / others

Verify per provider. Many do not yet have prompt caching as of 2026; cached-input fields will be zero.
