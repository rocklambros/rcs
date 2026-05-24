# RCS Conventions

This document defines the frontmatter spec, status semantics, naming rules, and Layer-3 SKILL.md required sections that every RCS skill must satisfy. Lint-enforced via `tools/lint_frontmatter.py` and `tools/lint_skill_md.py`.

## Naming

- Skill slugs are **gerund-form** (verb + -ing): `selecting-...`, `enforcing-...`, `auditing-...`, `evaluating-...`, `building-...`, `writing-...`, `running-...`, `scaffolding-...`, `validating-...`, `deduplicating-...`, `tuning-...`.
- Lowercase-kebab. ≤ 64 characters. No `anthropic` or `claude` reserved words. No XML tags.
- The slug is the directory name AND the frontmatter `name` field.

## Frontmatter (YAML)

### Required (Anthropic spec)

```yaml
name: <gerund-form-slug>
description: >
  <Third-person, ≤ 1024 chars, includes WHAT the skill does and WHEN to trigger it.>
```

**Third-person rule**: write "Walks a decision tree..." NOT "I can help you..." or "You can use this..." (per Anthropic best-practices doc; the description is injected into the system prompt and POV inconsistency causes discovery problems).

### RCS-required fields (lint-enforced)

These six fields are required by `tools/lint_frontmatter.py`. A missing or malformed field fails the lint and blocks the PR.

```yaml
version: 0.1.0                       # SemVer per skill
status: shipped                       # shipped | drafting | planned | deprecated
track: ml-datasci                     # security | ml-datasci | workflow | teaching | claude-code-meta
audience:                             # list of tags
  - data-scientist
  - ml-engineer
  - stats-student
  - instructor
evidence:                             # repos where the gap appeared (provenance)
  - DU-MSDSAI-4441-Final
  - llm-safety-alignment-study
last-updated: 2026-05-22              # ISO date YYYY-MM-DD
```

## Status semantics

| Status | Filesystem | Required for | Auto-invocable |
|---|---|---|---|
| `shipped` | Full SKILL.md + 3 passing evals + Layer-3 H2 sections | Production use | Yes |
| `drafting` | SKILL.md exists, evals incomplete or failing on one model | Public review | No |
| `planned` | NO directory; listed only in track README | Roadmap visibility | No |

## SKILL.md Layer-3 contract — required H2 sections in order

1. `## When to use` — explicit triggers (user requests, keywords, situations)
2. `## When NOT to use` — anti-triggers (when Claude should skip or hand off)
3. `## Quick start` — minimum-viable runnable example
4. `## Inputs / Arguments / Flags` — every parameter (name, type, required/optional, default, allowed values, example)
5. `## Workflow` — numbered steps; checklist if multi-step (per Anthropic best-practices)
6. `## Outputs` — what the skill produces (format, location, conventions)
7. `## Failure modes` — known pitfalls + how the skill catches them
8. `## References` — bundled `reference/` files + external links (one level deep)
9. `## Examples` — ≥ 2 real input/output pairs
10. `## See also` — sibling skills (one level deep links)
11. `## Status & version` — restates status + SemVer + last-updated

Body ≤ 500 lines. Longer content goes in `reference/` (no startup token cost; loaded on-demand).

## File path rules

- Forward slashes only (Unix-style, works on all platforms).
- Reference links one level deep from SKILL.md — Claude may partially read transitively-linked files, missing content.
- Bundle large reference material in `reference/`; bundle scripts in `scripts/`.

## Eval requirements (see `eval-protocol.md` for details)

- Exactly 3 scenarios per skill in v1: happy-path, edge-case, anti-trigger.
- Exactly 3 rubric items per scenario.
- **Default flow (PRAGMATIC):** Sonnet judges Sonnet via in-session subagent dispatch. No API key required. Used for every skill shipped through v7.0.3.
- **Aspirational flow (3-model harness):** Sonnet judges Haiku, Sonnet, and Opus completions via the external `tools/run_evals.py` harness. Requires `ANTHROPIC_API_KEY`. Run during periodic re-validation sweeps.
