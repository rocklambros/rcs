# Tool-result budget

Tool calls return text into the conversation. That text stays there until compressed. Budgeting per-tool keeps the session from drifting into the 75%+ pressure zone.

## Rule of thumb

| Tool | Soft budget per call | If over budget |
|---|---|---|
| `Read` | 5KB | Use `offset` / `limit` to slice; read only the needed lines |
| `Grep` | 5KB / 100 matches | Narrow the pattern, scope to a path, pipe through `head` |
| `Glob` | 200 paths | Narrow the glob; if you need every match, summarize the list inline ("matched 1247 paths under src/...") |
| `Bash` | 5KB | Pipe through `head`, `tail`, `wc`, or redirect to a file (`> /tmp/out.txt`) and reference by path |
| `WebFetch` | 10KB | Use the `prompt` parameter to ask the fetch to summarize on the way back |
| Subagent (`Agent` tool) | 1KB return | Set a return contract — "report in under 200 words" — so the subagent summarizes its own work product |

The 5KB number is empirical, not a hard line. Past it, conversation history dominates context usage in long sessions.

## Patterns that blow the budget

### Reading a whole large file

```
# ❌ Bad
Read("/path/to/3000-line-config.yaml")

# ✅ Better
Read("/path/to/3000-line-config.yaml", offset=850, limit=120)
# or, if you genuinely need the whole thing:
Bash("wc -l /path/to/3000-line-config.yaml; sha256sum /path/to/3000-line-config.yaml")
# then refer to the file by path going forward
```

### Wide grep

```
# ❌ Bad — returns every match in the repo
Grep("function")

# ✅ Better — narrow + bound
Grep("^async function", glob="src/**/*.ts", head_limit=20)
```

### Subagent returns its full transcript

```
# ❌ Bad — no return contract
Agent({prompt: "Investigate the auth flow and report"})

# ✅ Better — explicit contract
Agent({prompt: "Investigate the auth flow. Report findings in under 200 words: list each issue with file:line, severity, recommended fix."})
```

## When the budget is right to break

Some operations genuinely need the full body:

- A code review where the diff IS the artifact under inspection
- A SKILL.md authoring pass where the whole file is being rewritten
- A one-shot fact extraction where the source must be quoted

For these cases, do the full read once, complete the work, and then opportunistically `/compact` after the result lands — don't carry the verbatim body through the rest of the session.
