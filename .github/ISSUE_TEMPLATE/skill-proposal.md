---
name: Skill proposal
about: Propose a new skill before authoring it (required first step per CONTRIBUTING.md)
title: "[skill-proposal] <gerund-form-slug>"
labels: ["skill-proposal", "needs-triage"]
assignees: []
---

## Proposed slug

`<verb-ing-form-noun-phrase>` (lowercase-kebab, ≤ 64 characters, no `anthropic` or `claude` reserved words)

Track: `security` | `ml-datasci` | `workflow` | `teaching` | `claude-code-meta`

## The gap this skill closes

What discipline does a competent practitioner rebuild from scratch every time, that this skill would encode once?

Be concrete. "Statistics" is too broad. "Decides whether a chi-squared test's expected-cell-count requirement is satisfied before running it" is the right level.

## Evidence the gap exists in ≥ 2 real contexts

RCS only accepts skills whose gap has been observed in two or more independent projects. List them:

1. **Project / context A:**
   - What happened:
   - Where the discipline would have helped:
2. **Project / context B:**
   - What happened:
   - Where the discipline would have helped:

If the gap has only appeared once, this is probably a project-specific note and belongs in that project's `CLAUDE.md`, not in RCS.

## Why this skill instead of an existing one

Scan [`skills/README.md`](../../skills/README.md) for the cross-track index. If an existing skill covers the same gap, the proposal should explain why it is insufficient (different audience, different stack, different decision point). Linking the nearest existing skill is required.

Nearest existing skill: ` <slug or "none">`

## Audience tiers the skill targets

Pick all that apply. The skill's `audience:` frontmatter list will mirror this.

- [ ] `data-scientist`
- [ ] `ml-engineer`
- [ ] `stats-student`
- [ ] `instructor`
- [ ] `security-eng`
- [ ] `devops`
- [ ] `skill-author`
- [ ] Other: `<tag>`

## Draft eval scenarios

Three sketches. The full JSON files go in the eventual PR.

### 01-happy-path

One-sentence user query:

Expected behavior (3 rubric items):

1.
2.
3.

### 02-edge-case

One-sentence user query:

Expected behavior (3 rubric items):

1.
2.
3.

### 03-anti-trigger

One-sentence user query (the skill should refuse or hand off):

Expected behavior (3 rubric items):

1.
2.
3.

## Anti-triggers worth naming

When should this skill NOT engage? Hand-off targets (other skills or external tools) the workflow should defer to:

-
-

## Estimated Σ

A rough triage on the 1-20 ROI scale (frequency the gap appears × cost of getting it wrong). Maintainer triage will finalize. Range:

- 7-10: niche but real
- 11-14: broadly useful within one track
- 15-19: cross-track, high frequency
- 20: rare; reserved for the most universally applicable disciplines

Proposed Σ:

## Checklist before this issue is ready for triage

- [ ] Slug follows the gerund + lowercase-kebab + length + reserved-word rules
- [ ] At least 2 independent contexts named with evidence
- [ ] Nearest existing skill searched and linked
- [ ] 3 draft eval scenarios sketched (not full JSON, but enough to evaluate the discipline)
- [ ] Anti-triggers named
- [ ] Read [`CONTRIBUTING.md`](../../CONTRIBUTING.md) and [`docs/conventions.md`](../../docs/conventions.md)
