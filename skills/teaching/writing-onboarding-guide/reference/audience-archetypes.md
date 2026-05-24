# Audience archetypes for multi-audience onboarding

The seven archetypes the main skill recognizes, with the depth ceiling and the primary decision for each. Pick 2-5 per document.

## Engineer (integration audience)

**Primary decision after reading:** *Can I integrate this into my service in the current sprint?*

**Depth ceiling:** API surface, error model, performance envelope, runbook entry points.

**Below the ceiling (link out):** internal architecture, model training details, business case, long-term roadmap.

**Opener pattern:** *"You will call [endpoint] from [your typical workflow]; the [rate limit / SLA / quota] is [number]. Read this before your next [shift / sprint / deploy]."*

**Required subsections:**
- Endpoints + auth + rate limits
- Error model (codes, retry semantics, idempotency)
- Performance envelope (p50 / p95 / p99, throughput cap)
- Runbook entry point (where the on-call doc lives)
- Versioning + deprecation policy

**Red flag if missing:** an integration-day question lands in the support channel that the engineer section did not pre-answer.

## Scientist (validation audience)

**Primary decision after reading:** *Is this output reliable enough for my downstream model / analysis?*

**Depth ceiling:** evaluation methodology, baselines, drift signals, regression workflow.

**Below the ceiling (link out):** production SLOs, on-call rotation, infra cost detail.

**Opener pattern:** *"[Metric]@[k] on the [eval set] is [value] (baseline: [value]); regressions below [threshold] page the owner. The full eval methodology is in [link]."*

**Required subsections:**
- Eval set name + provenance + size + last refresh
- Headline metric + baseline + current value + threshold
- Drift signals being monitored
- How to file a quality regression (issue template, owner, SLA)
- Known limitations (segments where quality is weak)

**Red flag if missing:** a scientist starts integrating without knowing the metric ceiling, then discovers a quality cliff in production.

## Executive (decision audience)

**Primary decision after reading:** *Should I sponsor / fund / approve this?*

**Depth ceiling:** TL;DR, decision summary, cost, risk surface, dependency map, exit criteria.

**Below the ceiling (link out):** API code, eval methodology, runbook detail, code commit log.

**Opener pattern:** *"This [replaces / enables / accelerates] [business outcome]; it costs [\$ + FTE], the largest risk is [single named risk], and the exit criterion is [measurable]."*

**Required subsections:**
- One-line value proposition (in business language, not technical)
- Cost (infra + FTE + license)
- Single largest risk (named, with mitigation owner)
- Dependency map (vendor / team / system)
- Exit criteria (what would trigger sunset)

**Red flag if missing:** a status review where the executive asks "wait, how much does this cost?" three months after launch.

## Security / compliance (policy-bar audience)

**Primary decision after reading:** *Does this clear our policy bar (security, privacy, regulatory)?*

**Depth ceiling:** threat model, data classification, audit trail, DSR readiness, encryption posture.

**Below the ceiling (link out):** code-level implementation, performance optimization, business case.

**Opener pattern:** *"Data classification: [public / internal / confidential / restricted]. Audit log: [location]. DSR readiness: [days to deletion]. Largest unresolved finding: [name + status]."*

**Required subsections:**
- Data classification + data flows
- Authentication + authorization model
- Audit log location + retention
- DSR / GDPR / sector-specific readiness
- Open findings + remediation owners

**Red flag if missing:** a regulatory ask lands and the team scrambles to assemble evidence from scratch.

## Auditor / external reviewer (attestation audience)

**Primary decision after reading:** *Can I attest to its operation against [control framework]?*

**Depth ceiling:** control mapping, evidence pointers, change history, incident history.

**Below the ceiling (link out):** operational debugging, performance tuning, code internals.

**Opener pattern:** *"Control framework: [SOC 2 / ISO 27001 / NIST CSF / HIPAA / specific subset]. Evidence repository: [link]. Change log: [link]. Last incident: [date + RCA link]."*

**Required subsections:**
- Control framework + scope of attestation
- Per-control evidence pointer
- Change-management process + log
- Incident log + post-mortems
- Governance owner + escalation chain

**Red flag if missing:** an audit window opens and the team builds evidence binders ad hoc.

## Student / learner (skill-acquisition audience)

**Primary decision after reading:** *What do I need to know before I touch this, and where do I start?*

**Depth ceiling:** prerequisites, guided tutorial path, escalation channel.

**Below the ceiling (link out):** API reference, advanced configuration, internal architecture.

**Opener pattern:** *"Before you start: [prerequisite list]. The tutorial path is [steps 1-N]. If you get stuck, post in [channel]."*

**Required subsections:**
- Prerequisites (knowledge + tooling + access)
- Tutorial path (numbered steps, each with a checkpoint)
- Common pitfalls (named, with how-to-recover)
- Escalation channel (one place to ask for help)

**Red flag if missing:** a learner drops out at step 3 because step 2's checkpoint was implicit.

## Instructor / TA (pedagogy audience)

**Primary decision after reading:** *How do I teach this with it?*

**Depth ceiling:** pedagogy notes, common student pitfalls, reference solutions, assessment hooks.

**Below the ceiling (link out):** production deployment, scaling, security hardening.

**Opener pattern:** *"This module covers [learning objectives]. Common student failure modes are [list]. Reference solutions are at [link]. Assessment rubric is [link]."*

**Required subsections:**
- Learning objectives (Bloom-level if applicable)
- Suggested teaching sequence
- Common student pitfalls + diagnostics
- Reference solutions / answer keys
- Assessment rubric pointer

**Red flag if missing:** a TA discovers in office hours that the doc has no answer key.
