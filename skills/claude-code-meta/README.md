# Claude Code Meta Track

For Claude Code skill / plugin / hook / MCP / rule authors. Meta-skills that encode how to build the kinds of things this repo itself ships.

## Shipped skills

_Populated in Phase 6._

| Skill | What it does | When to use | Σ |
|---|---|---|---|

## Planned skills

| Skill | What it does | Σ | Status |
|---|---|---|---|
| `writing-claude-code-skill` | Walks the Anthropic best-practices checklist; eval-first workflow; Layer-3 H2 contract | 18 | 📝 planned (Phase 6) |
| `auditing-claude-md-hierarchy` | Size check (≤ 400 lines), cache hygiene (no timestamps), drift detection | 18 | 📝 planned (Phase 6) |
| `writing-claude-code-plugin` | marketplace.json + commands + agents + hooks + lifecycle | 11 | 📝 planned |
| `writing-mcp-server-securely` | Six-check audit baked into the authoring workflow | 14 | 📝 planned |
| `writing-claude-code-hook` | PreToolUse / PostToolUse / Stop / SessionStart patterns with security review | 12 | 📝 planned |
| `writing-deny-allow-rules` | `.claude/rules/*.md` allow/deny rule authoring with glob path matching | 13 | 📝 planned |
| `writing-decision-trees-as-skills` | Meta: convert "given data shape X, do Y" expertise into a deterministic walk | 13 | 📝 planned |
| `running-eval-driven-skill-development` | Per Anthropic best-practices: write 3 evals BEFORE the SKILL.md body | 13 | 📝 planned |

## Cross-track references

- Skill-authoring discipline pairs with `workflow/auditing-context-window-pressure` (cache hygiene) and `workflow/running-adversarial-premortem` (premortem your skill before shipping).
- For security-critical skills (MCP servers, hooks that wield permissions), see `security/auditing-mcp-server-pre-trust`.
