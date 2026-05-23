# PII policy file schema

The PII / sensitive-content audit (Step 6) consumes a user-supplied policy file. This document defines that file's schema. The policy is NOT bundled with the skill — operators supply it because PII boundaries are domain- and regulation-specific.

## File format

YAML or JSON. The audit accepts either.

## Schema

```yaml
policy_version: "1.0"
policy_owner: "<team or person responsible>"
last_reviewed: "2026-05-15"

entities:
  - name: email
    detector: regex
    pattern: '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    severity: medium
    action: redact
    redaction_token: "<EMAIL>"

  - name: phone_us
    detector: regex
    pattern: '\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    severity: medium
    action: redact
    redaction_token: "<PHONE>"

  - name: ssn_like
    detector: regex
    pattern: '\b\d{3}-\d{2}-\d{4}\b'
    severity: critical
    action: quarantine

  - name: credit_card_luhn
    detector: regex_plus_luhn
    pattern: '\b(?:\d[ -]?){13,19}\b'
    severity: critical
    action: quarantine

  - name: ip_address
    detector: regex
    pattern: '\b(?:\d{1,3}\.){3}\d{1,3}\b'
    severity: low
    action: flag

  - name: person_name
    detector: ner
    model: "spacy:en_core_web_lg"
    label: PERSON
    severity: medium
    action: flag

  - name: medical_record_number
    detector: regex
    pattern: '\bMRN-?\d{7,10}\b'
    severity: critical
    action: quarantine

defaults:
  action_for_unmatched: flag
  redaction_style: "<{NAME}>"
  case_sensitive: false
```

## Field semantics

| Field | Meaning |
|---|---|
| `name` | Unique identifier for the entity class; used in findings reports |
| `detector` | `regex` (Python `re` syntax), `regex_plus_luhn` (regex + Luhn-check post-filter, for card numbers), `ner` (named-entity recognition; requires `model` and `label`) |
| `pattern` | The regex (for regex detectors) |
| `severity` | `low` / `medium` / `high` / `critical` — informational; the audit reports it; the action is what drives behavior |
| `action` | `flag` (record in findings, no file action), `redact` (write to redacted companion file with `redaction_token`), `quarantine` (move row to quarantine, do NOT include in training file) |
| `redaction_token` | The literal string used to replace the matched span when `action: redact` |

## Default minimum policy

If the user does not supply a policy, the audit uses this minimum:

```yaml
policy_version: "default-minimum"
entities:
  - {name: email, detector: regex, pattern: ..., action: flag}
  - {name: phone_us, detector: regex, pattern: ..., action: flag}
  - {name: ssn_like, detector: regex, pattern: ..., action: flag}
  - {name: ip_address, detector: regex, pattern: ..., action: flag}
  - {name: credit_card_luhn, detector: regex_plus_luhn, pattern: ..., action: flag}
defaults:
  action_for_unmatched: flag
```

The default policy is `flag`-only (no redaction, no quarantine). This is deliberate: the audit will not modify the dataset under defaults. The audit emits a prominent warning that the default policy is a *minimum* and may not satisfy the operator's regulatory or contractual requirements.

## What this schema does NOT cover

- **PHI under HIPAA Safe Harbor** — the 18 identifiers require a more comprehensive policy than the minimum; operators in healthcare contexts should supply their own
- **GDPR Article 9 special categories** — biometric, genetic, political-opinion content is out of scope for regex detectors; consider a separate content-classification audit
- **Confidential business information** — NDA-protected content (customer names, internal project codenames) is operator-specific; supply via the `entities` list
- **Cross-row PII aggregation** — re-identification by combining quasi-identifiers across rows is out of scope; this audit is row-local

## Findings report format

Each PII finding row in the audit output:

```json
{
  "row_id": "...",
  "entity_name": "email",
  "severity": "medium",
  "action_taken": "redact" | "quarantine" | "flag",
  "evidence_span": {"offset": <int>, "length": <int>},
  "redaction_token_used": "<EMAIL>"
}
```

The matched VALUE is NEVER in the findings report — only the span. The value is written only to the quarantine file (under restricted access if the operator's policy requires) or the redacted-companion file (with the redaction token substituted).
