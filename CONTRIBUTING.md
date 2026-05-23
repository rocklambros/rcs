# Contributing to RCS

## What we accept

Skills that match the RCS positioning:

- **Catalog-free**: no bundled framework controls (NIST / MITRE / OWASP / ISO / EU AI Act / CMMC / PCI). Methodology-only or catalog-as-input.
- **Capability, not output**: reusable workflow disciplines, not skills that replicate a finished project's output.
- **Real evidence**: the gap the skill closes must have appeared in 2+ real-world contexts.

If your skill doesn't fit, propose a separate sibling repo or open an issue to discuss.

## Workflow

### 1. Open an issue first

Describe the gap (which workflow you keep redoing) and propose the skill name (gerund-form, lowercase-kebab, ≤ 64 chars).

### 2. Write evals before the skill body

Per the [Anthropic best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), evals come first. For each new skill, create:

- `skills/<track>/<skill>/evals/01-happy-path.json` — typical use case
- `skills/<track>/<skill>/evals/02-edge-case.json` — assumption violation, missing data, or ambiguity
- `skills/<track>/<skill>/evals/03-anti-trigger.json` — skill should refuse or hand off

Each scenario has exactly 3 checkable `expected_behavior` rubric items in v1.

### 3. Write SKILL.md against the Layer-3 documentation contract

Required H2 sections in this order: `When to use`, `When NOT to use`, `Quick start`, `Inputs / Arguments / Flags`, `Workflow`, `Outputs`, `Failure modes`, `References`, `Examples`, `See also`, `Status & version`. See `docs/conventions.md`.

Body ≤ 500 lines. Longer content goes in `reference/` files (loaded on-demand, no startup token cost).

### 4. Run lint locally

```bash
uv run python -m tools.lint_frontmatter skills/<track>/<skill>/SKILL.md
uv run python -m tools.lint_skill_md skills/<track>/<skill>/SKILL.md
uv run python -m tools.lint_links skills/<track>/<skill>/
```

### 5. Run evals locally

You need `ANTHROPIC_API_KEY` set with access to Haiku 4.5, Sonnet 4.6, and Opus 4.7.

```bash
uv run python -m tools.run_evals skills/<track>/<skill>/
```

Pass thresholds (per `docs/eval-protocol.md`):

- Haiku 4.5: ≥ 2 of 3 rubric items on each scenario, all 3 scenarios
- Sonnet 4.6: 3 of 3 on happy-path AND edge-case; ≥ 2 of 3 on anti-trigger
- Opus 4.7: 3 of 3 on all 3 scenarios

### 6. Update track README + root README catalog

Add a row to the track's shipped-skills table and to the root catalog.

### 7. Submit PR

CI will run frontmatter lint, link check, and eval suite. The PR is blocked until all three pass.

## Batch authoring (multi-skill PRs)

For shipping multiple skills at once, RCS uses a documented batch-authoring discipline called **PRAGMATIC**: a deviation from the strict writing-skills RED-GREEN-REFACTOR Iron Law that skips formal baseline (RED) testing in exchange for in-session Sonnet-only eval validation. PRAGMATIC is appropriate when:

- The gap evidence for each skill is already documented in repo history (see the spec for v1)
- The batch is methodology-only skills (no novel framework catalogs)
- The author can validate via in-session subagent dispatch instead of an external eval harness

PRAGMATIC batches use the per-batch isolation contract documented in [`docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md`](docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md): one branch + worktree per batch, changelog fragments instead of CHANGELOG.md edits, deferred root-catalog updates to a final integration step.

Invocation per batch session:

```
/superpowers:writing-skills create batch <N> at docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md using PRAGMATIC
```

For single-skill PRs, follow the standard 7-step workflow above (eval-first, full 3-model validation if `ANTHROPIC_API_KEY` is available).

## No AI attribution

Do not credit Claude, GPT, or any AI as an author or contributor — in commits, PR descriptions, code comments, file headers, changelogs, or documentation. No `Co-Authored-By: Claude`, no "Generated with AI" lines, no robot emoji. Git author and committer stay the human. PRs that include AI attribution will be asked to amend.

## Naming convention

Skill slugs are gerund-form, lowercase-kebab, ≤ 64 characters, no `anthropic` or `claude` as reserved words. Examples: `selecting-statistical-test`, `enforcing-seed-hygiene`, `auditing-mcp-server-pre-trust`.

## License

By contributing, you agree your contribution is licensed under the MIT license that covers this repo.
