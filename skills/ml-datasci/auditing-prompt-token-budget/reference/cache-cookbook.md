# Prompt-Cache Cookbook (Anthropic API)

Copy-paste reference for adding `cache_control` to the Anthropic Messages API. All snippets target Claude 4.x (Haiku 4.5, Sonnet 4.6, Opus 4.7). Pricing rates current as of 2026-05.

## Counting tokens (do this first)

```python
import anthropic

client = anthropic.Anthropic()
count = client.beta.messages.count_tokens(
    model="claude-opus-4-7",
    system=SYSTEM_PROMPT,
    messages=[{"role": "user", "content": user_text}],
    tools=TOOLS,
)
print(count.input_tokens)  # exact billed count
```

The `count_tokens` endpoint is the only thing that returns the count the API will actually bill. Approximations are off by 10–15%.

## Single breakpoint on a stable system prompt

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": LONG_STABLE_INSTRUCTIONS,
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        },
    ],
    messages=[{"role": "user", "content": user_text}],
)
```

The `cache_control` field on the LAST block of `system` caches everything in `system` up to and including that block. Always set `"ttl": "1h"` explicitly when you want extended caching (the default reverted to 5m in March 2026).

## Two breakpoints: system + tools

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": LONG_STABLE_INSTRUCTIONS,
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        },
    ],
    tools=[
        {
            "name": "search_kb",
            "description": "...",
            "input_schema": {...},
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        },
    ],
    messages=[{"role": "user", "content": user_text}],
)
```

## Three breakpoints: system + tools + conversation history

For a multi-turn agent, cache the conversation up to the most recent assistant turn:

```python
messages = [
    {"role": "user", "content": turn_1_user},
    {"role": "assistant", "content": turn_1_assistant},
    {"role": "user", "content": turn_2_user},
    {"role": "assistant", "content": [
        {"type": "text", "text": turn_2_assistant,
         "cache_control": {"type": "ephemeral", "ttl": "5m"}},
    ]},
    {"role": "user", "content": current_user_message},
]
```

5m TTL is the right choice inside a single conversation; the conversation typically completes within 5 minutes between turns.

## TypeScript / JavaScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-opus-4-7",
  max_tokens: 1024,
  system: [
    {
      type: "text",
      text: LONG_STABLE_INSTRUCTIONS,
      cache_control: { type: "ephemeral", ttl: "1h" },
    },
  ],
  messages: [{ role: "user", content: userText }],
});

console.log(response.usage.cache_creation_input_tokens);
console.log(response.usage.cache_read_input_tokens);
```

## Reading cache telemetry

```python
response = client.messages.create(...)

print(f"input_tokens:                 {response.usage.input_tokens}")
print(f"cache_creation_input_tokens:  {response.usage.cache_creation_input_tokens}")
print(f"cache_read_input_tokens:      {response.usage.cache_read_input_tokens}")
print(f"output_tokens:                {response.usage.output_tokens}")

# Aggregate hit rate over a window
hits = sum(r.usage.cache_read_input_tokens for r in window_responses)
total_cached = hits + sum(
    r.usage.cache_creation_input_tokens for r in window_responses
)
hit_rate = hits / total_cached if total_cached else 0.0
```

Alert thresholds:

- `hit_rate < 0.5` → cache is broken; something in the cached region is changing per call
- `hit_rate > 0.95` for several days → cache is fine but verify the prefix hasn't regressed silently

## Common anti-patterns

```python
# ANTI-PATTERN 1: cache_control on the FIRST block (only that block is cached)
system=[
    {"type": "text", "text": "...",
     "cache_control": {"type": "ephemeral"}},
    {"type": "text", "text": "..."},  # NOT cached
]

# Fix: move cache_control to the LAST block of the region you want cached
system=[
    {"type": "text", "text": "..."},
    {"type": "text", "text": "...",
     "cache_control": {"type": "ephemeral", "ttl": "1h"}},
]
```

```python
# ANTI-PATTERN 2: timestamp inside the cached region (cache miss every call)
system=[
    {"type": "text",
     "text": f"You are an assistant. Today is {datetime.now()}.",
     "cache_control": {"type": "ephemeral", "ttl": "1h"}},
]

# Fix: move volatile content to a system-reminder / out-of-cache block
system=[
    {"type": "text",
     "text": "You are an assistant.",
     "cache_control": {"type": "ephemeral", "ttl": "1h"}},
]
messages=[
    {"role": "user", "content": f"Today is {datetime.now()}. {user_text}"},
]
```

```python
# ANTI-PATTERN 3: tool definitions duplicated in system AND tools
system=[
    {"type": "text", "text": "You have access to a tool called search_kb..."},
]
tools=[
    {"name": "search_kb", "description": "...", ...},
]

# Fix: the API binds tools via the tools field only; describing them again in system
# wastes tokens and creates drift opportunities
```

```python
# ANTI-PATTERN 4: RAG context injected on every turn instead of cached at start
messages=[
    {"role": "user", "content": f"{retrieved_docs}\n\n{user_q_1}"},
    {"role": "assistant", "content": a_1},
    {"role": "user", "content": f"{retrieved_docs}\n\n{user_q_2}"},  # same docs!
]

# Fix: inject the retrieved_docs once in system (cached) or in the first user turn
# (cached via conversation-history breakpoint), then reference them subsequently.
```

```python
# ANTI-PATTERN 5: sub-1024-token segment as a cache breakpoint
system=[
    {"type": "text", "text": "<800 tokens of instructions>",
     "cache_control": {"type": "ephemeral", "ttl": "1h"}},  # silently doesn't cache
]

# Fix: combine with adjacent stable content to reach ≥ 1024 tokens, or skip caching
# entirely if the prompt is too small to amortize the write cost
```

## Cost cheat sheet

For a stable prefix of T tokens reused N times/day at hit rate H:

| TTL | Write multiplier | Read multiplier | Break-even hit rate |
|---|---|---|---|
| 5m (default) | 1.25× | 0.10× | ≈ 14% |
| 1h (explicit) | 2.0× | 0.10× | ≈ 21% |

Daily input-token-equivalent cost:

```
no_cache  = T × N × 1.0
with_cache_5m  = T × (1 - H) × 1.25 + T × H × 0.10
with_cache_1h  = T × (1 - H) × 2.0  + T × H × 0.10
```

Cache writes happen on cache MISS (one per ttl window per unique prefix). Reads happen on cache HIT. The hit rate is dominated by call frequency relative to TTL.
