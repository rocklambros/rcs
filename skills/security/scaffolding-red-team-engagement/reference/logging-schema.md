# Logging Schema — AI Red-Team Attack Attempts

Every attack attempt — successful, blocked, partial, inconclusive, or aborted — is logged against this schema. Logs are tamper-evident and append-only.

## Record schema (JSON)

```json
{
  "attempt_id": "uuid-v4",
  "timestamp": "2026-06-01T14:32:08.123Z",
  "operator": "alice",
  "engagement_id": "RT-2026-06-ACME",
  "attack_class": "prompt-injection",
  "attack_subclass": "role-play|authority|encoded|multi-turn|tool-abuse|other",
  "payload_hash": "sha256:...",
  "payload_ref": "s3://red-team-logs/RT-2026-06-ACME/payloads/<attempt_id>.txt",
  "target_endpoint": "https://chatbot.acme.example/v1/chat",
  "target_tool": "account-lookup-v2",
  "response_hash": "sha256:...",
  "response_ref": "s3://red-team-logs/RT-2026-06-ACME/responses/<attempt_id>.json",
  "outcome": "blocked|passed|partial|inconclusive|aborted",
  "severity_hypothesis": "info|low|medium|high|critical",
  "evidence_link": "https://github.com/owner/repo/pull/123#issuecomment-...",
  "notes": "free-form 1–3 sentences"
}
```

## Field semantics

| Field | Required | Notes |
|---|---|---|
| attempt_id | yes | UUID v4; never reused |
| timestamp | yes | UTC, ISO-8601 with milliseconds |
| operator | yes | red-teamer handle; must match a name on the RoE |
| engagement_id | yes | matches RoE Section 1 |
| attack_class | yes | one of: prompt-injection, multi-turn, encoded-payload, tool-abuse, retrieval-poisoning, jailbreak, other |
| attack_subclass | no | free-form subcategory |
| payload_hash | yes | sha256 of the raw input (so payload identity is logged even if payload_ref is purged) |
| payload_ref | yes | URI to the raw payload stored separately |
| target_endpoint | yes | exact URL or tool surface |
| target_tool | no | when the attack invokes a tool, the tool name |
| response_hash | yes | sha256 of the raw response |
| response_ref | yes | URI to the raw response stored separately |
| outcome | yes | blocked / passed / partial / inconclusive / aborted |
| severity_hypothesis | yes | red-teamer's initial severity guess; refined in the final report |
| evidence_link | no | PR / issue / screenshot URI when available |
| notes | no | free-form |

## Storage requirements

- **Append-only:** writes only; deletions blocked
- **Object lock / retention lock:** minimum retention `<<N>>` days (per RoE Section 7)
- **Hash chain or anchoring:** consecutive records hash the previous record's hash, OR the entire log is anchored periodically (e.g., daily) to a tamper-evident external store (sigstore, RFC 3161 timestamp, transparency log)
- **Access:** write access for the red-team operators; read access for Authorizer + lead red-teamer; full audit log of who read what

## Anti-patterns (DO NOT use)

- Slack / Teams / Discord threads as the primary log (not append-only, not tamper-evident)
- Per-operator local files (no central record, not auditable)
- Spreadsheets (mutable cells, edit history typically not preserved)
- Plain-text logs without hash chaining (silent tampering is undetectable)

## Verification on engagement close

At engagement end:

1. Compute the final hash-chain head; record it in the final report
2. Verify the record count matches the operator-side request count (within the engagement window) — gaps indicate missing logs
3. Spot-check 5% of records: dereference `payload_ref` + `response_ref`, recompute the sha256, compare against `payload_hash` / `response_hash`
4. Discrepancies are findings in their own right (the logging system has integrity gaps)
