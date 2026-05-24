---
name: running-cloud-ir-runbook
description: >
  Walks a cloud-incident-response runbook against an active or recent incident on
  AWS, GCP, or Azure — triage, evidence preservation, containment, comms,
  eradication, recovery, and lessons-learned. Provider-specific commands (AWS CLI,
  gcloud, az) for evidence capture, IAM blast-radius assessment, and snapshot
  preservation. Use when an alert fires (GuardDuty / Security Command Center /
  Defender), when an IAM credential leak is suspected, when an unusual cross-account
  access pattern surfaces, or when post-incident review is needed. Refuses to engage
  on on-prem laptop infections (no cloud blast radius), pre-incident hypotheticals
  without a triggering signal, or unauthorized response on infrastructure the
  operator does not own.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - ir-responder
  - devops
  - cloud-eng
evidence:
  - mac-harness-foundation-threat-model
  - claude-secure-coding-rules
  - rcs-batch-creation-plan
last-updated: 2026-05-23
---

# Running a Cloud Incident-Response Runbook

> **Tooling, not professional advice.** This skill walks a runbook; it does NOT
> replace your organization's IR plan, counsel's involvement when regulated data is
> exposed, or the cloud provider's incident-support escalation path.

## When to use

Trigger this skill when an active or recent cloud-side incident needs a structured response and one of:

- A cloud security alert fired: AWS GuardDuty, GCP Security Command Center, Azure Defender for Cloud, or a custom detection
- An IAM credential leak is suspected (key found in a public repo, leaked in logs, exposed in a third-party breach)
- An unusual cross-account / cross-project / cross-subscription access pattern surfaces
- Public storage misconfiguration is reported (S3 / GCS / Azure Blob public-read on sensitive data)
- A pen-test or bug-bounty finding turned into an active-exploit confirmation in prod
- Post-incident review is needed to produce a defensible lessons-learned document

Keyword triggers: "GuardDuty fired", "we think our AWS keys leaked", "someone accessed our prod account from an unknown IP", "S3 bucket was public", "IR runbook for AWS", "what do we do first".

## When NOT to use

Skip this skill and hand off when:

- The incident is an on-prem laptop / endpoint infection with no cloud blast radius — use a host-IR runbook (out of scope here)
- The user is asking hypothetically with no triggering signal — use `threat-modeling-llm-app` or a pre-incident tabletop instead
- The user wants response against infrastructure they do not own (a partner's account, an upstream SaaS, a third-party tenant) — the cloud provider's abuse / coordinated-disclosure path applies, not an internal IR runbook
- The user is in the middle of an authorized pen-test and the "incident" is the engagement's own activity — use `scaffolding-ctf-engagement` and confirm the activity matches the RoE before escalating

## Quick start

User says: "GuardDuty just fired `UnauthorizedAccess:IAMUser/MaliciousIPCaller.Custom` against `IAMUser/build-bot-prod` from `198.51.100.42`. Our IR rotation is on. Walk us through."

Skill produces in a single response:

1. **Triage** — confirm the alert is not a false positive (known build IP? recent role change?)
2. **Evidence preservation** — snapshot CloudTrail / Audit Logs to a separate account before anything is changed
3. **Containment** — revoke / rotate / quarantine the affected identity and any sessions it minted
4. **Blast-radius assessment** — what could this identity have touched? Which resources were accessed in the alert window?
5. **Comms** — who gets notified, by when, through which channel
6. **Eradication** — remove attacker access paths (long-lived keys, lingering sessions, backdoor IAM policies, cron-installed credentials)
7. **Recovery** — restore from clean state, validate, monitor for re-entry
8. **Lessons-learned** — timeline, root cause, contributing factors, remediation items with owners

Each step lists the specific provider commands or console paths.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| cloud_provider | "aws" \| "gcp" \| "azure" \| "multi" | yes | — | Drives the evidence-capture and containment commands. |
| triggering_signal | string | yes | — | What fired the runbook (alert name, observed behavior, finding id). |
| affected_identity | string | yes | — | IAM user / service account / managed identity / role suspected of compromise. |
| alert_window | ISO datetime range | yes | — | Start and end of the observed-malicious-activity window. |
| account_id | string | yes | — | AWS account id / GCP project id / Azure subscription id. |
| has_regulated_data | bool | no | false | Whether the touched scope contains PII / PHI / PCI; gates additional notification requirements. |
| evidence_destination | string | no | "ir-evidence-account" | The separate account / project / subscription where evidence is preserved. |
| communication_tier | "internal" \| "customer" \| "regulator" | no | "internal" | Drives the comms-template tree. |

## Workflow

```
Cloud IR runbook checklist:
- [ ] Step 1: Triage — confirm true positive vs known-good activity
- [ ] Step 2: Preserve evidence — capture logs to a separate account BEFORE containment
- [ ] Step 3: Contain — revoke credentials, kill sessions, quarantine resources
- [ ] Step 4: Assess blast radius — enumerate what the identity could and did touch
- [ ] Step 5: Communicate — notify per the comms tree
- [ ] Step 6: Eradicate — remove every attacker access path, not just the one observed
- [ ] Step 7: Recover — restore clean state, validate, monitor
- [ ] Step 8: Lessons-learned — timeline + root cause + remediation owners
```

### Step 1: Triage

Before responding, confirm the alert is not a false positive:

- Is the source IP a known-good (corporate egress, CI/CD provider, the build-bot's documented IP range)?
- Was the activity authorized by a recent change (a new region, a new role assumption, a scheduled task)?
- Is the affected identity in a recent rotation window where activity from new IPs is expected?

If yes to any, document and close. If no, proceed to Step 2.

A 5-minute triage saves hours of unnecessary containment. A skipped triage that turns out to be a false positive wastes the on-call's credibility for the next real alert.

### Step 2: Preserve evidence

BEFORE you change anything in the account, snapshot the logs to a separate
evidence-destination account. Containment overwrites context; evidence preserves
it. See `reference/aws-ir-commands.md` for the exact AWS CLI sequence; equivalent
patterns for GCP and Azure are in `reference/gcp-azure-ir-commands.md`.

Minimum evidence set:

- CloudTrail / Audit Logs / Activity Logs for the alert window ± 4h on each side
- VPC Flow Logs / VPC Flow / NSG Flow Logs for the alert window
- Resource-state snapshots: IAM policies attached to the identity, any roles it could assume, recent CreateAccessKey / CreateServiceAccountKey events
- Storage-access logs: S3 server-access / GCS data-access / Azure Storage diagnostics for any bucket the identity could touch
- Application logs from any service the identity called

Store in append-only / write-once storage in the evidence-destination account with
the IR rotation's role as the only writer. Hash each artifact and record the hashes.

### Step 3: Contain

Specific provider commands (full list in `reference/aws-ir-commands.md` and `reference/gcp-azure-ir-commands.md`):

**AWS:**
- Disable access keys: `aws iam update-access-key --status Inactive --access-key-id <key-id> --user-name <user>`
- Attach explicit deny policy: `aws iam put-user-policy --user-name <user> --policy-name IR-DENY-ALL --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*"}]}'`
- Revoke active sessions for assumed roles: `aws iam put-role-policy --role-name <role> --policy-name IR-REVOKE-SESSIONS --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*","Condition":{"DateLessThan":{"aws:TokenIssueTime":"<now>"}}}]}'`

**GCP:**
- Disable service account: `gcloud iam service-accounts disable <sa-email>`
- Delete leaked key: `gcloud iam service-accounts keys delete <key-id> --iam-account=<sa-email>`
- Revoke OAuth2 grants for human accounts via the admin console

**Azure:**
- Disable identity: `az ad user update --id <user-or-app> --account-enabled false`
- Reset credentials: `az ad app credential reset --id <app-id>`

Do NOT delete the identity yet — that destroys forensic context. Disable first, delete after lessons-learned.

### Step 4: Blast-radius assessment

Two questions:

1. **What could this identity have done?** Enumerate the union of every permission the identity has — direct policies + group/role-attached policies + assumable roles transitively. Tools: `aws iam simulate-principal-policy`, `policy-sentry`, GCP `policy analyzer`, Azure Resource Graph queries.
2. **What did it actually do?** Query the captured CloudTrail / Audit Logs / Activity Logs for every event keyed to the identity in the alert window. Bucket events by resource and action. Flag any data-read or data-export events.

Output: a `blast-radius.md` document under the evidence destination listing both the could-touch set and the did-touch set, with explicit identification of any data-class boundaries crossed.

### Step 5: Communicate

Notify per the comms tree:

- **Internal:** the IR rotation lead, the affected service's on-call, the security org, the relevant engineering manager
- **Customer:** if customer data is in the blast radius, the customer-success team coordinates external notification per the contract / DPA
- **Regulator:** if `has_regulated_data: true` AND the blast radius crossed regulated-data boundaries, the data-protection officer / counsel initiates the regulator notification (GDPR 72h, HIPAA breach-notification, sector-specific)

Use `reference/comms-templates.md` for the message structure: factual, no speculation, what is known + what is being investigated + next-update time.

### Step 6: Eradicate

Containment stopped the observed attacker. Eradication removes every path the
attacker could re-enter through. Look for:

- Other access keys / service-account keys the identity created during the window
- IAM roles / policies the identity attached or modified
- Lambda / Cloud Function / Function App triggers added during the window
- IAM principal additions to S3 / GCS / Azure Storage bucket policies
- Cross-account roles trusted to the attacker-controlled account
- Cron jobs / scheduled tasks / EventBridge rules the identity created
- Long-lived credentials embedded in resources the identity could modify (Lambda env vars, ECS task defs, Kubernetes secrets)

Each candidate gets verified and either reverted or quarantined for evidence.

### Step 7: Recover

- Restore affected resources from a known-clean state (snapshot pre-incident, or rebuilt from infrastructure-as-code)
- Rotate any secrets the identity could have read (database passwords, third-party API keys, signing keys)
- Re-enable the identity ONLY after the IR lead and the affected-service owner both sign off
- Monitor for re-entry: targeted detections on the previously-observed TTPs for at least 30 days

### Step 8: Lessons-learned

Within 5 business days of containment, produce a lessons-learned document:

- **Timeline** — every event keyed to a timestamp, sourced from preserved logs
- **Root cause** — what enabled the incident (leaked credential? overly broad IAM? missing detection?)
- **Contributing factors** — what made it worse (delayed alert? missing log retention? on-call gap?)
- **What worked** — preserve the good moves so they become routine
- **Remediation items** — each with an owner, a deadline, and a verification step

See `reference/lessons-learned-template.md` for the structure.

## Outputs

A single response containing the worked runbook for the specific incident:

1. Triage decision (true positive / false positive) with evidence
2. Evidence-capture commands executed + storage path + hashes
3. Containment commands executed + verification
4. Blast-radius document (could-touch + did-touch)
5. Comms messages drafted (internal + customer + regulator as applicable)
6. Eradication checklist with each access path verified
7. Recovery sign-off list
8. Lessons-learned document

## Failure modes

- **Containment before evidence** — overwrites the forensic context. Caught by: Step 2 explicitly precedes Step 3.
- **Disable the identity by deletion** — destroys IAM history. Caught by: Step 3 uses disable, not delete; delete moves to post-lessons-learned cleanup.
- **Treating the alert source IP as the only TTP** — attacker pivots through other identities. Caught by: Step 6 enumerates every access path the identity could have created.
- **Skipping the simulate-policy step** — misses transitive role-assumption blast radius. Caught by: Step 4 requires the full could-touch set, not just the did-touch set.
- **Comms speculation** — premature attribution ("APT-X"), customer-blame ("the partner integration was compromised"). Caught by: Step 5 comms templates are factual-only with explicit "what is known / what is being investigated" structure.
- **Lessons-learned without owners** — items die in a doc no one reads. Caught by: Step 8 requires each remediation item have an owner, deadline, and verification.
- **Re-enabling the identity without sign-off** — re-introduces the access path. Caught by: Step 7 explicit dual sign-off gate.
- **Mistaking authorized pen-test activity for an incident** — burns the IR rotation and the engagement. Caught by: Step 1 triage cross-references active RoE windows.

## References

- `reference/aws-ir-commands.md` — AWS CLI command set for evidence capture and containment
- `reference/gcp-azure-ir-commands.md` — gcloud and az equivalents
- `reference/comms-templates.md` — internal / customer / regulator message structures
- `reference/lessons-learned-template.md` — timeline + root cause + remediation document structure
- [AWS IR Guide](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html) — AWS-side IR reference
- [NIST SP 800-61r2](https://csrc.nist.gov/pubs/sp/800/61/r2/final) — Computer Security Incident Handling Guide

## Examples

### Example 1: GuardDuty alert on a leaked build-bot key

Input: `cloud_provider="aws"`, `triggering_signal="GuardDuty UnauthorizedAccess:IAMUser/MaliciousIPCaller.Custom"`, `affected_identity="IAMUser/build-bot-prod"`, `alert_window="2026-05-23T14:00Z to 2026-05-23T16:30Z"`, `account_id="123456789012"`, `has_regulated_data=false`.

Output: Triage confirms 198.51.100.42 is not a known-good build IP. Evidence captured: CloudTrail for ± 4h, VPC Flow Logs, IAM policy snapshot, S3 server-access logs for buckets the identity could touch, hashed to evidence account `999999999999`. Containment: access keys disabled, IR-DENY-ALL policy attached, role-assume sessions revoked. Blast radius: identity could read 12 S3 buckets (none regulated); did touch `s3:ListBuckets` and 47 `s3:GetObject` calls against `prod-build-artifacts`. Comms: internal-only (no regulated data). Eradication: no additional keys created, one IAM policy edit reverted, no Lambda triggers added. Recovery: build-bot identity rebuilt from Terraform, new key minted scoped to a single bucket, 30-day TTP monitoring enabled. Lessons-learned drafted with the team's CI/CD owner as the credential-rotation-policy item owner.

### Example 2: Public-S3 misconfiguration with PII

Input: `cloud_provider="aws"`, `triggering_signal="customer report: bucket reachable unauthenticated"`, `affected_identity="role/data-pipeline-prod"`, `alert_window="2026-05-20T00:00Z to 2026-05-23T15:00Z"`, `account_id="111122223333"`, `has_regulated_data=true`.

Output: Triage confirms the bucket was public for ~72 hours. Evidence: CloudTrail + S3 server-access logs preserved. Containment: bucket policy reset to deny-public, bucket-level block-public-access enabled. Blast radius: bucket contained 240k customer records (PII class); S3 server-access logs show 18 unique source IPs downloaded objects during the window — 4 of those IPs match known scanner ranges. Comms: internal IR rotation, customer-success notified, DPO engaged for GDPR 72h-clock assessment, counsel engaged. Eradication: IAM policy that allowed the misconfiguration was a Terraform drift — Terraform reverted and pre-merge guard added. Recovery: customer notification drafted per DPA, regulator notification drafted by counsel + DPO. Lessons-learned with named owners for the Terraform-guard remediation, the bucket-policy-CI-check remediation, and the public-access-detection-latency remediation.

### Example 3: Authorized pen-test mistaken for incident (anti-trigger)

Input: "GuardDuty fired on `IAMUser/red-team-tester-01` accessing prod-api from an unknown IP, but we are mid-engagement with the external pen-test firm under SOW ACME-2026-06. Walk us through IR."

Output: Skill does NOT proceed with full containment. Step 1 (triage) catches the active-RoE window: the alert source IP matches the pen-test firm's documented IP range named in the SOW. Skill confirms with the IR lead + pen-test point-of-contact that the activity is within the RoE scope and the time window. Outcome: log the alert as a documented false-positive for the engagement, no containment, no comms cascade. Recommend tightening the GuardDuty detection scope OR pre-staging an exception list for the engagement window so the on-call is not paged repeatedly.

## See also

- `security/scaffolding-ctf-engagement` — for confirming whether the "incident" is actually an authorized engagement
- `security/scaffolding-red-team-engagement` — AI-system engagement variant
- `security/writing-pentest-finding` — when the incident root-causes back to an unpatched pen-test finding
- `security/auditing-mcp-server-pre-trust` — when the incident touches a third-party MCP server's credentials
- `security/triaging-vulnerability-findings` — for prioritizing post-incident scanner output

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 for v6.0-batch-2 per PRAGMATIC discipline.
