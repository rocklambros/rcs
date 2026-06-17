---
name: auditing-instruction-hierarchy
description: >
  Audits the agent-instruction file hierarchy (managed > user > project > plugin
  scope) for size budget, cache hygiene, and drift. Checks total line count against
  the 400-line hard cap (250-line target), flags timestamps and per-run state that
  break the 5-minute prompt-cache TTL, and recommends moving dynamic content into
  hook-injected system-reminder blocks. Use when the instruction hierarchy feels
  bloated, prompt-cache hit rate is dropping, token usage seems high at session
  start, or the user is about to add a new instruction file to the hierarchy.
version: 0.1.0
status: shipped
track: claude-code-meta
audience: [skill-author, devops]
evidence:
  - RCS
  - rocks-mac-harness-QC.4b
last-updated: 2026-05-23
---

# Auditing an Instruction Hierarchy

## When to use

Trigger this skill when the user asks for or implies one of:

- "My CLAUDE.md is bloated" / "audit my CLAUDE.md" / "is my CLAUDE.md too big?"
- Token usage at session start feels high, or the prompt-cache hit rate has dropped
- The user is adding a new instruction file to `~/.claude/CLAUDE.md`, project `./CLAUDE.md`, or a plugin's `CLAUDE.md`
- "Should this rule go in CLAUDE.md or somewhere else?" — applies the size/cache filter against any candidate addition
- A plugin or fresh repo dropped a new CLAUDE.md into the hierarchy and the user wants to know the total cost

## When NOT to use

Skip this skill and hand off when:

- The user has a single CLAUDE.md under ~100 lines and no other files in the hierarchy — there's nothing to audit
- The user is starting a brand-new project and is asking what to PUT in CLAUDE.md → that's a setup question, not an audit (handoff to `setting-up-claude-md`, planned)
- The user is asking about Claude Desktop / claude.ai web UI memory, which is a different artifact than CLAUDE.md in Claude Code

## Quick start

User says: *"My CLAUDE.md hierarchy is bloated. Audit it."*

Skill response:

1. Run `wc -l ~/.claude/CLAUDE.md ./CLAUDE.md` and any plugin CLAUDE.mds; report total.
2. Compare total against the 400-line hard cap and the 250-line target.
3. Grep each file for cache-breaking patterns: timestamps, per-run identifiers, `$(date)` interpolation, anything that changes per session.
4. For each line, ask "does this need to be in EVERY cached prefix? Or can it move to a skill (loaded on demand), a hook, or a `<system-reminder>` block?"
5. Output: total line count + per-file count + cache-hygiene findings + prioritized trim list.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| user_claude_md | path | no | `~/.claude/CLAUDE.md` | The user-scope CLAUDE.md. |
| project_claude_md | path | no | `./CLAUDE.md` | The project-scope CLAUDE.md. |
| plugin_paths | list of paths | no | auto-detect under `~/.claude/plugins/` | Plugin CLAUDE.mds in the active hierarchy. |
| line_cap | integer | no | 400 | Hard cap on total hierarchy line count. |
| line_target | integer | no | 250 | Target total — anything above this is a warning, anything above `line_cap` is a fail. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as the audit progresses:

```
Audit progress:
- [ ] Step 1: Inventory — list every CLAUDE.md in the active hierarchy
- [ ] Step 2: Size budget — wc -l each + total; compare to target (250) and cap (400)
- [ ] Step 3: Cache hygiene — grep for timestamps, per-run identifiers, dynamic content
- [ ] Step 4: Per-directive — for each rule, decide: cached prefix vs skill vs hook vs system-reminder
- [ ] Step 5: Hierarchy precedence — confirm rules live at the right scope (managed > user > project > plugin)
- [ ] Step 6: Trim list — prioritized recommendations
```

### Step 1 — Inventory

The active hierarchy at session start, in precedence order:

1. **Managed** (deployment-installed) — rare; typically in MDM-managed Claude Code installs
2. **User** — `~/.claude/CLAUDE.md`
3. **Project** — `./CLAUDE.md` in the current working directory (or its ancestors up to the repo root)
4. **Plugin** — `~/.claude/plugins/<plugin>/CLAUDE.md` for each installed plugin

Confirm which of these exist before measuring.

### Step 2 — Size budget

```bash
wc -l ~/.claude/CLAUDE.md ./CLAUDE.md ~/.claude/plugins/*/CLAUDE.md 2>/dev/null
```

- **Total ≤ 250 lines** → green
- **Total 251–400 lines** → yellow; recommend trimming non-cacheable content
- **Total > 400 lines** → red; instruction-following degrades empirically past this point

Per Rock's harness QC.4b: 400 is the hard cap, 250 the target. The cap is empirical — past it, instruction following measurably drops.

### Step 3 — Cache hygiene

The prompt cache has a 5-minute TTL by default. Any content that changes between session starts invalidates the cache. Grep for:

```bash
grep -nE '(Today|current date|now\(\)|\$\{?date|UTC|Z$|session_id|run_id|[0-9]{4}-[0-9]{2}-[0-9]{2})' \
  ~/.claude/CLAUDE.md ./CLAUDE.md
```

Cache-breaking patterns to flag:

- Literal timestamps (`Today: 2026-05-23`) — the date will change tomorrow
- Per-run identifiers (session IDs, run IDs, PIDs)
- Shell interpolation that resolves dynamically (`$(date)`, `${NOW}`)
- Build / version SHAs that change on every commit

Dynamic content goes in a `<system-reminder>` block injected by a `SessionStart` hook, NOT in CLAUDE.md.

### Step 4 — Per-directive triage

For each rule in the hierarchy, ask:

| Question | If YES → keep in CLAUDE.md | If NO → move to … |
|---|---|---|
| Does Claude need to know this in every conversation, regardless of task? | yes | — |
| Is it < 3 lines and not better served by a skill? | yes | — |
| Could it be `Use when X → invoke skill Y`? | — | a skill (loaded on demand) |
| Is it a programmatic rule (allow/deny, lint, format)? | — | a hook or rule file (`.claude/rules/`, `.claude/hooks/`) |
| Does it change per session? | — | a `<system-reminder>` via `SessionStart` hook |
| Is it project-specific, not user-wide? | — | the project CLAUDE.md, not the user one |

### Step 5 — Hierarchy precedence

Each rule should live at the lowest specificity level that gets it to the right audience. Rules in `~/.claude/CLAUDE.md` load for every project; rules in `./CLAUDE.md` only when that project is active. Putting project-specific rules in the user CLAUDE.md wastes cache space on every other project.

### Step 6 — Trim list

Output a prioritized list:

- **Drop** — rules that are obsolete, never-fire, or duplicate
- **Move-to-skill** — rules whose body is workflow that should be invoked on demand
- **Move-to-hook** — programmatic rules better enforced deterministically
- **Move-to-system-reminder** — dynamic content
- **Move-to-project** — user-scope rules that are only project-relevant
- **Keep** — the cacheable, every-conversation residue

## Outputs

A markdown report:

1. **Inventory table**: file · path · line count · scope (managed / user / project / plugin)
2. **Total line count** + verdict against target (250) and cap (400)
3. **Cache-hygiene findings**: file:line · pattern · recommendation
4. **Trim list** with verdict per directive (drop / move-to-skill / move-to-hook / move-to-system-reminder / move-to-project / keep)
5. **Projected post-trim line count**

## Failure modes

- **Audit theater.** Going through the checklist without actually running `wc -l` or `grep` produces lint-flavored slop. Caught by: requiring the per-file line counts and per-finding `file:line` references in the report.
- **Counting comments and whitespace as content.** Some CLAUDE.md files are mostly section dividers and blank lines. A 400-line file that's 200 lines of blanks may still be fine, while a 200-line file of dense rules may already degrade. Caught by: reporting both raw and non-blank line counts.
- **Missing the plugin layer.** Plugin CLAUDE.mds load silently and accumulate. Caught by: Step 1 inventory explicitly lists `~/.claude/plugins/*/CLAUDE.md`.
- **Stale timestamps that survived a prior audit.** A trim run that didn't grep for date patterns leaves cache-breaking content in place. Caught by: Step 3 grep is mandatory regardless of size verdict.
- **Treating CLAUDE.md as an everything-bin.** "I just want this rule remembered" → into CLAUDE.md, indefinitely. Caught by: Step 4 forces a per-rule "could this live elsewhere?" decision.

## References

- `reference/cache-breaking-patterns.md` — full grep regex + examples of patterns that break the 5-min prompt cache
- `reference/trim-decision-tree.md` — per-directive triage tree (keep / move-to-skill / move-to-hook / ...)
- [Anthropic prompt-caching documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) — 5-min TTL, what invalidates a cache write
- [Claude Code memory hierarchy](https://code.claude.com/docs/en/memory.md) — precedence rules between managed / user / project / plugin CLAUDE.md files

## Examples

### Example 1: Bloated hierarchy (happy-path)

Input: *"My CLAUDE.md hierarchy is bloated. Audit it."*

Output: Skill runs `wc -l` on user + project + plugin CLAUDE.mds and reports e.g. 632 total lines (well past the 400-line cap). Greps for timestamps and finds two date lines in the user CLAUDE.md and one in the project file. Produces a trim list: 4 rules moved to skills, 1 timestamp moved to a `SessionStart` system-reminder, 2 project-specific rules promoted out of the user CLAUDE.md into the project one. Projected post-trim: 218 lines.

### Example 2: Timestamp in CLAUDE.md (edge-case)

Input: *"My project CLAUDE.md has a line like 'Today is 2026-05-23'. Is that OK?"*

Output: Skill flags the timestamp as cache-breaking. Explains that the literal date will be wrong tomorrow, the prompt cache TTL is 5 minutes, and the cached prefix invalidates as soon as a different date appears. Recommends moving the date to a `SessionStart` hook that injects a `<system-reminder>` block — same information reaches Claude, but the cached prefix stays stable.

### Example 3: First-time project setup (anti-trigger)

Input: *"I just started a new project. What should I put in CLAUDE.md?"*

Output: Skill explains this is a setup question, not an audit, and hands off. Audit applies to existing CLAUDE.md content (size budget, drift, cache hygiene); the user's question is greenfield. Suggests the planned `setting-up-claude-md` skill or working from a minimal template covering project-specific tooling, conventions, and any rule the project enforces that isn't already in the user-scope CLAUDE.md.

## See also

- `workflow/auditing-context-window-pressure` — broader context-bloat audit (CLAUDE.md is one of several sources)
- `claude-code-meta/authoring-skill` — for rules that should become skills instead of CLAUDE.md lines
- `claude-code-meta/writing-claude-code-hook` (planned) — for rules better enforced as `SessionStart` / `PreToolUse` hooks

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
