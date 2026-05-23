---
name: writing-successor-primers
description: >
  Writes a "successor primer" — the document a cold-pickup reader needs to
  carry a non-trivial project forward without the original author present.
  Covers purpose, founding principles, where-to-start entry points,
  defense-in-depth false-confidence warnings, project-specific glossary, and
  an explicit "what's NOT here" list. Use when a project has reached the
  point where a colleague, a future self, an open-source maintainer, or a
  next-team member will need to take over without sitting next to the
  original author. Refuses to write a primer for a throwaway prototype or a
  project the original author still owns day-to-day; in those cases a README
  is the right artifact, not a primer.
version: 0.1.0
status: shipped
track: workflow
audience: [data-scientist, ml-engineer, security-eng, devops, skill-author]
evidence:
  - ATACE
  - TRACT
  - ai-security-framework-crosswalk
last-updated: 2026-05-23
---

# Writing Successor Primers

## When to use

Trigger this skill when the user requests or implies one of:

- Handing off a project (planned departure, end of contract, end of rotation, open-sourcing)
- Phrases like "cold pickup", "if you join in six months", "what would my successor need to know?", "transfer doc", "knowledge transfer"
- Mid-stream refactor or rewrite where the original design rationale would otherwise be lost
- A long-running research project (≥ ~3 months) reaching a publication, release, or milestone boundary
- An MLOps / agentic / security system whose layers of redundancy could mislead a successor into trusting the wrong component

## When NOT to use

Use a different artifact when:

- The project is a throwaway prototype, a personal scratch repo, or a single-purpose script — a one-paragraph README is the right tool
- The original author still owns the project day-to-day — a README plus inline comments suffice
- The handoff is short-term (a vacation cover, an on-call swap) — a runbook or oncall handoff doc is more appropriate
- The audience is end users, not maintainers — write user docs instead
- The project has no design rationale worth preserving (pure data wrangling, glue scripts) — capture the data lineage in a dataset card and skip the primer

## Quick start

User says: *"I'm rolling off the incident-rank-validation project at the end of the month. There's no one specific successor — whoever picks this up will probably be a new hire 6 months from now. What do they need?"*

Skill response: produces a 1–3 page markdown primer with (1) a 3-sentence purpose statement; (2) the 5–8 founding principles that explain why the project looks the way it looks; (3) a where-to-start list of 3–5 concrete entry points (file paths, run commands, doc reads); (4) a defense-in-depth false-confidence section naming each redundancy layer and the single brittle component it might mask; (5) a glossary of project-specific terms; (6) a "what's NOT here" list of things a reasonable reader might expect but will not find.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| project_root | path | yes | — | Directory whose contents the primer must cover. |
| project_age | string | yes | — | How long the project has existed; under ~3 months → recommend README instead. |
| handoff_kind | "permanent" \| "milestone" \| "open-source" | yes | — | Permanent and open-source primers need more glossary + false-confidence depth. |
| audience | "engineer" \| "researcher" \| "executive" \| "mixed" | no | "engineer" | Affects vocabulary tier; mixed audiences trigger an executive-summary section. |
| max_length | integer | no | 1500 | Soft word cap; primers longer than 3 pages tend to be ignored. |

## Workflow

Copy this checklist into the response and check off items as the primer takes shape:

```
Primer progress:
- [ ] Purpose written as 3 sentences max
- [ ] Founding principles enumerated (5-8) with WHY each was chosen
- [ ] Where to start: 3-5 entry points (file paths + run commands)
- [ ] Defense-in-depth false-confidence section drafted
- [ ] Project-specific glossary written
- [ ] "What's NOT here" list enumerated
- [ ] Length sanity-check: ≤ ~1500 words / ≤ ~3 pages
- [ ] Primer committed to project root as PRIMER.md or docs/primer.md
```

### Step 1 — Purpose (3 sentences max)

Sentence 1: what the project IS. Sentence 2: who benefits and how. Sentence 3: the one constraint that shapes the design (regulatory, performance, audience).

### Step 2 — Founding principles

5–8 numbered principles. Each principle answers "why does the project look like this?" Include the trade-off rejected. Example: *"Principle 3: All judges run on Sonnet, not Opus. Trade-off: Opus would score higher on edge cases, but the cost-per-eval is 3× and the eval volume gated a Haiku release; the team accepted slightly noisier scoring to ship monthly."*

### Step 3 — Where to start

3–5 concrete entry points. Each entry point names a file path, a run command, and a one-sentence outcome. The first entry is "if you read only one thing": the single file that gives the most context per minute.

### Step 4 — Defense-in-depth false-confidence

For each layer of redundancy in the system, name what it protects against AND what it would NOT catch. The pattern: *"Layer X looks like defense-in-depth for Y, but if Z fails, the layer would not notice."* The pattern is critical because layered systems often produce false confidence — a successor who sees three layers may stop investigating, missing the single brittle component all three layers depend on.

### Step 5 — Glossary

Project-specific vocabulary: acronyms invented by the team, internal product names, jargon that overloads standard terms. One sentence per entry. Cross-reference any term that appears in the principles or where-to-start sections.

### Step 6 — What's NOT here

An explicit list of things a reasonable reader might expect but will not find: feature areas that were descoped, libraries that were evaluated and rejected (with the reason), CI gates that are intentionally absent. This section prevents the successor from re-litigating decisions the original team already made.

### Step 7 — Commit + announce

Commit the primer as `PRIMER.md` (project root) or `docs/primer.md`. Link from the project's main README. If the handoff has a date, schedule a 30-minute walkthrough on a calendar in the week the primer ships.

## Outputs

A markdown document at `PRIMER.md` (project root) or `docs/primer.md`, organized as:

1. **Purpose** (3 sentences)
2. **Founding principles** (5–8 numbered with WHY + the rejected trade-off)
3. **Where to start** (3–5 entry points with file path + run command + outcome)
4. **Defense-in-depth false-confidence warnings** (per-layer "looks like X, would not catch Y")
5. **Glossary** (project-specific terms, one sentence each)
6. **What's NOT here** (descoped areas + rejected alternatives + intentional gaps)
7. **Maintainers + escalation** (current owner, escalation contact, project board link if relevant)
8. **Last updated** (date + commit hash)

Target length 800–1500 words; primers longer than ~3 pages are skimmed at best.

## Failure modes

Known pitfalls in primer writing and how this skill catches them:

- **README disguised as primer** (feature list + install steps, no rationale). Caught by: Step 2 requires the WHY + rejected trade-off, which a README never carries.
- **Defense-in-depth false confidence omitted** (the primer lists redundancies as strengths without naming the brittle dependency). Caught by: Step 4 is a required section, not optional.
- **Length bloat** (the successor reads the first page and stops). Caught by: 1500-word soft cap + the "if you read only one thing" entry point in Step 3.
- **Glossary skipped** (the successor hits an acronym in Principle 3 and bounces). Caught by: Step 5 is required; lint suggestion is one entry per acronym that appears in Steps 1–4.
- **No "what's NOT here"** (successor reopens a closed decision because no record exists). Caught by: Step 6 is required; if the team has no rejected alternatives, the project is probably too young for a primer.
- **Stale primer** (the project moves on, the primer rots). Mitigated by: Step 8 records last-updated + commit hash, and the project README links to it so drift is visible.

## References

- [Diátaxis documentation framework](https://diataxis.fr/) — primer is closest to "Explanation" in Diátaxis; the four-quadrant model contextualizes when a primer is the right artifact
- [Will Larson, *An Elegant Puzzle*](https://lethain.com/elegant-puzzle/) — the chapter on rotating engineers through systems motivates primer-as-knowledge-transfer
- [Mozilla's *Open Source Project Templates*](https://github.com/mozilla/open-source-template) — useful starting points for open-source handoffs

## Examples

### Example 1: Long-running ML project handoff (happy-path)

Input: *"I'm rolling off the incident-rank-validation project at the end of the month. There's no one specific successor — whoever picks this up will be a new hire 6 months from now."*

Output: a primer with 3-sentence purpose ("Validates the rank-order of AI incidents under 5 severity scorers using NUTS sampler. Used by the IR team to triage incoming reports. Constraint: cross-platform determinism required — CPU-pinned"); 6 founding principles (one of which: "All sampling is CPU-pinned via OMP_NUM_THREADS=1; trade-off: 4× slower than GPU, but cross-platform determinism was the gating requirement for reproducibility"); 4 entry points starting with `notebooks/00-orientation.ipynb`; defense-in-depth section flagging that the 3 scoring judges look robust but all depend on the same prompt template (single point of brittleness); glossary covering project acronyms; "what's NOT here" listing the GPU acceleration that was tried and rejected.

### Example 2: Throwaway prototype (anti-trigger)

Input: *"I wrote a quick 80-line script to dedupe a CSV. Want a primer for it?"*

Output: skill declines. Explains that a primer is for projects with founding principles worth preserving and successor risk. An 80-line dedupe script needs a docstring at the top of the file and maybe a 3-line README explaining input/output. Hands off to a documentation pattern for scripts.

## See also

- `workflow/writing-release-notes-as-postmortem` — pairs naturally; the primer plus a postmortem-style release-note backlog gives a successor history + current-state in two artifacts
- `workflow/running-adversarial-premortem` — produces the defense-in-depth-false-confidence list the primer's Step 4 needs
- `claude-code-meta/writing-claude-code-skill` (planned) — primers for skills follow this same shape

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 under PRAGMATIC discipline as part of v2-batch-3 (research-discipline cluster)
