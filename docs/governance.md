# RCS Governance

## Versioning

Each skill has its own SemVer in `frontmatter.version`:

- **MAJOR** (`1.x.x` → `2.0.0`): breaking change — frontmatter `name` change, removed required argument, removed required H2 section, behavior change that would break an existing eval scenario.
- **MINOR** (`x.1.x` → `x.2.0`): new optional argument, new examples, refined wording, additional reference files, new scenario added to evals.
- **PATCH** (`x.x.1` → `x.x.2`): typos, lint fixes, eval rubric clarifications that don't change pass/fail behavior.

Repo-level tags are loose: `v1`, `v1.1`, `v2` mark batch releases that correspond to spec phases. They are NOT SemVer at the repo level.

## Deprecation policy

A skill moves to `status: deprecated` with a 90-day notice in `CHANGELOG.md`. The SKILL.md gets an `## Old patterns` block (per Anthropic best-practices) linking to the replacement. After 90 days, the skill is removed from catalog tables; the directory may remain with a tombstone SKILL.md pointing to the replacement.

## PR review SLAs

- Acknowledge within 7 days
- Initial review within 14 days
- Merge or rejection decision within 30 days

PRs that don't meet the documentation contract or eval thresholds get a checklist of what's missing; the contributor revises.

## No AI attribution — maintainer responsibilities

Per CONTRIBUTING.md, no AI attribution is permitted anywhere in the repo. Maintainers reviewing PRs must:

1. Check commit messages for `Co-Authored-By:` lines crediting AI; ask contributor to amend
2. Check PR description for "generated with" / "AI-assisted" language; ask contributor to remove
3. Check new files for AI-attribution comments

## Code of conduct

Contributors are expected to engage respectfully. Disagreement on technical merit is welcome; ad hominem is not. Maintainers may close issues and PRs that violate this norm without further discussion.
