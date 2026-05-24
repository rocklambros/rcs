# RCS Governance

## Versioning

Each skill has its own SemVer in `frontmatter.version`:

- **MAJOR** (`1.x.x` → `2.0.0`): breaking change. Frontmatter `name` change, removed required argument, removed required H2 section, behavior change that would break an existing eval scenario.
- **MINOR** (`x.1.x` → `x.2.0`): new optional argument, new examples, refined wording, additional reference files, new scenario added to evals.
- **PATCH** (`x.x.1` → `x.x.2`): typos, lint fixes, eval rubric clarifications that don't change pass/fail behavior.

Repo-level tags follow two patterns:

- **Integration tags** `vM.N-phaseK` (for example `v7.0-phase1`). Shipped after a batch of skills merges via independent per-batch PRs and the catalog is consolidated in a single integration commit. The phase number corresponds to the spec phase that batch served.
- **Patch tags** `vM.N.P` (for example `v6.0.1`, `v6.0.2`, `v7.0.1`, `v7.0.2`, `v7.0.3`). Shipped for single-skill releases or documentation-only patches that follow an integration tag.

Neither pattern is SemVer at the repo level. They are ordering tags. The per-skill SemVer in each `SKILL.md` frontmatter is the contract that downstream consumers should pin against. The repo-level tag tells you when a group of changes shipped together.

## Deprecation policy

A skill moves to `status: deprecated` with a 90-day notice in `CHANGELOG.md`. The SKILL.md gets an `## Old patterns` block (per Anthropic best-practices) linking to the replacement. After 90 days, the skill is removed from catalog tables. The directory may remain with a tombstone SKILL.md pointing to the replacement.

## PR review SLAs

- Acknowledge within 7 days
- Initial review within 14 days
- Merge or rejection decision within 30 days

PRs that don't meet the documentation contract or eval thresholds get a checklist of what's missing. The contributor revises.

## No AI attribution. Maintainer responsibilities

Per CONTRIBUTING.md, no AI attribution is permitted anywhere in the repo. Maintainers reviewing PRs must:

1. Check commit messages for `Co-Authored-By:` lines crediting AI. Ask contributor to amend
2. Check PR description for "generated with" / "AI-assisted" language. Ask contributor to remove
3. Check new files for AI-attribution comments

## Code of conduct

See [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) at the repo root. The repository adopts the Contributor Covenant v2.1. Enforcement contact is `rock@rockcyber.com`.
