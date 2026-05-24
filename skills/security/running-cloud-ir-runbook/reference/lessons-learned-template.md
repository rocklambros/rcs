# Lessons-learned template

Produce within 5 business days of containment. Timeline-sourced from preserved logs
(not memory). Each remediation item has an owner, a deadline, and a verification step.

```markdown
# Lessons learned: [incident-id]

- **Incident id:** [internal id]
- **Triggering signal:** [alert name + first-fire time]
- **Detection time:** [ISO-time]
- **Containment time:** [ISO-time]
- **Recovery time:** [ISO-time]
- **Detection-to-containment:** [duration]
- **Authorship:** [primary author + reviewers]
- **Date:** [ISO-date]

## Executive summary

[3–5 sentences: what happened, what was affected, what was done, what we are
fixing. Written so a non-IR reader can understand the magnitude and the response.]

## Timeline

Every entry sourced from preserved logs (CloudTrail / Audit Logs / Activity Logs /
chat / pages). No reconstructed-from-memory entries.

| ISO time | Source | Event |
|---|---|---|
| [time] | [log source] | [factual event] |
| [time] | [chat / page] | [factual event] |

## Root cause

The specific condition that enabled the incident. Examples:

- "An IAM access key was committed to a public Git repository on [date] and was used
  from [source IP] starting [date]."
- "The S3 bucket policy was changed at [date] by [identity] from [source], removing
  the public-access-block."

Avoid "human error" as a root cause — the question is what allowed the human error
to land in production. The deeper cause is what the remediation must address.

## Contributing factors

What made the incident worse than it had to be:

- [Detection latency — how many hours between event and alert?]
- [Containment latency — how many hours between alert and containment?]
- [Log gap — were logs preserved for the full needed window?]
- [Tooling gap — was the IR rotation able to query what they needed?]
- [On-call coverage — was the page acknowledged within target?]

## What worked

Preserve the good moves so they become routine:

- [Detection that fired correctly]
- [Evidence preservation that ran as designed]
- [Comms cadence that landed on time]
- [Cross-team coordination that worked]

## Remediation items

| ID | Item | Owner | Deadline | Verification | Status |
|---|---|---|---|---|---|
| R-1 | [Specific remediation] | [name + role] | [ISO-date] | [How we will know it is done — concrete check] | open |
| R-2 | ... | ... | ... | ... | open |

Each remediation item must be:

- **Specific** — not "improve detection" but "add GuardDuty custom finding for
  cross-region IAM activity > 50 calls/minute"
- **Owned** — a named person, not a team
- **Verifiable** — a concrete check that confirms the item is done
- **Deadlined** — an ISO date, not "next quarter"

## What we are NOT changing

Explicitly list things we considered changing but decided to leave as-is, with
rationale. Stops the next incident's review from re-proposing the same change.

- [Item considered] — [why it stays]
- ...

## Open questions

Items that surfaced during the incident but couldn't be answered:

- [Question 1]
- ...

Each open question gets assigned to someone with a follow-up date.

## Distribution

- IR rotation
- Affected service owner(s)
- Security org leadership
- (If customer-facing) Customer-success leadership
- (If regulated) DPO / counsel
```
