# Multi-audience onboarding template

Copy-paste-ready skeleton for the most common 3-audience set (engineer + scientist + executive). Adapt by adding / removing audience sections per the archetype list.

```markdown
# <System name>: launch onboarding

## TL;DR (60 seconds, all audiences)

- **What it is:** <one line, no jargon above any audience's ceiling>
- **Primary purpose:** <user job the system performs>
- **Owner:** <team> · <#slack-channel> · <on-call rotation link>
- **Status:** <alpha | beta | GA | sunset>
- **Not for:** <one to three concrete misuses to prevent wrong-cohort onboarding>

---

## For engineers (integration)

**Why you care:** <opener: name what you will do with it, the constraint, and the action to take>

### Endpoints & auth
- `POST /v1/<endpoint>` — <one-line purpose>
- Auth: <OAuth / API key / mTLS>, scope: <scope-name>

### Error model
| Code | Meaning | Retry policy |
|---|---|---|
| 200 | OK | — |
| 429 | Rate limited | Exponential backoff with jitter, max 5 retries |
| 5xx | Server error | Idempotent: retry. Non-idempotent: do not retry. |

### Performance envelope
- p50 / p95 / p99 latency: <ms / ms / ms>
- Throughput cap: <req/s per team>
- Rate limit: <req/min per team>

### Runbook
- Runbook: <link>
- On-call rotation: <link>
- Versioning policy: <link>; current API version: v1; deprecation horizon: 12 months

---

## For scientists (validation)

**Why you care:** <opener: name the metric, the baseline, and the regression page>

### Evaluation methodology
- Eval set: <name>, <size>, last refreshed <date>
- Headline metric: <metric>@<k> = <value> (baseline: <value>)
- Regression threshold: <value> (page the owner if breached)

### Drift signals being monitored
- <signal 1>: <metric + window + threshold>
- <signal 2>: <metric + window + threshold>

### How to file a quality regression
- Issue template: <link>
- Triage SLA: <hours>
- Owner: <team>

### Known limitations
- <segment / scenario where quality is weak, with the metric value>

---

## For executives (decision)

**Why you care:** <opener: business outcome, cost, single largest risk, exit criterion>

### Cost
- Infra: $<value>/year
- FTE: <value> (build) + <value> (run)
- License / vendor: $<value>/year

### Risk surface
- **Single largest risk:** <name + mitigation owner>
- Secondary risks: <2-3 bullets>
- Dependency map: <vendor / team / system>

### Exit criteria
- <measurable condition that would trigger sunset>

---

## Glossary

| Term | Definition (in the voice of the audience most likely to look it up) |
|---|---|
| <Retrieval@k> | <scientist voice: recall computed over top-k retrieved items against a held-out judgment set> |
| <Rate limit> | <engineer voice: per-team token budget; over-limit returns 429; use exponential backoff> |
| <Total cost of ownership> | <executive voice: infra spend + FTE-equivalent labor + vendor license, summed annually> |
| <DSR> | <compliance voice: data subject request; deletion within 30 days; logged in audit trail> |

---

## Out of scope (what this system is NOT)

- Not for <use case 1>
- Not for <use case 2>
- Not a substitute for <human process>

---

## Feedback channel

- <#slack-channel> — onboarding feedback, all audiences
- Owner: <name>, triages weekly
- Bug reports: <link to issue tracker>
```

## Adaptations

**For 2 audiences:** delete the unused audience section + glossary entries unique to that audience.

**For 4-5 audiences:** add audience sections from `audience-archetypes.md`; keep TL;DR ≤ 200 words even with more sections.

**For ≥ 6 audiences:** split into a launch doc (everyone reads TL;DR + their section) + per-audience deep-dives linked from each section.

**For dataset / model artifacts (not service):** drop "Endpoints & auth" subsection; replace with "Schema + provenance" for scientists, "Access path + license" for engineers.
