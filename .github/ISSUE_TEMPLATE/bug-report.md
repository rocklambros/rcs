---
name: Bug report
about: Report a defect in a skill, the lint or eval tooling, or repository documentation
title: "[bug] <one-line summary>"
labels: ["bug", "needs-triage"]
assignees: []
---

## Where the bug is

- [ ] In a specific skill: `skills/<track>/<slug>/SKILL.md` (line: )
- [ ] In a reference file: `skills/<track>/<slug>/reference/<file>`
- [ ] In an eval JSON: `skills/<track>/<slug>/evals/<file>`
- [ ] In the lint or eval tooling: `tools/<file>.py`
- [ ] In repository documentation: `<path>`
- [ ] In a CI workflow: `.github/workflows/<file>.yml`
- [ ] In the install loop or other scripted snippet
- [ ] Other:

## What happens

Be concrete. "It doesn't work" is not actionable. Useful descriptions name the input, the observed output, and the expected output.

## What should happen instead

Reference the skill's own `Failure modes` or `Examples` section if applicable; that is the contract the skill promises.

## How to reproduce

Steps a maintainer can run to see the bug:

1.
2.
3.

If the bug only appears with a specific model or Claude Code version, name it.

## Environment

- Claude Code version: `claude --version`
- Operating system:
- Skills installed: `ls ~/.claude/skills | wc -l` and a note on the install path
- Relevant project context (language, framework, dataset):

## Severity

Pick the closest match. Maintainer triage will finalize.

- [ ] **Critical.** A skill produces a confidently-wrong answer in a high-stakes domain (security, regulated ML, clinical), or the install/lint/eval tooling can be made to clobber user data
- [ ] **High.** A skill silently violates its own documented contract (e.g., the anti-trigger fires when it should not, or the skill engages on the named refuse-case)
- [ ] **Medium.** A skill produces a useful but partial answer, or documentation is materially misleading
- [ ] **Low.** A typo, a broken link, or a cosmetic issue

If you suspect this is a **security vulnerability**, do not file this issue. See [`SECURITY.md`](../../SECURITY.md) for the private reporting channel.

## What you have tried already

Optional. Saves the maintainer time if the obvious fixes have been ruled out.

## Proposed fix

Optional. A PR proposal with a sketch of the change is welcome but not required to file the bug.
