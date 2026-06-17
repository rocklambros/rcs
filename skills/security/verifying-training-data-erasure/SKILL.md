---
name: verifying-training-data-erasure
description: >
  Walks a Data Subject Request (DSR) erasure verification across the four stages of an
  ML pipeline where a subject's data can persist — raw/curated datasets, derived
  embeddings or representations, fine-tuned model weights, and inference-time caches or
  generated content — and produces a tamper-evident proof bundle (per-stage erasure
  evidence with timestamps, tool output, residual-risk acknowledgement). Use when an
  organization receives a GDPR Article 17 / CCPA / HIPAA right-to-be-forgotten request
  that touches data already used in training or retrieval, when an auditor asks for
  proof that a deleted user's data is gone from a deployed model, or when a fine-tuned
  model is being retired and the operator needs documented assurance that the training
  data has been erased downstream. Refuses to engage when no DSR exposure exists (no
  PII-derived training data, no retrieval store, no caching) — the workflow is
  cost-justified only when at least one stage actually carries subject-identifiable
  derivatives.
version: 0.1.0
status: shipped
track: security
audience:
  - security-eng
  - ai-security
  - ml-engineer
  - compliance-eng
evidence:
  - gdpr-art17-right-to-erasure
  - RCAP
last-updated: 2026-05-23
---

# Verifying Training-Data Erasure

## When to use

Trigger this skill when the user asks for or implies one of:

- A GDPR Article 17, CCPA §1798.105, or HIPAA right-to-amend request has been received and the operator must prove erasure across an ML pipeline
- An auditor (DPA, HHS, internal compliance) is asking for documented evidence that a deleted subject's data is no longer recoverable from a deployed model
- A fine-tuned model is being retired or replaced, and the operator wants a closeout artifact showing the training corpus has been erased from downstream artifacts (vector stores, caches, model weights)
- A data-breach notification triggers a wider DSR sweep across all systems trained on the affected dataset
- Phrases like "prove this user's data is gone from the model", "DSR verification on the embedding store", "right-to-be-forgotten on a fine-tune", "training-data erasure proof for the auditor"

## When NOT to use

Skip this skill and hand off when:

- No DSR exposure exists in the pipeline — the training data was fully synthetic, the model was never fine-tuned on identifiable data, and no retrieval store carries the subject's records. In that case the operator can answer the request with a one-line statement of non-applicability.
- The request is about *deleting* the data, not *verifying* that prior deletion held. Use the operator's data-deletion runbook first; only return to this skill after deletion is claimed and proof is needed.
- The request is about base-model providers (OpenAI, Anthropic, Google) where the operator has no training-pipeline access. Forward the DSR to the upstream provider per their published process; this skill cannot verify what it cannot inspect.
- The request is a content-moderation takedown (e.g., a specific generated output must be removed). Use the inference-policy / output-filter workflow; this skill addresses upstream data, not downstream outputs.

## Quick start

User says: "We received a HIPAA right-to-amend request from a patient whose record was in the fine-tuning corpus for our clinical-notes summarization model (deployed in production for 6 months). The vector store also indexed embeddings of their record. Prove erasure to the privacy officer."

Skill response: walks the four-stage verification (dataset → embeddings → model weights → inference caches), produces a per-stage evidence table (Stage · Erasure method · Tool output · Residual risk · Sign-off), names the model-weight stage as the hardest (recommends retrain-from-clean-corpus or model-deprecation, NOT relying on unverified machine-unlearning), and emits a proof bundle the privacy officer can attach to the DSR file.

## Inputs / Arguments / Flags

| Argument | Type | Required | Default | Description |
|---|---|---|---|---|
| subject_id | string | yes | — | The identifier the operator uses to locate the subject's records in source systems (patient MRN, account ID, email hash). |
| pipeline_stages | list of stages | yes | all four | Which of `dataset`, `embeddings`, `model_weights`, `inference_cache` are in scope. At least one must be present; if none, this skill does not apply. |
| regulation | string | no | "gdpr-art17" | One of `gdpr-art17`, `ccpa-1798-105`, `hipaa-right-to-amend`, `other`. Determines proof-bundle field set + retention period for the proof itself. |
| retain_proof_until | ISO date | no | regulation default | When the proof bundle itself can be deleted. GDPR: 3 years post-erasure. HIPAA: 6 years. CCPA: 24 months. |
| model_weight_strategy | string | no | "retrain-from-clean" | One of `retrain-from-clean`, `model-deprecation`, `machine-unlearning-with-caveat`. The third is documented but flagged as not audit-grade in 2026. |

## Reviewer stance

Adopt the stance of an expert senior software developer with 30 years of experience in the language(s) and frameworks of the artifact under review. Apply that depth throughout: name the failure modes a junior reviewer would miss, weigh tradeoffs explicitly, and ground every finding in specific evidence from the artifact.

## Workflow

Copy this checklist into the response and check off items as each stage's verification completes:

```
DSR erasure verification (subject_id: <redact-or-hash>):
- [ ] Stage 0: Scope confirmation — which stages apply
- [ ] Stage 1: Raw / curated dataset erasure verified
- [ ] Stage 2: Embeddings / vector-store erasure verified
- [ ] Stage 3: Model-weight erasure verified (named strategy + residual-risk statement)
- [ ] Stage 4: Inference cache / generated-content erasure verified
- [ ] Stage 5: Backup, replica, and disaster-recovery copies addressed
- [ ] Proof bundle assembled with sign-offs
- [ ] Proof retention date set per regulation
```

### Stage 0: Scope confirmation

- Read the DSR intake form. Confirm the subject identifier, the data categories named, and the legal basis for erasure.
- Identify every pipeline stage where the subject's data (or derivatives) may persist. A "no" at every stage means this skill does not apply — the operator returns a non-applicability statement instead of a proof bundle.
- Output: a scope table listing each stage with "in-scope: yes/no" and the evidence (dataset SHA, vector-store name, model fine-tune ID).

### Stage 1: Raw and curated dataset erasure

- Query every store that ingested the subject's record: raw drop zone, curated training table, feature store, data warehouse, S3 / GCS / Azure Blob backups.
- For each store, run a deletion command tied to the subject identifier and capture the command + return value + post-deletion count.
- Verify a post-deletion read returns zero rows. A non-zero count is a Stage 1 failure — fix before proceeding.
- Confirm any data-export side files (CSV dumps, parquet snapshots, BigQuery exports) are also removed.

### Stage 2: Embeddings and vector-store erasure

- List every vector store (Pinecone, Weaviate, pgvector, OpenSearch k-NN, FAISS index files on disk) that was populated from the source dataset.
- For each, locate vectors derived from the subject's records via either (a) metadata filter on subject_id, or (b) a recomputed embedding of the original record used as a nearest-neighbor probe (top-1 with cosine distance < 0.05 indicates retention).
- Delete the matching vectors and capture the count deleted.
- **Critical caveat**: embeddings are not anonymous. Embedding-inversion attacks (Song & Raghunathan 2020; Morris et al. 2023) can reconstruct meaningful portions of source text from dense embeddings. Do NOT report "embeddings retained, source deleted" as a valid Stage 2 closure — that is a Stage 2 failure.

### Stage 3: Model-weight erasure

This is the hardest stage. Model weights *memorize* training data, especially for fine-tunes on small or repetitive datasets (Carlini et al. 2021, 2023). Pick one of three strategies and document residual risk explicitly:

- **`retrain-from-clean`** (audit-grade): retrain the model on the corpus with the subject's records removed. Verify the new checkpoint's training-data manifest excludes the subject. Deprecate the old checkpoint. Highest cost, highest assurance.
- **`model-deprecation`** (audit-grade for low-stakes models): take the affected model out of service, archive the checkpoint behind access controls, and document the deprecation date. Acceptable when the model's business value does not justify retraining cost.
- **`machine-unlearning-with-caveat`** (NOT audit-grade in 2026): apply an unlearning method (gradient ascent, SISA partitioning, influence-function inversion). Document the method, the unlearning verification metric used, and an explicit residual-risk statement that current unlearning has no audit-grade guarantee — extraction attacks may still surface the data. The privacy officer must sign off accepting this residual risk.

The proof bundle MUST name the chosen strategy. Silence on this stage is a Stage 3 failure.

### Stage 4: Inference cache and generated-content erasure

- List every cache the model writes to: prompt-completion cache, RAG retrieved-passage cache, conversation-history store, generated-summary table, downstream-pipeline output tables.
- Search each for any record that contains the subject's identifier or content (substring match on the deleted source text where feasible).
- Delete matching records and capture the count.
- Address conversation logs: if the subject's data appeared in a generated response, the response is also subject to erasure.

### Stage 5: Backup, replica, and DR copies

- Identify every backup of stages 1, 2, and 4 (database backups, vector-store snapshots, cache replicas).
- Choose one of two policies and document it:
  - **Tombstone + scheduled re-deletion**: mark the backup as containing tombstones for the subject; when the backup is restored, replay the tombstones before bringing systems online.
  - **Backup rotation window**: confirm the backup will be naturally expired within the regulation's allowed window (GDPR allows reasonable backup-rotation delays if documented).
- A backup that will never expire and was not tombstoned is a Stage 5 failure.

### Proof bundle assembly

Emit a single artifact with these sections (the operator stores this as the DSR-response evidence):

1. DSR identifier, subject identifier (hashed if regulation requires), date received, date completed
2. Scope table from Stage 0
3. Per-stage evidence table: Stage · Method · Tool / command run · Output / counts · Sign-off · Date
4. Model-weight strategy + residual-risk statement (explicit, even if "none")
5. Backup policy declaration
6. Retention date for the proof bundle itself

## Outputs

A two-part deliverable:

1. **DSR proof bundle** (markdown or PDF) — the artifact above. Signed by the DPO / privacy officer / equivalent role.
2. **Skill-side findings memo** — any stages that failed verification, with named remediation. The operator MUST resolve failures before delivering the proof bundle. Partial-erasure proofs are worse than no proof — they create a written record of incomplete compliance.

Both go in the DSR case file with the regulation-derived retention date.

## Failure modes

- **Embedding-only retention claimed safe** — vendor docs sometimes assert embeddings are "anonymized representations". Embedding-inversion research disproves this. Caught by: Stage 2 caveat block in the proof bundle template requires an explicit embedding-erasure step, not an embedding-retention claim.
- **Unverified machine-unlearning relied on as audit-grade** — operators with expensive fine-tunes are tempted to apply an unlearning algorithm and claim erasure. As of 2026 no unlearning method has audit-grade extraction-resistance guarantees. Caught by: Stage 3 strategy selector forces an explicit named strategy plus residual-risk acknowledgement.
- **Inference cache forgotten** — Stage 4 is the most-skipped stage. RAG passage caches, prompt-completion caches, and conversation logs persist subject content. Caught by: Stage 4 step in the workflow checklist + cache enumeration prompt.
- **Backups left dormant** — Stage 5 is often "we'll deal with it later". Restoring a backup later resurrects the deleted data. Caught by: Stage 5 requires an explicit tombstone policy or a documented rotation window — silence on Stage 5 is a hard failure.
- **Verification = file-existence check** — "I deleted the row, here's a 0-count SELECT" is not a Stage-3 proof if the model still memorizes the row. Caught by: Stages 1 and 2 use existence checks; Stage 3 explicitly disallows existence checks alone and requires a named strategy.
- **Proof retention indefinite** — operators sometimes retain the DSR proof bundle forever, which contains the subject's identifier and is itself subject to erasure rules. Caught by: `retain_proof_until` is a required output field, populated from the regulation default.

## References

- `reference/proof-bundle-template.md` — fill-in-the-blank DSR proof artifact
- `reference/per-stage-checklist.md` — printable per-stage verification checklist
- [GDPR Article 17 — Right to erasure](https://gdpr-info.eu/art-17-gdpr/)
- [CCPA §1798.105 — Right to delete](https://oag.ca.gov/privacy/ccpa)
- [NIST IR 8053 — De-identification of personal information](https://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.8053.pdf)
- Carlini et al. 2023, *Extracting Training Data from Diffusion Models* — model-weight memorization evidence
- Morris et al. 2023, *Text Embeddings Reveal (Almost) As Much As Text* — embedding-inversion evidence

## Examples

### Example 1: HIPAA right-to-amend on a fine-tuned clinical summarizer (happy-path)

Input: "Patient (MRN redacted) was in our fine-tuning corpus for the clinical-notes summarization model deployed 6 months ago. Vector store also has embeddings of their notes. Prove erasure for the HIPAA privacy officer."

Output: Skill walks Stages 0–5. Stage 0 confirms dataset, vector store, model weights, and a summary cache are all in scope. Stage 1 deletes the patient's source notes from the training table (post-deletion count: 0). Stage 2 deletes 14 embeddings from the pgvector store identified via metadata filter on MRN. Stage 3 recommends `retrain-from-clean` (HIPAA + clinical use does not justify the residual risk of machine-unlearning); operator agrees, retrain is queued, old checkpoint deprecated immediately. Stage 4 finds 3 cached summaries containing patient content; deleted. Stage 5 declares tombstone-on-restore policy for nightly database backups. Proof bundle emitted with retention through 2032-05-23 (6-year HIPAA window).

### Example 2: Embedding-only retention attempt (edge-case)

Input: "Source data is deleted from our raw store. The embeddings in Pinecone are anonymized vectors, so we're keeping them — they aren't PII. Generate the proof."

Output: Skill refuses to issue a clean Stage 2 pass. Returns a Stage 2 failure with citation to embedding-inversion research and the explicit instruction that embeddings derived from the deleted source must be deleted from Pinecone (or re-derived from a non-deleted source via a documented re-derivation). Names the vendor's "anonymized" claim as a marketing assertion, not an audit-grade one. Stage 2 must be re-run before the bundle is issued.

### Example 3: No DSR exposure (anti-trigger)

Input: "We received a DSR on a user, but our model was trained entirely on public Common Crawl data and we never fine-tuned on user content. Should we run the verification?"

Output: Skill returns a non-applicability response, not a proof bundle. Explains that the workflow is cost-justified only when at least one pipeline stage carries subject-derived artifacts. Recommends the operator answer the DSR with a one-line statement that no subject-derived training, embeddings, weights, or caches exist in this pipeline, retained in the DSR case file. Skill does not produce a proof bundle for an absent risk.

## See also

- `security/scaffolding-ai-policy-doc` — pairs with this skill for the policy framework declaring DSR response SLAs and stakeholder roles
- `security/running-cloud-ir-runbook` — used when a DSR is triggered by a breach notification rather than a routine request
- `security/auditing-source-provenance` (planned) — captures the provenance metadata that Stage 0 / Stage 1 rely on
- `ml-datasci/writing-finetune-spec-sheet` — the upstream artifact that names which subjects were in the fine-tune corpus, making Stage 0 scope confirmation tractable

## Status & version

- Status: shipped
- Version: 0.1.0
- Last-updated: 2026-05-23
- Provenance: authored in RCS v7-batch-5 per PRAGMATIC discipline; Sonnet-only in-session eval validation
