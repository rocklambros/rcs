### v6-batch-1: governance methodologies — 2026-05-23

Skills shipped:

- `security/writing-vdp-and-coordinated-disclosure` v0.1.0 — public VDP page + security.txt (RFC 9116) + coordinated-disclosure runbook + severity rubric (CVSS v4.0) + researcher email templates + pre-publish gate (Σ 12, status: shipped)
- `security/scaffolding-ai-policy-doc` v0.1.0 — org-wide AI Use Policy (acceptable / prohibited use, oversight tiers, vendor inventory, IR addendum, employee acknowledgement) anchored on actual current usage (Σ 10, status: shipped)
- `security/interpreting-vendor-questionnaire-skeptically` v0.1.0 — per-answer claim · evidence · gap walk + hedge-word scan + missing-artifact scan + contradiction scan + staleness check + AI-specific overlay + follow-up questions, with explicit non-verdict (Σ 9, status: shipped)

Eval methodology: Sonnet-only in-session validation per PRAGMATIC discipline. Each scenario dispatched to a fresh general-purpose subagent (model: sonnet) with the SKILL.md inlined as system context; completion judged against the 3 rubric items by the parent session. Full 3-model validation (Haiku + Sonnet + Opus) deferred to a future re-run via `tools.run_evals`.

Eval results (rubric items passed / 3):

| Skill | happy-path | edge-case | anti-trigger |
|---|---|---|---|
| writing-vdp-and-coordinated-disclosure | 3/3 | 3/3 | 3/3 |
| scaffolding-ai-policy-doc | 3/3 | 3/3 | 3/3 |
| interpreting-vendor-questionnaire-skeptically | 3/3 | 3/3 | 3/3 |

All 27/27 rubric items passed. All three skills clear PRAGMATIC Sonnet thresholds (happy 3/3, edge 3/3, anti ≥ 2/3) and ship as `status: shipped`.

Notes: No `reference/` files bundled in this batch — SKILL.md bodies inline the schemas, templates, and rubrics the workflows produce. A v0.2 enhancement may extract expanded reference templates (VDP boilerplate, AI-policy boilerplate, findings-report template, hedge-word checklist).
