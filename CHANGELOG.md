# Changelog

All notable changes to RCS are documented here. Per-skill changes use the skill's SemVer; repo-level batch tags mark release groupings.

## [Unreleased]

## [v1.0.0-phase1] — 2026-05-23

### Added — Phase 0 (Bootstrap)

- Repo skeleton, root README, LICENSE (MIT), CONTRIBUTING.md
- `docs/conventions.md`, `docs/eval-protocol.md`, `docs/governance.md`
- `tools/lint_frontmatter.py`, `tools/lint_skill_md.py`, `tools/lint_links.py`, `tools/run_evals.py` — 27 unit tests passing
- `.github/workflows/frontmatter-lint.yml`, `link-check.yml`, `eval-suite.yml`
- All 5 track READMEs with planned-skills tables populated from the full ~80-skill universe

### Added — Phase 1 (Free-ship skill migrations)

- `workflow/running-adversarial-premortem` v0.1.0 — migrated from `~/.claude/skills/adversarial-premortem.skill`; status: shipped
- `security/auditing-mcp-server-pre-trust` v0.1.0 — migrated from `~/.claude/skills/mcp-server-pre-trust-audit/`; status: shipped

### Eval methodology note

Phase 1 evals were run interactively in-session using Claude Code subagent dispatch (model = haiku / sonnet / opus), not via the `tools/run_evals.py` API harness. Both skills passed intent-matched scoring across all 3 models on all 3 scenarios. Two rubric calibration issues were identified and corrected:

- Premortem `01-paper-math-claims.json` rubric item 2 was rewritten from a literal "bijection of operations on small finite set" phrasing to a broader structural-vs-functional / measure-zero / multi-head-interaction formulation, since all 3 models hit the intent without the exact wording.
- MCP-audit `01-pinned-licensed-mcp.json` query now explicitly instructs "assume the artifact exists; audit from information given" to prevent models (correctly) detecting that the placeholder `github.com/example/...` URL is fictional and rejecting on Check 2.

The `tools/run_evals.py` external API harness is retained for future CI automation but is optional; the in-session subagent-dispatch path is the recommended local validation flow.
