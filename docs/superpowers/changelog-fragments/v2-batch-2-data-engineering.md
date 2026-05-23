### v2-batch-2: data engineering depth — 2026-05-23

Skills shipped:

- `workflow/auditing-source-provenance` v0.1.0 — audits ingest pipelines for per-record provenance attachment, transform-survival, and CI gating (Σ 16, status: shipped)
- `workflow/validating-schema-evolution` v0.1.0 — classifies schema changes as breaking / non-breaking / ambiguous, scaffolds safe migrations including the 5-step rename and 3-step NOT-NULL-add patterns (Σ 13, status: shipped)
- `ml-datasci/generating-data-dictionary` v0.1.0 — per-column semantic-class + role inference, anomaly flagging, PII detection, JSON-Schema-validatable output (Σ 15, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline (9 dispatches total — 3 scenarios × 3 skills). Full 3-model (Haiku + Sonnet + Opus) validation deferred to a future re-run.

Eval results (Sonnet, intent-matched scoring against 3 rubric items per scenario):

- `auditing-source-provenance`: happy 3/3, edge 3/3, anti 3/3
- `validating-schema-evolution`: happy 3/3, edge 3/3, anti 3/3
- `generating-data-dictionary`: happy 3/3, edge 3/3, anti 3/3

All three skills pass Sonnet thresholds for happy-path (3/3), edge-case (3/3), and anti-trigger (≥ 2/3) and ship as `status: shipped`.

Notes: none. No demotions or deviations.
