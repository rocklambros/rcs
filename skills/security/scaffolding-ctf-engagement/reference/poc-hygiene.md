# PoC hygiene rules

Rules every tester on the engagement follows when producing proof-of-concept artifacts.
Violations expose the testing party to legal risk and the customer to data-loss events.

## Canary-only data access

When a finding requires touching data to prove impact:

- Use seeded canary records the customer pre-plants (e.g., `canary_user_acme_001`).
- If canary records are not available, stop and request them — do NOT use real records.
- Never paginate, dump, or enumerate real records. One canary read = sufficient proof.

## No pivoting beyond scope

- If an in-scope host yields credentials to an out-of-scope host, STOP.
- Document the credential-leak finding against the in-scope host. Do NOT use the leaked credentials against the out-of-scope host.
- If the scope must expand, request an RoE addendum signed by the authorizer; resume only after the addendum is signed.

## No persistence

- Do not install backdoors, scheduled tasks, services, or dropped binaries.
- Acceptable proof artifacts: a short-lived file (`/tmp/acme-2026-06-poc-<finding-id>.txt`), a beacon to the testing party's listener (in a non-prod canary network namespace where possible), an entry in an isolated test table.
- Remove every artifact before the engagement window closes. Document removal in the engagement log.

## Tamper-evident attack log

Every attempted exploit logs a structured record:

```json
{
  "attempt_id": "uuid",
  "timestamp": "ISO-8601 with timezone",
  "engagement_id": "[engagement id]",
  "tester": "handle",
  "finding_id": "if linked",
  "target_url": "exact URL or host:port",
  "method": "HTTP method or network protocol",
  "payload_hash": "sha256 of the payload",
  "payload_ref": "object-storage URI",
  "response_hash": "sha256 of response",
  "response_ref": "object-storage URI",
  "outcome": "exploited | blocked | partial | inconclusive | aborted",
  "evidence_link": "PR / ticket / screenshot URI",
  "notes": "freeform"
}
```

Store logs append-only (object storage with versioning + retention lock, or WORM
store). Hash-chain consecutive records or anchor periodically so tampering is detectable.

## Findings chains

If a low-severity finding chains with others to higher impact:

- Report each finding individually with its own severity AND a `findings_chain` link.
- Report a chained-impact finding whose severity reflects the combined path.
- Cross-reference both ways: the chain finding lists the link findings; each link
  finding lists the chain.

## Communication discipline

- Findings drop only via the channel named in the RoE (§9).
- Do NOT post findings, screenshots, or payloads to public chat / DMs / personal
  cloud storage. The findings drop is the legal record.
- Halt requests from the customer authorizer take immediate effect; do not finish
  "just one more attempt".

## Closeout checklist

Before the engagement window closes, every tester confirms:

- [ ] All canary records used are accounted for (no real records touched)
- [ ] All proof artifacts removed from customer systems
- [ ] All attack-log entries pushed to append-only storage
- [ ] All findings filed in the RoE-named drop
- [ ] Retest window scheduled with the customer
