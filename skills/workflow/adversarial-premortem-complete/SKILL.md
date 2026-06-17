---
name: adversarial-premortem-complete
description: >
  Runs a multi-subagent adversarial premortem on a spec, plan, design, paper, or codebase by
  orchestrating six independent perspectives (Red Teamer, Data Scientist, ML Engineer, Security
  Architect, MLOps/SRE, Governance/Risk) as parallel subagents across up to five rounds. Each
  perspective reads the artifacts in its own context and returns evidence-anchored findings with
  calibrated confidence bands; the orchestrator cross-attacks, adjudicates posteriors, applies a
  drop rule, and emits a prioritized remediation plan. Use for high-stakes AI, ML, data-science,
  agentic, MLOps, or security-sensitive artifacts where one reviewer's depth is not enough and the
  cost of being wrong is high. For a single-session multi-round premortem without subagents, use
  adversarial-premortem-single.
version: 0.1.0
status: shipped
track: workflow
audience: [security-eng, ai-security, ml-engineer, data-scientist, skill-author]
evidence:
  - ATACE
  - incident-rank-validation
  - TRACT
last-updated: 2026-06-17
---

# Adversarial Premortem (Multi-Subagent)

An adversarial premortem inverts normal review. Instead of asking "is this good," it assumes the spec, plan, or code has already failed six months from now, then works backward from that failure state to the cause. This variant runs the attack as a team: each perspective gets its own subagent with a clean context window, reads the artifacts independently, and returns findings the orchestrator then cross-examines and calibrates. The output is a prioritized remediation plan that closes the gaps before they become incidents.

This is not a vibe check. Speculation is the failure mode the skill exists to prevent. False precision is the second.

## When to use

Trigger this skill when the user asks for or implies one of:

- A red-team, stress-test, pressure-test, pre-mortem, or "tear this apart" pass on a spec, plan, design, paper, or codebase
- A failure-mode analysis for a high-stakes AI, ML, data-science, agentic, MLOps, or security-sensitive system before committing to it
- Phrases like "red team this," "what breaks," "stress test the plan," "poke holes," "what did the team miss," or "assume this failed"
- A multi-component artifact where one reviewer's depth is not enough and six independent lenses (adversarial, data, modeling, security, operations, governance) each have something anchored to attack

## When NOT to use

Hand off to a different skill when:

- The user wants a simple code review for a specific bug → use a debugging or code-review pattern
- The user wants new ideas → use brainstorming (this skill assumes the idea exists and stress-tests it)
- The artifact has not been written yet → run brainstorming or planning first, then return for premortem
- A single-session multi-round pass is enough and subagent orchestration is overkill → use `workflow/adversarial-premortem-single`
- The artifact is a one-line change or a tiny script where the orchestration overhead exceeds the blast radius

## Quick start

User says: "Here is the spec and code for our RAG-backed support agent. Red-team it before we ship."

Skill response: inventories the named artifacts (spec, retriever, prompts, tools, eval harness, deploy config), then spawns six perspective subagents in parallel for round 1, collects their evidence-anchored findings, cross-attacks each finding against the others, sets a posterior confidence band per finding, drops anything below Plausible to a retrievable ledger, and proceeds round by round (data, methodology, security, MLOps, governance) until convergence. It ends with a prioritized remediation plan ordered by expected cost reduction.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| artifact | file path(s) or pasted text | yes | — | The spec, plan, design, paper, or codebase to premortem, plus the paths to source, configs, schemas, eval harness, prompts, and data artifacts it names. |
| scope_hint | string | no | "full artifact" | Narrow the premortem to one component, layer, or claim when the artifact is too large for one pass. |
| max_rounds | integer | no | 5 | Cap on rounds. Each round attacks a distinct layer; convergence usually stops the run before five. |
| perspectives | list | no | all six | Override the default six perspectives. Skip a perspective only when it has nothing anchored to attack, and log the skip. |
| subagent_model | env `CLAUDE_CODE_SUBAGENT_MODEL` | no | inherit | Optional cost control: a smaller model for the perspective subagents while the orchestrator stays on the stronger model for adjudication. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact. As orchestrator you are also a disciplined Bayesian: treat every design choice as a hypothesis and every counterargument as evidence that moves a belief, not a gate that passes or fails it. Do not analyze the artifacts yourself first. Delegate each perspective to its own subagent, then adjudicate and calibrate.

## Workflow

Copy this checklist into the response and check off items as the premortem progresses:

```
Adversarial premortem progress:
- [ ] Step A: Inventory the artifacts, resolve paths, record named-but-unspecified components as findings
- [ ] Step B: Spawn the round's perspective subagents in one message (parallel)
- [ ] Step C: Cross-attack, update each finding prior → posterior, apply the drop rule, merge duplicates
- [ ] Step D: Write the round, check the stop signal, continue or converge (up to 5 rounds)
- [ ] Final: Dropped ledger, convergence statement, prioritized remediation plan, residual risk
```

### Orchestration model

The session is the orchestrator. Each perspective gets its own subagent with a clean context window so it reads the artifacts independently and its deep reading never pollutes the orchestrator context. The orchestrator collects findings, runs the cross-attack, and sets the final confidence.

- Spawn each perspective as a subagent (the Task tool in Claude Code).
- Launch all of a round's subagents in a single message so they run in parallel. Sequential spawning makes the premortem far slower.
- Subagents cannot spawn their own subagents. The cross-attack and confidence updating happen in the orchestrator context.
- Up to 10 subagents run concurrently; six perspectives per round fits inside that limit.
- If the Task tool is unavailable (for example, running outside Claude Code), fall back to running each perspective as a separate, clearly labeled analytical pass in one context, in sequence. The structure and output format do not change.

### Step A: Inventory, then delegate

Do a fast inventory pass. Read the spec or plan, list the referenced source files, configs, schemas, training scripts, eval harnesses, prompts, and data artifacts, and resolve their paths. Hand those paths to the subagents. Do not do the deep read in the orchestrator context. If a component is named but not specified, record that omission as a finding before delegating.

### Step B: Spawn one subagent per perspective

For each round, spawn these six perspectives in one message so they run in parallel. Each gets the same artifact paths and the same round attack surface, but a different lens:

- **Red Teamer** — adversarial misuse, abuse paths, what a hostile actor or malicious input does to this layer.
- **Data Scientist** — data validity, label definition, leakage, distribution shift, sample size, class balance, metric soundness.
- **ML Engineer** — model and code correctness, training and serving behavior, reproducibility, integration and wiring.
- **Security Architect** — trust boundaries, authorization scope, secrets handling, supply chain, injection surface.
- **MLOps / SRE** — deploy, monitoring, drift, rollback, canarying, cost ceilings, latency budgets, on-call burden, recovery.
- **Governance / Risk** — success-metric-to-business-outcome mapping, oversight model, accountability, regulatory exposure, cost of being wrong.

Skip a perspective only when it has nothing anchored to attack in this layer, and log the skip with the reason. Give each subagent the prompt in `reference/subagent-prompt-template.md`, filling the bracketed slots.

### Step C: Cross-attack, update confidence, then drop

Collect all returned findings. Merge duplicates into one before scoring, crediting the strongest evidence anchor. Run the cross-examination the subagents could not run on each other, then set each finding's posterior confidence (prior band → evidence → posterior, with one line naming what moved it). Apply the calibration penalties and the drop rule in `reference/confidence-and-drop-rule.md`. Findings at Plausible or above stay in the report body; Unlikely or Remote findings move to the dropped ledger with their reason. A Critical and irreversible finding below Plausible goes to a separate tail-risk line with the trigger that would raise its confidence, never deleted.

### Step D: Write the round, check the stop signal, continue

Write the round in the format in `reference/round-report-format.md`. Stop when a round yields no surviving findings at Plausible or above, or when the only survivors are Low impact. That shift is the convergence signal. Otherwise proceed to the next round, up to five.

### The five rounds

Each round attacks a distinct layer; the lead perspective frames it, but all six attack unless one has nothing anchored.

1. **Problem framing and data** (lead: Data Scientist) — hypothesis validity, label definition, leakage, distribution shift, sample size, class balance, whether the dataset can answer the question.
2. **Methodology and modeling** (lead: ML Engineer) — model choice, baselines, ablations, hyperparameter search, regularization, evaluation metrics, statistical significance, reproducibility.
3. **Security and adversarial robustness** (leads: Red Teamer, Security Architect) — prompt injection, data poisoning, model extraction, membership inference, supply-chain exposure, authorization scope, abuse paths.
4. **Implementation and MLOps** (lead: MLOps / SRE) — integration gaps, training/serving skew, drift monitoring, rollback, canarying, lineage, secret handling, cost ceilings, latency budgets, incident playbooks.
5. **Governance, business outcome, second-order effects** (lead: Governance / Risk) — metric-to-outcome mapping, oversight, accountability, regulatory exposure, opportunity cost, cost of being wrong.

Apply the rounds to everything the spec names (data, labels, features, training, eval, deployment, monitoring, agents, tools, prompts, retrieval, guardrails, human oversight), not just the headline model. The headline model is rarely where the failure starts.

### Self-verify before finalizing each round

1. Every finding cites a specific spec passage, file, function, or data artifact.
2. Each surviving verdict withstood cross-attack from at least one other perspective.
3. Every surviving finding shows an impact severity and a posterior confidence band, and the band names the evidence that set it.
4. Nothing below Plausible sits in the report body; everything dropped sits in the ledger with its reason, and Critical irreversible drops sit in the tail-risk line.
5. No decimal probability appears without a cited base rate.
6. Recommendations are concrete enough that an implementer can execute without a follow-up question.

## Outputs

A markdown report labeled with the artifact under review, its commit or version if known, and the date. Per round: the perspectives spawned (and any skipped, with reason), a one-paragraph premortem narrative of the failure state six months out, the surviving findings (impact, posterior confidence with prior and what moved it, evidence anchor, failure mode, blind spot, opportunity cost), and a cross-attack log. After the final round: the dropped ledger (one line per drop plus parked tail risks), a convergence statement, a prioritized remediation plan ordered by expected cost reduction per unit of effort (impact weighted by posterior confidence), and a residual-risk section. The full templates are in `reference/round-report-format.md`.

## Failure modes

- **Premortem theater** — going through the motions without genuine adversarial engagement. Caught by: the per-finding evidence anchor and the required cross-attack from another perspective.
- **False precision** — printing decimal probabilities the evidence does not support. Caught by: the rule that no decimal appears without a cited base rate; bands, not numbers, are the default.
- **Correlated-evidence inflation** — the same finding from several perspectives read as independent confirmation. Caught by: the calibration penalty that raises a band only when perspectives bring genuinely different evidence.
- **Dropping the catastrophe** — deleting a low-probability, high-impact finding with the rest of the Unlikely findings. Caught by: the tail-risk carve-out that parks Critical irreversible drops with their trigger.
- **Subagent context pollution** — the orchestrator doing the deep read itself, which defeats the clean-context design. Caught by: Step A keeping the deep read in the subagents.
- **Silent perspective skip** — dropping a lens without saying so. Caught by: the rule to log every skipped perspective with its reason.

## References

- `reference/subagent-prompt-template.md` — the per-perspective Task subagent prompt template
- `reference/round-report-format.md` — the per-round and final output templates
- `reference/confidence-and-drop-rule.md` — confidence bands, calibration penalties, the drop rule, the tail-risk carve-out
- [Klein 2007, *Performing a Project Premortem*, Harvard Business Review](https://hbr.org/2007/09/performing-a-project-premortem) — origin of the premortem method
- [Anthropic Skill best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — subagent orchestration and workflow-checklist patterns

## Examples

### Example 1: Multi-component ML system (happy-path)

Input: "Here is the spec and code for our RAG-backed support agent. Red-team it before we ship."

Output: Skill inventories the artifacts, then spawns six perspective subagents in parallel for round 1. The Data Scientist flags an eval set drawn from the same tickets used to build the retriever (leakage); the Security Architect flags an unauthenticated tool the agent can call; the MLOps perspective flags no rollback path for a bad prompt deploy. The orchestrator cross-attacks each, sets posteriors, drops two Unlikely findings to the ledger, parks one Critical-but-Remote data-exfiltration path in the tail-risk line, and produces a remediation plan ordered by expected cost reduction.

### Example 2: One applicable perspective (edge-case)

Input: "Premortem this nightly batch ETL job that dedupes a customer table. No model, no serving, no agent."

Output: Skill engages but logs that the ML Engineer (no model), Red Teamer (no external attack surface), and Governance perspectives have little anchored to attack here, and concentrates the Data Scientist and MLOps/SRE perspectives on the dedupe logic, idempotency, and rollback. It states the skipped perspectives and why, rather than forcing six full lenses onto a two-lens artifact.

### Example 3: Single bug (anti-trigger)

Input: "Can you check my Python loop for off-by-one errors? `for i in range(len(arr)): print(arr[i+1])`"

Output: Skill declines the multi-subagent orchestration. It explains that a premortem team is for high-stakes designs with multiple plausible failure modes, points out the off-by-one directly, and hands off to a debugging pattern (or to `adversarial-premortem-single` if the user wants a structured single-pass review of a larger artifact).

## See also

- `workflow/adversarial-premortem-single` — the single-session multi-round version when subagent orchestration is overkill
- `workflow/auditing-mathematical-claims` — narrower variant focused on proof and math claims
- `security/threat-modeling-agentic-systems` — threat-model an agentic system before the premortem stress-tests the design
- `workflow/writing-successor-primers` — pairs well after the premortem identifies areas a successor needs to know

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-06-17
- Provenance: migrated from `~/.claude/skills/adversarial-premortem.skill` and reformatted to the RCS Layer-3 contract. Named `adversarial-premortem-complete` to differentiate from the single-session `adversarial-premortem-single`.
