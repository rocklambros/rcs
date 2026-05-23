# Changelog

All notable changes to RCS are documented here. Per-skill changes use the skill's SemVer; repo-level batch tags mark release groupings.

## [Unreleased]

### Added (Phase 0 — Bootstrap)

- Repo skeleton, root README, LICENSE (MIT), CONTRIBUTING.md
- `docs/conventions.md`, `docs/eval-protocol.md`, `docs/governance.md`
- `tools/lint_frontmatter.py`, `tools/lint_skill_md.py`, `tools/lint_links.py`, `tools/run_evals.py`
- `.github/workflows/frontmatter-lint.yml`, `link-check.yml`, `eval-suite.yml`
- All 5 track READMEs with planned-skills tables populated from the full ~80-skill universe

### Added (Phase 1 — Free ships, status: drafting pending eval validation)

- `workflow/running-adversarial-premortem` v0.1.0 — migrated from `~/.claude/skills/adversarial-premortem.skill`; eval validation deferred
- `security/auditing-mcp-server-pre-trust` v0.1.0 — migrated from `~/.claude/skills/mcp-server-pre-trust-audit/`; eval validation deferred
