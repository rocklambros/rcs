---
name: auditing-context-window-pressure
description: >
  Audits a Claude Code (or Anthropic API) session for context-window pressure — total
  context usage as a percentage of the 200k window, prompt-cache hit rate, CLAUDE.md
  hierarchy size, tool-result bloat, system-reminder accumulation, and conversation-history
  compression triggers. Produces a prioritized triage plan (move large tool results
  to files, dispatch subagents with summary-only return contracts, /compact, /clear).
  Use when the session feels slow, prompt-cache hit rate is dropping, token cost
  seems high, or before starting a long-running multi-turn workflow.
version: 0.1.0
status: drafting
track: workflow
audience: [skill-author, devops, ml-engineer]
evidence:
  - RCS
  - rocks-mac-harness-QC.4b
last-updated: 2026-05-23
---

# Auditing Context-Window Pressure

## When to use

Trigger this skill when the user asks for or implies one of:

- "My session is slow" / "tokens are spiking" / "context feels bloated"
- The prompt-cache hit rate has dropped (was 90%, now 30%) — even if speed is OK
- The user is about to start a long-running multi-turn workflow (eval suite, agent loop, long-form authoring) and wants to right-size the session first
- "Should I /compact or /clear?" — the skill picks the right triage step
- The user pastes a large file or runs a wide grep and notices the response slowing

## When NOT to use

Skip this skill and hand off when:

- The session is < 10 turns and feels fine — no pressure to audit
- The user is making a one-shot Anthropic API call from a script (not Claude Code) — check the API response token counts directly; the multi-turn pressure model doesn't apply
- The user wants to debug a specific tool's output volume, not the whole session — that's a tool-level review, not a context audit

## Quick start

User says: *"My Claude Code session is slow and feels like it's using too much context. Help me audit it."*

Skill response:

1. Estimate total context usage as % of the 200k window. If > 75%, activate token-efficient mode immediately.
2. Check prompt-cache hit rate — if < 70%, investigate cache-prefix changes (CLAUDE.md edits mid-session, timestamp leaks, dynamic content in cached blocks).
3. Audit CLAUDE.md hierarchy size (cross-reference `auditing-instruction-hierarchy`).
4. Identify tool-result bloat — large file reads, wide greps, subagent outputs > 5KB.
5. Produce a triage list: move bloat to files, dispatch summary-only subagents, `/compact`, `/clear` (last resort).

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| context_pct | float (0–100) | no | (estimated) | Best estimate of % of the 200k context window in use. The skill works without an exact number but is more actionable with one. |
| cache_hit_rate | float (0–100) | no | (estimated) | Recent prompt-cache hit rate. Below 70% triggers the cache-prefix investigation branch. |
| session_turns | integer | no | — | How many user turns so far. Below ~10 turns the skill does not apply (see When NOT to use). |
| triage_budget | "minimal" \| "thorough" | no | "thorough" | "minimal" returns only the top recommendation; "thorough" walks the full audit. |

## Workflow

Copy this checklist into the response and check off items as the audit progresses:

```
Audit progress:
- [ ] Step 1: Total context % — over 75% triggers token-efficient mode
- [ ] Step 2: Cache hit rate — under 70% triggers prefix-drift investigation
- [ ] Step 3: CLAUDE.md hierarchy size — cross-ref auditing-claude-md-hierarchy
- [ ] Step 4: Tool-result bloat — large reads, wide greps, subagent outputs > 5KB
- [ ] Step 5: System-reminder accumulation — dynamic content in cached prefix
- [ ] Step 6: Compression triggers — does conversation history need /compact?
- [ ] Step 7: Triage plan — file-offload, subagent-summary, /compact, /clear
```

### Step 1 — Total context %

Estimate (or read from a runtime indicator if available) the share of the 200k context window currently in use. Bands:

- **< 50%** → green; the audit is mostly diagnostic
- **50–75%** → yellow; trim opportunistically
- **75–90%** → red; activate token-efficient mode + trim before next major operation
- **> 90%** → critical; the next large operation may fail; `/compact` or `/clear` now

### Step 2 — Cache hit rate

The prompt cache buys speed and cost. A drop from 90% to 30% means the cached prefix is invalidating. Causes, in order of likelihood:

1. **CLAUDE.md edited mid-session** — even a comment change rewrites the cached prefix
2. **Timestamp / dynamic content leaked into the cached prefix** — see `auditing-instruction-hierarchy`
3. **A `<system-reminder>` block that's supposed to be dynamic ended up in the cached portion** — check hook output ordering
4. **A plugin was installed / removed mid-session** — the plugin layer of CLAUDE.md changed
5. **Model switched mid-session** — Opus / Sonnet / Haiku do not share cache; the new model starts cold

### Step 3 — CLAUDE.md hierarchy size

Cross-reference the `auditing-instruction-hierarchy` skill. If the hierarchy is over 400 lines or has cache-breaking content, the session pays for it on every cache miss. Recommend running that audit if the line count exceeds 250.

### Step 4 — Tool-result bloat

Tool results that exceed ~5KB inflate context fast and stay in conversation history until compressed. Common culprits:

- Reading a large file in full when only a slice was needed — use `Read` with offset/limit
- Wide `grep` / `find` that returned hundreds of matches — narrow the pattern or pipe through `head`
- Subagent dispatches that returned the full work product instead of a summary — change the return contract to "report findings in under 200 words"
- Notebook outputs / huge JSON dumps — write to a file and refer by path

For each tool result over 5KB in recent history: was the full body needed, or could it have been a file path + summary?

### Step 5 — System-reminder accumulation

Each session-start hook injects a `<system-reminder>` block. Some hooks fire repeatedly (e.g., periodic reminders). Confirm:

- Reminders that should fire once per session aren't firing per turn
- Reminders fire OUTSIDE the cached prefix, not inside it
- The total volume of system-reminder content per session is bounded

### Step 6 — Compression triggers

Claude Code auto-compresses old turns past a threshold. The choice between `/compact` and `/clear`:

- **`/compact`** — in-place compression, preserves intent + recent context, loses verbatim detail
- **`/clear`** — full reset, loses all conversation context; use only when starting a genuinely new task

The asymmetric cost: compression-then-decompression on the next pass is cheaper than carrying continuous bloat indefinitely.

### Step 7 — Triage plan

Output a prioritized list:

1. **Move bloat to files** — for any tool result > 5KB still relevant, write to a file and reference by path
2. **Dispatch summary-only subagents** — re-do recent wide reads via subagent with "report in under 200 words"
3. **`/compact`** — if conversation history is the bulk of the context and the current task is mid-flight
4. **`/clear`** — only if starting a new task or the current task is unrecoverable
5. **CLAUDE.md trim** — if Step 3 surfaced a hierarchy over budget

## Outputs

A markdown report:

1. **Pressure snapshot**: total context %, cache hit rate, CLAUDE.md hierarchy line count, count of tool results > 5KB
2. **Findings table**: source · pressure · evidence · recommendation
3. **Triage plan** in priority order, each step with expected pressure reduction
4. **When to re-audit** — concrete signal that should trigger a follow-up (e.g., after a wide grep, after a model switch)

## Failure modes

- **Audit-by-vibes.** Reporting "context feels high" without measuring %. Caught by: Step 1 requires a numeric estimate, even if rough.
- **Treating /clear as a default.** `/clear` loses the current task state; recommending it casually wastes work. Caught by: Step 6 explicitly orders `/compact` before `/clear`.
- **Missing the model-switch cause.** A cache-rate drop right after Opus → Sonnet (or vice versa) is expected — different model caches. Caught by: Step 2 enumerates model switch as a cause to rule out.
- **Trimming CLAUDE.md as the first move.** CLAUDE.md is one source of pressure; tool-result bloat is often the larger lever in long sessions. Caught by: Step 4 measures tool-result bloat in parallel with Step 3.
- **Re-running the wide grep that caused the bloat.** "Audit" then re-runs the offending command in service of the audit. Caught by: subagent-summary pattern in Step 7 means the audit reproduces findings via summaries, not full re-reads.

## References

- `reference/triage-decision-tree.md` — when to /compact vs /clear vs file-offload vs subagent-summary
- `reference/tool-result-budget.md` — per-tool guidance on staying under ~5KB
- [Anthropic prompt-caching documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) — TTL, hit / miss behavior, what invalidates a write
- [Claude Code context-management docs](https://code.claude.com/docs/en/context-management.md) — /compact, /clear, conversation compression
- RCS `skills/claude-code-meta/auditing-instruction-hierarchy/` — companion audit specifically for the instruction-file size + cache-hygiene dimension

## Examples

### Example 1: Slow session (happy-path)

Input: *"My Claude Code session is slow and feels like it's using too much context. Help me audit it."*

Output: Skill estimates context at ~80% of 200k (over the 75% threshold; activate token-efficient mode). Checks cache hit rate — recent drop from 90% to 45% after a mid-session `CLAUDE.md` edit. Notes 4 tool results over 5KB (two wide greps, one large file read, one subagent that returned its full transcript). Triage: move the large file read to disk and reference by path; re-dispatch the noisy subagent with "report in under 200 words"; consider `/compact` after the current task lands. Recommends running `auditing-instruction-hierarchy` because the hierarchy is at 412 lines.

### Example 2: Cache-rate cliff (edge-case)

Input: *"My prompt cache hit rate just dropped from 90% to 30%. Why?"*

Output: Skill walks the cache-prefix-change diagnostic. Asks whether CLAUDE.md was edited (most likely cause), whether a plugin was added/removed, whether a model switch happened, and whether any dynamic content (timestamps, session IDs) leaked into the cached portion. Recommends inspecting recent changes to the user / project CLAUDE.md and any `SessionStart` hook output for new lines that vary per session.

### Example 3: One-shot API call (anti-trigger)

Input: *"I'm making a quick 3-message API call from a Python script. Audit the context."*

Output: Skill explains the audit is for long-running, multi-turn Claude Code sessions where pressure accumulates over time. A 3-message API call has no meaningful pressure; the right move is to check the API response's reported `usage.input_tokens` / `usage.output_tokens` / cache fields directly. Hands off — no full audit needed.

## See also

- `claude-code-meta/auditing-claude-md-hierarchy` — the CLAUDE.md half of context pressure
- `claude-code-meta/authoring-skill` — skills load on demand and reduce cached-prefix pressure compared to inline rules
- `workflow/running-adversarial-premortem` — premortem long-running workflows before they bloat

## Status & version

- Status: drafting
- Version: 0.1.0
- Last-updated: 2026-05-23
- Drafting reason: Sonnet eval 01-slow-session scored 2/3 — the triage plan in the response led with `/compact` and CLAUDE.md trim but did not surface subagent-summary or file-offload as triage steps, even though the SKILL.md teaches both. Awaiting re-eval after a body revision that strengthens the subagent-summary signal.
