---
name: running-adversarial-premortem
description: >
  Runs a structured multi-round adversarial premortem on a spec, plan, design, paper,
  proof, or codebase. Assumes the artifact has already failed six months out, works
  backward to identify causes, scores each surviving failure mode with a calibrated
  confidence band, and emits a prioritized remediation plan. Use when the cost of
  being wrong is high — AI security designs, ML system architecture, mathematical
  proofs, agentic-system designs, or any high-stakes plan where surfacing failure
  modes you would otherwise miss is the goal.
version: 0.1.0
status: shipped
track: workflow
audience: [security-eng, ai-security, ml-engineer, data-scientist, skill-author]
evidence:
  - ATACE
  - incident-rank-validation
  - TRACT
last-updated: 2026-05-23
---

# Running an Adversarial Premortem

## When to use

Trigger this skill when the user asks for or implies one of:

- A premortem, devil's-advocate review, or red-team pass on a spec, plan, design, paper, proof, or codebase
- A check on a mathematical or empirical claim where the cost of being wrong is high (research papers, regulatory submissions, safety arguments)
- A failure-mode analysis for an AI / ML / agentic / MLOps / security-sensitive design
- Phrases like "what would go wrong with...", "stress-test this plan", "what am I missing?", "argue against this"

## When NOT to use

Skip this skill and hand off to a different one when:

- The user wants a simple code review for bugs → use a debugging or code-review pattern
- The user wants a brainstorm for new ideas → use brainstorming (this skill is the inverse: it assumes the idea exists and stress-tests it)
- The artifact has not been written yet → run brainstorming or planning first, then return for premortem
- The artifact is a small bug fix or one-line change where premortem overhead exceeds blast radius

## Quick start

User says: "I just finished my paper claiming that all transformer attention heads are equivalent for short sequences. Can you premortem the math claims?"

Skill response: structured premortem report covering (1) the strongest counter-argument to the main claim, (2) per-claim audit table with location + concern + strongest-counter + stops-mattering-if, (3) prioritized remediation list, (4) confidence bands.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| artifact | file path or pasted text | yes | — | The spec, paper, plan, code, or proof to premortem. |
| scope_hint | string | no | "full artifact" | Narrow the premortem to a section, claim, or component if the artifact is too large to cover in one pass. |
| confidence_format | "calibrated" \| "binary" \| "qualitative" | no | "calibrated" | Output format for confidence per failure mode. |
| stop_after_rounds | integer | no | 3 | Cap on premortem rounds (each round may surface new failure modes; diminishing returns past 3). |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as the premortem progresses:

```
Premortem progress:
- [ ] Round 1: Assume failure → enumerate top-level failure modes
- [ ] Round 2: For each failure mode, work backward to root causes
- [ ] Round 3: Score each surviving failure mode (severity × likelihood × detectability)
- [ ] For each high-priority failure mode, write: location · concern · strongest-counter · stops-mattering-if
- [ ] Prioritized remediation plan
```

### Round 1: Assume failure

The artifact has already failed six months from now. Independently of the artifact's claims, ask: what is the most likely way this failed?

Generate 5–10 top-level failure modes. Categories to seed (use as appropriate):

- **Premise failure** — the claim is wrong; the data don't support it; the proof is flawed
- **Methodology failure** — the experimental design is wrong; the eval is biased; the dedupe is broken
- **Implementation failure** — code does not match design; off-by-one; race condition; memory leak
- **Operational failure** — the system is deployed wrong; monitoring is missing; rollback is impossible
- **Reception failure** — the audience misinterprets the result; the title oversells; the limitations are buried
- **Defense-in-depth-creates-false-confidence failure** — multiple layers of "safety" mask the actual brittle component

### Round 2: Backward chain to root cause

For each top-level failure mode, ask "why did this fail?" and write the strongest version of the answer. Repeat 3–5 times to reach a root cause.

### Round 3: Score and triage

For each surviving failure mode, produce:

```
Failure mode: <short name>
Location: <file:line / section / claim>
Concern: <one paragraph; the strongest version of the worry>
Strongest counter: <the most generous defense of the artifact>
Stops mattering if: <falsifiable stopping condition — what would have to be true to stop worrying>
Severity: 1–5 (1 = mildly embarrassing; 5 = retraction / safety incident)
Likelihood: 1–5 (calibrated)
Detectability: 1–5 (1 = invisible until a postmortem; 5 = caught by existing CI)
Priority = Severity × Likelihood / Detectability
```

### Remediation

Sort by priority descending. For the top half:

- Specific fix proposal
- What the fix costs (effort, schedule, scope reduction)
- What the fix does NOT solve

## Outputs

A markdown report with the following structure:

1. **Executive summary** (3 sentences max): the single highest-priority concern and recommended next step
2. **Per-claim audit table** (one row per failure mode): Location · Concern · Strongest counter · Stops mattering if · Severity · Likelihood · Detectability · Priority
3. **Prioritized remediation list** (top-half failure modes only)
4. **Calibrated confidence**: the premortem itself has limitations; state them

## Failure modes

Known pitfalls in running premortems and how this skill catches them:

- **Premortem theater** — going through the motions without genuine adversarial engagement. Caught by: requiring the "strongest counter" field (forces engagement with the artifact's defense).
- **Defense-in-depth false confidence** — listing many low-priority concerns masks one high-priority one. Caught by: explicit prioritization formula + remediation list limited to top-half.
- **Stops-mattering-if omission** — concerns that have no falsifiable stop condition are worry, not analysis. Caught by: required "stops mattering if" field per failure mode.
- **Scope overflow** — running premortem on a 10K-line spec produces noise. Caught by: `scope_hint` argument + Round 1 categorical seeding.

## References

- `reference/premortem-template.md` — the per-claim table template
- `reference/seed-failure-categories.md` — expanded category descriptions
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — for workflow-checklist pattern
- [Klein 2007 *Performing a Project Premortem*, Harvard Business Review](https://hbr.org/2007/09/performing-a-project-premortem) — origin of the premortem method

## Examples

### Example 1: Mathematical paper premortem (happy-path)

Input: "I just finished my paper claiming that all transformer attention heads are equivalent for short sequences. Can you premortem the math claims?"

Output: Skill produces a per-claim audit table — Theorem 1 (claim "equivalent" under specific norm; counter: "equivalent" is used loosely on a 6-element finite set, true isomorphism would require demonstrating bijection of operations not just sets), Theorem 2 (polynomial bound vs claimed exponential), Lemma 1 (dilution vs steering conflation). Emits stops-mattering-if conditions per claim.

### Example 2: Anti-trigger (simple bug review)

Input: "Just review my code for off-by-one errors in this loop."

Output: Skill refuses to engage premortem. Explains that premortem is for high-stakes designs with multiple plausible failure modes; for a single-bug code review, debugging or code-review patterns are the right tool. Hands off.

## See also

- `workflow/pre-registering-eval-study` — the prospective version of this skill
- `workflow/auditing-mathematical-claims` — narrower variant focused on proof claims
- `workflow/writing-successor-primers` — pairs well after premortem identifies areas a successor needs to know

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: migrated from `~/.claude/skills/adversarial-premortem.skill` (zip-encoded); reformatted to Layer-3 contract
