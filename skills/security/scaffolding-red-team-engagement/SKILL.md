---
name: scaffolding-red-team-engagement
description: >
  Scaffolds an AI red-team engagement before any attack runs — produces Rules of Engagement
  (RoE), in-scope / out-of-scope inventory, kill-switch protocol, and a tamper-evident
  logging template. Use when the user is about to red-team a deployed LLM application,
  agentic system, or AI feature for a third-party client, an internal team, a paid
  engagement, a bug bounty submission, or a regulatory exercise. Refuses to engage for
  solo jailbreak experiments on a personal account where no scope, authorization, or
  blast-radius constraints are needed.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - ai-security
  - red-team
  - grc
evidence:
  - claude-secure-coding-rules
  - mac-harness-foundation-threat-model
  - jetson-runbook
last-updated: 2026-05-23
---

# Scaffolding an AI Red-Team Engagement

> **Tooling, not professional advice.** This skill produces engagement scaffolding;
> it does NOT replace contractual review by counsel, an authorized signer's RoE
> approval, or the target operator's incident-response coordination.

## When to use

Trigger this skill when the user is about to start an AI red-team engagement and one of:

- A paid engagement against a third-party client (consulting, pen-test deliverable)
- An internal red-team rotation against a company-owned LLM app or agent
- A bug-bounty submission that involves prompt-injection, jailbreaking, or AI tool abuse
- A regulatory or compliance exercise (e.g., FedRAMP, ISO/IEC 42001, EU AI Act conformity testing)
- Pre-deployment authorization testing where the operator wants documented coverage

Keyword triggers: "red-team this LLM", "we're pen-testing an AI feature", "engagement scoping",
"AI bug bounty submission", "kill switch for our jailbreak eval", "RoE for prompt-injection
testing", "what should we log during this red-team".

## When NOT to use

Skip this skill and hand off when:

- The user is doing solo personal jailbreak experiments on their own account with no third-party blast radius — no scope or RoE is needed; refer to a one-off journal entry instead
- The actual attack execution is the request, not the scoping — use `running-prompt-injection-eval`, `running-multiturn-attack-suite`, or `running-encoded-payload-suite`
- The user is responding to an active incident on a production system — that is IR, not pre-engagement scoping; hand off to `running-cloud-IR-runbook` (planned)
- The system under test is a base model with no safety stack — there is nothing to red-team beyond the model itself, and any finding is a property of the base model (out of scope for an app-layer engagement)

## Quick start

User says: "We're red-teaming our customer-support chatbot before launch. The chatbot
uses retrieval over our help-docs corpus and exposes a few internal tools (account-lookup,
refund-issue). Three of us start Monday. Give us the scaffolding."

Skill produces six artifacts in a single response:

1. **Rules of Engagement (RoE)** — signed-off authorization, time window, contact list
2. **Scope inventory** — in-scope endpoints, models, tools, data classes
3. **Out-of-scope list** — explicit no-go targets (prod customer data, payment rails, third-party APIs the user does not own)
4. **Kill-switch protocol** — abort triggers, who can halt, how to halt, what to preserve
5. **Logging template** — tamper-evident log schema for every attack attempt
6. **Reporting + safe-harbor language** — disclosure pattern + coordinated-disclosure timeline

Each artifact is filled with the engagement-specific values the user provided.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| engagement_type | "paid" \| "internal" \| "bug-bounty" \| "regulatory" | yes | — | Drives the RoE and authorization template choice. |
| target_system_summary | freeform string | yes | — | 1–3 sentence description: model(s), retrieval, tools, user interface. |
| owner_authorizer | name + role | yes | — | The accountable person signing the RoE. Must be an executive or named-delegate. |
| time_window | ISO-date range | yes | — | Start and end of the testing window; outside this window all activity is unauthorized. |
| team_size | int | no | 1 | Number of red-teamers; affects log-channel design and conflict-detection. |
| has_prod_data | bool | no | false | Whether the target accesses real customer data; gates additional PII-safeguard scaffolding. |
| coordinated_disclosure_days | int | no | 90 | Embargo window for the public-disclosure clause. |

## Workflow

Walk these steps in order. Do not skip the authorizer-signature step — an unsigned RoE turns the engagement into unauthorized access.

```
Engagement scaffolding checklist:
- [ ] Step 1: Identify the authorizer and confirm signing authority
- [ ] Step 2: Define scope (in-scope endpoints, models, tools, data classes)
- [ ] Step 3: Define out-of-scope (explicit no-go list)
- [ ] Step 4: Establish kill-switch (who, how, what gets preserved)
- [ ] Step 5: Set up tamper-evident logging (schema + storage)
- [ ] Step 6: Document reporting + disclosure
- [ ] Step 7: Circulate RoE for sign-off BEFORE any test traffic flows
```

### Step 1: Authorizer identity and signing authority

Name the accountable executive or delegate. Confirm they have authority to authorize testing against the target system. For a third-party client, the authorizer must be on the customer side, not the testing vendor.

### Step 2: In-scope inventory

List every endpoint, model, tool, and data class the team is authorized to touch. Tools listed by exact name (e.g., `account-lookup-v2`), not category. Models listed by exact deployment id (e.g., `claude-sonnet-4-6` via your gateway `/chat` endpoint at `https://chatbot.example.com/v1`), not vendor.

### Step 3: Out-of-scope exclusions

Explicit blocked targets. Always include: prod customer data, payment processing endpoints, third-party APIs the operator does not own, denial-of-service attack patterns (cost-amplification, request-flooding), and any system not enumerated in scope.

For the "has_prod_data: true" case, the out-of-scope list MUST exclude real PII exfiltration as a success criterion — synthetic / canary records only.

### Step 4: Kill-switch protocol

Specify:
- **Abort triggers** — observed real-user impact, data exposure beyond canaries, unexpected cost spike, target-side rate limit at saturation
- **Halt authority** — at minimum the authorizer and the lead red-teamer; designate a backup
- **Halt mechanism** — explicit (revoke API keys, disable test account, network ACL); estimated TTI (time-to-isolate) ≤ 10 minutes
- **Preservation** — on halt, logs MUST be preserved untouched for post-mortem

### Step 5: Tamper-evident logging

Every attack attempt logs a structured record. Recommended schema:

```json
{
  "attempt_id": "uuid",
  "timestamp": "ISO-8601 with timezone",
  "operator": "red-teamer-handle",
  "engagement_id": "from RoE",
  "attack_class": "prompt-injection|multi-turn|encoded-payload|tool-abuse|...",
  "payload_hash": "sha256 of the input",
  "payload_ref": "path or storage URI; raw payload stored separately",
  "target_endpoint": "URL or tool name",
  "response_hash": "sha256 of response",
  "response_ref": "path or URI",
  "outcome": "blocked|passed|partial|inconclusive|aborted",
  "evidence_link": "PR / ticket / screenshot URI",
  "notes": "freeform"
}
```

Store logs append-only (object-storage with versioning + retention lock, or a write-once-read-many store). Hash chain consecutive records or anchor periodically to make tampering detectable.

### Step 6: Reporting + coordinated disclosure

Template the final-report sections (executive summary, findings, severity, repro, remediation, retest plan). Include safe-harbor language for the engagement window. Embargo public disclosure for `coordinated_disclosure_days` (default 90) after the report's delivery date, unless the operator publishes earlier.

### Step 7: Pre-flight gate

NO test traffic before the RoE is signed. The artifact pack from steps 1–6 is circulated to the authorizer, returned signed, and stored alongside the engagement logs. Skill output explicitly includes this halt point.

## Outputs

A single response containing:

1. **RoE document** (Markdown) ready for the authorizer to sign
2. **In-scope table** and **Out-of-scope list**
3. **Kill-switch runbook** (triggers / authority / mechanism / preservation)
4. **Logging schema** (JSON Schema or example payloads) + recommended storage
5. **Reporting + disclosure template** (final-report sections + safe-harbor + embargo)
6. **Pre-flight gate reminder** — explicit "do not run attack traffic before RoE is signed" sentence

## Failure modes

- **Verbal authorization, no signed RoE** — a "go ahead" Slack message is not a signed RoE. Caught by: Step 7 explicit gate; skill response includes the unsigned-RoE warning.
- **Scope creep mid-engagement** — testers add endpoints "since they're related". Caught by: in-scope table is a closed list; any addition requires a re-signed RoE addendum.
- **Logging in shared chat channels** — Slack/Teams threads are not tamper-evident. Caught by: Step 5 names append-only + hash-chained + retention-locked storage.
- **PII canary substitution** — testers use real customer ids "to keep it realistic". Caught by: when `has_prod_data: true`, the out-of-scope list explicitly prohibits real PII exfiltration as success criterion.
- **DoS as a finding** — submitting cost-amplification or request-flooding as a "finding". Caught by: out-of-scope list excludes DoS patterns by default.
- **Same testers + same operator over time without RoE refresh** — long-running internal red-team without periodic RoE renewal. Caught by: RoE includes `time_window`; expiry triggers a re-sign.

## References

- `reference/roe-template.md` — full Rules-of-Engagement document template
- `reference/kill-switch-runbook.md` — kill-switch triggers, halt authority matrix, preservation steps
- `reference/logging-schema.md` — JSON Schema for the attempt log, with field semantics
- [OWASP LLM Top 10](https://genai.owasp.org/llm-top-10/) — threat catalog the engagement may cover (BYO; this skill does not ship a catalog)
- [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final) — pen-test methodology baseline that informs RoE structure

## Examples

### Example 1: Paid engagement against a customer-support chatbot

Input: `engagement_type="paid"`, `target_system_summary="Customer-support chatbot using Sonnet 4.6 + RAG over a 12K-doc help corpus; exposes account-lookup and refund-issue tools."`, `owner_authorizer="VP Eng, ACME Corp"`, `time_window="2026-06-01 to 2026-06-21"`, `team_size=3`, `has_prod_data=true`.

Output: RoE addressed to the VP Eng with explicit scope (the chatbot's `/chat` endpoint + the two tools), out-of-scope (production customer PII exfiltration as a success criterion, third-party Stripe webhook, DoS patterns), kill-switch (the VP and the lead red-teamer, mechanism = revoke red-team API keys + flag the test account; TTI ≤ 10 min), logging schema with sha256-hashed payloads stored to append-only S3 with object lock + 90-day retention, final-report template, and the pre-flight gate sentence.

### Example 2: Solo personal jailbreak (anti-trigger)

Input: "I want to jailbreak ChatGPT on my personal account for fun. Scaffold the engagement."

Output: Skill declines to engage. Explanation: solo experiments on your own consumer account against a third-party provider do not constitute a red-team engagement requiring RoE; you have no authorization to formalize and no kill-switch authority to delegate. Recommends keeping a personal research notebook instead, and links to the provider's published acceptable-use policy as the binding constraint.

## See also

- `security/running-prompt-injection-eval` — single-turn injection harness once RoE is signed
- `security/running-multiturn-attack-suite` — multi-turn / state-poisoning harness
- `security/running-encoded-payload-suite` — encoding-bypass harness
- `security/auditing-mcp-server-pre-trust` — applies when the engagement touches MCP servers
- `security/writing-pentest-finding` (planned) — finding-write-up format for the final report
- `security/writing-vdp-and-coordinated-disclosure` (planned) — for the disclosure-policy side

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored 2026-05-23 for v4.0-batch-4 per PRAGMATIC discipline.
