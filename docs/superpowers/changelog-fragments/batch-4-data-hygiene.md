### Batch 4: data + workflow hygiene — 2026-05-23

Skills shipped:

- `workflow/deduplicating-records` v0.1.0 — multi-key dedup with documented per-rule confidence, ID-format normalization across sources, and union-find / connected-components transitive collapse; emits an auditable `{merged, borderline, untouched}` diff (Σ 18, status: shipped)
- `workflow/pinning-reproducible-environments` v0.1.0 — per-ecosystem lockfile pattern (uv / poetry / pip-compile / npm / pnpm / renv), runtime-version pinning, base-image digest pinning, CI strict-install, weekly drift-check (Σ 17, status: shipped)
- `workflow/auditing-data-quality` v0.1.0 — bounded-tabular audit covering per-column nulls / ranges / types, semantic-class detection, outlier flagging without auto-drop, cardinality alarm, row-level integrity (duplicates + conflicting fact-pairs) (Σ 17, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each skill ran 3 scenarios (happy-path, edge-case, anti-trigger) × 1 candidate model (Sonnet 4.6) = 3 dispatches per skill, 9 total. Each rubric item judged against intent in the parent session. Full 3-model validation (Haiku / Sonnet / Opus) deferred to a future re-run.

Eval results (Sonnet 4.6, intent-matched scoring):

| Skill | Happy-path | Edge-case | Anti-trigger |
|---|---|---|---|
| `deduplicating-records` | 3/3 | 3/3 | 3/3 |
| `pinning-reproducible-environments` | 3/3 | 3/3 | 3/3 |
| `auditing-data-quality` | 3/3 | 3/3 | 3/3 |

All 9 scenarios met Sonnet pass thresholds (happy-path 3/3, edge-case 3/3, anti-trigger ≥ 2/3). No demotion to `drafting` required.

Notes: no failures, no calibration corrections. References stayed one level deep per Anthropic best-practices doc. Each skill ships with 2 bundled `reference/` files (template + extended rules / worked example).
