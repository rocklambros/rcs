# Prompt-cache diagnostic checklist

When the cache-hit rate drops, walk this list in order. The earlier items are the most common.

## 1. Was the system prompt edited?

Any byte change to the cached prefix invalidates the cache for all callers until the warm-up traffic replays. Check recent commits to:

- System-prompt files (`system.md`, `prompt.py` system_prompt constant, etc.)
- Tool definitions (added, removed, or reordered tools change the cached prefix)
- The `cache_control` block placement (moved breakpoint = new cache key)

If a prompt edit lines up with the drop date, the rate will recover on its own as traffic warms the new cache. Quantify the unavoidable cost spike during warm-up.

## 2. Did a model version pin float forward?

The cache is keyed per model version. These all invalidate cached state:

- `claude-3-5-sonnet-20241022` → `claude-3-5-sonnet-latest` (the latest tag points to a different snapshot)
- A provider deprecation forcing you onto a new snapshot
- Cross-model fallback logic that occasionally routes to a different model

Always pin specific model snapshots (e.g., `claude-opus-4-7`, not `claude-opus-latest`) and treat version bumps as deliberate events.

## 3. Did per-request content leak into the cached prefix?

Anything that varies per call inside the cached region kills the cache. Common leaks:

- A timestamp or run-id in the prompt header
- A per-user identifier rendered before the breakpoint
- Conversation history concatenated with no breakpoint between fixed-history and turn-specific content
- Tool definitions that include a per-session URL or token

Inspect a sample of cached-prefix bytes across calls. They should be byte-identical up to the `cache_control` breakpoint.

## 4. Has the cache TTL changed?

Anthropic's API/SDK default cache TTL is 5 minutes; an explicit `"ttl": "1h"` extends it to one hour where supported. The 1h TTL also requires telemetry-on; with telemetry off, 1h is silently downgraded to 5m without raising an error (see RCS harness QC.4a).

For low-volume endpoints where calls are spaced more than 5 minutes apart, the cache expires between calls and the hit rate looks like zero. Either:

- Switch on the 1h TTL (and confirm telemetry is on)
- Accept that low-volume traffic patterns will not benefit from caching

## 5. Did the cache_control header get removed?

Easy to miss in code review. Search the repo for recent changes touching `cache_control` keys. A removed breakpoint disables caching for the message; the API does not error.

## 6. Is the cached region too small?

Anthropic requires a cached region to exceed a minimum size (typically 1024 tokens) to be eligible for caching. Below that floor, the cache silently no-ops. If a prompt was trimmed below the threshold by a recent refactor, caching stopped without error.

## 7. Cross-context: is a downstream system invalidating it?

For some orchestration frameworks (LangChain, LlamaIndex, custom agent loops), a wrapper may rebuild the message list per call in a way that breaks byte-stability of the prefix. Inspect the actual bytes sent to the API, not the abstract prompt template.

## How to verify the fix

After applying a hypothesized fix:

1. Run a representative test call
2. Inspect the API response for the `cache_read_input_tokens` (Anthropic) or `cached_tokens` (OpenAI) field
3. Confirm it returns a non-zero count on the second call within the TTL window
4. Re-pull the production cache-hit rate after 24 hours of warmed traffic
