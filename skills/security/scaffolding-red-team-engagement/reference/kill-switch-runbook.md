# Kill-Switch Runbook — AI Red-Team

A kill-switch protocol is mandatory before any test traffic flows.

## Abort triggers

Trigger HALT if any of the following is observed:

| Trigger | How detected | Action |
|---|---|---|
| Real-user impact (errors, exposure) | Operator monitoring / pages on-call | HALT immediately |
| Data exposure beyond canaries | Log inspection / DLP alert | HALT + preserve logs + notify Authorizer |
| Cost spike > $X/hour above baseline | Cloud billing alert | HALT + screenshot billing console |
| Target-side rate limit at saturation | Repeated 429 responses for > 5 minutes | HALT + back off |
| Law-enforcement contact or subpoena | Direct contact to either party | HALT + escalate to counsel |
| Authorizer requests halt | Any channel | HALT + acknowledge in writing |
| Lead red-teamer requests halt | Any channel | HALT + acknowledge |

## Halt-authority matrix

Any ONE of the following can unilaterally trigger HALT. None can unilaterally resume.

| Person | Halt | Resume |
|---|---|---|
| Authorizer | yes | yes (with red-team lead concurrence) |
| Lead red-teamer | yes | yes (with Authorizer concurrence) |
| Named backup (per RoE Section 6) | yes | no |

Resume requires both Authorizer and Lead red-teamer in writing, plus a documented root-cause of the trigger.

## Halt mechanism — minimum components

1. **Identity revocation:** rotate / disable red-team API keys, test-account credentials, OAuth tokens
2. **Network ACL block:** block red-team egress IPs at the operator firewall / WAF
3. **Notification:** automated page to all halt-authorities; manual confirmation each acknowledges
4. **Time-to-isolate target:** ≤ 10 minutes from trigger detection to traffic stopped

Pre-stage the revocation scripts and ACL rules; do not improvise them during a live halt.

## Preservation requirements

On HALT, the following must be preserved untouched until the Authorizer authorizes review:

- All attack-attempt logs (schema in `reference/logging-schema.md`)
- All raw payloads and responses
- All operator-side observability captures (traces, dashboards screenshotted)
- Billing console screenshots if a cost trigger fired

Storage: the engagement's tamper-evident log store (append-only with object lock + retention).

## Post-halt sequence

1. **Acknowledge** — every halt-authority confirms receipt in the engagement channel
2. **Document** — write a one-page memo: trigger, timestamps, observed impact, raw evidence references
3. **Notify operator-side incident response** if there is any chance of real-user impact
4. **Review with Authorizer** — within 24 hours of halt
5. **Decision:** terminate engagement, scope-down + resume with addendum, or fix trigger source + resume

Resume without a documented decision is not permitted.
