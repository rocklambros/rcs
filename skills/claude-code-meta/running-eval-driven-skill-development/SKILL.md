---
name: running-eval-driven-skill-development
description: >
  Walks the eval-driven skill development workflow per the Anthropic Skill best-practices
  guidance: write three evaluation scenarios BEFORE the SKILL.md body, then write the
  body to satisfy the evals, then verify by dispatching a subagent against each scenario
  and judging the completion against the rubric. Use when authoring a new Claude Code
  skill, plugin skill, or marketplace skill for any host (Claude Code, Copilot CLI,
  Gemini CLI, Anthropic API) and the skill is non-trivial enough that an implicit
  "looks right" review is insufficient. Refuses to engage on trivial one-method
  wrappers, status-line configs, or single-shell-alias skills where eval overhead
  exceeds skill complexity.
version: 0.1.0
status: shipped
track: claude-code-meta
audience: [skill-author, devops, ml-engineer]
evidence:
  - rcs-public-skills-repo
  - anthropic-skill-best-practices
last-updated: 2026-05-23
---

# Running Eval-Driven Skill Development

## When to use

Trigger this skill when:

- The user is about to write a new Claude Code skill, plugin skill, or marketplace skill
- The user has a draft SKILL.md and asks "is this any good?" or "how do I know if it works?"
- The user wants to publish a skill to a public registry (Anthropic plugin marketplace, internal team registry, peer-shared collection)
- The skill encodes judgment, multi-step reasoning, or domain expertise where "looks right on review" is not a sufficient quality bar
- The skill description includes phrases like "audit", "evaluate", "decide", "recommend", "walk a decision tree", "select among", "diagnose" — judgment-loaded verbs where downstream agents will follow the skill on user requests

## When NOT to use

Skip this skill (eval overhead is not worth it) when:

- The skill is a one-line shell-alias wrapper (e.g., "run `make test`")
- The skill is a status-line, theme, or pure-config artifact (no behavioral assertion to test)
- The skill is a personal scratch / single-user / single-project tool that will not be shared
- The skill is being authored under a batch-authoring discipline like RCS PRAGMATIC where eval reduction is explicitly documented as a tradeoff (use PRAGMATIC instead)
- The user is asking how to USE a skill, not how to AUTHOR one (different skill — see `claude-code-meta/authoring-skill`)

## Quick start

User says: "I want to write a skill that helps audit GraphQL schemas for over-permissive nullability. Walk me through it."

Skill response: (1) co-author the three eval scenarios FIRST — happy-path, edge-case, anti-trigger — with three rubric items each, written as checkable third-person assertions about the response. (2) Author the SKILL.md body to satisfy those evals, including the Layer-3 H2 sections. (3) Dispatch a subagent per scenario with the SKILL.md inlined as context, judge each completion against the rubric, score N/3. (4) If any scenario fails, revise the body and re-run.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| skill_slug | string | yes | — | The gerund-form slug for the skill (e.g., `auditing-graphql-nullability`). |
| skill_intent | string | yes | — | One-paragraph description of what the skill does and when to use it. |
| host_tier | "claude-code" \| "plugin" \| "marketplace" \| "api" | no | "claude-code" | Discovery context the skill will run in; affects frontmatter constraints. |
| model_coverage | "sonnet-only" \| "haiku-sonnet" \| "haiku-sonnet-opus" | no | "sonnet-only" | How many models to validate against. Sonnet-only is a documented shortcut; full coverage is haiku-sonnet-opus. |
| eval_rounds | integer | no | 1 | Number of revise-and-rerun cycles permitted if evals fail. Default 1. |

## Workflow

Copy this checklist into the response and check off items as the work progresses:

```
Eval-driven skill development:
- [ ] Step 1: Draft the skill description (what + when, third-person, ≤ 1024 chars)
- [ ] Step 2: Author 3 eval scenarios (happy-path, edge-case, anti-trigger) BEFORE the body
- [ ] Step 3: Each scenario has 3 checkable third-person rubric items
- [ ] Step 4: Author the SKILL.md body to satisfy the evals
- [ ] Step 5: Dispatch a subagent per scenario with the SKILL.md inlined; capture completion
- [ ] Step 6: Judge each completion against the rubric — pass/fail per item, score N/3
- [ ] Step 7: If any scenario fails, revise the body (one revision round) and re-run
- [ ] Step 8: Pass thresholds met → status: shipped. Otherwise → status: drafting + note failures
```

### Step 1: Draft the description first

Write the frontmatter `description` BEFORE the body. The description is the discovery contract — it tells Claude when to load the skill. If the description is vague, no eval will save the skill.

Third-person rule (Anthropic best-practices): write "Walks a decision tree..." NOT "I can help you..." or "You can use this...". The description is injected into the system prompt; POV inconsistency causes discovery problems.

### Step 2: Author 3 eval scenarios BEFORE the body

The three scenarios per skill follow the RCS contract (one of each kind, exactly three rubric items each):

- **happy-path** (`01-<descriptive>.json`) — a typical user query that should fully engage the skill. The skill should produce the canonical correct response.
- **edge-case** (`02-<descriptive>.json`) — a near-miss or tricky variant where the skill should still engage but produce a non-obvious correct response (handle an exception, name a gotcha, refuse the wrong default).
- **anti-trigger** (`03-<descriptive>.json`) — a query that LOOKS like it should engage the skill but actually should not. The skill should hand off or decline.

Eval JSON schema:

```json
{
  "skill": "<slug>",
  "scenario_id": "0[1-3]-<short-descriptive>",
  "scenario_kind": "happy-path | edge-case | anti-trigger",
  "query": "<verbatim user prompt>",
  "files": [],
  "expected_behavior": [
    "<rubric item 1 — third-person checkable assertion>",
    "<rubric item 2>",
    "<rubric item 3>"
  ]
}
```

### Step 3: Write checkable rubric items

Each rubric item is a third-person assertion about the response that a judge model can mark `pass: true | false` without partial credit. Anti-patterns:

- *"Response is helpful"* — not checkable
- *"Mentions Wilcoxon"* — too literal; judge should match intent not phrasing
- *"Does the right thing"* — circular

Good rubric items:

- *"Recommends Wilcoxon signed-rank, NOT paired t-test"*
- *"Names the Shapiro-Wilk p-value as the gating assumption check"*
- *"Does NOT immediately recommend a test before asking about pairing / scale / assumption status"*

### Step 4: Author the SKILL.md body to satisfy the evals

Now write the SKILL.md body. The evals are the spec. If the body does not let a model satisfy all three rubric items in all three scenarios, the body is incomplete.

Follow the Layer-3 H2 contract (see `claude-code-meta/authoring-skill` for the full section list).

### Step 5: Dispatch a subagent per scenario

For each of the 3 scenarios:

1. Open a subagent dispatch
2. System context = the SKILL.md body inlined verbatim
3. User message = the eval `query` (and `files` if any)
4. Capture the completion

In Claude Code, use the Agent tool with `subagent_type: general-purpose` and `model: sonnet` (or haiku / opus per `model_coverage`).

### Step 6: Judge each completion against the rubric

For each rubric item, decide pass/fail against the captured completion. Match intent, not literal phrasing. Partial credit is a fail. Score N/3 per scenario.

Pass thresholds (per `docs/eval-protocol.md` and per the RCS PRAGMATIC tier):

| Model coverage | happy-path | edge-case | anti-trigger |
|---|---|---|---|
| sonnet-only (PRAGMATIC) | 3/3 | 3/3 | ≥ 2/3 |
| haiku-sonnet-opus (full) | Haiku ≥ 2/3 per scenario; Sonnet 3/3 per scenario; Opus 3/3 per scenario | | |

### Step 7: Revise once if failed

If any scenario fails, revise the SKILL.md body to address the specific rubric items that failed. Re-dispatch the failed scenarios. Default is one revision round; deeper iteration suggests the eval scenarios themselves need re-examination (was the rubric item achievable?).

### Step 8: Set status

- All thresholds met → `status: shipped` in frontmatter
- Any scenario fails after revision → `status: drafting` + note the failure in the changelog / PR description

## Outputs

Per skill, the eval-driven workflow produces:

- `skills/<track>/<slug>/SKILL.md` with required Layer-3 H2 sections + frontmatter `status: shipped` or `drafting`
- `skills/<track>/<slug>/evals/01-<happy>.json`
- `skills/<track>/<slug>/evals/02-<edge>.json`
- `skills/<track>/<slug>/evals/03-<anti>.json`
- An eval-results note (in PR description, changelog fragment, or a results JSON if persisted) recording the score per scenario per model

## Failure modes

- **Body-first authoring** — writing the SKILL.md body first and back-filling evals to whatever the body happens to produce. Caught by: this skill's Step 2 ordering. The discipline is evals-first; back-filled evals validate nothing.
- **Unfalsifiable rubric items** — rubric items like "response is good" that a judge cannot mark pass/fail. Caught by: Step 3 anti-patterns + the third-person checkable-assertion rule.
- **Same-family judge bias** — when the candidate model and the judge model are the same family, agreement is inflated. Caught by: rotating judge across versions (v2+ uses non-Sonnet judges occasionally) per `docs/eval-protocol.md`.
- **Single-model overconfidence** — Sonnet-only passes do not guarantee Haiku or Opus pass. Caught by: explicit `model_coverage` argument; PRAGMATIC sonnet-only is documented as a shortcut not a default.
- **Anti-trigger collapse** — anti-trigger scenarios that are too easy (the skill obviously does not apply) test nothing. Caught by: anti-triggers should LOOK like the skill applies (near-miss surface features) but actually require the skill to hand off.

## References

- `reference/eval-json-template.md` — copy-paste template for the 3 eval files
- `reference/rubric-writing-guide.md` — examples of good vs bad rubric items
- [Anthropic Skill best-practices — eval-driven development](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — origin of the evals-first guidance
- `docs/eval-protocol.md` (in this repo) — the RCS-specific eval JSON schema + pass thresholds

## Examples

### Example 1: Authoring a new domain skill (happy-path)

Input: "I want to write a skill that audits GraphQL schemas for over-permissive nullability. Walk me through it."

Output: Skill walks the user through (1) drafting a third-person description, (2) authoring 3 eval scenarios — e.g., happy = realistic schema with several mixed nullable / non-null fields; edge = schema with one nullable field where the nullability is intentional and load-bearing; anti = REST OpenAPI spec (not GraphQL), (3) authoring the SKILL.md body, (4) dispatching subagents per scenario, (5) scoring N/3. Refuses to write the body before the evals exist.

### Example 2: Evals are hard to define (edge-case)

Input: "I'm writing a skill that helps with creative brainstorming. The output is open-ended and there is no single right answer. How do I write evals for that?"

Output: Skill acknowledges the difficulty, then proposes process-rubric items rather than outcome-rubric items: e.g., "Response asks at least one clarifying question before generating", "Response produces at least 5 distinct ideas spanning at least 2 different framings", "Response does NOT collapse to a single recommendation without enumeration first". Notes that process rubrics generalize across open-ended outputs without forcing a canonical "right answer".

### Example 3: One-line wrapper (anti-trigger)

Input: "I'm writing a skill that wraps `npm test` and `npm run lint` in a single command. Should I run eval-driven development on it?"

Output: Skill declines to engage the full workflow. Explains that a one-line wrapper has no judgment surface to evaluate — the skill either runs the two commands or it doesn't, and that's caught by a smoke test, not a behavioral eval. Suggests a brief smoke test instead and notes that eval-driven development is overhead-justified only for skills that encode judgment.

## See also

- `claude-code-meta/authoring-skill` — the canonical authoring guide that this skill complements with eval discipline
- `claude-code-meta/writing-decision-trees-as-skills` — when the skill is a decision tree, rubric items can mirror tree branches
- `workflow/pre-registering-eval-study` — analogous discipline applied to empirical research studies

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
