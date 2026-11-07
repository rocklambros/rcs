Differences from the Claude Code source:

- Authority: for Codex-specific format questions, `~/.codex/skills/.system/skill-creator` wins over this skill. This skill adds the RCS Layer-3 contract (gerund slug, 11 H2 sections, eval-first discipline, provenance fields) on top of it.
- Canonical source: RCS skills are authored in RCS format under `~/github_projects/RCS/skills/` and ported to Codex with `tools/port_to_codex.py`, which nests the custom fields under `metadata` and writes `agents/openai.yaml`. A Codex-only skill can skip the RCS source and use the Codex template directly.
- Eval runs: run each eval scenario against a fresh `spawn_agent` subagent, collect it with `wait_agent`, then `close_agent`. If multi-agent tools are unavailable, say so and run the scenarios yourself in separate clearly labeled passes.
- Sibling skills are invoked as `$skill-name`. Skills named here that are not installed under `~/.codex/skills` belong to the Claude Code library. Apply the named guidance inline instead of invoking them.
