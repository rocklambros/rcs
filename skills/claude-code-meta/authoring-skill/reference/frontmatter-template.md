# Frontmatter template

Copy this block to the top of a new `SKILL.md`. Fill in the bracketed fields.

```yaml
---
name: <gerund-form-slug>
description: >
  <Third-person sentence describing WHAT the skill does and WHEN to trigger it.
  No first-person ("I can help..."). No second-person ("You can use..."). No
  workflow summaries. ≤ 1024 characters total for the whole block.>
version: 0.1.0
status: shipped         # shipped | drafting | planned
track: <track>          # security | ml-datasci | workflow | teaching | claude-code-meta
audience:               # one or more
  - skill-author
evidence:               # repos or sources where the gap appeared
  - <repo-or-source-name>
last-updated: 2026-05-23
---
```

## Field-by-field rules

| Field | Required by | Rule |
|---|---|---|
| `name` | Anthropic spec | gerund-form, lowercase-kebab, ≤ 64 chars, no `anthropic` / `claude` reserved words, matches the directory name |
| `description` | Anthropic spec | third-person, WHAT + WHEN, ≤ 1024 chars, no workflow summary, no first/second-person POV |
| `version` | RCS | SemVer (`MAJOR.MINOR.PATCH`); start at `0.1.0` for new skills |
| `status` | RCS | `shipped` only after lint + eval thresholds pass; `drafting` if some scenario failed materially; `planned` only in track README, never in a real `SKILL.md` |
| `track` | RCS | exactly one of the 5 — must match the parent directory |
| `audience` | RCS | list; pick the tags that match the consumer of this skill, not every plausible reader |
| `evidence` | RCS | repos / sources where the underlying gap was observed; the provenance trail. Empty list is acceptable for net-new skills, but flag it if there's no real evidence |
| `last-updated` | RCS | ISO date (`YYYY-MM-DD`) — bump on every meaningful edit |

## Description anti-patterns to avoid

| ❌ Bad | Why it breaks |
|---|---|
| "I can help you audit GraphQL schemas." | First-person POV — breaks discovery |
| "You can use this to audit GraphQL schemas." | Second-person POV — same problem |
| "Use when auditing GraphQL schemas. Walks 6 steps: introspect, ..." | Workflow summary — Claude follows the description and skips the body |
| "Use when the user is unsure." | No WHAT, no concrete trigger — never gets matched |
| "Audits GraphQL schemas." | No WHEN, no triggering condition — never gets loaded |

## Description that works

> "Audits a GraphQL schema for over-permissive query depth, missing field-level authorization, and dangerous introspection exposure. Use when the user is about to expose a public GraphQL endpoint, has a schema diff to review, or asks 'is this schema safe?'."

WHAT (audits schema for X, Y, Z) + WHEN (3 concrete triggers) + third-person + no workflow steps.
