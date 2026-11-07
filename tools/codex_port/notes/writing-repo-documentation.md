Differences from the Claude Code source:

- Style rules: Codex does not load `~/.claude/CLAUDE.md`, so the house style rules that the source skill pointed to are written out in Step 6 and in `reference/ai-slop-patterns.md`. A repo-level `AGENTS.md` overrides them where the two conflict.
- Cold-read test (Step 7): a fresh subagent from `spawn_agent` is the closest stand-in for a human cold reader because it starts with no project context. Give it only the document under test. Collect the result with `wait_agent`, then `close_agent`. If multi-agent tools are unavailable, say so and fall back to the 24-hour-gap self-read. A model cold read does not replace a human one for the novice tier.
- Sibling skills are invoked as `$skill-name`. Skills named here that are not installed under `~/.codex/skills` belong to the Claude Code library. Apply the named guidance inline instead of invoking them.
- File edits: draft documents with `apply_patch` in the target repository. Do not write outside the repository without confirmation.
