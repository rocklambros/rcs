---
name: auditing-prompt-token-budget
description: >
  Audits an Anthropic API prompt (system + user + tool definitions + tool
  results) for token budget pressure and prompt-cache hygiene. Tokenizes the
  full request, flags prompts above a configurable budget, detects duplicated
  boilerplate that should be moved to a cache_control segment, and recommends
  the right TTL (5m default vs 1h extended). Use whenever per-call cost is
  rising, latency is climbing on otherwise-identical prompts, the request
  payload is approaching the model context window, or when shipping any new
  agentic loop, RAG application, or multi-turn workflow. Refuses to engage on
  prompts under ~500 tokens (no meaningful budget pressure) and redirects
  raw-text re-tokenizing requests to the model's tokenizer directly.
version: 0.1.0
status: shipped
track: ml-datasci
audience: [data-scientist, ml-engineer, devops, security-eng]
evidence:
  - mac-harness QC.4a (1h TTL discipline)
  - email-spam-classifier-naive-bayes-comparisson-roc
  - multiturn-injection-detection
  - llm-toxicity-visual-analysis
last-updated: 2026-05-23
---

# Auditing Prompt Token Budget

## When to use

Trigger this skill when the user asks for or implies one of:

- "Why is my Anthropic API bill climbing?" — per-call token cost rising over time
- "My agent is slow on the first turn but fast on later turns" — cache miss on the cold turn, cache hit later (or the inverse, which is the bug case)
- "I'm getting `prompt_too_long` or approaching the 200k context window"
- "I want to add prompt caching to my app" — recommend where to put `cache_control` and which TTL to pick
- "How big is my prompt?" — wants a token count and a budget recommendation
- Shipping a new agentic loop, RAG application, multi-turn chat, or any system where the same large prefix is sent on every call
- Cache hit rate has dropped (was ≥ 70%, now < 50%) and the user wants to know why

This skill pairs with `workflow/auditing-context-window-pressure` (Claude Code session pressure) and `ml-datasci/recommending-model-tier` (different model = different per-token cost).

## When NOT to use

Skip this skill and hand off or do nothing when:

- The prompt is < 500 tokens — no meaningful caching benefit; the 1024-token minimum cache write would fail silently on most providers anyway and the savings are negligible
- The user is asking about Claude Code's session context (use `workflow/auditing-context-window-pressure`)
- The user wants raw tokenizer output for arbitrary text with no prompt structure — point them at the Anthropic `count_tokens` endpoint or `tiktoken`-equivalent directly
- The application is a one-shot script with no repeated prefix — caching adds latency overhead on a single call and helps nothing
- The user is on a non-Anthropic provider — the cache_control / TTL guidance here is Anthropic-specific; OpenAI / Gemini / Bedrock have different cache primitives and the recommendations would mislead

## Quick start

User says: "Our customer-support agent sends a 5,000-token system prompt plus a 200-token user message on every turn. We're running 50,000 conversations per day, average 8 turns. Audit it."

Skill response (in order):

1. **Tokenize** the system + tool definitions + first user turn → ~5,200 tokens input on turn 1, ~5,400 on turn 2 (with assistant + user history), growing
2. **Stable-vs-volatile split**: the 5,000-token system block is stable across all 50,000 × 8 = 400,000 calls per day → prime caching candidate. The 200-token user message is volatile → not cached.
3. **Recommend `cache_control` placement**: add `"cache_control": {"type": "ephemeral", "ttl": "1h"}` on the final block of the system prompt (the cache breakpoint is set at the END of the cached region; everything before it is cached)
4. **Pick TTL**: 8-turn conversation typically spans < 1 hour but inter-conversation reuse spans days → 1h TTL beats 5m (default). Justify the explicit `"ttl": "1h"` per the harness QC.4a discipline.
5. **Cost projection**: cache write costs 1.25× base input rate; cache reads cost 0.10× base. With 400k daily reads on a 5k-token stable block, the savings are ~85% of input cost on that segment.
6. **Telemetry**: enable `cache_creation_input_tokens` + `cache_read_input_tokens` in the response and dashboard them; cache hit rate must be ≥ 70% to be worth keeping.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| prompt_source | "anthropic-messages-json" \| "openai-chat-json" \| "raw-text" \| "code-snippet" | yes | — | How the prompt was supplied. Each path uses a different tokenizer. |
| call_volume | int (calls/day) or "unknown" | no | "unknown" | Used for cost projection and TTL recommendation. ≥ 1,000 with stable prefix → cache. |
| reuse_window | "within-conversation" \| "hours" \| "days" \| "weeks" | no | "hours" | Drives TTL choice: within-conversation → 5m fine; hours-to-days → 1h; weeks → cache rebuild cost dominates, often not worth it. |
| budget_threshold_tokens | int | no | 8000 | Total-prompt threshold above which the skill loudly recommends caching. |
| min_segment_tokens | int | no | 1024 | Anthropic's minimum cacheable segment. Segments below this can't be cache breakpoints. |
| context_window | int | no | 200000 | The deployed model's window. Used to compute headroom %. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check items off as each step completes:

```
Prompt-budget audit progress:
- [ ] Step 1: Tokenize the full request (system + tools + tool_results + each user/assistant turn)
- [ ] Step 2: Split tokens into stable-prefix vs volatile-suffix
- [ ] Step 3: Compute total tokens vs context window (headroom %)
- [ ] Step 4: Detect duplicate boilerplate across calls (same block hashed repeatedly = cache opportunity)
- [ ] Step 5: Recommend cache_control breakpoint placement (≤ 4 breakpoints; end of cached region)
- [ ] Step 6: Pick TTL — 5m default vs explicit "1h" — based on reuse_window and call_volume
- [ ] Step 7: Project cost: write cost (1.25× base) vs read cost (0.10× base) vs no-cache cost
- [ ] Step 8: Recommend telemetry (cache_creation_input_tokens, cache_read_input_tokens) and a hit-rate alert
```

### Step 1: Tokenize

For Anthropic Messages API JSON, the count includes:

- `system` (string or array of content blocks)
- `tools` definitions (each tool's name + description + input_schema)
- Every `messages[i].content` (string or array)
- Every `tool_result` payload in tool-use turns

Use the official tokenizer: `anthropic.beta.messages.count_tokens(...)` — it returns the exact count the API will bill. Approximations (chars / 4, `tiktoken` `cl100k_base`) drift ~10–15% from Claude's tokenizer; don't ship a budget audit on an approximation.

### Step 2: Stable-vs-volatile split

Classify each block:

| Block | Typical class | Cache candidate? |
|---|---|---|
| System prompt (instructions, persona, format rules) | Stable | Yes |
| Tool definitions | Stable | Yes |
| RAG-retrieved documents pinned for the conversation | Stable within conversation | Yes (5m TTL) |
| Long reference documents reused across conversations | Stable across calls | Yes (1h TTL) |
| User turn | Volatile | No |
| Assistant turn | Volatile | No |
| Tool result | Volatile (usually) | No |

The cache breakpoint goes at the END of the longest contiguous stable region. Everything before the breakpoint is cached as a single unit.

### Step 3: Total tokens vs context window

Report headroom: `(context_window - total_tokens) / context_window`. Flag if:

- Headroom < 25% → user is one long turn away from `prompt_too_long`
- Headroom < 10% → emergency; recommend conversation compaction or older-turn pruning immediately

### Step 4: Detect duplicate boilerplate

Hash each block in the request and look for the same hash appearing in N consecutive calls (from logs if available, or from the structure of the prompt template). Same hash N times = wasted tokens; collapse the duplicates into a single cached prefix and reference them.

Common offenders:

- Few-shot examples re-included on every turn instead of cached once
- Tool definitions repeated in both `system` and `tools` (the API expects them in `tools` only)
- The same retrieval-augmented context injected on every turn of a conversation when it should be injected once at the start

### Step 5: Recommend cache_control breakpoints

Anthropic API supports up to 4 cache breakpoints per request. Place them at:

1. End of the deepest-stable region (largest cached unit, almost always end of `system` or end of tool definitions)
2. End of the next-deepest stable region (e.g., end of RAG context)
3. End of the assistant turn just before the current user turn (cache the conversation history up to this point)
4. Reserved for future use; don't fill it speculatively

The cache_control object goes on the LAST content block of the cached region. Everything BEFORE that block becomes part of the cached prefix.

```python
# Example: system prompt with cache breakpoint
system = [
    {"type": "text", "text": "<long, stable instructions>",
     "cache_control": {"type": "ephemeral", "ttl": "1h"}},
]
```

### Step 6: Pick TTL

| Reuse window | Recommended TTL | Rationale |
|---|---|---|
| Single conversation, < 5 min between turns | 5m (default — omit `ttl` field) | Default is cheapest write cost and fine for conversations |
| Same prefix across multiple conversations within a few hours | "1h" (explicit) | Pay 2× write cost once; amortize over many reads. Default reverted to 5m March 2026 — always set "1h" explicitly. |
| Same prefix reused for days or weeks | "1h" still — the cache TTL caps at 1 hour. For longer reuse, the cache is rebuilt repeatedly; consider whether the rebuild cost is justified by the read savings (usually yes if volume is high) |
| Prefix changes every call (e.g., the user message is in the cached region) | DO NOT cache | Cache miss every call; you pay 1.25× write cost for zero read savings |

**Always set `"ttl": "1h"` explicitly when you want extended caching.** The default reverted from 1h to 5m in March 2026, and telemetry-off silently falls back to 5m. Explicit beats implicit.

### Step 7: Cost projection

Anthropic pricing for cache (as of writing):

| Operation | Cost (relative to base input tokens) |
|---|---|
| Base input | 1.0× |
| Cache write (5m TTL) | 1.25× |
| Cache write (1h TTL) | 2.0× |
| Cache read | 0.10× |

Cost per day with cache, for a stable prefix of T tokens, N calls/day, hit rate H:

```
write_cost = T × (1 - H) × 1.25  (or 2.0 for 1h TTL)
read_cost  = T × H × 0.10
no_cache   = T × N × 1.0
```

The break-even hit rate is roughly H > 14% for 5m TTL and H > 21% for 1h TTL. Below that, caching is a net loss.

### Step 8: Telemetry

Every response from a cached prompt returns:

- `usage.cache_creation_input_tokens` — tokens written to the cache this call
- `usage.cache_read_input_tokens` — tokens read from cache this call
- `usage.input_tokens` — tokens billed at base rate (not cached)

Aggregate these into a dashboard panel:

- Cache hit rate per day: `cache_read / (cache_read + cache_creation)`
- Alert at hit rate < 50% (broken cache) or > 95% (over-cached, may indicate a prompt regression)

## Outputs

A short markdown report:

1. **Header** — total input tokens, total output tokens, context window headroom %
2. **Block table** — each block, token count, classification (stable / volatile), cache recommendation
3. **Breakpoint placement** — JSON snippet showing where to add `cache_control` (with the explicit `"ttl"` field)
4. **TTL recommendation** — 5m vs 1h with rationale tied to the user's `reuse_window`
5. **Cost projection** — write cost, read cost, no-cache cost, monthly delta at the user's call volume
6. **Telemetry** — code snippet for reading `cache_creation_input_tokens` / `cache_read_input_tokens` and a recommended hit-rate threshold
7. **Anti-patterns flagged** — duplicate boilerplate, tool definitions repeated in `system`, RAG-context injected per-turn, etc.

## Failure modes

- **Approximating tokens via `chars / 4` or wrong tokenizer** — drift is 10–15%; budget audits based on approximations under-count and surprise the user with a `prompt_too_long`. Caught by: Step 1 mandates the official `count_tokens` endpoint.
- **Caching the wrong end of the prompt** — placing `cache_control` on the FIRST block of the stable region instead of the LAST → only the first block is cached, not the whole region. Caught by: Step 5 states the breakpoint is the END of the cached region.
- **Putting volatile content inside the cached region** — a timestamp, a session id, or per-call user data injected into the system prompt → cache miss every call. Caught by: Step 2 stable-vs-volatile classification before recommending breakpoints.
- **Implicit 5m TTL when the user needs 1h** — relying on Anthropic's default; the default reverted from 1h to 5m in March 2026, breaking apps that relied on the previous behavior. Caught by: Step 6 requires explicit `"ttl"` when extended caching is wanted (per harness QC.4a).
- **Cache segment under 1024 tokens** — Anthropic silently doesn't cache segments under the minimum; the API doesn't error, it just doesn't cache. Caught by: `min_segment_tokens` argument default = 1024 and the skill checks each breakpoint segment.
- **Over-caching breakpoint 4** — placing all 4 breakpoints speculatively, including one in a region that always changes → 1 wasted breakpoint and confusing telemetry. Caught by: Step 5 explicitly reserves breakpoint 4.
- **Not measuring hit rate post-deployment** — caching configured at ship time, then never verified. Cache silently breaks (e.g., a downstream code change adds a timestamp to the system block). Caught by: Step 8 requires telemetry and an alert.

## References

- [`reference/cache-cookbook.md`](reference/cache-cookbook.md) — copy-paste snippets for `cache_control` in Python and TypeScript SDKs, including the 4-breakpoint pattern and the `count_tokens` call
- [Anthropic prompt-caching docs](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) — official cache_control semantics, TTL options, billing rates
- [Anthropic count_tokens beta](https://docs.claude.com/en/api/messages-count-tokens) — token counting endpoint
- mac-harness `foundation/00-quality-contract.md` QC.4a — origin of the "always set `ttl: 1h` explicitly" discipline

## Examples

### Example 1: 5k-token system prompt with high call volume (happy-path)

Input: "Our agent has a 5,000-token system prompt with persona + tool list + few-shot examples. We send 50,000 calls/day, average 8 turns per conversation. Audit it."

Output: Total prompt on turn 1 = ~5,200 tokens (system + tool defs + 200-token user turn); headroom in a 200k window = 97%. The 5,000-token system block is stable across 400k daily calls — prime cache target. Place one breakpoint at the end of the system content with `"ttl": "1h"` (reuse spans days across conversations). Projected cost at 95% hit rate: write 5,000 × 0.05 × 2.0 = 500 token-equivalents per call; read 5,000 × 0.95 × 0.10 = 475; vs no-cache 5,000 × 1.0 = 5,000. **Savings ≈ 80% on input tokens.** Telemetry: log `cache_read_input_tokens / (cache_read + cache_creation)` daily; alert below 70%.

### Example 2: Under budget but missing cache_control (edge-case)

Input: "My prompt is 3,000 tokens, well under the 200k window. We send 200 calls/day. Do I need caching?"

Output: 3,000 × 200 = 600k base input tokens/day = ~$1.80/day on Opus 4.7 at $3/M input. Audit anyway — the question isn't headroom, it's whether the 3,000 are stable. If yes (a system prompt + few-shots): add cache_control. Even at 200 calls/day with 5m TTL, expected hit rate is low (calls likely > 5m apart) → 1h TTL is the right choice. Break-even calculus: 1h-TTL write cost is 3,000 × 2.0 = 6,000; reads at 0.10× × 199 = 59,700 token-equivalents saved → net savings ~50,700 tokens/day. 1h-TTL is worth it even at this low volume. **Recommendation:** add the breakpoint and the explicit `"ttl": "1h"`.

### Example 3: Sub-500-token one-shot script (anti-trigger)

Input: "I'm writing a one-shot Python script that asks Claude to summarize a 300-token user-provided text. Should I add prompt caching?"

Output: **No.** Total prompt is ~400 tokens (~100-token system + 300-token user message); below the 1024-token cache minimum, the cache write would silently no-op anyway. One-shot scripts have no repeated prefix to amortize the write cost against. Caching adds zero value here and adds the 1.25× write cost on the first call for nothing. Stick with the default un-cached path. (If the script later evolves into a long-running service with thousands of calls/day, re-audit at that point.)

## See also

- `workflow/auditing-context-window-pressure` — Claude Code session-level context pressure (different problem class from API-prompt budgeting)
- `ml-datasci/recommending-model-tier` — model choice changes the per-token rate; the cache calc is per-model
- `ml-datasci/profiling-llm-cost` (planned) — broader per-call cost rollup including output tokens, latency, and per-task $ projection

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
