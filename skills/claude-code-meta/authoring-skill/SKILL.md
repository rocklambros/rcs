---
name: authoring-skill
description: >
  Walks the Anthropic Skill best-practices checklist plus the RCS Layer-3 documentation
  contract for authoring a new skill. Covers gerund-form naming, third-person
  frontmatter description, the 11 required H2 sections in order, the ≤ 500-line
  body cap with reference/ bundles, one-level-deep reference linking, and the
  eval-first discipline (3 scenarios written before the body). Use when the user
  wants to write a new skill — for any host (Claude Code, Copilot CLI, Gemini CLI,
  Anthropic API plugin) — and needs the authoring rules plus a skeleton to fill in.
version: 0.1.0
status: shipped
track: claude-code-meta
audience: [skill-author]
evidence:
  - RCS
  - superpowers
  - anthropic-skill-best-practices
last-updated: 2026-05-23
---

# Authoring a Skill

## When to use

Trigger this skill when the user asks for or implies one of:

- "Help me write a new skill" / "scaffold a skill" / "I want to author a skill for X"
- "What's the right structure for a Claude Code skill?"
- "Review my SKILL.md" / "is my frontmatter right?" / "is my description third-person?"
- They are about to author a skill for any host (Claude Code, Copilot CLI, Gemini CLI, Anthropic API plugins) — the artifact structure is identical
- They have an existing skill draft that needs to conform to the RCS Layer-3 contract or the Anthropic best-practices doc

## When NOT to use

Skip this skill and hand off when:

- The user is writing code that *uses* the Anthropic SDK or Claude API directly → that is API-client work, not skill authoring; use the `claude-api` skill instead
- The user is writing a plugin manifest, hook script, or rules file — those are different artifacts and have their own skills (`writing-claude-code-plugin`, `writing-claude-code-hook`, `writing-deny-allow-rules`, all planned)
- The user is writing an MCP server, not a skill → use `writing-mcp-server-securely` (planned) or audit an existing MCP via `security/auditing-mcp-server-pre-trust`
- The "skill" the user describes is one-off project-specific tooling that belongs in `scripts/` or `CLAUDE.md`, not a portable workflow discipline (see Failure modes → "skill vs. tool confusion")

## Quick start

User says: *"I want to write a skill that helps with auditing GraphQL schemas. Walk me through it."*

Skill response:

1. Confirm the slug as a gerund: `auditing-graphql-schemas`. Reject non-gerund forms (`graphql-audit`, `graphql-auditor`) and explain why.
2. Draft frontmatter — third-person `description` that includes WHAT + WHEN; required custom RCS fields (`version`, `status`, `track`, `audience`, `evidence`, `last-updated`).
3. **Write 3 evals first** under `evals/01-happy-path.json`, `02-edge-case.json`, `03-anti-trigger.json` — each with exactly 3 rubric items.
4. Fill the body: the 11 required H2 sections in order from the Layer-3 contract.
5. Lint: `uv run python -m tools.lint_frontmatter`, `lint_skill_md`, `lint_links`.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| skill_topic | string | yes | — | What discipline the skill encodes (e.g., "auditing GraphQL schemas"). |
| target_track | one of `security` / `ml-datasci` / `workflow` / `teaching` / `claude-code-meta` | yes | — | Top-level track the skill belongs in. |
| audience_tags | list of audience tags | yes | — | One or more of `security-eng`, `ai-security`, `data-scientist`, `ml-engineer`, `stats-student`, `instructor`, `skill-author`, `devops`. |
| host | "claude-code" \| "copilot-cli" \| "gemini-cli" \| "anthropic-api" | no | "claude-code" | Target host. Structure is portable; this field only affects install-instruction tailoring in examples. |
| evidence_repos | list of repo names | no | [] | Prior work where the gap appeared. Empty is acceptable for net-new skills; flag if the skill has no provenance trail. |

## Workflow

Copy this checklist into the response and check off items as the skill is authored:

```
Authoring progress:
- [ ] Slug is gerund-form, lowercase-kebab, ≤ 64 chars, no anthropic/claude reserved words
- [ ] Third-person description with WHAT + WHEN, ≤ 1024 chars, no workflow summary
- [ ] Track + audience tags chosen
- [ ] 3 eval JSONs (01-happy-path, 02-edge-case, 03-anti-trigger) written BEFORE the body
- [ ] Each eval has exactly 3 rubric items, written as third-person assertions
- [ ] Body: 11 required H2 sections in order (see Outputs)
- [ ] Body ≤ 500 lines; bundle long content under reference/
- [ ] References one level deep — no transitive linking
- [ ] Lint: frontmatter, skill_md, links — all OK
- [ ] Sanity: "does the description answer 'should I load this skill right now?'"
```

### Step 1 — Slug

Gerund (verb + -ing). Lowercase kebab-case. ≤ 64 characters. No reserved words "anthropic" or "claude". No XML tags. The slug is BOTH the directory name AND the frontmatter `name` field.

Acceptable: `auditing-graphql-schemas`, `selecting-loss-function`, `running-chaos-test`.
Rejected: `graphql-audit` (noun), `Audit-GraphQL` (capitalized), `claude-graphql-helper` (reserved word).

### Step 2 — Frontmatter

Required (Anthropic spec): `name`, `description`.

Description rules — non-negotiable per Anthropic best-practices:

- **Third-person**: "Walks a decision tree...", NOT "I can help you..." or "You can use this...". The description is injected into the system prompt; first-person POV breaks discovery.
- **WHAT + WHEN**: describe the function AND the triggering conditions. A description that says only "Use when X happens" without saying what the skill does forces Claude to load the body to find out. A description that says only "Walks a decision tree" without trigger conditions never gets loaded.
- **≤ 1024 chars total** for the whole `description` block.
- **No workflow summaries**: do NOT summarize the skill's steps in the description. Claude will follow the description and skip the body. Describe triggers; let the body teach the workflow.

RCS custom fields (don't break Anthropic schema):

```yaml
version: 0.1.0                       # SemVer per skill
status: shipped                       # shipped | drafting | planned
track: claude-code-meta               # one of the 5 tracks
audience: [skill-author]              # list of tags
evidence: [RCS, anthropic-skill-best-practices]
last-updated: 2026-05-23              # ISO date
```

### Step 3 — Evals first

Per Anthropic best-practices: write 3 evals BEFORE the SKILL.md body. This forces explicit rubric items that double as design constraints; a body authored first rationalizes away inconvenient rubrics.

Each eval is a JSON file under `evals/`:

- `01-<happy-path-name>.json` — the canonical positive case
- `02-<edge-case-name>.json` — a known difficulty (assumption violation, missing data, ambiguity)
- `03-<anti-trigger-name>.json` — a query that should NOT engage the skill

Schema:

```json
{
  "skill": "<slug>",
  "scenario_id": "01-<descriptive>",
  "scenario_kind": "happy-path",
  "query": "<verbatim user prompt>",
  "files": [],
  "expected_behavior": [
    "Checkable rubric item 1 (third-person assertion about the response)",
    "Checkable rubric item 2",
    "Checkable rubric item 3"
  ]
}
```

Exactly 3 rubric items per scenario in v1. Write them as falsifiable assertions a judge can score 0/1, not aspirational adjectives ("the response is helpful" is unjudgeable).

### Step 4 — Body: 11 H2 sections in order

```
## When to use
## When NOT to use
## Quick start
## Inputs / Arguments / Flags
## Workflow
## Outputs
## Failure modes
## References
## Examples
## See also
## Status & version
```

Lint enforces both the presence AND the order. Body ≤ 500 lines. Longer content goes in `reference/` (loaded on-demand; no startup token cost).

### Step 5 — References one level deep

The Anthropic doc is explicit: Claude may partially read transitively-linked files, missing content. So every markdown reference in SKILL.md must point to a file that stands alone. Do not chain reference → reference → reference.

### Step 6 — Lint

```bash
uv run python -m tools.lint_frontmatter skills/<track>/<slug>/SKILL.md
uv run python -m tools.lint_skill_md skills/<track>/<slug>/SKILL.md
uv run python -m tools.lint_links skills/<track>/<slug>/
```

All three must print `OK`. Fix and re-run until clean.

## Outputs

A new skill directory with:

```
skills/<track>/<slug>/
├── SKILL.md           # 11 H2 sections, ≤ 500-line body, valid frontmatter
├── evals/
│   ├── 01-<happy>.json
│   ├── 02-<edge>.json
│   └── 03-<anti>.json
├── reference/         # optional; for bundled long content
│   └── <topic>.md
└── scripts/           # optional; for executable utilities
    └── <utility>.py
```

Plus a row added to the track README's "Shipped skills" table (or "Planned skills" if `status: planned`). In RCS batch mode, the row goes into a `shipped-fragments/batch-N.md` file instead, consolidated by the Batch 6 integration pass.

## Failure modes

- **First-person POV in description.** "I can help you..." or "You can use this..." breaks discovery and violates Anthropic spec. Caught by: `lint_frontmatter` regex check + explicit reminder in Step 2.
- **Workflow summary in description.** A description that summarizes steps causes Claude to follow it instead of reading the body. Caught by: this skill's Step 2 warning + a reviewer eyeball check ("does the description summarize what the skill DOES, or just when to trigger?").
- **Skill vs. tool confusion.** A one-off bash script that cleans up logs in one project is project-specific tooling, not a portable skill. It belongs in `scripts/` or `CLAUDE.md`. Caught by: the When-NOT-to-use section + the sanity question "would this be useful in 3+ unrelated projects? If no → not a skill."
- **Body over 500 lines.** Long bodies inflate every cached prefix that touches them. Caught by: `lint_skill_md` MAX_BODY_LINES check + the `reference/` bundle pattern.
- **Reference-chain leakage.** SKILL.md links A.md, A.md links B.md, B.md has the actual content — Claude won't reliably reach B. Caught by: `lint_links` one-level-deep enforcement.
- **Evals written after body.** Body-first authoring rationalizes away inconvenient rubric items. Caught by: this skill's Workflow ordering (Step 3 before Step 4) + Anthropic best-practices doc citation.

## References

- `reference/frontmatter-template.md` — copy-paste frontmatter block with required + RCS-custom fields
- `reference/eval-skeleton.md` — copy-paste eval JSON skeleton for all 3 scenario types
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — authoritative source for description rules and eval-first discipline
- [Claude Code skill docs](https://code.claude.com/docs/en/skills.md) — host-specific install + discovery
- RCS `docs/conventions.md` — Layer-3 H2 contract + frontmatter spec
- RCS `docs/eval-protocol.md` — eval JSON schema + pass thresholds

## Examples

### Example 1: Net-new skill scaffold (happy-path)

Input: *"I want to write a skill that helps with auditing GraphQL schemas. Walk me through it."*

Output: Skill confirms slug `auditing-graphql-schemas` (gerund ✓). Drafts third-person description naming WHAT (audits a GraphQL schema for over-permissive query depth, missing field-level authorization, dangerous introspection exposure) and WHEN (user is about to expose a public GraphQL endpoint, has a schema diff to review, or asks "is this schema safe?"). Writes 3 evals BEFORE the body: 01-happy-path (review a typical schema for over-permissive query depth), 02-edge-case (introspection disabled — fall back to schema-file audit), 03-anti-trigger (user asks "what is GraphQL?" — pedagogy, not audit). Then fills the 11 H2 sections in order. Lints clean.

### Example 2: First-person description rewrite (edge-case)

Input: *"My description is 'I can help you find vulnerabilities in your GraphQL schema.' Is that good?"*

Output: Skill flags the first-person POV violation. Rewrites in third person: *"Audits a GraphQL schema for over-permissive query depth, missing field-level authorization, and dangerous introspection exposure. Use when the user is about to expose a public GraphQL endpoint, has a schema diff to review, or asks 'is this schema safe?'"*. Cites the Anthropic best-practices rule.

### Example 3: One-off tooling rejection (anti-trigger)

Input: *"I have a one-off bash script that cleans up logs in this project. Should I make it a skill?"*

Output: Skill answers no — this is project-specific tooling, not a portable, reusable workflow discipline. Suggests committing the script to `scripts/cleanup-logs.sh` in the project repo and documenting its purpose in `CLAUDE.md`. Explains that skills are reusable across 3+ unrelated projects; one-off scripts are not the same artifact.

## See also

- `claude-code-meta/auditing-instruction-hierarchy` — audit the CLAUDE.md hierarchy your new skill will run under
- `workflow/adversarial-premortem-single` — premortem your skill before shipping (especially for high-stakes domains)
- `workflow/auditing-context-window-pressure` — verify your skill doesn't bloat the cached prefix

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
