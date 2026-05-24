# Per-Stage Verification Checklist

Print this and check off items as each stage's verification runs. Every box must be checked OR explicitly marked N/A with rationale before the proof bundle is issued.

## Stage 0 — Scope confirmation

- [ ] DSR intake form read; subject identifier and data categories confirmed
- [ ] Legal basis identified (regulation + article / section)
- [ ] Every pipeline stage assessed for in-scope / out-of-scope
- [ ] At least one stage is in scope (else: issue non-applicability statement, not this bundle)

## Stage 1 — Raw / curated dataset

- [ ] Every store that ingested the subject's records enumerated (raw drop zone, curated tables, feature store, warehouses, object storage)
- [ ] Deletion command run against each store with the subject identifier
- [ ] Post-deletion count = 0 verified per store
- [ ] Side files (CSV, parquet, BigQuery exports) removed
- [ ] Command + output captured as evidence

## Stage 2 — Embeddings / vector store

- [ ] Every vector store derived from the source dataset enumerated (Pinecone, Weaviate, pgvector, OpenSearch k-NN, FAISS on disk)
- [ ] Per store: metadata-filter delete OR nearest-neighbor probe + delete
- [ ] Count of vectors deleted captured per store
- [ ] Embedding-inversion risk acknowledged explicitly — NOT closed by claiming "embeddings are anonymous"

## Stage 3 — Model weights

- [ ] Strategy selected: retrain-from-clean | model-deprecation | machine-unlearning-with-caveat
- [ ] Strategy rationale documented (one paragraph)
- [ ] Strategy-specific evidence captured:
  - retrain-from-clean: new checkpoint id, training manifest excludes subject, old checkpoint deprecated date
  - model-deprecation: deprecation date, archive location, access-control policy
  - machine-unlearning-with-caveat: method, verification metric, explicit residual-risk statement signed by privacy officer
- [ ] Stage 3 sign-off includes BOTH ML engineer AND privacy officer

## Stage 4 — Inference cache / generated content

- [ ] Every cache the model writes to enumerated (prompt-completion cache, RAG passage cache, conversation logs, downstream output tables)
- [ ] Each cache searched for subject identifier OR subject content (substring)
- [ ] Matching records deleted with counts captured
- [ ] Generated content containing subject data deleted (responses, summaries, derived outputs)

## Stage 5 — Backups / replicas / DR

- [ ] Every backup of stages 1, 2, and 4 enumerated
- [ ] One of two policies declared and documented:
  - Tombstone + scheduled re-deletion (tombstone manifest + restore-replay procedure)
  - Backup rotation window (window length + expected expiry date)
- [ ] No silent "deal with it later" — silence is a failure

## Cross-stage

- [ ] Proof bundle assembled per `proof-bundle-template.md`
- [ ] Failure log populated (empty = no failures observed)
- [ ] Privacy officer signed the cross-stage residual-risk statement (even if risk is "none")
- [ ] Proof retention date set per regulation default
- [ ] Bundle stored with content-hash in evidence-management system
