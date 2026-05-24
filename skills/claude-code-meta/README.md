# Claude Code Meta Track

For Claude Code skill / plugin / hook / MCP / rule authors. Meta-skills that encode how to build the kinds of things this repo itself ships.

## Shipped skills

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`authoring-skill`](authoring-skill/) | Walks the Anthropic Skill best-practices + RCS Layer-3 contract for authoring a new skill: gerund-form slug, third-person description, 11 required H2 sections, eval-first ordering | User wants to write a new skill (Claude Code, Copilot CLI, Gemini CLI, Anthropic API plugin), is reviewing a SKILL.md, or asks "is my frontmatter right?" | 18 |
| [`auditing-instruction-hierarchy`](auditing-instruction-hierarchy/) | Audits the agent-instruction file hierarchy (managed > user > project > plugin) for size budget (≤ 400 lines), cache hygiene (no timestamps in the cached prefix), and drift | CLAUDE.md feels bloated, prompt-cache hit rate is dropping, token usage seems high at session start, or the user is about to add a new instruction file | 18 |
| [`writing-mcp-server-securely`](writing-mcp-server-securely/) | Walks MCP server authoring with the six pre-trust checks baked in as design constraints from day one — SPDX license + LICENSE file, source-review-friendly code (no eval/dynamic dispatch), documented network egress, version pin discipline, env-var-only secret handling with least-privilege scopes, explicit tool subset | User is writing a new MCP server, refactoring one to pass pre-trust audit, or preparing to publish; hands off to `auditing-mcp-server-pre-trust` for consumer-side audits and skips most of the workflow for no-behavior-change republishes (which still require re-audit) | 14 |
| [`running-eval-driven-skill-development`](running-eval-driven-skill-development/) | Walks the evals-first → body → dispatch-and-judge workflow for authoring a new Claude Code skill; refuses on trivial wrappers. | New skill, plugin skill, or marketplace skill that encodes judgment / multi-step reasoning / domain expertise. | 13 |
| [`writing-deny-allow-rules`](writing-deny-allow-rules/) | Walks `.claude/rules/*.md` authoring — one rule per file, with a tool matcher, an action matcher (path glob, regex, structured input), decision (allow/deny/ask), severity, auditable rationale section, and explicit precedence (user > project > plugin; more-specific > less-specific) | User wants reviewable, version-controlled, multi-line allow/deny policy beyond what fits in a one-line settings.json entry; hands off to `update-config` for trivial single-tool allowlists and to `authoring-tool-hook` for the executor side | 13 |
| [`writing-decision-trees-as-skills`](writing-decision-trees-as-skills/) | Converts existing decision-tree expertise (test-selection trees, triage flowcharts, dispatch rules, troubleshooting trees) into deterministic walk-the-tree skills with numbered-step predicates, explicit branches, per-predicate preconditions, anti-shortcut discipline, and explicit cycle-handling (state-enrichment, state-machine, or revisit-cap) | User has a written or implicit decision tree whose predicates are objectively checkable and leaves are deterministic; refuses to encode open-judgment domains (novelty review, design critique, taste calls) as trees | 13 |
| [`authoring-tool-hook`](authoring-tool-hook/) | Walks Claude Code hook authoring across all 8 events with per-event stdin/stdout contracts, fail-open vs. fail-closed discipline, hook-as-elevated-permission-artifact security review, mandatory HTTP-egress timeout + client-side caching with bounded TTL, and matcher-scoping discipline | User is writing a runtime hook script to gate tool calls, audit session starts, log conversations, or enforce a deny rule; hands off to declarative settings for statusline / theme / model configuration | 12 |
| [`authoring-plugin`](authoring-plugin/) | Walks Claude Code plugin authoring — `.claude-plugin/plugin.json` manifest, `marketplace.json` entry, auto-discovered `skills/` + `commands/` + `agents/` subdirs vs. explicitly-registered `hooks/` + `rules/`, version pinning, lifecycle metadata, and the security review every bundled hook and MCP server needs before publication | User has 2+ artifacts to bundle (skills + commands + agents + hooks + MCP servers), wants to publish to a marketplace, or asks how to package artifacts for distribution; hands off to `authoring-skill` for single-skill cases | 11 |

## Drafting skills

_No drafting skills in the claude-code-meta track. `authoring-tool-hook` promoted to shipped at v0.2.0 via the v6.0.2 promotion pass after Workflow reorder + new top-level HTTP-egress step._

## Planned skills

_All v1-planned claude-code-meta skills shipped in v6-batch-4 and v6-batch-6. Note: `writing-claude-code-plugin` shipped as `authoring-plugin` and `writing-claude-code-hook` shipped as `authoring-tool-hook` — the `claude` reserved word is rejected by the frontmatter linter._

## Cross-track references

- Skill-authoring discipline pairs with `workflow/auditing-context-window-pressure` (cache hygiene) and `workflow/running-adversarial-premortem` (premortem your skill before shipping).
- For security-critical skills (MCP servers, hooks that wield permissions), see `security/auditing-mcp-server-pre-trust` and the publisher-side `claude-code-meta/writing-mcp-server-securely`.
- `authoring-plugin` is the bundling discipline; the four per-artifact authoring skills (`writing-mcp-server-securely`, `authoring-tool-hook`, `writing-deny-allow-rules`, `writing-decision-trees-as-skills`) cover the artifacts a plugin can ship; `running-eval-driven-skill-development` is the test-first wrapper that complements `authoring-skill`.
