# Log Schema — Prompt-Injection Eval Attempts

Each dispatched attempt produces a structured log record. Append-only, tamper-evident, hash-chained or anchored per the engagement's RoE.

## Record fields

```json
{
  "attempt_id": "uuid-v4",
  "engagement_id": "RT-2026-06-ACME",
  "timestamp": "2026-06-01T14:32:08.123Z",
  "operator": "alice",
  "payload_id": "from corpus",
  "payload_hash": "sha256 of the raw payload",
  "payload_ref": "URI to raw payload in payload store",
  "taxonomy_class": "OWASP-LLM01",
  "taxonomy_subclass": "DAN-variant",
  "target_endpoint": "https://chatbot.acme.example/v1/chat",
  "target_deployment_id": "<model id observed in response or response headers>",
  "request_headers_hash": "sha256 of significant headers",
  "response_hash": "sha256 of the raw response",
  "response_ref": "URI to raw response in response store",
  "response_status_code": 200,
  "outcome": "blocked|passed|partial|inconclusive",
  "outcome_classifier_version": "judge-v1.0+sha256:...",
  "outcome_rationale": "1-sentence judge rationale",
  "human_spot_check": null,
  "harness_version": "v0.1.0",
  "elapsed_ms": 1842
}
```

## Field semantics

| Field | Required | Notes |
|---|---|---|
| attempt_id | yes | UUID v4 |
| engagement_id | yes | binds attempt to authorized scope |
| timestamp | yes | UTC ISO-8601 |
| payload_id | yes | matches corpus record |
| payload_hash | yes | sha256 of raw payload — payload identity stays even if `payload_ref` is purged |
| payload_ref | yes | URI to payload in the payload store |
| taxonomy_class | yes | when corpus is tagged; otherwise "user-defined" |
| target_endpoint | yes | exact URL |
| target_deployment_id | yes | model id observed; drift triggers re-baseline |
| request_headers_hash | yes | sha256 of significant request headers (excluding auth tokens) |
| response_hash | yes | sha256 of raw response |
| response_ref | yes | URI to response in store |
| response_status_code | yes | HTTP status |
| outcome | yes | one of the four classes |
| outcome_classifier_version | yes | judge-prompt-hash + judge-model-id — eval reproducibility |
| outcome_rationale | yes | one-sentence justification |
| human_spot_check | no | populated post-hoc when the record is in the 10% sample |
| harness_version | yes | the eval-harness package version |
| elapsed_ms | yes | request → response time |

## Storage requirements

Per the engagement's RoE — append-only, retention-locked, with hash-chaining or external anchoring. See `scaffolding-red-team-engagement/reference/logging-schema.md` for the engagement-level logging contract.

## Drift detection

- `target_deployment_id` drift mid-run → halt + re-baseline (the target system changed)
- `harness_version` drift mid-run → halt + restart (the harness self-updated)
- `outcome_classifier_version` drift → annotate the run; reclassify earlier records OR document the boundary
