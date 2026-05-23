---
name: building-canary-rollout
description: >
  Builds a canary rollout plan for a new model version — a traffic-split definition,
  per-cohort online metrics, a guardrail-metric set with pre-committed thresholds,
  and an auto-rollback trigger. Triggers when the user is promoting a packaged
  model to production, when a teammate proposes a 0%-to-100%-overnight flip, when
  per-cohort regression risk is at issue, or when "the new model looks better
  offline but we're not sure online." Refuses to recommend canary on single-user
  / single-tenant / no-traffic systems where statistical comparison is impossible.
version: 0.1.0
status: shipped
track: ml-datasci
audience:
  - ml-engineer
  - data-scientist
  - devops
  - security-eng
evidence:
  - DU-MSDSAI-4432-DiabetesDiseasePrediction
  - email-spam-classifier-naive-bayes-comparisson-roc
last-updated: 2026-05-23
---

# Building Canary Rollout

## When to use

Trigger this skill when:

- A new model version (packaged per `ml-datasci/packaging-model-for-deployment`) is about to replace a production model and the user wants to limit blast radius
- The user proposes a "Friday afternoon flip" / "deploy everywhere overnight" / 0%-to-100% promotion
- An offline metric improved but online behavior under real traffic is not yet known
- The deployment surface has multiple cohorts (geographies, customer tiers, device classes, locales) and the user has not stated how the canary will be allocated
- Keywords: canary, rollout, traffic split, A/B, guardrail, shadow traffic, ramp, promotion

## When NOT to use

Skip this skill and hand off when:

- The system has a single user / single tenant / no meaningful production traffic — there is no statistical comparison to be made; ship behind a feature flag and monitor manually
- Offline-only batch scoring with no user-facing surface — no canary needed; compare batch outputs head-to-head against the previous version
- The model is not yet packaged — use `ml-datasci/packaging-model-for-deployment` first; canary on an unpackaged artifact is operationally unsound
- The system has no observability (no per-cohort metric emission, no rollback path) — fix observability first; canary without metrics is theater
- The deployment is the very first version of the system (no champion model to canary against) — ship to a percentage of traffic, but the framing is staged rollout, not canary comparison

## Quick start

User: "We're about to promote `churn-rf v0.2.0` to production, replacing `v0.1.0`. The product team wants the new model live by Friday. How should I roll it out?"

Response: A 4-stage canary plan with pre-committed guardrail thresholds and an auto-rollback trigger wired BEFORE the first traffic flip.

```yaml
canary:
  champion: churn-rf:0.1.0
  challenger: churn-rf:0.2.0
  stages:
    - traffic_pct: 1    # smoke-on-real-traffic; minimum to detect crash loops
      duration_hours: 4
      gate: no_crashes AND no_p99_latency_regression
    - traffic_pct: 5
      duration_hours: 24
      gate: business_metric_within_band AND no_cohort_regression
    - traffic_pct: 25
      duration_hours: 48
      gate: business_metric_neutral_or_better AND no_cohort_regression
    - traffic_pct: 100
      duration_hours: open
      gate: monitoring_only

guardrails:
  business_metric:
    name: conversion_rate
    direction: higher_is_better
    min_acceptable_delta_pct: -0.5    # rollback if challenger is > 0.5% worse than champion
    confidence: 0.95
  technical_metric:
    name: p99_latency_ms
    direction: lower_is_better
    max_acceptable_delta_ms: 20
  per_cohort_check:
    cohorts: [geo, tier, device]
    min_sample_per_cohort: 1000
    rule: no_cohort_regresses_by_more_than_2pct

auto_rollback:
  triggers:
    - crash_rate > 0.1%
    - p99_latency_ms > champion_p99 + 50
    - business_metric_delta < min_acceptable_delta AND p < 0.01
  action: route_100pct_to_champion
  notify: ["#ml-oncall"]
```

The traffic-split mechanism (Envoy / Istio / framework-level / load-balancer weights / feature-flag service) is implementation-dependent; the plan above is platform-agnostic.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `champion` | str (model:version) | yes | — | The currently-serving model that the canary will be compared against. |
| `challenger` | str (model:version) | yes | — | The new model version being canaried. Must be packaged per `ml-datasci/packaging-model-for-deployment`. |
| `stages` | list of `{traffic_pct, duration, gate}` | yes | — | The ramp schedule. Minimum 3 stages — small smoke, intermediate, full. |
| `business_metric` | dict | yes | — | Name + direction (higher/lower is better) + minimum acceptable delta + statistical confidence. The thing the system actually exists to optimize. |
| `technical_metrics` | list of dicts | yes | — | Latency (p50, p95, p99), error rate, throughput, with deltas tolerated relative to champion. |
| `cohorts` | list of str | yes | — | Dimensions the per-cohort regression check must split on. Minimum: geo + tier (or equivalent). |
| `min_sample_per_cohort` | int | yes | — | Below this, the per-cohort check is statistically meaningless; either skip the cohort or extend the stage. |
| `auto_rollback_triggers` | list of expressions | yes | — | Pre-committed thresholds that, when crossed, route 100% of traffic back to champion WITHOUT manual approval. |

## Workflow

Copy this checklist into the response:

```
Canary rollout progress:
- [ ] 0. Confirm champion + challenger are both packaged (manifest + smoke test + version pin)
- [ ] 1. Pre-commit the business metric, direction, minimum acceptable delta, and statistical confidence
- [ ] 2. Pre-commit technical-metric guardrails (latency p99, error rate, throughput) with tolerated deltas
- [ ] 3. Define cohorts (geo / tier / device / locale) and the minimum sample per cohort
- [ ] 4. Define stage schedule (≥ 3 stages from 1% → 5% → 25% → 100%) with per-stage gates
- [ ] 5. Wire the auto-rollback trigger — a deterministic threshold rule, NOT a manual decision
- [ ] 6. Verify per-cohort metric emission and rollback path BEFORE the first traffic flip
- [ ] 7. Run stage 1 (smoke on real traffic); check crash / latency only
- [ ] 8. Run subsequent stages with the business + cohort checks; advance only if every gate passes
- [ ] 9. Post-rollout review: did the offline metric predict the online one? File the delta as evidence for the next canary
```

### Step 1: Pre-commit the business metric

Pick ONE primary business metric. The system exists to optimize this; everything else is guardrail. Common choices: conversion rate, click-through rate, retention, ticket-resolution time, false-positive rate (for a moderation system). Direction (higher is better / lower is better) and minimum acceptable delta must be set BEFORE the canary launches. "We'll know it when we see it" is not a guardrail.

### Step 2: Technical guardrails

Latency (p99 in particular), error rate, throughput. These are platform health metrics, not business metrics — but a regression on any of them rolls back regardless of business metric direction. Common deltas: p99 latency +20ms tolerated, error rate no more than +0.1 percentage points, throughput within ±5%.

### Step 3: Cohorts

Average can be flat while a subgroup regresses badly. The minimum cohort split is geo + tier (or the deployment's analogues — region + customer segment, locale + device class, etc.). Per-cohort sample-size requirement is a precondition for the cohort check; if the smallest cohort cannot reach the minimum in the planned stage duration, extend the duration or skip the cohort check at that stage.

### Step 4: Stage schedule

Minimum 3 stages. The first stage is "is this thing even crashing under real traffic" — 1% for ~4 hours. Each subsequent stage tests larger blast radius with progressively stricter business / cohort gates. The final stage is 100% with monitoring-only.

### Step 5: Auto-rollback trigger

The trigger is a DETERMINISTIC rule, not a Slack thread. When the rule fires, traffic routes back to champion AUTOMATICALLY. Common triggers:

- `crash_rate > 0.1%` — challenger is faulting
- `p99_latency > champion_p99 + 50ms` — challenger is degraded
- `business_metric_delta < min_acceptable AND p < 0.01` — challenger is actively worse, with high statistical confidence

Manual rollback is the second line; the auto-trigger is the first.

### Step 6: Verify observability + rollback path BEFORE flipping

Run a "rollback drill" before stage 1: deliberately route a tiny slice to challenger, verify per-cohort metrics emit, then trigger the auto-rollback (or its manual equivalent) and verify traffic returns to champion. A canary plan that has never been rehearsed is not a plan.

### Step 7-8: Advance only if every gate passes

A stage that misses ANY gate (business, technical, or per-cohort) halts the rollout. The default action is to extend the stage, gather more data, then re-evaluate. Auto-rollback fires only on the pre-committed triggers; in-between is "halt and investigate."

### Step 9: Post-rollout review

After 100% promotion, file a one-page review: did the offline metric direction match the online one? By how much? Which cohort surprised you? The next canary inherits these calibration corrections — the offline-vs-online gap is one of the most underused signals in MLOps.

## Outputs

A markdown / YAML canary plan with:

1. **Rollout stages** — table of traffic_pct · duration · gate per stage
2. **Guardrail metrics** — business metric (name + direction + min delta + confidence); technical metrics (p99 latency, error rate, throughput) with tolerated deltas
3. **Cohort definition** — list of dimensions + minimum sample size per cohort
4. **Auto-rollback rules** — pre-committed deterministic triggers + escalation paths
5. **Rollback drill log** — proof the rollback path was rehearsed before stage 1
6. **Post-rollout review template** — to be filled in after 100% promotion, capturing the offline-vs-online metric gap

## Failure modes

- **Average metric is flat, a cohort regresses 10%** — caught by the per-cohort regression check (step 3); halts the stage before promotion.
- **Auto-rollback never fires because the trigger threshold was vague** — caught by step 5 (deterministic thresholds, not "judgement-call" rules).
- **"Friday afternoon flip" with no stages** — caught by step 4 (minimum 3 stages); 0%-to-100% is not a canary.
- **Per-cohort sample is too small to reach significance in the stage window** — caught by step 3 (`min_sample_per_cohort` precondition); either extend the stage or drop the cohort check for that stage.
- **Rollback path was never tested** — caught by step 6 (rollback drill required before stage 1).
- **Offline metric improved, online metric regressed, no one noticed** — caught by step 9 (post-rollout review compares offline-vs-online).
- **Canary applied to a system with no traffic** — caught by the `When NOT to use` section (statistical comparison requires real traffic volume).

## References

- [Google SRE Workbook — Canarying releases](https://sre.google/workbook/canarying-releases/) — staged-rollout pattern and auto-rollback discipline
- [Kohavi, Tang, Xu — *Trustworthy Online Controlled Experiments* (2020)](https://experimentguide.com/) — guardrail metrics, cohort splits, statistical power for online A/B tests
- [Envoy weighted clusters](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers#weighted-load-balancing) — traffic-split mechanism for service-mesh deployments
- `ml-datasci/packaging-model-for-deployment` — required pre-step; canary on an unpackaged model is unsound
- `ml-datasci/building-rollback-plan` — the reversal-path skill the auto-rollback trigger fires
- `ml-datasci/evaluating-binary-classifiers` / `ml-datasci/evaluating-regression-models` — the offline metric the canary will compare against online performance

## Examples

### Example 1: 5% canary, multi-cohort (happy-path)

Input: "Promoting `churn-rf v0.2.0` to replace `v0.1.0`. Plan the rollout."

Output: Skill produces a 4-stage plan (1% → 5% → 25% → 100%), pre-commits conversion rate as the business metric with a –0.5% minimum acceptable delta at 95% confidence, sets p99-latency-+20ms and error-rate-+0.1pp as technical guardrails, splits per-cohort regression checks on geo + tier with a 1000-sample minimum, and wires a deterministic auto-rollback on crash rate > 0.1% OR business-metric delta < min AND p < 0.01. Requires a rollback drill before stage 1.

### Example 2: Imbalanced cohorts (edge-case)

Input: "We want to canary the new model, but our enterprise tier has 200 requests / day and our SMB tier has 50,000 / day. How do we handle the cohort check?"

Output: Skill flags that the enterprise cohort will not reach a meaningful sample within the 5% / 24h stage. Recommends one of: (a) extend the enterprise stage duration until enterprise hits the minimum (e.g. 14 days at 5%), (b) lower the per-cohort sample minimum at the cost of statistical power (and document this trade-off in the canary plan), or (c) skip the per-cohort check for enterprise at this stage and defer it to a longer post-100% monitoring window. Refuses to treat 200 requests as a statistically valid cohort.

### Example 3: Single-user / internal-only system (anti-trigger)

Input: "Our model serves an internal dashboard with 3 analyst users. We want to canary the new version."

Output: Skill does NOT engage the canary workflow. Explains that statistical comparison requires meaningful traffic volume; 3 users is below any reasonable cohort threshold. Recommends shipping behind a feature flag with manual sign-off from the analyst team, plus a documented rollback path (cross-reference `ml-datasci/building-rollback-plan`). Canary is for production-traffic systems, not internal-tools.

## See also

- `ml-datasci/packaging-model-for-deployment` — required pre-step; canary an artifact with a manifest + smoke test, not a bare pickle
- `ml-datasci/building-rollback-plan` — the reversal workflow the auto-rollback trigger executes
- `ml-datasci/evaluating-binary-classifiers` / `ml-datasci/evaluating-regression-models` — offline metric + 95% CI that the online canary will compare against
- `ml-datasci/auditing-train-test-split` — the leakage discipline that makes the offline-to-online comparison fair

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-1, skill 5.1.2) via PRAGMATIC discipline
