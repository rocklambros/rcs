### v7-batch-5: training-data erasure + sigstore — 2026-05-23

Skills shipped:
- `security/verifying-training-data-erasure` v0.1.0 — DSR-proof workflow across dataset / embeddings / model weights / inference caches; produces a tamper-evident proof bundle with explicit residual-risk acknowledgement at the model-weight stage (Σ 10, status: shipped)
- `security/verifying-sigstore-signatures` v0.1.0 — cosign + in-toto + SLSA Build-level verification with a four-check verdict (identity, signature, attestation, provenance level); refuses tag-only inputs and undefined-trust-policy requests (Σ 10, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Six general-purpose Sonnet subagents dispatched (3 scenarios × 2 skills). Intent-matched judging against 3 rubric items per scenario. Full 3-model validation deferred to a future re-run.

Eval results (Sonnet-only):
- verifying-training-data-erasure / 01-hipaa-finetune (happy-path) — 3/3 PASS
- verifying-training-data-erasure / 02-embedding-only-retention (edge-case) — 3/3 PASS
- verifying-training-data-erasure / 03-no-dsr-exposure (anti-trigger) — 3/3 PASS
- verifying-sigstore-signatures / 01-cosign-container (happy-path) — 3/3 PASS
- verifying-sigstore-signatures / 02-attestation-digest-mismatch (edge-case) — 3/3 PASS
- verifying-sigstore-signatures / 03-apt-deb-signature (anti-trigger) — 3/3 PASS

Aggregate: 18 / 18 rubric items pass. Both skills earn `status: shipped`.

Notes: no deviations or calibration corrections. Both skills land in the `security/` track; one shipped-fragment file written (`skills/security/shipped-fragments/v7-batch-5.md`) for Batch 6 integration to consolidate into the track README.
