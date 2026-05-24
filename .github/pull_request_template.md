<!--
Pick the template variant that matches your PR scope:

  - New skill: keep all sections below
  - Existing-skill change: skip the "Skill shipped" section, keep "Eval results" if evals changed
  - Documentation-only: skip "Skill shipped" and "Eval results", keep "Files changed" + "Test plan"

Delete the parts that don't apply. The maintainer should not have to figure out what kind of PR this is.
-->

## Summary

Two or three bullets describing what this PR changes and why. Lead with the user-visible effect, not the implementation.

-
-

## Skill shipped (for new-skill PRs only)

- `<track>/<slug>` v0.1.0 — one-line description of what the skill does (Σ <N>, status: shipped | drafting)

Track-fit reasoning (if not obvious): why this skill belongs in `<track>` and not another.

## Files changed

- `skills/<track>/<slug>/` (new) — SKILL.md, evals (3 JSON files), reference (any bundled .md / .py / .sh files)
- `CHANGELOG.md` — new section under `## [Unreleased]` or under a versioned heading
- `README.md` — catalog row (if shipping)
- `skills/README.md` — cross-track index row (if shipping)
- `skills/<track>/README.md` — track shipped-table row (if shipping)

## Eval results

For new skills or material body changes. Skip if the PR does not touch eval-relevant content.

| Scenario | Score | Threshold | Pass |
|---|---|---|---|
| 01-happy-path | N/3 | 3/3 (Sonnet PRAGMATIC) or ≥ 2/3 (Haiku) | ✅ / ❌ |
| 02-edge-case | N/3 | 3/3 (Sonnet PRAGMATIC) or ≥ 2/3 (Haiku) | ✅ / ❌ |
| 03-anti-trigger | N/3 | ≥ 2/3 (any model) | ✅ / ❌ |

Methodology: `PRAGMATIC (Sonnet-only)` | `full 3-model harness (tools/run_evals.py)` | `other (explain)`

Scoring notes (intent-matched vs strict, any rubric mismatches worth flagging):

-

## Test plan

- [ ] `uv run pytest -q` — passes
- [ ] `uv run python -m tools.lint_frontmatter skills/<track>/<slug>/SKILL.md` — OK
- [ ] `uv run python -m tools.lint_skill_md skills/<track>/<slug>/SKILL.md` — OK
- [ ] `uv run python -m tools.lint_links skills/<track>/<slug>/` — OK
- [ ] (If docs changed) ran the AI-slop self-audit per `workflow/writing-repo-documentation` discipline
- [ ] (If install loop changed) ran the new script against a clean and a populated `~/.claude/skills/` and confirmed idempotency

## Reviewer attention

Anything specific the reviewer should look at. Subtle decisions worth flagging:

-

## No AI attribution

Confirm: commits, this PR description, and all files changed contain no `Co-Authored-By: Claude`, no "Generated with AI" lines, and no AI-attribution comments. See `CONTRIBUTING.md`. PRs that include AI attribution will be asked to amend.

- [ ] Confirmed
