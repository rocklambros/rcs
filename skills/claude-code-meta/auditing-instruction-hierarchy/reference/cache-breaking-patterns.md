# Cache-breaking patterns in CLAUDE.md

The prompt cache has a 5-minute default TTL. Any content that changes between session starts invalidates the cached prefix. The cost: the next session pays the full re-read instead of a cache hit.

## Patterns to grep for

| Pattern | Example | Why it breaks |
|---|---|---|
| ISO date literal | `Today: 2026-05-23` | Will not match tomorrow's session prefix |
| Wall-clock time | `Last run: 14:32 UTC` | Changes every session |
| Session / run identifiers | `Session ID: abc-123` | Unique per session — guarantees a miss |
| Process / PID references | `PID 7821` | Re-runs use a different PID |
| Shell interpolation | `$(date +%F)`, `${HOME}`, `$USER` | Resolves dynamically |
| Build SHAs | `Commit: 31f220b` | Changes on every commit |
| Counter / sequence | `Run #4`, `Iteration 12` | Increments per run |
| Random tokens | `nonce: 0xABCDEF` | Different every time |
| Today-relative phrases | `As of today`, `Currently`, `Right now` | Drift over time even without an explicit date |

## Recommended grep

```bash
grep -nE '(Today|current date|now\(\)|\$\(date|\$\{?date|UTC|[0-9]{4}-[0-9]{2}-[0-9]{2}|session_id|run_id|PID [0-9]+|nonce)' \
  ~/.claude/CLAUDE.md ./CLAUDE.md ~/.claude/plugins/*/CLAUDE.md 2>/dev/null
```

## What to do with a finding

For each cache-breaking line, choose:

1. **Delete** — if the info is decoration, not load-bearing
2. **Move to a `SessionStart` hook** — if the info needs to reach Claude at session start but can be computed at that moment (date, branch name, etc.) and injected via a `<system-reminder>` block
3. **Move to a runtime tool** — if Claude can fetch it on demand (run `date`, run `git status`)

The pattern: cached prefix stays stable, dynamic content rides in via `<system-reminder>` blocks that the runtime injects fresh each session.

## What stable content looks like

Stable, cacheable lines are descriptive and time-invariant:

- "I am a cybersecurity engineer." ← stable
- "I am a cybersecurity engineer as of 2026-05-23." ← cache-breaking

- "Pin all installs." ← stable
- "Pin all installs (we got bitten by an unpinned upgrade in March 2026)." ← debatable — the why is stable, but if it changes monthly, the line is at risk

The test: would this line read the same tomorrow, next week, next month? If no, it's dynamic content and belongs in a hook injection, not the cached prefix.
