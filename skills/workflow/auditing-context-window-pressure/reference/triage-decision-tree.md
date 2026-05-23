# Triage decision tree

When a Claude Code session is under context pressure, the question is not "what should I do?" — it is "in what order should I try things?". Pick the cheapest move that reduces pressure before reaching for a heavier one.

## The tree

1. **Is there a single tool result > 5KB in recent history that's no longer needed verbatim?**
   - Yes → **write it to a file**, refer to that path going forward, drop the inline body
   - No → continue to (2)

2. **Is the session about to do a wide read / grep / subagent dispatch?**
   - Yes → **redirect through a subagent with a summary-only return contract** ("report findings in under 200 words"). 50-100× context savings vs. inline result
   - No → continue to (3)

3. **Is the bulk of the context conversation history (old turns), not load-bearing for the current task?**
   - Yes → **`/compact`**. Preserves intent + recent turns; loses verbatim detail of old turns
   - No → continue to (4)

4. **Did the cache hit rate just drop hard (e.g., 90% → 30%)?**
   - Yes → **inspect the cached prefix for drift**. Run `auditing-instruction-hierarchy`, check `SessionStart` hook output for dynamic content, verify no mid-session `CLAUDE.md` edits
   - No → continue to (5)

5. **Is the current task unrecoverable or genuinely complete?**
   - Yes → **`/clear`** (last resort). Full reset; loses all conversation state. Use only when the next task is independent
   - No → continue to (6)

6. **Is the CLAUDE.md hierarchy over the 250-line target?**
   - Yes → trim opportunistically; cross-reference `auditing-instruction-hierarchy` for the audit
   - No → no further action; the pressure may simply reflect a legitimately long task

## Costs ranked

| Move | Cost | Recoverable? |
|---|---|---|
| Move tool result to file | Near-zero — one Write + one path reference | Yes — file persists |
| Subagent with summary-only contract | Spawn overhead + 200-word return | Yes — full result available in subagent's own context if re-dispatched |
| `/compact` | Lose verbatim detail of older turns; preserve recent + intent | Partial — can re-fetch from files / git / disk |
| `/clear` | Lose all conversation state | No — gone |
| CLAUDE.md trim | Author edit + file commit | Yes — git history |

The principle: prefer reversible, cheap moves first. `/clear` is the nuclear option; treat it that way.

## Anti-patterns

- **Reaching for `/clear` because the session feels slow** — almost always there's a file-offload or `/compact` that solves it without losing context
- **Trimming CLAUDE.md mid-session** — invalidates the cached prefix, costing more in the next few turns than it saves
- **Running the audit's own steps as wide tool calls** — the audit itself becomes a context bloat source. Use subagent summaries
