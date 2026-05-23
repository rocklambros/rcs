# Claude Tier Cheat Sheet

Quick-lookup for per-task tier recommendation. All numbers are illustrative defaults; verify against current Anthropic pricing and your own latency measurements before shipping.

## Tier capability bands (Claude 4.x)

| Tier | Model id | Best for | Avoid for |
|---|---|---|---|
| Haiku 4.5 | `claude-haiku-4-5-20251001` | Low-latency classification, extraction, summarization, simple tool calls, format conversions | Open-ended planning, deep code reasoning, multi-hop synthesis |
| Sonnet 4.6 | `claude-sonnet-4-6` | RAG synthesis, multi-step tool use, judge / evaluator, code generation, planning with bounded scope | Highest-stakes reasoning where the marginal Opus uplift matters |
| Opus 4.7 | `claude-opus-4-7` | Open-ended planning, deep code reasoning, novel-problem decomposition, math / proof, agentic loops with > 5 tool calls | Latency-critical UI paths, simple classification, cost-sensitive batch jobs |

All three share the 200k context window.

## Pricing snapshot (per million tokens)

| Tier | Input | Output | Cache write (5m) | Cache write (1h) | Cache read |
|---|---|---|---|---|---|
| Haiku 4.5 | $1 | $5 | $1.25 | $2 | $0.10 |
| Sonnet 4.6 | $3 | $15 | $3.75 | $6 | $0.30 |
| Opus 4.7 | $15 | $75 | $18.75 | $30 | $1.50 |

Verify at https://docs.claude.com/en/docs/about-claude/models — prices change.

## Latency snapshot (P50, 5k input + 1k output)

| Tier | P50 | P95 (estimated) |
|---|---|---|
| Haiku 4.5 | ~1.0 s | ~2.0 s |
| Sonnet 4.6 | ~2.5 s | ~5.0 s |
| Opus 4.7 | ~5.0 s | ~10.0 s |

Streaming first-token latency is roughly similar across tiers (~300–600 ms); total wall time is dominated by output token count × per-token decode speed.

## Per-task baseline tier (from SKILL.md Step 3)

| Task | Low reasoning depth | Medium | High |
|---|---|---|---|
| Classification (≤ 10 labels) | Haiku | Sonnet | Sonnet |
| Classification (> 10 labels) | Sonnet | Sonnet | Opus |
| Extraction (entities, fields) | Haiku | Sonnet | Sonnet |
| Summarization (single doc) | Haiku | Sonnet | Sonnet |
| Summarization (multi-doc) | Sonnet | Sonnet | Opus |
| RAG synthesis | Sonnet | Sonnet | Opus |
| Planning (bounded scope) | Sonnet | Sonnet | Opus |
| Planning (open-ended) | Sonnet | Opus | Opus |
| Tool use (single tool, simple) | Haiku | Sonnet | Sonnet |
| Tool use (multi-step agent) | Sonnet | Sonnet | Opus |
| Code generation (single function) | Sonnet | Sonnet | Opus |
| Code generation (cross-file refactor) | Opus | Opus | Opus |
| Judge / evaluator | Sonnet | Sonnet | Sonnet |
| Rewrite / style change | Haiku | Haiku | Sonnet |
| Translation | Haiku | Sonnet | Sonnet |

## Modifiers

Apply on top of the baseline tier. Modifiers compose.

| Modifier | Effect |
|---|---|
| Safety-critical (moderation, security, regulated decision) | +1 tier |
| Same-family cache lineage (Claude Code subagent of parent) | Match parent's tier |
| Latency P95 budget < 1500 ms | −1 tier (if eval permits) |
| Latency P95 budget > 4000 ms | No constraint from latency |
| Cost target = minimize | −1 tier + add escalation rule |
| Cost target = quality-first | +1 tier (cap at Opus) |
| Context-window pressure > 75% | No tier change; add cache_control (see auditing-prompt-token-budget) |
| Output must be structured JSON | No tier change; add schema-validation + escalate-on-fail |
| Judge for an LLM-as-judge eval | Sonnet, NOT same family as candidate model under test |

## Escalation rules (Step 5 reference)

| Task type | Trigger to escalate |
|---|---|
| Classification with confidence | confidence < 0.7 or "unknown" label |
| Structured output | JSON schema validation fails |
| RAG synthesis | faithfulness score below threshold |
| Code generation | generated code fails unit tests |
| Agentic loop | N consecutive tool failures or turn budget exceeded |
| Tool use | tool call returns error / no match |

Default escalation target: next tier up. Track escalation rate; if > 30% of calls, the downgrade is too aggressive.

## Same-family cache lineage (Claude Code subagents)

The Anthropic prompt cache is partitioned by model family. A Claude Code parent session on Opus 4.7 that dispatches a subagent on Sonnet 4.6 does NOT share the parent's cached prefix; the subagent pays the full input-token cost on its first call.

| Parent | Subagent | Cache shared? |
|---|---|---|
| Opus 4.7 | Opus 4.7 | Yes |
| Opus 4.7 | Sonnet 4.6 | No |
| Opus 4.7 | Haiku 4.5 | No |
| Sonnet 4.6 | Sonnet 4.6 | Yes |
| Sonnet 4.6 | Haiku 4.5 | No |

For subagent-heavy Claude Code workflows, match parent's tier unless the cost savings on the subagent's own input clearly outweigh the lost cache reads. Worked example: parent's cached prefix = 20k tokens; subagent makes 10 calls; matching the parent's tier costs 10 × 20k × 0.10 = 20k token-equivalents (cache reads). Going one tier down costs 10 × 20k × 1.0 = 200k token-equivalents (full reads). The cache-lineage saving usually dominates the per-token tier difference.

## Anti-patterns

- Single tier across a heterogeneous pipeline (one of Haiku/Sonnet/Opus for all stages)
- Downgrading without an escalation rule
- Downgrading without a per-task eval
- Picking tier from a single generic benchmark (MMLU, HumanEval) instead of the actual task's eval
- Using same-family judge for same-family candidate in an LLM-as-judge eval (bias)
- Mismatched subagent family in a cache-sensitive Claude Code session
