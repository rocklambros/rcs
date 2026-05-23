# Claude Code Meta Track

For Claude Code skill / plugin / hook / MCP / rule authors. Meta-skills that encode how to build the kinds of things this repo itself ships.

## Shipped skills

| Skill | What it does | When to use | Σ |
|---|---|---|---|
| [`authoring-skill`](authoring-skill/) | Walks the Anthropic Skill best-practices + RCS Layer-3 contract for authoring a new skill: gerund-form slug, third-person description, 11 required H2 sections, eval-first ordering | User wants to write a new skill (Claude Code, Copilot CLI, Gemini CLI, Anthropic API plugin), is reviewing a SKILL.md, or asks "is my frontmatter right?" | 18 |
| [`auditing-instruction-hierarchy`](auditing-instruction-hierarchy/) | Audits the agent-instruction file hierarchy (managed > user > project > plugin) for size budget (≤ 400 lines), cache hygiene (no timestamps in the cached prefix), and drift | CLAUDE.md feels bloated, prompt-cache hit rate is dropping, token usage seems high at session start, or the user is about to add a new instruction file | 18 |

## Planned skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `writing-claude-code-plugin` | marketplace.json + commands + agents + hooks + lifecycle | 11 | 📝 planned |
| `writing-mcp-server-securely` | Six-check audit baked into the authoring workflow | 14 | 📝 planned |
| `writing-claude-code-hook` | PreToolUse / PostToolUse / Stop / SessionStart patterns with security review | 12 | 📝 planned |
| `writing-deny-allow-rules` | `.claude/rules/*.md` allow/deny rule authoring with glob path matching | 13 | 📝 planned |
| `writing-decision-trees-as-skills` | Meta: convert "given data shape X, do Y" expertise into a deterministic walk | 13 | 📝 planned |
| `running-eval-driven-skill-development` | Per Anthropic best-practices: write 3 evals BEFORE the SKILL.md body | 13 | 📝 planned |

## Cross-track references

- Skill-authoring discipline pairs with `workflow/auditing-context-window-pressure` (cache hygiene) and `workflow/running-adversarial-premortem` (premortem your skill before shipping).
- For security-critical skills (MCP servers, hooks that wield permissions), see `security/auditing-mcp-server-pre-trust`.
