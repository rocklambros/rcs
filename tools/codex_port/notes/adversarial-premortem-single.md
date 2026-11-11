Tool mapping for Codex:

- Subagents: use Codex multi-agent tools. `spawn_agent` launches one perspective or fix worker, `wait_agent` collects results, `close_agent` releases the thread. Invoking this skill is the explicit user request to spawn subagents. Issue all of a round's `spawn_agent` calls before the first `wait_agent` so they run concurrently. Concurrency is capped by `[agents] max_threads` in `~/.codex/config.toml`. If the cap is below the round size, run the round in batches. Subagents do not spawn their own subagents, so cross-attack and adjudication stay in the orchestrator.
- If multi-agent tools are unavailable (`multi_agent` feature off), run each perspective as a separate, clearly labeled pass in one context, in sequence. Structure and output do not change.
- Cheaper subagent model: define an agent role in `~/.codex/config.toml` pointing to a smaller model and pass that role to `spawn_agent`. Keep the orchestrator on the stronger model.
- Structured reasoning: use a sequential-thinking MCP server if one is configured in Codex. Otherwise keep the reasoning chain explicit as numbered steps.
- Sibling skills are invoked as `$skill-name`. Skills named here that are not installed under `~/.codex/skills` belong to the Claude Code library. Apply the named check inline instead.
