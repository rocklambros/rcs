# How to contribute a skill

A recipe for adding a new skill to RCS. The canonical contract lives in [`CONTRIBUTING.md`](../../CONTRIBUTING.md); this page is the step-by-step expansion.

## Before you start

The skill should match the RCS positioning (catalog-free, methodology-only, evidence from at least two real contexts). If you are not sure, open a skill-proposal issue first and let triage decide before you author. The proposal template is at [`.github/ISSUE_TEMPLATE/skill-proposal.md`](../../.github/ISSUE_TEMPLATE/skill-proposal.md).

Pick a track. The five tracks are `security`, `ml-datasci`, `workflow`, `teaching`, `claude-code-meta`. A skill lives in the track whose audience reads it. If the skill spans tracks, pick the primary audience and cross-reference from the others.

Pick a slug. Gerund-form, lowercase-kebab, ≤ 64 characters, no `anthropic` or `claude` reserved words. Examples that pass the linter: `selecting-statistical-test`, `auditing-graphql-nullability`, `building-conformal-prediction-set`. Examples that fail: `claude-skill-author` (reserved word), `Selecting-Test` (uppercase), `selectTest` (no hyphens), `select` (no -ing form).

## Step 1: Write the eval scenarios first

Create the directory and the three eval files before the SKILL.md body. This forces you to commit to what the skill should do before figuring out how.

```bash
mkdir -p skills/<track>/<slug>/evals
mkdir -p skills/<track>/<slug>/reference
```

Three JSON files, one per scenario kind:

- `evals/01-happy-path.json` — a typical use case the skill handles correctly
- `evals/02-edge-case.json` — an assumption violation, missing data, or ambiguity
- `evals/03-anti-trigger.json` — a request the skill should refuse or hand off

Each file follows the schema in [`docs/eval-protocol.md`](../eval-protocol.md). Three rubric items per scenario; rubric items are third-person assertions about the response, not procedural steps.

## Step 2: Write the SKILL.md

Use the template implicit in [`docs/conventions.md`](../conventions.md): YAML frontmatter (eight required fields), then 11 required H2 sections in order. Body ≤ 500 lines.

Apply the [`workflow/writing-repo-documentation`](../../skills/workflow/writing-repo-documentation/) discipline to the body. Specifically:

- Lead the `When to use` section with concrete symptoms, not abstract triggers
- Quick start is a runnable example, not a checklist of concepts
- One concept per paragraph in the Workflow section
- Failure modes name specific anti-patterns the skill catches, not vague warnings
- Self-audit against [`reference/ai-slop-patterns.md`](../../skills/workflow/writing-repo-documentation/reference/ai-slop-patterns.md) before committing

## Step 3: Bundle reference material (if needed)

Anything that would push the SKILL.md body over 500 lines, or that the skill needs but the on-load context does not, goes in `reference/`:

- Long tables: cheatsheets, decision matrices, formula references
- Code templates: copy-pasteable scaffolds the user adapts
- External-doc indexes: lists of upstream references with one-line summaries

Reference links are one level deep from SKILL.md. A reference file should not link to other reference files inside the same skill; the linter rejects two-level-deep cross-references.

## Step 4: Run lint locally

```bash
uv run python -m tools.lint_frontmatter skills/<track>/<slug>/SKILL.md
uv run python -m tools.lint_skill_md skills/<track>/<slug>/SKILL.md
uv run python -m tools.lint_links skills/<track>/<slug>/
```

All three must print `OK`. The linter catches missing frontmatter fields, missing H2 sections, body-length overrun, broken internal links, and two-level-deep reference links.

## Step 5: Validate via Flow A (PRAGMATIC)

The default flow for every skill shipped through v7.0.3. No API key required.

From inside a Claude Code session, dispatch one general-purpose subagent per scenario with `model: sonnet`. Each subagent reads the SKILL.md you just wrote and answers the scenario's `query`. Judge each completion against the 3 rubric items using intent-matched scoring (not literal phrasing).

Sonnet thresholds:

- happy-path: 3 of 3
- edge-case: 3 of 3
- anti-trigger: ≥ 2 of 3

A skill that meets all thresholds ships at `status: shipped`. A skill that fails any threshold ships at `status: drafting` with the failure documented in its CHANGELOG entry. Drafting skills are visible to the catalog but not auto-invocable.

For the full 3-model harness (Flow B), see [`docs/eval-protocol.md`](../eval-protocol.md).

## Step 6: Update the catalog

Add a row to each of:

- `README.md` at the project root (skill-catalog table)
- `skills/README.md` (cross-track index)
- `skills/<track>/README.md` (track shipped-skills table)

If your skill is part of a multi-skill batch, use the batch-fragment pattern in [`docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md`](../superpowers/plans/2026-05-23-rcs-batch-creation-plan.md) instead. Per-batch fragments avoid merge conflicts when multiple authors ship batches in parallel; an integration commit consolidates them.

## Step 7: Add a CHANGELOG entry

Under `## [Unreleased]`, document the new skill: track, slug, Σ, status, one-paragraph what-it-does, eval methodology (Flow A or Flow B), eval results table.

## Step 8: Open the PR

Use the PR template at [`.github/pull_request_template.md`](../../.github/pull_request_template.md). The template's checklist enforces the test-plan items (lint, pytest, eval results) and the no-AI-attribution confirmation.

CI runs the frontmatter lint, the link check, and (if `ANTHROPIC_API_KEY` is set) the eval suite. The PR is blocked until all three pass.

## What happens after merge

The skill is reachable from the catalog within minutes. Users who pull and re-run the install loop get the symlink automatically. The next Claude Code session those users start picks up the new skill in its startup scan.

If the skill is drafting at merge time, the path to shipped is a follow-up patch release. Fix the failing scenario, re-run Flow A, promote to shipped, and ship a `vM.N.P` patch tag.
