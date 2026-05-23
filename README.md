# Rock's Claude Skills (RCS)

Production-quality Claude Code skills for AI security researchers, data scientists, and ML engineers. Every skill encodes a discipline that would otherwise be rebuilt from scratch each project — statistical-test selection, leakage firewalls, seed hygiene, MCP pre-trust audits, adversarial premortems. Catalog-free by design: no bundled framework controls, no ISO mirrors, no drift to maintain. Methodology only.

## Audience routing

- **Security engineer or AI red-teamer?** Start with `skills/security/`.
- **Data scientist, ML engineer, or stats student?** Start with `skills/ml-datasci/`.
- **Researcher working across both?** Start with `skills/workflow/` (cross-cutting hygiene).
- **Instructor or TA?** Start with `skills/teaching/` (pedagogy patterns).
- **Claude Code skill author?** Start with `skills/claude-code-meta/`.

## Install

### Claude Code

Clone and symlink each skill you want into `~/.claude/skills/`:

```bash
git clone https://github.com/rockcyber/rcs.git
cd rcs
for skill in skills/*/*/; do
  name=$(basename "$skill")
  ln -s "$(pwd)/$skill" "$HOME/.claude/skills/$name"
done
```

### Copilot CLI, Gemini CLI, Anthropic API

The `skills/<track>/<name>/SKILL.md` files follow the Anthropic Skills format and work in any host that supports the spec. Symlink or copy the directories into your tool's skill discovery path. For the Anthropic API, upload via the SDK per the Skills guide.

## Skill catalog

| Skill | Track | What it does | Status | Σ |
|---|---|---|---|---|
| [`running-adversarial-premortem`](skills/workflow/running-adversarial-premortem/) | workflow | Multi-round adversarial premortem on spec / plan / paper / proof / codebase | 🔨 drafting | 17 |
| [`auditing-mcp-server-pre-trust`](skills/security/auditing-mcp-server-pre-trust/) | security | Six-check audit before registering an MCP server | 🔨 drafting | 18 |

_2 of ~80 planned skills authored (currently `drafting`; pending eval validation). See each track's README for the planned-skills roadmap._

## Governance

- **License:** MIT (see `LICENSE`)
- **Contributing:** See `CONTRIBUTING.md` — eval-first workflow, gerund naming, no AI attribution
- **Versioning:** SemVer per skill (`frontmatter.version`) + loose repo-level batch tags (`v1`, `v1.1`, ...)
- **Documentation contract:** See `docs/conventions.md`

## Acknowledgments

Skill design follows the [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) document and the patterns demonstrated by the official `anthropics/claude-code` skills, `obra/superpowers`, and `affaan-m/everything-claude-code` repos.

## Disclaimer

Skills are tooling, not advice. They encode disciplines and decision trees observed in real research and engineering practice. Verify outputs against authoritative sources before relying on them in regulated or safety-critical contexts.
