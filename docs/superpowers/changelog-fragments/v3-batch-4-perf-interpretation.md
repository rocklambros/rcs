### v3-batch-4: perf + interpretation — 2026-05-23

Skills shipped:
- `ml-datasci/auditing-prompt-token-budget` v0.1.0 — Anthropic API prompt-budget audit with stable-vs-volatile classification, `cache_control` breakpoint placement (end of stable region, explicit `"ttl": "1h"` per QC.4a), write-vs-read cost projection, and hit-rate telemetry; refuses on sub-500-token one-shot scripts (Σ 16, status: shipped)
- `ml-datasci/recommending-model-tier` v0.1.0 — per-task Haiku 4.5 / Sonnet 4.6 / Opus 4.7 routing with reasoning-depth × task-category baseline, safety-critical / latency / cost / cache-lineage modifiers, mandatory escalation rule per downgrade, and pre-shipping eval requirement; refuses on policy-locked single-tier deployments (Σ 14, status: shipped)
- `ml-datasci/interpreting-conflicting-tests` v0.1.0 — adjudicates parametric-vs-non-parametric (and exact-vs-asymptotic) conflicts via assumption-status table, picks the test whose assumptions hold (not the smaller p-value), commits to one primary with matched rank-based or parametric effect-size + 95% CI; refuses 'mixed evidence' framing and p-hacking via test-shopping (Σ 16, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. 9 dispatches (3 scenarios × 3 skills); all scored 3/3 against intent. Full 3-model (Haiku / Sonnet / Opus) validation deferred to a future re-run.

Notes: No deviations or calibration corrections. All three skills retained `status: shipped` after eval validation. The auditing-prompt-token-budget skill explicitly encodes QC.4a's "always set `ttl: 1h` explicitly" discipline as a step-6 requirement and a failure-mode entry.
