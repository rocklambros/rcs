---
name: building-rollback-plan
description: >
  Builds a model-rollback plan — a versioned artifact store, a documented runbook
  that names who decides / what triggers / how state is handled, and a smoke-test
  gate that the previous version must clear before traffic returns to it. Triggers
  when a model is being promoted to production, when an oncall asks what to do if
  the new model breaks, when state migrations between versions are at issue, or
  when the deployment has stateful behavior (caches, sessions, downstream writes).
  Refuses to certify a rollout as production-ready without a tested rollback path,
  and refuses to engage the full workflow for throwaway / experimental models
  with no real impact surface.
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

# Building Rollback Plan

## When to use

Trigger this skill when:

- A new model version is about to be promoted to production (whether via canary, blue/green, or shadow)
- An incident commander or oncall is asking "what do we do if the new model misbehaves"
- The system has STATEFUL behavior — caches keyed by model output, sessions that carry model state, downstream writes that depend on the schema of model output — and the user has not stated how state is reconciled on rollback
- The deployment uses a custom traffic-routing mechanism (feature flag, weighted ingress, lambda alias) and the user has not documented the reverse path
- Keywords: rollback, revert, undo, blue/green, fallback, runbook, on-call, hotfix, recovery, RTO, MTTR

## When NOT to use

Skip this skill and hand off when:

- The model is experimental / sandboxed with no production impact — the cost of "the experiment crashes" is low; do not invest in runbook machinery
- The deployment surface has no real users or no downstream consumers — there is nothing to roll back to
- The model is not yet packaged — use `ml-datasci/packaging-model-for-deployment` first; a rollback plan needs a previous-version artifact to point at
- The user is asking about a rollout strategy (canary, A/B) — that is `ml-datasci/building-canary-rollout`; the rollback plan is the reversal path that canary's auto-rollback executes
- The user is asking about data-pipeline rollback (schema migrations, ETL reversal) — adjacent topic, different skill (data-pipeline rollback is not a model concern alone)

## Quick start

User: "We're about to promote `recommender v3.1` to replace `v3.0` in production. The model writes recommendation IDs to a session cache that downstream services read. What does the rollback plan look like?"

Response: A 6-part runbook — artifact store reference, triggers, decision authority, traffic-routing reversal, state reconciliation, smoke-test gate — written BEFORE the rollout and tested in a drill.

```markdown
# Rollback runbook — recommender v3.1 → v3.0

## 1. Versioned artifact store
- Champion (previous): `artifacts/recommender/3.0.4/` (manifest.json, model.joblib, smoke.json present)
- Challenger (new):    `artifacts/recommender/3.1.0/`
- Retention: all versions ≥ N-2 retained for 90 days
- Loader contract: handler accepts `MODEL_VERSION` env var; no code change required to switch

## 2. Rollback triggers (deterministic, pre-committed)
Auto-trigger when ANY:
- crash_rate > 0.1% over a 5-minute window
- p99_latency_ms > champion_p99 + 50ms over a 10-minute window
- business_metric (CTR) delta < -1.0% AND p < 0.01 over the canary stage window
Manual-trigger when an oncall judges:
- Cohort regression invisible to the auto-trigger (e.g. one customer-tier failing silently)
- Downstream consumer complaints exceed a documented threshold

## 3. Decision authority
- Auto-trigger fires: no human approval required; route to champion immediately
- Manual-trigger: oncall on-shift can route to champion unilaterally; postmortem follows
- Manager / VP approval is NOT a precondition for rollback

## 4. Traffic-routing reversal
- Primary mechanism: feature-flag service, key `recommender_model_version`; set to `3.0.4`
- Verification: `curl -s $SERVICE/healthz | jq .model_version` returns `3.0.4` within 60 seconds
- Fallback (if flag service is down): adjust ingress weights via Terraform-applied change; documented procedure at `runbooks/recommender/ingress-rollback.md`

## 5. State reconciliation
- Session cache: keyed by `(user_id, model_version)`. After rollback, v3.0.4 keys are warm; v3.1.0 keys decay over TTL (15 min). No purge needed.
- Downstream writes (recommendation_log): include `model_version` field. Schema is forward-compatible (v3.0.4 reads v3.1.0 rows ignoring new fields). Confirmed via consumer contract.
- In-flight requests: drained over 30s before flip; no half-state across versions.

## 6. Smoke-test gate (re-entry)
Before traffic returns to champion v3.0.4:
- Re-run smoke.json from artifacts/recommender/3.0.4/ against the on-disk artifact
- Verify all 3 cases pass within tolerance
- If smoke fails, escalate immediately — the champion is also broken; rolling back blind makes things worse

## Drill log
- 2026-04-12: rehearsed v3.0.3 → v3.0.2 rollback in staging; total time 4m 12s. Documented at `drills/2026-04-12.md` in the team runbook repo.
```

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| `champion_artifact` | path | yes | — | The previous version's artifact directory (must include manifest.json + smoke.json per `packaging-model-for-deployment`). |
| `challenger_artifact` | path | yes | — | The new version's artifact directory. |
| `triggers` | list of expressions | yes | — | Pre-committed deterministic rules that fire the rollback. Same form as `building-canary-rollout` auto-rollback triggers. |
| `decision_authority` | dict | yes | — | Who can pull the rollback trigger; what approvals are NOT required. Must explicitly state that oncall can rollback unilaterally. |
| `traffic_routing_mechanism` | str | yes | — | Feature flag / ingress weights / lambda alias / DNS / load-balancer config — name the specific control plane. |
| `state_reconciliation` | dict | yes | — | How caches, sessions, and downstream writes survive a version flip. Forward-compatible schema OR explicit purge / migration. |
| `smoke_gate` | path | yes | — | The previous version's smoke.json; re-run on disk before traffic returns. |
| `drill_log` | path | yes | — | Evidence the rollback was rehearsed before the rollout. A plan that has never been rehearsed is not a plan. |

## Workflow

Copy this checklist into the response:

```
Rollback plan progress:
- [ ] 0. Confirm both versions are packaged (manifest + smoke + version pin per packaging-model-for-deployment)
- [ ] 1. Retention policy: ≥ N-2 versions kept; the previous version's artifact must be loadable RIGHT NOW from the artifact store
- [ ] 2. Pre-commit deterministic rollback triggers (same set the canary auto-rollback uses, plus any cohort / business-metric rules)
- [ ] 3. Pre-commit decision authority: oncall can rollback unilaterally; no manager approval required for the auto-trigger or the obvious-emergency case
- [ ] 4. Document the traffic-routing reversal mechanism — name the specific control plane (flag service / ingress / alias)
- [ ] 5. State reconciliation: handle caches, sessions, downstream writes. Forward-compatible schemas preferred; explicit purge / migration when not possible.
- [ ] 6. Smoke-test gate: re-run the previous version's smoke.json against the on-disk artifact BEFORE returning traffic
- [ ] 7. Rehearse the rollback in staging; log time-to-rollback (TTR) and any surprises
- [ ] 8. Publish the runbook at a stable URL all oncalls have bookmarked
- [ ] 9. Post-incident: every actual rollback updates the runbook with the calibration correction
```

### Step 1: Retention policy

The artifact for the previous version must be live in the artifact store, not deleted to "save space." Retain at least N-2 versions for 90 days. If the artifact store is content-addressable (S3 + version IDs, container registry + image digests), the retention is trivial. If versions overwrite by name, fix that first.

### Step 2: Deterministic triggers

Same form as `building-canary-rollout` auto-rollback triggers: crash rate, p99 latency delta, business-metric delta + significance. Manual triggers are the catch-all for everything the auto-rules miss — cohort regressions invisible to the global metric, downstream consumer complaints exceeding a threshold, security incidents in the new code path.

### Step 3: Decision authority

The oncall pulls the trigger. Manager / VP approval is NOT a precondition for rollback. Trying to call up the chain during an active incident is a classic anti-pattern; the runbook must explicitly remove that ambiguity. Postmortems follow rollback, they do not precede it.

### Step 4: Traffic-routing reversal

Name the specific mechanism — `LaunchDarkly key recommender_model_version`, `Kubernetes service mesh weighted route`, `lambda alias`, `Route 53 weighted record`, `Terraform-applied ingress config`. The runbook references the exact command / UI path / kubectl invocation. "Talk to the platform team" is not a mechanism.

### Step 5: State reconciliation

The hard part. Three patterns by difficulty:

- **Stateless / read-only model**: trivial. Flip the version pointer; cache TTLs handle the rest.
- **Forward-compatible schema**: the new version writes a superset of the previous version's output schema. The previous version reads the new rows, ignoring new fields. Cross-reference `ml-datasci/packaging-model-for-deployment` step 5 (output schema discipline).
- **State requires migration**: the new version wrote in a format the previous version cannot read. The runbook must include a documented purge or migration step BEFORE the flip; doing this discovery during an incident is too late. If migration is non-trivial, consider whether the rollout strategy should be blue/green-with-data-replay, not in-place version swap.

### Step 6: Smoke-test gate on re-entry

Before traffic returns to the champion, re-run the champion's `smoke.json` against the on-disk artifact. Verify all cases pass within tolerance. If the smoke fails, the champion is ALSO broken (maybe its dependency lockfile drifted, maybe its artifact was corrupted in storage) — rolling back blind in that state makes the incident worse. Failing-smoke is an escalation, not a green light.

### Step 7: Rehearse

A rollback that has never been rehearsed is a plan in name only. Run a staging drill before the production rollout. Time-to-rollback (TTR) is the headline number; surprise items in the drill log are the value. Re-rehearse after any change to the artifact store, control plane, or downstream schema.

### Step 8: Publish at a stable URL

The runbook lives at a stable internal URL all oncalls know. `runbooks/recommender/rollback.md` in the repo, indexed by your incident-management tool. During an incident, no one has time to grep.

### Step 9: Post-incident update

Every real rollback teaches the plan something. Update the runbook with what surprised you. The drift between "the plan as written" and "what actually happened" is the most underused signal in incident review.

## Outputs

A markdown runbook at `runbooks/<model_name>/rollback.md` containing:

1. **Versioned artifact store** — paths to champion + challenger; retention policy
2. **Triggers** — deterministic auto-trigger expressions + manual-trigger criteria
3. **Decision authority** — who can pull the trigger; what approvals are not required
4. **Traffic-routing reversal** — the specific control plane + exact commands
5. **State reconciliation** — caches, sessions, downstream writes; forward-compatible schema or explicit migration
6. **Smoke-test gate** — re-run the previous version's smoke.json before traffic returns
7. **Drill log** — when the rollback was last rehearsed; TTR; surprises captured
8. **Post-incident update history** — every real rollback's calibration correction

## Failure modes

- **No previous artifact in the store** — caught by step 1 (retention policy); the rollback target must be loadable RIGHT NOW.
- **Approval-chain ambiguity** — "I need to ask my manager before pulling the trigger" delays the rollback while the incident worsens. Caught by step 3 (oncall acts unilaterally).
- **Schema-incompatible state** — the previous version cannot read the new version's outputs. Caught by step 5 (forward-compatible schema OR explicit migration documented BEFORE rollout).
- **Smoke fails on re-entry** — the champion is also broken. Caught by step 6 (smoke gate); failing-smoke is an escalation, not a green light.
- **Plan never rehearsed** — caught by step 7 (drill log required as part of the deliverable).
- **Manual-only rollback in an auto-rollback-eligible system** — caught by step 2 (deterministic auto-triggers required); manual is the second line, not the first.
- **Runbook is in someone's head, not in a repo** — caught by step 8 (stable URL); during an incident, knowledge that is not written down does not exist.

## References

- [Google SRE Workbook — Reliable Product Launches](https://sre.google/workbook/reliable-product-launches/) — rollback as a precondition for launch, not an afterthought
- [Etsy — Code as Craft: Rollback at scale](https://www.etsy.com/codeascraft/) — patterns for traffic-routing reversal and feature flagging
- [Atlassian Incident Management Handbook — Incident response](https://www.atlassian.com/incident-management/incident-response) — decision-authority patterns during active incidents
- `ml-datasci/packaging-model-for-deployment` — required pre-step; rollback needs a versioned artifact + smoke to re-enter
- `ml-datasci/building-canary-rollout` — the rollout-side skill; the canary's auto-rollback trigger executes this skill's runbook
- `workflow/pinning-reproducible-environments` — the lockfile discipline that makes the smoke-test gate on re-entry meaningful

## Examples

### Example 1: Production recommender (happy-path)

Input: "Planning to promote `recommender v3.1` to replace `v3.0`. Build the rollback runbook."

Output: Skill produces the 6-part runbook — artifact store + retention, deterministic triggers (auto + manual), oncall as the decision authority, named control-plane mechanism (e.g. feature flag), state reconciliation (forward-compatible schema, cache TTL handling), smoke-test gate on re-entry, drill log. Requires a staging rehearsal BEFORE the production rollout and publication of the runbook at a stable internal URL.

### Example 2: Stateful model (edge-case)

Input: "Our model writes embedding vectors to a downstream vector database that other services read. The new version uses a different embedding dimension (768 → 1024). Build the rollback plan."

Output: Skill flags that the schema is NOT forward-compatible — the previous version cannot read 1024-dim vectors, and the new version's writes will be wrong-dimension if re-read by v3.0. Requires either (a) blue/green with two parallel vector stores until the rollout completes, (b) a documented purge / re-embedding step as part of the rollback, OR (c) version-tagged rows in the vector store with a query-time filter. Refuses to certify the rollback plan as production-ready until the state-reconciliation step is concrete.

### Example 3: Throwaway experiment (anti-trigger)

Input: "I have an experimental classifier I'm trying on a side dataset to see if it's worth pursuing. Do I need a rollback plan?"

Output: Skill does NOT engage the runbook workflow. Explains that rollback machinery is for production systems with real impact surface; a side experiment with no downstream consumers does not have anything to roll back to. Suggests revisiting if / when the model is being considered for deployment.

## See also

- `ml-datasci/packaging-model-for-deployment` — required pre-step; the rollback plan points at a previous packaged artifact
- `ml-datasci/building-canary-rollout` — the rollout-side skill whose auto-rollback trigger calls into this skill's runbook
- `workflow/pinning-reproducible-environments` — lockfile + Python-version pinning that the re-entry smoke test relies on
- `ml-datasci/evaluating-binary-classifiers` / `ml-datasci/evaluating-regression-models` — the offline metric + 95% CI that informs the business-metric trigger threshold

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored per `docs/superpowers/plans/2026-05-23-rcs-batch-creation-plan.md` (v5-batch-1, skill 5.1.3) via PRAGMATIC discipline
