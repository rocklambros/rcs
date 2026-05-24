# DSR Erasure Proof Bundle Template

Fill in every field. A blank field is a verification failure, not a deliverable. If a section does not apply, write "Not applicable — <one-line rationale>" so the auditor sees the decision and the reasoning.

---

## 1. Request identification

| Field | Value |
|---|---|
| DSR ID | <internal-case-id> |
| Subject identifier (hashed if regulation requires) | <hash-or-id> |
| Regulation | <gdpr-art17 \| ccpa-1798.105 \| hipaa-right-to-amend \| other> |
| Date received | <YYYY-MM-DD> |
| Date verification completed | <YYYY-MM-DD> |
| Privacy officer / DPO sign-off | <name + date> |
| Proof bundle retained until | <YYYY-MM-DD per regulation default> |

## 2. Scope confirmation (Stage 0)

| Pipeline stage | In scope? | Evidence (dataset / store / model id) |
|---|---|---|
| Raw / curated dataset | yes / no | <fill> |
| Embeddings / vector store | yes / no | <fill> |
| Model weights | yes / no | <fill> |
| Inference cache / generated content | yes / no | <fill> |
| Backups, replicas, DR copies | yes / no | <fill> |

If every row is "no", do not issue this bundle — issue a non-applicability statement instead.

## 3. Per-stage verification

### Stage 1 — Raw / curated dataset

- Stores queried: <list>
- Deletion command run per store: <verbatim>
- Pre-deletion count / Post-deletion count: <n> / 0
- Side files (CSVs, parquet exports, BigQuery exports) removed: <list + counts>
- Stage 1 sign-off (engineer + date): <fill>

### Stage 2 — Embeddings / vector store

- Vector stores queried: <list>
- Identification method: <metadata-filter | nearest-neighbor-probe>
- Vectors deleted per store: <n>
- Embedding-inversion residual risk acknowledged: yes (this is a required acknowledgement, not optional)
- Stage 2 sign-off (engineer + date): <fill>

### Stage 3 — Model weights

- Strategy selected: <retrain-from-clean | model-deprecation | machine-unlearning-with-caveat>
- Strategy rationale (one paragraph): <fill>
- If `retrain-from-clean`: new checkpoint id, training-data manifest excludes subject, old checkpoint deprecated date
- If `model-deprecation`: deprecation date, archive location, access-control policy
- If `machine-unlearning-with-caveat`: method used, unlearning verification metric + value, EXPLICIT residual-risk statement, privacy-officer signature accepting residual risk (NOT optional)
- Stage 3 sign-off (ML engineer + privacy officer + date): <fill>

### Stage 4 — Inference cache / generated content

- Caches queried: <list — prompt-completion cache, RAG passage cache, conversation logs, downstream output tables>
- Records deleted per cache: <n>
- Generated content containing subject data deleted: <list + counts>
- Stage 4 sign-off (engineer + date): <fill>

### Stage 5 — Backups / replicas / DR

- Policy declared: <tombstone-on-restore | rotation-window-expiry | other>
- If tombstone-on-restore: tombstone manifest location, restore-replay procedure documented at <link>
- If rotation-window-expiry: window length, expected expiry date for affected backups
- Stage 5 sign-off (infra engineer + date): <fill>

## 4. Failure log

| Stage | Failure observed | Remediation | Remediation date | Re-verification date |
|---|---|---|---|---|

(One row per failure caught during verification. Empty means no failures observed.)

## 5. Cross-stage residual-risk statement

A single paragraph stating any residual risk after all stages closed, signed by the privacy officer. Even if the risk is "none", the explicit statement is required.

---

**Bundle integrity**: this artifact should be stored with content-hash + timestamp via the operator's evidence-management system (e.g., signed git commit, WORM bucket, evidence vault). The hash is part of the audit trail.
