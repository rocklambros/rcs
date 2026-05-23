# Trim decision tree

For each rule in any CLAUDE.md, walk this tree to decide whether it belongs in the cached prefix or somewhere else.

## The tree

1. **Is the rule load-bearing in EVERY conversation, regardless of task?**
   - Yes → continue to (2)
   - No → goto (3)

2. **Is the rule under ~3 lines AND not better served as a discoverable skill?**
   - Yes → **keep in CLAUDE.md** (the cached prefix is exactly where it belongs)
   - No → goto (3)

3. **Can the rule be expressed as `Use when X → invoke skill Y`?**
   - Yes → **move to a skill**. Replace the CLAUDE.md content with a 1-line pointer; let the skill load on demand
   - No → continue to (4)

4. **Is the rule a programmatic gate (allow / deny / lint / format)?**
   - Yes → **move to a hook or rule file**. `.claude/rules/*.md`, `.claude/hooks/*.sh`, or `.claude/hooks/*.py` enforce deterministically; CLAUDE.md hopes the model complies
   - No → continue to (5)

5. **Does the rule's content change per session (date, branch, env)?**
   - Yes → **move to a `<system-reminder>` injected by a `SessionStart` hook**. Cached prefix stays stable; the dynamic line rides in fresh each session
   - No → continue to (6)

6. **Is the rule only relevant to one specific project (not user-wide)?**
   - Yes → **move to the project `./CLAUDE.md`** if it currently lives in the user CLAUDE.md. Per-project rules in the user file waste cache on every other project
   - No → continue to (7)

7. **Is the rule duplicated by another file in the hierarchy?**
   - Yes → **drop the duplicate**. Pick the highest-precedence canonical location; remove the other(s)
   - No → **keep**, but flag for re-review next audit if total line count is still over target

## Worked example

Hypothetical user CLAUDE.md contains:

```
1. The current date is 2026-05-23.
2. I use Python 3.13 with uv.
3. When auditing GraphQL schemas, check for introspection exposure, depth limits, and field-level auth.
4. Never run `git push --force-with-lease` on main without confirmation.
5. The project rocky-deploy uses kubectl context `prod-us-east`.
6. Pin all install commands.
7. Today's stand-up is at 09:30 UTC.
```

Walking the tree:

| Line | Walk | Verdict |
|---|---|---|
| 1 | (5) yes — dynamic | Move to SessionStart `<system-reminder>` |
| 2 | (1) yes, (2) yes | Keep |
| 3 | (3) yes | Move to a `auditing-graphql-schemas` skill |
| 4 | (4) yes | Move to a `.claude/rules/no-force-push-main.md` |
| 5 | (6) yes — project-specific | Move to `rocky-deploy/CLAUDE.md` |
| 6 | (1) yes, (2) yes | Keep |
| 7 | (5) yes — dynamic | Drop (or system-reminder; depends on whether Claude actually needs to know) |

Original: 7 lines. Post-trim: 2 lines in user CLAUDE.md (#2 and #6). Everything else lives in a more specific, cache-friendly, or programmatic location.
